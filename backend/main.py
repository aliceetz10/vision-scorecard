import os
import sys
import sqlite3
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
METRICS_DB = os.path.join(BACKEND_DIR, 'database', 'metrics.db')
OVERVIEW_DB = os.path.join(FRONTEND_DIR, 'overview.db')
GOALS_DB = os.path.join(BACKEND_DIR, 'database', 'goals.db')


# Fetch all data
def fetch_unemployment():
    """Fetch unemployment data from StatsCan"""
    print("📊 Fetching unemployment data...")
    try:
        subprocess.run(['python', 'fetch-scripts/unemployment-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ Unemployment data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch unemployment: {e}")
        return False

def fetch_employment():
    """Fetch employment data from StatsCan"""
    print("📊 Fetching employment data...")
    try:
        subprocess.run(['python', 'fetch-scripts/employment-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ Employment data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch employment: {e}")
        return False

'''
def fetch_housing():
    """Fetch housing starts data from CMHC"""
    print("🏠 Fetching housing data...")
    try:
        subprocess.run(['python', 'fetch-scripts/housing-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ Housing data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch housing: {e}")
        return False

def fetch_transit():
    """Fetch transit ridership data from GRT"""
    print("🚌 Fetching transit data...")
    try:
        subprocess.run(['python', 'fetch-scripts/transit-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ Transit data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch transit: {e}")
        return False

def fetch_hospital():
    """Fetch hospital wait times data"""
    print("🏥 Fetching hospital data...")
    try:
        subprocess.run(['python', 'fetch-scripts/hospital-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ Hospital data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch hospital: {e}")
        return False

def fetch_go_train():
    """Fetch GO Train schedule data"""
    print("🚆 Fetching GO Train data...")
    try:
        subprocess.run(['python', 'fetch-scripts/go-train-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ GO Train data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch GO Train: {e}")
        return False

def fetch_ghg():
    """Fetch GHG emissions data"""
    print("🌍 Fetching GHG data...")
    try:
        subprocess.run(['python', 'fetch-scripts/ghg-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ GHG data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch GHG: {e}")
        return False

def fetch_schools():
    """Fetch school utilization data"""
    print("🏫 Fetching school data...")
    try:
        subprocess.run(['python', 'fetch-scripts/school-fetch.py'], 
                       cwd=BACKEND_DIR, check=True)
        print("✅ School data fetched")
        return True
    except Exception as e:
        print(f"❌ Failed to fetch schools: {e}")
        return False
'''

# Run AI analysis
def fetch_goals():
    """Fetch strategic goals from goals.db"""
    print("📁 Fetching strategic goals...")
    if not os.path.exists(GOALS_DB):
        print("⚠️ Goals database not found")
        return "No strategic goals found."
    
    conn = sqlite3.connect(GOALS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT area, goals FROM goals")
        rows = cursor.fetchall()
        return "\n".join([f"### {area} Strategic Goals:\n{goals}" for area, goals in rows])
    except:
        return "Goals table not found."
    finally:
        conn.close()

def fetch_metric_data(table_name, value_column, city_filter=None):
    """Fetch recent data for a metric"""
    print(f"📁 Fetching {table_name} data...")
    if not os.path.exists(METRICS_DB):
        print("⚠️ Metrics database not found")
        return ""
    
    conn = sqlite3.connect(METRICS_DB)
    cursor = conn.cursor()
    try:
        if city_filter:
            cursor.execute(f"SELECT date, {value_column} FROM {table_name} WHERE city = ? ORDER BY date DESC LIMIT 6", (city_filter,))
        else:
            cursor.execute(f"SELECT date, {value_column} FROM {table_name} ORDER BY date DESC LIMIT 6")
        rows = cursor.fetchall()
        return "\n".join([f"- {row[0]}: {row[1]}" for row in rows])
    except Exception as e:
        print(f"⚠️ Could not fetch {table_name}: {e}")
        return f"{table_name} data not available."
    finally:
        conn.close()

def analyze_metric(metric_name, data_text, goals_text):
    """Run AI analysis for a single metric"""
    print(f"🧠 Analyzing {metric_name}...")
    
    prompt = f"""
    You are a policy analyst for the Kitchener-Waterloo-Cambridge region.
    
    ### DATA TO ANALYZE ({metric_name}):
    Recent Trend:
    {data_text}
    
    ### REGIONAL STRATEGIC GOALS:
    {goals_text}
    
    ### TASK:
    1. Summarize the current trend.
    2. Evaluate if the region is meeting its strategic goals.
    3. Provide one specific, actionable recommendation.
    4. Determine the level of completion:
       - ACHIEVED
       - ON TRACK
       - IN PROGRESS
       - NEEDS ATTENTION
       - NO ASSESSMENT
    
    Format output as JSON with keys: "status" and "analysis"
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )
        result = eval(response.choices[0].message.content)
        print(f"✅ {metric_name} complete - Status: {result.get('status', 'Unknown')}")
        return result
    except Exception as e:
        print(f"❌ Failed to analyze {metric_name}: {e}")
        return {"status": "NO ASSESSMENT", "analysis": f"Error: {e}"}

def run_ai_analysis():
    """Run AI analysis on all metrics"""
    print("\n" + "="*50)
    print("🤖 RUNNING AI ANALYSIS")
    print("="*50)
    
    goals_text = fetch_goals()
    results = {}
    
    # Define all metrics to analyze
    metrics = [
        ("Unemployment Rate", fetch_metric_data("unemployment", "rate", "Kitchener-Cambridge-Waterloo")),
        ("Employment Rate", fetch_metric_data("employment", "rate", "Kitchener-Cambridge-Waterloo")),
        ("Housing Starts", fetch_metric_data("housing", "starts")),
        ("Transit Ridership", fetch_metric_data("transit", "ridership")),
        ("Hospital Wait Times", fetch_metric_data("hospital_wait_times", "wait_time")),
        ("GO Train Service", fetch_go_train_data()),
        ("GHG Emissions", fetch_metric_data("ghg_emissions", "emissions_tonnes")),
        ("School Utilization", fetch_school_summary()),
    ]
    
    for name, data in metrics:
        if data and "No data" not in data:
            result = analyze_metric(name, data, goals_text)
            results[name] = result
        else:
            results[name] = {"status": "NO ASSESSMENT", "analysis": "No data available for this metric."}
    
    return results


def fetch_go_train_data():
    """Fetch GO Train data (custom)"""
    print("🚆 Fetching GO Train data...")
    if not os.path.exists(METRICS_DB):
        return ""
    
    conn = sqlite3.connect(METRICS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT day_type, trips_total FROM go_train ORDER BY date DESC")
        rows = cursor.fetchall()
        return "\n".join([f"- {row[0]}: {row[1]} trips" for row in rows])
    except:
        return "GO Train data not available."
    finally:
        conn.close()

def fetch_school_summary():
    """Fetch school utilization summary"""
    print("🏫 Fetching school data...")
    if not os.path.exists(METRICS_DB):
        return ""
    
    conn = sqlite3.connect(METRICS_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT city, level, AVG(utilization) FROM school_utilization GROUP BY city, level")
        rows = cursor.fetchall()
        return "\n".join([f"- {row[0]} {row[1]}: {row[2]:.0f}% average utilization" for row in rows])
    except:
        return "School data not available."
    finally:
        conn.close()



# Update overview database
def update_overview_db(ai_results):
    """Save AI analysis results to overview.db"""
    print("\n💾 Saving analysis results to overview.db...")
    
    if not os.path.exists(OVERVIEW_DB):
        print(f"❌ Overview database not found at {OVERVIEW_DB}")
        return False
    
    conn = sqlite3.connect(OVERVIEW_DB)
    cursor = conn.cursor()
    
    # Create or update overview table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS overview (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field TEXT,
            analysis TEXT
        )
    ''')
    
    # Clear old AI analysis entries
    cursor.execute("DELETE FROM overview WHERE field LIKE '%AI Analysis%'")
    
    # Insert new results
    for metric_name, result in ai_results.items():
        cursor.execute('''
            INSERT INTO overview (field, analysis)
            VALUES (?, ?)
        ''', (f"🤖 AI Analysis - {metric_name}", f"{result['status']}: {result['analysis']}"))
    
    conn.commit()
    conn.close()
    print(f"✅ Updated overview.db with {len(ai_results)} AI analyses")
    return True


def run_overview_analysis():
    """Run the frontend overview AI analysis script"""
    print("\n🔎 RUNNING REGIONAL OVERVIEW ANALYSIS...")
    overview_script = os.path.join(FRONTEND_DIR, 'overview.py')
    if not os.path.exists(overview_script):
        print(f"❌ overview.py not found at {overview_script}")
        return False
    try:
        subprocess.run(['python', overview_script], cwd=FRONTEND_DIR, check=True)
        print("✅ Regional overview analysis complete")
        return True
    except Exception as e:
        print(f"❌ Failed to run overview analysis: {e}")
        return False


def main():
    """Main orchestration function"""
    print("\n" + "="*50)
    print("🚀 STARTING VISION ONE MILLION SCORECARD UPDATE")
    print("="*50)
    
    # Step 1: Skip fetch - data already in database
    print("\n📥 STEP 1: SKIPPING FETCH (data already in database)")
    
    # Step 2: Run AI analysis
    print("\n🧠 STEP 2: AI ANALYSIS")
    ai_results = run_ai_analysis()
    
    # Step 3: Update overview database
    print("\n💾 STEP 3: UPDATING DATABASE")
    update_success = update_overview_db(ai_results)
    
    # Step 4: Run regional overview analysis
    print("\n📝 STEP 4: REGIONAL OVERVIEW ANALYSIS")
    run_overview_analysis()
    
    if update_success:
        print("\n" + "="*50)
        print("🎉 UPDATE COMPLETED SUCCESSFULLY!")
        print("="*50)
    else:
        print("\n❌ Failed to update overview database")

# # Main execution
# def main():
#     """Main orchestration function"""
#     print("\n" + "="*50)
#     print("🚀 STARTING VISION ONE MILLION SCORECARD UPDATE")
#     print("="*50)
    
#     # Step 1: Fetch all data
#     print("\n📥 STEP 1: FETCHING DATA")
#     fetch_all = [
#         fetch_unemployment(),
#         fetch_employment(),
#         # fetch_housing(),
#         # fetch_transit(),
#         # fetch_hospital(),
#         # fetch_go_train(),
#         # fetch_ghg(),
#         # fetch_schools()
#     ]
    
#     if not all(fetch_all):
#         print("\n❌ Some data fetches failed")
#         return
    
#     # Step 2: Run AI analysis
#     print("\n🧠 STEP 2: AI ANALYSIS")
#     ai_results = run_ai_analysis()
    
#     # Step 3: Update overview database
#     print("\n💾 STEP 3: UPDATING DATABASE")
#     update_success = update_overview_db(ai_results)
    
#     if update_success:
#         print("\n" + "="*50)
#         print("🎉 UPDATE COMPLETED SUCCESSFULLY!")
#         print("="*50)
#     else:
#         print("\n❌ Failed to update overview database")

if __name__ == "__main__":
    main()