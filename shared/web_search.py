import os
from dotenv import load_dotenv
from tavily import TavilyClient
from .usage_tracking import UsageTracking
from .search_cache import SearchCache


# Handles websearching through Tavily search API
class WebSearch:
    monthly_credit_limit = 1000
    warning_thresholds = [0.5, 0.75, 0.9, 0.95, 1.0]

    def __init__(self):
        # Load env variables from .env and retrieve API key
        load_dotenv()
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.usage_tracker = UsageTracking()
        self.search_cache = SearchCache()

        if not self.api_key:
            raise ValueError(
                "Tavily API Key not found"
            )

        # Create connection
        self.client = TavilyClient(api_key = self.api_key)

    # Get monthly usage %
    def get_monthly_usage(self):
        return self.usage_tracker.get_monthly_usage() / self.monthly_credit_limit

    # Check if usage is within these warning thresholds
    def warning_check(self):
        highest_threshold = None
        percentage = self. get_monthly_usage()
        for threshold in self.warning_thresholds:
            if threshold <= percentage:
                highest_threshold = threshold
        if highest_threshold is None:
            return highest_threshold
        return highest_threshold * 100
    
    # Search the web returning k max results
    def search(self, query, max_results = 5):
        try:
            # Check if query already exists in cache, return if so
            cache = self.search_cache.get_search_cache_by_query(query)
            if cache is not None:
                return cache

            # Check monthly credit limit
            if self.usage_tracker.get_monthly_usage() >= self.monthly_credit_limit:
                raise ValueError("Monthly credit limit reached")

            # Give warnings depending on API usage %
            warning = self.warning_check()
            if warning is not None:
                print(f"WARNING: Monthly credit usage has reached {warning}%")

            response = self.client.search(
                query = query,
                max_results = max_results,
                search_depth = "basic"
            )
            self.search_cache.create_cache(query, response["results"])
            self.usage_tracker.create_usage(1, "estimated", "search", "success")
            return response["results"]
        except Exception as err:
            self.usage_tracker.create_usage(0, "estimated", "search", "failed")
            print("Error: ", err)
            raise