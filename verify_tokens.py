# verify_tokens.py
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Checking Slack Tokens")
print("=" * 50)

tokens = {
    "SLACK_BOT_TOKEN": {
        "prefix": "xoxb-",
        "name": "Bot User OAuth Token"
    },
    "SLACK_APP_TOKEN": {
        "prefix": "xapp-",
        "name": "App-Level Token (Socket Mode)"
    },
    "SLACK_SIGNING_SECRET": {
        "prefix": None,
        "name": "Signing Secret"
    }
}

all_valid = True

for key, info in tokens.items():
    value = os.getenv(key)
    
    if not value:
        print(f"❌ {key} is missing")
        print(f"   Description: {info['name']}")
        all_valid = False
    elif info["prefix"] and not value.startswith(info["prefix"]):
        print(f"⚠️  {key} might be wrong (should start with {info['prefix']})")
        print(f"   Current value starts with: {value[:5]}...")
        all_valid = False
    else:
        # Mask the token for security
        if len(value) > 10:
            masked = f"{value[:6]}...{value[-4:]}"
        else:
            masked = "***"
        print(f"✅ {key}: {masked}")
        print(f"   Type: {info['name']}")

print("\n" + "=" * 50)

if all_valid:
    print("✅ All tokens look good!")
    print("\nNext step: Run the bot with:")
    print("  python integrations/slack/test_bot.py")
else:
    print("❌ Some tokens need to be fixed")
    print("\nMake sure to:")
    print("1. Copy the exact token values from Slack")
    print("2. Don't include any extra spaces")
    print("3. Save the .env file")