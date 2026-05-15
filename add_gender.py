import sqlite3
import os

db_path = os.path.join('instance', 'dermaura.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN gender VARCHAR(20) DEFAULT 'Not Specified'")
        conn.commit()
        print("Successfully added gender column.")
    except Exception as e:
        print(f"Error adding column: {e}")
    conn.close()
else:
    print(f"Database not found at {db_path}")
