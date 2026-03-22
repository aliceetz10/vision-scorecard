import sqlite3
import os

# Get the folder where this script is
script_dir = os.path.dirname(os.path.abspath(__file__))

# Database will be in the same folder
db_path = os.path.join(script_dir, 'metrics.db')

# Connect (creates file if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create unemployment table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS unemployment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        date TEXT NOT NULL,
        rate REAL NOT NULL,
        month TEXT
    )
''')

# Create housing table (placeholder for now)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS housing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        date TEXT NOT NULL,
        starts INTEGER NOT NULL,
        month TEXT
    )
''')

# Create transit table (placeholder)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT NOT NULL,
        ridership INTEGER NOT NULL
    )
''')

conn.commit()
conn.close()

print("✅ metrics.db created successfully!")
print(f"   Location: {db_path}")
print("   Tables: unemployment, housing, transit")