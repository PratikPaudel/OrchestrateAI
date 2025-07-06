# File: backend/app/agents/writer.py
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from typing import List, Dict
import time
import random

class WriterAgent:
    def __init__(self):
        # Use powerful model for final report writing
        self.llm = ChatGroq(
            model_name="llama3-70b-8192",  # Keep powerful model for final output
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        system_prompt = (
            "You are an expert research report writer. Your goal is to synthesize the provided "
            "research findings into a clear, well-structured, and comprehensive report. "
            "Use Markdown for formatting. Only use the information provided in the research data. "
            "Do not add any external knowledge. Ensure the report directly addresses the original user query."
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Original Query: {query}\n\nResearch Data:\n---\n{research_data}\n---\n\nFinal Report:")
        ])
        
        self.chain = self.prompt | self.llm
    
    def _write_report_with_retry(self, query: str, research_data_str: str, max_attempts=5, base_wait=60, max_wait=300):
        """Write report with retry logic for rate limiting."""
        attempt = 0
        while attempt < max_attempts:
            try:
                # Add delay before API call
                if attempt > 0:
                    time.sleep(5)  # 5 second delay between retries
                else:
                    time.sleep(2)  # 2 second delay for first attempt
                
                print(f"Writing final report (attempt {attempt + 1}/{max_attempts})...")
                return self.chain.invoke({
                    "query": query,
                    "research_data": research_data_str
                }).content
                
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower():
                    wait_time = min(base_wait * (2 ** attempt), max_wait)
                    wait_time = wait_time + random.uniform(0, 10)  # Add jitter
                    print(f"Rate limit hit in writer. Waiting {wait_time:.1f} seconds before retrying...")
                    time.sleep(wait_time)
                    attempt += 1
                else:
                    print(f"Non-rate-limit error in writer: {e}")
                    raise
        
        raise Exception("Max retry attempts reached for writing report.")
    
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