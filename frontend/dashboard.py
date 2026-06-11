import streamlit as st
import sqlite3
import pandas as pd
import os

# Configure page layout suite
st.set_page_config(page_title="Rakshak AI Dashboard", page_icon="🚆", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ RAKSHAK AI — RAILWAY SAFETY COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>Real-Time Video Analytics & Visual Evidence Database</p>", unsafe_allow_html=True)
st.markdown("---")

def fetch_data():
    if not os.path.exists("database/alerts.db"):
        return pd.DataFrame()
    conn = sqlite3.connect("database/alerts.db")
    df = pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC", conn)
    conn.close()
    return df

df_alerts = fetch_data()

if df_alerts.empty:
    st.info("🛰️ Tracking servers active. Awaiting initial security logs from backend...")
else:
    # System KPIs Metrics Banner
    total_logs = len(df_alerts)
    track_count = len(df_alerts[df_alerts['alert_type'] == 'Track Intrusion'])
    crowd_count = len(df_alerts[df_alerts['alert_type'] == 'Crowd Gathering'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Logged Incidents", value=total_logs)
    with col2:
        st.metric(label="Track Intrusions 🚨", value=track_count)
    with col3:
        st.metric(label="Crowd Gatherings ⚠️", value=crowd_count)
    with col4:
        st.metric(label="System Nodes Active", value="3 Cameras")

    st.markdown("---")

    # =========================================================================
    # INTERFACE INTEGRATION UPGRADE: LIVE SURVEILLANCE DISPLAY TILES (ROW VIEW)
    # =========================================================================
    st.subheader("📺 Real-Time Forensic Video Monitoring Dashboard")
    
    view_col1, view_col2 = st.columns(2)
    
    with view_col1:
        st.markdown("### 🚨 Latest Security Breach Snapshot")
        latest_alert = df_alerts.iloc[0]
        img_path = latest_alert.get('image_path', None)
        
        if img_path and os.path.exists(img_path):
            st.image(img_path, caption=f"Breach Type: {latest_alert['alert_type']} at {latest_alert['timestamp']}", use_container_width=True)
        else:
            st.info("Awaiting initial visual snapshot logs from monitoring node...")

    with view_col2:
        st.markdown("### 🗺️ Dynamic Station Passenger Density Heatmap")
        heatmap_path = "alerts/latest_heatmap.jpg"
        
        if os.path.exists(heatmap_path):
            st.image(heatmap_path, caption="Live Crowd Spatial Pressure Concentration Grid Map", use_container_width=True)
        else:
            st.info("Thermal tracker engine offline. Initialize heatmap.py server to stream live grid canvas.")
    # =========================================================================

    st.markdown("---")

    # Data Analytics Ledger View
    left_column, right_column = st.columns([1, 1])

    with left_column:
        st.subheader("📋 Active Incident Log Ledger")
        st.dataframe(
            df_alerts[['timestamp', 'camera_name', 'alert_type', 'people_count']], 
            use_container_width=True
        )

    with right_column:
        st.subheader("📊 Incident Frequency Breakdown by Camera Station")
        if 'camera_name' in df_alerts.columns:
            camera_chart_data = df_alerts['camera_name'].value_counts()
            st.bar_chart(camera_chart_data)
        else:
            st.write("Gathering analytics trend lines...")

# Action trigger mechanism
if st.button("🔄 Refresh Terminal Feeds"):
    st.rerun()