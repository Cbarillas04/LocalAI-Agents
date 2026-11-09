from shared.search_cache import SearchCache

sample_results = [
    {"title": "Python Documentation", "url": "https://python.org"}
]

# Test 1: nonexistent query returns None
def test_get_cache_miss(tmp_path):
    db_path = tmp_path / "test_cache.db"
    cache = SearchCache(db_path)
    query = "What is Python?"
    result = cache.get_search_cache_by_query(query)
    assert result is None

# Test 2: Saved query returns its results
def test_get_cache_hit(tmp_path):
    db_path = tmp_path / "test_cache.db"
    cache = SearchCache(db_path)
    query = "What is Python?"
    cache.create_cache(query, sample_results)
    result = cache.get_search_cache_by_query(query)
    assert result is not None

# Test 3: Simple matching
# different white space & capitalization still get same query
def test_query_normalization(tmp_path):
    db_path = tmp_path / "test_cache.db"
    cache = SearchCache(db_path)
    query = "What is Python?"
    typo_query = "  wHaT iS pYtHoN?  "
    cache.create_cache(query, sample_results)
    result = cache.get_search_cache_by_query(typo_query)
    assert result == sample_results

# Test 4: Expired entry returns None
def test_cache_expiration(tmp_path):
    import sqlite3
    from datetime import datetime, timezone, timedelta
    db_path = tmp_path / "test_cache.db"
    cache = SearchCache(db_path)
    connection = sqlite3.connect(db_path)
    query = "What is Python?"
    cache.create_cache(query, sample_results)
    query = query.strip().lower() # strip and lower to find the normalized version
    connection.execute("""
        UPDATE search_cache
        SET created_at = ?
        WHERE query = ?
    """, ((datetime.now(timezone.utc) - timedelta(days = 2)).isoformat(), query))
    connection.commit()
    connection.close()
    result = cache.get_search_cache_by_query(query)
    assert result is None

# Test 5: Saving the same query updates its results and timestamp
def test_cache_refresh(tmp_path):
    db_path = tmp_path / "test_cache.db"
    cache = SearchCache(db_path)
    query = "What is Python?"
    cache.create_cache(query, sample_results)
    updated_results = [
        {"title": "Python Docs", "url": "https://python.org"}
    ]
    cache.create_cache(query, updated_results)
    result2 = cache.get_search_cache_by_query(query)
    assert result2 is not None and result2 == updated_results

# Test 6: Different queries hold their results without interference
def test_cache_independence(tmp_path):
    db_path = tmp_path / "test_cache.db"
    cache = SearchCache(db_path)
    query1 = "What is Python?"
    query2 = "What is Java?"
    sample_results2 = [
        {"title": "Java Documentation", "url": "https://docs.oracle.com/en/java/"}
    ]
    cache.create_cache(query1, sample_results)
    cache.create_cache(query2, sample_results2)
    result1 = cache.get_search_cache_by_query(query1)
    result2 = cache.get_search_cache_by_query(query2)
    assert result1 == sample_results and result2 == sample_results2