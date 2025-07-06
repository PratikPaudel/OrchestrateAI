import os
from exa_py import Exa

class ExaSearchTool:
    def __init__(self):
        self.api_key = os.getenv('EXA_API_KEY')
        self.client = Exa(self.api_key)

    def search(self, query, max_results=5):
        """Perform a web search using Exa API and return results with contents as dictionaries."""
        try:
            response = self.client.search_and_contents(query, num_results=max_results)
            # Convert Result objects to dictionaries
            return [r.__dict__ for r in response.results]
        except Exception as e:
            print(f"Error searching Exa: {e}")
            return []