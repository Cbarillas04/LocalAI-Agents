import sqlite3
from shared.usage_tracking import UsageTracking

# Testing
tracker = UsageTracking()
connection = sqlite3.connect(tracker.db_path)

# Table creation
# Usage credit tracker table
connection.execute("""
    CREATE TABLE IF NOT EXISTS api_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_date TEXT,
        credits_used INTEGER,
        usage_type TEXT,
        endpoint TEXT,
        request_status TEXT
    );
""")

# Query Cache Table
connection.execute("""
    CREATE TABLE IF NOT EXISTS search_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT UNIQUE NOT NULL,
        results TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
""")
connection.commit()
connection.close()

# Practice
'''
# Insertion
connection.execute("""
    INSERT INTO api_usage (request_date, credits_used) VALUES (?, ?)""",
    ("2026-11-03", 1)
)

cursor = connection.execute("SELECT * FROM api_usage")
rows = cursor.fetchall()

for row in rows:
    print(row)

# n total searches
cursor = connection.execute("SELECT COUNT(*) FROM api_usage")
result = cursor.fetchone()
print(result)

# Consumed credits
cursor = connection.execute("SELECT SUM(credits_used) FROM api_usage")
result = cursor.fetchone()
print(result)

# Consumed credits by date
cursor = connection.execute("""
    SELECT request_date, SUM(credits_used)
    FROM api_usage
    GROUP BY request_date;
""")
result = cursor.fetchall()
for r in result:
    print(r)

cursor = connection.execute("""
    SELECT COUNT(*)
    FROM api_usage
    WHERE request_date LIKE ?;
""", ('2026-11-%',))

result = cursor.fetchone()
print(result)

cursor = connection.execute("PRAGMA table_info(api_usage)")
for column in cursor.fetchall():
    print(column)


connection.commit()



connection.close()
'''