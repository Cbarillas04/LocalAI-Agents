import sqlite3
import pytest
from pathlib import Path
from shared.database import DatabaseManager

# Test 1: Test custom database path
def test_database_manager_custom(tmp_path):
    custom_path = tmp_path / 'custom'
    db_manager = DatabaseManager(custom_path)

    assert db_manager.db_path == custom_path

# Test 2: Default path
def test_database_manager_db(tmp_path):
    db_manager = DatabaseManager()

    assert db_manager.db_path == Path(__file__).resolve().parent.parent / "data" / "local_ai.db"

# Test 3: Connection is established
def test_get_connection(tmp_path):
    db_path = tmp_path / "test.db"
    db_manager = DatabaseManager(db_path)
    result = db_manager.get_connection()

    assert isinstance(result, sqlite3.Connection)
    result.close()

# Test 4: get_connection automatically creates dir parent
def test_get_connection_creates_directory(tmp_path):
    db_path = tmp_path / "nested" / "data.db"
    db_manager = DatabaseManager(db_path)
    result = db_manager.get_connection()

    assert db_manager.db_path.exists()
    assert isinstance(result, sqlite3.Connection)
    result.close()

# Test 5: Ensure that "connection" commits and closes db connections
def test_connection_commits(tmp_path):
    db_path = tmp_path / "test.db"
    db_manager = DatabaseManager(db_path)
    # create temp table and insert value into it
    with db_manager.connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS test_table(
                name TEXT PRIMARY KEY
            );  
        """)

        connection.execute(
            "INSERT INTO test_table (name) VALUES (?)",
            ("LocalAI",)
        )

    # Open a new connection to db and test grab inserted value
    with db_manager.connection() as connection:
        cursor = connection.execute("SELECT * FROM test_table")
        result = cursor.fetchone()

    assert result == ("LocalAI",)

# Test 6: rollback occurs on error
def test_connection_rolls_back(tmp_path):
    db_path = tmp_path / "test.db"
    db_manager = DatabaseManager(db_path)
    # create temp table
    with db_manager.connection() as connection:
        connection.execute("""
                CREATE TABLE IF NOT EXISTS test_table(
                    name TEXT PRIMARY KEY
                );  
            """)

    with pytest.raises(RuntimeError):
        with db_manager.connection() as connection:
            connection.execute(
                "INSERT INTO test_table (name) VALUES (?)",
                ("LocalAI",)
            )
            raise RuntimeError("Test rollback")

    # Confirm that insert wasn't successful
    with db_manager.connection() as connection:
        cursor = connection.execute("SELECT * FROM test_table")
        result = cursor.fetchone()

    assert result is None

# Test 7: Foreign Keys are active
def test_foreign_keys_enabled(tmp_path):
    db_path = tmp_path / "test.db"
    db_manager = DatabaseManager(db_path)
    with db_manager.connection() as connection:
        cursor = connection.execute(
            "PRAGMA foreign_keys"
        )
        result = cursor.fetchall()
    assert result[0][0] == 1
