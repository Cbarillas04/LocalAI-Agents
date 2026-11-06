import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient
from .usage_tracking import UsageTracking


# Handles websearching through Tavily search API
class WebSearch:
    def __init__(self):
        # Load env variables from .env and retrieve API key
        load_dotenv()
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.usage_tracker = UsageTracking()

        if not self.api_key:
            raise ValueError(
                "Tavily API Key nto found"
            )

        # Create connection
        self.client = TavilyClient(api_key = self.api_key)
    
    # Search the web returing k max results
    def search(self, query, max_results = 5):
        try:
            response = self.client.search(
                query = query,
                max_results = max_results,
                search_depth = "basic"
            )
            self.usage_tracker.create_usage(1, "estimated", "search", "success")
            return response["results"]
        except Exception as err:
            self.usage_tracker.create_usage(0, "estimated", "search", "failed")
            print("Error: ", err)
            raise