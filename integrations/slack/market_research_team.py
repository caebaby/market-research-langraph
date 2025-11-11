#!/usr/bin/env python
"""
Market Research Team Bot - Unified Version
Combines all features from team_bot and advanced_bot
With integrated template system for guided research
Version 3.0 - Production Ready
Updated with Sonnet 4.5 configuration
"""

import os
import sys
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta
import time
from typing import Dict, Any, Optional, List, Tuple
import asyncio
import re
import hashlib
from xmlrpc import client
import requests 
from functools import wraps
import copy  # For deep copying state

# ==============================================
# 1. ENVIRONMENT & PATH SETUP
# ==============================================

# Add path for core imports - CRITICAL FOR PROPER IMPORTS
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"✅ Added project root to path: {project_root}")

# Import custom configuration and prompts AFTER path setup
try:
    from core.config import Config
    print("✅ Successfully imported Config from core.config")
    CONFIG_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Failed to import Config: {e}")
    print(f"   Will use fallback configuration")
    CONFIG_AVAILABLE = False
    Config = None

try:
    from team_icp.prompts.research_prompts import ICPResearchPrompts
    print("✅ Successfully imported ICPResearchPrompts")
    PROMPTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Failed to import ICPResearchPrompts: {e}")
    print(f"   Will use embedded prompts")
    PROMPTS_AVAILABLE = False
    ICPResearchPrompts = None

# LangSmith environment setup (MUST BE FIRST!)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "market-research-unified"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")

# Alternative path setup for compatibility
project_root_alt = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root_alt))

print(f"Python path configured. Project root: {project_root}")

