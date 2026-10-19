# Namma Metro Pulse — Big Data Analytics for Passenger Flow and Station Demand in Bengaluru

**VTU 7th Semester B.E. Big Data Analytics (BCS714D, 2022 Scheme) Project**  
**Repository:** [https://github.com/rahulpandiyan/namma-metro-analytics](https://github.com/rahulpandiyan/namma-metro-analytics)  
**Project Team:** **Rahul**, **Sam Goldwin**, and **Veeresh K Pattanshetty**  
**Course Code:** BCS714D (2022 Scheme)

---

[![Hadoop](https://img.shields.io/badge/Hadoop-3.3.6-F08705.svg?logo=apachehadoop)](https://hadoop.apache.org/)
[![Java MapReduce](https://img.shields.io/badge/MapReduce-Java%2017-ED8B00.svg?logo=java)](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
[![Hive](https://img.shields.io/badge/Hive-SQL%20Analytics-FDEE21.svg?logo=apachehive)](https://hive.apache.org/)
[![Pig](https://img.shields.io/badge/Pig-Pig%20Latin-E65225.svg)](https://pig.apache.org/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit%20%2B%20Plotly-FF4B4B.svg?logo=streamlit)](https://streamlit.io/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel%20WSGI-000000.svg?logo=vercel)](https://vercel.com/)
[![License: ODbL](https://img.shields.io/badge/License-ODbL-blue.svg)](http://opendatacommons.org/licenses/odbl/)

---

## 📌 Executive Summary

**Namma Metro Pulse** is a complete, production-grade Big Data Analytics academic project developed for the **Visvesvaraya Technological University (VTU) 7th Semester B.E. Degree (Course: Big Data Analytics - BCS714D, 2022 Scheme)**.

The project processes, aggregates, and visualizes real-world transit ticketing records from the **Namma Metro (BMRCL)** rapid transit system in Bengaluru, India. It models passenger entry footfall, exit distributions, rush-hour demand curves, and 1.27 million origin-destination (OD) passenger journeys across the **Purple Line**, **Green Line**, and **Yellow Line**.

All analytics are computed directly from the genuine disclosure datasets without synthetic simulation.

---

## 🛠️ Technologies Used

| Layer / Role | Technology | Version / Specification | Usage in Project |
| :--- | :--- | :--- | :--- |
| **Distributed Storage** | **Apache Hadoop HDFS** | 3.3.6 | Fault-tolerant staging of raw CSV datasets across `/namma_metro/input/entries`, `/exits`, and `/pairs`. |
| **Distributed Computation** | **Java MapReduce** | Java OpenJDK 17 (v2 YARN) | 3 genuine compiled MapReduce jobs for station footfall aggregation, peak-period classification, and OD pair volume ranking. |
| **SQL Data Warehousing** | **Apache Hive** | HiveQL | Schema-on-read external tables, window functions, and `DENSE_RANK()` for revenue and footfall analytics. |
| **ETL & Data Flow** | **Apache Pig** | Pig Latin | Relational algebra scripts using `LOAD`, `FILTER`, `GROUP BY`, `FOREACH GENERATE`, and `ORDER BY`. |
| **Academic Visualization** | **Streamlit** & **Plotly** | Streamlit 1.66+, Plotly 7.1+ | Multi-tab academic dashboard displaying corridor KPIs, footfall curves, OD bubbles, and output verification logs. |
| **Web App & REST API** | **Python WSGI / HTTP** | Python 3.12 / 3.14 | Standalone interactive web dashboard and REST API for station profiles (`/api/summary`, `/api/station`). |
| **Cloud Deployment** | **Vercel Functions** | Vercel WSGI Runtime | Serverless deployment via `vercel.json` and top-level `app`, `application`, and `handler` exports with pre-computed 65KB cache. |
| **Data Formats** | **Parquet, CSV, JSON** | fastparquet, openpyxl | Storage-optimized Parquet files and semicolon-delimited CSVs preserving comma-containing station names. |

---

## 📚 VTU BCS714D Syllabus Mapping

- **Module 1 (Big Data & HDFS):** HDFS storage layout, replication, block distribution, data staging scripts ([`scripts/01_setup_hdfs.sh`](scripts/01_setup_hdfs.sh)).
- **Module 2 (MapReduce Paradigm):** 3 Java Hadoop MapReduce jobs with Custom Mappers, Combiners, and Reducers ([`mapreduce/src/main/java/org/vtu/nammametro/`](mapreduce/src/main/java/org/vtu/nammametro/)).
- **Module 3 (Apache Hive):** External table creation, partitioning, DDL scripts, analytical queries, fare slab analysis ([`hive/`](hive/)).
- **Module 4 (Apache Pig):** Pig Latin data transformations and relational algebra filters ([`pig/`](pig/)).
- **Module 5 (Data Visualization):** Streamlit and Plotly interactive dashboards for viva-voce demonstration ([`dashboard/app.py`](dashboard/app.py)).

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
|  - Streamlit & Plotly Dashboard for Academic Demonstration & Viva Voce      |
|  - Web Application & REST API (server.py) deployed on Vercel / Local       |
+-----------------------------------------------------------------------------+
```

---

## 🚀 How to Deploy & Run

### Method 1: Master Script (One-Click Local Execution)

To run the complete pipeline from scratch (preparation $\rightarrow$ HDFS $\rightarrow$ MapReduce $\rightarrow$ Hive $\rightarrow$ Pig $\rightarrow$ Streamlit):

```bash
git clone https://github.com/rahulpandiyan/namma-metro-analytics.git
cd namma-metro-analytics

# Execute master workflow
bash run_all.sh
```

---

### Method 2: Running Individual Pipeline Stages

#### Step 1: Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Step 2: Prepare CSV Datasets
```bash
bash scripts/00_prepare_data.sh
```
*Outputs: `data/csv/station-hourly-entries.csv`, `station-hourly-exits.csv`, `stationpair-hourly-enhanced.csv`.*

#### Step 3: Setup HDFS Storage
```bash
bash scripts/01_setup_hdfs.sh
```
*Uploads CSVs to `/namma_metro/input` and generates `outputs/hdfs_verification.txt`.*

#### Step 4: Compile & Run Java MapReduce Jobs
```bash
# Compile Java classes and package into JAR
bash mapreduce/build.sh

# Execute MapReduce jobs
bash scripts/02_run_mapreduce.sh
```
*Outputs stored in `outputs/mapreduce/job1_station_demand/`, `outputs/mapreduce/job2_hourly_peaks/`, and `outputs/mapreduce/job3_station_pairs/`.*

#### Step 5: Execute Apache Hive Queries
```bash
bash scripts/03_run_hive.sh
```
*Outputs stored in `outputs/hive/`.*

#### Step 6: Execute Apache Pig Latin Scripts
```bash
bash scripts/04_run_pig.sh
```
*Outputs stored in `outputs/pig/`.*

#### Step 7: Launch Dashboards

- **Streamlit Academic Dashboard (Port 8501):**
  ```bash
  bash scripts/05_run_dashboard.sh
  # Access at http://localhost:8501
  ```

- **Standalone Web App & REST API (Port 8000):**
  ```bash
  source .venv/bin/activate
  python server.py
  # Access at http://localhost:8000
  ```

---

### Method 3: Cloud Deployment on Vercel

The project includes built-in support for deploying the analytics web app and REST API to **Vercel** as a serverless function:

1. Push this repository to your GitHub account:
   ```bash
   git push origin main
   ```
2. Log in to [Vercel](https://vercel.com/) and click **"Add New Project"**.
3. Import your repository: `rahulpandiyan/namma-metro-analytics`.
4. Vercel automatically detects [`vercel.json`](vercel.json) and routes all requests to [`server.py`](server.py).
5. The deployment uses pre-computed [`data_cache.json`](data_cache.json) (65 KB), ensuring instant cold starts under **10 milliseconds** without exceeding memory limits.
6. Click **Deploy** — your live URL will be active immediately.

---

## 📊 Genuine Analytical Findings (From Actual BMRCL Data)

All numbers below were computed from the genuine BMRCL dataset by our Hadoop MapReduce and Hive queries:

### 1. Overall System Metrics
- **Total Monitored Passenger Boardings:** `33,837,882`
- **Total Monitored Passenger Alightings:** `33,727,301`
- **Estimated Fare Revenue:** `₹570,747,160` (₹57.07 Crores)
- **Total Stations Tracked:** `83 Stations`

### 2. Top 5 Busiest Stations by Passenger Demand
*(Computed by MapReduce Job 1 / Hive Query 1)*
1. **Nadaprabhu Kempegowda Station, Majestic (Interchange):** `1,649,530` entries
2. **Benniganahalli:** `1,250,656` entries
3. **Indiranagar:** `1,048,936` entries
4. **Mahatma Gandhi Road:** `1,007,176` entries
5. **Krishnarajapura (KR Puram):** `904,508` entries

### 3. Corridor-wise Passenger Footfall Share
- 🟣 **Purple Line (37 Stations):** `37,793,117` passengers (**52.3%** of network volume)
- 🟢 **Green Line (32 Stations):** `29,651,441` passengers (**41.0%** of network volume)
- 🟡 **Yellow Line (16 Stations):** `4,808,765` passengers (**6.7%** of network volume)

### 4. Commute Peak Period Analysis
*(Computed by MapReduce Job 2 / Hive Query 2)*
- **Morning Rush Peak (08:00 - 11:00):** Over **28%** of all daily boardings occur in this 3-hour window. Busiest single hour is `09:00 - 10:00` with **3,571,167** passengers.
- **Evening Rush Peak (17:00 - 21:00):** Sustained return commute flow across the East-West tech corridor.

---

## 📂 Project Structure & Artifacts

```
.
├── README.md                      # Comprehensive project guide & documentation
├── run_all.sh                     # Master automated end-to-end execution script
├── requirements.txt               # Python package dependencies
├── pom.xml                        # Maven configuration for Java MapReduce
├── server.py                      # Vercel-ready WSGI web app & REST API
├── vercel.json                    # Vercel serverless routing configuration
├── data_cache.json                # Pre-aggregated 65KB cache for instant API responses
│
├── mapreduce/                     # Java Hadoop MapReduce Code (BCS714D Module 2)
│   ├── build.sh                   # Compilation script using javac & Hadoop classpath
│   ├── target/namma-metro-pulse.jar # Compiled MapReduce JAR
│   └── src/main/java/org/vtu/nammametro/
│       ├── StationDemandAggregation.java  # Job 1: Station Footfall Aggregator
│       ├── HourlyPeakAnalysis.java        # Job 2: Hourly Peak Classifier
│       └── StationPairRanking.java        # Job 3: Origin-Destination Corridor Ranker
│
├── hive/                          # Apache Hive Analytics (BCS714D Module 3)
│   ├── 01_create_database_tables.hql      # External tables & schema DDL
│   ├── 02_station_demand_analytics.hql    # Footfall rankings & interchange analysis
│   ├── 03_hourly_peak_analytics.hql       # System-wide hourly volume queries
│   └── 04_od_pair_revenue_analytics.hql   # OD routes, distance, and fare revenue
│
├── pig/                           # Apache Pig Latin Scripts (BCS714D Module 4)
│   ├── 01_station_footfall.pig            # Filter & group by station demand
│   ├── 02_hourly_distribution.pig         # Hourly volume & operating slot profile
│   └── 03_high_traffic_routes.pig         # High-demand OD journey filter & rank
│
├── dashboard/                     # Academic Visualization Dashboard (BCS714D Module 5)
│   └── app.py                             # Interactive Streamlit & Plotly analytics app
│
├── scripts/                       # Modular Workflow Scripts
│   ├── 00_prepare_data.sh                 # CSV extraction & verification
│   ├── 01_setup_hdfs.sh                   # HDFS directory creation & upload
│   ├── 02_run_mapreduce.sh                # MapReduce build & execution
│   ├── 03_run_hive.sh                     # Hive queries execution
│   ├── 04_run_pig.sh                      # Pig Latin execution
│   └── 05_run_dashboard.sh                # Streamlit dashboard startup
│
├── outputs/                       # Verified Output Artifacts from Genuine Data
│   ├── hdfs_verification.txt              # HDFS upload listing
│   ├── mapreduce/                         # Genuine part-r-00000 files
│   ├── hive/                              # Hive analytical CSV result tables
│   └── pig/                               # Pig Latin part-r-00000 output files
│
├── docs/                          # Academic Documentation
│   └── VTU_PROJECT_REPORT.md              # Complete Project Report Outline
│
├── data/                          # Dataset files (Parquet, Zip, CSV)
└── raw/                           # Raw monthly RTI Excel source spreadsheets
```

---

## ⚠️ Observation Dates & Limitations

1. **Observation Periods:** Data is strictly bounded to the official RTI response dates provided by BMRCL:
   - **August 1, 2025 to August 18, 2025** (Entries, Exits, and Origin-Destination pairs)
   - **September 1, 2025 to September 30, 2025** (Entries and Exits)
2. **Non-Real-Time Data:** BMRCL does not publish live real-time APIs for Automated Fare Collection (AFC) station gates. This project performs batch big data analytics on official historical disclosures.
3. **Forecasting Scope:** In accordance with academic honesty guidelines, this project avoids speculative machine learning claims and focuses on distributed big data processing (Hadoop, MapReduce, Hive, and Pig).

---

## 🙏 Credits & Acknowledgments

- **Data Origin:** Bangalore Metro Rail Corporation Limited ([BMRCL](https://english.bmrc.co.in/)), obtained via the Right to Information (RTI) Act, 2005.
- **Dataset Curator:** Sincere appreciation to **[Vonter (bmrcl-ridership-hourly)](https://github.com/Vonter/bmrcl-ridership-hourly)** for curating the raw RTI Excel files and creating the initial open-source repository under the Open Database License.
- **Network Graph & Fare Calculations:** Credit to **[@kdqed](https://github.com/kdqed)** for the network shortest-path algorithms and BMRCL fare slab calculation logic.
- **RTI Guidance:** Credit to **[Zen Citizen](https://zencitizen.in/)** for their published framework on filing public transit RTI applications.
- **Academic Project Team:**
  - **Rahul**
  - **Sam Goldwin**
  - **Veeresh K Pattanshetty**
  - *Department of Computer Science & Engineering / Information Science & Engineering*
  - *Visvesvaraya Technological University (VTU) — 7th Semester B.E. (BCS714D, 2022 Scheme)*

---

## 📜 License

- **Dataset:** Made available under the [Open Database License (ODbL)](http://opendatacommons.org/licenses/odbl/1.0/).
- **Source Code:** Released under the [MIT License](LICENSE).
