# integrations/slack/test_bot.py
"""Minimal Slack bot to test connection"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required tokens
bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")
signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

if not all([bot_token, app_token, signing_secret]):
    print("❌ Missing required tokens in .env:")
    if not bot_token: print("   - SLACK_BOT_TOKEN")
    if not app_token: print("   - SLACK_APP_TOKEN")
    if not signing_secret: print("   - SLACK_SIGNING_SECRET")
    sys.exit(1)

print("✅ All tokens found")

# Initialize app
app = App(
    token=bot_token,
    signing_secret=signing_secret
)

# Simple test command
@app.command("/test")
def handle_test(ack, command, client):
    ack()
    client.chat_postMessage(
        channel=command["channel_id"],
        text="✅ Bot is working! Connection successful."
    )

# Help command
@app.command("/help")
def handle_help(ack, command, client):
    ack()
    client.chat_postMessage(
        channel=command["channel_id"],
        text="Available commands:\n• `/test` - Test connection\n• `/help` - Show this message"
    )

# Start the bot
if __name__ == "__main__":
    handler = SocketModeHandler(app, app_token)
    print("⚡ Starting bot...")
    print("📡 Bot is running! Go to Slack and type /test")
    handler.start()