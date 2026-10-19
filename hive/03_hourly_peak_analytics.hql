-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Hive Analytics Script
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Analytics 2: Network Hourly Distribution & Peak Period Classification
-- =============================================================================

USE namma_metro_db;

-- Query 1: System-wide 24-Hour Passenger Traffic Curve
SELECT 
    hour_of_day,
    SUM(ridership) AS total_hourly_entries,
    ROUND(SUM(ridership) * 100.0 / (SELECT SUM(ridership) FROM station_hourly_entries), 2) AS pct_of_daily_volume,
    CASE 
        WHEN hour_of_day BETWEEN 8 AND 10 THEN 'Morning Rush Peak'
        WHEN hour_of_day BETWEEN 17 AND 20 THEN 'Evening Rush Peak'
        WHEN hour_of_day BETWEEN 5 AND 23 THEN 'Standard Operating Hours'
        ELSE 'Off-Hours Night'
    END AS period_type
FROM station_hourly_entries
GROUP BY hour_of_day
ORDER BY hour_of_day ASC;

-- Query 2: Peak Hours vs Non-Peak Operating Comparison
SELECT 
    CASE 
        WHEN hour_of_day BETWEEN 8 AND 10 THEN '1_MORNING_PEAK (08-11)'
        WHEN hour_of_day BETWEEN 17 AND 20 THEN '2_EVENING_PEAK (17-21)'
        WHEN hour_of_day BETWEEN 5 AND 23 THEN '3_REGULAR_DAYTIME'
        ELSE '4_LATE_NIGHT'
    END AS commute_period,
    COUNT(DISTINCT hour_of_day) AS total_hours_in_slot,
    SUM(ridership) AS total_passengers,
    ROUND(AVG(ridership), 2) AS avg_station_hourly_volume
FROM station_hourly_entries
GROUP BY 
    CASE 
        WHEN hour_of_day BETWEEN 8 AND 10 THEN '1_MORNING_PEAK (08-11)'
        WHEN hour_of_day BETWEEN 17 AND 20 THEN '2_EVENING_PEAK (17-21)'
        WHEN hour_of_day BETWEEN 5 AND 23 THEN '3_REGULAR_DAYTIME'
        ELSE '4_LATE_NIGHT'
    END
ORDER BY commute_period ASC;

-- Query 3: Busiest Alighting (Exit) Stations During Morning Peak (08:00 - 11:00)
-- Identifies primary office & IT employment destinations
SELECT 
    station_name,
    SUM(ridership) AS morning_peak_alightings
FROM station_hourly_exits
WHERE hour_of_day BETWEEN 8 AND 10
GROUP BY station_name
ORDER BY morning_peak_alightings DESC
LIMIT 10;
