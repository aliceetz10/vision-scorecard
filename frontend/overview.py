import os
import sqlite3
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI()

# Get the directory of the current script and the project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Define robust paths for all databases
OVERVIEW_DB_PATH = os.path.join(SCRIPT_DIR, "overview.db")

def fetch_employment():
    print("📁 Fetching employment data...")
    if not os.path.exists(OVERVIEW_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, analysis, is_employment FROM employment")
        rows = cursor.fetchall()
        return "\n".join([f"### {status} Strategic Goals:\n{analysis}" for status, analysis, is_employment in rows])
    except sqlite3.OperationalError:
        return "Employment table not found."
    finally:
        conn.close()

def fetch_housing():
    print("📁 Fetching housing data...")
    if not os.path.exists(OVERVIEW_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, analysis FROM housing")
        rows = cursor.fetchall()
        return "\n".join([f"### {status} Strategic Goals:\n{analysis}" for status, analysis in rows])
    except sqlite3.OperationalError:
        return "Housing table not found."
    finally:
        conn.close()

def fetch_transit():
    print("📁 Fetching transit data...")
    if not os.path.exists(OVERVIEW_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, analysis FROM transit WHERE is_transit = 1")
        rows = cursor.fetchall()
        return "\n".join([f"### {status} Strategic Goals:\n{analysis}" for status, analysis in rows])
    except sqlite3.OperationalError:
        return "Transit table not found."
    finally:
        conn.close()

def fetch_placemaking():
    print("📁 Fetching placemaking data...")
    if not os.path.exists(OVERVIEW_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, analysis FROM placemaking WHERE is_school = 0")
        rows = cursor.fetchall()
        return "\n".join([f"### {status} Strategic Goals:\n{analysis}" for status, analysis in rows])
    except sqlite3.OperationalError:
        return "Placemaking table not found."
    finally:
        conn.close()

def fetch_health():
    print("📁 Fetching health data...")
    if not os.path.exists(OVERVIEW_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, analysis FROM healthcare")
        rows = cursor.fetchall()
        return "\n".join([f"### {status} Strategic Goals:\n{analysis}" for status, analysis in rows])
    except sqlite3.OperationalError:
        return "Healthcare table not found."
    finally:
        conn.close()

def fetch_education():
    print("📁 Fetching education data...")
    if not os.path.exists(OVERVIEW_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT status, analysis FROM placemaking WHERE is_school = 1")
        rows = cursor.fetchall()
        return "\n".join([f"### {status} Strategic Goals:\n{analysis}" for status, analysis in rows])
    except sqlite3.OperationalError:
        return "Placemaking table (education) not found."
    finally:
        conn.close()

employment_data = fetch_employment()
housing_data = fetch_housing()
transit_data = fetch_transit()
placemaking_data = fetch_placemaking()
health_data = fetch_health()
education_data = fetch_education()

def ai_analysis():
    prompt = f"""
    You are a policy analyst for the Kitchener-Waterloo-Cambridge region focusing on the overall vision scorecard.
    
    ### DATA TO ANALYZE (Overall Vision Scorecard):
    {employment_data}
    {housing_data}
    {transit_data}
    {placemaking_data}
    {health_data}
    {education_data}
    
    ### TASK:
    1. Summarize the current regional trend in the overall vision scorecard.
    2. Provide some specific, actionable recommendations for regional planners.

    Format the output as a markdown with these keys:
    "analysis": (Your 4-6 sentence summary including the trend, goal evaluation, and recommendation)
    "recommendations": (Your 4-6 sentence summary including the trend, goal evaluation, and recommendation)
    "summary": (Your 1-2 sentence summary of the overall vision scorecard)"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "You are a professional regional policy analyst who outputs JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"analysis": f"Error during AI analysis: {e}", "recommendations": "", "summary": ""}

# Perform Analysis
ai_results = ai_analysis()

# Prepare combined analysis for the database
combined_analysis = f"""
## Regional Vision Analysis
{ai_results.get('analysis', '')}

## Strategic Recommendations
{ai_results.get('recommendations', '')}

## Executive Summary
{ai_results.get('summary', '')}
"""

# Save to overview.db
print("\n💾 Saving results to overview.db...")
if not os.path.exists(OVERVIEW_DB_PATH):
    print(f"Error: {OVERVIEW_DB_PATH} not found.")
else:
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()

    # Clear previous overview data
    cursor.execute("DELETE FROM overview WHERE field = 'Regional Vision Scorecard'")

    # Insert overview
    cursor.execute("""
        INSERT INTO overview (field, analysis) 
        VALUES (?, ?)
    """, ("Regional Vision Scorecard", combined_analysis,))

    conn.commit()
    conn.close()
    print("Overview analysis saved to frontend/overview.db")

print("\n🎉 REFRESH YOUR FRONTEND TO SEE THE NEW OVERVIEW INSIGHT!")