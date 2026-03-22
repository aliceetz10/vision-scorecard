import sqlite3

conn = sqlite3.connect('overview.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 50)
print("DATABASE SCHEMA")
print("=" * 50)

for table in tables:
    table_name = table[0]
    print(f"\n📁 Table: {table_name}")
    print("-" * 30)
    
    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    for col in columns:
        col_id, col_name, col_type, not_null, default, pk = col
        pk_marker = "🔑 PRIMARY KEY" if pk else ""
        print(f"   {col_name} : {col_type} {pk_marker}")
    
    # Show sample data
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()
    
    if rows:
        print(f"\n   📊 Sample data (first 3 rows):")
        for row in rows:
            print(f"   {row}")

conn.close()

print("\n" + "=" * 50)
print("✅ Schema check complete!")