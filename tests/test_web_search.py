from shared.web_search import WebSearch
from unittest.mock import patch, MagicMock

# Test 1: Dependencies and API client are correctly initialized
def test_web_search_intialization():
    # mock dependencies used by web search
    with patch("shared.web_search.load_dotenv"),\
        patch("shared.web_search.os.getenv", return_value = "test-api-key"),\
        patch("shared.web_search.TavilyClient") as mock_tavily,\
        patch("shared.web_search.UsageTracking") as mock_usage,\
        patch("shared.web_search.SearchCache") as mock_cache:

        search = WebSearch()

        assert search.api_key == "test-api-key"
        assert search.client == mock_tavily.return_value
        assert search.usage_tracker == mock_usage.return_value
        assert search.search_cache == mock_cache.return_value
        mock_tavily.assert_called_once_with(api_key = "test-api-key")

# Test 2: search returns results
def test_search_success():
    with patch("shared.web_search.load_dotenv"),\
        patch("shared.web_search.os.getenv", return_value = "test-api-key"),\
        patch("shared.web_search.TavilyClient") as mock_tavily,\
        patch("shared.web_search.UsageTracking") as mock_usage,\
        patch("shared.web_search.SearchCache") as mock_cache:

        search = WebSearch()

        mock_usage.return_value.get_monthly_usage.return_value = 0
        mock_cache.return_value.get_search_cache_by_query.return_value = None
        results = [
            {
                "title": "Python",
                "url": "https://python.org",
                "content": "Python is a programming language"
            }
        ]
        mock_tavily.return_value.search.return_value = {"results": results}
        result = search.search("What is Python?")
        assert result == results

        # Tavily was called using the arguments
        mock_tavily.return_value.search.assert_called_once_with(
            query = "What is Python?",
            max_results = 5,
            search_depth = "basic"
        )
        # usage recorded
        mock_usage.return_value.create_usage.assert_called_once_with(
            1,"estimated", "search", "success"
        )
        # results were cached
        mock_cache.return_value.create_cache.assert_called_once_with(
            "What is Python?", results
        )

# Test 3: Verifies that search already exists in cache, grabs from cache if exists
def test_search_cache_hit():
    with patch("shared.web_search.load_dotenv"),\
        patch("shared.web_search.os.getenv", return_value = "test-api-key"),\
        patch("shared.web_search.TavilyClient") as mock_tavily,\
        patch("shared.web_search.SearchCache") as mock_cache:

        search = WebSearch()

        mock_cache.return_value.get_search_cache_by_query.return_value = [
            {
                "id": 1,
                "query" : "What is Python?",
                "results" : "Python is a programming language",
                "created_at": "2026-11-11",
            }
        ]

        results = [
            {
                "title": "Python",
                "url": "https://python.org",
                "content": "Python is a programming language"
            }
        ]
        mock_tavily.return_value.search.return_value = {"results": results}
        result = search.search("What is Python?")
        cached_results = mock_cache.return_value.get_search_cache_by_query.return_value

        # Tavily isn't called
        mock_tavily.return_value.search.assert_not_called()
        # doesn't create same cache entry
        mock_cache.return_value.create_cache.assert_not_called()

        assert result == cached_results

# Test 4: Verifies the Tavily API call fail is err and not added
def test_search_failure():
    import pytest
    with patch("shared.web_search.load_dotenv"), \
        patch("shared.web_search.os.getenv", return_value="test-api-key"), \
        patch("shared.web_search.TavilyClient") as mock_tavily, \
        patch("shared.web_search.UsageTracking") as mock_usage:

        search = WebSearch()
        mock_usage.return_value.create_usage.return_value = [
            {
                "id": 1,
                "request_date": "2026-11-11",
                "credits_used": 0,
                "usage_type": "estimated",
                "endpoint": "search",
                "request_status": "failed"
            }
        ]
        # search raises error
        mock_tavily.return_value.search.side_effect = Exception("API failed")
        with pytest.raises(Exception):
            search.search("What is Python?")
        # Confirm that usage log creation failed
        mock_usage.return_value.create_usage.assert_called_once_with(
            0, "estimated", "search", "failed"
        )

# Test 5: Verify that Api isn't called and cache isn't made when credit limit is hit
def test_monthly_credit_limit():
    import pytest
    with patch("shared.web_search.load_dotenv"), \
        patch("shared.web_search.os.getenv", return_value="test-api-key"), \
        patch("shared.web_search.TavilyClient") as mock_tavily, \
        patch("shared.web_search.UsageTracking") as mock_usage, \
        patch("shared.web_search.SearchCache") as mock_cache:

        search = WebSearch()

        mock_usage.return_value.get_monthly_usage.return_value = 1000
        mock_cache.return_value.get_search_cache_by_query.return_value = None

        # Get ValueError and check if it matches
        with pytest.raises(ValueError, match = "Monthly credit limit reached"):
            search.search("What is Python?")

        # Assure both cache creation and tavily api were not called
        mock_tavily.return_value.search.assert_not_called()
        mock_cache.return_value.create_cache.assert_not_called()
        # Usage tracks failed call
        mock_usage.return_value.create_usage.assert_called_once_with(
            0, "estimated", "search", "failed"
        )

# Test 6: Verify each warning threshold
def test_warning():
    with patch("shared.web_search.load_dotenv"), \
        patch("shared.web_search.os.getenv", return_value="test-api-key"), \
        patch("shared.web_search.UsageTracking") as mock_usage:

        search = WebSearch()
        thresholds = (0, 500, 750, 900, 950)

        def test_warning():
            with patch("shared.web_search.load_dotenv"), \
                    patch("shared.web_search.os.getenv", return_value="test-api-key"), \
                    patch("shared.web_search.UsageTracking") as mock_usage:

                search = WebSearch()
                thresholds = (0, 500, 750, 900, 950)
                for value in thresholds:
                    if value == 0:
                        assert search.warning_check() is None
                        continue
                    mock_usage.return_value.get_monthly_usage.return_value = value
                    assert search.warning_check() == (value / 10)





