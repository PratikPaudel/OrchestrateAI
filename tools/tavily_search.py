from tavily import TavilyClient
import os

class TavilySearchTool:
    def __init__(self):
        # You'll need to set your Tavily API key
        self.client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))
    
    def search(self, query, max_results=5):
        """Perform a web search using Tavily API"""
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            return response
        except Exception as e:
            return f"Search error: {str(e)}"