# File: backend/app/agents/summarizer.py
import os
from typing import List
from ..core.multi_llm import multi_llm_client

class SummarizerAgent:
    def __init__(self):
        # Use multi-LLM client
        self.multi_llm = multi_llm_client

    def _chunk_text(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    def _multi_llm_summarize(self, query, content):
        prompt = f"Original Query: {query}\n\nSource Text:\n---\n{content}\n---\n\nSummary:"
        
        # Use multi-LLM client with fallback
        return self.multi_llm.generate_with_fallback(prompt, max_tokens=300)

    def summarize(self, query: str, content: str) -> str:
        # Truncate content to reasonable size first
        max_content_length = 3000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        # Use multi-LLM for summarization
        if len(content) <= 2000:
            return self._multi_llm_summarize(query, content)
        else:
            # For longer content, chunk and summarize
            chunks = self._chunk_text(content)
            chunk_summaries = []
            for idx, chunk in enumerate(chunks):
                chunk_summary = self._multi_llm_summarize(query, chunk)
                chunk_summaries.append(chunk_summary)
            
            # Return the combined summaries without double processing
            return "\n".join(chunk_summaries)