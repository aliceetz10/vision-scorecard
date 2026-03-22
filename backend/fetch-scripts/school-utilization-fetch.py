import pandas as pd
import sqlite3
import re

# Read the CSV file
df = pd.read_csv('backend/data/raw/school-utilization-fetch.csv')

# Clean utilization column - remove % sign and convert to number
def clean_percentage(value):
    if pd.isna(value):
        return None
    # Convert to string, remove % sign, then to float
    value_str = str(value).replace('%', '').strip()
    try:
        return float(value_str)
    except:
        return None

df['utilization'] = df['utilization'].apply(clean_percentage)

# Also clean capacity and enrolment if needed
df['otg_capacity'] = pd.to_numeric(df['otg_capacity'], errors='coerce')
df['enrolment_2020'] = pd.to_numeric(df['enrolment_2020'], errors='coerce')
df['fci'] = pd.to_numeric(df['fci'], errors='coerce')

# Filter for Kitchener, Waterloo, Cambridge only
cities_to_keep = ['Kitchener', 'Waterloo', 'Cambridge']
df_filtered = df[df['city'].isin(cities_to_keep)]

print(f"\nSchool Utilization Data: {len(df_filtered)} schools (filtered to {cities_to_keep})")
print(df_filtered[['school_name', 'city', 'level', 'utilization']].head(10))

# Show a sample of schools with valid utilization
valid_schools = df_filtered[df_filtered['utilization'].notna()]
print(f"\nSchools with valid utilization data: {len(valid_schools)}")

# Schools by city
print("\nSchools by City:")
print(df_filtered['city'].value_counts())

print("\nSchools by Level:")
print(df_filtered['level'].value_counts())

# Average utilization by city and level
print("\nAverage Utilization by City and Level:")
avg_util = df_filtered.groupby(['city', 'level'])['utilization'].mean().round(1)
print(avg_util)

# Save to processed folder
df_filtered.to_csv('backend/data/processed/school-utilization-cleaned.csv', index=False, encoding='utf-8-sig')
print("\n✅ Saved to backend/data/processed/school-utilization-cleaned.csv")

# Connect to metrics.db
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()

# Create school_utilization table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS school_utilization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        school_name TEXT NOT NULL,
        board TEXT NOT NULL,
        level TEXT NOT NULL,
        city TEXT,
        capacity INTEGER,
        enrolment INTEGER,
        utilization REAL,
        fci REAL,
        fci_year INTEGER
    )
''')

# Clear existing data
cursor.execute('DELETE FROM school_utilization')

# Insert filtered data
for _, row in df_filtered.iterrows():
    cursor.execute('''
        INSERT INTO school_utilization (school_name, board, level, city, capacity, enrolment, utilization, fci, fci_year)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['school_name'], row['board'], row['level'], row['city'], 
          row['otg_capacity'], row['enrolment_2020'], row['utilization'], 
          row['fci'], row['fci_year']))

conn.commit()
conn.close()

print(f"\n✅ Saved {len(df_filtered)} school utilization records to metrics.db")