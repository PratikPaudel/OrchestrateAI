# File: backend/app/agents/writer.py
import os
from typing import List, Dict
from ..core.multi_llm import multi_llm_client

class WriterAgent:
    def __init__(self):
        # Use multi-LLM client
        self.multi_llm = multi_llm_client
        
        self.system_prompt = (
            "You are an expert research report writer. Your goal is to synthesize the provided "
            "research findings into a clear, well-structured, and comprehensive report. "
            "Use Markdown for formatting. Only use the information provided in the research data. "
            "Do not add any external knowledge. Ensure the report directly addresses the original user query."
        )
    
    def _write_report_with_multi_llm(self, query: str, research_data_str: str):
        """Write report using multi-LLM with fallback."""
        print(f"Writing final report...")
        
        prompt = f"{self.system_prompt}\n\nOriginal Query: {query}\n\nResearch Data:\n---\n{research_data_str}\n---\n\nFinal Report:"
        
        # Log context size for monitoring
        context_size = len(prompt)
        print(f"Writer context size: {context_size} characters (~{context_size//4} tokens)")
        
        return self.multi_llm.generate_with_fallback(prompt, max_tokens=800)
    
    def write_report(self, query: str, research_data_str: str) -> str:
        """
        Generates the final research report.
        
        Args:
            query: The original user query.
            research_data_str: Research data in string format.
            
        Returns:
            A string containing the final report in Markdown format.
        """
        return self._write_report_with_multi_llm(query, research_data_str)