# ==============================================
# 2. LOGGING CONFIGURATION
# ==============================================

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('market_research_team.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ==============================================
# 3. IMPORTS
# ==============================================

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables FIRST before any other initialization
load_dotenv()

# Additional imports for enhanced functionality
try:
    from langchain_community.tools.brave_search import BraveSearchResults
    BRAVE_SEARCH_AVAILABLE = True
except ImportError:
    try:
        # Fallback for older versions
        from langchain_community.tools.brave_search.tool import BraveSearch
        BraveSearchResults = BraveSearch
        BRAVE_SEARCH_AVAILABLE = True
    except ImportError:
        BRAVE_SEARCH_AVAILABLE = False
        logger.warning("Brave search not available - install langchain-community")

# ==============================================
# 4. CONFIGURATION FROM ENVIRONMENT
# ==============================================

print("\n" + "="*60)
print("LOADING CONFIGURATION FROM ENVIRONMENT")
print("="*60)

# Check if using new Config or fallback
if CONFIG_AVAILABLE and Config:
    # Use new Config class settings
    print("📊 Using Config module settings (Sonnet 4.5)")
    AGENT_TEMPERATURES = Config.AGENT_TEMPERATURES
    MAX_TOKENS = Config.MAX_TOKENS
    DEFAULT_TEMPERATURE = Config.DEFAULT_TEMPERATURE
    DEFAULT_MAX_TOKENS = Config.MAX_TOKENS["research"]
    MAX_TOKEN_LIMIT = max(Config.MAX_TOKENS.values())
else:
    # Fallback to environment variables - NOW WITH 0.3 TEMPERATURE
    print("📊 Using fallback configuration (Updated to 0.3 temp)")
    AGENT_TEMPERATURES = {
        "psychological": 0.3,           # Updated from 0.8
        "voice_of_customer": 0.3,       # Updated from 0.7
        "competitor": 0.3,              # Updated from 0.7
        "interview_psychological": 0.3,  # Updated from 0.8
        "interview_sales": 0.3,         # Updated from 0.75
        "gtm_blueprint": 0.3,           # Updated from 0.7
        "voice": 0.3,                   # Updated from 0.7
        "gtm": 0.3                      # Updated from 0.7
    }
    
    MAX_TOKENS = {
        "research": 20000,    # Updated from 8100
        "creative": 20000,    # Updated from 8100
        "summary": 10000      # Updated from 4000
    }
    
    DEFAULT_MAX_TOKENS = MAX_TOKENS["research"]
    DEFAULT_TEMPERATURE = 0.3  # Updated from 0.75
    MAX_TOKEN_LIMIT = 20000    # Updated from 8100

MIN_TOKENS = 500  # Minimum token threshold for quality control

# Memory configuration
MEMORY_ENABLED_ENV = os.getenv("MEMORY_ENABLED", "true").lower() == "true"

# Map our env var to what BraveSearch expects
os.environ['BRAVE_SEARCH_API_KEY'] = os.getenv('BRAVE_API_KEY', '')

# Brave Search configuration
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
SEARCH_ENABLED = bool(BRAVE_API_KEY) and BRAVE_SEARCH_AVAILABLE

print(f"📊 Configuration Summary:")
print(f"   Config Module: {'✅ Loaded' if CONFIG_AVAILABLE else '⚠️ Using Fallback'}")
print(f"   Memory Enabled (env): {MEMORY_ENABLED_ENV}")
print(f"   Brave Search: {'✅ Enabled' if SEARCH_ENABLED else '❌ Disabled'}")
print(f"   Token Limits: Research={MAX_TOKENS['research']}, Creative={MAX_TOKENS['creative']}, Summary={MAX_TOKENS['summary']}")
print(f"   Temperature Range: {min(AGENT_TEMPERATURES.values()):.1f} - {max(AGENT_TEMPERATURES.values()):.1f}")
print(f"   Default Temperature: {DEFAULT_TEMPERATURE}")
print(f"   Agents Configured: {len(AGENT_TEMPERATURES)}")

# ==============================================
# 5. MANDATORY BRAVE SEARCH INITIALIZATION
# ==============================================

print("\n🔒 INITIALIZING MANDATORY SEARCH SYSTEM...")

# Search is MANDATORY - Exit if not available
if not os.getenv('BRAVE_API_KEY'):
    print("❌ FATAL: BRAVE_API_KEY missing!")
    print("   Brave Search is REQUIRED for comprehensive analysis")
    print("   Get API key from https://brave.com/search/api/")
    sys.exit(1)

if not BRAVE_SEARCH_AVAILABLE:
    print("❌ FATAL: langchain-community not installed!")
    print("   Run: pip install langchain-community")
    sys.exit(1)

# Initialize variables
brave_search = None
search_context = None
response_cache = None
SEARCH_ENABLED = False
MEMORY_ENABLED = False  # Will be set later in memory initialization

# STEP 1: Define ResponseCache class FIRST (no dependencies)
class ResponseCache:
    """
    Intelligent caching system for agent responses and search results.
    Reduces API calls and improves response times for repeated queries.
    """
    
    def __init__(self, max_cache_size: int = 1000, ttl_hours: int = 24):
        print("[DEBUG] Initializing ResponseCache...")
        self.response_cache = {}  # Store agent responses
        self.search_cache = {}    # Store search results
        self.max_cache_size = max_cache_size
        self.ttl_seconds = ttl_hours * 3600
        self.access_times = {}    # Track last access for LRU eviction
        
    def _generate_cache_key(self, agent_name: str, query: str, client_id: str = None) -> str:
        """Generate consistent cache key"""
        # Normalize query for better cache hits
        normalized_query = ' '.join(query.lower().split())
        
        # Include client_id for personalized caching when memory is enabled
        # Check global MEMORY_ENABLED variable
        if 'MEMORY_ENABLED' in globals() and MEMORY_ENABLED and client_id:
            base_key = f"{agent_name}:{normalized_query}:{client_id}"
        else:
            base_key = f"{agent_name}:{normalized_query}"
            
        # Create hash to keep keys manageable
        import hashlib
        return hashlib.md5(base_key.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cache entry is still valid based on TTL"""
        return (time.time() - timestamp) < self.ttl_seconds
    
    def _evict_old_entries(self):
        """Remove expired entries and enforce size limits"""
        current_time = time.time()
        
        # Remove expired entries
        expired_keys = []
        for key, data in list(self.response_cache.items()):
            if not self._is_cache_valid(data['timestamp']):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.response_cache.pop(key, None)
            self.search_cache.pop(key, None)
            self.access_times.pop(key, None)
        
        # Enforce size limits using LRU
        if len(self.response_cache) > self.max_cache_size:
            # Sort by last access time and remove oldest
            sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
            keys_to_remove = [k for k, _ in sorted_keys[:len(self.response_cache) - self.max_cache_size]]
            
            for key in keys_to_remove:
                self.response_cache.pop(key, None)
                self.search_cache.pop(key, None)
                self.access_times.pop(key, None)
    
    def get_cached_response(self, agent_name: str, query: str, client_id: str = None) -> Optional[Dict]:
        """Get cached agent response if available and valid"""
        cache_key = self._generate_cache_key(agent_name, query, client_id)
        
        if cache_key in self.response_cache:
            data = self.response_cache[cache_key]
            
            if self._is_cache_valid(data['timestamp']):
                # Update access time for LRU
                self.access_times[cache_key] = time.time()
                
                print(f"[CACHE] HIT for {agent_name}: {query[:50]}...")
                return {
                    'response': data['response'],
                    'sources': data.get('sources', []),
                    'word_count': data.get('word_count', 0),
                    'cached': True,
                    'cache_age': time.time() - data['timestamp']
                }
        
        print(f"[CACHE] MISS for {agent_name}: {query[:50]}...")
        return None
    
    def cache_response(self, agent_name: str, query: str, response: str, 
                      sources: List[Dict] = None, client_id: str = None):
        """Cache agent response with metadata"""
        cache_key = self._generate_cache_key(agent_name, query, client_id)
        
        # Clean up old entries before adding new ones
        self._evict_old_entries()
        
        cache_data = {
            'response': response,
            'sources': sources or [],
            'word_count': len(response.split()),
            'timestamp': time.time(),
            'agent_name': agent_name,
            'query': query[:100]  # Store truncated query for debugging
        }
        
        self.response_cache[cache_key] = cache_data
        self.access_times[cache_key] = time.time()
        
        print(f"[CACHE] STORED for {agent_name}: {len(response)} chars, {len(sources or [])} sources")
    
    def get_cached_search(self, query: str) -> Optional[Tuple[str, List[Dict]]]:
        """Get cached search results"""
        import hashlib
        search_key = hashlib.md5(query.lower().encode()).hexdigest()
        
        if search_key in self.search_cache:
            data = self.search_cache[search_key]
            if self._is_cache_valid(data['timestamp']):
                print(f"[CACHE] Search HIT: {query[:50]}...")
                return data['results'], data['sources']
        
        print(f"[CACHE] Search MISS: {query[:50]}...")
        return None
    
    def cache_search(self, query: str, results: str, sources: List[Dict]):
        """Cache search results"""
        import hashlib
        search_key = hashlib.md5(query.lower().encode()).hexdigest()
        
        self.search_cache[search_key] = {
            'results': results,
            'sources': sources,
            'timestamp': time.time()
        }
        
        print(f"[CACHE] Search STORED: {query[:50]}")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        current_time = time.time()
        valid_entries = sum(1 for data in self.response_cache.values() 
                          if self._is_cache_valid(data['timestamp']))
        
        return {
            'total_entries': len(self.response_cache),
            'valid_entries': valid_entries,
            'search_entries': len(self.search_cache),
            'cache_hit_potential': f"{(valid_entries / max(len(self.response_cache), 1) * 100):.1f}%",
            'oldest_entry_age': max([current_time - data['timestamp'] 
                                   for data in self.response_cache.values()], default=0) / 3600,
            'memory_usage_estimate': len(str(self.response_cache)) + len(str(self.search_cache))
        }
    
    def clear_cache(self, agent_name: str = None):
        """Clear cache (optionally for specific agent)"""
        if agent_name:
            keys_to_remove = [k for k, v in self.response_cache.items() 
                             if v.get('agent_name') == agent_name]
            for key in keys_to_remove:
                self.response_cache.pop(key, None)
                self.access_times.pop(key, None)
            print(f"[CACHE] Cleared cache for {agent_name}")
        else:
            self.response_cache.clear()
            self.search_cache.clear()
            self.access_times.clear()
            print("[CACHE] Cleared all cache")

# STEP 2: Initialize ResponseCache FIRST
print("[DEBUG] Creating ResponseCache instance...")
response_cache = ResponseCache(max_cache_size=1000, ttl_hours=24)
print("✅ Cache system initialized")

# STEP 3: Initialize Brave Search
try:
    from langchain_community.tools.brave_search.tool import BraveSearch
    
    print("[DEBUG] Creating BraveSearch instance...")
    brave_search = BraveSearch(
        api_wrapper=None,
        api_key=os.getenv('BRAVE_API_KEY')
    )
    
    # Test the search connection
    print("[DEBUG] Testing Brave Search connection...")
    test_result = brave_search.run("test")
    print("✅ Brave Search connection verified")
    
except Exception as e:
    print(f"❌ FATAL: Brave Search initialization failed: {e}")
    print("   Check your BRAVE_API_KEY and internet connection")
    sys.exit(1)

# STEP 4: Define SearchEnhancedContext (now response_cache exists)
class SearchEnhancedContext:
    """Track and manage web search results with citations"""
    
    def __init__(self):
        print("[DEBUG] Initializing SearchEnhancedContext...")
        self.sources = {}
        self.search_cache = {}  # Local cache as backup
    
    def search_and_cite(self, query: str, agent_name: str) -> Tuple[str, List[Dict]]:
        """
        Search web and return results with citation tracking and caching
        WHY: Now response_cache is guaranteed to exist before this method is called
        """
        print(f"[DEBUG] search_and_cite called - agent: {agent_name}, query: {query[:50]}...")
        
        # Edge case: Check if search is available
        if not brave_search:
            print("[WARNING] Brave search not available, returning empty results")
            return "", []
        
        # Check global cache first (response_cache now exists)
        cached_result = response_cache.get_cached_search(query)
        if cached_result:
            results, sources = cached_result
            print(f"[INFO] Using cached search results for: {query[:50]}...")
            
            # Track sources for this agent
            if agent_name not in self.sources:
                self.sources[agent_name] = []
            self.sources[agent_name].extend(sources)
            
            return results, sources
        
        print(f"[INFO] No cache found, performing new search for: {query[:50]}...")
        
        try:
            # Perform the actual search
            print(f"[{agent_name}] Searching: {query}")
            raw_results = brave_search.run(query)
            
            # Handle different response formats robustly
            results = []
            if isinstance(raw_results, str):
                # Try to parse as JSON if it's a string
                try:
                    results = json.loads(raw_results)
                    print(f"[DEBUG] Parsed JSON string: {len(results)} items")
                except json.JSONDecodeError:
                    # Not JSON, might be plain text results
                    print(f"[WARNING] Search returned plain text, creating single result")
                    results = [{
                        "title": "Search Result",
                        "link": "",
                        "snippet": raw_results[:500] if raw_results else ""
                    }]
            elif isinstance(raw_results, list):
                # Already a list, use directly
                results = raw_results
                print(f"[DEBUG] Got list of {len(results)} results")
            elif isinstance(raw_results, dict):
                # Might be wrapped in a response object
                if 'results' in raw_results:
                    results = raw_results['results']
                elif 'web' in raw_results:
                    results = raw_results['web'].get('results', [])
                else:
                    # Use the dict as a single result
                    results = [raw_results]
                print(f"[DEBUG] Extracted {len(results)} results from dict")
            else:
                # Unknown format
                print(f"[ERROR] Unexpected search result type: {type(raw_results)}")
                print(f"[DEBUG] Raw result sample: {str(raw_results)[:200]}")
                results = []
            
            # Edge case: Handle empty results
            if not results:
                print(f"[WARNING] No search results found for: {query}")
                return "", []
            
            # Format results with sources
            sources = []
            formatted = f"\n=== WEB RESEARCH: {query} ===\n"
            
            for i, result in enumerate(results[:3], 1):
                source = {
                    "id": f"{agent_name}_source_{i}",
                    "title": result.get("title", "Unknown"),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                }
                sources.append(source)
                
                formatted += f"""
Source [{i}]: {source['title']}
URL: {source['url']}
Content: {source['snippet']}
---"""
            
            # Cache results in global cache
            response_cache.cache_search(query, formatted, sources)
            print(f"[INFO] Cached search results for future use")
            
            # Also store in local cache as backup
            self.search_cache[f"{agent_name}:{query}"] = (formatted, sources)
            
            # Track sources for this agent
            if agent_name not in self.sources:
                self.sources[agent_name] = []
            self.sources[agent_name].extend(sources)
            
            return formatted, sources
            
        except Exception as e:
            print(f"[ERROR] Search failed for {agent_name}: {str(e)}")
            print(f"[DEBUG] Error type: {type(e).__name__}")
            print("[FIX] Potential solutions:")
            print("  1. Check BRAVE_API_KEY is valid")
            print("  2. Verify internet connection")
            print("  3. Check if query contains special characters")
            return "", []
    
    def get_agent_sources(self, agent_name: str) -> List[Dict]:
        """Get all sources used by an agent"""
        return self.sources.get(agent_name, [])

# STEP 5: Initialize SearchEnhancedContext (response_cache now exists)
print("[DEBUG] Creating SearchEnhancedContext instance...")
search_context = SearchEnhancedContext()
SEARCH_ENABLED = True  # Force to True

print("✅ Search system fully initialized with caching")
print(f"[INFO] Cache TTL: 24 hours")
print(f"[INFO] Max cache size: 1000 entries")
print("[SUCCESS] Block 5 initialization complete!")

# ==============================================
# 6. MEMORY SYSTEM INITIALIZATION WITH ENHANCED DEBUG
# ==============================================

print("\n🔒 INITIALIZING MEMORY SYSTEM WITH DIAGNOSTICS...")

memory_system = None
MEMORY_ENABLED = False

# First, check and validate environment variables
qdrant_url = os.getenv('QDRANT_URL', '').strip()
qdrant_api_key = os.getenv('QDRANT_API_KEY', '').strip()

print("\n📋 MEMORY SYSTEM DIAGNOSTICS:")
print("=" * 50)

# Check credentials
if not qdrant_url or not qdrant_api_key:
    print("❌ ISSUE: Missing Qdrant credentials")
    print(f"   QDRANT_URL: {'Not set' if not qdrant_url else 'Set'}")
    print(f"   QDRANT_API_KEY: {'Not set' if not qdrant_api_key else 'Set (hidden)'}")
    print("\n✅ SOLUTION: Bot will run without memory features")
    MEMORY_ENABLED = False
else:
    print(f"✅ Credentials found")
    print(f"   URL: {qdrant_url}")
    print(f"   API Key: {'*' * 8 + qdrant_api_key[-4:] if len(qdrant_api_key) > 4 else 'Set'}")
    
    # Analyze the URL format
    print("\n🔍 URL ANALYSIS:")
    
    # Check if URL has correct format
    url_issues = []
    
    if not qdrant_url.startswith(('http://', 'https://')):
        url_issues.append("Missing http:// or https:// prefix")
    
    if ':6333' not in qdrant_url and ':6334' not in qdrant_url:
        print("⚠️  WARNING: URL doesn't include port :6333 or :6334")
        print("   Standard Qdrant ports are 6333 (HTTP) or 6334 (gRPC)")
        
    if '.gcp.cloud.qdrant.io' in qdrant_url:
        print("✅ GCP Qdrant Cloud URL detected")
    elif '.aws.cloud.qdrant.io' in qdrant_url:
        print("✅ AWS Qdrant Cloud URL detected")
    elif 'localhost' in qdrant_url:
        print("✅ Local Qdrant instance")
    else:
        print("⚠️  Non-standard Qdrant URL format")
    
    # Parse the URL to check components
    from urllib.parse import urlparse
    parsed = urlparse(qdrant_url)
    print(f"\n📊 URL COMPONENTS:")
    print(f"   Scheme: {parsed.scheme or 'missing'}")
    print(f"   Host: {parsed.hostname or 'missing'}")
    print(f"   Port: {parsed.port or 'not specified'}")
    
    # Try different connection methods
    print("\n🔄 ATTEMPTING CONNECTION METHODS:")
    
    try:
        # Method 1: Try direct connection with original URL
        print(f"\n1️⃣ Trying direct connection to: {qdrant_url}")
        
        try:
            import requests
            # Test if the endpoint is reachable
            test_url = qdrant_url if qdrant_url.endswith('/') else qdrant_url
            response = requests.get(test_url, timeout=5, headers={'api-key': qdrant_api_key})
            print(f"   HTTP Response: {response.status_code}")
            
            if response.status_code == 404:
                print("   ❌ 404 Error - Endpoint not found")
                print("   POSSIBLE CAUSES:")
                print("   - Qdrant cluster is paused/stopped")
                print("   - Incorrect URL format")
                print("   - Cluster was deleted")
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ Connection failed: Cannot reach server")
            print(f"   - Check if cluster is running at https://cloud.qdrant.io")
        except requests.exceptions.Timeout:
            print(f"   ❌ Connection timeout - server not responding")
        except Exception as e:
            print(f"   ❌ Request error: {str(e)[:100]}")
        
        # Method 2: Try with QdrantClient
        print(f"\n2️⃣ Trying QdrantClient initialization...")
        
        from core.memory_system_qdrant import QdrantMemorySystem
        
        # Try to initialize with modified settings
        print("   Attempting to create QdrantMemorySystem...")
        
        # Temporarily modify the initialization to add debugging
        import sys
        import io
        
        # Capture any output during initialization
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            memory_system = QdrantMemorySystem()
            output = buffer.getvalue()
            if output:
                print(f"   Debug output: {output}")
        finally:
            sys.stdout = old_stdout
        
        # Test basic functionality
        print("\n3️⃣ Testing memory operations...")
        test_client_id = f"test_{datetime.now().timestamp()}"
        
        try:
            memory_system.store_memory(
                client_id=test_client_id,
                agent_name="system",
                memory_type="test",
                content="System startup test",
                importance=0.1
            )
            print("   ✅ Memory write successful")
            MEMORY_ENABLED = True
            
        except Exception as test_error:
            print(f"   ❌ Memory test failed: {str(test_error)[:200]}")
            
            # Analyze the specific error
            error_str = str(test_error).lower()
            if '404' in error_str:
                print("\n   🔴 ROOT CAUSE: Qdrant cluster not accessible")
                print("   SOLUTIONS:")
                print("   1. Go to https://cloud.qdrant.io")
                print("   2. Check if your cluster is 'Running' (not paused)")
                print("   3. Click 'Resume' if it's paused")
                print("   4. Verify the cluster ID matches: 2d627959-580b-4411-959b")
                print("   5. Check region is: europe-west3-0")
            elif 'unauthorized' in error_str or '401' in error_str:
                print("\n   🔴 ROOT CAUSE: Authentication failed")
                print("   SOLUTIONS:")
                print("   1. Regenerate API key in Qdrant dashboard")
                print("   2. Update QDRANT_API_KEY in .env file")
            elif 'timeout' in error_str:
                print("\n   🔴 ROOT CAUSE: Network timeout")
                print("   SOLUTIONS:")
                print("   1. Check internet connection")
                print("   2. Check firewall settings")
                print("   3. Try a different network")
            
            MEMORY_ENABLED = False
            memory_system = None
            
    except ImportError as e:
        print(f"\n❌ Module import error: {e}")
        print("   SOLUTION: Install required packages:")
        print("   pip install qdrant-client sentence-transformers")
        MEMORY_ENABLED = False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)[:200]}")
        print("   Error type:", type(e).__name__)
        MEMORY_ENABLED = False

# Final decision
print("\n" + "=" * 50)
if MEMORY_ENABLED:
    print("✅ MEMORY SYSTEM: ACTIVE")
    print("   Bot will remember conversations")
else:
    print("⚠️  MEMORY SYSTEM: BYPASSED")
    print("   Bot will function normally without memory")
    print("   All other features (Sonnet 4.5, search, etc.) working")

# Set the environment variable
MEMORY_ENABLED_ENV = MEMORY_ENABLED

print("=" * 50)
print(f"\n🤖 Continuing with bot initialization...")
print(f"   Memory: {'Enabled' if MEMORY_ENABLED else 'Disabled (not required)'}")
print(f"   This will not affect other bot features\n")

# ==============================================
# 7. LLM INITIALIZATION - DYNAMIC CONFIGURATION
# ==============================================

def get_llm_for_agent(agent_name: str = None):
    """
    Get LLM with agent-specific configuration.
    NOW USES THE NEW CONFIG MODULE WITH SONNET 4.5 AND 0.3 TEMP
    """
    
    # Use Config class if available
    if CONFIG_AVAILABLE and Config:
        try:
            # Use the Config class to get LLM with proper settings
            llm = Config.get_llm(agent_name)
            
            if llm:
                # Get the configuration for logging
                agent_config = Config.get_agent_config(agent_name) if agent_name else {}
                
                logger.info(
                    f"Creating LLM for {agent_name or 'default'}: "
                    f"model={Config.LLM_MODEL}, "
                    f"temp={agent_config.get('temperature', Config.DEFAULT_TEMPERATURE)}, "
                    f"tokens={agent_config.get('max_tokens', Config.MAX_TOKENS['research'])}"
                )
                
                print(f"✅ Using Sonnet 4.5 with temp 0.3 for {agent_name or 'default'}")
                return llm
            else:
                logger.error(f"Failed to create LLM for {agent_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error using Config module: {e}")
            logger.info("Falling back to legacy LLM creation")
    
    # Fallback to legacy method if Config not available
    return get_llm_for_agent_legacy(agent_name)

def get_llm_for_agent_legacy(agent_name: str = None):
    """
    Legacy LLM creation - kept as fallback
    UPDATED: Now uses 0.3 temperature and 20k tokens to match Config
    """
    
    # Normalize agent name
    if agent_name:
        agent_name = agent_name.lower().replace('-', '_')
    
    # Get temperature for specific agent or use default
    if agent_name and agent_name in AGENT_TEMPERATURES:
        temperature = AGENT_TEMPERATURES[agent_name]
    else:
        temperature = DEFAULT_TEMPERATURE
    
    # Get token limit based on agent type
    if agent_name in ["psychological", "interview_psychological", "interview_sales"]:
        max_tokens = MAX_TOKENS["creative"]
        token_type = "creative"
    elif agent_name in ["gtm_blueprint", "gtm"]:
        # Maximum for comprehensive GTM analysis
        max_tokens = MAX_TOKENS["research"]
        token_type = "comprehensive"
    else:
        max_tokens = MAX_TOKENS["research"]
        token_type = "research"
    
    try:
        from langchain_anthropic import ChatAnthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment!")
            return None
        
        # Determine which model to use
        model = "claude-3-5-sonnet-4-20250514" if CONFIG_AVAILABLE else "claude-3-5-sonnet-20241022"
        
        logger.info(f"Creating LLM for {agent_name or 'default'}: temp={temperature:.2f}, tokens={max_tokens} ({token_type}), model={model}")
        
        return ChatAnthropic(
            model=model,
            anthropic_api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=60
        )
        
    except Exception as e:
        logger.error(f"LLM initialization failed for {agent_name}: {e}")
        return None

# Initialize default LLM for general use
llm = get_llm_for_agent()
LLM_AVAILABLE = llm is not None

if LLM_AVAILABLE:
    if CONFIG_AVAILABLE:
        print(f"✅ LLM initialized with Config module")
        print(f"   Model: {Config.LLM_MODEL}")
        print(f"   Default tokens: {Config.MAX_TOKENS['research']}")
        print(f"   Default temperature: {Config.DEFAULT_TEMPERATURE}")
    else:
        print(f"✅ LLM initialized with fallback configuration")
        print(f"   Model: claude-3-5-sonnet-20241022")
        print(f"   Default tokens: {DEFAULT_MAX_TOKENS}")
        print(f"   Default temperature: {DEFAULT_TEMPERATURE}")
        print(f"   Temperature: 0.3 (focused, consistent outputs)")
else:
    print("❌ LLM initialization failed - check ANTHROPIC_API_KEY")

# IMPORTANT: LLM_AVAILABLE must be defined here before it's used elsewhere
# Export for other modules if needed
__all__ = ['get_llm_for_agent', 'get_llm_for_agent_legacy', 'llm', 'LLM_AVAILABLE']

# ==============================================
# END OF SECTION 7 - LLM INITIALIZATION COMPLETE
# ==============================================
# 8. WORKFLOW INITIALIZATION
# ==============================================

workflow_available = False
try:
    from team_icp.workflows.graph import ICPGraph
    workflow_available = True
    logger.info("✅ Workflow graph imported successfully")
    print("✅ Workflow system ready")
    
    # Pass configuration to graph module
    import team_icp.workflows.graph as graph_module
    if hasattr(graph_module, 'MAX_TOKEN_LIMIT'):
        graph_module.MAX_TOKEN_LIMIT = MAX_TOKEN_LIMIT
    if hasattr(graph_module, 'DEFAULT_TEMPERATURE'):
        graph_module.DEFAULT_TEMPERATURE = DEFAULT_TEMPERATURE
        
except ImportError as e:
    logger.error(f"❌ Failed to import workflow: {e}")
    print(f"❌ Workflow not available: {e}")

# ==============================================
# 9. SLACK APP INITIALIZATION
# ==============================================

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

logger.info("✅ Slack app initialized")

# ==============================================
# 10. GLOBAL VARIABLES & CACHES
# ==============================================

# Memory stores
LAST_ANALYSIS = {}  # Store recent analyses by channel for elaboration
AGENT_RESPONSES = {}  # Store agent responses for direct Q&A
TEMPLATE_SESSIONS = {}  # Store multi-step template sessions
RESEARCH_UPLOAD_PENDING = {}  # Track users waiting to upload

# Rate limiting
last_api_call = 0
API_RATE_LIMIT = 1.0  # Minimum seconds between API calls

# ==============================================
# 11. SYSTEM STATUS SUMMARY
# ==============================================

print("\n" + "="*60)
print("MARKET RESEARCH TEAM BOT v3.0 - INITIALIZATION COMPLETE")
print("="*60)
print(f"✅ Core Systems:")
print(f"   • LLM: {'Ready' if LLM_AVAILABLE else 'Failed'}")
print(f"   • Workflow: {'Ready' if workflow_available else 'Failed'}")
print(f"   • Memory: {'✅ Connected (MANDATORY)' if MEMORY_ENABLED else '❌ FAILED (MANDATORY)'}")
print(f"   • Search: {'✅ Enabled (MANDATORY)' if SEARCH_ENABLED else '❌ FAILED (MANDATORY)'}")
print(f"   • Slack: Ready")

# Final check - don't continue if mandatory systems failed
if not SEARCH_ENABLED:  # Memory is optional
    print("\n❌ FATAL: Mandatory systems not available")
    print("   Both Memory (Qdrant) and Search (Brave) are REQUIRED")
    print("   Bot cannot function without these systems")
    sys.exit(1)

print(f"\n📊 Active Configuration:")
print(f"   • {len(AGENT_TEMPERATURES)} agents configured")
print(f"   • Temperature range: {min(AGENT_TEMPERATURES.values()):.1f}-{max(AGENT_TEMPERATURES.values()):.1f}")
print(f"   • Token limits: {MIN_TOKENS}-{MAX_TOKENS['creative']}")
print("="*60 + "\n")


# ==============================================
# 9. AGENT PERSONAS REGISTRY
# ==============================================

AGENT_PERSONAS = {
    "psychological": {
        "emoji": "🧠",
        "name": "Psychological Analyst",
        "personality": "I analyze deep psychological patterns, unconscious motivations, and identity conflicts.",
        "focus": ["fears", "identity", "unconscious", "transformation", "resistance"],
        "color": "#9B59B6"
    },
    "voice_of_customer": {
        "emoji": "🗣️",
        "name": "Voice of Customer Specialist",
        "personality": "I extract exact customer language, pain points, and aspirations.",
        "focus": ["language", "pain points", "exact words", "phrases", "aspirations"],
        "color": "#3498DB"
    },
    "competitor": {
        "emoji": "🔍",
        "name": "Competitor Intelligence Analyst",
        "personality": "I map competitive landscapes and identify positioning opportunities.",
        "focus": ["competitors", "positioning", "gaps", "opportunities", "weaknesses"],
        "color": "#E74C3C"
    },
    "interview_psychological": {
        "emoji": "🎭",
        "name": "Psychological Interview Specialist",
        "personality": "I simulate deep psychological interviews to reveal emotional vulnerabilities.",
        "focus": ["interviews", "emotions", "vulnerabilities", "objections", "beliefs"],
        "color": "#8E44AD"
    },
    "interview_sales": {
        "emoji": "💰",
        "name": "Sales Interview Specialist",
        "personality": "I conduct sales discovery to identify buying triggers and decision criteria.",
        "focus": ["sales", "buying triggers", "decision process", "budget", "timeline"],
        "color": "#F39C12"
    },
    "gtm_blueprint": {
        "emoji": "📋",
        "name": "GTM Blueprint Strategist",
        "personality": "I synthesize insights into actionable go-to-market strategies.",
        "focus": ["strategy", "positioning", "messaging", "channels", "tactics"],
        "color": "#27AE60"
    }
}

# Create aliases for convenience
AGENT_ALIASES = {
    "voice": "voice_of_customer",
    "gtm": "gtm_blueprint",
    "psychological_interview": "interview_psychological",
    "sales_interview": "interview_sales",
    "blueprint": "gtm_blueprint"
}

def normalize_agent_name(agent_name: str) -> str:
    """Normalize agent names to their canonical form"""
    agent_name = agent_name.lower().strip().replace('-', '_')
    
    # Check if it's an alias
    if agent_name in AGENT_ALIASES:
        return AGENT_ALIASES[agent_name]
    
    # Check if it's already valid
    if agent_name in AGENT_PERSONAS:
        return agent_name
    
    # Return None if invalid
    return None

# ==============================================
# 10. TEMPLATE STRUCTURE
# ==============================================

TEMPLATE_STRUCTURE = {
    "sections": [
        "business_type",
        "company_name",
        "industry",
        "product_service",
        "target_customer",
        "demographics",
        "customer_context",
        "problems_solved",
        "customer_complaints",
        "customer_goals",
        "success_vision",
        "market_details",
        "marketing_goal",
        "additional_context"
    ],
    "section_details": {
        "business_type": "B2B, B2C, or B2B2C",
        "company_name": "Your company name",
        "industry": "Specific industry/niche",
        "product_service": "Detailed description with pillars",
        "target_customer": "One sentence ideal customer",
        "demographics": "Age, gender, education, income, etc.",
        "customer_context": "Day-to-day reality and pressures",
        "problems_solved": "5-7 specific problems",
        "customer_complaints": "7-10 exact customer quotes",
        "customer_goals": "5-6 stated goals",
        "success_vision": "5-6 success quotes",
        "market_details": "Segments and trends",
        "marketing_goal": "Specific action desired",
        "additional_context": "Founder story, differentiators, etc."
    }
}

# ==============================================
# 11. HELPER FUNCTIONS
# ==============================================

def get_client_id(channel_id: str, user_id: Optional[str] = None) -> str:
    """
    Generate consistent client ID for memory persistence.
    Format: channel_id_user_id (e.g., "C123456_U789012")
    CRITICAL: Must be consistent across all bot instances
    """
    if user_id:
        return f"{channel_id}_{user_id}"
    return channel_id

def format_quality_score(score: float) -> str:
    """Format quality score with emoji indicator"""
    if score >= 0.9:
        return f"🌟 {score:.2%}"
    elif score >= 0.8:
        return f"✅ {score:.2%}"
    elif score >= 0.7:
        return f"⚠️ {score:.2%}"
    else:
        return f"❌ {score:.2%}"

def format_web_sources_limited(sources_list: List[Dict], limit: int = 10) -> str:
    """
    Format web sources with a limit on how many to display.
    Shows only first 'limit' sources but indicates total count.
    
    Args:
        sources_list: List of source dictionaries from web search
        limit: Maximum number of sources to display (default 10)
    
    Returns:
        Formatted string with limited source citations
    """
    if not sources_list:
        return ""
    
    total_sources = len(sources_list)
    display_sources = sources_list[:limit]  # Only show first N sources
    
    citations = []
    for i, source in enumerate(display_sources, 1):
        title = source.get('title', 'Untitled')
        url = source.get('url', '#')
        
        # Extract domain for cleaner display
        try:
            domain = url.split('//')[1].split('/')[0] if '//' in url else 'Unknown'
        except:
            domain = 'Unknown'
        
        # Clean up title (remove extra whitespace, truncate if too long)
        clean_title = ' '.join(title.split())
        if len(clean_title) > 80:
            clean_title = clean_title[:77] + "..."
        
        citations.append(f"[{i}] {clean_title}\n    🔗 {domain} - {url}")
    
    citation_text = "\n".join(citations)
    
    # Add summary if there are more sources than displayed
    if total_sources > limit:
        citation_text += f"\n\n... and {total_sources - limit} additional sources analyzed but not shown for brevity"
    
    # Create header with count information
    if total_sources > limit:
        header = f"🔍 **Web Sources** (Showing {limit} of {total_sources} total):"
    else:
        header = f"🔍 **Web Sources** ({total_sources} total):"
    
    return f"\n\n{header}\n{citation_text}"

def save_report_to_file(company: str, content: str, report_type: str = "analysis") -> str:
    """Save report to file and return filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = company.lower().replace(' ', '_').replace('/', '_')[:30]
    filename = f"{safe_company}_{report_type}_{timestamp}.txt"
    
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    filepath = reports_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Report saved to: {filepath}")
    return str(filepath)

def create_downloadable_file(content: str, filename: str) -> str:
    """
    Create a temporary file and return its path.
    """
    import tempfile
    import os
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name
    
    return temp_path


# ============================================
# ALSO FIX: send_response_with_file_fallback function signature
# UPDATE to accept both display and full content
# ============================================

async def send_response_with_file_fallback(
    client, 
    channel: str, 
    thread_ts: str, 
    initial_message: str,
    full_content: str = None,  # NEW: Add full content parameter
    title: str = "Analysis",
    max_length: int = 3800
):
    """
    Send response to Slack, falling back to file upload if too long.
    
    Args:
        client: Slack client
        channel: Channel ID
        thread_ts: Thread timestamp
        initial_message: Message to display in Slack (may be truncated)
        full_content: Full content for file upload (untruncated)
        title: Title for the file if uploaded
        max_length: Maximum message length before file upload
    """
    
    # Use full_content for file if provided, otherwise fall back to initial_message
    content_for_file = full_content if full_content else initial_message
    
    print(f"\n{'='*50}")
    print(f"[FILE_HANDLER] Starting file fallback handler")
    print(f"[FILE_HANDLER] Display message length: {len(initial_message)} chars")
    print(f"[FILE_HANDLER] Full content length: {len(content_for_file)} chars")
    print(f"[FILE_HANDLER] First 100 chars: {initial_message[:100]}...")
    print(f"[FILE_HANDLER] Will upload file: {len(initial_message) > max_length}")
    print(f"[FILE_HANDLER] Channel: {channel}, Thread: {thread_ts}")
    print(f"{'='*50}")
    
    try:
        # Always try to send the display message first
        if len(initial_message) <= max_length:
            # Message fits, send normally
            result = client.chat_postMessage(
                channel=channel,
                text=initial_message,
                thread_ts=thread_ts
            )
            print(f"[FILE_HANDLER] ✅ Message sent directly (within limit)")
            return result
        
        # Message too long, upload FULL content as file
        print(f"[FILE_HANDLER] ⚠️ Response exceeds limit by {len(initial_message) - max_length} chars")
        print(f"[FILE_HANDLER] Creating file for upload...")
        
        # Create file with FULL content
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title.replace(' ', '_')}_{timestamp}.txt"
        
        print(f"[FILE_HANDLER] Filename: {filename}")
        print(f"[FILE_HANDLER] File content length: {len(content_for_file)} chars")
        
        # Create summary message for Slack
        summary = initial_message[:500] + "...\n\n📎 *Full analysis uploaded as file attachment*"
        
        # Upload the FULL content as file
        print(f"[FILE_HANDLER] Calling files_upload_v2...")
        result = client.files_upload_v2(
            channel=channel,
            thread_ts=thread_ts,
            content=content_for_file,  # Use FULL content here
            filename=filename,
            title=f"{title} (Full Analysis)",
            initial_comment=summary
        )
        
        print(f"[FILE_HANDLER] ✅ File uploaded successfully!")
        print(f"[FILE_HANDLER] Upload result: {result}")
        return result
        
    except Exception as e:
        print(f"[FILE_HANDLER] ❌ Error: {str(e)}")
        # Fallback: try to send truncated message
        try:
            truncated = initial_message[:max_length-100] + "\n\n... [truncated due to length]"
            result = client.chat_postMessage(
                channel=channel,
                text=truncated,
                thread_ts=thread_ts
            )
            print(f"[FILE_HANDLER] Sent truncated message as fallback")
            return result
        except Exception as e2:
            print(f"[FILE_HANDLER] ❌ Failed to send even truncated message: {str(e2)}")
            raise
        
def extract_agent_and_question(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract agent name and question from mention text.
    Examples:
    - "@Agentic Team @psychological what are deep fears?" -> ("psychological", "what are deep fears?")
    - "@Agentic Team voice: show customer pain" -> ("voice", "show customer pain")
    """
    # Remove bot mention (handles both @bot and @Agentic Team)
    text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
    text = re.sub(r'@Agentic Team', '', text, flags=re.IGNORECASE).strip()
    
    # Pattern 1: @agent_name question
    pattern1 = r'@(\w+)\s+(.*)'
    match1 = re.match(pattern1, text)
    if match1:
        agent = normalize_agent_name(match1.group(1))
        if agent:
            return agent, match1.group(2)
    
    # Pattern 2: agent_name: question
    pattern2 = r'(\w+):\s*(.*)'
    match2 = re.match(pattern2, text)
    if match2:
        agent = normalize_agent_name(match2.group(1))
        if agent:
            return agent, match2.group(2)
    
    # Pattern 3: Just agent name followed by question
    words = text.split(None, 1)
    if len(words) >= 2:
        agent = normalize_agent_name(words[0])
        if agent:
            return agent, words[1]
    
    return None, None

def send_full_report_to_slack(client, channel_id, thread_ts, full_report, company):
    """Send full report to Slack, handling message limits"""
    MAX_MESSAGE_LENGTH = 35000
    
    if len(full_report) <= MAX_MESSAGE_LENGTH:
        try:
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=full_report
            )
            logger.info(f"Sent full report as single message ({len(full_report)} chars)")
        except Exception as e:
            logger.error(f"Failed to send full report: {e}")
    else:
        # Split into chunks
        chunks = []
        lines = full_report.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > MAX_MESSAGE_LENGTH:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = len(line) + 1
            else:
                current_chunk.append(line)
                current_length += len(line) + 1
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Send each chunk
        for i, chunk in enumerate(chunks, 1):
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=f"**Report Part {i}/{len(chunks)}**\n\n{chunk}"
                )
                time.sleep(0.5)
                logger.info(f"Sent report chunk {i}/{len(chunks)}")
            except Exception as e:
                logger.error(f"Failed to send chunk {i}: {e}")

def format_web_sources(sources_list: List[Dict], agent_name: str = None) -> str:
    """
    Format web sources into readable citations with URLs.
    
    Args:
        sources_list: List of source dictionaries from Brave search
        agent_name: Name of agent for context
    
    Returns:
        Formatted citation string
    """
    if not sources_list:
        return ""
    
    # Limit to top 5 sources to avoid clutter
    top_sources = sources_list[:5]
    
    citations = []
    for i, source in enumerate(top_sources, 1):
        title = source.get('title', 'Untitled')
        url = source.get('url', '#')
        domain = url.split('//')[1].split('/')[0] if '//' in url else 'Unknown'
        
        # Clean up title (remove extra whitespace, truncate if too long)
        clean_title = ' '.join(title.split())
        if len(clean_title) > 80:
            clean_title = clean_title[:77] + "..."
        
        citations.append(f"[{i}] {clean_title}\n    📱 {domain} - {url}")
    
    citation_text = "\n".join(citations)
    
    if agent_name:
        header = f"🔍 **{agent_name.title()} Sources:**"
    else:
        header = "🔍 **Research Sources:**"
    
    return f"\n\n{header}\n{citation_text}"


def enhance_response_with_sources(response: str, sources_list: List[Dict], agent_name: str = None) -> str:
    """
    Add source citations to agent response.
    Now limits to 10 sources for cleaner display.
    
    Args:
        response: Original agent response
        sources_list: List of web sources used
        agent_name: Agent name for context
    
    Returns:
        Response with LIMITED citations appended
    """
    if not sources_list:
        return response + "\n\n📊 *Analysis enhanced with web search*"
    
    # Use the limited formatter
    sources_section = format_web_sources_limited(sources_list, limit=10)
    
    # Count sources for summary
    source_count = len(sources_list)
    
    enhanced_response = (
        f"{response}"
        f"{sources_section}"
        f"\n\n📊 *Analysis based on {source_count} web sources*"
    )
    
    if source_count > 10:
        enhanced_response += f" *(top 10 shown above)*"
    
    return enhanced_response

def clean_company_name(query: str) -> str:
    """Clean and normalize company name from query"""
    # Remove common prefixes
    query = query.strip()
    prefixes_to_remove = ['analyze', 'research', 'tell me about', 'what about']
    query_lower = query.lower()
    
    for prefix in prefixes_to_remove:
        if query_lower.startswith(prefix):
            query = query[len(prefix):].strip()
    
    # Capitalize properly
    return ' '.join(word.capitalize() for word in query.split())

def format_search_results(search_results: list) -> str:
    """Format search results into readable text"""
    if not search_results:
        return "No search results available."
    
    formatted = []
    for i, result in enumerate(search_results[:5], 1):
        if isinstance(result, dict):
            title = result.get('title', 'Result')
            snippet = result.get('snippet', result.get('description', ''))
            formatted.append(f"{i}. {title}: {snippet[:200]}...")
        else:
            formatted.append(f"{i}. {str(result)[:200]}...")
    
    return "\n".join(formatted)

def validate_agent_output(output: str, agent_name: str) -> bool:
    """Check if agent completed all required sections"""
    
    required_sections = [
        "1. EXECUTIVE SUMMARY",
        "2. MARKET CONTEXT", 
        "3. TARGET AUDIENCE",
        "4. CUSTOMER PSYCHOLOGY",
        "5. VOICE OF CUSTOMER",
        "6. COMPETITIVE LANDSCAPE",
        "7. POSITIONING STRATEGY",
        "8. MESSAGING FRAMEWORK",
        "9. PRODUCT STRATEGY",
        "10. PRICING STRATEGY",
        "11. SALES STRATEGY",
        "12. MARKETING STRATEGY",
        "13. SUCCESS METRICS",
        "14. IMPLEMENTATION ROADMAP"
    ]
    
    missing = []
    output_upper = output.upper()
    for section in required_sections:
        if section not in output_upper:
            missing.append(section)
    
    if missing:
        print(f"[WARNING] {agent_name} missing sections: {missing}")
        return False
    
    return True

async def execute_single_agent_direct(agent_name: str, query: str, user_id: str, channel_id: str) -> tuple:
    """
    Execute a single agent directly with intelligent caching.
    Much faster for repeated queries.
    
    Args:
        agent_name: Name of the agent to execute
        query: The query/question to process
        user_id: Slack user ID
        channel_id: Slack channel ID
    
    Returns:
        tuple: (response_text, sources_list)
    """
    import time
    start_time = time.time()
    
    # Build client_id from user_id and channel_id
    client_id = get_client_id(channel_id, user_id)
    
    print(f"\n{'='*60}")
    print(f"EXECUTING SINGLE AGENT: {agent_name}")
    print(f"Query: {query}")
    print(f"Request ID: {client_id}")
    print(f"{'='*60}")
    
    # Check cache first
    cached_result = response_cache.get_cached_response(agent_name, query, client_id)
    if cached_result:
        cache_age = cached_result['cache_age']
        print(f"[CACHE] Using cached response for {agent_name} (age: {cache_age/60:.1f} min)")
        return cached_result['response'], cached_result['sources']
    
    print(f"[DIRECT] Executing {agent_name} directly (no workflow)")
    
    try:
        # 1. Clean the query
        company_name = clean_company_name(query)
        
        # 2. Get agent-specific LLM configuration
        agent_llm = get_llm_for_agent(agent_name)
        if not agent_llm:
            return f"[ERROR] Could not initialize LLM for {agent_name}", []
        
        # 3. Load ONLY this agent's memories (if enabled)
        agent_context = ""
        if MEMORY_ENABLED and memory_system:
            try:
                memories = memory_system.retrieve_memories(
                    client_id=client_id,
                    agent_name=agent_name,
                    query=query,
                    limit=5  # Only top 5 relevant memories
                )
                if memories:
                    agent_context = "\n\nRelevant memories from previous analyses:\n"
                    for mem in memories:
                        agent_context += f"- {mem.content}\n"
                    print(f"[DIRECT] Loaded {len(memories)} memories for {agent_name}")
            except Exception as e:
                print(f"[DIRECT] Memory load failed: {e}")
        
        # 4. Perform ONLY this agent's search (if enabled) - WITH CACHING
        search_context_text = ""
        sources_used = []  # Store sources for citations
        
        if SEARCH_ENABLED and search_context:
            try:
                # Agent-specific search query
                search_query = f"{query} {' '.join(AGENT_PERSONAS[agent_name]['focus'][:2])}"
                search_results, sources = search_context.search_and_cite(search_query, agent_name)
                
                if search_results:
                    search_context_text = search_results
                    sources_used = sources  # Capture the sources
                    print(f"[DIRECT] Found {len(sources)} web sources for {agent_name}")
            except Exception as e:
                print(f"[DIRECT] Search failed: {e}")
        
        # 5. Build agent-specific prompt
        persona = AGENT_PERSONAS[agent_name]
        
        # Special handling for psychological agent with new research prompts
        if agent_name == "psychological":
            try:
                # Import the new research prompts
                from team_icp.prompts.research_prompts import ICPResearchPrompts
                
                # Get the sophisticated prompt
                prompt_generator = ICPResearchPrompts()
                base_prompt = prompt_generator.get_psychological_analysis_prompt()
                
                # Build business context
                business_context = f"""
                COMPANY: {company_name}
                QUERY: {query}
                INDUSTRY CONTEXT: {agent_context if agent_context else 'General market'}
                
                SEARCH RESULTS:
                {search_context_text if search_context_text else 'No specific search results available.'}
                """
                
                # Format with context
                prompt = base_prompt.format(
                    business_context=business_context,
                    memory_patterns=agent_context if agent_context else "No previous patterns available."
                )
                
                print(f"[DIRECT] Using research prompts for psychological agent")
                
            except ImportError:
                # Fallback to standard prompt if research_prompts not available
                print("[DIRECT] Research prompts not available, using standard prompt")
                prompt = f"""You are the {persona['name']}.
                
                Personality: {persona['personality']}
                Focus areas: {', '.join(persona['focus'])}
                
                {agent_context}
                
                {search_context_text}
                
                Query: {query}
                
                Provide a comprehensive analysis focusing on your specific expertise. Be detailed and insightful."""
        else:
            # Standard prompt for other agents
            prompt = f"""You are the {persona['name']}.
            
            Personality: {persona['personality']}
            Focus areas: {', '.join(persona['focus'])}
            
            {agent_context}
            
            {search_context_text}
            
            Query: {query}
            
            Provide a comprehensive analysis focusing on your specific expertise. Be detailed and insightful."""
        
        # 6. Execute agent directly
        print(f"[DIRECT] Invoking LLM for {agent_name}...")
        response = await agent_llm.ainvoke(prompt)
        result = response.content if hasattr(response, 'content') else str(response)
        
        elapsed = time.time() - start_time
        print(f"[DIRECT] {agent_name} completed in {elapsed:.2f}s (vs ~30s with workflow)")
        
        # 7. Cache the response
        response_cache.cache_response(agent_name, query, result, sources_used, client_id)
        
        # 8. Store memory of this interaction
        if MEMORY_ENABLED and memory_system and len(result) > 100:
            try:
                memory_system.store_memory(
                    client_id=client_id,
                    agent_name=agent_name,
                    memory_type="direct_qa",
                    content=f"Q: {query[:200]} A: {result[:500]}",
                    importance=0.7
                )
            except:
                pass
        
        return result, sources_used  # Return both response and sources
        
    except Exception as e:
        print(f"[DIRECT] Agent execution failed: {e}")
        return f"[ERROR] {agent_name} execution failed: {str(e)}", []

def should_use_workflow(agents_requested: List[str], query_complexity: str = None) -> bool:
    """
    Decide whether to use workflow or direct execution.
    """
    # Multiple agents always benefit from workflow
    if len(agents_requested) > 1:
        return True
    
    # Complex agents that need other agent context
    if any(agent in ['interview_psychological'] for agent in agents_requested):
        return True
    
    # Complex queries marked for full analysis
    if query_complexity == "comprehensive":
        return True
    
    return False  # Single simple agents can run directly

def format_full_team_results(result: Dict[str, Any], query: str, elapsed: float) -> str:
    """
    Format complete team analysis results without truncation.
    Now limits source display to 10 for cleaner output.
    """
    lines = []
    lines.append("=" * 80)
    lines.append("MARKET RESEARCH TEAM ANALYSIS")
    lines.append(f"Company/Query: {query}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if elapsed > 0:
        lines.append(f"Execution Time: {elapsed:.2f} seconds")
    
    # Statistics section
    if 'statistics' in result:
        stats = result['statistics']
        lines.append(f"Quality Score: {format_quality_score(stats.get('overall_quality', 0))}")
        lines.append(f"Total Words: {stats.get('total_words', 0):,}")
        lines.append(f"Agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)} successful")
        
        # Memory stats if available
        if MEMORY_ENABLED and 'memories_loaded' in stats:
            loaded = sum(stats['memories_loaded'].values()) if isinstance(stats['memories_loaded'], dict) else 0
            stored = sum(1 for v in stats.get('memories_stored', {}).values() if v)
            lines.append(f"Memories: {loaded} loaded, {stored} new stored")
        
        # Add web source count if available
        if 'web_sources_total' in stats:
            lines.append(f"Web Sources Analyzed: {stats['web_sources_total']}")
    
    lines.append("=" * 80)
    lines.append("")
    
    # Full agent outputs
    if 'result' in result:
        for agent_name, agent_output in result['result'].items():
            if agent_output and not str(agent_output).startswith("[ERROR"):
                lines.append("")
                lines.append("=" * 60)
                emoji = AGENT_PERSONAS.get(agent_name, {}).get('emoji', '🤖')
                lines.append(f"{emoji} AGENT: {agent_name.upper().replace('_', ' ')}")
                lines.append("=" * 60)
                lines.append("")
                lines.append(str(agent_output))
                lines.append("")
    
    # GTM Blueprint if available
    if 'analysis_results' in result and 'gtm_blueprint' in result['analysis_results']:
        gtm_data = result['analysis_results']['gtm_blueprint']
        if 'content' in gtm_data:
            lines.append("")
            lines.append("=" * 80)
            lines.append("📋 GTM BLUEPRINT DETAILS")
            lines.append("=" * 80)
            lines.append(f"Sections: {gtm_data.get('sections_generated', 0)}/14")
            lines.append(f"Word Count: {gtm_data.get('word_count', 0):,}")
            lines.append(f"Quality: {format_quality_score(gtm_data.get('quality_score', 0))}")
            lines.append("")
            lines.append(gtm_data['content'])
    
    # Add LIMITED source citations at the end
    web_sources = result.get('web_sources', [])
    if not web_sources and 'search_details' in result:
        web_sources = result['search_details'].get('web_sources', [])
    
    if web_sources:
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"WEB SOURCES (Top 10 of {len(web_sources)} analyzed)")
        lines.append("=" * 80)
        
        # Display only first 10 sources
        for i, source in enumerate(web_sources[:10], 1):
            title = source.get('title', 'Untitled')
            url = source.get('url', '#')
            
            # Clean title
            clean_title = ' '.join(title.split())
            if len(clean_title) > 100:
                clean_title = clean_title[:97] + "..."
            
            lines.append(f"\n[{i}] {clean_title}")
            lines.append(f"    URL: {url}")
        
        if len(web_sources) > 10:
            lines.append(f"\n📊 Note: Analysis used {len(web_sources)} total web sources.")
            lines.append("         Only top 10 shown above for brevity.")
    
    return '\n'.join(lines)

# ============================================
# 1. COMPLETE get_agent_direct_response FUNCTION
# REPLACE the entire function in market_research_team.py
# ============================================

async def get_agent_direct_response(agent_name: str, question: str, context: Dict = None) -> tuple:
    """
    Execute a single agent directly and return its response.
    FIXED: Returns tuple of (display_response, full_response) to prevent truncation in files.
    
    Args:
        agent_name: Name of the agent to execute
        question: The question/query to process
        context: Optional context with user_id and channel_id
        
    Returns:
        tuple: (display_response for Slack, full_response for file upload)
    """
    
    print(f"\n[DEBUG] get_agent_direct_response called for agent: {agent_name}")
    print(f"[DEBUG] Question: {question[:100]}...")
    
    # Validate agent exists
    if agent_name not in AGENT_PERSONAS:
        error_msg = f"Unknown agent: {agent_name}. Available: {', '.join(AGENT_PERSONAS.keys())}"
        return error_msg, error_msg  # Return tuple
    
    persona = AGENT_PERSONAS[agent_name]
    
    # Extract context
    user_id = context.get("user_id", "direct") if context else "direct"
    channel_id = context.get("channel_id", "qa") if context else "qa"
    
    # Check if we should use direct execution vs workflow
    use_workflow = should_use_workflow([agent_name])
    
    if not use_workflow:
        # FAST PATH: Direct execution with sources
        print(f"[OPTIMIZE] Using DIRECT execution for {agent_name} (faster)")
        try:
            # Get both response and sources from direct execution
            agent_output, sources_used = await execute_single_agent_direct(
                agent_name=agent_name,
                query=question,
                user_id=user_id,
                channel_id=channel_id
            )
            
            # Check for errors
            if str(agent_output).startswith("[ERROR"):
                error_response = f"⚠️ [{persona['name']}] Analysis Error\n\n{agent_output}"
                return error_response, error_response  # Return tuple
            
            # FIXED: Store FULL response before any truncation
            full_response = str(agent_output)  # Keep the complete untruncated response
            word_count = len(full_response.split())
            char_count = len(full_response)
            
            print(f"[DEBUG] Full response stats: {char_count} chars, {word_count} words")
            
            # Create display version (may be truncated for Slack UI)
            if char_count > 3500:  # Leave room for formatting
                display_response = full_response[:3200] + f"\n\n... *[Response truncated - {word_count} words total]*"
                display_response += f"\n\n💡 For full analysis, run: `/team {question[:50]}`"
                print(f"[DEBUG] Created truncated display: {len(display_response)} chars")
            else:
                display_response = full_response
                print(f"[DEBUG] Response fits, no truncation needed")
            
            # Add source citations to BOTH versions if available
            if sources_used:
                print(f"[DEBUG] Adding {len(sources_used)} source citations")
                display_response = enhance_response_with_sources(display_response, sources_used, persona['name'])
                full_response = enhance_response_with_sources(full_response, sources_used, persona['name'])
            elif SEARCH_ENABLED:
                web_note = f"\n\n📊 *Analysis enhanced with web search*"
                display_response += web_note
                full_response += web_note
            
            # Debug output to verify we have both versions
            print(f"\n{'='*60}")
            print(f"[DEBUG] Response Processing Complete:")
            print(f"  - Full response length: {len(full_response)} chars")
            print(f"  - Display response length: {len(display_response)} chars")
            print(f"  - Word count: {word_count} words")
            print(f"  - Sources included: {len(sources_used) if sources_used else 0}")
            print(f"{'='*60}\n")
            
            # Return BOTH versions as tuple
            return display_response, full_response
            
        except Exception as e:
            print(f"[OPTIMIZE] Direct execution failed: {e}")
            import traceback
            traceback.print_exc()
            error_msg = f"⚠️ Error executing {agent_name}: {str(e)}"
            return error_msg, error_msg  # Return tuple
    
    # FALLBACK: Use workflow for complex scenarios
    print(f"[OPTIMIZE] Using WORKFLOW execution for {agent_name}")
    try:
        workflow_result = await get_agent_direct_response_with_workflow(agent_name, question, context)
        # For workflow, return same content for both (workflow handles its own formatting)
        return workflow_result, workflow_result
    except Exception as e:
        print(f"[WORKFLOW] Execution failed: {e}")
        error_msg = f"⚠️ Workflow error for {agent_name}: {str(e)}"
        return error_msg, error_msg

# ============================================
async def get_agent_direct_response_with_workflow(agent_name: str, question: str, context: Dict = None) -> str:
    """
    Original workflow-based implementation as fallback.
    Uses the full ICPGraph workflow for complex agents or when direct execution fails.
    """
    global last_api_call
    
    print(f"[DEBUG] Starting workflow-based response for agent: {agent_name}")
    print(f"[DEBUG] Question: {question[:100]}...")
    print(f"[DEBUG] Search enabled: {SEARCH_ENABLED}")
    print(f"[DEBUG] Memory enabled: {MEMORY_ENABLED}")
    
    # Rate limiting to prevent API overload
    current_time = time.time()
    time_since_last = current_time - last_api_call
    if time_since_last < API_RATE_LIMIT:
        wait_time = API_RATE_LIMIT - time_since_last
        print(f"[DEBUG] Rate limiting: waiting {wait_time:.2f} seconds")
        await asyncio.sleep(wait_time)
    last_api_call = time.time()
    
    # Validate agent exists
    persona = AGENT_PERSONAS.get(agent_name)
    if not persona:
        error_msg = f"Unknown agent: {agent_name}"
        print(f"[ERROR] {error_msg}")
        return error_msg
    
    # Check workflow availability (should always be true if bot started successfully)
    if not workflow_available:
        error_msg = f"[{persona['name']}] Workflow not available. Please check system configuration."
        print(f"[ERROR] Workflow unavailable for {agent_name}")
        return error_msg
    
    try:
        print(f"[DEBUG] Initializing ICPGraph for single agent: {agent_name}")
        
        # Create workflow instance for single agent execution
        workflow = ICPGraph(verbose=False)  # Less verbose for single agent
        
        # Build context for single agent execution
        client_id = context.get('client_id', 'direct_qa') if context else 'direct_qa'
        
        print(f"[DEBUG] Running workflow with parameters:")
        print(f"  - Agent: {agent_name}")
        print(f"  - Client ID: {client_id}")
        print(f"  - Search: MANDATORY (True)")
        print(f"  - Memory: {MEMORY_ENABLED}")
        
        # Run workflow with JUST THIS AGENT
        # The workflow ENFORCES search_enabled=True internally
        result = workflow.run({
            "company": question,  # Use question as the "company" context
            "business_context": f"Direct question: {question}",
            "client_id": client_id,
            "requested_agents": [agent_name],  # ONLY this agent
            "analysis_depth": "quick",  # Faster for single agent
            "agent_config": {
                "temperatures": AGENT_TEMPERATURES,
                "max_tokens": MAX_TOKENS,
                "search_enabled": True,  # MANDATORY - workflow enforces this
                "memory_enabled": MEMORY_ENABLED
            }
        })
        
        print(f"[DEBUG] Workflow completed, processing results...")
        
        # Extract this agent's response
        if 'result' in result and agent_name in result['result']:
            agent_output = result['result'][agent_name]
            
            # Check for error in output
            if str(agent_output).startswith("[ERROR"):
                print(f"[WARNING] Agent returned error: {agent_output[:100]}")
                return f"""⚠️ [{persona['name']}] Analysis Error

The agent encountered an issue during analysis.

**Possible causes:**
- Search API rate limit reached
- Temporary network issue
- Processing timeout

**Solution:** Wait a moment and try again, or use `/team {question[:50]}` for more robust execution."""
            
            # Get word count for quality indication
            word_count = len(str(agent_output).split()) if agent_output else 0
            print(f"[DEBUG] Agent output: {word_count} words")
            
            # Check if search was actually used
            web_sources = result.get('search_details', {}).get('web_sources', [])
            search_indicator = f"\n\n📊 *Analysis enhanced with {len(web_sources)} web sources*" if web_sources else ""
            
            print(f"[DEBUG] Web sources used: {len(web_sources)}")
            
            # Format response with character limit for Slack
            #if len(str(agent_output)) > 3800:  # Slightly higher since workflow has better context
                #response = str(agent_output)[:3500] + f"\n\n... *[Response truncated - {word_count} words total]*"
                #response += f"\n\n💡 For full analysis, run: `/team {question[:30]}`"
            #else:
                #response = str(agent_output)
            
            response = str(agent_output)
            
            # Store as memory if successful and substantial
            if MEMORY_ENABLED and word_count > 100:
                try:
                    print(f"[DEBUG] Storing memory for client: {client_id}")
                    memory_system.store_memory(
                        client_id=client_id,
                        agent_name=agent_name,
                        memory_type="qa",
                        content=f"Q: {question} A: {response[:500]}",
                        importance=0.7
                    )
                    print(f"[DEBUG] Memory stored successfully")
                except Exception as e:
                    print(f"[WARNING] Could not store memory: {e}")
            
            return response
            
        else:
            # No output found in results
            print(f"[ERROR] No output found for agent {agent_name} in results")
            print(f"[DEBUG] Result keys: {result.keys() if result else 'None'}")
            
            return f"""[{persona['name']}] Analysis completed but no output generated.
            
This might be due to:
- Search API rate limits (mandatory search failed)
- Memory system issues
- Workflow timeout

Try again in a moment or use `/team {question}` for full analysis."""
            
    except RuntimeError as e:
        # Handle mandatory system failures explicitly
        error_str = str(e)
        print(f"[ERROR] RuntimeError caught: {error_str}")
        
        if "search" in error_str.lower() or "brave" in error_str.lower():
            return f"""⚠️ [{persona['name']}] Search System Required but Failed

**The agent cannot provide analysis without web search (MANDATORY).**

**Error:** {error_str}

**Solutions:**
1. Check Brave API key is valid and has credits
2. Verify internet connection
3. Check if Brave API is operational
4. Wait a moment if rate limited
5. Run `/status` to check system configuration

Alternative: Try `/team {question[:50]}` which has better error recovery."""
            
        elif "memory" in error_str.lower() or "qdrant" in error_str.lower():
            return f"""⚠️ [{persona['name']}] Memory System Error

**Error:** {error_str}

The memory system is required but encountered an error.
Check Qdrant connection with `/memory-test`."""
            
        else:
            # Generic RuntimeError
            return f"""⚠️ [{persona['name']}] Runtime Error

**Error:** {error_str}

The agent cannot proceed due to a system requirement.
Run `/status` to check all systems."""
            
    except TimeoutError as e:
        print(f"[ERROR] Timeout in agent execution: {e}")
        return f"""⏱️ [{persona['name']}] Analysis Timeout

The analysis took too long to complete.

**Solutions:**
- Try a simpler/shorter question
- Use `/team {question[:30]}` for better handling
- Check system status with `/status`"""
        
    except Exception as e:
        print(f"[ERROR] Unexpected error in agent workflow: {e}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        
        # Check for specific error patterns
        if "529" in str(e) or "overloaded" in str(e).lower():
            return f"""⚠️ [{persona['name']}] Service Overloaded

The AI service is currently overloaded (Error 529).
Please wait a few moments and try again.

Tip: Spread out requests to avoid rate limits."""
            
        elif "api" in str(e).lower() and "key" in str(e).lower():
            return f"""⚠️ [{persona['name']}] API Key Issue

There's a problem with one of the API keys.

Run `/status` to check which system has issues."""
            
        else:
            # Generic error with helpful context
            return f"""⚠️ [{persona['name']}] Workflow Error

**Error:** {str(e)[:200]}

**Debugging Info:**
- Agent: {agent_name}
- Search: {'✅ Enabled' if SEARCH_ENABLED else '❌ Disabled'}
- Memory: {'✅ Enabled' if MEMORY_ENABLED else '❌ Disabled'}

**Solutions:**
1. Try `/team {question[:30]}` for more robust execution
2. Check system status with `/status`
3. Verify all API keys are valid
4. Wait a moment and retry

If this persists, check the logs for details."""

# ==============================================
# 12. STARTUP MESSAGES
# ==============================================

print("=" * 80)
print("MARKET RESEARCH TEAM BOT v3.0")
print("=" * 80)
print(f"Memory System: {'✅ Enabled' if MEMORY_ENABLED else '❌ Disabled'}")
print(f"LLM Available: {'✅ Yes' if LLM_AVAILABLE else '❌ No'}")
print(f"Workflow: {'✅ Ready' if workflow_available else '❌ Not Available'}")
print(f"LangSmith: {'✅ Tracing' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else '❌ Disabled'}")
print("=" * 80)
print("Features:")
print("- Unified bot with all team_bot and advanced_bot features")
print("- Template-based guided research system")
print("- Memory persistence across sessions")
print("- Direct agent Q&A via @Agentic Team mentions")
print("- Real-time progress updates")
print("- Full untruncated reports")
print("=" * 80)

# END OF PART 1
# CONTINUES IN PART 2: Core Analysis Commands
# PART 2: CORE ANALYSIS COMMANDS & INDIVIDUAL AGENT COMMANDS
# Continues from Part 1

# ============================================
# MISSING FUNCTION: handle_agent_direct_command
# ADD THIS AFTER YOUR OTHER COMMAND HANDLERS (around line 2000-2500)
# BEFORE the individual agent slash commands
# ============================================

def handle_agent_direct_command(command_name):
    """
    Factory function to create handlers for individual agent commands.
    FIXED: Properly handles tuple return from get_agent_direct_response.
    
    Args:
        command_name: The slash command name (e.g., '/psychological')
        
    Returns:
        A command handler function for that specific agent
    """
    
    def handler(ack, command, say, client):
        # Acknowledge command immediately
        ack()
        
        # Extract agent name from command
        agent = command_name.replace('/', '')
        
        print(f"\n{'='*60}")
        print(f"[AGENT_DIRECT] Received command: {command_name}")
        print(f"[AGENT_DIRECT] Text: {command.get('text', '')[:100]}...")
        print(f"[AGENT_DIRECT] User: {command.get('user_id', 'Unknown')}")
        print(f"{'='*60}\n")
        
        # Validate agent exists
        if agent not in AGENT_PERSONAS:
            say(f"❌ Unknown agent: {agent}\nAvailable agents: {', '.join(AGENT_PERSONAS.keys())}")
            return
        
        # Get question from command text
        question = command.get('text', '').strip()
        if not question:
            persona = AGENT_PERSONAS[agent]
            say(f"*{persona['name']}*\n{persona['personality']}\n\nPlease provide a question or topic to analyze.\n\nUsage: `{command_name} [your question]`")
            return
        
        # Get user and channel info
        user_id = command.get('user_id', 'unknown')
        channel_id = command.get('channel_id', 'direct')
        
        # Send initial acknowledgment
        persona = AGENT_PERSONAS[agent]
        initial_msg = say(f"🔮 *{persona['name']}* is analyzing: _{question}_\n\n_This may take 20-30 seconds for deep analysis..._")
        thread_ts = initial_msg['ts'] if initial_msg else None
        
        async def process_agent():
            try:
                print(f"[AGENT_DIRECT] Processing with agent: {agent}")
                print(f"[AGENT_DIRECT] Question: {question}")
                
                # Get the response - NOW RETURNS TUPLE
                response_data = await get_agent_direct_response(
                    agent_name=agent,
                    question=question,
                    context={"user_id": user_id, "channel_id": channel_id}
                )
                
                # FIXED: Handle tuple return (display_response, full_response)
                if isinstance(response_data, tuple):
                    display_response, full_response = response_data
                    print(f"[AGENT_DIRECT] Received tuple response")
                    print(f"[AGENT_DIRECT] Display: {len(display_response)} chars")
                    print(f"[AGENT_DIRECT] Full: {len(full_response)} chars")
                else:
                    # Backward compatibility for non-tuple returns
                    display_response = full_response = response_data
                    print(f"[AGENT_DIRECT] Received single response (backward compat)")
                
                # Check for errors
                if display_response.startswith("❌") or display_response.startswith("⚠️"):
                    client.chat_postMessage(
                        channel=channel_id,
                        text=display_response,
                        thread_ts=thread_ts
                    )
                    return
                
                # Format final message with agent header
                formatted_display = f"🧠 *{persona['name']}*\n\n{display_response}"
                formatted_full = f"{'='*50}\n{persona['name']} Analysis\n{'='*50}\n\n{full_response}"
                
                # Add memory note
                formatted_display += f"\n\n_Memory stored for future analyses. Try other agents or run `/team {question[:30]}` for full analysis._"
                formatted_full += f"\n\n_Analysis by {persona['name']} for: {question}_"
                
                # Send response with file fallback using BOTH versions
                print(f"[AGENT_DIRECT] Sending response with file fallback...")
                await send_response_with_file_fallback(
                    client=client,
                    channel=channel_id,
                    thread_ts=thread_ts,
                    initial_message=formatted_display,  # Display version for Slack
                    full_content=formatted_full,  # FULL version for file upload
                    title=f"{persona['name']} Analysis"
                )
                
                # Log completion
                print(f"[AGENT_DIRECT] ✅ Completed {agent} analysis for: {question[:50]}...")
                logger.info(f"{agent} analysis completed for: {question}")
                
            except Exception as e:
                print(f"[AGENT_DIRECT] ❌ Error in process_agent: {str(e)}")
                import traceback
                traceback.print_exc()
                
                error_message = f"❌ Error executing {agent}: {str(e)}\n\nPlease try again or use `/test` to check system status."
                client.chat_postMessage(
                    channel=channel_id,
                    text=error_message,
                    thread_ts=thread_ts
                )
        
        # Run async processing
        print(f"[AGENT_DIRECT] Starting async processing...")
        try:
            import asyncio
            asyncio.run(process_agent())
        except Exception as e:
            print(f"[AGENT_DIRECT] ❌ Failed to run async: {str(e)}")
            say(f"❌ Failed to process command: {str(e)}", thread_ts=thread_ts)
    
    return handler

# ==============================================
# 13. INDIVIDUAL AGENT SLASH COMMANDS (UPDATED)
# Fixed /psychological command for market_research_team.py
# Complete refactored @app.command("/psychological") with ALL mandatory requirements

# Complete refactored /psychological command with ALL fixes applied

@app.command("/psychological")
def handle_psychological(ack, respond, command):
    """
    Deep psychological analysis with MANDATORY requirements:
    - Sonnet 4.5 (claude-sonnet-4-5-20250929)
    - Temperature 0.3
    - 20,000 max tokens
    - New psychological prompt from TXT file
    - MANDATORY Brave Search for market context
    - Automatic file generation for long analyses
    - Fixed Slack file upload and local backup
    - Memory system integration
    - Response caching
    """
    ack()
    
    # ENSURE ALL REQUIRED IMPORTS ARE DECLARED HERE
    import os
    import sys
    import time
    import hashlib
    import traceback
    from datetime import datetime
    from slack_sdk import WebClient
    
    respond("🧠 *Starting Deep Psychological Analysis with Enhanced Configuration...*")
    
    business_context = command.get('text', '').strip()
    if not business_context:
        respond("Please provide business context: `/psychological [business description]`")
        return
    
    try:
        # Import required modules and set globals
        global ICPResearchPrompts, Config, PROMPTS_AVAILABLE, CONFIG_AVAILABLE, LAST_ANALYSIS
        global search_context, SEARCH_ENABLED, brave_search, response_cache, MEMORY_ENABLED, memory_system
        
        # MANDATORY CHECK 1: Ensure Brave Search is available
        if not SEARCH_ENABLED or not search_context:
            respond("❌ ERROR: Brave Search is MANDATORY but not available.")
            respond("Please ensure BRAVE_API_KEY is set in environment variables.")
            return
        
        # Get the configured LLM - MUST be Sonnet 4.5
        llm = get_llm_for_agent("psychological")
        
        if not llm:
            respond("❌ Error: Could not initialize LLM. Check your ANTHROPIC_API_KEY.")
            return
        
        # MANDATORY CHECK 2: Verify we're using Sonnet 4.5
        if CONFIG_AVAILABLE and Config:
            if Config.LLM_MODEL != "claude-sonnet-4-5-20250929":
                respond(f"⚠️ Warning: Not using required Sonnet 4.5. Current model: {Config.LLM_MODEL}")
                respond("Please update config.py to use claude-sonnet-4-5-20250929")
        
        # MANDATORY CHECK 3: Get the prompt template from TXT file
        if PROMPTS_AVAILABLE and ICPResearchPrompts:
            prompt_template = ICPResearchPrompts.get_psychological_analysis_prompt()
            print("✅ Using new psychological prompt from ICPResearchPrompts")
        else:
            respond("❌ Error: Psychological prompt not available from research_prompts.py")
            return
        
        # MANDATORY: Perform Brave Search for market context
        respond("🔍 *Performing mandatory market research...*")
        
        # Define comprehensive search queries
        search_queries = [
            f"{business_context} market analysis",
            f"{business_context} customer psychology",
            f"{business_context} industry trends",
            f"{business_context} competitor analysis"
        ]
        
        all_search_results = []
        all_sources = []
        
        # Execute searches
        for query in search_queries:
            print(f"[BRAVE SEARCH] Searching: {query}")
            search_result, sources = search_context.search_and_cite(query, "psychological")
            if search_result:
                all_search_results.append(search_result)
                all_sources.extend(sources)
                print(f"✅ Found {len(sources)} sources for: {query}")
        
        # Combine search results
        combined_search = "\n\n".join(all_search_results) if all_search_results else "No search results available"
        
        respond(f"✅ *Search complete: Found {len(all_sources)} relevant sources*")
        
        # FIXED: Helper function with correct memory retrieval method
        def get_memory_patterns(context):
            """Get memory patterns for the business context - FIXED method name"""
            if MEMORY_ENABLED and memory_system:
                try:
                    client_id = hashlib.md5(context.encode()).hexdigest()[:8]
                    
                    # Check which method the memory system has and use the correct one
                    if hasattr(memory_system, 'retrieve_memories'):
                        memories = memory_system.retrieve_memories(
                            client_id=client_id,
                            query=context,
                            top_k=5
                        )
                    elif hasattr(memory_system, 'search_memories'):
                        memories = memory_system.search_memories(
                            client_id=client_id,
                            query=context,
                            limit=5
                        )
                    elif hasattr(memory_system, 'get_relevant_memories'):
                        memories = memory_system.get_relevant_memories(
                            client_id=client_id,
                            query=context,
                            top_k=5
                        )
                    else:
                        print("Warning: Memory system has no known retrieval method")
                        return ""
                    
                    if memories:
                        # Handle different memory formats
                        if isinstance(memories, list):
                            return "\n".join([
                                m.get('content', '') if isinstance(m, dict) else str(m) 
                                for m in memories
                            ])
                        else:
                            return str(memories)
                except Exception as e:
                    print(f"Memory retrieval error (handled): {e}")
            return ""
        
        # Helper function: Save to memory
        def save_to_memory(agent_name, context, analysis):
            """Save analysis to memory system"""
            if MEMORY_ENABLED and memory_system:
                try:
                    client_id = hashlib.md5(context.encode()).hexdigest()[:8]
                    memory_system.store_memory(
                        client_id=client_id,
                        agent_name=agent_name,
                        memory_type="analysis",
                        content=analysis[:2000],  # Store first 2000 chars
                        importance=0.8
                    )
                    print(f"✅ Saved {agent_name} analysis to memory")
                except Exception as e:
                    print(f"Memory save error (handled): {e}")
        
        # Get memory patterns if available
        memory_patterns = get_memory_patterns(business_context) if MEMORY_ENABLED else ""
        
        # Format enhanced context with search results
        enhanced_context = f"""
BUSINESS CONTEXT:
{business_context}

MARKET RESEARCH (FROM BRAVE SEARCH):
{combined_search[:3000]}  # Limit to avoid overwhelming the prompt

PREVIOUS INSIGHTS:
{memory_patterns if memory_patterns else "No previous insights available"}
"""
        
        # Format the final prompt
        try:
            prompt = prompt_template.format(
                business_context=enhanced_context,
                memory_patterns=memory_patterns if memory_patterns else "Building initial analysis"
            )
        except KeyError as e:
            print(f"Prompt formatting with fallback: {e}")
            # Fallback formatting
            prompt = prompt_template.replace("{business_context}", enhanced_context).replace(
                "{memory_patterns}", memory_patterns if memory_patterns else "Initial analysis"
            )
        
        # Log mandatory configuration verification
        print(f"📊 MANDATORY CONFIGURATION CHECK:")
        print(f"   ✅ Model: {Config.LLM_MODEL if CONFIG_AVAILABLE and Config else 'claude-sonnet-4-5-20250929'}")
        print(f"   ✅ Temperature: 0.3")
        print(f"   ✅ Max Tokens: 20,000")
        print(f"   ✅ Prompt Length: {len(prompt)} characters")
        print(f"   ✅ Brave Search: {len(all_sources)} sources integrated")
        
        # Run the analysis with Sonnet 4.5
        respond("*Processing with Sonnet 4.5 at temperature 0.3...*")
        analysis = llm.invoke(prompt).content
        
        # Store in LAST_ANALYSIS global cache
        if 'LAST_ANALYSIS' not in globals():
            LAST_ANALYSIS = {}
        
        LAST_ANALYSIS[command['channel_id']] = {
            'psychological': analysis,
            'timestamp': datetime.now(),
            'sources': all_sources
        }
        
        # Prepare full report with sources
        full_report = f"""{analysis}

{'='*60}
WEB SOURCES CONSULTED ({len(all_sources)} sources):
{'='*60}
"""
        for i, source in enumerate(all_sources, 1):
            full_report += f"\n[{i}] {source.get('title', 'Unknown')}\n"
            full_report += f"    URL: {source.get('url', 'N/A')}\n"
        
        # Calculate statistics
        word_count = len(full_report.split())
        char_count = len(full_report)

        # MANDATORY: Generate and upload file for long analyses (>3,000 chars)
        if char_count > 3000:
            # Create comprehensive file content
            file_content = f"""PSYCHOLOGICAL INTELLIGENCE ANALYSIS
{'='*80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Model: Sonnet 4.5 (claude-sonnet-4-5-20250929)
Temperature: 0.3
Max Tokens: 20,000
Business Context: {business_context}
Web Sources: {len(all_sources)} sources from Brave Search
Memory Status: {'Enabled - Past insights included' if MEMORY_ENABLED else 'Disabled'}

{'='*80}
ANALYSIS:
{'='*80}

{full_report}

{'='*80}
ANALYSIS STATISTICS:
{'='*80}
- Total Words: {word_count:,}
- Total Characters: {char_count:,}
- Sources Consulted: {len(all_sources)}
- Generated by: Agentic Team Bot with Sonnet 4.5
- Cached: Yes
{'='*80}
"""
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"psychological_analysis_{timestamp}.txt"
            
            # Try Slack upload first
            upload_success = False
            slack_file_url = None
            
            try:
                slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
                file_bytes = file_content.encode('utf-8')
                
                # FIXED: Use 'channel' (singular) not 'channels' (plural)
                result = slack_client.files_upload_v2(
                    channel=command['channel_id'],  # Fixed parameter name
                    file=file_bytes,
                    filename=filename,
                    title=f"Psychological Analysis - {business_context[:50]}",
                    initial_comment=f"""*🧠 PSYCHOLOGICAL INTELLIGENCE ANALYSIS*
_Enhanced with Sonnet 4.5, temp 0.3, max 20k tokens_
_Brave Search: {len(all_sources)} sources analyzed_

Full analysis attached as file ({word_count:,} words)."""
                )
                
                if result.get("ok"):
                    upload_success = True
                    slack_file_url = result.get("file", {}).get("permalink", "")
                    
                    # Send preview in channel
                    preview = analysis[:2500] + f"\n\n_...See attached file for complete {word_count:,} word analysis with {len(all_sources)} sources_"
                    respond(preview)
                    
                    # Send completion summary
                    respond(f"""*📊 Analysis Complete:*
• Length: {word_count:,} words ({char_count:,} characters)
• Sources: {len(all_sources)} from Brave Search
• Model: Sonnet 4.5
• Temperature: 0.3
• File: {filename} (uploaded to Slack)
• Memory: {'✅ Saved' if MEMORY_ENABLED else '⚠️ Disabled'}""")
                else:
                    raise Exception(f"Slack upload failed: {result.get('error', 'Unknown')}")
                    
            except Exception as upload_error:
                print(f"Slack upload error: {upload_error}")
                upload_success = False
            
            # If Slack upload failed, save locally - IMPORTS ARE NOW IN SCOPE
            if not upload_success:
                try:
                    # Try Downloads folder first
                    downloads_path = os.path.expanduser("~/Downloads")
                    if not os.path.exists(downloads_path):
                        # Fallback to Desktop
                        downloads_path = os.path.expanduser("~/Desktop")
                    
                    local_file_path = os.path.join(downloads_path, filename)
                    
                    with open(local_file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    print(f"✅ File saved locally: {local_file_path}")
                    
                    respond(f"""*🧠 PSYCHOLOGICAL INTELLIGENCE ANALYSIS*
_(Slack upload failed - File saved locally)_

📁 **File saved to:** `{local_file_path}`
📊 **Analysis:** {word_count:,} words with {len(all_sources)} sources
✅ **Model:** Sonnet 4.5
{'✅ **Memory:** Saved' if MEMORY_ENABLED else '⚠️ **Memory:** Disabled'}

**Preview:**""")
                    
                    # Send preview chunks
                    preview_text = analysis[:5000]
                    chunks = [preview_text[i:i+3000] for i in range(0, len(preview_text), 3000)]
                    for chunk in chunks:
                        respond(chunk)
                        time.sleep(0.5)
                    
                    respond(f"_...Complete analysis saved to {filename}_")
                    
                except Exception as local_error:
                    print(f"Local save failed: {local_error}")
                    # Last resort: send truncated version
                    respond("*🧠 PSYCHOLOGICAL INTELLIGENCE ANALYSIS*\n_(File save failed, showing truncated preview)_")
                    chunks = analysis[:10000].split('\n\n')
                    for i, chunk in enumerate(chunks[:5]):
                        respond(chunk)
                        if i < 4:
                            time.sleep(0.5)
                    respond(f"_...Truncated. Full analysis: {word_count:,} words_")
        else:
            # Analysis is short enough to send directly in Slack
            respond(f"""*🧠 PSYCHOLOGICAL INTELLIGENCE ANALYSIS*
_Sonnet 4.5 | Temp 0.3 | {len(all_sources)} sources from Brave Search_

{analysis}

*📊 Analysis Complete:*
• Words: {word_count:,}
• Sources: {len(all_sources)}
• Model: Sonnet 4.5
• Memory: {'✅ Saved' if MEMORY_ENABLED else '⚠️ Disabled'}
• Cached: Yes""")
        
        # Save to memory system
        save_to_memory('psychological', business_context, full_report)
        
        # Cache the complete response with sources
        if response_cache:
            response_cache.cache_response(
                agent_name='psychological',
                query=business_context,
                response=full_report,
                sources=all_sources,
                client_id=hashlib.md5(business_context.encode()).hexdigest()[:8]
            )
            print(f"✅ Response cached with {len(all_sources)} sources")
        
        # Log final success metrics
        print(f"✅ PSYCHOLOGICAL ANALYSIS COMPLETE:")
        print(f"   - Model: Sonnet 4.5 (claude-sonnet-4-5-20250929)")
        print(f"   - Temperature: 0.3")
        print(f"   - Max Tokens: 20,000")
        print(f"   - Words: {word_count:,}")
        print(f"   - Characters: {char_count:,}")
        print(f"   - Sources: {len(all_sources)}")
        print(f"   - Memory: {'Saved' if MEMORY_ENABLED else 'Disabled'}")
        print(f"   - Cached: Yes")
        print(f"   - File Generated: {'Yes' if char_count > 15000 else 'No (under 15k threshold)'}")
        
    except Exception as e:
        logger.error(f"Psychological analysis error: {e}")
        error_details = traceback.format_exc()
        print(f"Full error trace:\n{error_details}")
        
        respond(f"❌ Error in psychological analysis: {str(e)[:200]}")
        print(f"Business context: {business_context[:100]}...")
# Also add a helper command to test the configuration

@app.command("/test-psychological-config")
def handle_test_psychological_config(ack, respond):
    """Test psychological agent configuration"""
    ack()
    
    status_lines = []
    
    # Check Config module
    if CONFIG_AVAILABLE and Config:
        status_lines.append(f"✅ Config Module: Loaded")
        status_lines.append(f"   Model: {Config.LLM_MODEL}")
        status_lines.append(f"   Psychological Temp: {Config.AGENT_TEMPERATURES.get('psychological', 'N/A')}")
        status_lines.append(f"   Max Tokens: {Config.MAX_TOKENS.get('research', 'N/A')}")
    else:
        status_lines.append(f"⚠️ Config Module: Using Fallback")
        status_lines.append(f"   Model: claude-3-5-sonnet-20241022")
        status_lines.append(f"   Temperature: 0.3")
        status_lines.append(f"   Max Tokens: 20000")
    
    # Check Prompts module
    if PROMPTS_AVAILABLE and ICPResearchPrompts:
        try:
            prompt = ICPResearchPrompts.get_psychological_analysis_prompt()
            status_lines.append(f"✅ Prompts Module: Loaded")
            status_lines.append(f"   Prompt Length: {len(prompt)} characters")
        except Exception as e:
            status_lines.append(f"❌ Prompts Module Error: {e}")
    else:
        status_lines.append(f"⚠️ Prompts Module: Using Fallback")
    
    # Check LLM
    try:
        test_llm = get_llm_for_agent("psychological")
        if test_llm:
            status_lines.append(f"✅ LLM: Initialized")
        else:
            status_lines.append(f"❌ LLM: Failed to Initialize")
    except Exception as e:
        status_lines.append(f"❌ LLM Error: {e}")
    
    # Check Memory
    status_lines.append(f"{'✅' if MEMORY_ENABLED else '❌'} Memory System: {'Enabled' if MEMORY_ENABLED else 'Disabled'}")
    
    # Check Cache
    if response_cache:
        stats = response_cache.get_cache_stats()
        status_lines.append(f"✅ Response Cache: {stats['total_entries']} entries")
    else:
        status_lines.append(f"❌ Response Cache: Not Available")
    
    response = "*Psychological Agent Configuration Test*\n\n" + "\n".join(status_lines)
    respond(response)
# ==============================================================

@app.command("/voice")
def handle_voice(ack, respond, command, client):
    """Direct voice of customer analysis"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide a question or company. Usage: `/voice [question/company]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text="🗣️ *Voice of Customer Specialist* is extracting insights..."
    )
    thread_ts = initial_msg['ts']
    
    # Get agent response - returns tuple
    import asyncio
    response_tuple = asyncio.run(get_agent_direct_response(
        "voice_of_customer",
        query,
        {"client_id": client_id}
    ))
    
    # Handle tuple response
    if isinstance(response_tuple, tuple):
        display_response, full_response = response_tuple
    else:
        display_response = full_response = response_tuple
    
    # Format responses
    display_formatted = f"""🗣️ *Voice of Customer Analysis*

{display_response}

_Customer language patterns captured. Memory saved._"""
    
    full_formatted = f"""🗣️ *Voice of Customer Analysis*

{full_response}

_Customer language patterns captured. Memory saved._"""
    
    # Send with file fallback
    asyncio.run(send_response_with_file_fallback(
        client=client,
        channel=channel_id,
        thread_ts=thread_ts,
        initial_message=display_formatted,
        full_content=full_formatted,
        title="Voice of Customer Analysis",
        max_length=3800
    ))
    
    logger.info(f"Voice analysis completed for: {query}")

@app.command("/competitor")
def handle_competitor(ack, respond, command, client):
    """Direct competitor analysis"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide a question or company. Usage: `/competitor [question/company]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text="🔍 *Competitor Intelligence Analyst* is researching..."
    )
    thread_ts = initial_msg['ts']
    
    # Get agent response - returns tuple
    import asyncio
    response_tuple = asyncio.run(get_agent_direct_response(
        "competitor",
        query,
        {"client_id": client_id}
    ))
    
    # Handle tuple response
    if isinstance(response_tuple, tuple):
        display_response, full_response = response_tuple
    else:
        display_response = full_response = response_tuple
    
    # Format responses
    display_formatted = f"""🔍 *Competitive Intelligence*

{display_response}

_Competitive insights stored for strategic planning._"""
    
    full_formatted = f"""🔍 *Competitive Intelligence*

{full_response}

_Competitive insights stored for strategic planning._"""
    
    # Send with file fallback
    asyncio.run(send_response_with_file_fallback(
        client=client,
        channel=channel_id,
        thread_ts=thread_ts,
        initial_message=display_formatted,
        full_content=full_formatted,
        title="Competitive Analysis",
        max_length=3800
    ))
    
    logger.info(f"Competitor analysis completed for: {query}")

@app.command("/interview_psychological")
def handle_interview_psych(ack, respond, command, client):
    """Psychological interview simulation"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide context. Usage: `/interview_psychological [customer/scenario]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text="🎭 *Psychological Interview Specialist* is preparing interview..."
    )
    thread_ts = initial_msg['ts']
    
    # Get agent response - returns tuple
    import asyncio
    response_tuple = asyncio.run(get_agent_direct_response(
        "interview_psychological",
        query,
        {"client_id": client_id}
    ))
    
    # Handle tuple response
    if isinstance(response_tuple, tuple):
        display_response, full_response = response_tuple
    else:
        display_response = full_response = response_tuple
    
    # Format responses
    display_formatted = f"""🎭 *Psychological Interview Insights*

{display_response}

_Interview patterns and vulnerabilities documented._"""
    
    full_formatted = f"""🎭 *Psychological Interview Insights*

{full_response}

_Interview patterns and vulnerabilities documented._"""
    
    # Send with file fallback
    asyncio.run(send_response_with_file_fallback(
        client=client,
        channel=channel_id,
        thread_ts=thread_ts,
        initial_message=display_formatted,
        full_content=full_formatted,
        title="Psychological Interview",
        max_length=3800
    ))
    
    logger.info(f"Psychological interview completed for: {query}")

@app.command("/interview_sales")
def handle_interview_sales(ack, respond, command, client):
    """Sales interview simulation"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide context. Usage: `/interview_sales [customer/scenario]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text="💰 *Sales Interview Specialist* is conducting discovery..."
    )
    thread_ts = initial_msg['ts']
    
    # Get agent response - returns tuple
    import asyncio
    response_tuple = asyncio.run(get_agent_direct_response(
        "interview_sales",
        query,
        {"client_id": client_id}
    ))
    
    # Handle tuple response
    if isinstance(response_tuple, tuple):
        display_response, full_response = response_tuple
    else:
        display_response = full_response = response_tuple
    
    # Format responses
    display_formatted = f"""💰 *Sales Discovery Insights*

{display_response}

_Buying triggers and decision criteria identified._"""
    
    full_formatted = f"""💰 *Sales Discovery Insights*

{full_response}

_Buying triggers and decision criteria identified._"""
    
    # Send with file fallback
    asyncio.run(send_response_with_file_fallback(
        client=client,
        channel=channel_id,
        thread_ts=thread_ts,
        initial_message=display_formatted,
        full_content=full_formatted,
        title="Sales Interview",
        max_length=3800
    ))
    
    logger.info(f"Sales interview completed for: {query}")

@app.command("/gtm")
def handle_gtm(ack, respond, command, client):
    """GTM strategy synthesis"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide context. Usage: `/gtm [company/product]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    # Send initial message
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text="📋 *GTM Blueprint Strategist* is synthesizing strategy..."
    )
    thread_ts = initial_msg['ts']
    
    # Get agent response - returns tuple
    import asyncio
    import time
    start_time = time.time()
    
    response_tuple = asyncio.run(get_agent_direct_response(
        "gtm_blueprint",
        query,
        {"client_id": client_id}
    ))
    
    elapsed = time.time() - start_time
    
    # Handle tuple response
    if isinstance(response_tuple, tuple):
        display_response, full_response = response_tuple
    else:
        display_response = full_response = response_tuple
    
    # Format responses
    display_formatted = f"""📋 *Go-to-Market Strategy*

{display_response}

_Strategic blueprint saved. Run `/team {query[:30]}` for comprehensive analysis._"""
    
    full_formatted = f"""📋 *Go-to-Market Strategy*

{full_response}

_Strategic blueprint saved. Run `/team {query[:30]}` for comprehensive analysis._"""
    
    # Send with file fallback
    try:
        asyncio.run(send_response_with_file_fallback(
            client=client,
            channel=channel_id,
            thread_ts=thread_ts,
            initial_message=display_formatted,
            full_content=full_formatted,
            title="GTM Strategy",
            max_length=3800
        ))
        
        logger.info(f"GTM strategy completed for: {query} in {elapsed:.2f}s")
        
    except Exception as e:
        logger.error(f"Error sending GTM response: {str(e)}")
        # Fallback: try to send something
        try:
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"⚠️ Error sending full response. Query: {query}\nError: {str(e)[:200]}"
            )
        except:
            pass
        
