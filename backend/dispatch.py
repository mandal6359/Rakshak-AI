import sqlite3
from datetime import datetime

def dispatch_team(zone_name, team_name):
    """Inserts an active tactical RPF intercept row into the database log registry."""
    conn = sqlite3.connect("database/alerts.db")
    cursor = conn.cursor()

    # Log timestamp format matching your requirements
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO dispatch_logs (timestamp, zone_name, assigned_team, status)
    VALUES (?, ?, ?, ?)
    """, (now_str, zone_name, team_name, "DISPATCHED"))

    # Simultaneously update the live status marker inside the zones map model table
    cursor.execute("""
    UPDATE zones 
    SET rpf_status = 'DISPATCHED', assigned_team = ? 
    WHERE zone_name = ?
    """, (team_name, zone_name))

    conn.commit()
    conn.close()
    print(f"📡 Dispatch Signal Written to DB: Unit {team_name} heading to {zone_name}")