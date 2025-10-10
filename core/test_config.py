# core/test_config.py
"""
Test script to verify Sonnet 4.5 configuration changes
Run this file to ensure the configuration is working correctly
"""

import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config

def test_configuration():
    """Test the Sonnet 4.5 configuration"""
    
    print("=" * 60)
    print("TESTING SONNET 4.5 CONFIGURATION @ TEMPERATURE 0.3")
    print("=" * 60)
    
    # Test 1: Check model version
    print("\n1. Checking Model Version:")
    print(f"   Current Model: {Config.LLM_MODEL}")
    if "claude-3-5-sonnet-4" in Config.LLM_MODEL:
        print("   ✅ Sonnet 4.5 model confirmed!")
    else:
        print("   ❌ WARNING: Not using Sonnet 4.5")
    
    # Test 2: Check temperature settings
    print("\n2. Checking Temperature Settings:")
    print(f"   Default Temperature: {Config.DEFAULT_TEMPERATURE}")
    if Config.DEFAULT_TEMPERATURE == 0.3:
        print("   ✅ Default temperature is 0.3")
    else:
        print(f"   ❌ Default temperature is {Config.DEFAULT_TEMPERATURE}, expected 0.3")
    
    # Test 3: Check all agent temperatures
    print("\n3. Checking All Agent Temperatures:")
    all_correct = True
    for agent, temp in Config.AGENT_TEMPERATURES.items():
        status = "✅" if temp == 0.3 else "❌"
        print(f"   {status} {agent}: {temp}")
        if temp != 0.3:
            all_correct = False
    
    if all_correct:
        print("   ✅ All agents set to temperature 0.3!")
    else:
        print("   ❌ Some agents have incorrect temperature")
    
    # Test 4: Try creating an LLM instance
    print("\n4. Testing LLM Creation with 20k Tokens:")
    try:
        print("   Creating LLM for 'psychological' agent...")
        llm = Config.get_llm("psychological")
        print("   ✅ LLM created successfully!")
        
        # Check the actual LLM properties
        print(f"   - Model: {llm.model}")
        print(f"   - Temperature: {llm.temperature}")
        print(f"   - Max Tokens: {llm.max_tokens}")
        
        # Verify it's 20k
        if llm.max_tokens == 20000:
            print("   ✅ Token limit correctly set to 20,000!")
        else:
            print(f"   ⚠️  Token limit is {llm.max_tokens}, expected 20,000")
        
    except Exception as e:
        print(f"   ❌ Failed to create LLM: {e}")
        print("\n   Troubleshooting:")
        print("   1. Check if ANTHROPIC_API_KEY is set in .env file")
        print("   2. Verify you have access to Sonnet 4.5")
        print("   3. Check internet connection")
    
    # Test 5: Verify environment
    print("\n5. Environment Validation:")
    if Config.validate_environment():
        print("   ✅ All required environment variables are set")
    else:
        print("   ⚠️  Some environment variables may be missing")
        print("   Required: ANTHROPIC_API_KEY")
        print("   Optional: SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET (if using Slack)")
    
    # Test 6: System info
    print("\n6. System Information:")
    info = Config.get_system_info()
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    # Test 7: Token Limits Verification
    print("\n7. Token Limits for Each Category:")
    print(f"   Research: {Config.MAX_TOKENS['research']:,} tokens")
    print(f"   Creative: {Config.MAX_TOKENS['creative']:,} tokens")
    print(f"   Summary: {Config.MAX_TOKENS['summary']:,} tokens")
    print(f"   Quick: {Config.MAX_TOKENS['quick']:,} tokens")
    
    if all(v >= 5000 for v in Config.MAX_TOKENS.values()):
        print("   ✅ All token limits successfully increased!")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_configuration()