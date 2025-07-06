# File: backend/app/agents/summarizer.py
import os
import random
import time
from langchain_groq import ChatGroq
import google.generativeai as genai
from typing import List

class SummarizerAgent:
    def __init__(self):
        # Set up Groq
        self.groq_llm = ChatGroq(
            model_name="llama3-8b-8192",
            api_key=os.getenv("GROQ_API_KEY")
        )
        # Set up Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.gemini_model = genai.GenerativeModel("gemini-pro")

    def _chunk_text(self, text: str, max_chunk_size: int = 3000) -> List[str]:
        return [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    def _groq_summarize(self, query, content):
        prompt = f"Original Query: {query}\n\nSource Text:\n---\n{content}\n---\n\nSummary:"
        return self.groq_llm.invoke({"query": query, "content": content}).content

    def _gemini_summarize(self, query, content):
        prompt = f"Original Query: {query}\n\nSource Text:\n---\n{content}\n---\n\nSummary:"
        response = self.gemini_model.generate_content(prompt)
        return response.text

    def summarize(self, query: str, content: str) -> str:
        # Use Groq for short texts, Gemini for long, or alternate if rate limited
        try:
            if len(content) <= 3000:
                return self._groq_summarize(query, content)
            else:
                # For long content, chunk and use Gemini for better handling
                chunks = self._chunk_text(content)
                chunk_summaries = []
                for idx, chunk in enumerate(chunks):
                    chunk_summary = self._gemini_summarize(query, chunk)
                    chunk_summaries.append(chunk_summary)
                    time.sleep(2)  # avoid rate limit
                combined = "\n".join(chunk_summaries)
                if len(combined) > 3000:
                    return self._gemini_summarize(query, combined)
                else:
                    return combined
        except Exception as e:
            # If Groq fails, fallback to Gemini
            print(f"Groq failed, falling back to Gemini: {e}")
            return self._gemini_summarize(query, content)