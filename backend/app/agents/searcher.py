# File: backend/app/agents/searcher.py

import os
from exa_py import Exa
from typing import List, Dict

class SearcherAgent:
    def __init__(self):
        self.client = Exa(api_key=os.getenv("EXA_API_KEY"))

    def search(self, query: str, max_results: int = 1) -> List[Dict]:
        """
        Performs a web search using the Exa API.
        
        Args:
            query: The search query, typically a sub-task from the Planner.
            max_results: The maximum number of search results to return.
            
        Returns:
            A list of search result dictionaries, each containing 'url', 'title', and 'content'.
        """
        try:
            # search_and_contents returns both metadata and cleaned HTML content
            response = self.client.search_and_contents(
                query,
                num_results=max_results,
                text=True, # Ensure text content is returned
            )
            # Convert the Result objects into a simpler dictionary format
            return [
                {"url": r.url, "title": r.title, "content": r.text}
                for r in response.results
            ]
        except Exception as e:
            print(f"An error occurred during search: {e}")
            return []