-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Hive Analytics Script
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Analytics 1: Station-wise Passenger Demand & Footfall Ranking
-- =============================================================================

USE namma_metro_db;

-- Query 1: Top 15 Busiest Metro Stations by Total Boarding Entries
SELECT 
    station_name,
    COUNT(DISTINCT ridership_date) AS active_days,
    SUM(ridership) AS total_entries,
    ROUND(AVG(ridership), 2) AS avg_hourly_entries
FROM station_hourly_entries
WHERE ridership > 0
GROUP BY station_name
ORDER BY total_entries DESC
LIMIT 15;

-- Query 2: Top 15 Busiest Metro Stations by Total Alighting Exits
SELECT 
    station_name,
    COUNT(DISTINCT ridership_date) AS active_days,
    SUM(ridership) AS total_exits,
    ROUND(AVG(ridership), 2) AS avg_hourly_exits
FROM station_hourly_exits
WHERE ridership > 0
GROUP BY station_name
ORDER BY total_exits DESC
LIMIT 15;

-- Query 3: Comprehensive Footfall Demand Ranking (Entries + Exits Combined)
WITH entry_agg AS (
    SELECT station_name, SUM(ridership) AS total_entries
    FROM station_hourly_entries
    GROUP BY station_name
),
exit_agg AS (
    SELECT station_name, SUM(ridership) AS total_exits
    FROM station_hourly_exits
    GROUP BY station_name
)
SELECT 
    e.station_name,
    e.total_entries,
    x.total_exits,
    (e.total_entries + x.total_exits) AS total_footfall,
    DENSE_RANK() OVER (ORDER BY (e.total_entries + x.total_exits) DESC) AS footfall_rank
FROM entry_agg e
JOIN exit_agg x ON e.station_name = x.station_name
ORDER BY total_footfall DESC
LIMIT 20;

-- Query 4: Key Interchange Stations Comparison
SELECT 
    e.station_name,
    e.total_entries,
    x.total_exits,
    (e.total_entries + x.total_exits) AS total_footfall
FROM (
    SELECT station_name, SUM(ridership) AS total_entries
    FROM station_hourly_entries
    WHERE station_name IN ('Nadaprabhu Kempegowda Station, Majestic', 'Rashtreeya Vidyalaya Road')
    GROUP BY station_name
) e
JOIN (
    SELECT station_name, SUM(ridership) AS total_exits
    FROM station_hourly_exits
    WHERE station_name IN ('Nadaprabhu Kempegowda Station, Majestic', 'Rashtreeya Vidyalaya Road')
    GROUP BY station_name
) x ON e.station_name = x.station_name;
