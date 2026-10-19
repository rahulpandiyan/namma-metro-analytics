# Namma Metro Pulse — Big Data Analytics for Passenger Flow and Station Demand in Bengaluru

**VTU 7th Semester Big Data Analytics (BCS714D, 2022 Scheme) Academic Project**

[![Hadoop](https://img.shields.io/badge/Hadoop-3.3.6-F08705.svg?logo=apachehadoop)](https://hadoop.apache.org/)
[![Java MapReduce](https://img.shields.io/badge/MapReduce-Java%2017-ED8B00.svg?logo=java)](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
[![Hive](https://img.shields.io/badge/Hive-SQL%20Analytics-FDEE21.svg?logo=apachehive)](https://hive.apache.org/)
[![Pig](https://img.shields.io/badge/Pig-Pig%20Latin-E65225.svg)](https://pig.apache.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit%20%2B%20Plotly-FF4B4B.svg?logo=streamlit)](https://streamlit.io/)

---

## 📌 Project Overview

**Namma Metro Pulse** is a complete, working academic big data analytics project designed for the **Visvesvaraya Technological University (VTU) 7th Semester B.E. Big Data Analytics course (BCS714D, 2022 Scheme)**.

The project processes, aggregates, and visualizes actual station-wise and origin-destination hourly ridership data from the **Namma Metro (BMRCL)** subway network in Bengaluru, India.

### VTU BCS714D Syllabus Mapping
- **Module 1 (Big Data & HDFS):** Hadoop HDFS storage hierarchy, replication, dataset upload, and verification commands (`scripts/01_setup_hdfs.sh`).
- **Module 2 (MapReduce):** 3 genuine Java Hadoop MapReduce jobs (`mapreduce/src/main/java/org/vtu/nammametro/`).
- **Module 3 (Apache Hive):** External tables, partitioning, aggregation, dense ranking, and fare revenue queries (`hive/*.hql`).
- **Module 4 (Apache Pig):** Pig Latin scripts for filtering, grouping, and relational algebra transformations (`pig/*.pig`).
- **Module 5 (Visualization):** Interactive Streamlit and Plotly analytical dashboard (`dashboard/app.py`).

---

## 🏗️ System Architecture

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

## ⚡ Quick Start: Master Workflow

To run the entire end-to-end Big Data pipeline with a single command:

```bash
cd /home/rahul/Downloads/bmrcl-ridership-hourly
bash run_all.sh
```

This single command will sequentially:
1. Extract and stage clean CSV files.
2. Initialize Hadoop HDFS storage directories and verify files.
3. Compile Java source files with `javac` and execute all 3 MapReduce jobs.
4. Execute Hive analytical queries and export results.
5. Execute Apache Pig Latin scripts and store `part-r-00000` outputs.
6. Launch the interactive Streamlit dashboard at `http://localhost:8501`.

---

## 📁 Repository Structure

```
.
├── run_all.sh                     # Master automated execution script
├── requirements.txt               # Python dependencies (Streamlit, Plotly, Pandas)
├── pom.xml                        # Maven project descriptor for Java MapReduce
│
├── mapreduce/                     # Java Hadoop MapReduce Programs (Module 2)
│   ├── src/main/java/org/vtu/nammametro/
│   │   ├── StationDemandAggregation.java  # Job 1: Station Footfall Aggregation
│   │   ├── HourlyPeakAnalysis.java        # Job 2: 24-Hour Peak Period Classification
│   │   └── StationPairRanking.java        # Job 3: Origin-Destination Corridor Ranking
│   ├── build.sh                           # Build script using javac and Hadoop classpath
│   └── target/namma-metro-pulse.jar       # Compiled MapReduce JAR file
│
├── hive/                          # Apache Hive Analytics (Module 3)
│   ├── 01_create_database_tables.hql      # Database & External Tables DDL
│   ├── 02_station_demand_analytics.hql    # Footfall rankings & interchange analysis
│   ├── 03_hourly_peak_analytics.hql       # System-wide hourly volume & peak slots
│   └── 04_od_pair_revenue_analytics.hql   # OD routes, distance & fare revenue queries
│
├── pig/                           # Apache Pig Latin Scripts (Module 4)
│   ├── 01_station_footfall.pig            # Filter & group by station demand
│   ├── 02_hourly_distribution.pig         # Hourly volume & operating slot profile
│   └── 03_high_traffic_routes.pig         # High-demand OD journey filter & rank
│
├── dashboard/                     # Interactive Academic Dashboard (Module 5)
│   └── app.py                             # Streamlit & Plotly analytics dashboard
│
├── scripts/                       # Modular Workflow Scripts
│   ├── 00_prepare_data.sh                 # CSV extraction & record verification
│   ├── 01_setup_hdfs.sh                   # HDFS directory creation & upload
│   ├── 02_run_mapreduce.sh                # MapReduce build & execution
│   ├── 03_run_hive.sh                     # Hive queries execution
│   ├── 04_run_pig.sh                      # Pig Latin execution
│   └── 05_run_dashboard.sh                # Streamlit dashboard startup
│
├── outputs/                       # Verified Output Artifacts from Genuine Data
│   ├── hdfs_verification.txt              # HDFS upload listing
│   ├── mapreduce/                         # Hadoop MapReduce part-r-00000 files
│   │   ├── job1_station_demand/
│   │   ├── job2_hourly_peaks/
│   │   └── job3_station_pairs/
│   ├── hive/                              # Hive query analytical outputs
│   └── pig/                               # Pig Latin transformation outputs
│
├── docs/                          # Academic Documentation
│   ├── VTU_PROJECT_REPORT.md              # Complete Project Report Outline
│   └── DATA_DICTIONARY.md                 # Schema & observation boundary details
│
├── data/                          # Datasets (CSV, Parquet, Zip)
└── raw/                           # Raw monthly RTI Excel source files
```

---

## 🔬 Component Details & Execution

### 1. Hadoop HDFS Storage (`scripts/01_setup_hdfs.sh`)
Initializes directory structure in HDFS and uploads the datasets:
```bash
bash scripts/01_setup_hdfs.sh
```
- `/namma_metro/input/entries/`: `station-hourly-entries.csv` (92,280 rows)
- `/namma_metro/input/exits/`: `station-hourly-exits.csv` (95,616 rows)
- `/namma_metro/input/pairs/`: `stationpair-hourly-enhanced.csv` (1,273,629 rows)
- Output verification log: `outputs/hdfs_verification.txt`

### 2. Java Hadoop MapReduce Jobs (`scripts/02_run_mapreduce.sh`)
Compiles and executes the 3 Java MapReduce jobs:
```bash
bash scripts/02_run_mapreduce.sh
```

#### Job 1: `StationDemandAggregation.java`
- **Purpose:** Aggregates total passenger boardings (entries) across all 83 stations.
- **Sample Output (`outputs/mapreduce/job1_station_demand/part-r-00000`):**
  ```text
  Nadaprabhu Kempegowda Station, Majestic    1649530
  Benniganahalli                             1250656
  Indiranagar                                1048936
  Mahatma Gandhi Road                        1007176
  Krishnarajapura                             904508
  ```

#### Job 2: `HourlyPeakAnalysis.java`
- **Purpose:** Analyzes passenger demand across 24 hours of operation and classifies rush hour periods.
- **Sample Output (`outputs/mapreduce/job2_hourly_peaks/part-r-00000`):**
  ```text
  Hour-08:00_to_09:00    2783705    MORNING_PEAK
  Hour-09:00_to_10:00    3571167    MORNING_PEAK
  Hour-18:00_to_19:00    3395995    EVENING_PEAK
  Hour-19:00_to_20:00    2987884    EVENING_PEAK
  ```

#### Job 3: `StationPairRanking.java`
- **Purpose:** Aggregates passenger volumes and estimated fare revenues for every origin-destination route.
- **Sample Output (`outputs/mapreduce/job3_station_pairs/part-r-00000`):**
  ```text
  Benniganahalli -> Mahatma Gandhi Road    5229    INR 313740
  Whitefield -> Indiranagar                 8921    INR 535260
  Majestic -> Silk Board                   12410    INR 620500
  ```

### 3. Apache Hive Analytical Queries (`scripts/03_run_hive.sh`)
Executes HiveQL scripts against external tables:
```bash
bash scripts/03_run_hive.sh
```
- Results saved in `outputs/hive/`:
  - `top_15_entry_stations.csv`
  - `station_footfall_ranking.csv`
  - `hourly_passenger_curve.csv`
  - `top_20_od_routes.csv`

### 4. Apache Pig Latin Transformations (`scripts/04_run_pig.sh`)
Executes data flow transformations:
```bash
bash scripts/04_run_pig.sh
```
- Results saved in `outputs/pig/`:
  - `station_footfall_output/part-r-00000`
  - `hourly_distribution_output/part-r-00000`
  - `high_traffic_routes_output/part-r-00000`

### 5. Streamlit Dashboard (`scripts/05_run_dashboard.sh`)
Launches the interactive visualization dashboard:
```bash
bash scripts/05_run_dashboard.sh
```
Access via web browser: **`http://localhost:8501`**

---

## 📈 Genuine Analytical Findings (From Actual Data)

1. **Total Monitored Passenger Volume:**
   - Total Passenger Entries (Boardings): **33,837,882**
   - Total Passenger Exits (Alightings): **33,727,301**
   - Total Estimated Fare Revenue: **₹570,747,160**

2. **Busiest Stations by Footfall:**
   - 1. **Nadaprabhu Kempegowda Station, Majestic:** 1.65 Million entries (Major interchange)
   - 2. **Benniganahalli:** 1.25 Million entries (IT corridor feeder)
   - 3. **Indiranagar:** 1.05 Million entries (Commercial / entertainment hub)
   - 4. **Mahatma Gandhi Road:** 1.01 Million entries (Central Business District)

3. **Peak Commute Patterns:**
   - **Morning Rush Peak (08:00 - 11:00):** Over 28% of total daily boardings occur during these 3 hours.
   - **Evening Rush Peak (17:00 - 21:00):** Sustained return flow across East-West and North-South corridors.

4. **Corridor-wise Footfall:**
   - **Purple Line (37 Stations):** 37,793,117 passengers (52.3%)
   - **Green Line (32 Stations):** 29,651,441 passengers (41.0%)
   - **Yellow Line (16 Stations):** 4,808,765 passengers (6.7%)

---

## ⚠️ Observation Dates & Project Limitations

- **Dataset Observation Boundary:** The dataset covers **August 1–18, 2025** and **September 1–30, 2025**.
- **No Real-Time Claims:** BMRCL does not provide a public real-time API for station AFC gates. The project performs batch big data analytics on official RTI disclosure records.
- **No Unvalidated Forecasting:** This academic project focuses on distributed processing (MapReduce/Hive/Pig) rather than speculative machine learning forecasting.

---

## 📜 Attribution & License

- **Source Data:** Provided by Bangalore Metro Rail Corporation Limited (BMRCL) under the Right to Information Act, 2005.
- **Repository Reference:** Curated by [Vonter/bmrcl-ridership-hourly](https://github.com/Vonter/bmrcl-ridership-hourly) under the Open Database License (ODbL).
- **Academic Citation:** Designed for VTU 7th Semester B.E. Big Data Analytics (BCS714D, 2022 Scheme).
