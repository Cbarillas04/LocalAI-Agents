import sqlite3
from datetime import date
from pathlib import Path

# Track the Tavily API credits used
class UsageTracking:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent.parent/"data"/"local_ai.db"
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_date TEXT,
                credits_used INTEGER,
                usage_type TEXT,
                endpoint TEXT,
                request_status TEXT
            );
        """)
        self.connection.commit()
        self.connection.close()

    # Insert a row when API credit(s) used
    def create_usage(self, credits_used, usage_type, endpoint, request_status):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("""
            INSERT INTO api_usage (request_date, credits_used, usage_type, endpoint, request_status)
            VALUES (?, ?, ? ,? , ?);
        """, (date.today(),credits_used, usage_type, endpoint, request_status))
        self.connection.commit()
        self.connection.close()

    # Get total credits used for this month
    def get_monthly_usage(self):
        today = date.today()
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.execute("""
            SELECT SUM(credits_used)
            FROM api_usage
            WHERE request_date LIKE ?;
        """, (f'{today.strftime("%Y-%m")}-%',))
        result = cursor.fetchone()[0] or 0
        self.connection.close()
        return result
    
    def get_usage_history(self):
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.execute("""
            SELECT * FROM api_usage
            ORDER BY id DESC
        """)
        result = cursor.fetchall()
        self.connection.close()
        return result