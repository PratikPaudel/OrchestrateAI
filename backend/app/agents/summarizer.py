# File: backend/app/agents/summarizer.py
import os
import openai
from typing import List
from ..core.rate_limiter import retry_with_adaptive_backoff

class SummarizerAgent:
    def __init__(self):
        # Set up OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()

    def _chunk_text(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    def _openai_summarize(self, query, content):
        prompt = f"Original Query: {query}\n\nSource Text:\n---\n{content}\n---\n\nSummary:"
        
        # Log context size for monitoring
        context_size = len(prompt)
        print(f"Summarizer context size: {context_size} characters (~{context_size//4} tokens)")
        
        def make_request():
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
        
        response = retry_with_adaptive_backoff(make_request)
        return response.choices[0].message.content

    def summarize(self, query: str, content: str) -> str:
        # Truncate content to reasonable size first
        max_content_length = 3000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        # Use OpenAI for summarization
        if len(content) <= 2000:
            return self._openai_summarize(query, content)
        else:
            # For longer content, chunk and summarize
            chunks = self._chunk_text(content)
            chunk_summaries = []
            for idx, chunk in enumerate(chunks):
                chunk_summary = self._openai_summarize(query, chunk)
                chunk_summaries.append(chunk_summary)
            
            # Return the combined summaries without double processing
            return "\n".join(chunk_summaries)