import pandas as pd
import sqlite3

# Read the Excel file
df = pd.read_excel('backend/data/raw/housing-fetch.xlsx', 
                   sheet_name='Table 11', 
                   header=None)

# Create a list to store housing data
housing_data = []
current_year = None

# Loop through rows to find Kitchener data
for idx, row in df.iterrows():
    # Kitchener data is in column 5 (index 5)
    # Year is in column 0, Month in column 1
    year = row[0]
    month = row[1]
    starts = row[5]
    
    # Update current year if this row has a year
    if pd.notna(year) and str(year).isdigit() and len(str(year)) == 4:
        current_year = int(year)
    
    # Check if this is a valid data row
    if pd.notna(starts) and pd.notna(month) and current_year:
        if month in ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']:
            # Convert month name to number
            month_num = {
                'January': '01', 'February': '02', 'March': '03', 'April': '04',
                'May': '05', 'June': '06', 'July': '07', 'August': '08',
                'September': '09', 'October': '10', 'November': '11', 'December': '12'
            }.get(month, '01')
            
            date_str = f"{current_year}-{month_num}-01"
            
            housing_data.append({
                'city': 'Kitchener-Cambridge-Waterloo',
                'date': date_str,
                'starts': int(starts),
                'month': f"{month} {current_year}"
            })

# Create DataFrame
df_housing = pd.DataFrame(housing_data)

print("\nHousing Data Extracted:")
print(df_housing)

# Save to CSV
df_housing.to_csv('backend/data/processed/housing-cleaned.csv', index=False, encoding='utf-8-sig')
print("✅ Saved to backend/data/processed/housing-cleaned.csv")

# Connect to metrics.db
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()

# Create housing table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS housing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT NOT NULL,
        date TEXT NOT NULL,
        starts INTEGER NOT NULL,
        month TEXT
    )
''')

# Clear existing data first (to avoid duplicates)
cursor.execute('DELETE FROM housing')

# Insert data
for _, row in df_housing.iterrows():
    cursor.execute('''
        INSERT INTO housing (city, date, starts, month)
        VALUES (?, ?, ?, ?)
    ''', (row['city'], row['date'], row['starts'], row['month']))

conn.commit()
conn.close()

print(f"\n✅ Saved {len(df_housing)} housing records to metrics.db")