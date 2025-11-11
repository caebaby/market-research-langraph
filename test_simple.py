import os
from dotenv import load_dotenv

print("=" * 50)
print("SIMPLE ENV TEST")
print("=" * 50)

# BEFORE loading .env
print("BEFORE load_dotenv():")
print(f"  ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY')}")

# Load .env
result = load_dotenv()
print(f"\nload_dotenv() returned: {result}")

# AFTER loading .env
print("\nAFTER load_dotenv():")
key = os.getenv('ANTHROPIC_API_KEY')
if key:
    print(f"  ANTHROPIC_API_KEY: {key[:15]}...")
else:
    print(f"  ANTHROPIC_API_KEY: Still None")

# Double check the file exists
print(f"\n.env file exists: {os.path.exists('.env')}")
print(f"Current directory: {os.getcwd()}")