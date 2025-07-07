# File: backend/app/core/rate_limiter.py
import time
import random
import threading
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that learns from rate limit responses
    and adjusts delays accordingly to minimize wait times.
    """
    
    def __init__(self, initial_rps: float = 3.0, min_delay: float = 0.5, max_delay: float = 10.0):
        self.rps = initial_rps  # requests per second
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.current_delay = 1.0 / self.rps
        self.last_request_time = 0
        self.rate_limit_count = 0
        self.success_count = 0
        self.lock = threading.Lock()
        
        # Adaptive parameters
        self.backoff_multiplier = 1.5
        self.recovery_multiplier = 0.9
        self.stability_threshold = 10  # consecutive successes before reducing delay
        
    def wait_if_needed(self):
        """Wait if necessary to respect rate limits."""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_request_time
            
            if time_since_last < self.current_delay:
                sleep_time = self.current_delay - time_since_last
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
    
    def on_rate_limit(self):
        """Called when a rate limit is hit - increase delay."""
        with self.lock:
            self.rate_limit_count += 1
            self.success_count = 0  # Reset success count
            
            # Increase delay with backoff
            self.current_delay = min(
                self.current_delay * self.backoff_multiplier,
                self.max_delay
            )
            
            logger.info(f"Rate limit hit. New delay: {self.current_delay:.2f}s")
    
    def on_success(self):
        """Called when a request succeeds - potentially reduce delay."""
        with self.lock:
            self.success_count += 1
            self.rate_limit_count = max(0, self.rate_limit_count - 1)
            
            # If we've had many consecutive successes and no recent rate limits,
            # gradually reduce the delay
            if (self.success_count >= self.stability_threshold and 
                self.rate_limit_count == 0 and 
                self.current_delay > self.min_delay):
                
                self.current_delay = max(
                    self.current_delay * self.recovery_multiplier,
                    self.min_delay
                )
                self.success_count = 0  # Reset for next cycle
                
                logger.info(f"Stable performance. Reduced delay to: {self.current_delay:.2f}s")
    
    def get_stats(self):
        """Get current rate limiter statistics."""
        with self.lock:
            return {
                "current_delay": self.current_delay,
                "rate_limit_count": self.rate_limit_count,
                "success_count": self.success_count,
                "effective_rps": 1.0 / self.current_delay
            }

# Global rate limiter instance
rate_limiter = AdaptiveRateLimiter()

def retry_with_adaptive_backoff(func, max_retries=3, base_delay=1.0):
    """
    Enhanced retry function with adaptive backoff based on rate limiter state.
    """
    for attempt in range(max_retries):
        try:
            # Wait for rate limiter before making request
            rate_limiter.wait_if_needed()
            
            result = func()
            
            # Mark success
            rate_limiter.on_success()
            
            return result
            
        except Exception as e:
            if "429" in str(e):
                # Mark rate limit hit
                rate_limiter.on_rate_limit()
                
                # Calculate adaptive delay
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Rate limit hit, waiting {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                
                if attempt == max_retries - 1:
                    raise Exception(f"Max retries ({max_retries}) exceeded due to rate limiting")
            else:
                # For non-rate-limit errors, still wait a bit but don't adjust rate limiter
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Request failed, waiting {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                
                if attempt == max_retries - 1:
                    raise e 