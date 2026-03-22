import pandas as pd
import sqlite3

# Read the CSV file
df = pd.read_csv('backend/data/raw/ghg-emissions-fetch.csv')

print("\nGHG Emissions Data:")
print(df)

# Save to processed folder
df.to_csv('backend/data/processed/ghg-emissions-cleaned.csv', index=False, encoding='utf-8-sig')
print("\n✅ Saved to backend/data/processed/ghg-emissions-cleaned.csv")

# Connect to metrics.db
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()

# Create ghg_emissions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ghg_emissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        sector TEXT NOT NULL,
        emissions_tonnes INTEGER NOT NULL,
        notes TEXT
    )
''')

# Clear existing data
cursor.execute('DELETE FROM ghg_emissions')

# Insert data
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO ghg_emissions (year, sector, emissions_tonnes, notes)
        VALUES (?, ?, ?, ?)
    ''', (row['year'], row['sector'], row['emissions_tonnes'], row['notes']))

conn.commit()
conn.close()

print(f"\n✅ Saved {len(df)} GHG records to metrics.db")