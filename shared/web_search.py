import os
import requests
from dotenv import load_dotenv
from tavily import TavilyClient


# Handles websearching through Tavily search API
class WebSearch:
    def __init__(self):
        # Load env variables from .env and retrieve API key
        load_dotenv()
        self.api_key = os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Tavily API Key nto found"
            )

        # Create connection
        self.client = TavilyClient(api_key = self.api_key)
        
    """"
    # Tavily API usage tracking
    def get_usage(self):
        try:
            response = requests.get(
                url = "https://api.tavily.com/usage",
                headers = {"Authorization" : f"Bearer + {self.api_key}"},
                timeout = 5
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as err:
            print(f"Error retrieving Travily Usage: {err}")
            raise
    """
    
    # Search the web returing k max results
    def search(self, query, max_results = 5):
        response = self.client.search(
            query = query,
            max_results = max_results,
            search_depth = "basic"
        )
        return response["results"]