from agents.researcher import ResearcherAgent
from agents.analyst import AnalystAgent
from agents.writer import WriterAgent

class SupervisorAgent:
    def __init__(self):
        self.system_prompt = (
            "You are the Supervisor, a meticulous project manager. Your job is to coordinate the workflow, "
            "delegate tasks to the right agent, and ensure quality at every step. You never do the research, "
            "analysis, or writing yourself—instead, you guide the team and communicate clearly with the user. "
            "Always keep the process organized and user-friendly."
        )
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()

    def run_workflow(self, user_query, human_validate_callback):
        # Step 1: Delegate to Researcher
        research_results = self.researcher.handle_query(user_query)
        if not human_validate_callback('research', research_results):
            return 'Research not approved by human.'

        # Step 2: Delegate to Analyst
        # For now, assume the analysis is just a summary of research
        analysis_code = f"# Analyze the following research findings:\n{research_results}"
        analysis_results = self.analyst.analyze(analysis_code)
        if not human_validate_callback('analysis', analysis_results):
            return 'Analysis not approved by human.'

        # Step 3: Delegate to Writer
        final_report = self.writer.write_report(research_results, analysis_results)
        return final_report 