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
GOALS_DB_PATH = os.path.join(PROJECT_ROOT, "backend", "database", "goals.db")
METRICS_DB_PATH = os.path.join(PROJECT_ROOT, "backend", "database", "metrics.db")
OVERVIEW_DB_PATH = os.path.join(PROJECT_ROOT, "frontend", "overview.db")

# 1. Helper to connect and fetch data
def fetch_goals():
    print("📁 Fetching regional goals...")
    if not os.path.exists(GOALS_DB_PATH):
        return "No strategic goals found in database."
    
    conn = sqlite3.connect(GOALS_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT area, goals FROM goals")
        rows = cursor.fetchall()
        return "\n".join([f"### {area} Strategic Goals:\n{goals}" for area, goals in rows])
    except sqlite3.OperationalError:
        return "Goals table not found."
    finally:
        conn.close()

def fetch_ghg_metrics():
    print("📁 Fetching recent ghg metrics...")
    if not os.path.exists(METRICS_DB_PATH):
        return "No metrics data found."
    
    conn = sqlite3.connect(METRICS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get latest 15 transit records
        cursor.execute("SELECT year, sector, emissions_tonnes, notes FROM ghg_emissions ORDER BY year DESC LIMIT 15")
        rows = cursor.fetchall()
        return "\n".join([f"- {sector} ({year}): {emissions_tonnes} tonnes" for year, sector, emissions_tonnes, notes in rows])
    except sqlite3.OperationalError:
        return "GHG Emissions table not found."
    finally:
        conn.close()

def fetch_school_metrics():
    print("📁 Fetching recent school metrics...")
    if not os.path.exists(METRICS_DB_PATH):
        return "No metrics data found."
    
    conn = sqlite3.connect(METRICS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get latest 15 school utilization records
        cursor.execute("SELECT school_name, board, level, city, capacity, enrolment, utilization, fci, fci_year FROM school_utilization ORDER BY fci_year DESC LIMIT 15")
        rows = cursor.fetchall()
        return "\n".join([f"- {school_name} ({city}): {capacity} capacity, {enrolment} enrolment, {utilization} utilization, {fci} fci, {fci_year} fci_year" for school_name, board, level, city, capacity, enrolment, utilization, fci, fci_year in rows])
    except sqlite3.OperationalError:
        return "School Utilization table not found."
    finally:
        conn.close()

# 2. Get the data
goals_text = fetch_goals()
ghg_data = fetch_ghg_metrics()
school_data = fetch_school_metrics()

# 3. AI Analysis Function
def analyze_placemaking(placemaking_type, data_text, goals_context):
    print(f"🧠 AI is analyzing {placemaking_type}...")
    
    prompt = f"""
    You are a policy analyst for the Kitchener-Waterloo-Cambridge region focusing on {placemaking_type}.
    
    ### DATA TO ANALYZE ({placemaking_type} Statistics):
    {data_text}
    
    ### REGIONAL STRATEGIC GOALS:
    {goals_context}
    
    ### TASK:
    1. Summarize the current regional trend in {placemaking_type}.
    2. Evaluate if the region is meeting its strategic goals based on this data.
    3. Provide one specific, actionable recommendation for regional planners.
    4. Determine the level of completion:
       - ACHIEVED: Goal met or exceeded.
       - ON TRACK: Milestones are being met.
       - IN PROGRESS: Significant work remains or uncertainty exists.
       - NEEDS ATTENTION: Critical concerns about meeting goals.
       - NO ASSESSMENT: Insufficient data.
    
    Format the output as a JSON object with these keys:
    "status": (The category name only: ACHIEVED, ON TRACK, IN PROGRESS, NEEDS ATTENTION, or NO ASSESSMENT)
    "analysis": (Your 4-6 sentence summary including the trend, goal evaluation, and recommendation)
    """
    
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
        return {"status": "NO ASSESSMENT", "analysis": f"Error during AI analysis: {e}"}

# 4. Perform Analysis
ghg_result = analyze_placemaking("GHG Emissions", ghg_data, goals_text)
school_result = analyze_placemaking("School Utilization", school_data, goals_text)

# 5. Save to overview.db
print("\n💾 Saving results to overview.db...")
if not os.path.exists(OVERVIEW_DB_PATH):
    print(f"Error: {OVERVIEW_DB_PATH} not found.")
else:
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()

    # Clear previous data
    cursor.execute("DELETE FROM placemaking")

    # Insert Schools (is_school = 1)
    cursor.execute("""
        INSERT INTO placemaking (is_school, status, analysis) 
        VALUES (?, ?, ?)
    """, (1, school_result['status'], school_result['analysis']))

    # Insert GHG (is_school = 0)
    cursor.execute("""
        INSERT INTO placemaking (is_school, status, analysis) 
        VALUES (?, ?, ?)
    """, (0, ghg_result['status'], ghg_result['analysis']))

    conn.commit()
    conn.close()
    print("Placemaking analysis saved to backend/overview.db")

print("\n🎉 REFRESH YOUR FRONTEND TO SEE THE NEW PLACEMAKING INSIGHT!")
