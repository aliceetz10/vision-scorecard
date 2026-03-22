import pandas as pd

# Read Table 11 without skipping rows first to see structure
df_raw = pd.read_excel('backend/data/raw/housing-fetch.xlsx', 
                        sheet_name='Table 11', 
                        header=None,
                        nrows=30)

print("RAW TABLE 11 (first 30 rows):")
print(df_raw)