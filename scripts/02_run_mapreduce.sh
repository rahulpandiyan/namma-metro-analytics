#!/bin/bash
# ==============================================================================
# VTU 7th Semester Big Data Analytics (BCS714D) - MapReduce Execution Script
# Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MAPREDUCE_DIR="$PROJECT_ROOT/mapreduce"
JAR_PATH="$MAPREDUCE_DIR/target/namma-metro-pulse.jar"
OUTPUT_DIR="$PROJECT_ROOT/outputs/mapreduce"

# Auto-detect HADOOP_HOME and JAVA_HOME
if [ -z "$HADOOP_HOME" ]; then
    if [ -d "/home/rahul/hadoop" ]; then
        export HADOOP_HOME="/home/rahul/hadoop"
    elif [ -d "/usr/local/hadoop" ]; then
        export HADOOP_HOME="/usr/local/hadoop"
    fi
fi
if [ -z "$JAVA_HOME" ]; then
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
fi

HADOOP_BIN="$HADOOP_HOME/bin/hadoop"

echo "=========================================================="
echo "Stage 2: Running Hadoop MapReduce Jobs (Java)"
echo "HADOOP_HOME: $HADOOP_HOME"
echo "JAR:         $JAR_PATH"
echo "=========================================================="

# Build JAR if missing
if [ ! -f "$JAR_PATH" ]; then
    echo "MapReduce JAR not found. Building with javac..."
    bash "$MAPREDUCE_DIR/build.sh"
fi

# Detect HDFS Root
if $HADOOP_BIN fs -ls hdfs://localhost:9000/ >/dev/null 2>&1; then
    HDFS_ROOT="hdfs://localhost:9000/namma_metro"
else
    HDFS_ROOT="$PROJECT_ROOT/hdfs_storage/namma_metro"
fi

HDFS_INPUT="$HDFS_ROOT/input"
HDFS_OUTPUT="$HDFS_ROOT/output"

mkdir -p "$OUTPUT_DIR"

# ------------------------------------------------------------------------------
# JOB 1: Station-wise Passenger Demand Aggregation
# ------------------------------------------------------------------------------
echo ""
echo "----------------------------------------------------------"
echo "Executing Job 1: StationDemandAggregation"
echo "Input:  $HDFS_INPUT/entries"
echo "Output: $HDFS_OUTPUT/job1_station_demand"
echo "----------------------------------------------------------"
$HADOOP_BIN fs -rm -r -f "$HDFS_OUTPUT/job1_station_demand" || true
$HADOOP_BIN jar "$JAR_PATH" org.vtu.nammametro.StationDemandAggregation \
    "$HDFS_INPUT/entries" \
    "$HDFS_OUTPUT/job1_station_demand"

mkdir -p "$OUTPUT_DIR/job1_station_demand"
$HADOOP_BIN fs -copyToLocal -f "$HDFS_OUTPUT/job1_station_demand/part-r-00000" "$OUTPUT_DIR/job1_station_demand/"
echo "Job 1 complete. Sample output:"
head -n 5 "$OUTPUT_DIR/job1_station_demand/part-r-00000"

# ------------------------------------------------------------------------------
# JOB 2: Hourly and Day-wise Peak Passenger Analysis
# ------------------------------------------------------------------------------
echo ""
echo "----------------------------------------------------------"
echo "Executing Job 2: HourlyPeakAnalysis"
echo "Input:  $HDFS_INPUT/entries"
echo "Output: $HDFS_OUTPUT/job2_hourly_peaks"
echo "----------------------------------------------------------"
$HADOOP_BIN fs -rm -r -f "$HDFS_OUTPUT/job2_hourly_peaks" || true
$HADOOP_BIN jar "$JAR_PATH" org.vtu.nammametro.HourlyPeakAnalysis \
    "$HDFS_INPUT/entries" \
    "$HDFS_OUTPUT/job2_hourly_peaks"

mkdir -p "$OUTPUT_DIR/job2_hourly_peaks"
$HADOOP_BIN fs -copyToLocal -f "$HDFS_OUTPUT/job2_hourly_peaks/part-r-00000" "$OUTPUT_DIR/job2_hourly_peaks/"
echo "Job 2 complete. Sample output:"
head -n 5 "$OUTPUT_DIR/job2_hourly_peaks/part-r-00000"

# ------------------------------------------------------------------------------
# JOB 3: Origin-Destination Station-Pair Ranking
# ------------------------------------------------------------------------------
echo ""
echo "----------------------------------------------------------"
echo "Executing Job 3: StationPairRanking"
echo "Input:  $HDFS_INPUT/pairs"
echo "Output: $HDFS_OUTPUT/job3_station_pairs"
echo "----------------------------------------------------------"
$HADOOP_BIN fs -rm -r -f "$HDFS_OUTPUT/job3_station_pairs" || true
$HADOOP_BIN jar "$JAR_PATH" org.vtu.nammametro.StationPairRanking \
    "$HDFS_INPUT/pairs" \
    "$HDFS_OUTPUT/job3_station_pairs"

mkdir -p "$OUTPUT_DIR/job3_station_pairs"
$HADOOP_BIN fs -copyToLocal -f "$HDFS_OUTPUT/job3_station_pairs/part-r-00000" "$OUTPUT_DIR/job3_station_pairs/"
echo "Job 3 complete. Sample output:"
head -n 5 "$OUTPUT_DIR/job3_station_pairs/part-r-00000"

echo ""
echo "=========================================================="
echo "SUCCESS: All 3 Java MapReduce jobs completed successfully!"
echo "Outputs stored locally in:"
echo "  - $OUTPUT_DIR/job1_station_demand/part-r-00000"
echo "  - $OUTPUT_DIR/job2_hourly_peaks/part-r-00000"
echo "  - $OUTPUT_DIR/job3_station_pairs/part-r-00000"
echo "=========================================================="
