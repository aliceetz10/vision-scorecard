import pandas as pd
import sqlite3

# Read the CSV file
df = pd.read_csv('backend/data/raw/go-train-fetch.csv')

print("\nGO Train Data:")
print(df)

# Save to processed folder
df.to_csv('backend/data/processed/go-train-cleaned.csv', index=False, encoding='utf-8-sig')
print("\n✅ Saved to backend/data/processed/go-train-cleaned.csv")

# Connect to metrics.db
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()

# Create go_train table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS go_train (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        line TEXT NOT NULL,
        day_type TEXT NOT NULL,
        trips_direct INTEGER,
        trips_transfer INTEGER,
        trips_total INTEGER
    )
''')

# Clear existing data
cursor.execute('DELETE FROM go_train')

# Insert data
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO go_train (date, line, day_type, trips_direct, trips_transfer, trips_total)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['date'], row['line'], row['day_type'], 
          row['trips_direct'], row['trips_transfer'], 
          row['trips_total']))

conn.commit()
conn.close()

print(f"\n✅ Saved {len(df)} GO Train records to metrics.db")