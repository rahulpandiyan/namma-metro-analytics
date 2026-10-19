-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Hive Analytics Script
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Analytics 3: Origin-Destination Pair Traffic & Fare Revenue Ranking
-- =============================================================================

USE namma_metro_db;

-- Query 1: Top 20 Origin-Destination Commute Corridors by Passenger Ridership
SELECT 
    origin_station,
    destination_station,
    travelled_stations,
    fare,
    SUM(ridership) AS total_passengers,
    SUM(revenue) AS total_fare_revenue_inr,
    DENSE_RANK() OVER (ORDER BY SUM(ridership) DESC) AS route_ridership_rank
FROM stationpair_hourly_enhanced
GROUP BY origin_station, destination_station, travelled_stations, fare
ORDER BY total_passengers DESC
LIMIT 20;

-- Query 2: Top 15 Highest Revenue Generating Corridors
SELECT 
    origin_station,
    destination_station,
    travelled_stations,
    fare,
    SUM(ridership) AS total_passengers,
    SUM(revenue) AS total_fare_revenue_inr
FROM stationpair_hourly_enhanced
GROUP BY origin_station, destination_station, travelled_stations, fare
ORDER BY total_fare_revenue_inr DESC
LIMIT 15;

-- Query 3: Overall Revenue, Average Trip Distance & Fare Metrics
SELECT 
    COUNT(DISTINCT origin_station) AS unique_origins,
    COUNT(DISTINCT destination_station) AS unique_destinations,
    SUM(ridership) AS total_od_passengers,
    SUM(revenue) AS total_system_revenue_inr,
    ROUND(SUM(travelled_stations * ridership) / SUM(ridership), 2) AS weighted_avg_travelled_stations,
    ROUND(SUM(revenue) / SUM(ridership), 2) AS weighted_avg_fare_per_passenger
FROM stationpair_hourly_enhanced;

-- Query 4: Fare Slab Distribution (BMRCL Slabs 1 through 10)
SELECT 
    fare_slab,
    fare,
    SUM(ridership) AS passengers_in_slab,
    SUM(revenue) AS revenue_in_slab,
    ROUND(SUM(ridership) * 100.0 / (SELECT SUM(ridership) FROM stationpair_hourly_enhanced), 2) AS pct_of_total_ridership
FROM stationpair_hourly_enhanced
GROUP BY fare_slab, fare
ORDER BY fare_slab ASC;
