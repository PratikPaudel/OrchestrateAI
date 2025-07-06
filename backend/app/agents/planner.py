# File: backend/app/agents/planner.py
import os
import openai
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import time
import random

load_dotenv()

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "429" in str(e):
                delay = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limit hit, waiting {delay:.1f} seconds...")
                time.sleep(delay)
            else:
                raise

# Define the structured output for the plan
class ResearchPlan(BaseModel):
    """A structured research plan with a list of tasks."""
    plan: List[str] = Field(description="A list of concise, actionable research sub-tasks.")
    summary: str = Field(description="A brief summary of the overall research approach.")

class PlannerAgent:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()

    def _openai_plan(self, query):
        prompt = (
            "You are an expert research planner. Your job is to create a clear, "
            "step-by-step research plan based on a user's query. Decompose the query into "
            "3-5 specific, answerable sub-tasks. Provide a brief summary of your plan.\n\n"
            f"Create a research plan for the following query: {query}"
        )
        
        def make_request():
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
        
        response = retry_with_backoff(make_request)
        time.sleep(2)  # Increased delay to respect rate limits
        return response.choices[0].message.content

    def create_plan(self, query: str) -> ResearchPlan:
        plan_text = self._openai_plan(query)
        
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
        
        # Limit to 3-5 tasks maximum
        if len(tasks) > 5:
            tasks = tasks[:5]
        
        # If no tasks found, create a default task
        if not tasks:
            tasks = [f"Research and analyze information about: {query}"]
        
        # If no summary, create a default summary
        if not summary:
            summary = f"Research plan for: {query}"
        
        print(f"Parsed {len(tasks)} tasks from plan")
        return ResearchPlan(plan=tasks, summary=summary)