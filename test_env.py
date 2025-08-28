import os
from dotenv import load_dotenv

print("Current working directory:", os.getcwd())
print(".env file exists:", os.path.exists(".env"))

# Load .env file
load_result = load_dotenv()
print(f".env loaded: {load_result}")

# Check the key
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    print(f"API Key found: {api_key[:10]}...")
else:
    print("API Key NOT found")
    
# Show all environment variables (be careful with this)
print("\nAll ANTHROPIC-related env vars:")
for key, value in os.environ.items():
    if "ANTHROPIC" in key or "CLAUDE" in key:
        print(f"{key}: {value[:10]}..." if value else f"{key}: None")