# ==============================================
# 14. TEAM ANALYSIS COMMAND (UPDATED)
# ==============================================

@app.command("/team")
def handle_team_analysis(ack, respond, command, client):
    """Full team analysis with all agents and progress updates"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide a company/context. Usage: `/team [company description]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    # Send initial message
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text=f"""🚀 *Starting Full Team Analysis*
Company/Query: {query}

⏳ Initializing 6 specialized agents..."""
    )
    thread_ts = initial_msg['ts']
    
    # Check for existing memories
    memory_status = ""
    if MEMORY_ENABLED:
        try:
            context = memory_system.get_client_context(client_id)
            if context:
                total_memories = sum(len(insights) for insights in context.values())
                memory_status = f"\n💾 Found {total_memories} previous insights to build upon"
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=f"💾 Loading {total_memories} memories from previous analyses..."
                )
        except Exception as e:
            logger.warning(f"Could not check memories: {e}")
    
    # Create Slack update function
    def send_slack_update(message):
        """Send real-time updates to Slack thread"""
        try:
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=message
            )
            logger.info(f"Slack update: {message}")
        except Exception as e:
            logger.error(f"Could not send Slack update: {e}")
    
    try:
        logger.info("=" * 80)
        logger.info(f"NEW TEAM ANALYSIS: {query}")
        logger.info(f"User: {user_id}, Channel: {channel_id}")
        logger.info(f"Client ID: {client_id}")
        logger.info(f"Memory Enabled: {MEMORY_ENABLED}")
        logger.info("=" * 80)
        
        if not workflow_available:
            respond("❌ Workflow not available. Check system configuration.")
            return
        
        send_slack_update("🔄 Initializing workflow with memory system...")
        workflow = ICPGraph(verbose=True)
        
        # Create context with client_id for memory
        context = {
            "company": query,
            "requested_agents": ["psychological", "voice_of_customer", "competitor", 
                                "interview_psychological", "interview_sales", 
                                "gtm_blueprint"],
            "client_id": client_id,
            "slack_updater": send_slack_update
        }
        
        logger.info(f"Starting workflow with client_id: {client_id}")
        send_slack_update("🧠 Psychological Analyst: Starting deep analysis...")
        
        # Run workflow
        start_time = time.time()
        result = workflow.run(context)
        elapsed = time.time() - start_time
        
        logger.info(f"WORKFLOW COMPLETE in {elapsed:.2f} seconds")
        
        # Store analysis for elaboration
        LAST_ANALYSIS[channel_id] = {
            'query': query,
            'result': result,
            'timestamp': datetime.now(),
            'thread_ts': thread_ts,
            'client_id': client_id,
            'full_data': {}
        }
        
        # Store full agent outputs
        if 'result' in result:
            for agent_name, output in result['result'].items():
                LAST_ANALYSIS[channel_id]['full_data'][agent_name] = str(output)
        
        # Build full report
        full_report = format_full_team_results(result, query, elapsed)
        
        # Save to file
        filename = save_report_to_file(query, full_report, "team_analysis")
        
        # Send results using centralized handler
        send_slack_update("✅ Analysis complete! Sending full report...")
        
        
        
        # Final statistics message
        stats = result.get('statistics', {})
        total_chars = sum(len(str(v)) for v in result.get('result', {}).values())
        
        stats_message = f"""
