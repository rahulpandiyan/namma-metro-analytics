-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Pig Latin Script 2
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Transformation: Hourly Passenger Profile & Rush Hour Peak Extraction
-- =============================================================================

-- Step 1: Load Station Hourly Entry Records
raw_entries = LOAD 'data/csv/station-hourly-entries.csv' USING PigStorage(';') AS (
    obs_date:chararray,
    hour:int,
    station:chararray,
    ridership:long
);

-- Step 2: Clean and validate records
clean_records = FILTER raw_entries BY (obs_date != 'Date') AND (hour >= 0 AND hour <= 23);

-- Step 3: Group by Hour of Day (0 to 23)
grouped_by_hour = GROUP clean_records BY hour;

-- Step 4: Aggregate passenger volumes across all 83 stations for each operating hour
hourly_agg = FOREACH grouped_by_hour GENERATE
    group AS operating_hour,
    SUM(clean_records.ridership) AS network_hourly_passengers,
    COUNT(clean_records) AS station_records_count;

-- Step 5: Sort by operating hour sequentially
sorted_hourly = ORDER hourly_agg BY operating_hour ASC;

-- Step 6: Store hourly distribution into output
STORE sorted_hourly INTO 'outputs/pig/hourly_distribution_output' USING PigStorage('\t');
