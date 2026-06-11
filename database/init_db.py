import sqlite3
import os

# Create database directory if it doesn't exist
os.makedirs("database", exist_ok=True)

# Connect to database file (creates it if missing)
conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# Create table for logging security incidents
cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    camera_name TEXT NOT NULL,
    alert_type TEXT NOT NULL,
    people_count INTEGER NOT NULL
)
""")

conn.commit()
conn.close()
print("🚀 Rakshak AI Database Initialized Successfully!")