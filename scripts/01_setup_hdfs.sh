#!/bin/bash
# ==============================================================================
# VTU 7th Semester Big Data Analytics (BCS714D) - HDFS Storage Setup Script
# Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CSV_DIR="$PROJECT_ROOT/data/csv"
OUTPUT_DIR="$PROJECT_ROOT/outputs"

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
echo "Stage 1: Setting up Hadoop HDFS Storage for Namma Metro"
echo "HADOOP_HOME: $HADOOP_HOME"
echo "=========================================================="

# Ensure CSVs are prepared
if [ ! -f "$CSV_DIR/station-hourly-entries.csv" ]; then
    echo "CSVs not found. Running preparation script first..."
    bash "$SCRIPT_DIR/00_prepare_data.sh"
fi

# Detect whether HDFS daemon is running (pseudo-distributed/cluster) or Standalone mode
if $HADOOP_BIN fs -ls hdfs://localhost:9000/ >/dev/null 2>&1; then
    HDFS_PREFIX="hdfs://localhost:9000"
    HDFS_ROOT="$HDFS_PREFIX/namma_metro"
    echo "Mode: Hadoop Distributed HDFS Cluster detected ($HDFS_PREFIX)"
else
    # Standalone mode uses dedicated user-owned storage directory
    HDFS_ROOT="$PROJECT_ROOT/hdfs_storage/namma_metro"
    echo "Mode: Hadoop Standalone / Local HDFS storage ($HDFS_ROOT)"
fi

HDFS_INPUT="$HDFS_ROOT/input"
HDFS_OUTPUT="$HDFS_ROOT/output"

echo "[1/4] Creating HDFS directory structure..."
$HADOOP_BIN fs -mkdir -p "$HDFS_INPUT/entries"
$HADOOP_BIN fs -mkdir -p "$HDFS_INPUT/exits"
$HADOOP_BIN fs -mkdir -p "$HDFS_INPUT/pairs"
$HADOOP_BIN fs -mkdir -p "$HDFS_OUTPUT"

echo "[2/4] Uploading station-hourly entry dataset to HDFS..."
$HADOOP_BIN fs -put -f "$CSV_DIR/station-hourly-entries.csv" "$HDFS_INPUT/entries/"

echo "[3/4] Uploading station-hourly exit dataset to HDFS..."
$HADOOP_BIN fs -put -f "$CSV_DIR/station-hourly-exits.csv" "$HDFS_INPUT/exits/"

echo "[4/4] Uploading stationpair enhanced dataset to HDFS..."
$HADOOP_BIN fs -put -f "$CSV_DIR/stationpair-hourly-enhanced.csv" "$HDFS_INPUT/pairs/"

echo ""
echo "=========================================================="
echo "HDFS Verification Output:"
echo "=========================================================="
mkdir -p "$OUTPUT_DIR"
$HADOOP_BIN fs -ls -R "$HDFS_ROOT" | tee "$OUTPUT_DIR/hdfs_verification.txt"

echo ""
echo "SUCCESS: Datasets verified and stored in Hadoop HDFS."
echo "Log saved to: $OUTPUT_DIR/hdfs_verification.txt"
echo "HDFS_ROOT:    $HDFS_ROOT"
echo "=========================================================="
