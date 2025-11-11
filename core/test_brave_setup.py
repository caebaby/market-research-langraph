# test_brave_setup.py
import os
import sys

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check if API key is set
api_key = os.getenv('BRAVE_API_KEY')
if not api_key:
    print("ERROR: Please set BRAVE_API_KEY environment variable")
    print("In PowerShell: $env:BRAVE_API_KEY=\"your_key_here\"")
    exit(1)

print(f"API Key found: {api_key[:10]}...")

# Now import from brave_search_wrapper directly (since it's in the same directory)
from brave_search_wrapper import CustomBraveSearch

searcher = CustomBraveSearch()
print(f"Search enabled: {searcher.enabled}")

# Do a test search
print("\nTesting search for 'Python programming'...")
results = searcher.search("Python programming", count=2)

for i, result in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(f"  Title: {result.get('title', 'N/A')[:50]}")
    print(f"  Content: {result.get('content', 'N/A')[:100]}...")

print("\nBrave search setup complete!")