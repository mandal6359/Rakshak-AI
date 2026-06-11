import sqlite3

conn = sqlite3.connect("database/alerts.db")
cursor = conn.cursor()

try:
    # Safely inject the new image_path column into your existing structure
    cursor.execute("ALTER TABLE alerts ADD COLUMN image_path TEXT;")
    conn.commit()
    print("🚀 Database modified successfully! Added 'image_path' column.")
except sqlite3.OperationalError:
    print("ℹ️ 'image_path' column already exists inside database. Skipping modification.")

conn.close()