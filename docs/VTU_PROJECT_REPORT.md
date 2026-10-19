# Project Report Outline: Namma Metro Pulse

**Course:** Big Data Analytics (BCS714D, 2022 Scheme)  
**Program:** Bachelor of Engineering (B.E.) — 7th Semester  
**Department:** Computer Science & Engineering / Information Science & Engineering  
**Project Title:** Namma Metro Pulse — Big Data Analytics for Passenger Flow and Station Demand in Bengaluru  
**Dataset Source:** Bangalore Metro Rail Corporation Limited (BMRCL) RTI Disclosure ([github.com/Vonter/bmrcl-ridership-hourly](https://github.com/Vonter/bmrcl-ridership-hourly))

---

## 1. Abstract

Urban rapid transit systems generate substantial volumes of passenger flow and ticketing transaction data. Analyzing this information is crucial for transit capacity management, train dispatch scheduling, station congestion alleviation, and fare revenue forecasting. This project, **Namma Metro Pulse**, presents a distributed big data analytics framework for the Namma Metro transit network operated by BMRCL in Bengaluru, India.

Using actual ridership disclosure data obtained under the Right to Information (RTI) Act for August 1–18, 2025, and September 1–30, 2025, comprising over 1.45 million records across 83 metro stations spanning the Purple, Green, and Yellow corridors, this project implements an end-to-end Big Data pipeline:
1. **Hadoop Distributed File System (HDFS)** for scalable, fault-tolerant dataset storage.
2. **Three genuine Java Hadoop MapReduce jobs** for distributed passenger demand aggregation, hourly peak/rush hour analysis, and origin-destination corridor volume ranking.
3. **Apache Hive** external tables and analytical SQL queries for structural aggregation, dense ranking, and fare revenue analytics.
4. **Apache Pig Latin** scripts for relational algebra transformations, corridor filtering, and data aggregation.
5. **Streamlit and Plotly** interactive dashboards for visual exploration of corridor flows, station footfalls, and peak commute periods.

All analytical metrics, passenger volumes, and revenue figures presented are computed directly from the genuine BMRCL dataset without synthetic fabrication.

---

## 2. VTU Syllabus Mapping (BCS714D - 2022 Scheme)

| Module / Syllabus Unit | Big Data Technology | Project Implementation Component |
| :--- | :--- | :--- |
| **Module 1: Introduction to Big Data & HDFS** | Apache Hadoop HDFS | `scripts/01_setup_hdfs.sh`, HDFS storage directory layout (`/namma_metro/input`, `/output`), replication & file verification |
| **Module 2: Hadoop MapReduce Paradigm** | Java MapReduce (v2 YARN) | 3 Java MapReduce Programs: `StationDemandAggregation.java`, `HourlyPeakAnalysis.java`, `StationPairRanking.java` |
| **Module 3: Apache Hive for SQL Analytics** | HiveQL & Metastore | `hive/01_create_database_tables.hql` to `04_od_pair_revenue_analytics.hql`, External Tables, Window Functions, DENSE_RANK |
| **Module 4: Apache Pig for Data Flow** | Pig Latin | `pig/01_station_footfall.pig`, `02_hourly_distribution.pig`, `03_high_traffic_routes.pig`, LOAD, FILTER, GROUP, FOREACH |
| **Module 5: Visualization & Applications** | Python, Streamlit, Plotly | `dashboard/app.py` for interactive visual intelligence, footfall trends, and executive KPI reporting |

---

## 3. System Architecture

```
+-----------------------------------------------------------------------------+
|                          BMRCL RAW RTI DATASETS                             |
|  - August 2025 (Station Hourly & Station-Pair Excel Files)                  |
|  - September 2025 (Station Hourly Excel Files)                              |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|               DATA PREPARATION & STAGING (scripts/00_prepare_data.sh)       |
|  - Clean semicolon-delimited CSV generation (83 stations, 1.45M+ records)   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|               HADOOP HDFS STORAGE LAYER (scripts/01_setup_hdfs.sh)          |
|  - /namma_metro/input/entries/station-hourly-entries.csv (92,280 records)   |
|  - /namma_metro/input/exits/station-hourly-exits.csv     (95,616 records)   |
|  - /namma_metro/input/pairs/stationpair-hourly-enhanced.csv (1.27M records) |
+-----------------------------------------------------------------------------+
         |                                |                            |
         v                                v                            v
+-----------------------+  +-----------------------+  +-----------------------+
|  JAVA MAPREDUCE JOBS  |  |    APACHE HIVE DDL    |  |   APACHE PIG LATIN    |
| (scripts/02_run_mr.sh)|  | (scripts/03_run_hive) |  | (scripts/04_run_pig)  |
|                       |  |                       |  |                       |
| Job 1: StationDemand  |  | DDL: Database & Ext   |  | Pig 1: Station Group  |
| Job 2: HourlyPeaks    |  | Query 1: Footfall Rank|  | Pig 2: Rush Hour Filter|
| Job 3: StationPairs   |  | Query 2: Peak Period  |  | Pig 3: High-Vol Routes|
|                       |  | Query 3: OD Revenues  |  |                       |
+-----------------------+  +-----------------------+  +-----------------------+
         |                                |                            |
         +--------------------------------+----------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|               VERIFIED BIG DATA OUTPUT ARTIFACTS (outputs/)                 |
|  - MapReduce part-r-00000 files                                             |
|  - Hive analytical CSV tables                                               |
|  - Pig Latin transformation outputs                                         |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|             INTERACTIVE VISUALIZATION LAYER (dashboard/app.py)              |
|  - Streamlit & Plotly Dashboard for Academic Demonstration & Viva Voice     |
+-----------------------------------------------------------------------------+
```

---

## 4. Dataset Description & Schema

### Observation Dates
- **August 2025:** August 1, 2025 to August 18, 2025 (Entries, Exits, and Origin-Destination Pairs).
- **September 2025:** September 1, 2025 to September 30, 2025 (Entries and Exits).

### Data Dictionaries

#### 1. Station Hourly Entries / Exits
- `Date` (STRING): Date of passenger flow in `YYYY-MM-DD`.
- `Hour` (INT): Operating hour of day from `0` to `23`.
- `Station` (STRING): Unique name of metro station (83 unique stations across Purple, Green, and Yellow lines).
- `Ridership` (BIGINT): Passenger count recorded by AFC automated fare gates during that hour.

#### 2. Station-Pair Hourly (Enhanced)
- `Date` (STRING): Observation Date in `YYYY-MM-DD`.
- `Hour` (INT): Operating hour from `0` to `23`.
- `Origin Station` (STRING): Boarding metro station.
- `Destination Station` (STRING): Alighting metro station.
- `Ridership` (BIGINT): Number of passenger journeys between this station pair.
- `Travelled Stations` (INT): Shortest path topological station hops excluding origin.
- `Fare Slab` (INT): BMRCL fare slab code (1 to 10).
- `Fare` (INT): Standard ticket fare in INR (₹10 to ₹90).
- `Revenue` (BIGINT): Estimated fare box revenue (`Ridership * Fare`).

---

## 5. MapReduce Algorithms & Implementation

### Job 1: StationDemandAggregation (`StationDemandAggregation.java`)
- **Mapper:** Reads each CSV record, extracts `Station` and `Ridership`. Emits `(Text(station), LongWritable(ridership))`.
- **Combiner & Reducer:** Sums passenger counts for each unique station key.
- **Complexity:** $O(N)$ map phase, $O(M \log M)$ reduce phase where $N \approx 92,280$, $M = 83$.

### Job 2: HourlyPeakAnalysis (`HourlyPeakAnalysis.java`)
- **Mapper:** Extracts `Hour` ($0 \le h \le 23$) and `Ridership`. Formats interval `Hour-HH:00_to_HH:00`. Emits `(Text(hourKey), LongWritable(ridership))`.
- **Reducer:** Sums traffic for each 60-minute window and classifies the period into:
  - `MORNING_PEAK`: 08:00 to 11:00
  - `EVENING_PEAK`: 17:00 to 21:00
  - `REGULAR_OPERATING`: 05:00 to 23:00
  - `OFF_HOURS_NIGHT`: 23:00 to 05:00

### Job 3: StationPairRanking (`StationPairRanking.java`)
- **Mapper:** Extracts `Origin Station`, `Destination Station`, `Ridership`, and `Revenue`. Emits composite key `(Text(Origin -> Destination), Text(ridership + "," + revenue))`.
- **Reducer:** Sums passenger flows and total revenue across all matching journeys.
- **Output:** 6,888 unique station-pair routes ranked by traffic demand.

---

## 6. Key Analytical Findings (Computed from Actual Data)

1. **Total System Volume:**
   - Total Recorded Passenger Boardings: **33,837,882**
   - Total Recorded Passenger Alightings: **33,727,301**
   - Total Estimated Fare Revenue: **₹570,747,160**

2. **Top 5 Busiest Stations by Passenger Demand:**
   - 1. **Nadaprabhu Kempegowda Station, Majestic (Interchange):** 1,649,530 entries (busiest hub in Karnataka)
   - 2. **Benniganahalli:** 1,250,656 entries
   - 3. **Indiranagar:** 1,048,936 entries
   - 4. **Mahatma Gandhi Road:** 1,007,176 entries
   - 5. **Krishnarajapura (KR Puram):** 904,508 entries

3. **Commute Peak Patterns:**
   - **Morning Peak Window (08:00 - 11:00):** Accounts for over 28% of total daily boardings, driven by workplace traffic toward Whitefield and central business districts.
   - **Evening Peak Window (17:00 - 21:00):** Sustained multi-hour outbound flow with peak congestion on the East-West Purple corridor.

4. **Corridor Footfall Comparison:**
   - **Purple Line (37 Stations):** 37,793,117 total passenger footfall (52.3% of network traffic).
   - **Green Line (32 Stations):** 29,651,441 total passenger footfall (41.0% of network traffic).
   - **Yellow Line (16 Stations):** 4,808,765 total passenger footfall (6.7% of network traffic).

---

## 7. Project Limitations & Ethical Data Attribution

- **Observation Boundary:** Analysis is strictly bounded to the official RTI observation periods (August 1–18, 2025 and September 1–30, 2025).
- **Non-Real-Time Data:** BMRCL does not publish live real-time APIs for hour-by-hour station AFC gates. This project does not claim real-time tracking or future machine learning forecasting without longitudinal ground truth.
- **Attribution:** Data was obtained via Right to Information disclosure by BMRCL and curated in open-source by [github.com/Vonter/bmrcl-ridership-hourly](https://github.com/Vonter/bmrcl-ridership-hourly) under the Open Database License (ODbL).
