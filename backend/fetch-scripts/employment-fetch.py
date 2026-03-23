import requests
import pandas as pd
import sqlite3
import os

print("📊 Fetching employment data from StatsCan...")

os.makedirs("backend/data/raw", exist_ok=True)
os.makedirs("backend/data/processed", exist_ok=True)

# Working URL for employment rate
url = "https://www150.statcan.gc.ca/t1/tbl1/en/dtl!downloadDbLoadingData-nonTraduit.action?pid=1410045801&latestN=0&startDate=20251001&endDate=20260201&csvLocale=en&selectedMembers=%5B%5B%5D%2C%5B10%5D%2C%5B%5D%2C%5B1%5D%5D&checkedLevels=0D1%2C0D2%2C0D3%2C2D1"

raw_filename = "backend/data/raw/employment_fetch.csv"
response = requests.get(url)
with open(raw_filename, 'wb') as f:
    f.write(response.content)
print(f"✅ Raw file saved: {raw_filename}")

df = pd.read_csv(raw_filename, encoding='utf-8')
kitchener_data = df[df['GEO'].str.contains('Kitchener', na=False)]

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
df_cleaned.to_csv("backend/data/processed/employment_cleaned.csv", index=False)

conn = sqlite3.connect('backend/database/metrics.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM employment")
for _, row in df_cleaned.iterrows():
    cursor.execute('INSERT INTO employment (city, date, rate, month) VALUES (?, ?, ?, ?)',
                   (row['city'], row['date'], row['rate'], row['month']))
conn.commit()
conn.close()
print(f"✅ Saved {len(df_cleaned)} records to metrics.db")