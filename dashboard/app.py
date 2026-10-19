"""
Namma Metro Pulse — Big Data Analytics for Passenger Flow and Station Demand in Bengaluru
VTU 7th Semester Big Data Analytics (BCS714D, 2022 Scheme) Academic Project
Interactive Streamlit & Plotly Dashboard
"""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configure Streamlit page
st.set_page_config(
    page_title="Namma Metro Pulse | VTU BCS714D",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(PROJECT_ROOT, "data_cache.json")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

@st.cache_data
def load_cached_data():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return None

data = load_cached_data()

# Custom CSS for clean academic styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 800; color: #1e293b; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.0rem; color: #64748b; margin-bottom: 1.5rem; }
    .vtu-badge { background-color: #ede9fe; color: #6d28d9; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.8rem; }
    .stMetric { background-color: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://english.bmrc.co.in/images/metro/logo-svg.svg", width=180)
    st.markdown("### Namma Metro Pulse")
    st.markdown('<span class="vtu-badge">VTU BCS714D Project</span>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("**Academic Details**")
    st.text("Course: Big Data Analytics (2022 Scheme)")
    st.text("Semester: 7th Semester B.E.")
    st.text("Source: BMRCL RTI Dataset")
    st.text("Period: Aug 1-18 & Sep 1-30, 2025")
    
    st.markdown("---")
    selected_line = st.selectbox(
        "Corridor / Line Filter",
        ["All Corridors", "Purple Line", "Green Line", "Yellow Line"]
    )
    
    st.markdown("---")
    st.info("💡 **Academic Scope Note**: This project performs batch big data analytics using Hadoop MapReduce, Hive, and Pig on official BMRCL RTI records. It does not perform live tracking or unverified forecasts.")

# Header
st.markdown('<div class="main-header">🚇 Namma Metro Pulse — Big Data Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Passenger Flow and Station Demand Analysis in Bengaluru • Hadoop HDFS, MapReduce, Apache Hive & Apache Pig</div>', unsafe_allow_html=True)

if not data:
    st.error("Data cache not found. Please run scripts/00_prepare_data.sh and scripts/02_run_mapreduce.sh first.")
    st.stop()

summary = data["summary"]
lines_stats = summary["lines"]
stations_summary = pd.DataFrame(data["stations_summary"])
top_routes = pd.DataFrame(data["top_routes"])
hourly_labels = data["hourly_labels"]
hourly_purple = data["hourly_purple"]
hourly_green = data["hourly_green"]
hourly_yellow = data["hourly_yellow"]

# Apply Line filter
if selected_line == "Purple Line":
    filtered_stations = stations_summary[stations_summary['lines'].apply(lambda l: 'purple' in l)]
elif selected_line == "Green Line":
    filtered_stations = stations_summary[stations_summary['lines'].apply(lambda l: 'green' in l)]
elif selected_line == "Yellow Line":
    filtered_stations = stations_summary[stations_summary['lines'].apply(lambda l: 'yellow' in l)]
else:
    filtered_stations = stations_summary

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 System Overview",
    "⏰ Hourly & Peak Analysis",
    "🚉 Station Footfall Rankings",
    "🔄 Origin-Destination Corridors",
    "📂 Hadoop & Hive Outputs"
])

# -----------------------------------------------------------------------------
# TAB 1: System Overview
# -----------------------------------------------------------------------------
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Passenger Entries", f"{summary['total_entries']:,}")
    col2.metric("Total Passenger Exits", f"{summary['total_exits']:,}")
    col3.metric("Est. Total Fare Revenue", f"₹{summary['total_revenue']:,}")
    col4.metric("Monitored Stations", f"{summary['station_count']} Stations")

    st.markdown("#### Corridor-wise Passenger Distribution")
    col_p, col_g, col_y = st.columns(3)
    with col_p:
        st.markdown(f"**🟣 Purple Line (37 Stations)**")
        st.write(f"Footfall: **{lines_stats['purple']['total']:,}** ({lines_stats['purple']['entries']:,} in / {lines_stats['purple']['exits']:,} out)")
        st.caption("Challaghatta ↔ Whitefield (Kadugodi)")
    with col_g:
        st.markdown(f"**🟢 Green Line (32 Stations)**")
        st.write(f"Footfall: **{lines_stats['green']['total']:,}** ({lines_stats['green']['entries']:,} in / {lines_stats['green']['exits']:,} out)")
        st.caption("Madavara ↔ Silk Institute")
    with col_y:
        st.markdown(f"**🟡 Yellow Line (16 Stations)**")
        st.write(f"Footfall: **{lines_stats['yellow']['total']:,}** ({lines_stats['yellow']['entries']:,} in / {lines_stats['yellow']['exits']:,} out)")
        st.caption("Rashtreeya Vidyalaya Road ↔ Bommasandra")

    st.markdown("---")
    top10 = filtered_stations.head(10)
    fig_top = px.bar(
        top10,
        x="station",
        y=["entries", "exits"],
        title=f"Top 10 Busiest Stations by Passenger Flow ({selected_line})",
        labels={"value": "Total Passengers", "station": "Metro Station", "variable": "Flow Type"},
        color_discrete_map={"entries": "#a855f7", "exits": "#22c55e"},
        barmode="group"
    )
    fig_top.update_layout(xaxis_tickangle=-30, height=420, margin=dict(t=40, b=80))
    st.plotly_chart(fig_top, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: Hourly & Peak Analysis
# -----------------------------------------------------------------------------
with tab2:
    st.markdown("#### Hourly Passenger Demand Across 24 Operating Hours")
    st.caption("Aggregated by MapReduce Job 2 (HourlyPeakAnalysis) and Hive Analytics Query 2")
    
    # Build Hourly comparison DataFrame
    hours_int = list(range(24))
    purple_total = [hourly_purple['entries'][i] + hourly_purple['exits'][i] for i in range(24)]
    green_total = [hourly_green['entries'][i] + hourly_green['exits'][i] for i in range(24)]
    yellow_total = [hourly_yellow['entries'][i] + hourly_yellow['exits'][i] for i in range(24)]
    
    fig_hourly = go.Figure()
    fig_hourly.add_trace(go.Scatter(x=hourly_labels, y=purple_total, mode='lines+markers', name='Purple Line', line=dict(color='#a855f7', width=3)))
    fig_hourly.add_trace(go.Scatter(x=hourly_labels, y=green_total, mode='lines+markers', name='Green Line', line=dict(color='#22c55e', width=3)))
    fig_hourly.add_trace(go.Scatter(x=hourly_labels, y=yellow_total, mode='lines+markers', name='Yellow Line', line=dict(color='#eab308', width=3)))
    
    fig_hourly.add_vrect(x0="08:00", x1="10:00", fillcolor="rgba(234, 88, 12, 0.15)", line_width=0, annotation_text="Morning Peak (08:00-11:00)", annotation_position="top left")
    fig_hourly.add_vrect(x0="17:00", x1="20:00", fillcolor="rgba(14, 165, 233, 0.15)", line_width=0, annotation_text="Evening Peak (17:00-21:00)", annotation_position="top left")
    
    fig_hourly.update_layout(
        title="24-Hour Passenger Traffic Volume by Metro Corridor",
        xaxis_title="Time Interval (Hour of Day)",
        yaxis_title="Total Commuters",
        hovermode="x unified",
        height=450
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

    col_peak1, col_peak2 = st.columns(2)
    with col_peak1:
        st.markdown("##### Morning Commute Characteristics (08:00 - 11:00)")
        st.markdown("""
        - Peak workplace travel driven by tech and commercial hubs.
        - High boarding concentration at residential terminals (Kengeri, Nagasandra, Whitefield).
        - High alightings at office hubs (Indiranagar, MG Road, Benniganahalli, Silk Board).
        """)
    with col_peak2:
        st.markdown("##### Evening Commute Characteristics (17:00 - 21:00)")
        st.markdown("""
        - Return journey flow with widespread boarding across central commercial corridors.
        - Primary transfer load on Majestic interchange connecting East-West and North-South lines.
        """)

# -----------------------------------------------------------------------------
# TAB 3: Station Footfall Rankings
# -----------------------------------------------------------------------------
with tab3:
    st.markdown("#### Station Passenger Footfall Leaderboard")
    
    st_table = filtered_stations[['station', 'entries', 'exits', 'total', 'is_interchange']].copy()
    st_table.columns = ['Station Name', 'Total Entries', 'Total Exits', 'Combined Footfall', 'Interchange Station']
    st.dataframe(st_table.style.format({'Total Entries': '{:,}', 'Total Exits': '{:,}', 'Combined Footfall': '{:,}'}), use_container_width=True, height=350)
    
    st.markdown("---")
    st.markdown("#### Individual Station Flow Inspector")
    chosen_station = st.selectbox("Select Station to Inspect", filtered_stations['station'].tolist())
    
    st_data = data['station_hourly_lookup'].get(chosen_station, {'entries': [0]*24, 'exits': [0]*24})
    fig_st = go.Figure()
    fig_st.add_trace(go.Bar(x=hourly_labels, y=st_data['entries'], name='Entries (Boardings)', marker_color='#a855f7'))
    fig_st.add_trace(go.Bar(x=hourly_labels, y=st_data['exits'], name='Exits (Alightings)', marker_color='#22c55e'))
    fig_st.update_layout(
        title=f"Hourly Passenger Profile for {chosen_station}",
        barmode='group',
        xaxis_title="Hour of Day",
        yaxis_title="Passengers",
        height=380
    )
    st.plotly_chart(fig_st, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 4: Origin-Destination Corridors
# -----------------------------------------------------------------------------
with tab4:
    st.markdown("#### Busiest Origin-Destination Journeys")
    st.caption("Aggregated by MapReduce Job 3 (StationPairRanking) and Pig Script 3 (High-Traffic Routes)")
    
    min_ridership = st.slider("Filter Minimum Ridership:", min_value=1000, max_value=50000, value=5000, step=1000)
    filtered_pairs = top_routes[top_routes['Ridership'] >= min_ridership]
    
    fig_pairs = px.scatter(
        filtered_pairs.head(30),
        x="Travelled Stations",
        y="Ridership",
        size="Revenue",
        color="Fare",
        hover_name="Origin Station",
        hover_data=["Destination Station", "Fare", "Revenue"],
        title="Top OD Routes: Travelled Stations vs. Passenger Volume (Bubble Size = Total Revenue)",
        color_continuous_scale="Viridis",
        height=420
    )
    st.plotly_chart(fig_pairs, use_container_width=True)
    
    st.dataframe(
        filtered_pairs[['Origin Station', 'Destination Station', 'Travelled Stations', 'Fare', 'Ridership', 'Revenue']]
        .style.format({'Ridership': '{:,}', 'Revenue': '₹{:,}', 'Fare': '₹{}'}),
        use_container_width=True,
        height=350
    )

# -----------------------------------------------------------------------------
# TAB 5: Hadoop & Hive Outputs
# -----------------------------------------------------------------------------
with tab5:
    st.markdown("#### Verified VTU Project Execution Artifacts")
    st.caption("Inspect genuine execution results generated by Hadoop HDFS, Java MapReduce, Hive, and Pig")
    
    out_tab1, out_tab2, out_tab3, out_tab4 = st.tabs([
        "HDFS Storage Verification",
        "MapReduce Job Outputs",
        "Hive Analytics Outputs",
        "Pig Latin Outputs"
    ])
    
    with out_tab1:
        hdfs_log = os.path.join(OUTPUTS_DIR, "hdfs_verification.txt")
        if os.path.exists(hdfs_log):
            st.code(open(hdfs_log).read(), language="text")
        else:
            st.warning("Run scripts/01_setup_hdfs.sh to generate HDFS verification log.")
            
    with out_tab2:
        mr_choice = st.radio("Select MapReduce Job Output:", ["Job 1: Station Demand", "Job 2: Hourly Peaks", "Job 3: Station Pairs"])
        if mr_choice == "Job 1: Station Demand":
            p = os.path.join(OUTPUTS_DIR, "mapreduce", "job1_station_demand", "part-r-00000")
        elif mr_choice == "Job 2: Hourly Peaks":
            p = os.path.join(OUTPUTS_DIR, "mapreduce", "job2_hourly_peaks", "part-r-00000")
        else:
            p = os.path.join(OUTPUTS_DIR, "mapreduce", "job3_station_pairs", "part-r-00000")
        
        if os.path.exists(p):
            lines = open(p).readlines()[:40]
            st.code("".join(lines), language="text")
            st.caption(f"Showing first 40 lines of {os.path.basename(os.path.dirname(p))}/part-r-00000")
        else:
            st.warning(f"File not found: {p}")
            
    with out_tab3:
        st.markdown("**Hive Query Results (outputs/hive/)**")
        top_entries_csv = os.path.join(OUTPUTS_DIR, "hive", "top_15_entry_stations.csv")
        if os.path.exists(top_entries_csv):
            st.dataframe(pd.read_csv(top_entries_csv), use_container_width=True)
            
        st.markdown("**Top 20 OD Routes (outputs/hive/top_20_od_routes.csv)**")
        od_csv = os.path.join(OUTPUTS_DIR, "hive", "top_20_od_routes.csv")
        if os.path.exists(od_csv):
            st.dataframe(pd.read_csv(od_csv), use_container_width=True)
            
    with out_tab4:
        st.markdown("**Pig Latin Transformation Output (outputs/pig/station_footfall_output/part-r-00000)**")
        pig_p = os.path.join(OUTPUTS_DIR, "pig", "station_footfall_output", "part-r-00000")
        if os.path.exists(pig_p):
            st.code("".join(open(pig_p).readlines()[:30]), language="text")
        else:
            st.warning("Run scripts/04_run_pig.sh to generate Pig output.")
