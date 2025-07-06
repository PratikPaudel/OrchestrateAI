# File: backend/app/agents/writer.py
import os
import openai
from typing import List, Dict
import time
import random

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

class WriterAgent:
    def __init__(self):
        # Use OpenAI for final report writing
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()
        
        self.system_prompt = (
            "You are an expert research report writer. Your goal is to synthesize the provided "
            "research findings into a clear, well-structured, and comprehensive report. "
            "Use Markdown for formatting. Only use the information provided in the research data. "
            "Do not add any external knowledge. Ensure the report directly addresses the original user query."
        )
    
    def _write_report_with_retry(self, query: str, research_data_str: str, max_attempts=3):
        """Write report with retry logic."""
        print(f"Writing final report...")
        
        prompt = f"{self.system_prompt}\n\nOriginal Query: {query}\n\nResearch Data:\n---\n{research_data_str}\n---\n\nFinal Report:"
        
        def make_request():
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
        
        response = retry_with_backoff(make_request)
        time.sleep(2)  # Increased delay to respect rate limits
        return response.choices[0].message.content
    
    def write_report(self, query: str, research_data: List[Dict]) -> str:
        """
        Generates the final research report.
        
        Args:
            query: The original user query.
            research_data: A list of dictionaries, each containing a summary and its review.
            
        Returns:
            A string containing the final report in Markdown format.
        """
        # Format the research data into a readable string for the prompt
        research_data_str = "\n\n".join([
            f"Source URL: {d['url']}\nSummary: {d['summary']}\nReview: {d['review']}"
            for d in research_data
        ])
        
        return self._write_report_with_retry(query, research_data_str)