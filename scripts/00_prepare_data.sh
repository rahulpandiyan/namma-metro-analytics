#!/bin/bash
# ==============================================================================
# VTU 7th Semester Big Data Analytics (BCS714D) - Data Preparation Script
# Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_ROOT/data"
CSV_DIR="$DATA_DIR/csv"

echo "=========================================================="
echo "Stage 0: Preparing BMRCL Ridership CSVs for Hadoop"
echo "Project Root: $PROJECT_ROOT"
echo "=========================================================="

mkdir -p "$CSV_DIR"

echo "[1/3] Extracting station hourly entry records..."
unzip -q -o "$DATA_DIR/station-hourly.csv.zip" -d "$CSV_DIR/"
mv "$CSV_DIR/station-hourly.csv" "$CSV_DIR/station-hourly-entries.csv"

echo "[2/3] Extracting station hourly exit records..."
unzip -q -o "$DATA_DIR/station-hourly-exits.csv.zip" -d "$CSV_DIR/"

echo "[3/3] Extracting station pair enhanced records..."
unzip -q -o "$DATA_DIR/stationpair-hourly-enhanced.csv.zip" -d "$CSV_DIR/"

echo ""
echo "Dataset preparation summary:"
ls -lh "$CSV_DIR"
echo "Total records in entries:  $(wc -l < "$CSV_DIR/station-hourly-entries.csv")"
echo "Total records in exits:    $(wc -l < "$CSV_DIR/station-hourly-exits.csv")"
echo "Total records in OD pairs: $(wc -l < "$CSV_DIR/stationpair-hourly-enhanced.csv")"
echo "=========================================================="
echo "Data preparation complete and ready for HDFS upload."
echo "=========================================================="