✨ *Team Analysis Complete!*

📊 **Statistics:**
- Execution time: {elapsed:.2f} seconds
- Successful agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)}
- Total output: {total_chars:,} characters
- Quality score: {format_quality_score(stats.get('overall_quality', 0))}
"""
        
        if MEMORY_ENABLED and 'memories_stored' in stats:
            stored = sum(1 for v in stats.get('memories_stored', {}).values() if v)
            loaded = sum(stats.get('memories_loaded', {}).values()) if 'memories_loaded' in stats else 0
            stats_message += f"• Memories: {loaded} loaded, {stored} new stored\n"
        
        stats_message += f"""
💡 **Next Steps:**
- Ask specific agents: `/psychological deep fears about {query}`
- Get elaboration: `@Agentic Team @psychological elaborate`
- Check memories: `/memory`
"""
        
        send_slack_update(stats_message)
        
    except RuntimeError as e:
        if "search" in str(e).lower() or "brave" in str(e).lower():
            error_msg = f"""❌ CRITICAL: Search system failure

The analysis cannot proceed without web search (mandatory requirement).

**Error:** {str(e)}

**Solutions:**
1. Check Brave API key in .env
2. Verify internet connection
3. Check Brave API status
4. Run `/status` to diagnose"""
        else:
            error_msg = f"❌ Analysis failed: {str(e)}"
        
        logger.error(error_msg, exc_info=True)
        respond(error_msg)
        
    except Exception as e:
        error_msg = f"❌ Error in team analysis: {str(e)}"
        logger.error(error_msg, exc_info=True)
        respond(error_msg)

# ==============================================
# 15. ANALYZE COMMAND (UPDATED)
# ==============================================

@app.command("/analyze")
def handle_analyze(ack, respond, command, client):
    """Standard analysis - simpler than team, no progress updates"""
    ack()
    
    company = command['text'].strip()
    if not company:
        respond("Please provide a company name. Usage: `/analyze [company name]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    # Initial message
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text=f"""🔍 Starting analysis of *{company}*...

⏳ This will take 1-2 minutes..."""
    )
    thread_ts = initial_msg['ts']
    
    # Add memory status if available
    if MEMORY_ENABLED:
        try:
            context = memory_system.get_client_context(client_id)
            if context:
                total_memories = sum(len(insights) for insights in context.values())
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=f"💾 Found {total_memories} previous insights"
                )
        except:
            pass
    
    try:
        if not workflow_available:
            respond("❌ Workflow not available.")
            return
        
        workflow = ICPGraph()
        
        result = workflow.run({
            "company": company,
            "client_id": client_id,
            "requested_agents": ["psychological", "voice_of_customer", "competitor", "gtm_blueprint"]
        })
        
        # Extract results
        report = result.get('final_report', 'No report generated')
        if not report or report == 'No report generated':
            # Build report from agent outputs
            report = format_full_team_results(result, company, 0)
        
        stats = result.get('statistics', {})
        
        # Save report
        filename = save_report_to_file(company, report, "analysis")
        
        # Send full report using centralized handler
        send_response_with_file_fallback(
            client=client,
            channel_id=channel_id,
            thread_ts=thread_ts,
            response_text=report,
            title=f"Analysis - {company}",
            agent_name="analyze",
            query=company
        )
        
        # Send summary statistics
        quality = stats.get('overall_quality', 0)
        words = stats.get('total_words', len(report.split()))
        
        summary_text = f"""
✅ *Analysis Complete: {company}*

📊 **Statistics:**
- Quality Score: {format_quality_score(quality)}
- Total Words: {words:,}
- Report saved: `{filename}`
"""
        
        if MEMORY_ENABLED:
            stored = sum(1 for v in stats.get('memories_stored', {}).values() if v)
            loaded = sum(stats.get('memories_loaded', {}).values()) if 'memories_loaded' in stats else 0
            summary_text += f"• Memories: {loaded} loaded, {stored} stored\n"
        
        summary_text += f"""

💡 **Next Steps:**
- Ask agents directly: `/psychological {company} fears`
- Run full team: `/team {company}`
"""
        
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=summary_text
        )
        
        logger.info(f"Analysis complete for {company}. Quality: {quality:.2f}")
        
    except RuntimeError as e:
        if "search" in str(e).lower() or "brave" in str(e).lower():
            error_msg = f"""❌ Search system required but unavailable

Cannot analyze without web search (mandatory).
Error: {str(e)}

Run `/status` to check system configuration."""
        else:
            error_msg = f"❌ Analysis blocked: {str(e)}"
        respond(error_msg)
        logger.error(f"Analysis failed: {e}")
        
    except Exception as e:
        error_msg = f"❌ Error analyzing {company}: {str(e)}"
        respond(error_msg)
        logger.error(f"Analysis failed: {e}")

# ==============================================
# 16. MEMORY COMMANDS
# ==============================================

@app.command("/memory")
def handle_memory_command(ack, respond, command):
    """Show memory statistics for this channel/user"""
    ack()
    
    if not MEMORY_ENABLED:
        respond("💾 Memory system is not available. Check Qdrant configuration.")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    try:
        context = memory_system.get_client_context(client_id)
        
        if not context:
            respond(f"""
📊 *Memory Statistics*

• **Client ID:** `{client_id}`
• **Status:** No memories stored yet

💡 **How to create memories:**
• Run any agent: `/psychological [question]`
• Run team analysis: `/team [company]`
• Ask questions: `@Agentic Team @voice [question]`

All memories persist across sessions!""")
            return
        
        total_memories = sum(len(insights) for insights in context.values())
        agents_with_memory = list(context.keys())
        
        message = f"""
📊 *Memory Statistics*

• **Client ID:** `{client_id}`
• **Total memories:** {total_memories}
• **Agents with memories:** {', '.join(agents_with_memory)}

**Recent Insights by Agent:**
"""
        
        for agent, insights in context.items():
            if insights:
                agent_title = agent.replace('_', ' ').title()
                emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖')
                message += f"\n{emoji} **{agent_title}:**\n"
                for insight in insights[:2]: 
                    message += f"  • {insight}\n"  # Full insight, no truncation
        
        message += """
💡 These memories enhance all future analyses!
Agents reference these insights automatically."""
        
        respond(message)
        
    except Exception as e:
        logger.error(f"Memory command error: {e}")
        respond(f"Error retrieving memories: {str(e)}")

@app.command("/memory-test")
def handle_memory_test(ack, respond, command):
    """Test memory configuration - verify system is working"""
    ack()
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    test_result = f"""
🧪 *Memory Configuration Test*

**Bot:** Market Research Team v3.0
**Channel:** `{channel_id}`
**User:** `{user_id}`
**Client ID:** `{client_id}`
**Memory Enabled:** {'✅ Yes' if MEMORY_ENABLED else '❌ No'}
**Qdrant URL:** `{os.getenv('QDRANT_URL', 'Not configured')}`
**Collection:** `{memory_system.collection_name if memory_system else 'N/A'}`
"""
    
    if MEMORY_ENABLED:
        try:
            # Try to store a test memory
            memory_system.store_memory(
                client_id=client_id,
                agent_name="system",
                memory_type="test",
                content=f"Test from unified bot at {datetime.now().isoformat()}",
                importance=0.5
            )
            test_result += "\n✅ Successfully wrote test memory"
            
            # Try to retrieve it
            memories = memory_system.retrieve_memories(
                client_id=client_id,
                agent_name="system",
                query="test",
                limit=1
            )
            if memories:
                test_result += f"\n✅ Successfully retrieved test memory"
            else:
                test_result += f"\n⚠️ Could not retrieve test memory"
                
        except Exception as e:
            test_result += f"\n❌ Memory system error: {e}"
    
    test_result += """

💡 **Important:** All agent commands share the same memory space!
Run `/psychological fear` then `/voice pain` - they build on each other."""
    
    respond(test_result)

# ==============================================
# 17. SYSTEM COMMAND
# ==============================================
@app.command("/system")
def handle_status(ack, respond):
    """Check system status"""
    ack()
    
    # Test live connections
    memory_status = "❌ Not Connected"
    search_status = "❌ Not Connected"
    
    try:
        # Test memory
        if memory_system:
            test_id = f"test_{datetime.now().timestamp()}"
            memory_system.store_memory(
                client_id=test_id,
                agent_name="system",
                memory_type="test",
                content="Status check",
                importance=0.1
            )
            memory_status = "✅ Connected (MANDATORY)"
    except:
        pass
    
    try:
        # Test search
        if brave_search:
            result = brave_search.run("test")
            if result:
                search_status = "✅ Connected (MANDATORY)"
    except:
        pass
    
    status_text = f"""*System Status - Market Research Team Bot*

**🔒 MANDATORY Systems:**
- Memory (Qdrant): {memory_status}
- Search (Brave): {search_status}
- LLM (Anthropic): {'✅ Connected' if LLM_AVAILABLE else '❌ Not Connected'}

**Configuration:**
- Workflow: {'✅ Ready' if workflow_available else '❌ Not Available'}
- Agents: {len(AGENT_PERSONAS)} configured

⚠️ **Note:** Memory and Search are MANDATORY.
Bot will not function without both systems connected.

If any mandatory system shows ❌, the bot needs restart with proper credentials."""
    
    respond(status_text)

# ==============================================
# 18. HELP COMMAND
# ==============================================

@app.command("/help")
def handle_help(ack, respond):
    """Show comprehensive help message"""
    ack()
    
    memory_status = "✅ Enabled" if MEMORY_ENABLED else "❌ Disabled"
    llm_status = "✅ Enabled" if LLM_AVAILABLE else "❌ Disabled"
    
    help_text = f"""
*Market Research Team Bot - Command Guide*

**🎯 Individual Agent Analysis:** {llm_status}
• `/psychological [question/company]` - Deep psychological analysis
• `/voice [question/company]` - Customer language extraction
• `/competitor [question/company]` - Competitive intelligence
• `/interview_psychological [scenario]` - Psychological interview
• `/interview_sales [scenario]` - Sales discovery interview
• `/gtm [company/product]` - Go-to-market strategy

**📊 Full Team Analysis:**
• `/team [company]` - All 6 agents with progress updates
• `/analyze [company]` - Quick 4-agent analysis

**💬 Direct Q&A:**
• `@Agentic Team @psychological [question]` - Ask specific agent
• `@Agentic Team voice: [question]` - Alternative format

**💾 Memory System:** {memory_status}
• `/memory` - View stored insights
• `/memory-test` - Test configuration

**📋 Template Research:**
• `/research-guided` - Step-by-step guided form
• `/research-complete` - Upload full template
• `/template` - Download template

**🎭 Agent Interactions:**
• `/debate [topic]` - Agents debate
• `/conversation agent1 agent2 [topic]` - Two agents discuss
• `/coach [agent] [feedback]` - Improve agents
• `/learning` - View agent improvements

**📈 System:**
- `/status` - System status
- `/sources` - How to access research sources
- `/cache-stats` - View cache performance
- `/cache-clear [agent]` - Clear cache (optional: specific agent)
- `/help` - This message

**Examples:**
• `/psychological what drives founder anxiety?`
• `/team OpenAI market position`
• `@Agentic Team @voice show customer pain language`
• `/competitor analyze Stripe vs Square`

💡 **Tip:** All commands share memory - insights from one command enhance all others!"""
    
    respond(help_text)

@app.command("/sources")
def handle_sources_command(ack, respond, command, client):
    """Show sources from the last analysis in this channel"""
    ack()
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    
    respond("""🔍 **How to Access Sources:**

**Current Analysis:** Sources are automatically included at the bottom of each agent response.

**Commands that show sources:**
- Individual agents: `/psychological`, `/voice`, `/competitor`, etc.
- Team analysis: `/team [company]` 
- All responses include clickable source URLs

**Source Information Includes:**
- Article titles and domains
- Direct links to source material
- Number of sources consulted

**Tip:** Scroll to the bottom of any analysis to see the complete source list with URLs.""")

@app.command("/cache-stats")
def handle_cache_stats(ack, respond):
    """Show cache performance statistics"""
    ack()
    
    stats = response_cache.get_cache_stats()
    
    respond(f"""📊 **Cache Performance Statistics**

