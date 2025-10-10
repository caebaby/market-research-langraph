#!/usr/bin/env python
"""Team Bot - Enhanced with Full Reports, Fixed Upload, and Complete Display"""

import os
import sys
from pathlib import Path
import logging
import json
from datetime import datetime
import time
from typing import Dict, Any, Optional

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

# Configure detailed logging without emojis to prevent encoding issues
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('agent_thinking.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

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
    logger.info("LLM available for elaboration")
except Exception as e:
    LLM_AVAILABLE = False
    logger.warning(f"LLM not available for elaboration: {e}")

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
ANALYSIS_CACHE = {}  # Cache for reaction-based downloads

# ==============================================
# 3. STARTUP MESSAGES
# ==============================================
print("=" * 80)
print("TEAM BOT - FULL REPORT VERSION")
print("=" * 80)
print(f"LangSmith Tracing: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"Project: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"API Key Set: {bool(os.getenv('LANGSMITH_API_KEY'))}")
print("=" * 80)
print("Features Enabled:")
print("- Real-time progress updates to Slack")
print("- LangSmith tracing for visualization")
print("- FULL reports in Slack (no truncation)")
print("- Analysis memory for elaboration")
print("- Fixed file upload with files_upload_v2")
print("=" * 80)

# ==============================================
# 4. HELPER FUNCTION TO SEND FULL REPORT TO SLACK
# ==============================================
def send_full_report_to_slack(client, channel_id, thread_ts, full_report, company):
    """Send full report to Slack, handling message limits"""
    
    # Slack's message limit is ~40,000 characters, but we'll use 35,000 to be safe
    MAX_MESSAGE_LENGTH = 35000
    
    if len(full_report) <= MAX_MESSAGE_LENGTH:
        # Send as single message
        try:
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=full_report
            )
            logger.info(f"Sent full report as single message ({len(full_report)} chars)")
        except Exception as e:
            logger.error(f"Failed to send full report: {e}")
    else:
        # Split into multiple messages
        chunks = []
        lines = full_report.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > MAX_MESSAGE_LENGTH:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_length = len(line) + 1
            else:
                current_chunk.append(line)
                current_length += len(line) + 1
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        # Send each chunk
        for i, chunk in enumerate(chunks, 1):
            try:
                client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=thread_ts,
                    text=f"**Report Part {i}/{len(chunks)}**\n\n{chunk}"
                )
                time.sleep(0.5)  # Small delay to maintain order
                logger.info(f"Sent report chunk {i}/{len(chunks)}")
            except Exception as e:
                logger.error(f"Failed to send chunk {i}: {e}")

