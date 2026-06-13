import sys
import os

# Ensure package system boundaries resolve higher lookup hierarchies smoothly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import sqlite3
import pandas as pd
import time
import glob
from datetime import datetime

st.set_page_config(page_title="Rakshak AI Command Center", page_icon="🚆", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ RAKSHAK AI — RAILWAY SAFETY COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>Live Spatial Mapping Intelligence & Emergency Response Tactical Console</p>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# CENTRALIZED AUTOMATED REFRESH LOOP TICKER
# Forces Streamlit to re-evaluate structural variables every 5 seconds
# =========================================================================
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

def trigger_refresh_loop():
    time.sleep(5.0)  # Bounded 5-second automatic update rule
    st.session_state.refresh_counter += 1
    st.rerun()

st.sidebar.markdown(f"**Last Sync Marker:** `{datetime.now().strftime('%H:%M:%S')}`")
# =========================================================================

def get_db_connection():
    return sqlite3.connect("database/alerts.db")

# ==========================================
# SIDEBAR REPOSITORY LOGS VIEWPORTS
# ==========================================
with st.sidebar:
    st.header("⚙️ Central Controller Registry")
    conn = get_db_connection()
    try:
        df_caps = pd.read_sql_query("SELECT id, camera_name, location, status FROM cameras", conn)
        st.subheader("Active Camera Grid Inventory")
        st.dataframe(df_caps, use_container_width=True, hide_index=True)
    except Exception:
        st.caption("Awaiting initial camera infrastructure link configuration...")
    conn.close()
    
    st.markdown("---")
    st.subheader("📋 Tactical Intercept Dispatch Logs")
    conn = get_db_connection()
    try:
        df_disp_history = pd.read_sql_query("SELECT timestamp, zone_name, assigned_team, status FROM dispatch_log ORDER BY id DESC LIMIT 5", conn)
        if not df_disp_history.empty:
            st.dataframe(df_disp_history, use_container_width=True, hide_index=True)
        else:
            st.caption("No historical response dispatch interventions registered.")
    except Exception:
        st.caption("Awaiting initial tactical logging parameters entries...")
    conn.close()

# Fetch active monitoring parameters metrics lines
conn = get_db_connection()
df_alerts = pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC", conn)
df_zones = pd.read_sql_query("SELECT zone_name, people_count, status, rpf_status, assigned_team FROM zones", conn)
conn.close()

if df_alerts.empty:
    st.info("🛰️ Rakshak AI Server Engine running... Awaiting initial video processing array link signals.")
else:
    total_logs = len(df_alerts)
    emergency_count = len(df_alerts[df_alerts['severity'] == 'EMERGENCY'])
    critical_count = len(df_alerts[df_alerts['severity'] == 'CRITICAL'])
    high_count = len(df_alerts[df_alerts['severity'] == 'HIGH'])

    # Flashing Emergency System Banners Header Injection
    if df_alerts.iloc[0]['severity'] in ["CRITICAL", "EMERGENCY"]:
        st.error(f"🚨 ALARM URGENT INCIDENT WARNING: {df_alerts.iloc[0]['alert_type'].upper()} ACTIVE ON {df_alerts.iloc[0]['camera_name'].upper()} @ {df_alerts.iloc[0]['timestamp']}")

    # System Status KPIs Matrix Metrics Row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: st.metric(label="Total Logged Incidents", value=total_logs)
    with kpi2: st.metric(label="EMERGENCY STATUS LEVEL 🔴", value=emergency_count, delta=f"{critical_count} Critical States", delta_color="inverse")
    with kpi3: st.metric(label="HIGH SEVERITY CONGESTIONS 🟠", value=high_count)
    with kpi4: st.metric(label="Network Grid Synchronization", value="Synchronized")

    st.markdown("---")

    # =========================================================================
    # UPGRADE: DIGITAL TWIN STATION OVERLAY BLUEPRINT MATRIX
    # =========================================================================
    map_col, dispatch_col = st.columns([2, 1])
    with map_col:
        st.subheader("🚉 Live Station Digital Twin Spatial Blueprint Matrix")
        z_map = {row['zone_name']: row for _, row in df_zones.iterrows()}
        m_col1, m_col2 = st.columns(2)
        m_col3, m_col4 = st.columns(2)
        
        with m_col1:
            z = z_map.get("Platform 1 Track Area", {"people_count": 0, "status": "NORMAL"})
            if z['status'] in ['DANGER', 'EMERGENCY', 'CRITICAL']: st.error(f"🚨 Platform 1 Track Area — {z['status']}")
            else: st.success(f"🟢 Platform 1 Track Area — {z['status']}")
            st.metric("Track Population Index", f"{z['people_count']} Pax")
        with m_col2:
            z = z_map.get("Platform 1 Passenger Walkway", {"people_count": 0, "status": "NORMAL"})
            if 'CROWDED' in z['status']: st.warning(f"🟡 Platform 1 Walkway — {z['status']}")
            else: st.success(f"🟢 Platform 1 Walkway — {z['status']}")
            st.metric("Walkway Population Index", f"{z['people_count']} Pax")
        with m_col3:
            z = z_map.get("Main Waiting Hall Center", {"people_count": 0, "status": "NORMAL"})
            if 'CROWDED' in z['status']: st.warning(f"🟡 Main Waiting Concourse — {z['status']}")
            else: st.success(f"🟢 Main Waiting Concourse — {z['status']}")
            st.metric("Concourse Population Index", f"{z['people_count']} Pax")
        with m_col4:
            z = z_map.get("Ticketing Counter Queue", {"people_count": 0, "status": "NORMAL"})
            if 'CROWDED' in z['status']: st.warning(f"🟡 Ticket Line Queue — {z['status']}")
            else: st.success(f"🟢 Ticket Line Queue — {z['status']}")
            st.metric("Queue Population Index", f"{z['people_count']} Pax")

    # Operations Countermeasures Control intercept card
    with dispatch_col:
        st.subheader("🚨 Emergency Operations Intercepts")
        danger_zones_list = df_zones[df_zones['status'].isin(['DANGER', 'CROWDED', 'EMERGENCY', 'CRITICAL'])]
        if danger_zones_list.empty:
            st.success("🟢 All station sectors reporting clear standard parameters.")
        else:
            st.warning("⚠️ Active threat anomalies registered!")
            selected_zone = st.selectbox("Select Target Emergency Sector Node", danger_zones_list['zone_name'].tolist())
            selected_row_data = df_zones[df_zones['zone_name'] == selected_zone].iloc[0]
            st.info(f"**Target:** {selected_zone}\n\n**Current RPF Node State:** `{selected_row_data['rpf_status']}`")
            
            if st.button("🚨 EXECUTE HIGH-PRIORITY RPF SECURITY DISPATCH", use_container_width=True):
                from backend.dispatch import dispatch_team
                dispatch_team(selected_zone)
                st.success(f"🚀 RPF TEAM DISPATCHED TO {selected_zone}!")
                time.sleep(0.5)
                st.rerun()

    st.markdown("---")

    # Chronological Incident Timeline Feed Layout Component 
    st.subheader("⏳ Chronological System Event Timeline")
    timeline_cols = st.columns(4)
    recent_events = df_alerts.head(4)
    for idx, row in recent_events.reset_index().iterrows():
        t_col = timeline_cols[idx]
        t_stamp = row['timestamp'].split(" ")[1]
        if row['severity'] in ['CRITICAL', 'EMERGENCY']: card_bg, border = "#450A0A", "#EF4444"
        elif 'HIGH' in row['severity']: card_bg, border = "#451A03", "#F97316"
        else: card_bg, border = "#1E293B", "#64748B"
        
        t_col.markdown(f"""
        <div style="background-color: {card_bg}; border-left: 4px solid {border}; padding: 12px; border-radius: 4px;">
            <span style="color: #94A3B8; font-size: 11px; font-weight: bold;">⏱️ TIME: {t_stamp}</span><br>
            <strong style="color: white; font-size: 13px;">{row['alert_type']}</strong><br>
            <span style="color: #CBD5E1; font-size: 12px;">{row['camera_name']} | Load: {row['people_count']} Pax</span><br>
            <span style="color: {border}; font-size: 11px; font-weight: bold;">SEVERITY: {row['severity']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Live CCTV Verification Display grids wall layers
    st.subheader("📸 Live Threat Verification & Evidence Capture Wall")
    view_col1, view_col2 = st.columns(2)
    
    with view_col1:
        st.markdown("### 🚨 Latest Captured Forensic Threat Asset")
        all_captured_images = sorted(glob.glob("alerts/*.jpg"), key=os.path.getmtime, reverse=True)
        true_evidence_images = [img for img in all_captured_images if "live_cam" not in img and "latest_heatmap" not in img]
        if true_evidence_images:
            st.image(true_evidence_images[0], caption=f"Evidence Asset ID: {os.path.basename(true_evidence_images[0])}", use_container_width=True)
        else:
            st.caption("No permanent threat evidence captures stored on system disk yet.")

    with view_col2:
        st.markdown("### 📺 Active Process Surveillance Stream Ticker")
        if os.path.exists("alerts/live_cam_1.jpg"):
            st.image("alerts/live_cam_1.jpg", caption="Active Core Monitoring Primary Channel Feed", use_container_width=True)

    st.markdown("---")
    
    # Administrative Actions Section
    st.subheader("📊 Administrative Export Station")
    if st.button("📊 Compile and Write PDF Audit Report Data", use_container_width=True):
        try:
            from backend.report_generator import generate_pdf_report
            generate_pdf_report()
            st.success("📄 Operational incident audit report written successfully into the reports/ folder directory.")
        except Exception as e:
            st.error(f"Report compilation fault: {e}")

    st.markdown("---")
    st.subheader("📋 Core Incident Registry Logs Ledger")
    ledger_col, chart_col = st.columns(2)
    with ledger_col:
        st.dataframe(df_alerts[['timestamp', 'camera_name', 'alert_type', 'severity', 'people_count']], use_container_width=True, hide_index=True)
    with chart_col:
        st.bar_chart(df_alerts['camera_name'].value_counts())

# Run background re-evaluation ticker loops loop parameters
trigger_refresh_loop()