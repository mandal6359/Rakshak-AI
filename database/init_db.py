import sqlite3
import os

# Ensure the parent directory exists
os.makedirs("database", exist_ok=True)

# Establish connection handshake
conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# 1. Verify Core Alerts Table Structure
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

# 2. Verify System Cameras Table Structure
cursor.execute("""
CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_name TEXT NOT NULL UNIQUE,
    camera_path TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'ONLINE'
)
""")

# 3. Verify Spatial Station Zones Table Structure
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

# 4. STEP 1 ADDITION: Create the dedicated Incident Response Dispatch logs table
cursor.execute("""
CREATE TABLE IF NOT EXISTS dispatch_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    zone_name TEXT NOT NULL,
    assigned_team TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("🚀 Rakshak AI Table Schema Verified & Initialized successfully!")