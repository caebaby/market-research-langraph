#!/usr/bin/env python
"""Team Bot - Enhanced with LangSmith, Real-time Updates, Full Reports & Downloads"""

import os
import sys
from pathlib import Path
import logging
import json
from datetime import datetime
import time

# ==============================================
# 1. LANGSMITH ENVIRONMENT SETUP (MUST BE FIRST!)
# ==============================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "icp-team-analysis"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | 🤖 %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_thinking.log')
    ]
)

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Import workflow and LLM for elaboration
from team_icp.workflows.graph import ICPGraph

# Try to import LLM for elaboration feature
try:
    from langchain_anthropic import ChatAnthropic
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        temperature=0.7
    )
    LLM_AVAILABLE = True
except:
    LLM_AVAILABLE = False
    print("⚠️ LLM not available for elaboration")

load_dotenv()

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# ==============================================
# 2. MEMORY STORE FOR LAST ANALYSIS
# ==============================================
LAST_ANALYSIS = {}  # Store recent analyses by channel for elaboration

# ==============================================
# 3. STARTUP MESSAGES
# ==============================================
print("=" * 80)
print("🚀 TEAM BOT - ENHANCED VERSION")
print("=" * 80)
print(f"📊 LangSmith Tracing: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"📊 Project: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"📊 API Key Set: {bool(os.getenv('LANGSMITH_API_KEY'))}")
print("=" * 80)
print("Features Enabled:")
print("✅ Real-time progress updates to Slack")
print("✅ LangSmith tracing for visualization")
print("✅ Full reports in Slack (not previews)")
print("✅ Analysis memory for elaboration")
print("✅ Report download as .txt file")
print("=" * 80)

# ==============================================
# 4. MAIN TEAM COMMAND WITH ALL FEATURES
# ==============================================
@app.command("/team")
def handle_team_analysis(ack, respond, command, client):
    """Enhanced team analysis with all features"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide a company/context. Usage: `/team [company description]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    
    # Send initial message and get thread timestamp for updates
    initial_msg = client.chat_postMessage(
        channel=channel_id,
        text=f"🎯 **Starting Team Analysis:** {query}\n\n⏳ Initializing agents..."
    )
    thread_ts = initial_msg['ts']
    
    # ==============================================
    # 5. CREATE SLACK UPDATE FUNCTION
    # ==============================================
    def send_slack_update(message):
        """Send real-time updates to Slack thread"""
        try:
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=message
            )
            print(f"📡 SLACK UPDATE: {message}")
        except Exception as e:
            print(f"⚠️ Could not send Slack update: {e}")
    
    try:
        print("\n" + "="*80)
        print(f"🎯 NEW TEAM ANALYSIS: {query}")
        print("="*80)
        
        # Check LangSmith is configured
        print(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
        print(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
        print(f"LANGSMITH_API_KEY exists: {bool(os.getenv('LANGSMITH_API_KEY'))}")
        print("="*80)
        
        # Initialize workflow
        send_slack_update("🔄 Initializing workflow...")
        workflow = ICPGraph(verbose=True)
        
        # Create context with updater
        context = {
            "company": query,
            "requested_agents": ["psychological", "voice", "competitor", 
                                "interview_psychological", "interview_sales", 
                                "gtm_blueprint"],
            "client_id": f"slack_{user_id}",
            "slack_updater": send_slack_update  # Pass updater for real-time updates
        }
        
        print("\n🔄 STARTING LANGGRAPH WORKFLOW")
        print(f"📊 Agents to run: {context['requested_agents']}")
        print("-" * 40)
        
        # Send progress message
        send_slack_update("🤖 Agents starting analysis...")
        send_slack_update("🧠 Psychological: Starting deep analysis...")
        
        # Run workflow
        start_time = time.time()
        result = workflow.run(context)
        elapsed = time.time() - start_time
        
        print(f"\n✅ WORKFLOW COMPLETE in {elapsed:.2f} seconds")
        print("="*80)
        
        # ==============================================
        # 6. STORE ANALYSIS FOR ELABORATION
        # ==============================================
        LAST_ANALYSIS[channel_id] = {
            'query': query,
            'result': result,
            'timestamp': datetime.now(),
            'thread_ts': thread_ts,
            'full_data': {}
        }
        
        # Store full agent outputs
        if 'result' in result:
            for agent_name, output in result['result'].items():
                LAST_ANALYSIS[channel_id]['full_data'][agent_name] = str(output)
        
        # ==============================================
        # 7. SAVE FULL REPORT TO FILE
        # ==============================================
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reports/team_analysis_{timestamp}_{query.replace(' ', '_')[:30]}.txt"
        
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write(f"TEAM ANALYSIS REPORT\n")
            f.write(f"Query: {query}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Execution Time: {elapsed:.2f} seconds\n")
            f.write("="*80 + "\n\n")
            
            if 'result' in result:
                for agent_name, agent_output in result['result'].items():
                    f.write(f"\n{'='*60}\n")
                    f.write(f"AGENT: {agent_name.upper().replace('_', ' ')}\n")
                    f.write(f"{'='*60}\n\n")
                    f.write(str(agent_output))
                    f.write("\n\n")
        
        print(f"📄 Report saved to: {filename}")
        
        # ==============================================
        # 8. FORMAT AND SEND FULL RESULTS TO SLACK
        # ==============================================
        output = format_full_team_results(result, filename)
        
        # Send main results
        respond(output)
        
        # ==============================================
        # 9. UPLOAD FILE TO SLACK FOR DOWNLOAD
        # ==============================================
        try:
            client.files_upload(
                channels=channel_id,
                file=filename,
                title=f"Full Analysis - {query}",
                initial_comment=f"📊 Complete analysis report for: {query}\n⏱️ Generated in {elapsed:.2f} seconds",
                thread_ts=thread_ts
            )
            send_slack_update(f"✅ Full report uploaded! Download above for complete analysis.")
        except Exception as e:
            print(f"⚠️ Could not upload file: {e}")
            send_slack_update(f"📄 Report saved locally: `{filename}`")
        
        # Final update
        send_slack_update(f"""
