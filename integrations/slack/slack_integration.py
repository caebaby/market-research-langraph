# integrations/slack/slack_integration.py
import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dataclasses import dataclass
from enum import Enum

# Fix the imports - use try/except for safety
try:
    from team_icp.agents.registry import AGENT_REGISTRY
except ImportError:
    print("Warning: Could not import AGENT_REGISTRY")
    AGENT_REGISTRY = {}

try:
    from team_icp.workflows.graph import graph
    workflow_graph = graph  # Use your existing graph
except ImportError:
    print("Warning: Could not import workflow graph")
    workflow_graph = None



# Import your modular architecture components
from team_icp.agents.registry import AGENT_REGISTRY
from team_icp.workflows.graph import graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackCommandType(Enum):
    """Enum for different Slack command types"""
    RESEARCH = "research"
    AGENT_DIRECT = "agent"
    STATUS = "status"
    HELP = "help"
    LIST_AGENTS = "list"

@dataclass
class SlackContext:
    """Context for Slack interactions"""
    channel_id: str
    user_id: str
    team_id: str
    thread_ts: Optional[str] = None
    command: Optional[str] = None
    text: Optional[str] = None
    
class SlackIntegration:
    """
    Main Slack integration class for the modular agent system
    """
    
    def __init__(self):
        # Initialize Slack app with bot token and signing secret
        self.app = App(
            token=os.environ.get("SLACK_BOT_TOKEN"),
            signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
        )
        
        # Initialize Socket Mode Handler for real-time events
        self.socket_handler = None
        if os.environ.get("SLACK_APP_TOKEN"):
            self.socket_handler = SocketModeHandler(
                self.app, 
                os.environ.get("SLACK_APP_TOKEN")
            )
        
        # Store active research sessions
        self.active_sessions: Dict[str, Dict] = {}
        
        # Initialize workflow graph
        self.workflow_graph = ICPWorkflowGraph()
        
        # Register all Slack event handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register all Slack event handlers and slash commands"""
        
        # Slash Commands
        self.app.command("/research")(self.handle_research_command)
        self.app.command("/agent")(self.handle_agent_command)
        self.app.command("/status")(self.handle_status_command)
        self.app.command("/help")(self.handle_help_command)
        self.app.command("/list-agents")(self.handle_list_agents_command)
        
        # Message Events
        self.app.event("app_mention")(self.handle_app_mention)
        self.app.event("message")(self.handle_message)
        
        # Interactive Components
        self.app.action("agent_selection")(self.handle_agent_selection)
        self.app.action("confirm_research")(self.handle_research_confirmation)
        
    # ============== SLASH COMMAND HANDLERS ==============
    
    def handle_research_command(self, ack, command, client):
        """
        Handle /research command to start a full research workflow
        Usage: /research [company_name] [optional: specific agents]
        """
        ack()  # Acknowledge command receipt
        
        context = self._create_context(command)
        text = command.get("text", "").strip()
        
        if not text:
            self._send_error_message(
                client, 
                context.channel_id,
                "Please provide a company name. Usage: `/research [company_name]`"
            )
            return
        
        # Parse command
        parts = text.split()
        company_name = parts[0]
        requested_agents = parts[1:] if len(parts) > 1 else None
        
        # Create research session
        session_id = self._create_session(context, company_name, requested_agents)
        
        # Send initial message
        message = self._send_initial_research_message(
            client, 
            context, 
            company_name, 
            requested_agents
        )
        
        # Start async research
        asyncio.create_task(
            self._execute_research(
                session_id, 
                company_name, 
                requested_agents, 
                client, 
                context
            )
        )
        
    def handle_agent_command(self, ack, command, client):
        """
        Handle /agent command to run a specific agent
        Usage: /agent [agent_name] [query]
        """
        ack()
        
        context = self._create_context(command)
        text = command.get("text", "").strip()
        
        if not text:
            self._send_agent_selection_modal(client, command["trigger_id"])
            return
        
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            self._send_error_message(
                client,
                context.channel_id,
                "Usage: `/agent [agent_name] [query]`"
            )
            return
            
        agent_name = parts[0]
        query = parts[1]
        
        # Validate agent exists
        if agent_name not in AGENT_REGISTRY:
            available = ", ".join(AGENT_REGISTRY.keys())
            self._send_error_message(
                client,
                context.channel_id,
                f"Unknown agent: {agent_name}\nAvailable agents: {available}"
            )
            return
        
        # Execute single agent
        asyncio.create_task(
            self._execute_single_agent(
                agent_name,
                query,
                client,
                context
            )
        )
        
    def handle_status_command(self, ack, command, client):
        """Handle /status command to check active research sessions"""
        ack()
        
        context = self._create_context(command)
        
        if not self.active_sessions:
            client.chat_postMessage(
                channel=context.channel_id,
                text="No active research sessions."
            )
            return
        
        # Build status message
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Active Research Sessions"
                }
            }
        ]
        
        for session_id, session in self.active_sessions.items():
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Session:* {session_id}\n"
                           f"*Company:* {session['company_name']}\n"
                           f"*Started:* {session['started_at']}\n"
                           f"*Status:* {session['status']}"
                }
            })
        
        client.chat_postMessage(
            channel=context.channel_id,
            blocks=blocks
        )
        
    def handle_help_command(self, ack, command, client):
        """Handle /help command"""
        ack()
        
        context = self._create_context(command)
        
        help_text = """
        🤖 *Market Research Bot Commands*
        
        `/research [company_name] [agents...]` - Start full research workflow
        `/agent [agent_name] [query]` - Run specific agent
        `/status` - Check active research sessions  
        `/list-agents` - Show available agents
        `/help` - Show this help message
        
        *Available Agents:*
        • psychological - Deep psychological analysis
        • voice - Voice of customer research
        • competitor - Competitive analysis
        • gtm_blueprint - Go-to-market strategy
        • interview_generator - Generate interview questions
        • interview_analyzer - Analyze interview responses
        
        *Examples:*
        `/research Airbnb`
        `/research Tesla psychological competitor`
        `/agent psychological "analyze buyer motivations for Tesla"`
        """
        
        client.chat_postMessage(
            channel=context.channel_id,
            text=help_text
        )
        
    def handle_list_agents_command(self, ack, command, client):
        """Handle /list-agents command"""
        ack()
        
        context = self._create_context(command)
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🎯 Available Research Agents"
                }
            }
        ]
        
        for agent_name, agent_class in AGENT_REGISTRY.items():
            # Get agent instance to access metadata
            agent = agent_class()
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{agent_name}*\n{agent.agent_name}"
                }
            })
        
        client.chat_postMessage(
            channel=context.channel_id,
            blocks=blocks
        )
    
    # ============== EVENT HANDLERS ==============
    
    def handle_app_mention(self, event, client):
        """Handle when the bot is mentioned"""
        context = SlackContext(
            channel_id=event["channel"],
            user_id=event["user"],
            team_id=event["team"],
            thread_ts=event.get("thread_ts", event["ts"])
        )
        
        text = event["text"]
        # Remove bot mention from text
        text = text.split(">", 1)[-1].strip() if ">" in text else text
        
        # Parse as natural language command
        self._handle_natural_language(text, client, context)
        
    def handle_message(self, event, client):
        """Handle direct messages to the bot"""
        # Only process DMs
        if event.get("channel_type") != "im":
            return
            
        # Ignore bot's own messages
        if event.get("bot_id"):
            return
            
        context = SlackContext(
            channel_id=event["channel"],
            user_id=event["user"],
            team_id=event.get("team", ""),
            thread_ts=event.get("thread_ts", event["ts"])
        )
        
        text = event.get("text", "")
        self._handle_natural_language(text, client, context)
    
    # ============== INTERACTIVE HANDLERS ==============
    
    def handle_agent_selection(self, ack, body, client):
        """Handle agent selection from interactive modal"""
        ack()
        
        selected_agent = body["actions"][0]["selected_option"]["value"]
        context = self._create_context_from_body(body)
        
        # Open input modal for query
        client.views_open(
            trigger_id=body["trigger_id"],
            view={
                "type": "modal",
                "callback_id": f"agent_query_{selected_agent}",
                "title": {
                    "type": "plain_text",
                    "text": f"Query for {selected_agent}"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit"
                },
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "query_input",
                        "label": {
                            "type": "plain_text",
                            "text": "Enter your query:"
                        },
                        "element": {
                            "type": "plain_text_input",
                            "action_id": "query_text",
                            "multiline": True
                        }
                    }
                ]
            }
        )
        
    def handle_research_confirmation(self, ack, body, client):
        """Handle research confirmation"""
        ack()
        
        action = body["actions"][0]["value"]
        context = self._create_context_from_body(body)
        
        if action == "cancel":
            client.chat_postMessage(
                channel=context.channel_id,
                thread_ts=context.thread_ts,
                text="Research cancelled."
            )
            return
            
        # Continue with research
        # Implementation depends on your workflow
        
    # ============== EXECUTION METHODS ==============
    
    async def _execute_research(
        self, 
        session_id: str,
        company_name: str,
        requested_agents: Optional[List[str]],
        client: WebClient,
        context: SlackContext
    ):
        """Execute full research workflow"""
        try:
            # Update session status
            self.active_sessions[session_id]["status"] = "running"
            
            # Send progress update
            client.chat_postMessage(
                channel=context.channel_id,
                thread_ts=context.thread_ts,
                text=f"🔄 Starting research for *{company_name}*..."
            )
            
            # Prepare workflow input
            workflow_input = {
                "company_name": company_name,
                "requested_agents": requested_agents or list(AGENT_REGISTRY.keys()),
                "slack_context": {
                    "channel_id": context.channel_id,
                    "thread_ts": context.thread_ts
                }
            }
            
            # Execute workflow
            result = await self.workflow_graph.execute(workflow_input)
            
            # Format and send results
            self._send_research_results(client, context, company_name, result)
            
            # Update session
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Research execution error: {e}")
            self._send_error_message(
                client,
                context.channel_id,
                f"Research failed: {str(e)}",
                context.thread_ts
            )
            self.active_sessions[session_id]["status"] = "failed"
            
    async def _execute_single_agent(
        self,
        agent_name: str,
        query: str,
        client: WebClient,
        context: SlackContext
    ):
        """Execute a single agent"""
        try:
            # Send initial message
            message = client.chat_postMessage(
                channel=context.channel_id,
                text=f"🤖 Running *{agent_name}* agent..."
            )
            thread_ts = message["ts"]
            
            # Get agent instance
            agent_class = AGENT_REGISTRY[agent_name]
            agent = agent_class()
            
            # Execute agent
            result = await agent.process({
                "query": query,
                "company_name": query.split()[0] if query else "Unknown"
            })
            
            # Send results
            self._send_agent_results(
                client,
                context.channel_id,
                thread_ts,
                agent_name,
                result
            )
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            self._send_error_message(
                client,
                context.channel_id,
                f"Agent execution failed: {str(e)}"
            )
    
    # ============== HELPER METHODS ==============
    
    def _create_context(self, command: Dict) -> SlackContext:
        """Create context from Slack command"""
        return SlackContext(
            channel_id=command["channel_id"],
            user_id=command["user_id"],
            team_id=command["team_id"],
            command=command.get("command"),
            text=command.get("text")
        )
        
    def _create_context_from_body(self, body: Dict) -> SlackContext:
        """Create context from interactive body"""
        return SlackContext(
            channel_id=body["channel"]["id"],
            user_id=body["user"]["id"],
            team_id=body["team"]["id"]
        )
        
    def _create_session(
        self,
        context: SlackContext,
        company_name: str,
        requested_agents: Optional[List[str]]
    ) -> str:
        """Create a new research session"""
        session_id = f"{context.user_id}_{datetime.now().timestamp()}"
        self.active_sessions[session_id] = {
            "company_name": company_name,
            "requested_agents": requested_agents,
            "user_id": context.user_id,
            "channel_id": context.channel_id,
            "started_at": datetime.now().isoformat(),
            "status": "initialized"
        }
        return session_id
        
    def _send_initial_research_message(
        self,
        client: WebClient,
        context: SlackContext,
        company_name: str,
        requested_agents: Optional[List[str]]
    ) -> Dict:
        """Send initial research message with status"""
        agents_text = ", ".join(requested_agents) if requested_agents else "all agents"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🔬 Research: {company_name}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Agents:* {agents_text}\n*Status:* Initializing..."
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Started by <@{context.user_id}> at {datetime.now().strftime('%H:%M:%S')}"
                    }
                ]
            }
        ]
        
        return client.chat_postMessage(
            channel=context.channel_id,
            blocks=blocks
        )
        
    def _send_research_results(
        self,
        client: WebClient,
        context: SlackContext,
        company_name: str,
        results: Dict
    ):
        """Send formatted research results"""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"✅ Research Complete: {company_name}"
                }
            }
        ]
        
        # Add results from each agent
        for agent_name, agent_result in results.items():
            if agent_result:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{agent_name.upper()} Analysis*\n{agent_result[:2000]}"
                    }
                })
                blocks.append({"type": "divider"})
        
        # Send in thread
        client.chat_postMessage(
            channel=context.channel_id,
            thread_ts=context.thread_ts,
            blocks=blocks
        )
        
    def _send_agent_results(
        self,
        client: WebClient,
        channel_id: str,
        thread_ts: str,
        agent_name: str,
        result: Dict
    ):
        """Send single agent results"""
        text = result.get("output", "No results generated")
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{agent_name} Results:*\n{text[:3000]}"
                }
            }
        ]
        
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            blocks=blocks
        )
        
    def _send_error_message(
        self,
        client: WebClient,
        channel_id: str,
        error_text: str,
        thread_ts: Optional[str] = None
    ):
        """Send error message"""
        client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=f"❌ {error_text}"
        )
        
    def _send_agent_selection_modal(self, client: WebClient, trigger_id: str):
        """Send agent selection modal"""
        options = [
            {
                "text": {"type": "plain_text", "text": name},
                "value": name
            }
            for name in AGENT_REGISTRY.keys()
        ]
        
        client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "agent_selection_modal",
                "title": {
                    "type": "plain_text",
                    "text": "Select Agent"
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Choose an agent to run:"
                        },
                        "accessory": {
                            "type": "static_select",
                            "action_id": "agent_selection",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select an agent"
                            },
                            "options": options
                        }
                    }
                ]
            }
        )
        
    def _handle_natural_language(
        self,
        text: str,
        client: WebClient,
        context: SlackContext
    ):
        """Handle natural language commands"""
        text_lower = text.lower()
        
        # Detect intent
        if any(word in text_lower for word in ["research", "analyze", "study"]):
            # Extract company name (simple approach)
            words = text.split()
            company_name = None
            for word in words:
                if word[0].isupper() and word not in ["Research", "Analyze", "Study"]:
                    company_name = word
                    break
                    
            if company_name:
                asyncio.create_task(
                    self._execute_research(
                        self._create_session(context, company_name, None),
                        company_name,
                        None,
                        client,
                        context
                    )
                )
            else:
                client.chat_postMessage(
                    channel=context.channel_id,
                    thread_ts=context.thread_ts,
                    text="I couldn't identify a company name. Please specify what company you'd like to research."
                )
        else:
            # Default response
            client.chat_postMessage(
                channel=context.channel_id,
                thread_ts=context.thread_ts,
                text="I can help you research companies! Try:\n"
                     "• 'Research [Company Name]'\n"
                     "• 'Analyze [Company Name]'\n"
                     "• Or use `/help` for all commands"
            )
    
    # ============== MAIN EXECUTION ==============
    
    def start(self):
        """Start the Slack bot"""
        logger.info("Starting Slack bot...")
        
        if self.socket_handler:
            # Use Socket Mode for development
            logger.info("Running in Socket Mode")
            self.socket_handler.start()
        else:
            # Use Web API for production
            logger.info("Running in Web API mode")
            self.app.start(port=int(os.environ.get("PORT", 3000)))


# ============== MAIN ==============

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validate required environment variables
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_SIGNING_SECRET",
        "SLACK_APP_TOKEN"  # For Socket Mode
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please set these in your .env file")
        exit(1)
    
    # Initialize and start bot
    slack_bot = SlackIntegration()
    slack_bot.start()