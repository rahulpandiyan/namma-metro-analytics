-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Hive DDL Script
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Schema definitions for Namma Metro BMRCL Ridership Datasets
-- =============================================================================

CREATE DATABASE IF NOT EXISTS namma_metro_db
COMMENT 'VTU BCS714D Project Database for Namma Metro Analytics';

USE namma_metro_db;

-- Table 1: Station Hourly Entries (Passenger Boardings)
DROP TABLE IF EXISTS station_hourly_entries;
CREATE EXTERNAL TABLE IF NOT EXISTS station_hourly_entries (
    ridership_date STRING COMMENT 'Observation Date YYYY-MM-DD',
    hour_of_day INT COMMENT 'Operating Hour (0-23)',
    station_name STRING COMMENT 'Metro Station Name',
    ridership BIGINT COMMENT 'Number of Passenger Boardings'
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ';'
STORED AS TEXTFILE
LOCATION '/namma_metro/input/entries'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Table 2: Station Hourly Exits (Passenger Alightings)
DROP TABLE IF EXISTS station_hourly_exits;
CREATE EXTERNAL TABLE IF NOT EXISTS station_hourly_exits (
    ridership_date STRING COMMENT 'Observation Date YYYY-MM-DD',
    hour_of_day INT COMMENT 'Operating Hour (0-23)',
    station_name STRING COMMENT 'Metro Station Name',
    ridership BIGINT COMMENT 'Number of Passenger Deboardings'
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ';'
STORED AS TEXTFILE
LOCATION '/namma_metro/input/exits'
TBLPROPERTIES ("skip.header.line.count"="1");

-- Table 3: Station-Pair Hourly Enhanced (Origin-Destination Journeys)
DROP TABLE IF EXISTS stationpair_hourly_enhanced;
CREATE EXTERNAL TABLE IF NOT EXISTS stationpair_hourly_enhanced (
    ridership_date STRING COMMENT 'Observation Date YYYY-MM-DD',
    hour_of_day INT COMMENT 'Operating Hour (0-23)',
    origin_station STRING COMMENT 'Journey Origin Metro Station',
    destination_station STRING COMMENT 'Journey Destination Metro Station',
    ridership BIGINT COMMENT 'Passenger Flow Count',
    travelled_stations INT COMMENT 'Number of Stations Travelled',
    fare_slab INT COMMENT 'BMRCL Fare Slab Code (1-10)',
    fare INT COMMENT 'Ticket Fare per Passenger in INR',
    revenue BIGINT COMMENT 'Estimated Revenue in INR'
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ';'
STORED AS TEXTFILE
LOCATION '/namma_metro/input/pairs'
TBLPROPERTIES ("skip.header.line.count"="1");

SHOW TABLES;