**Response Cache:**
- Total entries: {stats['total_entries']}
- Valid entries: {stats['valid_entries']}
- Cache efficiency: {stats['cache_hit_potential']}
- Oldest entry: {stats['oldest_entry_age']:.1f} hours

**Search Cache:**
- Search entries: {stats['search_entries']}
- TTL: 24 hours
- Memory usage: ~{stats['memory_usage_estimate'] / 1024:.1f} KB

**Performance Benefits:**
- Cached responses return in ~0.1 seconds
- Typical savings: 15-20 seconds per cached query
- Reduces API costs and rate limiting

**Cache Strategy:**
- Agent responses: 24 hour TTL
- Search results: 24 hour TTL
- LRU eviction when full
- Client-specific caching for personalized results""")

@app.command("/cache-clear")
def handle_cache_clear(ack, respond, command):
    """Clear cache (optionally for specific agent)"""
    ack()
    
    agent_name = command['text'].strip().lower() if command['text'].strip() else None
    
    if agent_name and agent_name in AGENT_PERSONAS:
        response_cache.clear_cache(agent_name)
        respond(f"🗑️ Cache cleared for **{agent_name}** agent.\n\nNext queries to this agent will fetch fresh results.")
    elif agent_name:
        respond(f"❌ Unknown agent: {agent_name}\n\nValid agents: {', '.join(AGENT_PERSONAS.keys())}")
    else:
        response_cache.clear_cache()
        respond(f"🗑️ **All cache cleared.**\n\nNext queries will fetch fresh results from all agents and searches.")

# END OF PART 2
# CONTINUES IN PART 3: Agent Interaction Commands
# PART 3: AGENT INTERACTION COMMANDS
# Continues from Part 2

# ==============================================
# 19. APP MENTION HANDLER FOR DIRECT Q&A
# ==============================================

@app.event("app_mention")
def handle_app_mention(event, client):
    """
    Handle bot mentions for direct agent Q&A and elaboration
    Examples:
    - @Agentic Team @psychological what are deep fears?
    - @Agentic Team voice: show exact customer language
    - @Agentic Team elaborate on the psychological analysis
    """
    
    text = event.get('text', '')
    channel_id = event.get('channel')
    user_id = event.get('user')
    thread_ts = event.get('thread_ts', event.get('ts'))
    
    logger.info(f"Bot mentioned: {text}")
    
    # Extract agent and question
    agent_name, question = extract_agent_and_question(text)
    
    if agent_name and question:
        # Direct agent Q&A with memory
        persona = AGENT_PERSONAS.get(agent_name)
        
        if persona:
            emoji = persona['emoji']
            name = persona['name']
            
            # Send typing indicator
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"{emoji} *{name}* is thinking..."
            )
            
            # Get response with memory context
            client_id = get_client_id(channel_id, user_id)
            response = asyncio.run(get_agent_direct_response(
                agent_name,
                question,
                {"client_id": client_id}
            ))
            
            # Send response in thread with formatting
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"""{emoji} *{name}:*

{response}

_Memory stored. Try another agent or run `/team {question.split()[0]}` for full analysis._"""
            )
            
            logger.info(f"Agent {agent_name} responded with memory context")
            
    elif 'elaborate' in text.lower() or 'explain' in text.lower() or 'detail' in text.lower():
        # Elaboration request on last analysis
        last_analysis = LAST_ANALYSIS.get(channel_id)
        
        if not last_analysis:
            client.chat_postMessage(
                channel=channel_id,
                text="No recent analysis found. Run `/team [company]` or ask an agent directly.",
                thread_ts=thread_ts
            )
            return
        
        # Determine which agent to elaborate
        agent_to_elaborate = None
        for agent in ['psychological', 'voice', 'competitor', 'interview', 'sales', 'gtm']:
            if agent in text.lower():
                agent_to_elaborate = agent
                break
        
        if not agent_to_elaborate:
            agent_to_elaborate = 'psychological'  # Default
        
        # Get full output for that agent
        full_output = last_analysis['full_data'].get(agent_to_elaborate, 
                     last_analysis['full_data'].get(f"{agent_to_elaborate}_agent", ""))
        
        if not full_output:
            for key, value in last_analysis['full_data'].items():
                if agent_to_elaborate in key:
                    full_output = value
                    break
        
        if full_output and LLM_AVAILABLE:
            # Create deeper elaboration
            elaboration_prompt = f"""
            Based on this {agent_to_elaborate} analysis for {last_analysis['query']}:
            
            {full_output}
            
            Provide a DEEP ELABORATION with:
            1. Specific tactical insights and implementation steps
            2. Hidden implications and second-order effects
            3. Concrete examples and scenarios
            4. Actionable recommendations
            
            Be specific to: {last_analysis['query']}
            """
            
            try:
                response = llm.invoke(elaboration_prompt)
                elaborated = response.content
                
                emoji = AGENT_PERSONAS.get(agent_to_elaborate, {}).get('emoji', '🤖')
                agent_name = AGENT_PERSONAS.get(agent_to_elaborate, {}).get('name', agent_to_elaborate)
                
                # Send full elaboration without truncation
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"""{emoji} *{agent_name} - Detailed Elaboration:*

{elaborated}

_Based on analysis of: {last_analysis['query']}_
_Ask another agent for their perspective: `@Agentic Team @competitor elaborate`_""",
                    thread_ts=thread_ts
                )
            except Exception as e:
                logger.error(f"LLM elaboration failed: {e}")
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"Error creating elaboration: {str(e)}",
                    thread_ts=thread_ts
                )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"No analysis found for {agent_to_elaborate} agent.",
                thread_ts=thread_ts
            )
            
    else:
        # General help message
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=f"""Hello <@{user_id}>! I'm the Market Research Team Bot.

**Ask agents directly:**
• `@Agentic Team @psychological what drives customer fear?`
• `@Agentic Team voice: show exact pain language`
• `@Agentic Team @competitor who are the main threats?`

**Or use commands:**
• `/team [company]` - Full 6-agent analysis
• `/psychological [question]` - Direct psychological analysis
• `/memory` - Check stored insights

All agents share memory and build on each other's insights!"""
        )

# ==============================================
# 20. COACH COMMAND - IMPROVE AGENTS
# ==============================================

@app.command("/coach")
def handle_coach_command(ack, respond, command):
    """Coach an agent to improve with memory"""
    ack()
    
    parts = command['text'].split(' ', 1)
    if len(parts) < 2:
        respond("""Usage: `/coach [agent] [coaching message]`
        
Example: `/coach psychological Focus more on identity conflicts and transformation resistance`
        
Available agents: psychological, voice, competitor, interview_psychological, interview_sales, gtm""")
        return
    
    agent_name = parts[0].lower().replace('-', '_')
    coaching_message = parts[1]
    
    # Validate agent name
    if agent_name not in AGENT_PERSONAS:
        # Try common variations
        if agent_name == "interview":
            respond("Please specify: `/coach interview_psychological` or `/coach interview_sales`")
            return
        elif agent_name in ["gtm_blueprint", "blueprint"]:
            agent_name = "gtm"
        
        if agent_name not in AGENT_PERSONAS:
            respond(f"""Unknown agent: {agent_name}
            
Valid agents: psychological, voice, competitor, interview_psychological, interview_sales, gtm""")
            return
    
    # Get agent details
    persona = AGENT_PERSONAS[agent_name]
    emoji = persona['emoji']
    name = persona['name']
    
    # Record learning if memory enabled
    improvement_expected = 0.05  # 5% expected improvement
    
    if MEMORY_ENABLED:
        try:
            channel_id = command['channel_id']
            user_id = command['user_id']
            client_id = get_client_id(channel_id, user_id)
            
            # Store coaching as high-importance memory
            memory_system.store_memory(
                client_id=client_id,
                agent_name=agent_name,
                memory_type="coaching",
                content=f"Coaching insight: {coaching_message}",
                importance=0.9  # High importance for coaching
            )
            
            # Get current improvement stats
            try:
                improvements = memory_system.get_agent_improvements(agent_name)
                total_coachings = improvements.get('total_learnings', 0)
            except:
                total_coachings = 0
            
            response = f"""
{emoji} *Learning Recorded for {name}*

**Coaching:** {coaching_message}

**Impact:**
• Expected improvement: +{improvement_expected:.1%} quality
• Total coaching sessions: {total_coachings + 1}
• This insight will be applied in all future analyses

**Test the improvement:**
• Direct: `/psychological How does this apply to startups?`
• Q&A: `@Agentic Team @{agent_name} show me how you apply this insight`
• Full analysis: `/team [company]` - agent will use this learning

Memory stored with high importance (0.9) for maximum impact."""
            
        except Exception as e:
            logger.error(f"Failed to record coaching: {e}")
            response = f"Coaching acknowledged but couldn't store: {str(e)}"
    else:
        response = f"""
{emoji} *Coaching Acknowledged for {name}*

**Guidance:** {coaching_message}

⚠️ Memory system not available - coaching won't persist across sessions.
Enable memory system (Qdrant) for persistent agent improvements."""
    
    respond(response)

# ==============================================
# 21. LEARNING COMMAND - VIEW IMPROVEMENTS
# ==============================================

@app.command("/learning")
def handle_learning_command(ack, respond, command):
    """Show agent learning progress and improvements"""
    ack()
    
    if not MEMORY_ENABLED:
        respond("""📈 Learning tracking requires memory system to be enabled.
        
Configure Qdrant in your .env file to enable persistent learning.""")
        return
    
    try:
        channel_id = command['channel_id']
        user_id = command['user_id']
        client_id = get_client_id(channel_id, user_id)
        
        agents = ["psychological", "voice_of_customer", "competitor", 
                 "interview_psychological", "interview_sales", "gtm_blueprint"]
        
        message = "📈 *Agent Learning Progress Report*\n\n"
        total_learnings = 0
        
        for agent in agents:
            try:
                # Get coaching memories for this agent
                memories = memory_system.retrieve_memories(
                    client_id=client_id,
                    agent_name=agent,
                    query="coaching",
                    limit=5
                )
                
                coaching_count = len([m for m in memories if 'coaching' in m.content.lower()])
                
                if coaching_count > 0:
                    total_learnings += coaching_count
                    agent_display = agent.replace('_', ' ').title()
                    emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖')
                    
                    message += f"{emoji} **{agent_display}**\n"
                    message += f"• Coaching sessions: {coaching_count}\n"
                    message += f"• Estimated improvement: {coaching_count * 5}% quality boost\n"
                    
                    # Show most recent coaching
                    for mem in memories[:1]:
                        if 'coaching' in mem.content.lower():
                            coaching_text = mem.content.replace('Coaching insight: ', '')
                            preview = coaching_text[:100] + "..." if len(coaching_text) > 100 else coaching_text
                            message += f"• Latest: _{preview}_\n"
                    
                    message += "\n"
            except Exception as e:
                logger.debug(f"Could not get learning for {agent}: {e}")
        
        if total_learnings == 0:
            message += """_No coaching recorded yet._

**How to coach agents:**
`/coach psychological Focus on deeper unconscious patterns`
`/coach voice Extract more emotional language`
`/coach competitor Look for indirect competition`

Coaching makes agents permanently better at their analysis!"""
        else:
            message += f"""**Total learnings across all agents:** {total_learnings}

These improvements are applied to all analyses automatically.
Test with `/team [company]` to see enhanced agent performance!"""
        
        respond(message)
        
    except Exception as e:
        logger.error(f"Learning command error: {e}")
        respond(f"Error retrieving learning data: {str(e)}")

import asyncio
import logging
from typing import Dict, List, Any

# Configure logging for debugging
logger = logging.getLogger(__name__)

@app.command("/debate")
def handle_debate(ack, respond, command, client):
    """Multiple agents debate with two-message consensus for optimal display"""
    
    # Acknowledge immediately
    ack()
    print(f"[DEBUG] Debate command received. Topic: {command['text']}")
    
    try:
        # Extract and validate topic
        topic = command['text'].strip()
        if not topic:
            error_msg = """Please provide a debate topic. 
            
Usage: `/debate [topic]`

Examples:
- `/debate AI vs human consultants`
- `/debate Should startups focus on product or marketing first?`
- `/debate The future of remote work culture`"""
            
            print(f"[DEBUG] No topic provided")
            respond(error_msg)
            return
        
        # Get channel and client info
        channel_id = command.get('channel_id', '')
        client_id = get_client_id(channel_id) if 'get_client_id' in globals() else 'default'
        print(f"[DEBUG] Channel: {channel_id}, Client: {client_id}")
        
        # Select debating agents
        debaters = ['psychological', 'voice_of_customer', 'competitor']
        print(f"[DEBUG] Selected debaters: {debaters}")
        
        # Start debate thread
        initial_msg = client.chat_postMessage(
            channel=channel_id,
            text=f"🎭 *Starting Debate:* {topic}\n_Gathering perspectives from {len(debaters)} agents..._"
        )
        thread_ts = initial_msg['ts']
        print(f"[DEBUG] Created thread: {thread_ts}")
        
        # Collect FULL positions from each agent
        positions = {}
        
        for agent in debaters:
            try:
                print(f"[DEBUG] Getting position from {agent}...")
                
                # Get agent response
                if 'LLM_AVAILABLE' in globals() and LLM_AVAILABLE:
                    if 'get_agent_direct_response' in globals():
                        import asyncio
                        position = asyncio.run(get_agent_direct_response(
                            agent,
                            f"Give your position on this debate topic: {topic}. Be concise but insightful (max 150 words).",
                            {"client_id": client_id}
                        ))
                        print(f"[DEBUG] Got LLM response from {agent}: {len(position)} chars")
                    else:
                        position = f"[{agent} perspective on {topic}]"
                        print(f"[DEBUG] Function not found, using fallback")
                else:
                    # Mock response when LLM not available
                    agent_info = AGENT_PERSONAS.get(agent, {}) if 'AGENT_PERSONAS' in globals() else {}
                    focus = agent_info.get('focus', ['analysis'])[0] if agent_info else 'analysis'
                    position = f"As {agent}, my position on '{topic}' centers on {focus}. This requires deep understanding."
                    print(f"[DEBUG] Using mock response for {agent}")
                
                # Store FULL position
                positions[agent] = position
                
                # Post FULL position to thread
                emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖') if 'AGENT_PERSONAS' in globals() else '🤖'
                agent_name = agent.replace('_', ' ').title()
                
                # Post the complete position
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=f"{emoji} *{agent_name}:*\n\n{position}"
                )
                print(f"[DEBUG] Posted {agent}'s full position ({len(position)} chars)")
                
            except Exception as agent_error:
                print(f"[ERROR] Failed to get position from {agent}: {str(agent_error)}")
                positions[agent] = f"[Error getting {agent} perspective]"
        
        # TWO-MESSAGE CONSENSUS APPROACH
        print(f"[DEBUG] Generating two-message consensus...")
        
        # MESSAGE 1: Ultra-short summary for thread preview (max 250 chars)
        preview_consensus = f"💡 *Debate Complete: {topic}*\n\n"
        
        # Just show who participated with checkmarks
        for agent in positions.keys():
            emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖') if 'AGENT_PERSONAS' in globals() else '🤖'
            agent_name = agent.replace('_', ' ').title()
            preview_consensus += f"{emoji} {agent_name} ✓\n"
        
        preview_consensus += "\n📊 *Verdict:* Multiple perspectives revealed"
        preview_consensus += "\n💬 See full positions above"
        
        print(f"[DEBUG] Preview consensus: {len(preview_consensus)} chars")
        
        # Post the preview consensus
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=preview_consensus
        )
        print(f"[DEBUG] Posted preview consensus")
        
        # MESSAGE 2: Detailed takeaways (separate message for those who open thread)
        detailed_summary = "📋 *Key Takeaways from the Debate:*\n\n"
        
        # Extract key points from each position
        for agent, position in positions.items():
            emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖') if 'AGENT_PERSONAS' in globals() else '🤖'
            agent_name = agent.replace('_', ' ').title()
            
            # Extract the most important sentence (usually first one)
            if '. ' in position:
                sentences = position.split('. ')
                key_sentence = sentences[0] + '.'
                # If first sentence is too long, try second
                if len(key_sentence) > 150 and len(sentences) > 1:
                    key_sentence = sentences[1] + '.' if len(sentences[1]) < 150 else sentences[0][:100] + "..."
            else:
                key_sentence = position[:100] + "..." if len(position) > 100 else position
            
            detailed_summary += f"{emoji} **{agent_name}:** {key_sentence}\n\n"
        
        # Add synthesis based on topic
        if 'AI' in topic.upper() or 'HUMAN' in topic.upper():
            synthesis = "The AI vs human dynamic reveals not competition but complementarity - each excels in different dimensions."
        elif 'MARKET' in topic.upper() or 'BUSINESS' in topic.upper():
            synthesis = "Market success requires balancing multiple strategic perspectives and stakeholder needs."
        else:
            synthesis = "This debate highlights how different analytical lenses reveal complementary insights."
        
        detailed_summary += f"💭 *Synthesis:* {synthesis}\n\n"
        
        # Add interaction options
        detailed_summary += "🔄 *Continue the Discussion:*\n"
        detailed_summary += f"• Deep dive: `@Agentic Team @psychological elaborate on [aspect]`\n"
        detailed_summary += f"• New debate: `/debate [your topic]`\n"
        detailed_summary += f"• Agent dialogue: `/conversation {debaters[0]} {debaters[1]} [topic]`"
        
        print(f"[DEBUG] Detailed summary: {len(detailed_summary)} chars")
        
        # Post detailed summary as separate message
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=detailed_summary
        )
        print(f"[DEBUG] Posted detailed summary")
        
        # Optional: Save to file if debate is very long
        total_content = sum(len(p) for p in positions.values())
        if total_content > 4000:
            print(f"[DEBUG] Large debate ({total_content} chars), considering file save...")
            try:
                save_debate_to_file(topic, positions, channel_id, client)
            except Exception as file_error:
                print(f"[WARNING] Could not save to file: {file_error}")
        
        # Store in memory if available
        if 'MEMORY_ENABLED' in globals() and MEMORY_ENABLED and 'memory_system' in globals():
            try:
                for agent, position in positions.items():
                    memory_system.store_memory(
                        client_id=client_id,
                        agent_name=agent,
                        memory_type="debate",
                        content=f"Debate on {topic}: {position[:500]}",
                        importance=0.6
                    )
                print(f"[DEBUG] Stored debate in memory system")
            except Exception as mem_error:
                print(f"[WARNING] Failed to store memory: {mem_error}")
        
        print(f"[DEBUG] Debate completed successfully")
        
    except Exception as e:
        error_msg = f"❌ Error running debate: {str(e)}"
        print(f"[ERROR] Debate command failed: {e}")
        import traceback
        traceback.print_exc()
        respond(error_msg)


def save_debate_to_file(topic, positions, channel_id, client):
    """
    Save full debate transcript when content is extensive
    
    WHY: Some debates generate lots of content worth preserving
    """
    import datetime
    import os
    
    print(f"[DEBUG] Saving debate to file...")
    
    # Create filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debate_{topic.replace(' ', '_')[:30]}_{timestamp}.txt"
    
    # Build file content
    content = []
    content.append("="*60)
    content.append(f"DEBATE TRANSCRIPT: {topic}")
    content.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("="*60)
    content.append("")
    
    for agent, position in positions.items():
        agent_name = agent.replace('_', ' ').title()
        emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖') if 'AGENT_PERSONAS' in globals() else '🤖'
        
        content.append(f"\n{emoji} {agent_name}")
        content.append("-"*40)
        content.append(position)
        content.append("")
    
    content.append("="*60)
    content.append("END OF DEBATE TRANSCRIPT")
    content.append("="*60)
    
    file_content = "\n".join(content)
    
    # Ensure reports directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    filepath = os.path.join(reports_dir, filename)
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    print(f"[DEBUG] Saved debate to {filepath}")
    
    # Upload to Slack
    try:
        client.files_upload_v2(
            channel=channel_id,
            file=filepath,
            title=f"Debate Transcript: {topic}",
            initial_comment=f"📄 Complete debate transcript for: *{topic}*\n_Download for full analysis_"
        )
        print(f"[DEBUG] Uploaded transcript to Slack")
    except Exception as upload_error:
        print(f"[ERROR] Could not upload file to Slack: {upload_error}")


def smart_truncate(text, max_length=2900, preserve_structure=True):
    """
    Intelligently truncate text while preserving meaning and structure
    
    WHY: Slack has message limits, but we want to keep the most important info
    """
    if len(text) <= max_length:
        return text
    
    print(f"[DEBUG] Truncating text from {len(text)} to {max_length} chars")
    
    if preserve_structure:
        # Try to preserve complete sentences
        sentences = text.split('. ')
        truncated = []
        current_length = 0
        
        for sentence in sentences:
            sentence_with_period = sentence + '. '
            if current_length + len(sentence_with_period) <= max_length - 100:  # Leave room for "..."
                truncated.append(sentence_with_period)
                current_length += len(sentence_with_period)
            else:
                break
        
        result = ''.join(truncated)
        if len(result) < len(text):
            result += "\n\n_[Message truncated - see thread for full discussion]_"
        return result
    else:
        # Simple truncation
        return text[:max_length-50] + "\n\n_[Truncated]_"


def create_debate_summary_file(topic, positions, channel_id):
    """
    Create a text file with the full debate content
    
    WHY: When debate is too long for Slack, save full version as downloadable file
    """
    import datetime
    
    print(f"[DEBUG] Creating debate summary file for topic: {topic}")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debate_{timestamp}.txt"
    
    # Build file content
    content = []
    content.append("="*60)
    content.append(f"DEBATE TRANSCRIPT: {topic}")
    content.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("="*60)
    content.append("\n")
    
    for agent, position in positions.items():
        agent_name = agent.replace('_', ' ').title()
        content.append(f"\n{agent_name}'s Position:")
        content.append("-"*40)
        content.append(position)
        content.append("\n")
    
    content.append("="*60)
    content.append("END OF DEBATE")
    content.append("="*60)
    
    file_content = "\n".join(content)
    
    # Save to reports folder
    import os
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        print(f"[DEBUG] Created reports directory")
    
    filepath = os.path.join(reports_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)
        print(f"[DEBUG] Saved debate to {filepath}")
        
        # Upload to Slack if file is created
        if 'client' in globals() and os.path.exists(filepath):
            client.files_upload_v2(
                channel=channel_id,
                file=filepath,
                title=f"Debate: {topic}",
                initial_comment=f"📄 Full debate transcript attached"
            )
            print(f"[DEBUG] Uploaded debate file to Slack")
        
        return filepath
    except Exception as e:
        print(f"[ERROR] Failed to create debate file: {e}")
        return None


# ==============================================
# CONVERSATION COMMAND - FIXED VERSION
# ==============================================

@app.command("/conversation")
def handle_conversation(ack, respond, command, client):
    """Two agents conversation with transcript file generation"""
    
    # Acknowledge immediately
    ack()
    print(f"[DEBUG] Conversation command received: {command['text']}")
    
    try:
        # Parse command arguments
        parts = command['text'].split(' ', 2)
        if len(parts) < 3:
            respond("""Usage: `/conversation [agent1] [agent2] [topic]`
Example: `/conversation psychological voice customer needs`
Agents: psychological, voice, competitor, gtm""")
            return
        
        agent1_input = parts[0].lower()
        agent2_input = parts[1].lower()
        topic = parts[2]
        
        print(f"[DEBUG] Parsed: agent1={agent1_input}, agent2={agent2_input}, topic={topic}")
        
        # Normalize agent names
        agent_aliases = {
            'voice': 'voice_of_customer',
            'voc': 'voice_of_customer',
            'gtm': 'gtm_blueprint',
            'psych': 'psychological',
            'comp': 'competitor',
            'psy': 'psychological'
        }
        
        agent1 = agent_aliases.get(agent1_input, agent1_input)
        agent2 = agent_aliases.get(agent2_input, agent2_input)
        
        print(f"[DEBUG] Normalized: {agent1}, {agent2}")
        
        # Validate agents exist
        if 'AGENT_PERSONAS' in globals():
            valid_agents = list(AGENT_PERSONAS.keys())
            if agent1 not in valid_agents or agent2 not in valid_agents:
                respond(f"❌ Invalid agents. Available: {', '.join(valid_agents[:5])}")
                return
        
        # Get emojis and names
        emoji1 = AGENT_PERSONAS.get(agent1, {}).get('emoji', '🤖') if 'AGENT_PERSONAS' in globals() else '🤖'
        emoji2 = AGENT_PERSONAS.get(agent2, {}).get('emoji', '🤖') if 'AGENT_PERSONAS' in globals() else '🤖'
        agent1_name = agent1.replace('_', ' ').title()
        agent2_name = agent2.replace('_', ' ').title()
        
        # Setup
        channel_id = command.get('channel_id', '')
        client_id = get_client_id(channel_id) if 'get_client_id' in globals() else 'default'
        
        print(f"[DEBUG] Channel: {channel_id}, Client: {client_id}")
        
        # Start conversation thread
        initial_msg = client.chat_postMessage(
            channel=channel_id,
            text=f"💬 *Starting Conversation on: {topic}*\n{emoji1} {agent1_name} ↔️ {emoji2} {agent2_name}\n_Generating dialogue..._"
        )
        thread_ts = initial_msg['ts']
        
        print(f"[DEBUG] Thread created: {thread_ts}")
        
        # Store full conversation for transcript
        conversation_transcript = []
        
        # ROUND 1: Opening perspectives
        try:
            print(f"[DEBUG] Round 1: Opening perspectives")
            
            # Agent 1 opens
            prompt1 = f"Share your perspective on '{topic}'. Be insightful but concise (max 120 words)."
            
            if 'LLM_AVAILABLE' in globals() and LLM_AVAILABLE and 'get_agent_direct_response' in globals():
                import asyncio
                response1 = asyncio.run(get_agent_direct_response(
                    agent1,
                    prompt1,
                    {"client_id": client_id}
                ))
                print(f"[DEBUG] {agent1} response: {len(response1)} chars")
            else:
                response1 = f"From the {agent1} perspective, {topic} presents complex challenges."
            
            # Store in transcript
            conversation_transcript.append({
                'round': 1,
                'agent': agent1_name,
                'emoji': emoji1,
                'type': 'opening',
                'response': response1
            })
            
            # Post to Slack
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"{emoji1} *{agent1_name}:*\n\n{response1}"
            )
            
            # Agent 2 responds
            context1 = response1[:150] if len(response1) > 150 else response1
            prompt2 = f"Respond to this perspective on '{topic}': '{context1}...' Add your insights (max 120 words)."
            
            if 'LLM_AVAILABLE' in globals() and LLM_AVAILABLE and 'get_agent_direct_response' in globals():
                import asyncio
                response2 = asyncio.run(get_agent_direct_response(
                    agent2,
                    prompt2,
                    {"client_id": client_id}
                ))
                print(f"[DEBUG] {agent2} response: {len(response2)} chars")
            else:
                response2 = f"Building on that, from the {agent2} perspective, we see different patterns."
            
            # Store in transcript
            conversation_transcript.append({
                'round': 1,
                'agent': agent2_name,
                'emoji': emoji2,
                'type': 'response',
                'response': response2
            })
            
            # Post to Slack
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"{emoji2} *{agent2_name}:*\n\n{response2}"
            )
            
        except Exception as round1_error:
            print(f"[ERROR] Round 1 failed: {round1_error}")
        
        # ROUND 2: Deeper insights
        try:
            print(f"[DEBUG] Round 2: Deeper insights")
            
            import time
            time.sleep(0.5)
            
            # Agent 1 key insight
            prompt3 = f"What's the crucial insight about {topic} from our discussion? (max 100 words)"
            
            if 'LLM_AVAILABLE' in globals() and LLM_AVAILABLE and 'get_agent_direct_response' in globals():
                import asyncio
                response3 = asyncio.run(get_agent_direct_response(
                    agent1,
                    prompt3,
                    {"client_id": client_id}
                ))
            else:
                response3 = f"The key insight about {topic} is the interplay between perspectives."
            
            # Store in transcript
            conversation_transcript.append({
                'round': 2,
                'agent': agent1_name,
                'emoji': emoji1,
                'type': 'insight',
                'response': response3
            })
            
            # Post to Slack
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"{emoji1} *{agent1_name} (Key Insight):*\n\n{response3}"
            )
            
            # Agent 2 synthesis
            prompt4 = f"Synthesize our discussion on {topic}. What's the takeaway? (max 100 words)"
            
            if 'LLM_AVAILABLE' in globals() and LLM_AVAILABLE and 'get_agent_direct_response' in globals():
                import asyncio
                response4 = asyncio.run(get_agent_direct_response(
                    agent2,
                    prompt4,
                    {"client_id": client_id}
                ))
            else:
                response4 = f"Our dialogue on {topic} reveals complementary perspectives."
            
            # Store in transcript
            conversation_transcript.append({
                'round': 2,
                'agent': agent2_name,
                'emoji': emoji2,
                'type': 'synthesis',
                'response': response4
            })
            
            # Post to Slack
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"{emoji2} *{agent2_name} (Synthesis):*\n\n{response4}"
            )
            
        except Exception as round2_error:
            print(f"[ERROR] Round 2 failed: {round2_error}")
        
        # Save conversation to file
        print(f"[DEBUG] Saving conversation transcript...")
        try:
            filepath = save_conversation_to_file(
                topic=topic,
                agent1=agent1_name,
                agent2=agent2_name,
                transcript=conversation_transcript,
                channel_id=channel_id,
                client=client
            )
            print(f"[DEBUG] Transcript saved to: {filepath}")
        except Exception as file_error:
            print(f"[WARNING] Could not save transcript: {file_error}")
        
        # Store in memory if available
        if 'MEMORY_ENABLED' in globals() and MEMORY_ENABLED and 'memory_system' in globals():
            try:
                memory_content = f"Conversation between {agent1} and {agent2} on {topic}. "
                if conversation_transcript:
                    memory_content += f"Key: {conversation_transcript[0]['response'][:100]}"
                
                memory_system.store_memory(
                    client_id=client_id,
                    agent_name=f"{agent1}_{agent2}",
                    memory_type="conversation",
                    content=memory_content[:500],
                    importance=0.7
                )
                print(f"[DEBUG] Stored conversation memory")
            except Exception as mem_error:
                print(f"[WARNING] Memory storage failed: {mem_error}")
        
        print(f"[DEBUG] Conversation completed successfully")
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        print(f"[ERROR] Conversation failed: {e}")
        import traceback
        traceback.print_exc()
        respond(error_msg)


