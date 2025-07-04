from tools.tavily_search import TavilySearchTool

class ResearcherAgent:
    def __init__(self):
        self.system_prompt = (
            "You are the Researcher, a curious and resourceful AI. Your mission is to find the most relevant, "
            "up-to-date, and credible information from the web. Summarize findings clearly, cite sources, and avoid "
            "speculation. You do not analyze or interpret—just gather and present the facts."
        )
        self.search_tool = TavilySearchTool()

    def handle_query(self, query):
        """Perform a web search using Tavily and return the results."""
        return self.search_tool.search(query) 