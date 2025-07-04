from tools.tavily_search import TavilySearchTool

class ResearcherAgent:
    def __init__(self):
        self.search_tool = TavilySearchTool()

    def handle_query(self, query):
        """Perform a web search using Tavily and return the results."""
        return self.search_tool.search(query) 