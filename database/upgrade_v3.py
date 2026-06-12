import sqlite3
import os

os.makedirs("database", exist_ok=True)
conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# 1. Upgrade the alerts table to support Severity Levels
try:
    cursor.execute("ALTER TABLE alerts ADD COLUMN severity TEXT DEFAULT 'LOW';")
    print("✅ Added 'severity' column to alerts table.")
except sqlite3.OperationalError:
    print("ℹ️ 'severity' column already exists.")

# 2. Create the dynamic cameras management table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cameras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_name TEXT NOT NULL UNIQUE,
    camera_path TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'ONLINE'
)
""")
print("✅ Created 'cameras' management table.")

# 3. Populate default cameras if table is empty
cursor.execute("SELECT COUNT(*) FROM cameras")
if cursor.fetchone()[0] == 0:
    default_cameras = [
        ("Camera 01", "datasets/videos/railway_station.mp4", "Platform 1 Edge"),
        ("Camera 02", "datasets/videos/railway_st.mp4", "Main Waiting Hall"),
        ("Camera 03", "datasets/videos/railway_st1.mp4", "Ticketing Counter")
    ]
    cursor.executemany("INSERT INTO cameras (camera_name, camera_path, location) VALUES (?, ?, ?)", default_cameras)
    print("✅ Seeded default railway camera nodes into database.")

conn.commit()
conn.close()