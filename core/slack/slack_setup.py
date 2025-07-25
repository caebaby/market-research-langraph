import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

# Replace with your actual bot token
SLACK_BOT_TOKEN = "xoxb-your-token-here"

async def setup_team_channel():
    client = AsyncWebClient(token=SLACK_BOT_TOKEN)
    
    try:
        result = await client.conversations_create(
            name="agentic_team",
            is_private=True
        )
        channel_id = result["channel"]["id"]
        print(f"✅ Created #agentic_team (ID: {channel_id})")
        return channel_id
    except SlackApiError as e:
        if e.response["error"] == "name_taken":
            print("✅ Channel #agentic_team already exists")
            channels = await client.conversations_list()
            for channel in channels["channels"]:
                if channel["name"] == "agentic_team":
                    print(f"✅ Found existing channel ID: {channel['id']}")
                    return channel["id"]
        else:
            print(f"❌ Error: {e}")

async def test_posting():
    client = AsyncWebClient(token=SLACK_BOT_TOKEN)
    
    try:
        await client.chat_postMessage(
            channel="agentic_team",
            text="🤖 AI Team is online and ready!",
            username="TestBot"
        )
        print("✅ Successfully posted test message")
    except SlackApiError as e:
        print(f"❌ Error posting: {e}")

async def main():
    print("Setting up your AI team workspace...")
    await setup_team_channel()
    await test_posting()
    print("🎉 Setup complete!")

if __name__ == "__main__":
    asyncio.run(main())
