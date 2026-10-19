-- =============================================================================
-- VTU 7th Semester Big Data Analytics (BCS714D) - Apache Pig Latin Script 3
-- Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
-- Transformation: High-Traffic Origin-Destination Corridor Filtering & Fare Aggregation
-- =============================================================================

-- Step 1: Load Enhanced OD Pair Records
raw_pairs = LOAD 'data/csv/stationpair-hourly-enhanced.csv' USING PigStorage(';') AS (
    obs_date:chararray,
    hour:int,
    origin:chararray,
    destination:chararray,
    ridership:long,
    travelled_stations:int,
    fare_slab:int,
    fare:int,
    revenue:long
);

-- Step 2: Filter out header and invalid rows
valid_pairs = FILTER raw_pairs BY (obs_date != 'Date') AND (ridership > 0);

-- Step 3: Group by Origin and Destination Station Route
grouped_routes = GROUP valid_pairs BY (origin, destination);

-- Step 4: Aggregate ridership and total fare revenue for each unique route
route_metrics = FOREACH grouped_routes GENERATE
    FLATTEN(group) AS (origin_station, destination_station),
    SUM(valid_pairs.ridership) AS total_route_ridership,
    SUM(valid_pairs.revenue) AS total_route_revenue;

-- Step 5: Filter high-demand corridors (over 10,000 passenger journeys)
high_demand_corridors = FILTER route_metrics BY total_route_ridership >= 10000;

-- Step 6: Order by ridership in descending order
ranked_corridors = ORDER high_demand_corridors BY total_route_ridership DESC;

-- Step 7: Store the top ranked corridors
STORE ranked_corridors INTO 'outputs/pig/high_traffic_routes_output' USING PigStorage('\t');
