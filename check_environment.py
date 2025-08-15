# check_environment.py
"""
Quick environment check before testing LangSmith
"""

import os
from dotenv import load_dotenv

def check_environment():
    """Check all required environment variables"""
    
    print("🔧 Environment Configuration Check")
    print("=" * 40)
    
    # Load .env file
    env_loaded = load_dotenv()
    print(f"📁 .env file loaded: {'✅ Yes' if env_loaded else '❌ No'}")
    
    # Check critical API keys
    required_vars = {
        "ANTHROPIC_API_KEY": "Anthropic Claude API",
        "LANGSMITH_API_KEY": "LangSmith Tracing",
        "LANGCHAIN_TRACING_V2": "LangChain Tracing Flag",
        "LANGCHAIN_PROJECT": "LangSmith Project Name"
    }
    
    optional_vars = {
        "BRAVE_SEARCH_API_KEY": "Brave Search API",
        "SUPABASE_URL": "Supabase Database",
        "SUPABASE_KEY": "Supabase API Key"
    }
    
    print(f"\n📋 Required Variables:")
    all_required_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask API keys for security
            if "API_KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: Missing - {description}")
            all_required_present = False
    
    print(f"\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            if "API_KEY" in var or "KEY" in var:
                display_value = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚪ {var}: Not set - {description}")
    
    return all_required_present

if __name__ == "__main__":
    if check_environment():
        print(f"\n🎉 Environment check passed! Ready to test LangSmith.")
        print(f"\nNext: Run 'python test_langsmith.py' to test integration")
    else:
        print(f"\n⚠️  Missing required environment variables.")
        print(f"\nPlease update your .env file with the missing variables.")