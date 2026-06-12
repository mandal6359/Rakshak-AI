import sqlite3

conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# Add RPF Dispatch simulation columns to the existing zones layout
try:
    cursor.execute("ALTER TABLE zones ADD COLUMN rpf_status TEXT DEFAULT 'STANDBY';")
    cursor.execute("ALTER TABLE zones ADD COLUMN assigned_team TEXT DEFAULT 'NONE';")
    print("✅ Successfully injected RPF Operations Tracking Columns into database.")
except sqlite3.OperationalError:
    print("ℹ️ RPF tracking vectors are already provisioned within the database structure.")

conn.commit()
conn.close()