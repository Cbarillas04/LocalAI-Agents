from shared.usage_tracking import UsageTracking

# Test 1: usage record correctly inserted into db
def test_create_usage(tmp_path):
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    tracker.create_usage(1, "estimated", "search", "success")
    result = tracker.get_usage_history()
    assert result is not None

# Test 2: current month are sum
def test_get_monthly_usage(tmp_path):
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    tracker.create_usage(1, "estimated", "search", "success")
    result = tracker.get_monthly_usage()
    assert result == 1

# Test 3: monthly usage only counts this month and not previous
def  test_get_monthly_usage_ignores_others(tmp_path):
    import sqlite3
    from datetime import datetime, timedelta
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    connection = sqlite3.connect(db_path)
    tracker.create_usage(1, "estimated", "search", "success")
    tracker.create_usage(1, "estimated", "search", "success")
    prev_month = datetime.today() - timedelta(days=32)
    connection.execute("""
        UPDATE api_usage
        SET request_date = ?
        WHERE id = 2
    """,(prev_month,))
    connection.commit()
    connection.close()
    result = tracker.get_monthly_usage()
    assert result == 1

# Test 4: 0 when no current month record exists
def test_get_monthly_usage_miss(tmp_path):
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    result = tracker.get_monthly_usage()
    assert result == 0

# Test 5: Verify all usage records are returned
def test_get_usage_history(tmp_path):
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    tracker.create_usage(1, "estimated", "search", "success")
    tracker.create_usage(1, "estimated", "search", "success")
    result = tracker.get_usage_history()
    assert len(result) == 2

# Test 6: record return the newest first
def test_get_usage_history_order(tmp_path):
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    tracker.create_usage(1, "estimated", "search", "success")
    tracker.create_usage(1, "estimated", "search", "failure")
    result = tracker.get_usage_history()
    assert result[0][5] == "failure"

# Test 7: each record inserted does not overwrite another
def test_usage_records_independent(tmp_path):
    db_path = tmp_path / "test_usage.db"
    tracker = UsageTracking(db_path)
    tracker.create_usage(1, "estimated", "search", "success")
    tracker.create_usage(1, "estimated", "search", "failure")
    result = tracker.get_usage_history()
    assert result[0][5] == "failure" and result[1][5] == "success"