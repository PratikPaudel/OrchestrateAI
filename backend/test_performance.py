#!/usr/bin/env python3
"""
Performance test script for OrchestrateAI with adaptive rate limiting.
"""

import time
import logging
from app.core.graph import execute_research
from app.core.rate_limiter import rate_limiter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_performance():
    """Test the performance of the research system."""
    
    # Test query
    query = "What are the top 3 AI startups in San Francisco in 2024?"
    
    print("🚀 Starting performance test...")
    print(f"Query: {query}")
    print("-" * 50)
    
    # Get initial rate limiter stats
    initial_stats = rate_limiter.get_stats()
    print(f"Initial rate limiter stats: {initial_stats}")
    
    # Start timing
    start_time = time.time()
    
    try:
        # Execute research
        result = execute_research(query)
        
        # End timing
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Get final stats
        final_stats = rate_limiter.get_stats()
        
        print("-" * 50)
        print("📊 PERFORMANCE RESULTS:")
        print(f"Total execution time: {execution_time:.2f} seconds")
        print(f"Final rate limiter stats: {final_stats}")
        
        if "error" in result:
            print(f"❌ Error occurred: {result['error']}")
        else:
            print("✅ Research completed successfully!")
            print(f"Report length: {len(result.get('final_report', ''))} characters")
            
            # Show a preview of the report
            report = result.get('final_report', '')
            if report:
                print("\n📄 Report Preview:")
                print(report[:500] + "..." if len(report) > 500 else report)
        
    except Exception as e:
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"❌ Test failed after {execution_time:.2f} seconds: {e}")

if __name__ == "__main__":
    test_performance() 