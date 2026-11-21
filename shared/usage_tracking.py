import sqlite3
from datetime import date
from shared.database import DatabaseManager

# Track the Tavily API credits used
class UsageTracking:
    def __init__(self, db_path = None):
        self.db_manager = DatabaseManager(db_path)
        with self.db_manager.connection() as connection:
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

    # Insert a row when API credit(s) used
    def create_usage(self, credits_used, usage_type, endpoint, request_status):
        with self.db_manager.connection() as connection:
            connection.execute(""" 
                INSERT INTO api_usage (request_date, credits_used, usage_type, endpoint, request_status)
                VALUES (?, ?, ? ,? , ?);
            """, (date.today(),credits_used, usage_type, endpoint, request_status))

    # Get total credits used for this month
    def get_monthly_usage(self):
        today = date.today()
        with self.db_manager.connection() as connection:
            cursor = connection.execute("""
                SELECT SUM(credits_used)
                FROM api_usage
                WHERE request_date LIKE ?;
            """, (f'{today.strftime("%Y-%m")}-%',))
            result = cursor.fetchone()[0] or 0
        return result
    
    def get_usage_history(self):
        with self.db_manager.connection() as connection:
            cursor = connection.execute("""
                SELECT * FROM api_usage
                ORDER BY id DESC
            """)
            result = cursor.fetchall()
        return result