import pandas as pd
import sqlite3

# Connect to metrics.db
metrics_db_path = 'backend/database/metrics.db'
conn = sqlite3.connect(metrics_db_path)
cursor = conn.cursor()

# Read the file - skip to row 8 (headers), data starts at row 9
df = pd.read_csv('backend/data/raw/unemployment-fetch.csv', skiprows=8, encoding='utf-8')

# Rename columns
df.columns = ['Geography', 'Oct_2025', 'Nov_2025', 'Dec_2025', 'Jan_2026', 'Feb_2026']

# Remove empty rows
df_new = df.dropna(how='all')


# Clean the Geography column - remove footnote numbers
df_new['Geography'] = df_new['Geography'].str.replace(r'\s+\d+$', '', regex=True)
df_new['Geography'] = df_new['Geography'].str.strip()
df_new = df_new[df_new['Geography'].str.contains(',', na=False)]
df_new = df_new[~df_new['Geography'].str.contains('Footnotes|Table|Corrections', na=False, case=False)]

print(df_new.head(70))

# Find Kitchener
kitchener = df_new[df_new['Geography'].str.contains('Kitchener', na=False)]

# Convert to numbers
for month in ['Oct_2025', 'Nov_2025', 'Dec_2025', 'Jan_2026', 'Feb_2026']:
    kitchener[month] = pd.to_numeric(kitchener[month], errors='coerce')

# Display
print("\n" + "="*60)
print("KITCHENER-CAMBRIDGE-WATERLOO UNEMPLOYMENT RATE")
print("="*60)
print(kitchener.to_string(index=False))

# Also show the most recent value
latest = kitchener['Feb_2026'].values[0]
print(f"\n📊 Most recent (Feb 2026): {latest}%")

df_new.to_csv('backend/data/processed/unemployment-cleaned.csv', index=False, encoding='utf-8-sig')

# Insert each month as a row
months = [
    ('2025-10-01', 'October 2025', 'Oct_2025'),
    ('2025-11-01', 'November 2025', 'Nov_2025'),
    ('2025-12-01', 'December 2025', 'Dec_2025'),
    ('2026-01-01', 'January 2026', 'Jan_2026'),
    ('2026-02-01', 'February 2026', 'Feb_2026'),
]

for date, month_name, column in months:
    rate = kitchener[column].values[0]
    cursor.execute('''
        INSERT INTO unemployment (city, date, rate, month)
        VALUES (?, ?, ?, ?)
    ''', ('Kitchener-Cambridge-Waterloo', date, rate, month_name))

conn.commit()
conn.close()

print("✅ Also saved to metrics.db")