import sqlite3
from pathlib import Path
from contextlib import contextmanager

# Database manager for opening db connections, creating tables, etc
class DatabaseManager:
    def __init__(self, db_path = None):
        if db_path is None:
            self.db_path = Path(__file__).resolve().parent.parent / "data" / "local_ai.db"
        else:
            self.db_path = Path(db_path)

    # Initialize and return a db connection
    def get_connection(self):
        # Ensure data folder exists already, if not create parent
        self.db_path.parent.mkdir(parents = True, exist_ok = True)
        return sqlite3.connect(self.db_path)

    # Automatically handle commiting and closing db connections
    @contextmanager
    def connection(self):
        connection = self.get_connection()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
