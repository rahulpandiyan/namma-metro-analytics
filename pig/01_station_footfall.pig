-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Pig Latin Script 1
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Transformation: Station-wise Passenger Demand Filtering and Aggregation
-- =============================================================================

-- Step 1: Load Station Hourly Entry Records
raw_entries = LOAD 'data/csv/station-hourly-entries.csv' USING PigStorage(';') AS (
    obs_date:chararray,
    hour:int,
    station:chararray,
    ridership:long
);

-- Step 2: Filter out CSV header and records with zero/negative ridership
valid_entries = FILTER raw_entries BY (obs_date != 'Date') AND (ridership > 0);

-- Step 3: Group by Station Name
grouped_by_station = GROUP valid_entries BY station;

-- Step 4: Aggregate total ridership and count active operational hours
station_totals = FOREACH grouped_by_station GENERATE 
    group AS station_name,
    SUM(valid_entries.ridership) AS total_entries,
    COUNT(valid_entries) AS total_operational_slots;

-- Step 5: Rank stations by total passenger demand in descending order
ranked_stations = ORDER station_totals BY total_entries DESC;

-- Step 6: Store result to output directory
STORE ranked_stations INTO 'outputs/pig/station_footfall_output' USING PigStorage('\t');
