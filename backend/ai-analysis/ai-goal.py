from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# PROCESSED_DIR should be backend/data/processed
PROCESSED_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "processed")

# Function to read file content robustly
def read_plan(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {path} not found.")
        return ""

cambridge_plan = read_plan("Cambridge_Strategic_Plan_2024-2026.txt")
kitchener_plan = read_plan("Kitchener_Strategic_Plan_2023-2026.txt")
waterloo_plan = read_plan("Waterloo_Strategic_Plan_2023-2026.txt")

# Load environment variables from .env in project root
# Script is in backend/ai-analysis/, .env is in project root
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), ".env")
load_dotenv(dotenv_path)

client = OpenAI()

def get_overview(plan_text, city_name):
    if not plan_text:
        return f"No plan data for {city_name}."
    
    print(f"Generating overview for {city_name}...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a policy analyst summarizing city strategic plans."},
                {"role": "user", "content": f"Please read this document and give me a overview of each of the main goals and objectives (housing, transportation, healthcare, employment, and placemaking):\n\n{plan_text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating overview for {city_name}: {e}"

cambridge_overview = get_overview(cambridge_plan, "Cambridge")
kitchener_overview = get_overview(kitchener_plan, "Kitchener")
waterloo_overview = get_overview(waterloo_plan, "Waterloo")

print("\n--- CAMBRIDGE OVERVIEW ---")
print(cambridge_overview)
print("\n--- KITCHENER OVERVIEW ---")
print(kitchener_overview)
print("\n--- WATERLOO OVERVIEW ---")
print(waterloo_overview)

# 4. Generate Regional Overview (Combined)
def get_regional_overview(p1, p2, p3):
    print("Generating Regional Overview (Waterloo + Kitchener + Cambridge)...")
    combined_text = f"WATERLOO PLAN:\n{p1}\n\nKITCHENER PLAN:\n{p2}\n\nCAMBRIDGE PLAN:\n{p3}"
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a regional strategic advisor. Synthesize multiple city plans into one cohesive regional vision."},
                {"role": "user", "content": f"Please read these three strategic plans and provide a high-level regional overview of the main goals and objectives for the entire Kitchener-Waterloo-Cambridge area (housing, transportation, healthcare, employment, and placemaking):\n\n{combined_text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating regional overview: {e}"

regional_overview = get_regional_overview(waterloo_plan, kitchener_plan, cambridge_plan)

print("\n--- REGIONAL OVERVIEW ---")
print(regional_overview)

# Database setup
# Ensure the database directory exists
DB_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "goals.db")

db = sqlite3.connect(DB_PATH)
cursor = db.cursor()

# delete previous data
cursor.execute("DELETE FROM goals")

# Insert or replace overviews
print(f"Saving goals to {DB_PATH}...")
cursor.execute("INSERT OR REPLACE INTO goals (area, goals) VALUES (?, ?)", ("Cambridge", cambridge_overview))
cursor.execute("INSERT OR REPLACE INTO goals (area, goals) VALUES (?, ?)", ("Kitchener", kitchener_overview))
cursor.execute("INSERT OR REPLACE INTO goals (area, goals) VALUES (?, ?)", ("Waterloo", waterloo_overview))
cursor.execute("INSERT OR REPLACE INTO goals (area, goals) VALUES (?, ?)", ("Regional", regional_overview))

db.commit()
db.close()
print("Done!")