✅ **Analysis Complete!**
- Execution time: {elapsed:.2f} seconds
- Total output: {sum(len(str(v)) for v in result.get('result', {}).values())} characters
- Report saved: {filename}
- View in LangSmith: Project 'icp-team-analysis'

💡 Ask agents for details: `@Agentic Team @psychological elaborate`
        """)
        
    except Exception as e:
        error_msg = f"❌ Error in team analysis: {str(e)}"
        print(f"\n{error_msg}")
        import traceback
        traceback.print_exc()
        respond(error_msg)

# ==============================================
# 10. ENHANCED FORMAT FUNCTION FOR FULL REPORTS
# ==============================================
def format_full_team_results(result, filename):
    """Format COMPLETE team analysis results for Slack"""
    output = "# 🎊 **Team Analysis Complete!**\n\n"
    
    total_chars = 0
    
    if 'result' in result:
        agents_data = result['result']
        
        # Show summary first
        output += "## 📊 Analysis Summary\n"
        for agent_name in agents_data.keys():
            emoji_map = {
                "psychological": "🧠",
                "voice": "🗣️",
                "competitor": "🔍",
                "interview_psychological": "🎭",
                "interview_sales": "💰",
                "gtm_blueprint": "📋"
            }
            emoji = emoji_map.get(agent_name, "🤖")
            agent_chars = len(str(agents_data[agent_name]))
            total_chars += agent_chars
            output += f"{emoji} **{agent_name.replace('_', ' ').title()}**: {agent_chars:,} characters ✅\n"
        
        output += f"\n**Total Output**: {total_chars:,} characters\n"
        output += "\n---\n\n"
        
        # Show key insights from each agent (more than preview)
        for agent_name, agent_output in agents_data.items():
            emoji_map = {
                "psychological": "🧠",
                "voice": "🗣️",
                "competitor": "🔍",
                "interview_psychological": "🎭",
                "interview_sales": "💰",
                "gtm_blueprint": "📋"
            }
            emoji = emoji_map.get(agent_name, "🤖")
            
            output += f"## {emoji} **{agent_name.upper().replace('_', ' ')}**\n\n"
            
            # Show more content (2500 chars instead of 1000)
            full_content = str(agent_output)
            if len(full_content) > 2500:
                output += full_content[:2500] + "\n\n*[Continued in downloaded report...]*\n\n"
            else:
                output += full_content + "\n\n"
            
            output += "---\n\n"
    
    # Add footer with instructions
    output += f"""
