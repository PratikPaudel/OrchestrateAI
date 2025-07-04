from tools.python_repl import python_repl_tool

class AnalystAgent:
    def __init__(self):
        self.system_prompt = (
            "You are the Analyst, a data-driven problem solver. Your job is to process the research data, extract "
            "insights, and perform calculations or visualizations as needed. Be logical, precise, and explain your "
            "reasoning. Do not gather new data or write the final report—focus on analysis only."
        )
        self.repl_tool = python_repl_tool

    def analyze(self, code):
        """Execute Python code and return the result."""
        return self.repl_tool.run(code) 