import sqlite3

conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# Create table to keep a historical log of all dispatched response actions
cursor.execute("""
CREATE TABLE IF NOT EXISTS dispatches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    zone_name TEXT,
    assigned_team TEXT,
    status TEXT
)
""")
print("✅ Created 'dispatches' historical action registry table.")

conn.commit()
conn.close()