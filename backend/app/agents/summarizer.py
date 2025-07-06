# File: backend/app/agents/summarizer.py
import os
import openai
from typing import List
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

class SummarizerAgent:
    def __init__(self):
        # Set up OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.client = openai.OpenAI()

    def _chunk_text(self, text: str, max_chunk_size: int = 4000) -> List[str]:
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    def _openai_summarize(self, query, content):
        prompt = f"Original Query: {query}\n\nSource Text:\n---\n{content}\n---\n\nSummary:"
        
        def make_request():
            return self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
        
        response = retry_with_backoff(make_request)
        time.sleep(2)  # Increased delay to respect rate limits
        return response.choices[0].message.content

    def summarize(self, query: str, content: str) -> str:
        # Use OpenAI for all summarization
        if len(content) <= 8000:
            return self._openai_summarize(query, content)
        else:
            # For very long content, chunk and use OpenAI for better handling
            chunks = self._chunk_text(content)
            chunk_summaries = []
            for idx, chunk in enumerate(chunks):
                chunk_summary = self._openai_summarize(query, chunk)
                chunk_summaries.append(chunk_summary)
            combined = "\n".join(chunk_summaries)
            if len(combined) > 8000:
                return self._openai_summarize(query, combined)
            else:
                return combined