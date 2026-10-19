#!/bin/bash
# ==============================================================================
# VTU 7th Semester Big Data Analytics (BCS714D) - MapReduce Build Script
# Project: Namma Metro Pulse — Big Data Analytics for Passenger Flow
# ==============================================================================
set -e

# Detect or default HADOOP_HOME and JAVA_HOME
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

echo "=========================================================="
echo "Compiling Namma Metro Pulse Java Hadoop MapReduce Jobs"
echo "JAVA_HOME:   $JAVA_HOME"
echo "HADOOP_HOME: $HADOOP_HOME"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/build_classes"
JAR_DIR="$SCRIPT_DIR/target"

mkdir -p "$BUILD_DIR"
mkdir -p "$JAR_DIR"

HADOOP_CP="$($HADOOP_HOME/bin/hadoop classpath)"

echo "[1/2] Compiling Java source files with javac..."
"$JAVA_HOME/bin/javac" -cp "$HADOOP_CP" \
    -d "$BUILD_DIR" \
    "$SCRIPT_DIR/src/main/java/org/vtu/nammametro/"*.java

echo "[2/2] Packaging classes into JAR file..."
"$JAVA_HOME/bin/jar" -cvf "$JAR_DIR/namma-metro-pulse.jar" -C "$BUILD_DIR" .

echo "=========================================================="
echo "SUCCESS: MapReduce JAR generated at:"
echo "  $JAR_DIR/namma-metro-pulse.jar"
echo "Available Jobs:"
echo "  - org.vtu.nammametro.StationDemandAggregation"
echo "  - org.vtu.nammametro.HourlyPeakAnalysis"
echo "  - org.vtu.nammametro.StationPairRanking"
echo "=========================================================="
