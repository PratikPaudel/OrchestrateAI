# File: backend/app/agents/writer.py
import os
import openai
from typing import List, Dict
from ..core.rate_limiter import retry_with_adaptive_backoff

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
        
        # Log context size for monitoring
        context_size = len(prompt)
        print(f"Writer context size: {context_size} characters (~{context_size//4} tokens)")
        
        def make_request():
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
        
        response = retry_with_adaptive_backoff(make_request)
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
        # Limit to top 1 source and truncate content
        limited_data = research_data[-1:] if len(research_data) > 1 else research_data
        
        # Truncate summaries and reviews if too long
        for item in limited_data:
            if len(item['summary']) > 300:
                item['summary'] = item['summary'][:300] + "..."
            if len(item['review']) > 200:
                item['review'] = item['review'][:200] + "..."
        
        # Format the research data into a readable string for the prompt
        research_data_str = "\n\n".join([
            f"Source URL: {d['url']}\nSummary: {d['summary']}\nReview: {d['review']}"
            for d in limited_data
        ])
        
        return self._write_report_with_retry(query, research_data_str)