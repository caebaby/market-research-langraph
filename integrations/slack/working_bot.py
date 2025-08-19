# integrations/slack/working_bot.py
"""Bot that works despite VS Code errors - Channel Fix Version"""

import subprocess
import sys

# First, ensure packages are installed
def ensure_packages():
    try:
        import slack_bolt
        import slack_sdk
        print("✅ Packages already installed")
    except ImportError:
        print("📦 Installing packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "slack-bolt", "slack-sdk", "python-dotenv"])
        print("✅ Packages installed")

ensure_packages()

# Now import normally
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os

# FIXED: Manual env loading with UTF-8 encoding
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    if os.path.exists(env_path):
        # Specify UTF-8 encoding to handle special characters
        with open(env_path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print(f"❌ .env file not found at {env_path}")

load_env()

# Check if tokens are loaded
bot_token = os.environ.get("SLACK_BOT_TOKEN")
app_token = os.environ.get("SLACK_APP_TOKEN")
signing_secret = os.environ.get("SLACK_SIGNING_SECRET")

if not all([bot_token, app_token, signing_secret]):
    print("❌ Missing tokens:")
    if not bot_token: print("  - SLACK_BOT_TOKEN")
    if not app_token: print("  - SLACK_APP_TOKEN")
    if not signing_secret: print("  - SLACK_SIGNING_SECRET")
    sys.exit(1)

print("✅ All tokens found")

# Create app
app = App(
    token=bot_token,
    signing_secret=signing_secret
)

@app.command("/test")
def test_command(ack, respond, command):
    """Test command to verify bot is working"""
    # Acknowledge the command first
    ack()
    
    # Use respond() instead of client.chat_postMessage()
    # This automatically handles the channel correctly
    respond("✅ Bot is working! Your Slack integration is successful!")
    
    print(f"✅ /test command received from user: {command.get('user_name', 'unknown')}")

@app.command("/help")
def help_command(ack, respond, command):
    """Show available commands"""
    ack()
    
    help_text = """
🤖 *Market Research Bot Commands:*

• `/test` - Test bot connection
• `/help` - Show this help message
• `/agents` - List available AI agents
• `/analyze [company]` - Run market analysis

*Example:* `/analyze OpenAI`

Status: ✅ Bot is operational!
"""
    respond(help_text)
    print(f"✅ /help command received from user: {command.get('user_name', 'unknown')}")

@app.command("/agents")
def agents_command(ack, respond, command):
    """Show available agents in the system"""
    ack()
    
    # Try to import and show agents
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from team_icp.agents.registry import AgentRegistry
        
        registry = AgentRegistry()
        agents = registry.get_all_agents()
        
        agent_list = "*🤖 Available Agents:*\n\n"
        for i, (name, agent) in enumerate(agents.items(), 1):
            agent_list += f"{i}. `{name}` - ✅ Ready\n"
        
        agent_list += f"\n*Total:* {len(agents)} agents operational"
        
        respond(agent_list)
        print(f"✅ /agents command received - {len(agents)} agents found")
    except Exception as e:
        error_msg = f"⚠️ Could not load agents: {str(e)}\n\nMake sure you're in the project directory with the agents installed."
        respond(error_msg)
        print(f"❌ Error loading agents: {e}")

@app.command("/analyze")
def analyze_command(ack, respond, command):
    """Run a market analysis with the agents"""
    ack()
    
    # Extract the query from the command text
    query = command.get("text", "").strip()
    
    if not query:
        respond("❌ Please provide a company or topic to analyze.\n*Example:* `/analyze OpenAI`")
        return
    
    print(f"🔍 Starting analysis for: {query}")
    
    # Send initial message
    respond(f"🔍 Starting analysis for: *{query}*\n⏱️ This will take 2-3 minutes...")
    
    try:
        # Import and run the workflow
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from team_icp.workflows.graph import ICPGraph
        
        graph = ICPGraph()
        
        # Run the analysis
        result = graph.run({"company": query})
        
        # Format and send results
        if result and "final_report" in result:
            report = result["final_report"]
            
            # Split long messages if needed (Slack has a 3000 char limit)
            if len(report) > 3000:
                # Send first chunk with header
                respond(f"✅ *Analysis Complete for {query}:*\n\n{report[:2900]}...")
                
                # Send remaining chunks
                remaining = report[2900:]
                while remaining:
                    chunk = remaining[:3000]
                    respond(chunk)
                    remaining = remaining[3000:]
            else:
                respond(f"✅ *Analysis Complete for {query}:*\n\n{report}")
            
            print(f"✅ Analysis completed for {query}")
        else:
            respond("⚠️ Analysis completed but no report was generated.")
            print("⚠️ No report generated")
            
    except Exception as e:
        error_msg = f"❌ Analysis failed: {str(e)}"
        respond(error_msg)
        print(f"❌ Analysis error: {e}")

@app.event("app_mention")
def handle_mention(event, say):
    """Handle when the bot is mentioned"""
    user = event.get("user", "")
    say(f"Hi <@{user}>! 👋 Type `/help` to see what I can do.")
    print(f"✅ Bot mentioned by user: {user}")

@app.event("message")
def handle_message(event, say):
    """Handle direct messages to the bot"""
    # Only respond to DMs (direct messages)
    channel_type = event.get("channel_type", "")
    if channel_type == "im":
        say("Hi! I'm the Market Research Bot. 🤖\n\nUse slash commands to interact with me:\n• `/help` - See all commands\n• `/test` - Test connection\n• `/agents` - Show available agents\n• `/analyze [company]` - Run analysis")
        print("✅ DM received and responded")

# Error handler for better debugging
@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"Error: {error}")
    logger.info(f"Request body: {body}")

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 STARTING SLACK BOT (Fixed Version)")
    print("=" * 50)
    print("✅ UTF-8 encoding fix applied")
    print("✅ Channel response fix applied")
    print("✅ Using respond() for slash commands")
    print("\n📡 Go to Slack and try these commands:")
    print("  • /test   - Test the connection")
    print("  • /help   - Show all commands")
    print("  • /agents - Show available agents")
    print("  • /analyze [company] - Run market analysis")
    print("=" * 50)
    
    try:
        handler = SocketModeHandler(app, app_token)
        print("\n🟢 Bot is running! Press Ctrl+C to stop.")
        print("📌 Commands are working when you see '✅' messages here")
        handler.start()
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has all required tokens")
        print("2. Verify tokens are correct in Slack app settings")
        print("3. Ensure Socket Mode is enabled in your Slack app")