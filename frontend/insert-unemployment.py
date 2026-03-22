import sqlite3
import pandas as pd
import os

# Get the folder where this script is located (frontend folder)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to overview.db (same folder)
db_path = os.path.join(script_dir, 'overview.db')

# Path to your cleaned data (go up one level, then into backend)
csv_path = os.path.join(script_dir, '..', 'backend', 'data', 'processed', 'unemployment-cleaned.csv')

# Load your cleaned unemployment data
df = pd.read_csv(csv_path)

# Find Kitchener row
kitchener = df[df['Geography'].str.contains('Kitchener', na=False)]

# Create the text to insert
analysis_text = f"""
Unemployment Rate - Kitchener-Cambridge-Waterloo:
- October 2025: {kitchener['Oct_2025'].values[0]}%
- November 2025: {kitchener['Nov_2025'].values[0]}%
- December 2025: {kitchener['Dec_2025'].values[0]}%
- January 2026: {kitchener['Jan_2026'].values[0]}%
- February 2026: {kitchener['Feb_2026'].values[0]}%

Trend: {'📈 Increasing' if kitchener['Feb_2026'].values[0] > kitchener['Jan_2026'].values[0] else '📉 Decreasing'}
"""

# Connect and insert
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insert into overview table
cursor.execute("""
    INSERT INTO overview (field, analysis) 
    VALUES (?, ?)
""", ('Unemployment Rate - Kitchener-Waterloo-Cambridge', analysis_text))

conn.commit()
print("✅ Unemployment data inserted successfully!")

# Verify
cursor.execute("SELECT * FROM overview")
rows = cursor.fetchall()
print(f"\nTotal rows in overview table: {len(rows)}")

conn.close()