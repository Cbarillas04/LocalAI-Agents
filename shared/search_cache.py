import json
from datetime import datetime, timezone, timedelta
from shared.database import DatabaseManager

class SearchCache:
    def __init__(self, db_path = None):
        self.db_manager = DatabaseManager(db_path)
        self.expiration_period = timedelta(hours = 24)
        with self.db_manager.connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS search_cache(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT UNIQUE NOT NULL,
                    results TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );  
            """)

    # Get and return the results from query
    # Simple matching for now, to-do(later) add semantic matching
    def get_search_cache_by_query(self, query):
        query = query.strip().lower()
        with self.db_manager.connection() as connection:
            cursor = connection.execute(
                "SELECT * FROM search_cache WHERE query = ?", (query,)
            )
            result = cursor.fetchone()
            if result is None:
                return None

            created_at = datetime.fromisoformat(result[3])
            current_time = datetime.now(timezone.utc)

        # Check if cache expired
        if self.expiration_period < current_time - created_at:
            return None

        return json.loads(result[2])

    # Create a cache
    def create_cache(self, query, results):
        query = query.strip().lower()
        with self.db_manager.connection() as connection:
            connection.execute("""
                INSERT INTO search_cache (query, results, created_at)
                VALUES (?, ?, ?)
                -- If there is a duplicate entry, replace it
                ON CONFLICT (query) DO UPDATE SET
                    results = excluded.results,
                    created_at = excluded.created_at;
            """, (query, json.dumps(results), datetime.now(timezone.utc).isoformat()))