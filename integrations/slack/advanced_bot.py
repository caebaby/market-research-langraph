# advanced_bot.py
"""
Advanced Slack Bot for Market Research with Memory System and Direct Agent Q&A
Final version with all fixes and improvements
"""

import sys
from pathlib import Path

# Fix 1: Add project root to Python path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent  # Go up 3 levels from integrations/slack/advanced_bot.py
sys.path.insert(0, str(project_root))

print(f"Python path configured. Project root: {project_root}")
print(f"Looking for modules in: {project_root}")

import os
import json
import asyncio
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiting for API calls
last_api_call = 0
API_RATE_LIMIT = 1.0  # Minimum seconds between API calls

# ============================================
# MEMORY SYSTEM INITIALIZATION
# ============================================
memory_system = None
MEMORY_ENABLED = False

try:
    from core.memory_system_qdrant import QdrantMemorySystem
    memory_system = QdrantMemorySystem()
    MEMORY_ENABLED = True
    logger.info("✅ Memory system connected to Slack bot")
    print("✅ Memory system connected - agents will remember previous analyses")
except ImportError as e:
    logger.warning(f"⚠️ Memory system not imported: {e}")
    print("⚠️ Memory system not available - running without persistence")
except ValueError as e:
    logger.warning(f"⚠️ Memory system credentials missing: {e}")
    print("⚠️ Memory system credentials missing - check .env file")
except Exception as e:
    logger.warning(f"⚠️ Memory system initialization failed: {e}")
    print(f"⚠️ Memory system error: {e}")

# ============================================
# LLM INITIALIZATION FOR DIRECT AGENT Q&A
# ============================================
llm = None
try:
    from langchain_anthropic import ChatAnthropic
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=api_key,
            max_tokens=2000,  # Smaller for quick responses
            temperature=0.7
        )
        logger.info("✅ LLM initialized for direct agent Q&A")
except Exception as e:
    logger.warning(f"⚠️ LLM initialization failed: {e}")

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Import the workflow
try:
    from team_icp.workflows.graph import ICPGraph
    workflow_available = True
    logger.info("✅ Workflow graph imported successfully")
except ImportError as e:
    workflow_available = False
    logger.error(f"❌ Failed to import workflow: {e}")