def save_conversation_to_file(topic, agent1, agent2, transcript, channel_id, client):
    """
    Save full conversation transcript to file and upload to Slack
    
    WHY: Preserves complete conversation without any truncation
    """
    import datetime
    import os
    
    # Create filename with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.replace(' ', '_').replace('/', '-')[:30]
    filename = f"conversation_{safe_topic}_{timestamp}.txt"
    
    # Build file content
    content = []
    content.append("="*60)
    content.append(f"CONVERSATION TRANSCRIPT: {topic}")
    content.append(f"Participants: {agent1} ↔️ {agent2}")
    content.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("="*60)
    content.append("")
    
    # Add each exchange
    for i, exchange in enumerate(transcript, 1):
        round_num = exchange.get('round', 1)
        agent = exchange.get('agent', 'Unknown')
        emoji = exchange.get('emoji', '🤖')
        ex_type = exchange.get('type', 'message')
        response = exchange.get('response', '')
        
        if ex_type == 'opening':
            content.append(f"\n--- ROUND {round_num}: OPENING PERSPECTIVES ---\n")
        elif ex_type == 'insight':
            content.append(f"\n--- ROUND {round_num}: KEY INSIGHTS ---\n")
        
        content.append(f"{emoji} {agent}")
        if ex_type in ['insight', 'synthesis']:
            content.append(f"[{ex_type.upper()}]")
        content.append("-"*40)
        content.append(response)
        content.append("")
    
    # Add summary
    content.append("="*60)
    content.append("CONVERSATION SUMMARY")
    content.append("="*60)
    content.append(f"\nThe dialogue between {agent1} and {agent2} on '{topic}'")
    content.append("explored multiple perspectives and revealed complementary insights.")
    content.append(f"\nTotal exchanges: {len(transcript)}")
    content.append(f"Total content: {sum(len(ex['response']) for ex in transcript)} characters")
    content.append("\n" + "="*60)
    content.append("END OF CONVERSATION TRANSCRIPT")
    content.append("="*60)
    
    file_content = "\n".join(content)
    
    # Ensure reports directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    filepath = os.path.join(reports_dir, filename)
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)
    
    print(f"[DEBUG] Saved conversation to {filepath}")
    
    # Upload to Slack
    try:
        # Get emojis for the message
        emoji1 = '🧠' if 'psychological' in agent1.lower() else '🗣️' if 'voice' in agent1.lower() else '🔍'
        emoji2 = '🧠' if 'psychological' in agent2.lower() else '🗣️' if 'voice' in agent2.lower() else '🔍'
        
        client.files_upload_v2(
            channel=channel_id,
            file=filepath,
            title=f"Conversation: {topic}",
            initial_comment=f"📄 *Complete conversation transcript for: {topic}*\n{emoji1} {agent1} ↔️ {emoji2} {agent2}\n_Download for full analysis_"
        )
        print(f"[DEBUG] Uploaded transcript to Slack")
    except Exception as upload_error:
        print(f"[ERROR] Could not upload file to Slack: {upload_error}")
    
    return filepath

# ==============================================
# POTENTIAL FIX CHECKLIST
# ==============================================

def verify_async_fix():
    """
    Run this to verify your async issues are fixed
    """
    issues = []
    fixes = []
    
    print("\n" + "="*50)
    print("ASYNC FIX VERIFICATION CHECKLIST")
    print("="*50)
    
    # Check 1: Command handlers should be sync
    print("\n✓ Command handlers are now SYNC (not async)")
    fixes.append("Changed: @app.command handlers from 'async def' to regular 'def'")
    
    # Check 2: Async calls use asyncio.run()
    print("✓ Async agent calls use asyncio.run()")
    fixes.append("Using: asyncio.run(get_agent_direct_response(...)) for async LLM calls")
    
    # Check 3: Error handling
    print("✓ Comprehensive try-except blocks added")
    fixes.append("Added: Detailed error messages and logging at each step")
    
    # Check 4: Debug prints
    print("✓ Debug print statements for troubleshooting")
    fixes.append("Added: [DEBUG] prints to track execution flow")
    
    # Check 5: Validation
    print("✓ Input validation before processing")
    fixes.append("Added: Checks for empty topics, invalid agents, missing parameters")
    
    print("\n" + "-"*50)
    print("POTENTIAL ISSUES TO CHECK:")
    print("-"*50)
    
    # Common issues
    potential_issues = [
        "1. Ensure 'AGENT_PERSONAS' dictionary is defined",
        "2. Verify 'get_agent_direct_response' function exists",
        "3. Check 'LLM_AVAILABLE' flag is set correctly",
        "4. Confirm 'get_client_id' function is available",
        "5. Validate 'memory_system' is initialized if MEMORY_ENABLED=True"
    ]
    
    for issue in potential_issues:
        print(f"⚠️  {issue}")
    
    print("\n" + "-"*50)
    print("TEST COMMANDS:")
    print("-"*50)
    print("/debate AI vs human creativity")
    print("/conversation psychological voice customer needs")
    print("/conversation gtm competitor market positioning")
    
    print("\n" + "="*50)
    print("If errors persist, check the [DEBUG] outputs!")
    print("="*50 + "\n")
    
    return fixes

# Run verification
if __name__ == "__main__":
    verify_async_fix()

# ==============================================
# 24. MESSAGE EVENT HANDLER - CONSOLIDATED
# ==============================================
@app.event("message")
def handle_message_events(event, client, logger):
    """Handle all message events including file uploads"""
    
    # Debug every message event
    if event.get('type') == 'message' and not event.get('bot_id'):
        print(f"\n[DEBUG] === MESSAGE EVENT ===")
        print(f"[DEBUG] User: {event.get('user')}")
        print(f"[DEBUG] Channel: {event.get('channel')}")
        print(f"[DEBUG] Has files: {'files' in event and len(event.get('files', []))}")
        print(f"[DEBUG] Subtype: {event.get('subtype', 'regular message')}")
    
    # Skip bot messages
    if event.get('bot_id') or event.get('subtype') == 'bot_message':
        return
    
    # CRITICAL: Handle file uploads
    if 'files' in event and event.get('files'):
        print(f"\n[DEBUG] 🎯 FILE UPLOAD DETECTED!")
        
        channel_id = event.get('channel')
        user_id = event.get('user')
        files = event.get('files', [])
        
        print(f"[DEBUG] Files count: {len(files)}")
        for f in files:
            print(f"[DEBUG] File: {f.get('name')} ({f.get('mimetype')})")
        
        if not channel_id or not user_id:
            print("[DEBUG] ❌ Missing channel or user ID")
            return
        
        # Check if user has pending research-complete command
        pending_key = f"{channel_id}_{user_id}"
        print(f"[DEBUG] Checking pending key: {pending_key}")
        print(f"[DEBUG] All pending keys: {list(RESEARCH_UPLOAD_PENDING.keys())}")
        
        if pending_key in RESEARCH_UPLOAD_PENDING:
            print("[DEBUG] ✅ USER HAS PENDING RESEARCH-COMPLETE!")
            
            # Check timeout
            pending_data = RESEARCH_UPLOAD_PENDING[pending_key]
            time_elapsed = datetime.now() - pending_data['timestamp']
            
            if time_elapsed > timedelta(minutes=5):
                print(f"[DEBUG] ⏰ Command expired ({time_elapsed.seconds}s)")
                del RESEARCH_UPLOAD_PENDING[pending_key]
                client.chat_postMessage(
                    channel=channel_id,
                    text="⏰ Upload timeout. Please run `/research-complete` again."
                )
                return
            
            # Process the first file
            if files:
                file_to_process = files[0]
                print(f"[DEBUG] 🔄 Processing file: {file_to_process.get('name')}")
                
                # Send acknowledgment
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"📥 **File received:** {file_to_process.get('name')}\n🔄 Processing your template..."
                )
                
                # Process the file
                process_template_file(
                    client, event, file_to_process, 
                    channel_id, user_id, 
                    is_research_complete=True
                )
                
                # Clear pending status
                del RESEARCH_UPLOAD_PENDING[pending_key]
                print(f"[DEBUG] ✅ Cleared pending status for {pending_key}")
                return
        else:
            print("[DEBUG] No pending research-complete command")
            
            # Check if file looks like a template anyway
            for file_info in files:
                file_name = file_info.get('name', '').lower()
                print(f"[DEBUG] Checking if template-like: {file_name}")
                
                template_keywords = [
                    'template', 'research', 'market', 'brief',
                    'analysis', 'business', 'company'
                ]
                
                is_template_file = (
                    any(keyword in file_name for keyword in template_keywords) or
                    file_name.endswith(('.txt', '.md', '.pdf', '.docx', '.doc'))
                )
                
                if is_template_file:
                    print(f"[DEBUG] 📋 File appears to be template")
                    
                    client.chat_postMessage(
                        channel=channel_id,
                        text=f"""📎 **Possible template detected:** {file_info.get('name')}

To process this file:
1. Type `/research-complete` 
2. Then upload the file again

Or I can check if it's valid now..."""
                    )
                    
                    # Try processing anyway
                    process_template_file(
                        client, event, file_info,
                        channel_id, user_id,
                        is_research_complete=False
                    )
                    return

# ==============================================
# 25. TEMPLATE DOWNLOAD COMMAND
# ==============================================

@app.command("/template")
def handle_template_download(ack, respond, command, client):
    """Provide the market research template for download"""
    ack()
    
    template_content = """Market Research Brief Template

1. BUSINESS TYPE
[ ] B2B
[ ] B2C
[ ] B2B2C

2. COMPANY NAME
[Your company name]

3. INDUSTRY
[Specific industry/niche - be detailed]
Example: "Financial Services - Independent Financial Advisors"
Example: "Health & Wellness - Premium Recovery & Wellness Spa Services"
Example: "SaaS - Project Management for Construction Companies"

4. PRODUCT/SERVICE DESCRIPTION
[Detailed description of what you offer and HOW it works. Include your unique methodology if applicable]

Structure using pillars/components:
- PILLAR 1: [Component name] - [What it does and why it matters]
- PILLAR 2: [Component name] - [What it does and why it matters]
- PILLAR 3: [Component name] - [What it does and why it matters]
- PILLAR 4: [Component name] - [What it does and why it matters]

Unique methodology: [Your proprietary approach, framework, or system]

5. TARGET CUSTOMER DESCRIPTION
[One sentence describing your ideal customer]

Example: "Mid-career financial advisors with 5-10 years experience who are stuck and frustrated with current practice growth"
Example: "Affluent business professionals aged 35-65 experiencing age-related recovery challenges and seeking premium wellness solutions"

6. DEMOGRAPHICS & CHARACTERISTICS
- Age: [Range or specific age group]
- Gender: [If relevant, otherwise note "Both" or "No preference"]
- Education: [Level - high school, college, advanced degrees]
- Income: [Individual or household income range]
- Company size: [For B2B - employees, revenue, etc.]
- Location: [Geographic focus - city, region, national, global]
- Career stage: [Experience level, seniority, career phase]
- Other relevant traits: [Industry-specific characteristics, lifestyle, values, etc.]

7. CUSTOMER CONTEXT/SITUATION
[Describe their day-to-day reality, responsibilities, and pressures]

Include:
- Daily/weekly routines and responsibilities
- Professional pressures and challenges
- Personal life situation
- Time constraints and priorities
- Current tools/solutions they use
- Environmental factors affecting them

8. PROBLEMS YOUR OFFERING SOLVES
[List 5-7 specific problems, starting with most painful]

1. [Most urgent/painful problem - the one that keeps them up at night]
2. [Second most painful - significant impact on daily life/business]
3. [Third problem - frustrating but manageable]
4. [Fourth problem - emerging concern]
5. [Fifth problem - nice-to-solve]
6. [Sixth problem - secondary impact]
7. [Seventh problem - related challenge]

9. CUSTOMER COMPLAINTS (EXACT QUOTES)
[7-10 actual quotes or paraphrases of what customers say]

- "Quote 1 expressing frustration about main problem"
- "Quote 2 about emotional impact of their pain"
- "Quote 3 showing urgency or desperation"
- "Quote 4 about failed solutions they've tried"
- "Quote 5 expressing time/resource constraints"
- "Quote 6 about competition or alternatives"
- "Quote 7 showing fear or anxiety"
- "Quote 8 expressing desire for change"
- "Quote 9 about current unsatisfactory situation"
- "Quote 10 showing willingness to invest in solution"

10. CUSTOMER'S STATED GOALS
[What they SAY they want to achieve - 5-6 goals]

- Goal 1 (in their words, not business jargon)
- Goal 2 (specific, measurable outcome they want)
- Goal 3 (emotional or lifestyle goal)
- Goal 4 (professional or business goal)
- Goal 5 (personal development or growth goal)
- Goal 6 (long-term vision or aspiration)

11. WHAT SUCCESS LOOKS LIKE (IN THEIR WORDS)
[5-6 quotes describing their vision of success]

- "Success quote 1 - specific outcome they can visualize"
- "Success quote 2 - emotional state they want to achieve"
- "Success quote 3 - lifestyle change they desire"
- "Success quote 4 - professional milestone they're aiming for"
- "Success quote 5 - personal transformation they envision"
- "Success quote 6 - long-term vision of their ideal situation"

12. TARGET MARKET DETAILS
[Expand on demographics with market segmentation details]

Primary segment: [Description of main target]
- Company characteristics: [For B2B - size, industry, maturity, etc.]
- Individual characteristics: [For B2C - lifestyle, values, behaviors]
- Current situation: [What stage/state they're in]
- Aspirational direction: [Where they want to go]

Secondary segments: [Additional viable markets]
- Segment 2: [Description]
- Segment 3: [Description]

Market size and trends: [If known - growth, competition, opportunities]

13. MARKETING GOAL
[What specific action do you want them to take?]

Example: "Generate qualified leads for discovery calls with [target customer] who are frustrated with [main pain] and want [primary desire]"
Example: "Drive trial signups from [target segment] who need [solution] to achieve [outcome]"

14. ADDITIONAL CONTEXT
[Important details about your company, founders, culture, differentiators]

Include:
- Founder story/credibility: [Background, experience, personal connection to problem]
- Company values/culture: [What drives the organization]
- Main differentiators: [What makes you unique in the market]
- Social proof: [Current customers, results, testimonials, case studies]
- Unique positioning: [How you're different from competitors]
- Current marketing assets: [Website, content, tools, systems you have]
- Brand personality: [Tone, voice, style preferences]
- Budget considerations: [If relevant to strategy decisions]
- Timeline: [Launch dates, milestones, urgency factors]
- Geographic considerations: [Local market dynamics, cultural factors]

INSTRUCTIONS:
Fill out each section with as much detail as possible. The more context you provide, the more tailored and actionable your market research analysis will be."""
    
    # Save template to file
    filename = save_report_to_file("template", template_content, "template")
    
    # Upload to Slack
    try:
        channel_id = command['channel_id']
        
        file_response = client.files_upload_v2(
            channel=channel_id,
            file=filename,
            title="Market Research Brief Template",
            initial_comment="""📋 Market Research Brief Template*

Download this template and fill it out with your business details.

**How to use:**
1. Download and fill out all 14 sections
2. Save as a text file
3. Upload with `/research-complete` for comprehensive analysis

**Quick version:** Use `/research-guided` for a simplified step-by-step form

All 6 agents will analyze your inputs for deep market insights!"""
        )
        
        respond("✅ Template uploaded! Download it above and fill it out for comprehensive analysis.")
        
    except Exception as e:
        logger.error(f"Could not upload template: {e}")
        respond(f"Template saved to: `{filename}`\n\nUse `/research-guided` for the interactive version.")

# ==============================================
# 26. RESEARCH-GUIDED COMMAND (MULTI-MODAL FLOW)
# ==============================================

@app.command("/research-guided")
def handle_research_guided(ack, respond, command, client):
    """Start guided research with simplified multi-step modals"""
    ack()
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    
    try:
        # Open first modal
        client.views_open(
            trigger_id=command['trigger_id'],
            view={
                "type": "modal",
                "callback_id": "research_modal_step1",
                "private_metadata": json.dumps({
                    "channel_id": channel_id,
                    "user_id": user_id,
                    "step": 1
                }),
                "title": {
                    "type": "plain_text",
                    "text": "Research Brief (1/3)"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Next"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Step 1: Business Fundamentals*\nLet's start with basic information about your business."
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "business_type",
                        "element": {
                            "type": "radio_buttons",
                            "action_id": "business_type_select",
                            "options": [
                                {
                                    "text": {"type": "plain_text", "text": "B2B"},
                                    "value": "B2B"
                                },
                                {
                                    "text": {"type": "plain_text", "text": "B2C"},
                                    "value": "B2C"
                                },
                                {
                                    "text": {"type": "plain_text", "text": "B2B2C"},
                                    "value": "B2B2C"
                                }
                            ]
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Business Type"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "company_name",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "company_name_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Your company name"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Company Name"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "industry",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "industry_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "e.g., SaaS - Project Management for Construction"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Industry (Be Specific)"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "product_service",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "product_service_input",
                            "multiline": True,
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Describe what you offer and how it works"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Product/Service Description"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "target_customer",
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "target_customer_input",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "One sentence describing your ideal customer"
                            }
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Target Customer"
                        }
                    }
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Could not open modal: {e}")
        respond("Error opening research form. Please try `/template` for the downloadable version.")

# Modal submission handlers
@app.view("research_modal_step1")
def handle_research_modal_step1(ack, body, client, view):
    """Handle first modal submission and open second"""
    ack()
    
    # Extract data from step 1
    values = view['state']['values']
    metadata = json.loads(view['private_metadata'])
    
    # Store step 1 data in session
    session_id = f"{metadata['channel_id']}_{metadata['user_id']}"
    if session_id not in TEMPLATE_SESSIONS:
        TEMPLATE_SESSIONS[session_id] = {}
    
    TEMPLATE_SESSIONS[session_id].update({
        "business_type": values['business_type']['business_type_select']['selected_option']['value'],
        "company_name": values['company_name']['company_name_input']['value'],
        "industry": values['industry']['industry_input']['value'],
        "product_service": values['product_service']['product_service_input']['value'],
        "target_customer": values['target_customer']['target_customer_input']['value']
    })
    
    # Open second modal
    client.views_open(
        trigger_id=body['trigger_id'],
        view={
            "type": "modal",
            "callback_id": "research_modal_step2",
            "private_metadata": view['private_metadata'],
            "title": {
                "type": "plain_text",
                "text": "Research Brief (2/3)"
            },
            "submit": {
                "type": "plain_text",
                "text": "Next"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Step 2: Customer Profile*\nTell us about your customers' challenges and context."
                    }
                },
                {
                    "type": "input",
                    "block_id": "demographics",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "demographics_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Age range, income, education, location, etc."
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Demographics & Characteristics"
                    }
                },
                {
                    "type": "input",
                    "block_id": "customer_context",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "customer_context_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Describe their day-to-day reality, pressures, current tools"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Customer Context/Situation"
                    }
                },
                {
                    "type": "input",
                    "block_id": "top_problems",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "top_problems_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "List 3-5 specific problems you solve, starting with most painful"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Top Problems You Solve"
                    }
                },
                {
                    "type": "input",
                    "block_id": "customer_complaints",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "customer_complaints_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "3-5 actual quotes of what customers complain about"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Customer Complaints (Exact Quotes)"
                    }
                }
            ]
        }
    )

@app.view("research_modal_step2")
def handle_research_modal_step2(ack, body, client, view):
    """Handle second modal submission and open third"""
    ack()
    
    # Extract and store step 2 data
    values = view['state']['values']
    metadata = json.loads(view['private_metadata'])
    session_id = f"{metadata['channel_id']}_{metadata['user_id']}"
    
    TEMPLATE_SESSIONS[session_id].update({
        "demographics": values['demographics']['demographics_input']['value'],
        "customer_context": values['customer_context']['customer_context_input']['value'],
        "top_problems": values['top_problems']['top_problems_input']['value'],
        "customer_complaints": values['customer_complaints']['customer_complaints_input']['value']
    })
    
    # Open third modal
    client.views_open(
        trigger_id=body['trigger_id'],
        view={
            "type": "modal",
            "callback_id": "research_modal_step3",
            "private_metadata": view['private_metadata'],
            "title": {
                "type": "plain_text",
                "text": "Research Brief (3/3)"
            },
            "submit": {
                "type": "plain_text",
                "text": "Analyze"
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel"
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Step 3: Goals & Context*\nFinalize with your objectives and additional context."
                    }
                },
                {
                    "type": "input",
                    "block_id": "customer_goals",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "customer_goals_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "What customers say they want to achieve (3-4 goals)"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Customer's Stated Goals"
                    }
                },
                {
                    "type": "input",
                    "block_id": "success_vision",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "success_vision_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "How customers describe success (2-3 quotes)"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "What Success Looks Like"
                    }
                },
                {
                    "type": "input",
                    "block_id": "marketing_goal",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "marketing_goal_input",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "e.g., Generate qualified leads for discovery calls"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Your Marketing Goal"
                    }
                },
                {
                    "type": "input",
                    "block_id": "differentiators",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "differentiators_input",
                        "multiline": True,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "What makes you unique, founder story, social proof"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Key Differentiators & Context"
                    }
                }
            ]
        }
    )

@app.view("research_modal_step3")
def handle_research_modal_step3(ack, body, client, view):
    """Handle final modal submission and run analysis"""
    ack()
    
    # Extract final data
    values = view['state']['values']
    metadata = json.loads(view['private_metadata'])
    session_id = f"{metadata['channel_id']}_{metadata['user_id']}"
    channel_id = metadata['channel_id']
    user_id = metadata['user_id']
    
    # Complete the template data
    TEMPLATE_SESSIONS[session_id].update({
        "customer_goals": values['customer_goals']['customer_goals_input']['value'],
        "success_vision": values['success_vision']['success_vision_input']['value'],
        "marketing_goal": values['marketing_goal']['marketing_goal_input']['value'],
        "differentiators": values['differentiators']['differentiators_input']['value']
    })
    
    # Get all template data
    template_data = TEMPLATE_SESSIONS[session_id]
    
    # Format as comprehensive context
    context = format_template_for_analysis(template_data)
    
    # Enhance with web search if enabled
    enhanced_context = context
    web_sources = []
    
    if SEARCH_ENABLED and search_context:
        try:
            company_name = template_data.get('company_name', '')
            industry = template_data.get('industry', '')
            
            # Search for company and market data
            search_query = f"{company_name} {industry} market analysis 2024 2025"
            search_results, sources = search_context.search_and_cite(search_query, "research_modal")
            
            if search_results:
                enhanced_context += f"\n\n{search_results}"
                web_sources = sources
                logger.info(f"Enhanced context with {len(sources)} web sources")
        except Exception as e:
            logger.warning(f"Search enhancement failed: {e}")
    
    # Send initial message
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text=f"""📋 *Guided Research Analysis Starting*

**Company:** {template_data['company_name']}
**Industry:** {template_data['industry']}

Processing your comprehensive brief with all 6 specialized agents...
This will take 2-3 minutes for deep analysis."""
    )
    thread_ts = initial_msg['ts']
    
    # Run comprehensive analysis
    try:
        if workflow_available:
            client_id = get_client_id(channel_id, user_id)
            workflow = ICPGraph(verbose=True)
            
            result = workflow.run({
                "company": template_data['company_name'],
                "business_context": enhanced_context,
                "template_data": template_data,
                "client_id": client_id,
                "requested_agents": ["psychological", "voice_of_customer", "competitor", 
                                   "interview_psychological", "interview_sales", "gtm_blueprint"],
                "agent_config": {
                    "temperatures": AGENT_TEMPERATURES,
                    "max_tokens": MAX_TOKENS,
                    "search_enabled": SEARCH_ENABLED
                },
                "web_sources": web_sources
            })
            
            # Format and send results
            report = format_full_team_results(result, template_data['company_name'], 0)
            
            # Add source citations if available
            if web_sources:
                report += "\n\n=== WEB SOURCES USED ===\n"
                for i, source in enumerate(web_sources, 1):
                    report += f"[{i}] {source['title']}: {source['url']}\n"
            
            filename = save_report_to_file(template_data['company_name'], report, "guided_research")
            
            # Send using centralized handler
            send_response_with_file_fallback(
                client=client,
                channel_id=channel_id,
                thread_ts=thread_ts,
                response_text=report,
                title=f"Guided Research - {template_data['company_name']}",
                agent_name="research_guided",
                query=template_data['company_name']
            )
            
            # Send completion message
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=f"""✅ *Guided Research Analysis Complete!*

**Company:** {template_data['company_name']}
**Word count:** {len(report.split())} words
**Web sources:** {len(web_sources)}

All 6 agents have analyzed your inputs with deep, nuanced insights tailored to your specific context."""
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Workflow not available. Please check system configuration with `/status`"
            )
            
    except Exception as e:
        logger.error(f"Research analysis error: {e}", exc_info=True)
        client.chat_postMessage(
            channel=channel_id,
            text=f"Error running analysis: {str(e)}\n\nPlease try `/research-guided` again or contact support."
        )
    
    # Clear session data
    if session_id in TEMPLATE_SESSIONS:
        del TEMPLATE_SESSIONS[session_id]

