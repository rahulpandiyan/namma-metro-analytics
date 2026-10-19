#!/bin/bash
# ==============================================================================
# VTU 7th Semester Big Data Analytics (BCS714D, 2022 Scheme)
# Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
# Master End-to-End Workflow Execution Script
# ==============================================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "================================================================================"
echo "          NAMMA METRO PULSE — BIG DATA ANALYTICS (VTU BCS714D)"
echo "  End-to-End Hadoop HDFS, MapReduce, Hive, Pig & Streamlit Analytics Workflow  "
echo "================================================================================"

# Step 0: Ensure Python virtualenv exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "[Init] Setting up Python virtual environment..."
    python3 -m venv "$PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
    if [ -f "$PROJECT_ROOT/requirements-local.txt" ]; then
        pip install -r "$PROJECT_ROOT/requirements-local.txt"
    else
        pip install -r "$PROJECT_ROOT/requirements.txt"
    fi
fi

# Step 1: Data Preparation
echo ""
echo ">>> [STAGE 0/5] Preparing Raw Datasets into Clean CSV format..."
bash "$PROJECT_ROOT/scripts/00_prepare_data.sh"

# Step 2: HDFS Storage Setup
echo ""
echo ">>> [STAGE 1/5] Setting up Hadoop HDFS Storage & Uploading Datasets..."
bash "$PROJECT_ROOT/scripts/01_setup_hdfs.sh"

# Step 3: Java Hadoop MapReduce Execution
echo ""
echo ">>> [STAGE 2/5] Compiling and Executing 3 Java MapReduce Jobs..."
bash "$PROJECT_ROOT/scripts/02_run_mapreduce.sh"

# Step 4: Apache Hive Analytics
echo ""
echo ">>> [STAGE 3/5] Executing Apache Hive Analytical Queries..."
bash "$PROJECT_ROOT/scripts/03_run_hive.sh"

# Step 5: Apache Pig Latin Transformations
echo ""
echo ">>> [STAGE 4/5] Executing Apache Pig Latin Scripts..."
bash "$PROJECT_ROOT/scripts/04_run_pig.sh"

# Final Step: Launch Dashboard
echo ""
echo "================================================================================"
echo "               ALL BIG DATA PROCESSING STAGES COMPLETED!                        "
echo "================================================================================"
echo "All outputs verified in $PROJECT_ROOT/outputs/"
echo ""
echo "Starting Streamlit Analytics Dashboard on port 8501..."
echo "Press Ctrl+C to terminate the dashboard."
echo "================================================================================"
bash "$PROJECT_ROOT/scripts/05_run_dashboard.sh"