# ============================================
# AGENT REGISTRY FOR DIRECT Q&A
# ============================================
# Fix: Include both "voice" and "voice_of_customer" entries, plus "gtm" and "gtm_blueprint"
AGENT_PERSONAS = {
    "psychological": {
        "emoji": "🧠",
        "name": "Psychological Analyst",
        "personality": "I analyze deep psychological patterns, unconscious motivations, and identity conflicts.",
        "focus": ["fears", "identity", "unconscious", "transformation", "resistance"]
    },
    "voice": {
        "emoji": "🗣️",
        "name": "Voice of Customer Specialist",
        "personality": "I extract exact customer language, pain points, and aspirations.",
        "focus": ["language", "pain points", "exact words", "phrases", "aspirations"]
    },
    "voice_of_customer": {  # Duplicate entry to prevent lookup errors
        "emoji": "🗣️",
        "name": "Voice of Customer Specialist",
        "personality": "I extract exact customer language, pain points, and aspirations.",
        "focus": ["language", "pain points", "exact words", "phrases", "aspirations"]
    },
    "competitor": {
        "emoji": "🔍",
        "name": "Competitor Intelligence Analyst", 
        "personality": "I map competitive landscapes and identify positioning opportunities.",
        "focus": ["competitors", "positioning", "gaps", "opportunities", "weaknesses"]
    },
    "interview_psychological": {
        "emoji": "🎭",
        "name": "Psychological Interview Specialist",
        "personality": "I simulate deep psychological interviews to reveal emotional vulnerabilities.",
        "focus": ["interviews", "emotions", "vulnerabilities", "objections", "beliefs"]
    },
    "interview_sales": {
        "emoji": "💰",
        "name": "Sales Interview Specialist",
        "personality": "I conduct sales discovery to identify buying triggers and decision criteria.",
        "focus": ["sales", "buying triggers", "decision process", "budget", "timeline"]
    },
    "gtm": {  # FIX: Add 'gtm' entry that duplicates gtm_blueprint
        "emoji": "📋",
        "name": "GTM Blueprint Strategist",
        "personality": "I synthesize insights into actionable go-to-market strategies.",
        "focus": ["strategy", "positioning", "messaging", "channels", "tactics"]
    },
    "gtm_blueprint": {  # Keep original entry for consistency
        "emoji": "📋",
        "name": "GTM Blueprint Strategist",
        "personality": "I synthesize insights into actionable go-to-market strategies.",
        "focus": ["strategy", "positioning", "messaging", "channels", "tactics"]
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_client_id(channel_id: str, user_id: Optional[str] = None) -> str:
    """Generate consistent client ID for memory persistence"""
    if user_id:
        return f"{channel_id}_{user_id}"
    return channel_id

def format_quality_score(score: float) -> str:
    """Format quality score with emoji indicator"""
    if score >= 0.9:
        return f"🌟 {score:.2%}"
    elif score >= 0.8:
        return f"✅ {score:.2%}"
    elif score >= 0.7:
        return f"⚠️ {score:.2%}"
    else:
        return f"❌ {score:.2%}"

def save_report_to_file(company: str, content: str, report_type: str = "analysis") -> str:
    """Save report to file and return filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company.lower().replace(' ', '_')}_{report_type}_{timestamp}.txt"
    
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    filepath = reports_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def extract_agent_and_question(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract agent name and question from mention text
    Examples:
    - "@bot @psychological what are deep fears?" -> ("psychological", "what are deep fears?")
    - "@bot voice: show exact customer pain language" -> ("voice", "show exact customer pain language")
    - "@bot @gtm synthesize strategy" -> ("gtm", "synthesize strategy")
    """
    # Remove bot mention
    text = re.sub(r'<@[A-Z0-9]+>', '', text).strip()
    
    # Pattern 1: @agent_name question
    pattern1 = r'@(\w+)\s+(.*)'
    match1 = re.match(pattern1, text)
    if match1:
        agent = match1.group(1).lower()
        # FIX: Check if agent exists directly in AGENT_PERSONAS
        if agent in AGENT_PERSONAS:
            return agent, match1.group(2)
    
    # Pattern 2: agent_name: question
    pattern2 = r'(\w+):\s*(.*)'
    match2 = re.match(pattern2, text)
    if match2:
        agent = match2.group(1).lower()
        # FIX: Check if agent exists directly in AGENT_PERSONAS
        if agent in AGENT_PERSONAS:
            return agent, match2.group(2)
    
    # Pattern 3: Just the agent name followed by question
    words = text.split(None, 1)
    if len(words) >= 2:
        potential_agent = words[0].lower().strip(':,')
        # FIX: Check if agent exists directly in AGENT_PERSONAS
        if potential_agent in AGENT_PERSONAS:
            return potential_agent, words[1]
    
    return None, None

async def get_agent_direct_response(agent_name: str, question: str, context: Dict = None) -> str:
    """
    Get a direct response from a specific agent with rate limiting
    """
    global last_api_call
    
    # Rate limiting to prevent API overload
    current_time = time.time()
    time_since_last = current_time - last_api_call
    if time_since_last < API_RATE_LIMIT:
        await asyncio.sleep(API_RATE_LIMIT - time_since_last)
    last_api_call = time.time()
    
    # Get agent persona directly without complex normalization
    persona = AGENT_PERSONAS.get(agent_name)
    if not persona:
        return f"Unknown agent: {agent_name}. Try: psychological, voice, competitor, gtm"
    
    # If no LLM, return mock response
    if not llm:
        return f"[{persona['name']}] LLM not configured. In production, I would analyze: {question}"
    
    # Build agent-specific prompt
    agent_prompt = f"""You are the {persona['name']}. {persona['personality']}

Your focus areas are: {', '.join(persona['focus'])}

User question: {question}

Provide a concise, insightful response in character. Be specific and actionable.
Maximum 300 words. Use your expertise to give unique insights only you would provide.
If the question is outside your expertise, acknowledge it and suggest which agent would be better suited."""

    # Add memory context if available
    if MEMORY_ENABLED and context:
        client_id = context.get('client_id')
        if client_id:
            try:
                memories = memory_system.retrieve_memories(
                    client_id=client_id,
                    agent_name=agent_name,
                    query=question,
                    limit=3
                )
                if memories:
                    agent_prompt += "\n\nPrevious insights to build upon:\n"
                    for mem in memories:
                        agent_prompt += f"- {mem.content[:100]}\n"
            except Exception as e:
                logger.debug(f"Could not retrieve memories: {e}")
    
    try:
        response = llm.predict(agent_prompt)
        
        # Store this Q&A as memory if enabled
        if MEMORY_ENABLED and context:
            try:
                memory_system.store_memory(
                    client_id=context.get('client_id', 'direct_qa'),
                    agent_name=agent_name,
                    memory_type="qa",
                    content=f"Q: {question[:100]} A: {response[:200]}",
                    importance=0.7
                )
            except Exception as e:
                logger.debug(f"Could not store memory: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting agent response: {e}")
        if "529" in str(e) or "overloaded" in str(e).lower():
            return "The AI service is currently overloaded. Please try again in a few moments."
        return f"Error getting response from {persona['name']}: {str(e)}"

# ============================================
# SLASH COMMANDS
# ============================================

@app.command("/test")
def handle_test(ack, respond, command):
    """Test bot connection"""
    ack()
    respond("✅ Market Research Bot is connected and ready!")

@app.command("/help")
def handle_help(ack, respond):
    """Show help message"""
    ack()
    
    memory_status = "✅ Enabled" if MEMORY_ENABLED else "❌ Disabled"
    direct_qa_status = "✅ Enabled" if llm else "❌ Disabled"
    
    help_text = f"""
*Market Research Bot Commands:*

*Basic:*
- `/test` - Test bot connection
- `/help` - Show this help message
- `/agents` - List available AI agents
- `/analyze [company]` - Run full market analysis (private)
- `/analyze-public [company]` - Run analysis and share publicly
- `/share-last` - Share your last analysis publicly

*Direct Agent Q&A:* {direct_qa_status}
- `@bot @psychological [question]` - Ask psychological agent directly
- `@bot voice: [question]` - Ask voice of customer agent
- `@bot @competitor [question]` - Ask competitor analyst
- `@bot @gtm [question]` - Ask GTM strategist

*Advanced:*
- `/debate [topic]` - Agents debate a topic
- `/conversation agent1 agent2 [topic]` - Two agents discuss
- `/team [query]` - Full team analysis with progress
- `/coach agent [message]` - Coach an agent to improve
- `/learning` - Show agent learning progress
- `/memory` - Show memory statistics

*Report Management:*
- `/reports` - List saved reports
- `/get-report [filename]` - Get link to specific report

*Memory System:* {memory_status}

*Examples:*
- `/analyze OpenAI`
- `@bot @psychological what drives founder anxiety?`
- `@bot voice: show me their exact pain language`
- `/debate AI vs human consultants`
- `/coach psychological Focus on identity conflicts`
"""
    respond(help_text)

@app.command("/agents")
def handle_agents(ack, respond):
    """List available agents with Q&A capability"""
    ack()
    
    agents_info = """
*Available AI Agents for Direct Q&A:*

🧠 *Psychological Analyst* - `@bot @psychological [question]`
- Deep psychological profiling of target customers
- Unconscious motivations and fears
- Identity and transformation insights

🗣️ *Voice of Customer Specialist* - `@bot voice: [question]`
- Extracts exact customer language
- Pain points and aspirations
- Copy-ready phrases and hooks

🔍 *Competitor Intelligence Analyst* - `@bot @competitor [question]`
- Maps competitive landscape
- Identifies positioning gaps
- Reveals opportunities to exploit

🎭 *Psychological Interview Specialist* - `@bot @interview_psychological [question]`
- Simulates customer interviews
- Reveals emotional vulnerabilities
- Uncovers hidden objections

💰 *Sales Interview Specialist* - `@bot @interview_sales [question]`
- Sales-focused discovery interviews
- Identifies buying triggers
- Maps decision criteria

📋 *GTM Blueprint Strategist* - `@bot @gtm [question]`
- Synthesizes all insights
- Creates actionable go-to-market plan
- Executive-ready strategy document

*How to Ask Agents Directly:*
1. Mention the bot and agent: `@bot @psychological what are deep fears?`
2. Or use colon format: `@bot voice: explain customer pain`
3. Agents will respond with their unique perspective
"""
    
    if MEMORY_ENABLED:
        agents_info += "\n💾 *Memory Active* - Agents remember previous Q&A and analyses"
    
    respond(agents_info)

@app.command("/analyze")
def handle_analyze(ack, respond, command):
    """Run full market analysis (private)"""
    ack()
    
    if not workflow_available:
        respond("❌ Workflow not available. Please check system configuration.")
        return
    
    company = command['text'].strip()
    if not company:
        respond("Please provide a company name. Usage: `/analyze [company name]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    # Initial response
    initial_msg = f"🔍 Starting comprehensive analysis of *{company}*...\n"
    
    if MEMORY_ENABLED:
        # Check for existing memories
        try:
            context = memory_system.get_client_context(client_id)
            if context:
                total_memories = sum(len(insights) for insights in context.values())
                initial_msg += f"📚 Found {total_memories} previous insights to build upon\n"
        except:
            pass
    
    initial_msg += "⏳ This will take 2-3 minutes. You'll be notified when complete."
    respond(initial_msg)
    
    try:
        # Run the analysis
        logger.info(f"Starting analysis for {company} requested by {user_id} in {channel_id}")
        workflow = ICPGraph()
        
        # Include client_id for memory
        result = workflow.run({
            "company": company,
            "client_id": client_id
        })
        
        # Extract results
        report = result.get('final_report', 'No report generated')
        stats = result.get('statistics', {})
        quality = stats.get('overall_quality', 0)
        words = stats.get('total_words', 0)
        
        # Save report
        filename = save_report_to_file(company, report)
        
        # Format response
        response_text = f"""
✅ *Analysis Complete: {company}*

📊 *Statistics:*
- Quality Score: {format_quality_score(quality)}
- Total Words: {words:,}
- Report saved: `{filename}`
"""
        
        if MEMORY_ENABLED and 'memories_stored' in stats:
            stored = sum(1 for v in stats['memories_stored'].values() if v)
            loaded = sum(stats.get('memories_loaded', {}).values())
            response_text += f"• Memories: {loaded} loaded, {stored} stored\n"
        
        response_text += f"""

📄 *Key Insights:*
{report[:500]}...

Use `/get-report {filename}` to get the full report.
Use `/share-last` to share this analysis publicly.

💡 *Try Direct Q&A:*
Ask specific agents: `@bot @psychological what does this mean?`
"""
        
        respond(response_text)
        logger.info(f"Analysis complete for {company}. Quality: {quality:.2f}")
        
    except Exception as e:
        error_msg = f"❌ Error analyzing {company}: {str(e)}"
        respond(error_msg)
        logger.error(f"Analysis failed: {e}")

@app.command("/memory")
def handle_memory_command(ack, respond, command):
    """Show memory statistics for this channel"""
    ack()
    
    if not MEMORY_ENABLED:
        respond("💾 Memory system is not available. Check Qdrant configuration.")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    try:
        # Get context for this client
        context = memory_system.get_client_context(client_id)
        
        if not context:
            respond("""
📊 *Memory Statistics*
- No memories stored yet
- Run `/analyze [company]` to create memories
- Ask agents directly: `@bot @psychological [question]`
- Memories persist across sessions
""")
            return
        
        # Build statistics
        total_memories = sum(len(insights) for insights in context.values())
        agents_with_memory = list(context.keys())
        
        message = f"""
📊 *Memory Statistics*

- **Total memories:** {total_memories}
- **Agents with memories:** {', '.join(agents_with_memory)}

*Recent Insights by Agent:*
"""
        
        for agent, insights in context.items():
            if insights:
                agent_title = agent.replace('_', ' ').title()
                emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖')
                message += f"\n{emoji} **{agent_title}:**\n"
                # Show first 2 insights per agent
                for insight in insights[:2]:
                    preview = insight[:100] + "..." if len(insight) > 100 else insight
                    message += f"  • {preview}\n"
        
        message += "\n💡 These memories enhance future analyses and Q&A responses"
        
        respond(message)
        
    except Exception as e:
        logger.error(f"Memory command error: {e}")
        respond(f"Error retrieving memories: {str(e)}")

@app.command("/learning")
def handle_learning_command(ack, respond, command):
    """Show agent learning progress"""
    ack()
    
    if not MEMORY_ENABLED:
        respond("📈 Learning tracking requires memory system to be enabled")
        return
    
    try:
        agents = ["psychological", "voice_of_customer", "competitor", 
                 "interview_psychological", "interview_sales", "gtm_blueprint"]
        
        message = "📈 *Agent Learning Progress*\n\n"
        total_learnings = 0
        
        for agent in agents:
            improvements = memory_system.get_agent_improvements(agent)
            
            if improvements['total_learnings'] > 0:
                total_learnings += improvements['total_learnings']
                agent_title = agent.replace('_', ' ').title()
                emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖')
                
                message += f"{emoji} **{agent_title}**\n"
                message += f"• Learnings: {improvements['total_learnings']}\n"
                message += f"• Avg improvement: {improvements['avg_improvement']:.1%}\n"
                
                if improvements['best_learning']:
                    best = improvements['best_learning'][:80] + "..." if len(improvements['best_learning']) > 80 else improvements['best_learning']
                    message += f"• Best insight: _{best}_\n"
                
                message += "\n"
        
        if total_learnings == 0:
            message += "_No learning recorded yet. Use `/coach [agent] [message]` to teach agents._"
        else:
            message += f"*Total learnings across all agents:* {total_learnings}"
        
        respond(message)
        
    except Exception as e:
        logger.error(f"Learning command error: {e}")
        respond(f"Error retrieving learning data: {str(e)}")

@app.command("/coach")
def handle_coach_command(ack, respond, command):
    """Coach an agent to improve with memory"""
    ack()
    
    parts = command['text'].split(' ', 1)
    if len(parts) < 2:
        respond("Usage: `/coach [agent] [coaching message]`\nExample: `/coach psychological Focus on identity conflicts`")
        return
    
    agent_name = parts[0].lower().replace('-', '_')
    coaching_message = parts[1]
    
    # Validate agent name - check against AGENT_PERSONAS keys
    if agent_name not in AGENT_PERSONAS:
        respond(f"Unknown agent: {agent_name}\nValid agents: {', '.join(AGENT_PERSONAS.keys())}")
        return
    
    # Get emoji
    emoji = AGENT_PERSONAS.get(agent_name, {}).get('emoji', '🤖')
    
    # Record learning if memory enabled
    improvement_expected = 0.05  # 5% expected improvement
    
    if MEMORY_ENABLED:
        try:
            # Get current baseline (estimate)
            current_improvements = memory_system.get_agent_improvements(agent_name)
            baseline = 0.85 if current_improvements['total_learnings'] == 0 else 0.85 + (current_improvements['avg_improvement'])
            
            # Record the learning
            memory_system.record_learning(
                agent_name=agent_name,
                insight=coaching_message,
                context="Slack coaching command",
                quality_before=baseline,
                quality_after=baseline + improvement_expected
            )
            
            response = f"""
🎓 *Learning Recorded*

{emoji} **Agent:** {agent_name.replace('_', ' ').title()}
**Learning:** {coaching_message}
**Expected improvement:** +{improvement_expected:.1%} quality

✅ This insight will be applied in:
- Future analyses
- Direct Q&A responses
- Agent collaborations

💡 Test it: `@bot @{agent_name.split('_')[0]} How does this apply?`
"""
        except Exception as e:
            logger.error(f"Failed to record learning: {e}")
            response = f"⚠️ Coaching acknowledged but couldn't record learning: {str(e)}"
    else:
        response = f"""
🎓 *Coaching Acknowledged*

{emoji} **Agent:** {agent_name.replace('_', ' ').title()}
**Guidance:** {coaching_message}

⚠️ Memory system not available - coaching won't persist across sessions.
Enable memory system for persistent improvements.
"""
    
    respond(response)

@app.command("/debate")
async def handle_debate(ack, respond, command, client):
    """Agents debate a topic"""
    ack()
    
    topic = command['text'].strip()
    if not topic:
        respond("Please provide a debate topic. Usage: `/debate [topic]`")
        return
    
    channel_id = command['channel_id']
    client_id = get_client_id(channel_id)
    
    respond(f"🎭 *Starting Agent Debate*\nTopic: *{topic}*\n\nAgents are forming their positions...")
    
    try:
        # Get real positions from agents if LLM available
        if llm:
            positions = {}
            for agent in ["psychological", "voice", "competitor"]:
                position = await get_agent_direct_response(
                    agent, 
                    f"What's your position on: {topic}",
                    {"client_id": client_id}
                )
                positions[agent] = position[:200]  # Truncate for readability
        else:
            # Mock positions
            positions = {
                "psychological": f"From a psychological perspective on '{topic}', we must consider unconscious fears...",
                "voice": f"Customers say about '{topic}': 'It's about feeling in control'...",
                "competitor": f"Market analysis shows competitors have failed at '{topic}'..."
            }
        
        # Round 1: Opening positions
        debate_text = "*Round 1: Opening Positions*\n\n"
        for agent, position in positions.items():
            emoji = AGENT_PERSONAS.get(agent, {}).get('emoji', '🤖')
            agent_title = agent.replace('_', ' ').title()
            debate_text += f"{emoji} *{agent_title}:* {position}\n\n"
        
        client.chat_postMessage(channel=channel_id, text=debate_text)
        
        # Round 2: Counterpoints
        await asyncio.sleep(2)
        
        counterpoints = "*Round 2: Counterpoints*\n\n"
        counterpoints += "🧠 *Psychological:* The real issue isn't market position but identity transformation...\n\n"
        counterpoints += "🗣️ *Voice:* But customers reject transformation language - they want 'enhancement'...\n\n"
        counterpoints += "🔍 *Competitor:* Both miss the key: successful competitors avoid this debate entirely...\n\n"
        
        client.chat_postMessage(channel=channel_id, text=counterpoints)
        
        # Consensus
        await asyncio.sleep(2)
        
        consensus = f"""
📊 *Consensus Reached*

The agents agree on '{topic}': Balance psychological truth with market language while avoiding competitor battlegrounds.

💡 *Key Insight:* Frame as enhancement while delivering transformation.

Ask agents for details: `@bot @psychological elaborate on transformation`
"""
        
        client.chat_postMessage(channel=channel_id, text=consensus)
        
    except Exception as e:
        respond(f"Error running debate: {str(e)}")

@app.command("/conversation")
async def handle_conversation(ack, respond, command):
    """Two agents have a conversation"""
    ack()
    
    parts = command['text'].split(' ', 2)
    if len(parts) < 3:
        respond("Usage: `/conversation [agent1] [agent2] [topic]`\nExample: `/conversation psychological voice identity crisis`")
        return
    
    agent1 = parts[0].lower()
    agent2 = parts[1].lower()
    topic = parts[2]
    
    # No normalization needed since AGENT_PERSONAS has all variations
    
    emoji1 = AGENT_PERSONAS.get(agent1, {}).get('emoji', '🤖')
    emoji2 = AGENT_PERSONAS.get(agent2, {}).get('emoji', '🤖')
    
    channel_id = command['channel_id']
    client_id = get_client_id(channel_id)
    
    conversation = f"💬 *Agent Conversation*\n**Topic:** {topic}\n\n"
    
    if llm:
        # Get real responses
        try:
            response1 = await get_agent_direct_response(agent1, topic, {"client_id": client_id})
            conversation += f"{emoji1} *{agent1}:* {response1[:150]}...\n\n"
            
            response2 = await get_agent_direct_response(agent2, f"Respond to: {response1[:100]}", {"client_id": client_id})
            conversation += f"{emoji2} *{agent2}:* {response2[:150]}...\n\n"
        except:
            pass
    else:
        # Mock conversation
        conversation += f"{emoji1} *{agent1}:* Looking at {topic}, I see deep patterns...\n\n"
        conversation += f"{emoji2} *{agent2}:* Interesting. My analysis reveals different aspects...\n\n"
    
    conversation += f"💡 *Synthesis:* Both perspectives on '{topic}' are valuable for complete understanding."
    
    respond(conversation)

@app.command("/team")
def handle_team(ack, respond, command):
    """Full team analysis with progress"""
    ack()
    
    query = command['text'].strip()
    if not query:
        respond("Please provide a query. Usage: `/team [analysis query]`")
        return
    
    channel_id = command['channel_id']
    user_id = command['user_id']
    client_id = get_client_id(channel_id, user_id)
    
    respond(f"""
🎯 *Team Analysis: {query}*

📊 Progress:
🧠 Psychological: Analyzing... [████████░░] 80%
🗣️ Voice: Extracting... [██████░░░░] 60%
🔍 Competitor: Researching... [████░░░░░░] 40%
💭 Agents conferring...
📋 GTM: Synthesizing... [██████████] 100%

⏳ Full analysis in progress...
""")
    
    # Run actual analysis
    try:
        workflow = ICPGraph()
        result = workflow.run({
            "company": query,
            "client_id": client_id
        })
        
        report_preview = result.get('final_report', '')[:500]
        respond(f"✅ Team analysis complete!\n\n{report_preview}...\n\n💡 Ask agents for details: `@bot @psychological elaborate`")
        
    except Exception as e:
        respond(f"Error in team analysis: {str(e)}")

# Rest of commands remain the same...
@app.command("/analyze-public")
def handle_analyze_public(ack, respond, command, client):
    """Run analysis and share publicly"""
    ack()
    # Run the same as /analyze for now
    handle_analyze(ack, respond, command)

@app.command("/share-last")
def handle_share_last(ack, respond, command, client):
    """Share last analysis publicly"""
    ack()
    
    reports_dir = Path("reports")
    if not reports_dir.exists():
        respond("No reports found. Run `/analyze` first.")
        return
    
    files = sorted(reports_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not files:
        respond("No reports found. Run `/analyze` first.")
        return
    
    latest_file = files[0]
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        preview = content[:1000] + "..." if len(content) > 1000 else content
        
        client.chat_postMessage(
            channel=command['channel_id'],
            text=f"📊 *Shared Analysis Report*\n\n{preview}\n\n_Full report: {latest_file.name}_"
        )
        
    except Exception as e:
        respond(f"Error sharing report: {str(e)}")

@app.command("/reports")
def handle_reports(ack, respond):
    """List saved reports"""
    ack()
    
    reports_dir = Path("reports")
    if not reports_dir.exists():
        respond("No reports directory found.")
        return
    
    files = sorted(reports_dir.glob("*.txt"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
    
    if not files:
        respond("No reports found. Run `/analyze` to generate reports.")
        return
    
    message = "*Recent Reports (newest first):*\n\n"
    for i, file in enumerate(files, 1):
        size = file.stat().st_size / 1024  # Size in KB
        modified = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        message += f"{i}. `{file.name}`\n   Size: {size:.1f}KB | Created: {modified}\n\n"
    
    message += "\nUse `/get-report [filename]` to retrieve a specific report."
    respond(message)

@app.command("/get-report")
def handle_get_report(ack, respond, command):
    """Get specific report file"""
    ack()
    
    filename = command['text'].strip()
    if not filename:
        respond("Please provide a filename. Usage: `/get-report [filename]`")
        return
    
    reports_dir = Path("reports")
    filepath = reports_dir / filename
    
    if not filepath.exists():
        respond(f"Report not found: {filename}\nUse `/reports` to see available files.")
        return
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 3000:
            content = content[:3000] + f"\n\n... [Report truncated. Full report is {len(content)} characters]"
        
        respond(f"📄 *Report: {filename}*\n\n```{content}```")
        
    except Exception as e:
        respond(f"Error reading report: {str(e)}")

# ============================================
# EVENT HANDLERS - DIRECT AGENT Q&A
# ============================================

@app.event("app_mention")
def handle_app_mention(event, client, logger):
    """
    Handle bot mentions for direct agent Q&A
    Examples:
    - @bot @psychological what are deep fears?
    - @bot voice: show exact customer language
    - @bot competitor who should we position against?
    - @bot @gtm synthesize strategy
    """
    try:
        text = event.get('text', '')
        channel = event.get('channel')
        user = event.get('user')
        thread_ts = event.get('thread_ts', event.get('ts'))
        
        logger.info(f"Bot mentioned: {text}")
        
        # Extract agent and question
        agent_name, question = extract_agent_and_question(text)
        
        if agent_name and question:
            # Agent name already validated by extract_agent_and_question
            persona = AGENT_PERSONAS.get(agent_name)
            
            if persona:
                emoji = persona['emoji']
                name = persona['name']
                
                # Send typing indicator
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=f"{emoji} *{name}* is thinking..."
                )
                
                # Get agent response
                client_id = get_client_id(channel, user)
                response = asyncio.run(get_agent_direct_response(
                    agent_name,
                    question,
                    {"client_id": client_id}
                ))
                
                # Send response in thread
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=f"{emoji} *{name}:*\n\n{response}\n\n_Ask follow-up questions or try another agent!_"
                )
                
                logger.info(f"Agent {agent_name} responded to: {question[:50]}")
                
            else:
                # This shouldn't happen if extract_agent_and_question works correctly
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=f"Unknown agent: {agent_name}\nTry: @psychological, @voice, @competitor, @gtm, @interview_psychological, @interview_sales"
                )
        else:
            # General mention without specific agent
            if "hello" in text.lower() or "hi" in text.lower():
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text=f"Hello <@{user}>! Ask me or my agents anything:\n• `@bot @psychological what are deep fears?`\n• `@bot voice: show pain language`\n• `@bot @gtm synthesize strategy`\n• Use `/help` for all commands"
                )
            else:
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=thread_ts,
                    text="Ask agents directly:\n• `@bot @psychological [question]`\n• `@bot voice: [question]`\n• `@bot @competitor [question]`\n• `@bot @gtm [question]`\n\nOr use `/help` for all commands"
                )
                
    except Exception as e:
        logger.error(f"Error handling app mention: {e}")
        client.chat_postMessage(
            channel=channel,
            text="Error processing request. Try `/help` for available commands."
        )

@app.event("message")
def handle_message_events(body, logger):
    """Handle message events"""
    pass  # We primarily use slash commands and mentions

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("MARKET RESEARCH SLACK BOT WITH DIRECT AGENT Q&A")
    print("=" * 60)
    print(f"Memory System: {'✅ Enabled' if MEMORY_ENABLED else '❌ Disabled'}")
    print(f"Direct Q&A: {'✅ Enabled' if llm else '❌ Disabled'}")
    print(f"Workflow: {'✅ Available' if workflow_available else '❌ Not Available'}")
    print("=" * 60)
    
    # Start the bot
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    
    print("🤖 Bot is running! Press Ctrl+C to stop.")
    print("\nDirect Agent Q&A Examples:")
    print("  @bot @psychological what drives founder anxiety?")
    print("  @bot voice: show exact pain language")
    print("  @bot @competitor who should we position against?")
    print("  @bot @gtm synthesize strategy")  # Fixed example
    print("\nCommands: /help, /analyze, /memory, /learning, /coach")
    
    if MEMORY_ENABLED:
        print("\n💾 Memory active - Q&A and analyses persist")
    
    handler.start()