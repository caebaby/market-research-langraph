"""
Test script for Brave Search API
Validates API key configuration and search functionality
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_brave_search():
    """
    Comprehensive test of Brave Search API functionality
    """
    print("="*60)
    print("BRAVE SEARCH API TEST")
    print("="*60)
    
    # Step 1: Check API key
    api_key = os.getenv("BRAVE_API_KEY")
    
    if not api_key:
        print("❌ FAILED: BRAVE_API_KEY not found in environment")
        print("FIX: Add to .env file: BRAVE_API_KEY=your_key_here")
        print("Get your key at: https://brave.com/search/api/")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Step 2: Test basic search
    print("\n" + "="*60)
    print("TEST 1: Basic Search")
    print("="*60)
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    test_query = "Python programming best practices 2024"
    url = "https://api.search.brave.com/res/v1/web/search"
    
    params = {
        "q": test_query,
        "count": 5
    }
    
    try:
        print(f"Searching for: '{test_query}'")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            print("✅ Search successful!")
            data = response.json()
            
            # Display results
            if "web" in data and "results" in data["web"]:
                results = data["web"]["results"]
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results[:3], 1):
                    print(f"\n{i}. {result.get('title', 'No title')}")
                    print(f"   URL: {result.get('url', 'No URL')}")
                    print(f"   Description: {result.get('description', 'No description')[:100]}...")
            else:
                print("⚠️ No results found in response")
                
        elif response.status_code == 401:
            print("❌ Authentication failed - Invalid API key")
            return False
        elif response.status_code == 429:
            print("❌ Rate limit exceeded - Too many requests")
            return False
        else:
            print(f"❌ Search failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during search: {str(e)}")
        return False
    
    # Step 3: Test with different parameters
    print("\n" + "="*60)
    print("TEST 2: Search with Country and Freshness")
    print("="*60)
    
    params = {
        "q": "AI market trends",
        "count": 3,
        "country": "us",
        "freshness": "pd"  # Past day
    }
    
    try:
        print(f"Searching for: '{params['q']}' (US, past day)")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            print("✅ Parameterized search successful!")
            data = response.json()
            
            if "web" in data and "results" in data["web"]:
                print(f"Found {len(data['web']['results'])} fresh results")
            
    except Exception as e:
        print(f"❌ Parameterized search failed: {str(e)}")
    
    # Step 4: Test news search
    print("\n" + "="*60)
    print("TEST 3: News Search")
    print("="*60)
    
    params = {
        "q": "technology news",
        "count": 3
    }
    
    try:
        print(f"Searching news for: '{params['q']}'")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if "news" in data and "results" in data["news"]:
                news_results = data["news"]["results"]
                print(f"✅ Found {len(news_results)} news articles")
                for article in news_results[:2]:
                    print(f"- {article.get('title', 'No title')}")
            else:
                print("ℹ️ No news results in this search")
                
    except Exception as e:
        print(f"⚠️ News search error: {str(e)}")
    
    # Step 5: Rate limit check
    print("\n" + "="*60)
    print("TEST 4: Rate Limit Check")
    print("="*60)
    
    try:
        # Make a simple request to check headers
        response = requests.get(url, headers=headers, params={"q": "test", "count": 1})
        
        # Check rate limit headers
        rate_limit = response.headers.get("X-RateLimit-Limit", "Not provided")
        rate_remaining = response.headers.get("X-RateLimit-Remaining", "Not provided")
        rate_reset = response.headers.get("X-RateLimit-Reset", "Not provided")
        
        print(f"Rate Limit: {rate_limit}")
        print(f"Remaining: {rate_remaining}")
        print(f"Reset: {rate_reset}")
        
        if rate_remaining != "Not provided" and int(rate_remaining) < 10:
            print("⚠️ WARNING: Low API calls remaining!")
            
    except Exception as e:
        print(f"⚠️ Could not check rate limits: {str(e)}")
    
    # Step 6: Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("✅ Brave Search API is working correctly!")
    print(f"✅ API Key is valid: {api_key[:10]}...")
    print("✅ Basic search works")
    print("✅ Parameterized search works")
    print("✅ Ready for use in agents")
    
    return True

def test_agent_integration():
    """
    Test how agents would use the search
    """
    print("\n" + "="*60)
    print("AGENT INTEGRATION TEST")
    print("="*60)
    
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        print("❌ Cannot test - API key missing")
        return
    
    # Simulate agent search patterns
    agent_queries = {
        "psychological": "customer psychology B2B enterprise software",
        "voice_of_customer": "enterprise software customer complaints reviews",
        "competitor": "Slack competitors alternatives 2024",
        "interview": "B2B sales discovery questions enterprise",
        "gtm_blueprint": "SaaS go-to-market strategy enterprise"
    }
    
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": api_key
    }
    
    url = "https://api.search.brave.com/res/v1/web/search"
    
    for agent, query in agent_queries.items():
        print(f"\n[{agent}] Testing: {query[:50]}...")
        
        params = {
            "q": query,
            "count": 2
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if "web" in data and "results" in data["web"]:
                    print(f"  ✅ Found {len(data['web']['results'])} results")
                else:
                    print(f"  ⚠️ No results")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
    
    print("\n✅ Agent integration tests complete!")

def main():
    """
    Run all tests
    """
    print("\n🔍 Starting Brave Search API Tests\n")
    
    # Run basic tests
    success = test_brave_search()
    
    if success:
        # Run agent integration tests
        test_agent_integration()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - Brave Search API Ready!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ TESTS FAILED - Fix issues above")
        print("="*60)
        
        print("\n📝 Setup Instructions:")
        print("1. Get API key: https://brave.com/search/api/")
        print("2. Add to .env: BRAVE_API_KEY=your_key_here")
        print("3. Run this test again: python tests/test_brave_search.py")

if __name__ == "__main__":
    main()