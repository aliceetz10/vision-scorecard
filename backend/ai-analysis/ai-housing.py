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

def fetch_housing_metrics():
    print("📁 Fetching recent housing metrics...")
    if not os.path.exists(METRICS_DB_PATH):
        return "No metrics data found."
    
    conn = sqlite3.connect(METRICS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get latest 10 housing start records
        cursor.execute("SELECT city, month, starts FROM housing ORDER BY date DESC LIMIT 15")
        rows = cursor.fetchall()
        return "\n".join([f"- {month} ({city}): {starts} units started" for city, month, starts in rows])
    except sqlite3.OperationalError:
        return "Housing table not found."
    finally:
        conn.close()

# 2. Get the data
goals_text = fetch_goals()
housing_data = fetch_housing_metrics()

# 3. AI Analysis Function
def analyze_housing(data_text, goals_context):
    print("🧠 AI is analyzing Housing...")
    
    prompt = f"""
    You are a policy analyst for the Kitchener-Waterloo-Cambridge region focusing on Housing.
    
    ### DATA TO ANALYZE (Housing Starts):
    {data_text}
    
    ### REGIONAL STRATEGIC GOALS:
    {goals_context}
    
    ### TASK:
    1. Summarize the current regional trend in housing starts.
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
housing_result = analyze_housing(housing_data, goals_text)

# 5. Save to overview.db
print("\n💾 Saving results to overview.db...")
if not os.path.exists(OVERVIEW_DB_PATH):
    print(f"Error: {OVERVIEW_DB_PATH} not found.")
else:
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()

    # Clear previous data
    cursor.execute("DELETE FROM housing")

    # Insert the new analysis
    cursor.execute("""
        INSERT INTO housing (status, analysis) 
        VALUES (?, ?)
    """, (housing_result['status'], housing_result['analysis']))

    conn.commit()
    conn.close()
    print("Housing analysis saved to frontend/overview.db")

print("\n🎉 REFRESH YOUR FRONTEND TO SEE THE NEW HOUSING INSIGHT!")