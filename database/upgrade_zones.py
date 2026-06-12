import sqlite3

conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

# 1. Create the station zones table
cursor.execute("""
CREATE TABLE IF NOT EXISTS zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_name TEXT NOT NULL UNIQUE,
    camera_name TEXT NOT NULL,
    people_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'NORMAL',
    last_updated TEXT
)
""")
print("✅ Created 'zones' intelligence table.")

# 2. Seed default station zones
cursor.execute("SELECT COUNT(*) FROM zones")
if cursor.fetchone()[0] == 0:
    default_zones = [
        ("Platform 1 Track Area", "Camera 01", 0, "NORMAL"),
        ("Platform 1 Passenger Walkway", "Camera 01", 0, "NORMAL"),
        ("Main Waiting Hall Center", "Camera 02", 0, "NORMAL"),
        ("Ticketing Counter Queue", "Camera 03", 0, "NORMAL")
    ]
    cursor.executemany(
        "INSERT INTO zones (zone_name, camera_name, people_count, status) VALUES (?, ?, ?, ?)", 
        default_zones
    )
    print("✅ Seeded default station zones into database.")

conn.commit()
conn.close()