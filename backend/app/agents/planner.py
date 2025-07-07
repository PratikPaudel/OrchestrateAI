# File: backend/app/agents/planner.py
import os
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from ..core.multi_llm import multi_llm_client

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
        prompt = (
            "You are an expert research planner. Your job is to create a clear, "
            "step-by-step research plan based on a user's query. Decompose the query into "
            "2-3 specific, answerable sub-tasks. Provide a brief summary of your plan.\n\n"
            f"Create a research plan for the following query: {query}"
        )
        
        return self.multi_llm.generate_with_fallback(prompt, max_tokens=800)

    def create_plan(self, query: str) -> ResearchPlan:
        plan_text = self._multi_llm_plan(query)
        
        # Parse plan_text into ResearchPlan with better parsing logic
        lines = [line.strip() for line in plan_text.split("\n") if line.strip()]
        
        # Extract tasks - look for numbered items, bullet points, or task-like content
        tasks = []
        summary = ""
        
        for line in lines:
            # Skip empty lines
            if not line:
                continue
                
            # Check if line looks like a task (numbered, bulleted, or contains action words)
            is_task = (
                (line[0].isdigit() and len(line) > 3) or  # Numbered items with content
                line.startswith("- ") or  # Bullet points
                line.startswith("* ") or  # Asterisk bullets
                (any(word in line.lower() for word in ["research", "find", "analyze", "examine", "investigate", "explore", "study", "look into", "search for"]) and len(line) > 10)
            )
            
            if is_task:
                # Clean up the task text
                task_text = line
                if line[0].isdigit() and ". " in line:
                    task_text = line.split(". ", 1)[1]  # Remove numbering
                elif line.startswith("- "):
                    task_text = line[2:]  # Remove bullet
                elif line.startswith("* "):
                    task_text = line[2:]  # Remove asterisk
                
                if task_text.strip() and len(task_text.strip()) > 5:
                    tasks.append(task_text.strip())
            elif not summary and not tasks and len(line) > 10:
                # First non-task line becomes the summary
                summary = line
        
        # Limit to 2-3 tasks maximum for faster execution
        if len(tasks) > 3:
            tasks = tasks[:3]
        
        # If no tasks found, create a default task
        if not tasks:
            tasks = [f"Research and analyze information about: {query}"]
        
        # If no summary, create a default summary
        if not summary:
            summary = f"Research plan for: {query}"
        
        print(f"Parsed {len(tasks)} tasks from plan")
        return ResearchPlan(plan=tasks, summary=summary)