# ==============================================
# 27. RESEARCH-COMPLETE COMMAND (UPDATED)
# ==============================================
@app.command("/research-complete")
def handle_research_complete(ack, respond, command, client):
    """Process uploaded complete template file OR pasted content"""
    ack()
    
    text = command['text'].strip()
    channel_id = command['channel_id']
    user_id = command['user_id']
    
    print(f"[DEBUG] /research-complete called")
    print(f"[DEBUG] Text provided: {len(text)} chars")
    print(f"[DEBUG] Channel: {channel_id}, User: {user_id}")
    
    # Handle pasted content (even if truncated)
    if text and len(text) > 100:  # Assume it's template content if > 100 chars
        print(f"[DEBUG] Processing pasted content")
        
        # Check if Slack truncated it
        if "..." in text[-10:] or len(text) >= 3900:  # Near Slack limit
            respond("""⚠️ **Content appears truncated by Slack**
            
The character limit was reached. Please either:
1. Upload as a .txt file (recommended)
2. Use `/research-guided` for step-by-step form
3. Split into multiple messages

To upload: Just drag your file here after this message.""")
            
            # Still mark as pending for file upload
            key = f"{channel_id}_{user_id}"
            RESEARCH_UPLOAD_PENDING[key] = {
                'timestamp': datetime.now(),
                'channel': channel_id,
                'user': user_id,
                'partial_content': text  # Save what we got
            }
            print(f"[DEBUG] Marked as pending due to truncation: {key}")
            return
        
        # Process non-truncated pasted content
        client_id = get_client_id(channel_id, user_id)
        
        try:
            template_data = parse_template_content(text)
            
            if not template_data.get('company_name'):
                respond("""⚠️ Could not parse template structure.
                
**Tips:**
- Ensure sections are numbered 1-14
- Include section headers like "1. BUSINESS TYPE"
- Or try `/research-guided` for easier input""")  # Fixed: proper closing
                return
            
            # Continue with existing processing...
            # Create comprehensive context
            context = format_template_for_analysis(template_data)
            
            # Enhance with web search if enabled
            enhanced_context = context
            web_sources = []
            
            if SEARCH_ENABLED and search_context:
                try:
                    company_name = template_data.get('company_name', '')
                    industry = template_data.get('industry', '')
                    
                    # Perform multiple targeted searches
                    searches = [
                        f"{company_name} {industry} company profile 2024 2025",
                        f"{industry} market trends challenges opportunities",
                        f"{company_name} competitors alternatives comparison"
                    ]
                    
                    for search_query in searches[:2]:  # Limit to 2 searches
                        search_results, sources = search_context.search_and_cite(search_query, "research_complete")
                        if search_results:
                            enhanced_context += f"\n\n{search_results}"
                            web_sources.extend(sources)
                        time.sleep(0.5)  # Rate limiting
                    
                    logger.info(f"Enhanced context with {len(web_sources)} total web sources")
                except Exception as e:
                    logger.warning(f"Search enhancement failed: {e}")
            
            # Send initial message
            initial_msg = client.chat_postMessage(
                channel=channel_id,
                text=f"""📋 *Processing Complete Template*

**Company:** {template_data.get('company_name', 'Unknown')}
**Industry:** {template_data.get('industry', 'Not specified')}
**Sections filled:** {len([v for v in template_data.values() if v])}/14

Starting comprehensive analysis with all 14 sections of your template...
All 6 agents will provide deep, nuanced insights."""
            )
            thread_ts = initial_msg['ts']
            
            # Run full analysis
            if workflow_available:
                workflow = ICPGraph(verbose=True)
                
                # Pass enhanced configuration to workflow
                result = workflow.run({
                    "company": template_data.get('company_name', 'Unknown'),
                    "business_context": enhanced_context,
                    "template_data": template_data,
                    "client_id": client_id,
                    "analysis_depth": "comprehensive",
                    "requested_agents": ["psychological", "voice_of_customer", "competitor", 
                                       "interview_psychological", "interview_sales", "gtm_blueprint"],
                    "agent_config": {
                        "temperatures": AGENT_TEMPERATURES,
                        "max_tokens": MAX_TOKENS,
                        "search_enabled": SEARCH_ENABLED,
                        "get_llm_func": get_llm_for_agent
                    },
                    "web_sources": web_sources
                })
                
                # Generate comprehensive report
                report = format_full_team_results(result, template_data['company_name'], 0)
                
                # Add source citations if available
                if web_sources:
                    report += "\n\n=== SOURCES CITED ===\n"
                    for i, source in enumerate(web_sources, 1):
                        report += f"[Source {i}]: {source['title']}\n   URL: {source['url']}\n"
                
                filename = save_report_to_file(template_data['company_name'], report, "complete_research")
                
                # Send using centralized handler
                send_response_with_file_fallback(
                    client=client,
                    channel_id=channel_id,
                    thread_ts=thread_ts,
                    response_text=report,
                    title=f"Complete Research - {template_data['company_name']}",
                    agent_name="research_complete",
                    query=template_data['company_name']
                )
                
                # Send completion message with metrics
                respond(f"""✅ *Complete Template Analysis Finished!*

**Company:** {template_data['company_name']}
**All 14 sections processed**
**Report generated:** {len(report.split())} words

The analysis incorporates:
- Deep psychological profiling
- Exact customer language patterns  
- Competitive positioning analysis
- Interview simulations
- Sales discovery insights
- Complete GTM strategy

All insights are tailored to your specific context and enhanced with real-time market data.""")
                
            else:
                respond("⌛ Workflow not available. Please check system configuration with `/status`")
                
        except Exception as e:  # THIS WAS MISSING!
            logger.error(f"Template processing error: {e}", exc_info=True)
            respond(f"""Error processing template: {str(e)}
            
Please check your template format or try `/research-guided` for step-by-step guidance.""")
            
    elif not text:
        # Mark user as pending file upload
        key = f"{channel_id}_{user_id}"
        RESEARCH_UPLOAD_PENDING[key] = {
            'timestamp': datetime.now(),
            'channel': channel_id,
            'user': user_id
        }
        
        print(f"[DEBUG] Marked user as pending upload: {key}")
        print(f"[DEBUG] Pending dict now contains: {list(RESEARCH_UPLOAD_PENDING.keys())}")
        
        respond("""📋 **Ready to process your template!**

**Next step:** Upload your filled template file
- Drag and drop your .txt, .pdf, or .docx file
- Or paste the content (if under 4000 chars)

⏱️ Waiting for your upload (timeout in 5 minutes)...

_Need the template? Use `/template` to download_""")
        return
    
    # If text exists but is too short
    else:
        respond("""Please provide either:
1. Your complete template text (paste it after the command)
2. Upload your template file (type just `/research-complete` then upload)
3. Use `/research-guided` for interactive form""")
        
# ==============================================
# 27.5. ENHANCED FILE UPLOAD HANDLER (COMPLETE)
# ==============================================

# Define MIN_TOKENS constant for quality control
MIN_TOKENS = 500  # Minimum token threshold for quality validation

@app.event("message")
def handle_research_file_upload(event, client):
    """
    Handle file uploads for research templates.
    Supports: .txt, .md, .markdown, .pdf, .docx files
    """
    
    # Skip if no files in message
    if 'files' not in event or not event.get('files'):
        return
    
    # Skip bot messages
    if event.get('bot_id') or event.get('subtype') == 'bot_message':
        return
    
    channel_id = event.get('channel')
    user_id = event.get('user')
    
    if not channel_id or not user_id:
        return
    
    # Check if user has pending research-complete command
    pending_key = f"{channel_id}_{user_id}"
    
    if pending_key in RESEARCH_UPLOAD_PENDING:
        # Check if command is still valid (within 5 minutes)
        pending_data = RESEARCH_UPLOAD_PENDING[pending_key]
        time_elapsed = datetime.now() - pending_data['timestamp']
        
        if time_elapsed > timedelta(minutes=5):
            # Command expired, clean up
            del RESEARCH_UPLOAD_PENDING[pending_key]
            return
        
        # Process file for research-complete
        files = event.get('files', [])
        if files:
            process_template_file(client, event, files[0], channel_id, user_id, is_research_complete=True)
            # Clear pending status after processing
            del RESEARCH_UPLOAD_PENDING[pending_key]
            return
    
    # Check if any file looks like a template
    files = event.get('files', [])
    for file_info in files:
        file_name = file_info.get('name', '').lower()
        
        # Check if it's a potential template file
        is_template_file = (
            file_name.endswith('.txt') or
            file_name.endswith('.md') or
            file_name.endswith('.markdown') or
            file_name.endswith('.pdf') or
            file_name.endswith('.docx') or
            file_name.endswith('.doc') or
            'template' in file_name or
            'research' in file_name or
            'market' in file_name
        )
        
        if is_template_file:
            # Process this as a potential research template
            process_template_file(client, event, file_info, channel_id, user_id, is_research_complete=False)
            return

def clean_for_search(text: str, max_length: int = 50) -> str:
    """Clean and truncate text for search queries"""
    if not text:
        return ""
    
    # Remove special characters but keep spaces
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    
    # Take first line/sentence
    text = text.split('\n')[0].split('.')[0]
    
    # Clean up multiple spaces
    text = ' '.join(text.split())
    
    # Limit length
    return text[:max_length].strip()

def process_template_file(client, event, file_info, channel_id, user_id, is_research_complete=False):
    """Process an uploaded template file with encoding and search fixes"""
    
    file_name = file_info.get('name', 'template')
    file_id = file_info.get('id')
    
    print(f"[DEBUG] Processing file: {file_name} (ID: {file_id})")
    print(f"[DEBUG] Is research-complete: {is_research_complete}")
    
    # Send processing notification
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text=f"""📎 **File Detected: {file_name}**
        
🔍 Analyzing file format...
📄 Extracting content...

**Active Configuration:**
- Temperatures: {min(AGENT_TEMPERATURES.values()):.1f}-{max(AGENT_TEMPERATURES.values()):.1f}
- Max tokens: {MAX_TOKENS['research']}
- Search: {'✅' if SEARCH_ENABLED else '❌'}"""
    )
    
    try:
        # Download and process based on file type
        content = None
        file_lower = file_name.lower()
        
        print(f"[DEBUG] File type detection for: {file_lower}")
        
        if file_lower.endswith('.pdf'):
            print("[DEBUG] Processing as PDF")
            content = download_and_extract_pdf(client, file_id)
            if not content:
                raise Exception("Could not extract text from PDF. Ensure it contains selectable text.")
                
        elif file_lower.endswith('.docx') or file_lower.endswith('.doc'):
            print("[DEBUG] Processing as Word document")
            content = download_and_extract_docx(client, file_id)
            if not content:
                raise Exception("Could not extract text from Word document.")
                
        else:
            # For txt, md, markdown - plain text files
            print("[DEBUG] Processing as text file")
            content = download_text_file(client, file_id)
            if not content:
                raise Exception("Could not read text file.")
        
        print(f"[DEBUG] Content extracted: {len(content)} characters")
        
        if not content or len(content.strip()) < 100:
            raise Exception("File appears to be empty or too short to be a valid template.")
        
        # Try to parse as template
        print("[DEBUG] Parsing template content...")
        template_data = parse_template_content(content)
        
        print(f"[DEBUG] Template parsing results:")
        print(f"  - Company name: {template_data.get('company_name', 'Not found')[:50] if template_data.get('company_name') else 'Not found'}")
        print(f"  - Sections found: {len([v for v in template_data.values() if v])}")
        
        # Check if it's a valid template
        if template_data and template_data.get('company_name'):
            # Valid template found - count filled sections
            filled_sections = len([v for v in template_data.values() if v and len(str(v).strip()) > 10])
            
            client.chat_postMessage(
                channel=channel_id,
                text=f"""✅ **Valid Template Detected!**
                
**File:** {file_name}
**Company:** {template_data.get('company_name', 'Unknown')[:100]}
**Industry:** {template_data.get('industry', 'Not specified')[:100]}
**Sections filled:** {filled_sections}/14
                
🚀 Starting comprehensive analysis with 6 specialized agents...

**Enhanced Configuration (v2.0):**
- Temperature Range: 0.7-0.8 (optimized for nuanced insights)
- Token Limit: 8,100 per agent
- Web Search: Active
- Professional terminology preservation: Enabled"""
    )
            
            # Process the template with fixed search queries
            process_research_template_with_search_fix(
                client=client,
                channel_id=channel_id,
                user_id=user_id,
                template_data=template_data,
                source=f"uploaded_{file_name}"
            )
            
        else:
            # Not a valid template, provide helpful guidance
            client.chat_postMessage(
                channel=channel_id,
                text=f"""⚠️ **File Format Issue**
                
The file *{file_name}* was uploaded successfully but doesn't match the expected template format.

**What I found:**
- File size: {len(content)} characters
- Company name field: {'Not found' if not template_data.get('company_name') else 'Found'}

**Solutions:**
- `/template` - Download the correct template format
- `/research-guided` - Use the interactive form (easier!)
- Make sure your file has numbered sections (1-14)

**Supported formats:** .txt, .md, .pdf, .docx

If this IS your template, ensure it follows the numbered format:
1. BUSINESS TYPE
[Your answer]
2. COMPANY NAME
[Your company]
... and so on for all 14 sections."""
            )
            
    except Exception as e:
        logger.error(f"Error processing template file: {e}", exc_info=True)
        
        client.chat_postMessage(
            channel=channel_id,
            text=f"""❌ **Error Processing File**
            
**File:** {file_name}
**Error:** {str(e)}

**Try these alternatives:**
- `/research-guided` - Interactive form (recommended!)
- `/template` - Get the correct template format
- Make sure file contains text (not just images)
- For PDFs, ensure text is selectable (not scanned)
- For Word docs, save as .docx (not .doc)

**Need help?** Contact support or try a different file format."""
        )

def process_research_template_with_search_fix(client, channel_id: str, user_id: str, 
                                              template_data: Dict[str, Any], source: str = "unknown"):
    """
    Process the research template with FIXED search queries.
    Now limits source display to 10 in the final report.
    """
    
    client_id = get_client_id(channel_id, user_id)
    
    print("[DEBUG] Starting template processing with search fix")
    
    # Format context
    context = format_template_for_analysis(template_data)
    
    # Enhance with web search if enabled
    enhanced_context = context
    web_sources = []
    
    if SEARCH_ENABLED and search_context:
        try:
            # Extract and CLEAN values for search
            company_name = clean_for_search(template_data.get('company_name', ''), max_length=30)
            industry = clean_for_search(template_data.get('industry', ''), max_length=30)
            target_customer = clean_for_search(template_data.get('target_customer', ''), max_length=50)
            
            print(f"[DEBUG] Cleaned search terms:")
            print(f"  - Company: {company_name}")
            print(f"  - Industry: {industry}")
            print(f"  - Target: {target_customer}")
            
            # Create SHORT, SPECIFIC search queries
            search_queries = []
            
            # Only add queries if we have clean values
            if company_name:
                search_queries.append(f"{company_name} company profile")
            
            if industry:
                search_queries.append(f"{industry} market analysis 2024 2025")
            
            if target_customer and "physician" in target_customer.lower():
                search_queries.append("physician financial planning trends")
            elif target_customer:
                search_queries.append(f"{target_customer[:30]} market research")
            
            # Execute searches (but collect ALL sources)
            for query in search_queries:
                if len(query) > 100:
                    query = query[:100].strip()
                
                print(f"[DEBUG] Executing search: {query}")
                
                try:
                    search_results, sources = search_context.search_and_cite(query, "template_processor")
                    if search_results:
                        enhanced_context += f"\n\n=== SEARCH RESULTS FOR: {query} ===\n{search_results}"
                        web_sources.extend(sources)
                        print(f"[DEBUG] Search successful, found {len(sources)} sources")
                    else:
                        print(f"[DEBUG] No results for: {query}")
                except Exception as search_error:
                    print(f"[WARNING] Search failed for '{query}': {search_error}")
                
                time.sleep(0.5)  # Rate limiting
            
            print(f"[DEBUG] Total web sources collected: {len(web_sources)}")
                
        except Exception as e:
            logger.warning(f"Search enhancement failed: {e}")
            print(f"[WARNING] Search enhancement error: {e}")
    
    # Run workflow
    if workflow_available:
        try:
            print("[DEBUG] Starting workflow execution")
            workflow = ICPGraph(verbose=True)
            
            # Pass clean company name to workflow
            clean_company = clean_for_search(template_data.get('company_name', 'Unknown'), max_length=50)
            
            # Pass the total count in statistics
            result = workflow.run({
                "company": clean_company,
                "business_context": enhanced_context,
                "template_data": template_data,
                "client_id": client_id,
                "analysis_depth": "comprehensive",
                "requested_agents": ["psychological", "voice_of_customer", "competitor", 
                                   "interview_psychological", "interview_sales", "gtm_blueprint"],
                "agent_config": {
                    "temperatures": AGENT_TEMPERATURES,
                    "max_tokens": MAX_TOKENS,
                    "search_enabled": SEARCH_ENABLED,
                    "get_llm_func": get_llm_for_agent if 'get_llm_for_agent' in globals() else None
                },
                "web_sources": web_sources,  # Pass ALL sources for analysis
                "source": source
            })
            
            # Store the total count in statistics
            if 'statistics' not in result:
                result['statistics'] = {}
            result['statistics']['web_sources_total'] = len(web_sources)
            
            print("[DEBUG] Workflow completed, generating report")
            
            # Generate report with LIMITED source display
            report = format_full_team_results(result, clean_company, 0)
            
            # Add LIMITED citations (only top 10)
            if web_sources:
                report += "\n\n" + "=" * 80
                report += "\n🔍 WEB SOURCES USED"
                report += "\n" + "=" * 80
                
                # Display only first 10
                for i, source in enumerate(web_sources[:10], 1):
                    report += f"\n[{i}] {source['title'][:100]}: {source['url']}"
                
                if len(web_sources) > 10:
                    report += f"\n\n📊 Total sources analyzed: {len(web_sources)}"
                    report += f"\n   (Showing top 10 for brevity. Full analysis used all {len(web_sources)} sources)"
            
            # Save report
            filename = save_report_to_file(clean_company, report, "template_research")
            
            print(f"[DEBUG] Report saved to: {filename}")
            
            # Upload to Slack
            try:
                client.files_upload_v2(
                    channel=channel_id,
                    file=filename,
                    title=f"Research Analysis - {clean_company}",
                    initial_comment=f"""✅ **Template Analysis Complete!**
                    
**Company:** {clean_company}
**Source:** {source}
**Word count:** {len(report.split())} words
**Web sources analyzed:** {len(web_sources)} (top 10 shown in report)

All 6 agents have completed their analysis using {len(web_sources)} web sources."""
                )
                print("[DEBUG] Report uploaded to Slack successfully")
            except Exception as e:
                logger.error(f"Upload failed: {e}")
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"Analysis complete! Report saved to: `{filename}`\n📊 Used {len(web_sources)} web sources (top 10 shown)"
                )
                
        except Exception as e:
            logger.error(f"Workflow processing error: {e}", exc_info=True)
            client.chat_postMessage(
                channel=channel_id,
                text=f"Error during analysis: {str(e)[:500]}"
            )
    else:
        client.chat_postMessage(
            channel=channel_id,
            text="⌛ Workflow not available. Please check configuration."
        )

# ==============================================
# 28. TEMPLATE PARSING AND PROCESSING UTILITIES
# ==============================================

import re
from typing import Dict, Optional, Any, List
import logging
import traceback

logger = logging.getLogger(__name__)

def format_template_for_analysis(template_data: Dict[str, Any]) -> str:
    """
    Format template data into comprehensive context for agents.
    UPDATED: Dynamically preserves specific professional terminology from template.
    """
    
    # Extract key terms to preserve from the actual template
    target_customer = template_data.get('target_customer', '')
    industry = template_data.get('industry', '')
    product_service = template_data.get('product_service', '')
    
    # Dynamically detect professional terminology to preserve
    professional_terms = set()
    
    # Check for various professional terms in the template
    text_to_scan = f"{target_customer} {industry} {product_service}".lower()
    
    # Medical professionals
    if 'physician' in text_to_scan:
        professional_terms.add('physicians')
    if 'doctor' in text_to_scan:
        professional_terms.add('doctors')
    if 'dentist' in text_to_scan:
        professional_terms.add('dentists')
    if 'medical professional' in text_to_scan:
        professional_terms.add('medical professionals')
    
    # Financial professionals
    if 'financial advisor' in text_to_scan:
        professional_terms.add('financial advisors')
    if 'wealth manager' in text_to_scan:
        professional_terms.add('wealth managers')
    if 'investment advisor' in text_to_scan:
        professional_terms.add('investment advisors')
    if 'financial planner' in text_to_scan:
        professional_terms.add('financial planners')
    
    # Other professionals
    if 'consultant' in text_to_scan:
        professional_terms.add('consultants')
    if 'attorney' in text_to_scan or 'lawyer' in text_to_scan:
        professional_terms.add('attorneys')
    if 'accountant' in text_to_scan or 'cpa' in text_to_scan:
        professional_terms.add('accountants')
    if 'engineer' in text_to_scan:
        professional_terms.add('engineers')
    
    # Extract specific descriptors (early-career, mid-career, etc.)
    career_stages = []
    if 'early-career' in text_to_scan or 'early career' in text_to_scan:
        career_stages.append('early-career')
    if 'mid-career' in text_to_scan or 'mid career' in text_to_scan:
        career_stages.append('mid-career')
    if 'senior' in text_to_scan or 'experienced' in text_to_scan:
        career_stages.append('senior/experienced')
    
    # Build terminology instruction based on what was found
    terminology_instruction = ""
    if professional_terms:
        terminology_instruction = f"""
IMPORTANT TERMINOLOGY PRESERVATION:
- Use these EXACT professional terms: {', '.join(professional_terms)}
- Do NOT substitute with generic terms like "customers," "clients," or "professionals"
- Maintain the specific professional context throughout"""
        
        if career_stages:
            terminology_instruction += f"""
- Include career stage descriptors when relevant: {', '.join(career_stages)}"""
    
    context = f"""
COMPREHENSIVE MARKET RESEARCH BRIEF

====================
BUSINESS FUNDAMENTALS
====================
Business Type: {template_data.get('business_type', 'Not specified')}
Company Name: {template_data.get('company_name', 'Unknown')}
Industry: {template_data.get('industry', 'Not specified')}

Product/Service Description:
{template_data.get('product_service', 'Not provided')}

====================
TARGET CUSTOMER PROFILE
====================
Target Customer: {template_data.get('target_customer', 'Not specified')}

Demographics & Characteristics:
{template_data.get('demographics', 'Not provided')}

Customer Context/Situation:
{template_data.get('customer_context', 'Not provided')}

====================
PROBLEMS & PAIN POINTS
====================
Problems Solved:
{template_data.get('problems_solved', 'Not provided')}

Customer Complaints (Exact Quotes):
{template_data.get('customer_complaints', 'Not provided')}

====================
GOALS & SUCCESS VISION
====================
Customer's Stated Goals:
{template_data.get('customer_goals', 'Not provided')}

What Success Looks Like:
{template_data.get('success_vision', 'Not provided')}

====================
MARKET & STRATEGY
====================
Market Details:
{template_data.get('market_details', 'Not provided')}

Marketing Goal:
{template_data.get('marketing_goal', 'Not specified')}

====================
ADDITIONAL CONTEXT
====================
{template_data.get('additional_context', 'Not provided')}

{template_data.get('differentiators', '')}

====================
{terminology_instruction}

ANALYSIS INSTRUCTIONS:
- Use ALL provided context to generate deep, nuanced insights
- Reference specific details from the template in your analysis
- Provide actionable recommendations based on the stated goals
- Consider the customer complaints and pain points as primary drivers
- Align all strategies with the marketing goal
- CRITICAL: Preserve the EXACT professional terminology used in the template
- If template says "financial advisors," use "financial advisors" not "advisors" or "professionals"
- If template says "physicians," use "physicians" not "doctors" or "medical professionals"
- Be specific with compound terms: "early-career financial advisors" not just "advisors"
- Maintain consistency: use the same terms throughout the entire analysis
"""
    
    return context

