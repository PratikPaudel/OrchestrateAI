# File: backend/app/agents/planner.py
import os
from pydantic import BaseModel, Field
from typing import List
import re
from dotenv import load_dotenv
from ..core.multi_llm import multi_llm_client
import logging

logger = logging.getLogger("orchestrateai.agent.planner")

load_dotenv()

# Define the structured output for the plan
class ResearchPlan(BaseModel):
    """A structured research plan with a list of tasks."""
    plan: List[str] = Field(description="A list of concise, actionable research sub-tasks.")
    summary: str = Field(description="A brief summary of the overall research approach.")

class PlannerAgent:
    def __init__(self):
        self.multi_llm = multi_llm_client

    def _multi_llm_plan(self, query):
        # --- FIX: Improved prompt with clear delimiters ---
        prompt = (
            "You are an expert research planner. Your job is to create a clear, "
            "step-by-step research plan for the given query. Decompose the query into "
            "2-3 specific, answerable sub-tasks. Provide a brief summary of your plan.\n\n"
            "Respond using the following format, and do not include any other text or conversational preamble:\n"
            "[SUMMARY]\n"
            "Your brief summary of the research approach.\n"
            "[/SUMMARY]\n"
            "[TASKS]\n"
            "1. First specific sub-task.\n"
            "2. Second specific sub-task.\n"
            "3. Third specific sub-task.\n"
            "[/TASKS]\n\n"
            f"Create a research plan for the following query: {query}"
        )
        
        return self.multi_llm.generate_with_fallback(prompt, max_tokens=800)

    def create_plan(self, query: str) -> ResearchPlan:
        plan_text = self._multi_llm_plan(query)
        
        # --- FIX: More robust parsing logic based on the new prompt format ---
        tasks = []
        summary = "No summary generated."

        try:
            # Extract summary
            summary_match = re.search(r"\[SUMMARY\](.*?)\[/SUMMARY\]", plan_text, re.DOTALL)
            if summary_match:
                summary = summary_match.group(1).strip()

            # Extract tasks
            tasks_match = re.search(r"\[TASKS\](.*?)\[/TASKS\]", plan_text, re.DOTALL)
            if tasks_match:
                tasks_block = tasks_match.group(1).strip()
                # Split by newline and filter out empty lines
                raw_tasks = [line.strip() for line in tasks_block.split('\n') if line.strip()]
                # Remove numbering like "1. ", "2. ", etc.
                tasks = [re.sub(r'^\d+\.\s*', '', task) for task in raw_tasks]

        except Exception as e:
            logger.error(f"Failed to parse plan text: {e}. Using fallback.")
            # Fallback for safety, though the new prompt should prevent this
            tasks = [f"Research and analyze information about: {query}"]
            summary = f"Research plan for: {query}"

        # If parsing somehow failed, create a default task
        if not tasks:
            tasks = [f"Research and analyze information about: {query}"]
        
        logger.info(f"Successfully parsed {len(tasks)} tasks from plan.")
        return ResearchPlan(plan=tasks, summary=summary)