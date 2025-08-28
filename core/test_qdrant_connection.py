# test_qdrant_connection.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if credentials exist WITHOUT printing them
url = os.getenv('QDRANT_URL')
api_key = os.getenv('QDRANT_API_KEY')

if not url or not api_key:
    print("❌ Missing credentials in .env file")
    exit(1)

print(f"✅ Credentials loaded from .env")
print(f"   URL format: {url[:30]}...")  # Only show first 30 chars
print(f"   API key: {'*' * 8}...{api_key[-4:]}")  # Only show last 4 chars

# Test connection
from qdrant_client import QdrantClient

try:
    client = QdrantClient(url=url, api_key=api_key)
    collections = client.get_collections()
    print(f"✅ Connected! Found {len(collections.collections)} collections")
except Exception as e:
    print(f"❌ Connection failed: {e}")