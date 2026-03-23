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

def fetch_transit_metrics():
    print("📁 Fetching recent transit metrics...")
    if not os.path.exists(METRICS_DB_PATH):
        return "No metrics data found."
    
    conn = sqlite3.connect(METRICS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get latest 15 transit records
        cursor.execute("SELECT year, month, ridership FROM transit ORDER BY date DESC LIMIT 15")
        rows = cursor.fetchall()
        return "\n".join([f"- {month} ({year}): {ridership} ridership" for year, month, ridership in rows])
    except sqlite3.OperationalError:
        return "Transit table not found."
    finally:
        conn.close()

def fetch_train_metrics():
    print("📁 Fetching recent train metrics...")
    if not os.path.exists(METRICS_DB_PATH):
        return "No metrics data found."
    
    conn = sqlite3.connect(METRICS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get latest 15 train records from go_train table
        # Corrected columns: using trips_total as ridership proxy
        cursor.execute("SELECT date, line, trips_total FROM go_train ORDER BY date DESC LIMIT 15")
        rows = cursor.fetchall()
        return "\n".join([f"- {date} ({line}): {trips} total trips" for date, line, trips in rows])
    except sqlite3.OperationalError:
        return "GO Train table not found."
    finally:
        conn.close()

# 2. Get the data
goals_text = fetch_goals()
transit_data = fetch_transit_metrics()
train_data = fetch_train_metrics()

# 3. AI Analysis Function
def analyze_transport(transport_type, data_text, goals_context):
    print(f"🧠 AI is analyzing {transport_type}...")
    
    prompt = f"""
    You are a policy analyst for the Kitchener-Waterloo-Cambridge region focusing on {transport_type}.
    
    ### DATA TO ANALYZE ({transport_type} Statistics):
    {data_text}
    
    ### REGIONAL STRATEGIC GOALS:
    {goals_context}
    
    ### TASK:
    1. Summarize the current regional trend in {transport_type}.
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
transit_result = analyze_transport("Regional Transit (GRT)", transit_data, goals_text)
train_result = analyze_transport("GO Train Service", train_data, goals_text)

# 5. Save to overview.db
print("\n💾 Saving results to overview.db...")
if not os.path.exists(OVERVIEW_DB_PATH):
    print(f"Error: {OVERVIEW_DB_PATH} not found.")
else:
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()

    # Clear previous data
    cursor.execute("DELETE FROM transit")

    # Insert Transit (is_transit = 1)
    cursor.execute("""
        INSERT INTO transit (is_transit, status, analysis) 
        VALUES (?, ?, ?)
    """, (1, transit_result['status'], transit_result['analysis']))

    # Insert GO Train (is_transit = 0)
    cursor.execute("""
        INSERT INTO transit (is_transit, status, analysis) 
        VALUES (?, ?, ?)
    """, (0, train_result['status'], train_result['analysis']))

    conn.commit()
    conn.close()
    print("Transport analysis saved to frontend/overview.db")

print("\n🎉 REFRESH YOUR FRONTEND TO SEE THE NEW TRANSPORT INSIGHT!")
