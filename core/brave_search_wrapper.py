# core/brave_search_wrapper.py
"""
Custom Brave Search Wrapper using requests
Avoids httpx dependency conflicts
"""

import os
import json
from typing import List, Dict, Any, Optional
import requests


class CustomBraveSearch:
    """
    Custom wrapper for Brave Search API using requests.
    
    WHY: Avoid dependency conflicts with httpx
    HOW: Direct API calls using requests library
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Brave search with API key."""
        self.api_key = api_key or os.getenv('BRAVE_API_KEY')
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.enabled = False
        
        if self.api_key:
            self.enabled = True
            print("✅ Brave search client initialized (using requests)")
        else:
            print("⚠️ No Brave API key found")
    
    def search(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search using Brave API with requests.
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.enabled:
            return self._mock_search(query)
        
        try:
            # Set up headers and parameters
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": count
            }
            
            # Make the API request
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"   ⚠️ Brave API error: {response.status_code}")
                return self._mock_search(query)
            
            # Parse the response
            data = response.json()
            
            # Format results
            formatted_results = []
            
            # Extract web results
            web_results = data.get('web', {}).get('results', [])
            
            for result in web_results[:count]:
                formatted_results.append({
                    'content': f"{result.get('title', '')}. {result.get('description', '')}",
                    'source': result.get('url', 'Brave Search'),
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'description': result.get('description', '')
                })
            
            # Add news results if available
            news_results = data.get('news', {}).get('results', [])
            for result in news_results[:max(0, count - len(formatted_results))]:
                formatted_results.append({
                    'content': f"[News] {result.get('title', '')}. {result.get('description', '')}",
                    'source': result.get('url', 'Brave News'),
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'description': result.get('description', '')
                })
            
            if not formatted_results:
                print(f"   ⚠️ No results found for: {query}")
                return self._mock_search(query)
            
            print(f"   ✅ Found {len(formatted_results)} results for: {query[:30]}...")
            return formatted_results
            
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Request failed: {e}")
            return self._mock_search(query)
        except json.JSONDecodeError as e:
            print(f"   ⚠️ Failed to parse response: {e}")
            return self._mock_search(query)
        except Exception as e:
            print(f"   ⚠️ Search failed: {e}")
            return self._mock_search(query)
    
    def _mock_search(self, query: str) -> List[Dict[str, Any]]:
        """Provide mock search results as fallback."""
        print(f"   ℹ️ Using mock results for: {query[:30]}...")
        return [
            {
                'content': f"Industry analysis for {query}: Market trends show significant growth in AI adoption",
                'source': 'Mock Search',
                'title': f'Analysis: {query}',
                'url': 'https://example.com/1',
                'description': 'Industry insights and analysis'
            },
            {
                'content': f"Market research on {query}: Competitive landscape evolving rapidly",
                'source': 'Mock Search',
                'title': f'Market Research: {query}',
                'url': 'https://example.com/2',
                'description': 'Market trends and data'
            },
            {
                'content': f"Customer insights for {query}: Users prioritize efficiency and reliability",
                'source': 'Mock Search',
                'title': f'Customer Study: {query}',
                'url': 'https://example.com/3',
                'description': 'Customer behavior analysis'
            }
        ]
    
    def run(self, query: str) -> str:
        """
        Compatibility method for langchain-style interface.
        
        Args:
            query: Search query
            
        Returns:
            String representation of results
        """
        results = self.search(query)
        return "\n".join([r['content'] for r in results])


# Wrapper class for drop-in replacement
class BraveSearchResults:
    """Drop-in replacement for langchain BraveSearchResults."""
    
    def __init__(self, api_wrapper=None, max_results=5, **kwargs):
        """Initialize with compatibility parameters."""
        self.max_results = max_results
        api_key = None
        
        # Extract API key from wrapper if provided
        if api_wrapper and hasattr(api_wrapper, 'api_key'):
            api_key = api_wrapper.api_key
        
        self.search_client = CustomBraveSearch(api_key=api_key)
    
    def run(self, query: str) -> str:
        """Run search and return string results."""
        return self.search_client.run(query)
    
    def search(self, query: str) -> List[Dict]:
        """Run search and return structured results."""
        return self.search_client.search(query, self.max_results)


class BraveSearchWrapper:
    """Drop-in replacement for langchain BraveSearchWrapper."""
    
    def __init__(self, api_key: str = None, search_kwargs: Dict = None, **kwargs):
        """Initialize with compatibility parameters."""
        self.api_key = api_key or os.getenv('BRAVE_API_KEY')
        self.search_kwargs = search_kwargs or {'count': 5}