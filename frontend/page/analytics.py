import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(page_title="Rakshak AI - Advanced Analytics", page_icon="📊", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>📊 RAKSHAK AI — HISTORICAL SAFETY ANALYTICS DIALECT</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>Long-Term Station Risk Profiling, Density Trend Charts & Operational Intelligence Insights</p>", unsafe_allow_html=True)
st.markdown("---")

def get_db_connection():
    return sqlite3.connect("database/alerts.db")

conn = get_db_connection()
df_alerts = pd.read_sql_query("SELECT * FROM alerts", conn)
df_zones = pd.read_sql_query("SELECT * FROM zones", conn)
conn.close()

if df_alerts.empty:
    st.info("🛰_ Awaiting active tracking engine pipelines to generate historical metrics panels.")
else:
    # Parse timestamps into actual dataframe index markers
    df_alerts['timestamp_dt'] = pd.to_datetime(df_alerts['timestamp'])
    df_alerts['Hour'] = df_alerts['timestamp_dt'].dt.strftime('%I %p')

    # =========================================================================
    # UPGRADE: CRITICAL OPERATIONAL ANALYTICS CARD BOARD
    # =========================================================================
    st.subheader("🎯 Station Risk Profiling & Operational Core Insights")
    
    # Calculate peak parameters dynamically from data
    top_risk_camera = df_alerts['camera_name'].value_counts().idxmax()
    top_risk_count = df_alerts['camera_name'].value_counts().max()
    
    peak_hour = df_alerts['Hour'].value_counts().idxmax()
    
    most_crowded_zone = df_zones.loc[df_zones['people_count'].idxmax()]['zone_name'] if not df_zones.empty else "Platform 1"
    
    col_ins1, col_ins2, col_ins3 = st.columns(3)
    with col_ins1:
        st.error("🚨 TOP RISK CAMERA NODE")
        st.metric(label=top_risk_camera, value=f"{top_risk_count} Logged Breaks")
    with col_ins2:
        st.warning("⏳ PEAK INCIDENT TIME TRAFFIC")
        st.metric(label="System High-Load Hour", value=peak_hour)
    with col_ins3:
        st.info("🚉 HIGHEST REGIONAL DENSITY")
        st.metric(label="Critical Bottleneck Area", value=most_crowded_zone)
        
    st.markdown("---")
    # =========================================================================

    graph_col1, graph_col2 = st.columns(2)
    with graph_col1:
        st.subheader("📈 Chronological Incident Volume Timeline (Hourly Distribution)")
        hourly_distribution = df_alerts['Hour'].value_counts().sort_index()
        st.line_chart(hourly_distribution)
        
    with graph_col2:
        st.subheader("🎯 Camera Station Location Risk Weight Rankings")
        camera_risk_weights = df_alerts['camera_name'].value_counts()
        st.bar_chart(camera_risk_weights)

    st.markdown("---")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.subheader("🔥 Incident Distribution Breakdown by Threat Classification")
        st.area_chart(df_alerts['alert_type'].value_counts())
    with chart_col2:
        st.subheader("🛡️ Volume Weight Concentration Metrics per Severity Class")
        st.bar_chart(df_alerts['severity'].value_counts())