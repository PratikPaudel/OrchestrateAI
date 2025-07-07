# File: backend/app/core/multi_llm.py
import os
import time
import random
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
import openai
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get provider name."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.model = "gpt-3.5-turbo"
        
        # Only initialize client if API key is available
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        if not self.client:
            raise Exception("OpenAI client not initialized - no API key available")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            raise
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.client)
    
    def get_name(self) -> str:
        return "OpenAI"

class GroqProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        self.model = "llama3-8b-8192"  # Fast model
        
        # Only initialize client if API key is available
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
                self.client = None
    
    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        if not self.client:
            raise Exception("Groq client not initialized - no API key available")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq error: {e}")
            raise
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.client)
    
    def get_name(self) -> str:
        return "Groq"

class GeminiProvider(LLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        
        # Only initialize client if API key is available
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.model = None
    
    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        if not self.model:
            raise Exception("Gemini client not initialized - no API key available")
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.model)
    
    def get_name(self) -> str:
        return "Gemini"

class MultiLLMClient:
    """Multi-provider LLM client with automatic fallback."""
    
    def __init__(self):
        self.providers: List[LLMProvider] = []
        self.provider_stats: Dict[str, Dict[str, Any]] = {}
        
        # Initialize available providers
        self._init_providers()
        
        # Rate limiting per provider
        self.last_request_time: Dict[str, float] = {}
        self.min_request_interval = 0.5  # Minimum seconds between requests per provider
    
    def _init_providers(self):
        """Initialize available providers in order of preference."""
        providers_to_try = [
            GroqProvider(),      # Fastest, good for summarization
            OpenAIProvider(),    # Reliable fallback
            GeminiProvider()     # Alternative option
        ]
        
        available_keys = []
        for provider in providers_to_try:
            try:
                if provider.is_available():
                    self.providers.append(provider)
                    self.provider_stats[provider.get_name()] = {
                        "success_count": 0,
                        "error_count": 0,
                        "last_error": None,
                        "last_success": None
                    }
                    logger.info(f"✅ Initialized {provider.get_name()} provider")
                else:
                    logger.warning(f"❌ {provider.get_name()} provider not available - missing or invalid API key")
            except Exception as e:
                logger.error(f"❌ Failed to initialize {provider.get_name()} provider: {e}")
        
        if not self.providers:
            # Check which API keys are missing
            if not os.getenv("GROQ_API_KEY"):
                available_keys.append("GROQ_API_KEY")
            if not os.getenv("OPENAI_API_KEY"):
                available_keys.append("OPENAI_API_KEY")
            if not os.getenv("GEMINI_API_KEY"):
                available_keys.append("GEMINI_API_KEY")
            
            error_msg = f"No LLM providers available. Please set at least one API key in your .env file: {', '.join(available_keys)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info(f"🚀 Available providers: {[p.get_name() for p in self.providers]}")
    
    def _rate_limit_provider(self, provider_name: str):
        """Ensure minimum interval between requests to same provider."""
        now = time.time()
        last_time = self.last_request_time.get(provider_name, 0)
        
        if now - last_time < self.min_request_interval:
            sleep_time = self.min_request_interval - (now - last_time)
            time.sleep(sleep_time)
        
        self.last_request_time[provider_name] = time.time()
    
    def generate_with_fallback(self, prompt: str, max_tokens: int = 300) -> str:
        """Generate text using available providers with automatic fallback."""
        
        # Log context size for monitoring
        context_size = len(prompt)
        logger.info(f"MultiLLM context size: {context_size} characters (~{context_size//4} tokens)")
        
        # Try each provider in order
        for provider in self.providers:
            provider_name = provider.get_name()
            
            try:
                # Rate limit this provider
                self._rate_limit_provider(provider_name)
                
                logger.info(f"Trying {provider_name} for generation...")
                start_time = time.time()
                
                result = provider.generate(prompt, max_tokens)
                
                # Update stats
                self.provider_stats[provider_name]["success_count"] += 1
                self.provider_stats[provider_name]["last_success"] = time.time()
                
                elapsed = time.time() - start_time
                logger.info(f"✅ {provider_name} succeeded in {elapsed:.2f}s")
                
                return result
                
            except Exception as e:
                # Update error stats
                self.provider_stats[provider_name]["error_count"] += 1
                self.provider_stats[provider_name]["last_error"] = str(e)
                
                logger.warning(f"❌ {provider_name} failed: {e}")
                
                # If it's a rate limit, add extra delay
                if "429" in str(e) or "rate limit" in str(e).lower():
                    delay = random.uniform(2, 5)
                    logger.info(f"Rate limit hit on {provider_name}, waiting {delay:.1f}s")
                    time.sleep(delay)
                
                continue
        
        # If all providers failed
        error_msg = f"All providers failed. Last errors: {[stats['last_error'] for stats in self.provider_stats.values()]}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics."""
        return {
            "providers": self.provider_stats,
            "total_providers": len(self.providers),
            "available_providers": [p.get_name() for p in self.providers]
        }
    
    def get_best_provider(self) -> Optional[str]:
        """Get the provider with the best success rate."""
        if not self.provider_stats:
            return None
        
        best_provider = None
        best_ratio = -1
        
        for name, stats in self.provider_stats.items():
            total_requests = stats["success_count"] + stats["error_count"]
            if total_requests > 0:
                success_ratio = stats["success_count"] / total_requests
                if success_ratio > best_ratio:
                    best_ratio = success_ratio
                    best_provider = name
        
        return best_provider

# Global instance
multi_llm_client = MultiLLMClient() 