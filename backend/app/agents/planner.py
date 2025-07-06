# File: backend/app/agents/planner.py
import os
from langchain_groq import ChatGroq
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
import time
import random

load_dotenv()

# Define the structured output for the plan
class ResearchPlan(BaseModel):
    """A structured research plan with a list of tasks."""
    plan: List[str] = Field(description="A list of concise, actionable research sub-tasks.")
    summary: str = Field(description="A brief summary of the overall research approach.")

class PlannerAgent:
    def __init__(self):
        self.groq_llm = ChatGroq(
            model_name="llama3-70b-8192",
            api_key=os.getenv("GROQ_API_KEY")
        )
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.gemini_model = genai.GenerativeModel("gemini-pro")

    def _groq_plan(self, query):
        system_prompt = (
            "You are an expert research planner. Your job is to create a clear, "
            "step-by-step research plan based on a user's query. Decompose the query into "
            "3-5 specific, answerable sub-tasks. Provide a brief summary of your plan."
        )
        prompt = f"{system_prompt}\n\nCreate a research plan for the following query: {query}"
        return self.groq_llm.invoke({"query": query, "content": prompt}).content

    def _gemini_plan(self, query):
        prompt = (
            "You are an expert research planner. Your job is to create a clear, "
            "step-by-step research plan based on a user's query. Decompose the query into "
            "3-5 specific, answerable sub-tasks. Provide a brief summary of your plan.\n\n"
            f"Create a research plan for the following query: {query}"
        )
        response = self.gemini_model.generate_content(prompt)
        return response.text

    def create_plan(self, query: str) -> ResearchPlan:
        try:
            plan_text = self._groq_plan(query)
        except Exception as e:
            print(f"Groq failed, falling back to Gemini: {e}")
            plan_text = self._gemini_plan(query)
        # Parse plan_text into ResearchPlan (simple parsing for now)
        lines = [line.strip() for line in plan_text.split("\n") if line.strip()]
        numbered = [line for line in lines if line[0].isdigit() or line.startswith("-")]
        summary = lines[0] if lines else ""
        return ResearchPlan(plan=numbered, summary=summary)