## 📥 **Full Report Access**

- **Download**: Full report file uploaded above ({filename})
- **Elaborate**: Mention agent for details: `@Agentic Team @psychological elaborate`
- **LangSmith**: View execution trace in project 'icp-team-analysis'
    """
    
    return output

# ==============================================
# 11. APP MENTION HANDLER FOR ELABORATION
# ==============================================
@app.event("app_mention")
def handle_app_mention(event, client):
    """Handle @bot mentions for elaboration using stored analysis"""
    
    text = event['text'].lower()
    channel_id = event['channel']
    
    # Check if asking for elaboration
    if 'elaborate' in text or 'explain' in text or 'detail' in text:
        
        # Get stored analysis
        last_analysis = LAST_ANALYSIS.get(channel_id)
        
        if not last_analysis:
            client.chat_postMessage(
                channel=channel_id,
                text="❌ No recent analysis found. Please run `/team [company]` first.",
                thread_ts=event.get('thread_ts')
            )
            return
        
        # Determine which agent to elaborate
        agent_to_elaborate = None
        for agent in ['psychological', 'voice', 'competitor', 'interview', 'sales', 'gtm']:
            if agent in text:
                agent_to_elaborate = agent
                break
        
        if not agent_to_elaborate:
            agent_to_elaborate = 'psychological'  # Default
        
        # Get the full output for that agent
        full_output = last_analysis['full_data'].get(agent_to_elaborate, 
                     last_analysis['full_data'].get(f"{agent_to_elaborate}_agent", ""))
        
        if not full_output:
            # Try to find partial match
            for key, value in last_analysis['full_data'].items():
                if agent_to_elaborate in key:
                    full_output = value
                    break
        
        if full_output:
            # If we have LLM, create elaboration
            if LLM_AVAILABLE:
                elaboration_prompt = f"""
                Based on this {agent_to_elaborate} analysis for {last_analysis['query']}:
                
                {full_output[:2000]}
                
                Provide a DEEP ELABORATION with:
                1. Specific tactical insights
                2. Implementation details
                3. Examples and scenarios
                4. Hidden implications
                
                Be specific to: {last_analysis['query']}
                """
                
                response = llm.invoke(elaboration_prompt)
                elaborated = response.content
            else:
                # Just show the full original output
                elaborated = full_output
            
            # Send elaboration
            if len(elaborated) > 3000:
                # Split into multiple messages
                chunks = [elaborated[i:i+2900] for i in range(0, len(elaborated), 2900)]
                for i, chunk in enumerate(chunks):
                    client.chat_postMessage(
                        channel=channel_id,
                        text=f"**{agent_to_elaborate.upper()} Elaboration (Part {i+1}/{len(chunks)}):**\n\n{chunk}",
                        thread_ts=event.get('thread_ts', last_analysis.get('thread_ts'))
                    )
            else:
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"🧠 **Elaborating on {agent_to_elaborate.upper()} Analysis:**\n\n{elaborated}",
                    thread_ts=event.get('thread_ts', last_analysis.get('thread_ts'))
                )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ No {agent_to_elaborate} analysis found in recent run.",
                thread_ts=event.get('thread_ts')
            )

# ==============================================
# 12. STATUS COMMAND
# ==============================================
@app.command("/status")
def handle_status(ack, respond):
    """Check system status"""
    ack()
    
    from team_icp.agents.registry import AGENT_REGISTRY
    
    status = "🔍 **System Status**\n\n"
    status += f"✅ Bot: Online\n"
    status += f"✅ Agents Available: {len(AGENT_REGISTRY)}\n"
    status += f"✅ LangGraph: Ready\n"
    status += f"✅ LangSmith: {'Connected' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else 'Disabled'}\n"
    status += f"✅ Memory Store: {len(LAST_ANALYSIS)} channels cached\n\n"
    status += "**Available Agents**: " + ", ".join(AGENT_REGISTRY.keys())
    
    respond(status)

# ==============================================
# 13. MAIN EXECUTION
# ==============================================
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("\n📡 Bot is running! Go to Slack and type /team [company]")
    print("📊 LangSmith tracing at: https://smith.langchain.com")
    print("💾 Reports will be saved to: ./reports/")
    print("\n")
    handler.start()