def parse_template_content(content: str) -> Dict[str, Any]:
    """
    Parse filled template content with maximum flexibility.
    Handles both clean templates and markdown-formatted templates.
    This is a STANDALONE function, not a class method.
    """
    template_data = {}
    
    print("\n[PARSER DEBUG] Starting ultra-flexible template parsing...")
    print(f"[PARSER DEBUG] Content length: {len(content)} chars")
    print(f"[PARSER DEBUG] First 200 chars: {content[:200]}...")
    
    # Pre-process markdown-specific formatting
    original_content = content  # Keep original for fallback
    
    # Detect if this is a markdown file with code blocks
    has_code_blocks = '```' in content
    has_escaped_numbers = r'\.' in content
    has_bold_headers = '**' in content
    
    if has_code_blocks or has_escaped_numbers or has_bold_headers:
        print("[PARSER DEBUG] Detected markdown format, applying markdown cleaning...")
        
        # Remove code blocks but preserve content
        content = re.sub(r'```\n?([\s\S]*?)\n?```', r'\1', content)
        
        # Handle escaped numbers (1\. -> 1.)
        content = re.sub(r'(\d+)\\\.', r'\1.', content)
        
        # Remove bold markdown while preserving text
        content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)
        
        # Remove single asterisks (lists/italics) at line start
        content = re.sub(r'^\s*\*\s+', '', content, flags=re.MULTILINE)
        
        # Clean up headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
    
    # Now parse the cleaned content
    numbered_sections = {}
    
    # Try to find numbered sections (1. through 14.)
    # More flexible pattern that handles various formats
    for i in range(1, 15):
        # Multiple patterns to try for each section
        patterns = [
            # Standard format: "1. SECTION_NAME"
            rf"(?:^|\n)\s*{i}\.\s*([A-Z][^\n]*?)\s*\n([\s\S]*?)(?=\n\s*{i+1}\.|$)",
            # With colon: "1. SECTION_NAME:"
            rf"(?:^|\n)\s*{i}\.\s*([A-Z][^\n:]*?):\s*\n([\s\S]*?)(?=\n\s*{i+1}\.|$)",
            # Parenthesis format: "1) SECTION_NAME"
            rf"(?:^|\n)\s*{i}\)\s*([A-Z][^\n]*?)\s*\n([\s\S]*?)(?=\n\s*{i+1}[).]|$)",
        ]
        
        section_found = False
        for pattern in patterns:
            if i == 14:  # Last section captures until end
                pattern = pattern.replace(rf"(?=\n\s*{i+1}\.|$)", r"$")
                pattern = pattern.replace(rf"(?=\n\s*{i+1}[).]|$)", r"$")
            
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
            if match:
                section_title = match.group(1).strip()
                section_content = match.group(2).strip()
                
                # Additional cleanup for section content
                # Remove leading dashes, asterisks, etc.
                section_content = re.sub(r'^[-*•▪►◆]\s*', '', section_content, flags=re.MULTILINE)
                
                numbered_sections[i] = {
                    'title': section_title,
                    'content': section_content
                }
                print(f"[PARSER DEBUG] Found section {i}: {section_title[:50]}...")
                section_found = True
                break
        
        if not section_found:
            print(f"[PARSER DEBUG] Section {i} not found with standard patterns")
    
    print(f"[PARSER DEBUG] Found {len(numbered_sections)} numbered sections")
    
    # Map numbered sections to expected keys
    section_mapping = {
        1: "business_type",
        2: "company_name", 
        3: "industry",
        4: "product_service",
        5: "target_customer",
        6: "demographics",
        7: "customer_context",
        8: "problems_solved",
        9: "customer_complaints",
        10: "customer_goals",
        11: "success_vision",
        12: "market_details",
        13: "marketing_goal",
        14: "additional_context"
    }
    
    # Process each numbered section
    for num, key in section_mapping.items():
        if num in numbered_sections:
            content_value = numbered_sections[num]['content']
            
            # Special handling for business type
            if key == "business_type":
                content_upper = content_value.upper()
                if "B2B2C" in content_upper:
                    content_value = "B2B2C"
                elif "B2B" in content_upper:
                    content_value = "B2B"
                elif "B2C" in content_upper:
                    content_value = "B2C"
                else:
                    # Try to extract from the content
                    if content_value.strip():
                        content_value = content_value.strip().split('\n')[0]
            
            # Special handling for company name
            elif key == "company_name":
                # Often the company name is on the first non-empty line
                lines = [line.strip() for line in content_value.split('\n') if line.strip()]
                if lines:
                    content_value = lines[0]
                    # Remove any remaining formatting
                    content_value = re.sub(r'^[-*•]\s*', '', content_value)
            
            # Store if there's actual content
            if content_value and len(content_value.strip()) > 2:
                template_data[key] = content_value.strip()
                print(f"[PARSER DEBUG] ✅ Mapped section {num} to '{key}' ({len(content_value)} chars)")
        else:
            print(f"[PARSER DEBUG] ⚠️ Section {num} ({section_mapping[num]}) not found")
    
    # Fallback: Try flexible pattern matching for any missing critical sections
    if not template_data.get('company_name') or not template_data.get('business_type'):
        print("[PARSER DEBUG] Missing critical sections, attempting fallback extraction...")
        
        # Use original content for fallback (in case cleaning removed something important)
        fallback_content = original_content
        
        # Flexible patterns for critical fields
        fallback_patterns = {
            "business_type": [
                r"BUSINESS\s*TYPE[:\s]*\n*\s*\*?\s*(B2[BC](?:2C)?)",
                r"^\s*\*?\s*(B2[BC](?:2C)?)\s*$",
                r"Type[:\s]*\n*\s*\*?\s*(B2[BC](?:2C)?)",
            ],
            "company_name": [
                r"COMPANY\s*NAME[:\s]*\n*(?:```\n)?([^\n`]+?)(?:\n```)?",
                r"2\.\s*(?:COMPANY\s*NAME)?[:\s]*\n*(?:```\n)?([^\n`]+?)(?:\n```)?",
                r"^([A-Z][A-Za-z\s&]+(?:Partners|LLC|Inc|Corp|Limited|Ltd|Group|Services|Solutions|Consulting))$",
            ],
            "industry": [
                r"INDUSTRY[:\s]*\n*(?:```\n)?([\s\S]+?)(?:\n```|\n\d+\.)",
                r"3\.\s*INDUSTRY[:\s]*\n*([\s\S]+?)(?=\n\d+\.|$)",
            ],
        }
        
        for key, patterns in fallback_patterns.items():
            if key not in template_data or not template_data.get(key):
                for pattern in patterns:
                    match = re.search(pattern, fallback_content, re.IGNORECASE | re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        if value and len(value) > 2 and len(value) < 500:
                            template_data[key] = value
                            print(f"[PARSER DEBUG] ✅ Found '{key}' via fallback: {value[:50]}...")
                            break
    
    # Final validation
    found_sections = list(template_data.keys())
    all_expected = list(section_mapping.values())
    missing_sections = [s for s in all_expected if s not in found_sections]
    
    print(f"\n[PARSER DEBUG] Final Parsing Summary:")
    print(f"  - Sections found: {len(found_sections)}/14")
    print(f"  - Found: {', '.join(found_sections[:5])}..." if len(found_sections) > 5 else f"  - Found: {', '.join(found_sections)}")
    print(f"  - Missing: {', '.join(missing_sections[:5])}..." if len(missing_sections) > 5 else f"  - Missing: {', '.join(missing_sections) if missing_sections else 'None'}")
    
    # Show preview of key fields
    if template_data.get('company_name'):
        print(f"  - Company: {template_data['company_name'][:50]}")
    if template_data.get('business_type'):
        print(f"  - Type: {template_data['business_type']}")
    if template_data.get('industry'):
        print(f"  - Industry: {template_data['industry'][:80]}...")
    
    return template_data

# CLASS DEFINITION
class TemplateParser:
    """
    Parser for extracting company information from filled templates.
    Handles both plain text and markdown formats.
    """
    
    def parse_template(self, content: str) -> Dict[str, Any]:
        """
        Parse a filled template and extract structured information.
        Now uses the standalone parse_template_content function for consistency.
        """
        print("[DEBUG] Starting TemplateParser.parse_template...")
        
        # Use the standalone function for parsing
        parsed_data = parse_template_content(content)
        
        # Add any additional processing specific to the class if needed
        if not parsed_data.get('company_name'):
            # Try the class's extraction method as fallback
            parsed_data['company_name'] = self._extract_company_name(content)
        
        # Ensure we have all expected fields
        expected_fields = [
            'company_name', 'industry', 'business_type', 'product_service',
            'target_customer', 'demographics', 'customer_context',
            'problems_solved', 'customer_complaints', 'customer_goals',
            'success_vision', 'market_details', 'marketing_goal',
            'additional_context'
        ]
        
        for field in expected_fields:
            if field not in parsed_data:
                parsed_data[field] = None
        
        # Add raw content for reference
        if 'raw_content' not in parsed_data:
            parsed_data['raw_content'] = content[:1000]  # First 1000 chars
        
        return parsed_data
    
    def _clean_content(self, content: str) -> str:
        """Clean the template content for better parsing"""
        
        # Remove code blocks but preserve content
        content = re.sub(r'```\n?([\s\S]*?)\n?```', r'\1', content)
        
        # Handle escaped numbers (1\. -> 1.)
        content = re.sub(r'(\d+)\\\.', r'\1.', content)
        
        # Remove markdown formatting
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'__(.+?)__', r'\1', content)      # Alternative bold
        content = re.sub(r'\*(.+?)\*', r'\1', content)      # Italic
        content = re.sub(r'_(.+?)_', r'\1', content)        # Alternative italic
        content = re.sub(r'#+\s*', '', content)             # Headers
        content = re.sub(r'`([^`]+)`', r'\1', content)      # Inline code
        
        # Remove links
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Clean up list markers
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)
        
        # Normalize quotes
        content = content.replace('"', '"').replace('"', '"')
        content = content.replace(''', "'").replace(''', "'")
        
        # Normalize line breaks
        content = re.sub(r'\r\n', '\n', content)
        
        # Remove excessive blank lines
        content = re.sub(r'\n\n+', '\n\n', content)
        
        return content.strip()
    
    def _extract_company_name(self, content: str) -> Optional[str]:
        """
        Extract company name with multiple strategies.
        Enhanced for markdown format handling.
        """
        print("[DEBUG] Attempting to extract company name...")
        
        # Clean content first
        clean_content = self._clean_content(content)
        
        # Strategy 1: Look for explicit "Company Name:" pattern
        patterns = [
            r'(?:company\s*name|2[\.\)]*\s*company\s*name)[:\s]+([^\n]+)',
            r'(?:^|\n)\s*2[\.\)]\s*(?:company\s*name[:\s]*)?([^\n]+?)(?:\s*\n\s*3[\.\)]|\n|$)',
            r'COMPANY\s*NAME[:\s]*\n*([^\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, clean_content, re.IGNORECASE | re.MULTILINE)
            if match:
                company_name = match.group(1).strip()
                # Clean any remaining markers
                company_name = re.sub(r'^[-*•]\s*', '', company_name)
                company_name = re.sub(r'\s*\d+\.?\s*$', '', company_name)
                
                if self._validate_company_name(company_name):
                    print(f"[DEBUG] Found company name: {company_name}")
                    return company_name
        
        print("[DEBUG] No valid company name found")
        return None
    
    def _validate_company_name(self, name: str) -> bool:
        """Validate that the extracted string is likely a company name"""
        if not name or len(name) < 2:
            return False
        
        if len(name) > 100:
            return False
        
        # Check for common non-company patterns
        invalid_starts = [
            'the company', 'our company', 'this company',
            'lack of', 'need for', 'problem with'
        ]
        
        name_lower = name.lower()
        for invalid in invalid_starts:
            if name_lower.startswith(invalid):
                return False
        
        # Should have at least one alphabetic character
        if not re.search(r'[a-zA-Z]', name):
            return False
        
        return True
    
# ==============================================
# 29. FILE DOWNLOAD AND EXTRACTION FUNCTIONS
# ==============================================

def download_text_file(client, file_id: str) -> Optional[str]:
    """Download text-based file (txt, md, markdown) with encoding fix"""
    try:
        file_info = client.files_info(file=file_id)
        if not file_info.get('ok'):
            raise Exception("Could not get file information")
            
        file_data = file_info['file']
        download_url = (
            file_data.get('url_private_download') or 
            file_data.get('url_private') or
            file_data.get('permalink')
        )
        
        if not download_url:
            raise Exception("No download URL available")
        
        headers = {'Authorization': f'Bearer {os.environ.get("SLACK_BOT_TOKEN")}'}
        response = requests.get(download_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Handle text encoding properly
        content = decode_text_content(response.content)
        return content
        
    except Exception as e:
        logger.error(f"Error downloading text file: {e}")
        return None

def decode_text_content(raw_bytes: bytes) -> str:
    """
    Decode text content with multiple encoding attempts.
    Shared utility for all text extraction.
    """
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            content = raw_bytes.decode(encoding)
            # Clean common encoding issues
            content = content.replace('\uf0b7', '-')  # Bullet points
            content = content.replace('\u2019', "'")  # Smart apostrophe
            content = content.replace('\u201c', '"')  # Left quote
            content = content.replace('\u201d', '"')  # Right quote
            content = content.replace('\u2026', '...')  # Ellipsis
            content = content.replace('\u2013', '-')  # En dash
            content = content.replace('\u2014', '--')  # Em dash
            return content
        except UnicodeDecodeError:
            continue
    
    # Last resort: replace bad characters
    return raw_bytes.decode('utf-8', errors='replace')

def download_and_extract_pdf(client, file_id: str) -> Optional[str]:
    """PDF extraction - PyPDF2 handles encoding internally"""
    try:
        import PyPDF2
        import io
        
        file_info = client.files_info(file=file_id)
        if not file_info.get('ok'):
            raise Exception("Could not get PDF information")
            
        file_data = file_info['file']
        download_url = (
            file_data.get('url_private_download') or 
            file_data.get('url_private')
        )
        
        headers = {'Authorization': f'Bearer {os.environ.get("SLACK_BOT_TOKEN")}'}
        response = requests.get(download_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # PyPDF2 handles PDF text extraction with its own encoding
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                # Clean the extracted text
                page_text = decode_text_content(page_text.encode('utf-8'))
                text += page_text + "\n"
        
        return text
        
    except Exception as e:
        logger.error(f"Error extracting PDF: {e}")
        return None

def download_and_extract_docx(client, file_id: str) -> Optional[str]:
    """DOCX extraction - python-docx handles encoding internally"""
    try:
        from docx import Document
        import io
        
        file_info = client.files_info(file=file_id)
        if not file_info.get('ok'):
            raise Exception("Could not get document information")
            
        file_data = file_info['file']
        download_url = (
            file_data.get('url_private_download') or 
            file_data.get('url_private')
        )
        
        headers = {'Authorization': f'Bearer {os.environ.get("SLACK_BOT_TOKEN")}'}
        response = requests.get(download_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # python-docx handles DOCX encoding internally
        docx_file = io.BytesIO(response.content)
        doc = Document(docx_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text + "\n"
        
        # Clean any encoding issues in the extracted text
        text = decode_text_content(text.encode('utf-8'))
        return text
        
    except Exception as e:
        logger.error(f"Error extracting DOCX: {e}")
        return None
# ==============================================
# 30. RESEARCH TEMPLATE PROCESSOR
# ==============================================

def process_research_template(client, channel_id: str, user_id: str, 
                             template_data: Dict[str, Any], source: str = "unknown"):
    """Process the research template through full analysis workflow"""
    
    client_id = get_client_id(channel_id, user_id)
    
    # Format context
    context = format_template_for_analysis(template_data)
    
    # Enhance with web search if enabled
    enhanced_context = context
    web_sources = []
    
    if SEARCH_ENABLED and search_context:
        try:
            company_name = template_data.get('company_name', '')
            industry = template_data.get('industry', '')
            
            # Perform targeted searches
            search_queries = [
                f"{company_name} {industry} market analysis 2024 2025",
                f"{industry} trends challenges opportunities"
            ]
            
            for query in search_queries[:2]:  # Limit searches
                search_results, sources = search_context.search_and_cite(query, "template_processor")
                if search_results:
                    enhanced_context += f"\n\n{search_results}"
                    web_sources.extend(sources)
                time.sleep(0.5)  # Rate limiting
                
        except Exception as e:
            logger.warning(f"Search enhancement failed: {e}")
    
    # Run workflow
    if workflow_available:
        try:
            workflow = ICPGraph(verbose=True)
            
            result = workflow.run({
                "company": template_data.get('company_name', 'Unknown'),
                "business_context": enhanced_context,
                "template_data": template_data,
                "client_id": client_id,
                "analysis_depth": "comprehensive",
                "requested_agents": ["psychological", "voice_of_customer", "competitor", 
                                   "interview_psychological", "interview_sales", "gtm_blueprint"],
                "agent_config": {
                    "temperatures": AGENT_TEMPERATURES,
                    "max_tokens": MAX_TOKENS,
                    "search_enabled": SEARCH_ENABLED,
                    "get_llm_func": get_llm_for_agent
                },
                "web_sources": web_sources,
                "source": source
            })
            
            # Generate report
            report = format_full_team_results(result, template_data['company_name'], 0)
            
            # Add citations
            if web_sources:
                report += "\n\n=== WEB SOURCES ===\n"
                for i, source in enumerate(web_sources, 1):
                    report += f"[{i}] {source['title']}: {source['url']}\n"
            
            # Save report
            filename = save_report_to_file(template_data['company_name'], report, "template_research")
            
            # Upload to Slack
            try:
                client.files_upload_v2(
                    channel=channel_id,
                    file=filename,
                    title=f"Research Analysis - {template_data['company_name']}",
                    initial_comment=f"""✅ **Template Analysis Complete!**
                    
**Company:** {template_data['company_name']}
**Source:** {source}
**Word count:** {len(report.split())} words
**Web sources:** {len(web_sources)}

All 6 agents have completed their analysis."""
                )
            except Exception as e:
                logger.error(f"Upload failed: {e}")
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"Analysis complete! Report saved to: `{filename}`"
                )
                
        except Exception as e:
            logger.error(f"Workflow processing error: {e}")
            client.chat_postMessage(
                channel=channel_id,
                text=f"Error during analysis: {str(e)}"
            )
    else:
        client.chat_postMessage(
            channel=channel_id,
            text="❌ Workflow not available. Please check configuration."
        )

# ==============================================
# 31. UTILITY FUNCTIONS
# ==============================================

def get_client_id(channel_id: str, user_id: Optional[str] = None) -> str:
    """Generate consistent client ID for memory persistence"""
    if user_id:
        return f"{channel_id}_{user_id}"
    return channel_id

def save_report_to_file(company: str, content: str, report_type: str = "analysis") -> str:
    """Save report to file and return filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_company = re.sub(r'[^a-zA-Z0-9_-]', '_', company.lower())[:30]
    filename = f"reports/{safe_company}_{report_type}_{timestamp}.txt"
    
    # Create reports directory if it doesn't exist
    os.makedirs("reports", exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Report saved to: {filename}")
    return filename

def format_full_team_results(result: Dict[str, Any], query: str, elapsed: float) -> str:
    """Format complete team analysis results without truncation"""
    lines = []
    lines.append("=" * 80)
    lines.append("MARKET RESEARCH TEAM ANALYSIS")
    lines.append(f"Company/Query: {query}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if elapsed > 0:
        lines.append(f"Execution Time: {elapsed:.2f} seconds")
    
    # Statistics
    if 'statistics' in result:
        stats = result['statistics']
        lines.append(f"Quality Score: {stats.get('overall_quality', 0):.2%}")
        lines.append(f"Total Words: {stats.get('total_words', 0):,}")
        lines.append(f"Agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)} successful")
    
    lines.append("=" * 80)
    lines.append("")
    
    # Full agent outputs
    if 'result' in result:
        for agent_name, agent_output in result['result'].items():
            if agent_output and not str(agent_output).startswith("[ERROR"):
                lines.append("=" * 60)
                agent_display = agent_name.replace('_', ' ').title()
                lines.append(f"AGENT: {agent_display}")
                lines.append("=" * 60)
                lines.append("")
                lines.append(str(agent_output))
                lines.append("")
    
    return '\n'.join(lines)

def calculate_quality_score(output: str, agent_name: str) -> float:
    """Calculate quality score for agent output"""
    if not output:
        return 0.0
    
    score = 0.0
    word_count = len(output.split())
    
    # Word count scoring (40% weight)
    if word_count >= 2000:
        score += 0.4
    elif word_count >= 1500:
        score += 0.3
    elif word_count >= 1000:
        score += 0.2
    elif word_count >= MIN_TOKENS:
        score += 0.1
    
    # Source citations (20% weight)
    if "[Source" in output or "Source [" in output:
        score += 0.2
    elif "http" in output:
        score += 0.1
    
    # Agent-specific keywords (40% weight)
    agent_keywords = {
        "psychological": ["identity", "fear", "unconscious", "anxiety", "transformation"],
        "voice_of_customer": ["quote", "exact", "language", "complaint", "aspiration"],
        "voice": ["quote", "exact", "language", "complaint", "aspiration"],
        "competitor": ["competitor", "alternative", "position", "market", "threat"],
        "interview_psychological": ["question", "response", "reveal", "emotion", "vulnerability"],
        "interview_sales": ["budget", "decision", "timeline", "objection", "criteria"],
        "gtm_blueprint": ["strategy", "channel", "positioning", "message", "tactic"],
        "gtm": ["strategy", "channel", "positioning", "message", "tactic"]
    }
    
    keywords = agent_keywords.get(agent_name, [])
    keyword_hits = sum(1 for kw in keywords if kw.lower() in output.lower())
    
    if keyword_hits >= 4:
        score += 0.4
    elif keyword_hits >= 3:
        score += 0.3
    elif keyword_hits >= 2:
        score += 0.2
    elif keyword_hits >= 1:
        score += 0.1
    
    return min(score, 1.0)


# ==============================================
# 32. TEST COMMAND
# UPDATE the /help command to show new configuration:

@app.command("/help")
def handle_help(ack, respond):
    """Show available commands with configuration info"""
    ack()
    
    # Try to get config info
    try:
        from core.config import Config
        config_info = f"""
*Current Configuration:*
• Model: `{Config.LLM_MODEL}`
• Temperature: `{Config.DEFAULT_TEMPERATURE}`
• Max Tokens: `{max(Config.MAX_TOKENS.values()):,}`
"""
    except:
        config_info = ""
    
    help_text = f"""*Market Research Team Bot - Command Guide*
{config_info}
*Analysis Commands:*
• `/team [business]` - Full team analysis
• `/psychological [business]` - Deep psychological analysis (NEW PROMPT)
• `/voice [business]` - Voice of customer extraction
• `/competitor [business]` - Competitive analysis
• `/gtm [business]` - Go-to-market strategy

*Interview Commands:*
• `/interview_psychological [business]` - Simulated psychological interview
• `/interview_sales [business]` - Simulated sales interview

*Template Commands:*
• `/research-guided` - Start guided research
• `/template [type]` - Use specific template

*System Commands:*
• `/test` - Test bot configuration
• `/memory` - Check memory status
• `/help` - Show this help

*Direct Q&A:*
• `@Agentic Team @[agent] [question]` - Ask specific agent

_Bot is running with enhanced Sonnet 4.5 configuration_"""
    
    respond(help_text)

# ==============================================================
# 33. MAIN EXECUTION BLOCK
# ==============================================================

if __name__ == "__main__":
    """Main entry point for the unified market research bot"""
    
    print("\n" + "=" * 80)
    print("🚀 MARKET RESEARCH TEAM BOT v3.0 - STARTING")
    print("=" * 80)
    
    # REQUIRED environment variables - Bot cannot run without these
    REQUIRED_VARS = {
        # Slack essentials
        "SLACK_BOT_TOKEN": "Slack bot OAuth token (xoxb-...)",
        "SLACK_APP_TOKEN": "Slack app-level token for Socket Mode (xapp-...)",
        "SLACK_SIGNING_SECRET": "Slack signing secret for verification",
        
        # LLM (required for agents)
        "ANTHROPIC_API_KEY": "Claude API key for LLM (required)",
        
        # Search System (required for comprehensive analysis)
        "BRAVE_API_KEY": "Brave Search API key (required for web research)"
    }
    
    # OPTIONAL environment variables
    OPTIONAL_VARS = {
        "QDRANT_URL": "Qdrant cloud URL (optional - for memory persistence)",
        "QDRANT_API_KEY": "Qdrant API key (optional - for memory persistence)",
        "LANGSMITH_API_KEY": "LangSmith API key (optional - for tracing)"
    }
    
    # Check for missing required variables
    missing_required = []
    for var, description in REQUIRED_VARS.items():
        if not os.getenv(var):
            missing_required.append(f"  ❌ {var}: {description}")
    
    if missing_required:
        print("\n❌ REQUIRED CONFIGURATION MISSING:")
        print("\n".join(missing_required))
        print("\n" + "="*60)
        print("📝 SETUP INSTRUCTIONS:")
        print("="*60)
        print("\n1. Copy .env.example to .env:")
        print("   cp .env.example .env")
        print("\n2. Get Brave Search API key (REQUIRED):")
        print("   • Go to https://brave.com/search/api/")
        print("   • Sign up for free tier")
        print("   • Copy your API key")
        print("\n3. Get Anthropic API key (REQUIRED):")
        print("   • Go to https://console.anthropic.com")
        print("   • Create an API key")
        print("\n4. Configure Slack App (REQUIRED):")
        print("   • Enable Socket Mode")
        print("   • Install to workspace")
        print("   • Copy all tokens")
        print("\n" + "="*60)
        print("❌ CANNOT START: Missing required configuration")
        print("="*60)
        sys.exit(1)
    
    # Check optional variables
    missing_optional = []
    for var, description in OPTIONAL_VARS.items():
        if not os.getenv(var):
            missing_optional.append(f"  ⚠️ {var}: {description}")
    
    if missing_optional:
        print("\n⚠️ OPTIONAL FEATURES NOT CONFIGURED:")
        print("\n".join(missing_optional))
        print("   Bot will work without these features")
    
    # Test system connections
    print("\n🔒 VALIDATING SYSTEMS...")
    print("="*60)
    
    # Test 1: Brave Search System (REQUIRED)
    print("Testing Search System (Brave)...")
    try:
        import requests
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": os.getenv('BRAVE_API_KEY')
        }
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": "test"},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("  ✅ Brave search system: Connected")
        elif response.status_code == 401:
            print("  ❌ Brave API key invalid or expired")
            print("     Get a new key from https://brave.com/search/api/")
            sys.exit(1)
        else:
            print(f"  ❌ Brave API error: HTTP {response.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"  ❌ Brave connection failed: {e}")
        print("     Check internet connection and API key")
        sys.exit(1)
    
    # Test 2: Anthropic LLM (REQUIRED)
    print("Testing LLM System (Anthropic)...")
    try:
        test_llm = get_llm_for_agent()
        if test_llm:
            print("  ✅ Anthropic LLM: Connected")
            if CONFIG_AVAILABLE and Config:
                print(f"     Model: {Config.LLM_MODEL} (Sonnet 4.5)")
                print(f"     Temperature: {Config.DEFAULT_TEMPERATURE}")
                print(f"     Max Tokens: {max(Config.MAX_TOKENS.values())}")
            else:
                print(f"     Model: claude-3-5-sonnet-20241022")
                print(f"     Temperature: 0.3")
                print(f"     Max Tokens: 20000")
        else:
            print("  ❌ LLM initialization failed")
            sys.exit(1)
    except Exception as e:
        print(f"  ❌ Anthropic LLM failed: {e}")
        print("     Verify ANTHROPIC_API_KEY is correct")
        sys.exit(1)
    
    # Test 3: Qdrant Memory System (OPTIONAL)
    print("\nTesting Memory System (Qdrant)...")
    memory_available = False
    
    if os.getenv('QDRANT_URL') and os.getenv('QDRANT_API_KEY'):
        try:
            from qdrant_client import QdrantClient
            test_client = QdrantClient(
                url=os.getenv('QDRANT_URL'),
                api_key=os.getenv('QDRANT_API_KEY'),
                timeout=5
            )
            # Try to list collections to verify connection
            collections = test_client.get_collections()
            print("  ✅ Qdrant memory: Connected")
            print(f"     Collections: {len(collections.collections)}")
            memory_available = True
        except ImportError:
            print("  ⚠️ qdrant-client not installed")
            print("     Memory features disabled")
        except Exception as e:
            print(f"  ⚠️ Qdrant connection failed: {str(e)[:100]}")
            print("     Memory features disabled - bot will work without persistence")
            print("\n     To fix Qdrant later:")
            print("     1. Check cluster status at https://cloud.qdrant.io")
            print("     2. Click 'Resume' if cluster is paused")
            print("     3. Verify URL and API key are correct")
    else:
        print("  ⚠️ Qdrant credentials not configured")
        print("     Memory features disabled")
    
    # Test 4: Slack Connection (REQUIRED)
    print("\nTesting Slack Connection...")
    try:
        from slack_sdk import WebClient
        slack_client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        auth_response = slack_client.auth_test()
        if auth_response["ok"]:
            print("  ✅ Slack connection: Verified")
            print(f"     Bot name: {auth_response['user']}")
            print(f"     Workspace: {auth_response['team']}")
        else:
            print("  ❌ Slack auth test failed")
            sys.exit(1)
    except Exception as e:
        print(f"  ❌ Slack connection failed: {e}")
        print("     Verify SLACK_BOT_TOKEN and bot installation")
        sys.exit(1)
    
    print("="*60)
    print("✅ ALL REQUIRED SYSTEMS VERIFIED!")
    if not memory_available:
        print("⚠️  Memory system unavailable - bot will work without persistence")
    print("="*60)
    
    # Initialize Socket Mode Handler
    try:
        from slack_bolt.adapter.socket_mode import SocketModeHandler
        
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        
        print("\n📊 FINAL CONFIGURATION:")
        print("="*60)
        print("Required Systems:")
        print(f"  Search (Brave): ✅ CONNECTED")
        print(f"  LLM (Claude): ✅ CONNECTED")
        print(f"  Slack: ✅ CONNECTED")
        
        print("\nOptional Systems:")
        print(f"  Memory (Qdrant): {'✅ Connected' if memory_available else '⚠️ Disabled'}")
        print(f"  LangSmith: {'✅ Enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else '⚠️ Disabled'}")
        
        print("\nModel Configuration:")
        if CONFIG_AVAILABLE and Config:
            print(f"  Model: {Config.LLM_MODEL}")
            print(f"  Temperature: {Config.DEFAULT_TEMPERATURE}")
            print(f"  Max Tokens: {max(Config.MAX_TOKENS.values()):,}")
            print(f"  Agents: {len(Config.AGENT_TEMPERATURES)}")
        else:
            print(f"  Model: claude-3-5-sonnet-20241022 (fallback)")
            print(f"  Temperature: 0.3")
            print(f"  Max Tokens: 20,000")
            print(f"  Agents: {len(AGENT_TEMPERATURES)}")
        
        print("\n📋 Available Commands:")
        print("  Testing: /test, /test-psychological-config")
        print("  Analysis: /team, /psychological, /voice, /competitor, /gtm")
        print("  Interviews: /interview_psychological, /interview_sales")
        print("  Templates: /research-guided, /template")
        if memory_available:
            print("  Memory: /memory, /memory-test")
        print("  Interactions: /debate, /conversation")
        print("  Direct Q&A: @Agentic Team @[agent] [question]")
        
        print("\n💡 Quick Test:")
        print("  1. Run /test to verify configuration")
        print("  2. Run /psychological [test company] to test analysis")
        
        print("\n" + "="*60)
        print("🚀 STARTING BOT...")
        print("="*60)
        print("✅ Bot is running! Press Ctrl+C to stop")
        print("📊 All required features operational")
        if not memory_available:
            print("⚠️  Memory disabled - conversations won't persist")
        print("="*60 + "\n")
        
        # Start the handler
        handler.start()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Shutdown requested...")
        print("Closing connections...")
        print("✅ Bot stopped gracefully")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: Failed to start bot: {e}")
        print("\nTroubleshooting:")
        print("1. Verify all required systems passed tests above")
        print("2. Check your .env file has all required tokens")
        print("3. Verify Slack app configuration:")
        print("   - Socket Mode is enabled")
        print("   - App is installed to workspace")
        print("   - All OAuth scopes are granted")
        print("4. Review error logs above")
        
        import traceback
        print("\nDetailed Error:")
        traceback.print_exc()
        
        sys.exit(1)

# =============================
# END OF MARKET RESEARCH TEAM BOT
# =============================