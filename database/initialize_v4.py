import sqlite3
import os

os.makedirs("database", exist_ok=True)
conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# 1. Core tracking alerts data ledger table
cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    camera_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    people_count INTEGER NOT NULL,
    image_path TEXT,
    severity TEXT DEFAULT 'LOW'
)
""")

# 2. Dynamic camera feeds asset profile inventory management table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_name TEXT NOT NULL UNIQUE,
    camera_path TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'ONLINE'
)
""")

# 3. Structural spatial station zones intelligence tracking table
cursor.execute("""
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_name TEXT NOT NULL UNIQUE,
    camera_name TEXT NOT NULL,
    people_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'NORMAL',
    last_updated TEXT,
    rpf_status TEXT DEFAULT 'STANDBY',
    assigned_team TEXT DEFAULT 'NONE'
)
""")

# 4. FIXED/ADDED: Comprehensive tactical intercept dispatch log history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS dispatch_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    zone_name TEXT NOT NULL,
    assigned_team TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

# Seeding default parameters safely if the database entries do not exist
cursor.execute("SELECT COUNT(*) FROM cameras")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO cameras (camera_name, camera_path, location) VALUES (?, ?, ?)", [
        ("Camera 01", "datasets/videos/railway_station.mp4", "Platform 1 Edge"),
        ("Camera 02", "datasets/videos/railway_st.mp4", "Main Waiting Hall"),
        ("Camera 03", "datasets/videos/railway_st1.mp4", "Ticketing Counter")
    ])

cursor.execute("SELECT COUNT(*) FROM zones")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO zones (zone_name, camera_name, people_count, status) VALUES (?, ?, ?, ?)", [
        ("Platform 1 Track Area", "Camera 01", 0, "NORMAL"),
        ("Platform 1 Passenger Walkway", "Camera 01", 0, "NORMAL"),
        ("Main Waiting Hall Center", "Camera 02", 0, "NORMAL"),
        ("Ticketing Counter Queue", "Camera 03", 0, "NORMAL")
    ])

conn.commit()
conn.close()
print("🚀 Rakshak AI Unified V1.0 Enterprise Database Engine Synchronized Successfully!")