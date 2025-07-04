from tools.python_repl import python_repl_tool

class AnalystAgent:
    def __init__(self):
        self.repl_tool = python_repl_tool

    def analyze(self, code):
        """Execute Python code and return the result."""
        return self.repl_tool.run(code) 