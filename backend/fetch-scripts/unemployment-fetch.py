import requests
import pandas as pd
import sqlite3
import os

print("📊 Fetching unemployment data from StatsCan...")

# Create directories if they don't exist
os.makedirs("backend/data/raw", exist_ok=True)
os.makedirs("backend/data/processed", exist_ok=True)

# Working URL (downloads latest data)
url = "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDbLoadingData-nonTraduit.action?pid=1410045801&latestN=5&startDate=&endDate=&csvLocale=en&selectedMembers=%5B%5B%5D%2C%5B8%5D%2C%5B%5D%2C%5B1%5D%5D&checkedLevels=0D1%2C0D2%2C0D3%2C2D1"

# Download to RAW
raw_filename = "backend/data/raw/unemployment_fetch.csv"
response = requests.get(url)
with open(raw_filename, 'wb') as f:
    f.write(response.content)
print(f"✅ Raw file saved: {raw_filename}")

# Read and process
df = pd.read_csv(raw_filename, encoding='utf-8')

# Filter for Kitchener
kitchener_data = df[df['GEO'].str.contains('Kitchener', na=False)]

# Create cleaned data
cleaned_data = []
for _, row in kitchener_data.iterrows():
    date = f"{row['REF_DATE']}-01"
    month_name = pd.to_datetime(row['REF_DATE']).strftime('%B %Y')
    cleaned_data.append({
        'city': 'Kitchener-Cambridge-Waterloo',
        'date': date,
        'rate': row['VALUE'],
        'month': month_name
    })

df_cleaned = pd.DataFrame(cleaned_data)

# Save to processed
df_cleaned.to_csv("backend/data/processed/unemployment_cleaned.csv", index=False)
print(f"✅ Processed file saved")

# Update database
conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM unemployment")
for _, row in df_cleaned.iterrows():
    cursor.execute('INSERT INTO unemployment (city, date, rate, month) VALUES (?, ?, ?, ?)',
                   (row['city'], row['date'], row['rate'], row['month']))
conn.commit()
conn.close()
print(f"✅ Saved {len(df_cleaned)} records to metrics.db")