#!/usr/bin/env python3
"""
Test script for multi-LLM system with Groq, OpenAI, and Gemini.
"""

import os
import time
import logging
from dotenv import load_dotenv
from app.core.multi_llm import multi_llm_client

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_multi_llm():
    """Test the multi-LLM system with all available providers."""
    
    print("🚀 Testing Multi-LLM System")
    print("=" * 50)
    
    # Check available providers
    stats = multi_llm_client.get_stats()
    print(f"Available providers: {stats['available_providers']}")
    print(f"Total providers: {stats['total_providers']}")
    
    if stats['total_providers'] == 0:
        print("❌ No providers available. Please set API keys for at least one provider:")
        print("   - GROQ_API_KEY")
        print("   - OPENAI_API_KEY") 
        print("   - GEMINI_API_KEY")
        return
    
    # Test prompt
    test_prompt = "Summarize the key benefits of renewable energy in 2-3 sentences."
    
    print(f"\n📝 Test prompt: {test_prompt}")
    print("-" * 50)
    
    try:
        # Test generation
        start_time = time.time()
        result = multi_llm_client.generate_with_fallback(test_prompt, max_tokens=100)
        elapsed = time.time() - start_time
        
        print(f"✅ Generation successful in {elapsed:.2f}s")
        print(f"📄 Result: {result}")
        
        # Show final stats
        final_stats = multi_llm_client.get_stats()
        print(f"\n📊 Final Stats:")
        for provider, stats in final_stats['providers'].items():
            print(f"   {provider}:")
            print(f"     - Success: {stats['success_count']}")
            print(f"     - Errors: {stats['error_count']}")
            if stats['last_error']:
                print(f"     - Last error: {stats['last_error']}")
        
        # Show best provider
        best_provider = multi_llm_client.get_best_provider()
        if best_provider:
            print(f"\n🏆 Best performing provider: {best_provider}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_provider_fallback():
    """Test fallback behavior when some providers fail."""
    
    print("\n🔄 Testing Provider Fallback")
    print("=" * 50)
    
    # Test multiple generations to see fallback in action
    prompts = [
        "What is artificial intelligence?",
        "Explain machine learning briefly.",
        "What are the benefits of cloud computing?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Test {i}: {prompt}")
        try:
            result = multi_llm_client.generate_with_fallback(prompt, max_tokens=50)
            print(f"✅ Result: {result[:100]}...")
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        # Small delay between requests
        time.sleep(1)

if __name__ == "__main__":
    test_multi_llm()
    test_provider_fallback() 