# ==============================================
# 5. MAIN TEAM COMMAND WITH ALL FEATURES
# ==============================================
@app.command("/team")
def handle_team_analysis(ack, respond, command, client):
    """Enhanced team analysis with full reports and fixed upload"""
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
        text=f"Starting Team Analysis: {query}\n\nInitializing agents..."
    )
    thread_ts = initial_msg['ts']
    
    # Create Slack update function
    def send_slack_update(message):
        """Send real-time updates to Slack thread"""
        try:
            client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_ts,
                text=message
            )
            logger.info(f"Slack update: {message}")
        except Exception as e:
            logger.error(f"Could not send Slack update: {e}")
    
    try:
        logger.info("=" * 80)
        logger.info(f"NEW TEAM ANALYSIS: {query}")
        logger.info(f"User: {user_id}, Channel: {channel_id}")
        logger.info("=" * 80)
        
        # Check LangSmith is configured
        logger.info(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
        logger.info(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
        logger.info(f"LANGSMITH_API_KEY exists: {bool(os.getenv('LANGSMITH_API_KEY'))}")
        
        # Initialize workflow
        send_slack_update("Initializing workflow...")
        workflow = ICPGraph(verbose=True)
        
        # Create context with updater
        context = {
            "company": query,
            "requested_agents": ["psychological", "voice_of_customer", "competitor", 
                                "interview_psychological", "interview_sales", 
                                "gtm_blueprint"],
            "client_id": f"slack_{user_id}",
            "slack_updater": send_slack_update  # Pass updater for real-time updates
        }
        
        logger.info("STARTING LANGGRAPH WORKFLOW")
        logger.info(f"Agents to run: {context['requested_agents']}")
        
        # Send progress message
        send_slack_update("Agents starting analysis...")
        send_slack_update("Psychological: Starting deep analysis...")
        
        # Run workflow
        start_time = time.time()
        result = workflow.run(context)
        elapsed = time.time() - start_time
        
        logger.info(f"WORKFLOW COMPLETE in {elapsed:.2f} seconds")
        
        # Part 1 ends here with comment for continuation
        # Continue with Part 2: Analysis storage, report generation, and upload
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
        # 7. BUILD FULL REPORT
        # ==============================================
        full_report = format_full_team_results(result, query, elapsed)
        
        # ==============================================
        # 8. SAVE FULL REPORT TO FILE
        # ==============================================
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = query.replace(' ', '_').replace('/', '_')[:30]
        filename = f"reports/team_analysis_{timestamp}_{safe_query}.txt"
        
        os.makedirs("reports", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        logger.info(f"Report saved to: {filename}")
        
        # Cache for reaction-based downloads
        ANALYSIS_CACHE[thread_ts] = {
            'report': full_report,
            'company': query,
            'filename': filename,
            'timestamp': datetime.now()
        }
        
        # ==============================================
        # 9. SEND FULL RESULTS TO SLACK
        # ==============================================
        send_slack_update("Analysis complete! Sending full report...")
        
        # Send the full report (will auto-split if too large)
        send_full_report_to_slack(client, channel_id, thread_ts, full_report, query)
        
        # ==============================================
        # 10. UPLOAD FILE TO SLACK FOR DOWNLOAD (FIXED)
        # ==============================================
        try:
            # Use files_upload_v2 instead of deprecated files_upload
            file_response = client.files_upload_v2(
                channel=channel_id,
                file=filename,
                title=f"Full Analysis - {query}",
                initial_comment=f"Complete analysis report for: {query}\nGenerated in {elapsed:.2f} seconds",
                thread_ts=thread_ts
            )
            send_slack_update("Full report uploaded! Download above for offline access.")
            logger.info("File uploaded successfully via files_upload_v2")
        except Exception as e:
            logger.error(f"Could not upload file: {e}")
            # Try alternative upload method
            try:
                with open(filename, 'rb') as file_content:
                    client.files_upload_v2(
                        channels=[channel_id],
                        content=file_content.read(),
                        filename=f"team_analysis_{safe_query}.txt",
                        title=f"Analysis - {query}",
                        thread_ts=thread_ts
                    )
                send_slack_update("Report uploaded successfully!")
            except Exception as e2:
                logger.error(f"Alternative upload also failed: {e2}")
                send_slack_update(f"Report saved locally: `{filename}`")
        
        # ==============================================
        # 11. FINAL STATISTICS UPDATE
        # ==============================================
        stats = result.get('statistics', {})
        total_chars = sum(len(str(v)) for v in result.get('result', {}).values())
        
        send_slack_update(f"""
Analysis Complete!
- Execution time: {elapsed:.2f} seconds
- Successful agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)}
- Total output: {total_chars:,} characters
- Total words: {stats.get('total_words', 0):,}
- Quality score: {stats.get('overall_quality', 0):.2%}
- Report saved: {filename}

Ask agents for details: `@Agentic Team @psychological elaborate`
        """)
        
    except Exception as e:
        error_msg = f"Error in team analysis: {str(e)}"
        logger.error(error_msg, exc_info=True)
        respond(error_msg)

# ==============================================
# 12. FORMAT FUNCTION FOR COMPLETE REPORTS
# ==============================================
def format_full_team_results(result: Dict[str, Any], query: str, elapsed: float) -> str:
    """Format COMPLETE team analysis results without truncation"""
    
    lines = []
    lines.append("=" * 80)
    lines.append("TEAM ANALYSIS REPORT")
    lines.append(f"Query: {query}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Execution Time: {elapsed:.2f} seconds")
    
    # Add statistics if available
    if 'statistics' in result:
        stats = result['statistics']
        lines.append(f"Quality Score: {stats.get('overall_quality', 0):.2%}")
        lines.append(f"Total Words: {stats.get('total_words', 0):,}")
        lines.append(f"Agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)} successful")
    
    lines.append("=" * 80)
    lines.append("")
    
    # Add full agent outputs without truncation
    if 'result' in result:
        for agent_name, agent_output in result['result'].items():
            if agent_output and not str(agent_output).startswith("[ERROR"):
                lines.append("")
                lines.append("=" * 60)
                lines.append(f"AGENT: {agent_name.upper().replace('_', ' ')}")
                lines.append("=" * 60)
                lines.append("")
                lines.append(str(agent_output))  # Full output, no truncation
                lines.append("")
    
    # Add GTM Blueprint if available separately
    if 'analysis_results' in result and 'gtm_blueprint' in result['analysis_results']:
        gtm_data = result['analysis_results']['gtm_blueprint']
        if 'content' in gtm_data:
            lines.append("")
            lines.append("=" * 80)
            lines.append("GTM BLUEPRINT DETAILS")
            lines.append("=" * 80)
            lines.append(f"Sections: {gtm_data.get('sections_generated', 0)}/12")
            lines.append(f"Word Count: {gtm_data.get('word_count', 0):,}")
            lines.append(f"Quality: {gtm_data.get('quality_score', 0):.2%}")
            lines.append("")
            lines.append(gtm_data['content'])
    
    return '\n'.join(lines)

# ==============================================
# 13. APP MENTION HANDLER FOR ELABORATION
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
                text="No recent analysis found. Please run `/team [company]` first.",
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
                
                try:
                    response = llm.invoke(elaboration_prompt)
                    elaborated = response.content
                except Exception as e:
                    logger.error(f"LLM elaboration failed: {e}")
                    elaborated = full_output
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
                    text=f"**Elaborating on {agent_to_elaborate.upper()} Analysis:**\n\n{elaborated}",
                    thread_ts=event.get('thread_ts', last_analysis.get('thread_ts'))
                )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"No {agent_to_elaborate} analysis found in recent run.",
                thread_ts=event.get('thread_ts')
            )

# ==============================================
# 14. REACTION HANDLER FOR DOWNLOADS
# ==============================================
@app.event("reaction_added")
def handle_reaction_added(event, client):
    """Handle file download requests via reactions"""
    try:
        emoji = event['reaction']
        thread_ts = event['item']['ts']
        channel = event['item']['channel']
        
        # Check if we have cached analysis
        if thread_ts not in ANALYSIS_CACHE:
            return
        
        data = ANALYSIS_CACHE[thread_ts]
        
        if emoji == 'inbox_tray':  # Download emoji
            # Upload file
            client.files_upload_v2(
                channels=[channel],
                content=data['report'],
                filename=f"{data['company']}_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                title=f"Full analysis - {data['company']}",
                thread_ts=thread_ts
            )
            logger.info("File uploaded via reaction")
            
    except Exception as e:
        logger.error(f"Error handling reaction: {e}")

# ==============================================
# 15. STATUS COMMAND
# ==============================================
@app.command("/status")
def handle_status(ack, respond):
    """Check system status"""
    ack()
    
    try:
        from team_icp.agents.registry import AGENT_REGISTRY
        agent_count = len(AGENT_REGISTRY)
    except:
        agent_count = 6
    
    status = "System Status\n\n"
    status += f"Bot: Online\n"
    status += f"Agents Available: {agent_count}\n"
    status += f"LangGraph: Ready\n"
    status += f"LangSmith: {'Connected' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else 'Disabled'}\n"
    status += f"Memory Store: {len(LAST_ANALYSIS)} channels cached\n"
    status += f"Analysis Cache: {len(ANALYSIS_CACHE)} reports ready"
    
    respond(status)

# ==============================================
# 16. MAIN EXECUTION
# ==============================================
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("\nBot is running! Go to Slack and type /team [company]")
    print("LangSmith tracing at: https://smith.langchain.com")
    print("Reports will be saved to: ./reports/")
    print("\n")
    handler.start()