import streamlit as st
import sqlite3
import pandas as pd
import os
import random
import time
from datetime import datetime

st.set_page_config(page_title="Rakshak AI Command Center", page_icon="🚆", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🛡️ RAKSHAK AI — RAILWAY SAFETY COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777;'>Real-Time Video Analytics, Spatial Risk Intelligence & Emergency Operations Suite</p>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# UPGRADE MAJOR FEATURE: CENTRALIZED AUTOMATED REFRESH MATRIX TICKER LOOP
# Generates a low-latency thread loop to continuously re-render the screen every 5 seconds
# =========================================================================
current_epoch_time = int(time.time())
st.sidebar.markdown(f"**Last Monitor Sync:** `{datetime.now().strftime('%H:%M:%S')}`")

# Streamlit native session management loop simulation fallback trigger ticker
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

def trigger_refresh_loop():
    time.sleep(5.0)  # Configured 5-second control room refresh rule
    st.session_state.refresh_counter += 1
    st.rerun()

# =========================================================================

def get_db_connection():
    return sqlite3.connect("database/alerts.db")

def sync_dispatch_lifecycle():
    conn = get_db_connection()
    cursor = conn.cursor()
    now_time = datetime.now()
    cursor.execute("SELECT id, timestamp, zone_name FROM dispatch_logs WHERE status='DISPATCHED'")
    active_dispatches = cursor.fetchall()
    
    for disp in active_dispatches:
        d_id, t_stamp, z_name = disp
        dispatch_time = datetime.strptime(t_stamp, "%Y-%m-%d %H:%M:%S")
        elapsed_seconds = (now_time - dispatch_time).total_seconds()
        
        if elapsed_seconds > 120:
            cursor.execute("UPDATE dispatch_logs SET status='RESOLVED' WHERE id=?", (d_id,))
            cursor.execute("UPDATE zones SET rpf_status='STANDBY', assigned_team='NONE' WHERE zone_name=?", (z_name,))
        elif elapsed_seconds > 45:
            cursor.execute("UPDATE dispatch_logs SET status='ARRIVED' WHERE id=?", (d_id,))
            cursor.execute("UPDATE zones SET rpf_status='ON-SCENE (INVESTIGATING)' WHERE zone_name=?", (z_name,))
    conn.commit()
    conn.close()

sync_dispatch_lifecycle()

# ==========================================
# SIDEBAR NAVIGATION INTERFACES
# ==========================================
with st.sidebar:
    st.header("🎮 Operations Navigation")
    
    st.markdown("---")
    # UPGRADE: Fully working live active response dispatch ledger module component
    st.subheader("📋 Tactical Dispatch Log History")
    conn = get_db_connection()
    try:
        df_disp_history = pd.read_sql_query("SELECT timestamp, zone_name, assigned_team, status FROM dispatch_logs ORDER BY id DESC LIMIT 5", conn)
        if not df_disp_history.empty:
            st.dataframe(df_disp_history, use_container_width=True, hide_index=True)
        else:
            st.caption("No historical response dispatch actions logged yet.")
    except Exception:
        st.caption("Awaiting initial tactical deployment records...")
    conn.close()

    st.markdown("---")
    if st.button("📊 Export PDF Audit Report"):
        try:
            from backend.report_generator import generate_pdf_report
            generate_pdf_report()
            st.success("📄 Report Exported to /reports folder!")
        except Exception as e:
            st.error(f"Export Failed: {e}")

# Load active database logs rows
conn = get_db_connection()
df_alerts = pd.read_sql_query("SELECT * FROM alerts ORDER BY id DESC", conn)
df_zones = pd.read_sql_query("SELECT zone_name, people_count, status, rpf_status, assigned_team FROM zones", conn)
df_caps = pd.read_sql_query("SELECT id, camera_name, location, status FROM cameras", conn)
conn.close()

if df_alerts.empty:
    st.info("Awaiting initial connection stream handshake entries from backend AI server processing loop...")
else:
    # =========================================================================
    # BUG FIX: STRICT COUNTERS ALIGNMENT CORRECTION
    # Aligned exact target case strings to fix metric reporting counters mismatch
    # =========================================================================
    total_logs = len(df_alerts)
    emergency_count = len(df_alerts[df_alerts['severity'] == 'EMERGENCY'])
    critical_count = len(df_alerts[df_alerts['severity'] == 'CRITICAL'])
    high_count = len(df_alerts[df_alerts['severity'] == 'HIGH'])

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1: st.metric(label="Total Registered Breaches", value=total_logs)
    with kpi2: st.metric(label="EMERGENCY STATUS 🚨", value=emergency_count, delta=f"{critical_count} Critical States", delta_color="inverse")
    with kpi3: st.metric(label="HIGH THREAT CONGESTIONS 🟠", value=high_count)
    with kpi4: st.metric(label="Operational System Nodes", value="3 Cameras Online")
    # =========================================================================

    st.markdown("---")

    # Railway Digital Twin Layout Matrix Map Block Row
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
            st.metric("Track Zone Population", f"{z['people_count']} Pax")
            
        with m_col2:
            z = z_map.get("Platform 1 Passenger Walkway", {"people_count": 0, "status": "NORMAL"})
            if 'CROWDED' in z['status'] or 'HIGH' in z['status']: st.warning(f"🟡 Platform 1 Walkway — {z['status']}")
            else: st.success(f"🟢 Platform 1 Walkway — {z['status']}")
            st.metric("Walkway Zone Population", f"{z['people_count']} Pax")

        with m_col3:
            z = z_map.get("Main Waiting Hall Center", {"people_count": 0, "status": "NORMAL"})
            if 'CROWDED' in z['status']: st.warning(f"🟡 Main Waiting Concourse — {z['status']}")
            else: st.success(f"🟢 Main Waiting Concourse — {z['status']}")
            st.metric("Concourse Population", f"{z['people_count']} Pax")

        with m_col4:
            z = z_map.get("Ticketing Counter Queue", {"people_count": 0, "status": "NORMAL"})
            if 'CROWDED' in z['status']: st.warning(f"🟡 Ticket Line Queue — {z['status']}")
            else: st.success(f"🟢 Ticket Line Queue — {z['status']}")
            st.metric("Queue Population", f"{z['people_count']} Pax")

    # Tactical response countermeasures interface card block panel
    with dispatch_col:
        st.subheader("🚨 Emergency Intercept Countermeasures")
        danger_zones_list = df_zones[df_zones['status'].isin(['DANGER', 'CROWDED', 'EMERGENCY', 'CRITICAL'])]
        
        if danger_zones_list.empty:
            st.success("🟢 All station sectors reporting clear standard parameters.")
        else:
            st.warning("⚠️ Active threat anomalies registered! Action recommended.")
            target_zone_selection = st.selectbox("Select Target Emergency Sector Node", danger_zones_list['zone_name'].tolist())
            selected_row_data = df_zones[df_zones['zone_name'] == target_zone_selection].iloc[0]
            
            st.info(f"**Target Area:** {target_zone_selection}\n\n**Current RPF Node State:** `{selected_row_data['rpf_status']}`")
            
            if st.button("🔴 EXECUTE TACTICAL RPF COMMAND STRIKE DISPATCH", use_container_width=True):
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                assigned_team_name = f"RPF_TEAM_{random.randint(10,99)}"
                
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE zones SET rpf_status='DISPATCHED', assigned_team=? WHERE zone_name=?",
                    (assigned_team_name, target_zone_selection)
                )
                cursor.execute(
                    "INSERT INTO dispatch_logs (timestamp, zone_name, assigned_team, status) VALUES (?, ?, ?, ?)",
                    (now_str, target_zone_selection, assigned_team_name, "DISPATCHED")
                )
                conn.commit()
                conn.close()
                st.error(f"🚀 Tactical Dispatch Registered! Unit {assigned_team_name} deployed.")
                time.sleep(0.5)
                st.rerun()

    st.markdown("---")

    # Chronological Incident Timeline Rows Component
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

    # Real-Time CCTV Streaming Matrix Viewport Wall Layer
    st.subheader("📺 Real-Time Active CCTV Surveillance Stream Matrix")
    stream_toggle = st.checkbox("▶️ Open Live Web Stream Grid Feeds", value=True)
    
    if stream_toggle:
        feed_col1, feed_col2, feed_col3 = st.columns(3)
        with feed_col1:
            st.markdown("##### Camera Node 01")
            p1 = st.empty()
        with feed_col2:
            st.markdown("##### Camera Node 02")
            p2 = st.empty()
        with feed_col3:
            st.markdown("##### Camera Node 03")
            p3 = st.empty()

        for _ in range(15):
            if os.path.exists("alerts/live_cam_1.jpg"): p1.image("alerts/live_cam_1.jpg", use_container_width=True)
            if os.path.exists("alerts/live_cam_2.jpg"): p2.image("alerts/live_cam_2.jpg", use_container_width=True)
            if os.path.exists("alerts/live_cam_3.jpg"): p3.image("alerts/live_cam_3.jpg", use_container_width=True)
            time.sleep(0.05)
    else:
        st.info("Surveillance feeds minimized. Check the box above to toggle live web view panels.")

    st.markdown("---")

    # Core logging tables rows ledger view
    st.subheader("📋 Core Incident Registry Logs Ledger")
    ledger_col, chart_col = st.columns(2)
    with ledger_col:
        st.dataframe(df_alerts[['timestamp', 'camera_name', 'alert_type', 'severity', 'people_count']], use_container_width=True, hide_index=True)
    with chart_col:
        st.bar_chart(df_alerts['camera_name'].value_counts())

# Boot up the dynamic background loop ticker tracking sequence execution
trigger_refresh_loop()