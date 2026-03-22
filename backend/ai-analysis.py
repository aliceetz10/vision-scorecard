import os
import sqlite3
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

# Load API key
load_dotenv()

print("=" * 60)
print("🤖 LANGCHAIN AI ANALYZER - Vision One Million Scorecard")
print("=" * 60)

# 1. Connect to metrics.db
print("\n📁 Step 1: Connecting to metrics.db...")
db = SQLDatabase.from_uri("sqlite:///backend/database/metrics.db")
print("   ✅ Connected!")

# 2. Create AI model
print("\n🤖 Step 2: Loading AI model...")
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
print("   ✅ Ready!")

# 3. Create SQL toolkit
print("\n🛠️ Step 3: Setting up SQL tools...")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
print("   ✅ Tools ready!")

# 4. Create agent
print("\n🧠 Step 4: Creating AI Agent...")
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type="openai-tools"
)
print("   ✅ Agent ready!")

# 5. Questions for AI
print("\n" + "=" * 60)
print("❓ QUESTIONS FOR AI:")
print("=" * 60)

unemployment_question = """
Analyze the unemployment data for Kitchener-Cambridge-Waterloo.
Answer:
1. What is the current unemployment rate and trend?
2. What does this mean for the region's readiness for growth?
3. One actionable recommendation.

Keep it concise (4-6 sentences).
"""

employment_question = """
Analyze the employment data for Kitchener-Cambridge-Waterloo.
Answer:
1. What is the current employment rate and trend?
2. What does this mean for the region's readiness for growth?
3. One actionable recommendation.

Keep it concise (4-6 sentences).
"""

# 6. Run agent for both
print("\n🧠 AI IS ANALYZING UNEMPLOYMENT...")
unemployment_analysis = agent.run(unemployment_question)

print("\n🧠 AI IS ANALYZING EMPLOYMENT...")
employment_analysis = agent.run(employment_question)

# 7. Save to overview.db
print("\n💾 Step 5: Saving to overview.db...")

overview_db = 'frontend/overview.db'
conn = sqlite3.connect(overview_db)
cursor = conn.cursor()

# Get latest values for status
def get_latest_rate(table_name):
    metrics_conn = sqlite3.connect('backend/database/metrics.db')
    metrics_cursor = metrics_conn.cursor()
    metrics_cursor.execute(f"SELECT rate, month FROM {table_name} ORDER BY date DESC LIMIT 1")
    row = metrics_cursor.fetchone()
    metrics_conn.close()
    return f"{row[1]}: {row[0]}%" if row else "Unknown"

unemployment_status = f"Unemployment Rate: {get_latest_rate('unemployment')}"
employment_status = f"Employment Rate: {get_latest_rate('employment')}"

# Clear old entries in employment table if desired (optional)
cursor.execute("DELETE FROM employment")

# Insert Unemployment analysis (is_employment = 0)
cursor.execute("""
    INSERT INTO employment (status, analysis, is_employment) 
    VALUES (?, ?, ?)
""", (unemployment_status, unemployment_analysis, 0))

# Insert Employment analysis (is_employment = 1)
cursor.execute("""
    INSERT INTO employment (status, analysis, is_employment) 
    VALUES (?, ?, ?)
""", (employment_status, employment_analysis, 1))

conn.commit()
conn.close()
print("   ✅ Saved to overview.db 'employment' table!")

print("\n" + "=" * 60)
print("🎉 COMPLETE! Refresh your frontend to see the AI insight!")
print("=" * 60)