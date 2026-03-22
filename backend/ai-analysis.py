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

# 5. Question
print("\n" + "=" * 60)
print("❓ QUESTION FOR AI:")
print("=" * 60)

question = """
Analyze the unemployment data for Kitchener-Cambridge-Waterloo.
Answer:
1. What is the current unemployment rate and trend?
2. What does this mean for the region's readiness for growth?
3. One actionable recommendation.

Keep it concise (4-6 sentences).
"""

print(question)
print("\n🧠 AI IS THINKING...")
print("-" * 60)

# 6. Run agent
response = agent.run(question)

print("\n" + "=" * 60)
print("📊 AI ANALYSIS RESULT")
print("=" * 60)
print(response)
print("=" * 60)

# 7. Save to overview.db
print("\n💾 Step 5: Saving to overview.db...")

overview_db = 'frontend/overview.db'
conn = sqlite3.connect(overview_db)
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO overview (field, analysis) 
    VALUES (?, ?)
""", ('🤖 LangChain AI - Unemployment Analysis', response))

conn.commit()
conn.close()
print("   ✅ Saved to overview.db!")

print("\n" + "=" * 60)
print("🎉 COMPLETE! Refresh your frontend to see the AI insight!")
print("=" * 60)