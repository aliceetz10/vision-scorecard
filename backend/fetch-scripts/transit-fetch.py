import pandas as pd
import sqlite3

def month_to_num(month_name):
    months = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }
    return months.get(month_name, '01')

# Read the CSV file
df = pd.read_csv('backend/data/raw/grt-fetch.csv')

# Convert to date format
df['date'] = df.apply(lambda row: f"{row['year']}-{month_to_num(row['month'])}-01", axis=1)
df['month'] = df.apply(lambda row: f"{row['month']} {row['year']}", axis=1)

print("\nTransit Ridership Data:")
print(df.head(20))

# Save to processed folder
df.to_csv('backend/data/processed/transit-cleaned.csv', index=False, encoding='utf-8-sig')
print("\n✅ Saved to backend/data/processed/transit-cleaned.csv")

# Connect to metrics.db
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()

# Drop old table if exists
cursor.execute('DROP TABLE IF EXISTS transit')

# Create transit table with correct schema
cursor.execute('''
    CREATE TABLE transit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER NOT NULL,
        month TEXT NOT NULL,
        ridership INTEGER NOT NULL,
        date TEXT
    )
''')

# Insert data
for _, row in df.iterrows():
    cursor.execute('''
        INSERT INTO transit (year, month, ridership, date)
        VALUES (?, ?, ?, ?)
    ''', (row['year'], row['month'], row['ridership'], row['date']))

conn.commit()
conn.close()

print(f"✅ Saved {len(df)} transit records to metrics.db")