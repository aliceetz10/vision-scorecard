import pandas as pd
import sqlite3
import glob

# Find all hospital CSV files
csv_files = glob.glob('backend/data/raw/hospital-*-fetch.csv')

all_data = []

for file in csv_files:
    # Read the CSV, skipping the header rows (rows 0-3 are metadata)
    df = pd.read_csv(file, skiprows=4)
    
    # Get hospital name from filename
    if 'grand-river' in file:
        hospital = 'Grand River Hospital'
    elif 'st-marys' in file:
        hospital = "St. Mary's General Hospital"
    elif 'cambridge-memorial' in file:
        hospital = 'Cambridge Memorial Hospital'
    else:
        print(f"Unknown file: {file} - skipping")
        continue
    
    # Rename columns
    df.columns = ['month', 'ontario_avg', 'wait_time']
    
    # FILTER OUT NON-DATA ROWS
    # Keep only rows where month is a 6-digit number (like 202501)
    df = df[df['month'].astype(str).str.match(r'^\d{6}$', na=False)]
    
    # Convert wait_time to numeric (in case it's stored as string)
    df['wait_time'] = pd.to_numeric(df['wait_time'], errors='coerce')
    df['ontario_avg'] = pd.to_numeric(df['ontario_avg'], errors='coerce')
    
    # Drop rows where wait_time is NaN
    df = df.dropna(subset=['wait_time'])
    
    # Add hospital column
    df['hospital'] = hospital
    
    # Convert month string to date
    df['date'] = df['month'].apply(lambda x: f"{str(x)[:4]}-{str(x)[4:6]}-01")
    
    all_data.append(df)
    print(f"✅ Loaded {hospital}: {len(df)} records")

# Combine all data
combined_df = pd.concat(all_data, ignore_index=True)

print("\n" + "="*60)
print("HOSPITAL WAIT TIMES DATA")
print("="*60)
print(combined_df.head(20))

# Save to CSV
combined_df.to_csv('backend/data/processed/hospital-wait-times-cleaned.csv', index=False, encoding='utf-8-sig')
print("\n✅ Saved to backend/data/processed/hospital-wait-times-cleaned.csv")

# Connect to metrics.db
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()

# Create hospital_wait_times table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS hospital_wait_times (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital TEXT NOT NULL,
        month TEXT NOT NULL,
        wait_time REAL NOT NULL,
        ontario_avg REAL NOT NULL,
        date TEXT
    )
''')

# Clear existing data
cursor.execute('DELETE FROM hospital_wait_times')

# Insert data
for _, row in combined_df.iterrows():
    cursor.execute('''
        INSERT INTO hospital_wait_times (hospital, month, wait_time, ontario_avg, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (row['hospital'], row['month'], row['wait_time'], row['ontario_avg'], row['date']))

conn.commit()
conn.close()

print(f"\n✅ Saved {len(combined_df)} hospital records to metrics.db")

# Summary by hospital
print("\n" + "="*60)
print("SUMMARY BY HOSPITAL")
print("="*60)
summary = combined_df.groupby('hospital').agg({
    'wait_time': ['min', 'max', 'mean'],
    'month': 'count'
}).round(1)
print(summary)