#!/bin/bash
# ==============================================================================
# VTU 7th Semester Big Data Analytics (BCS714D) - Dashboard Startup Script
# Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PORT="${PORT:-8501}"

echo "=========================================================="
echo "Stage 5: Launching Namma Metro Pulse Streamlit Dashboard"
echo "Project Root: $PROJECT_ROOT"
echo "Port:         $PORT"
echo "=========================================================="

source "$PROJECT_ROOT/.venv/bin/activate"

streamlit run "$PROJECT_ROOT/dashboard/app.py" \
    --server.port "$PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
