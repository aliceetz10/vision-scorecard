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
        print(f"Warning: {GOALS_DB_PATH} not found.")
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

def fetch_recent_metrics(table_name):
    print(f"📁 Fetching recent {table_name} metrics...")
    if not os.path.exists(METRICS_DB_PATH):
        print(f"Warning: {METRICS_DB_PATH} not found.")
        return "No metrics data found."
    
    conn = sqlite3.connect(METRICS_DB_PATH)
    cursor = conn.cursor()
    try:
        # Get latest 6 months of data
        cursor.execute(f"SELECT area, month, rate FROM {table_name} ORDER BY date DESC LIMIT 6")
        rows = cursor.fetchall()
        return "\n".join([f"- {month} ({area}): {rate}%" for area, month, rate in rows])
    except sqlite3.OperationalError:
        return f"{table_name} table not found."
    finally:
        conn.close()

# 2. Get the data
goals_text = fetch_goals()
employment_data = fetch_recent_metrics("employment")
unemployment_data = fetch_recent_metrics("unemployment")

# 3. AI Analysis Function
def analyze_data(metric_type, data_text, goals_context):
    print(f"🧠 AI is analyzing {metric_type}...")
    
    # Get latest rate for context in prompt
    latest_status = get_latest_status(metric_type.lower())
    
    prompt = f"""
    You are a policy analyst for the Kitchener-Waterloo-Cambridge region.
    
    ### DATA TO ANALYZE ({metric_type}):
    Current Rate: {latest_status}
    Recent Trend:
    {data_text}
    
    ### REGIONAL STRATEGIC GOALS:
    {goals_context}
    
    ### TASK:
    1. Summarize the current trend of {metric_type}.
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

# Get latest rate for background info
def get_latest_status(table_name):
    if not os.path.exists(METRICS_DB_PATH): return "Unknown"
    m_conn = sqlite3.connect(METRICS_DB_PATH)
    m_cursor = m_conn.cursor()
    try:
        m_cursor.execute(f"SELECT rate, month FROM {table_name} ORDER BY date DESC LIMIT 1")
        row = m_cursor.fetchone()
        return f"{row[1]}: {row[0]}%" if row else "Data Unavailable"
    except:
        return "Unknown"
    finally:
        m_conn.close()

# 4. Perform Analysis
emp_result = analyze_data("Employment", employment_data, goals_text)
unemp_result = analyze_data("Unemployment", unemployment_data, goals_text)

# 5. Save to overview.db
print("\n💾 Saving results to overview.db...")
if not os.path.exists(OVERVIEW_DB_PATH):
    print(f"Error: {OVERVIEW_DB_PATH} not found.")
else:
    conn = sqlite3.connect(OVERVIEW_DB_PATH)
    cursor = conn.cursor()

    # Clear and Insert
    cursor.execute("DELETE FROM employment")

    # Insert Unemployment (is_employment = 0)
    cursor.execute("""
        INSERT INTO employment (status, analysis, is_employment) 
        VALUES (?, ?, ?)
    """, (unemp_result['status'], unemp_result['analysis'], 0))

    # Insert Employment (is_employment = 1)
    cursor.execute("""
        INSERT INTO employment (status, analysis, is_employment) 
        VALUES (?, ?, ?)
    """, (emp_result['status'], emp_result['analysis'], 1))

    conn.commit()
    conn.close()
    print("Analysis complete and saved to frontend/overview.db")

print("\n🎉 REFRESH YOUR FRONTEND TO SEE THE NEW CATEGORIZED BADGES!")