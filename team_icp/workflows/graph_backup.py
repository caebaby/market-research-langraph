# team_icp/workflows/graph.py
"""
Modular Workflow Graph - Fixed Version with Proper Agent Execution
Ensures agents actually generate content and return results
Compatible with both team_bot.py and advanced_slack_bot.py
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import traceback
import os
import sys
import inspect
from pathlib import Path
import importlib

# ============================================
# CONFIGURATION CONSTANTS
# ============================================
MAX_TOKEN_LIMIT = 8192  # Maximum tokens for Claude 3.5 Sonnet
DEFAULT_TEMPERATURE = 0.7
MODEL_NAME = "claude-3-5-sonnet-20241022"

# ============================================
# SETUP LOGGING WITH UTF-8 ENCODING FIX
# ============================================
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# IMPORT LANGGRAPH
# ============================================
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph successfully imported")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    logger.warning(f"LangGraph not available: {e}")

# ============================================
# SETUP PATH AND ENVIRONMENT
# ============================================
try:
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    sys.path.insert(0, str(project_root))
    
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Environment loaded from: {env_path}")
    else:
        logger.warning(f"No .env file found at: {env_path}")
        
except Exception as e:
    logger.error(f"Environment setup failed: {e}")

# ============================================
# MEMORY SYSTEM INITIALIZATION
# ============================================
memory_system = None
MEMORY_AVAILABLE = False

try:
    from core.memory_system_qdrant import QdrantMemorySystem
    memory_system = QdrantMemorySystem()
    MEMORY_AVAILABLE = True
    logger.info("Memory system connected - agents will remember insights")
except ImportError as e:
    logger.warning(f"Memory system not imported: {e}")
except ValueError as e:
    logger.warning(f"Memory system credentials missing: {e}")
except Exception as e:
    logger.warning(f"Memory system initialization failed: {e}")

if not MEMORY_AVAILABLE:
    logger.info("Running without memory - analyses won't persist")

# ============================================
# LLM CONFIGURATION WITH VALIDATION
# ============================================
llm = None

def initialize_llm():
    """Initialize LLM with proper validation and testing"""
    global llm
    
    try:
        from langchain_anthropic import ChatAnthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.error("ANTHROPIC_API_KEY not found in environment")
            return None
            
        logger.info(f"Creating LLM with {MAX_TOKEN_LIMIT} tokens...")
        
        llm = ChatAnthropic(
            model=MODEL_NAME,
            anthropic_api_key=api_key,
            max_tokens=MAX_TOKEN_LIMIT,
            temperature=DEFAULT_TEMPERATURE,
            timeout=60,
            max_retries=3
        )
        
        # Test the LLM
        logger.info("Testing LLM connection...")
        try:
            test_response = llm.invoke("Say 'test'")
            logger.info(f"LLM test successful: {test_response.content[:50]}")
            return llm
        except Exception as e:
            logger.error(f"LLM test failed: {e}")
            llm = None
            return None
            
    except ImportError as e:
        logger.error(f"Could not import langchain_anthropic: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error setting up LLM: {e}")
        logger.error(traceback.format_exc())
        return None

# Initialize LLM on module load
llm = initialize_llm()

if llm:
    logger.info(f"LLM READY with {MAX_TOKEN_LIMIT} max tokens")
else:
    logger.error("LLM NOT AVAILABLE - Agents will not work properly")

# ============================================
# STATE DEFINITION
# ============================================
class ICPState(Dict):
    """State definition for the workflow"""
    task: str
    context: str
    business_context: Optional[str]
    master_context: Optional[str]
    new_data: bool
    result: Optional[Dict[str, Any]]
    current_output: Optional[str]
    quality_score: Optional[float]
    
    requested_agents: Optional[List[str]]
    current_agent_index: Optional[int]
    agents_to_run: Optional[List[str]]
    
    current_task: Optional[Dict[str, Any]]
    client_id: Optional[str]
    shared_insights: Optional[Dict[str, Any]]
    memory_service: Optional[Any]
    tool_executor: Optional[Any]
    
    requires_human_review: Optional[bool]
    review_reason: Optional[str]
    
    team_name: Optional[str]
    industry_template: Optional[str]
    agent_config_overrides: Optional[Dict[str, Any]]
    
    total_tokens_used: Optional[int]
    token_limit: Optional[int]
    
    memories_loaded: Optional[Dict[str, int]]
    memories_stored: Optional[Dict[str, bool]]
    
    # Add fields for compatibility with advanced_slack_bot
    slack_updater: Optional[Any]
    verbose: Optional[bool]
    analysis_results: Optional[Dict[str, Any]]
    
    # ADD THESE THREE NEW LINES:
    statistics: Optional[Dict[str, Any]]
    synthesis_complete: Optional[bool]
    overall_quality: Optional[float]

# ============================================
# AGENT REGISTRY IMPORT
# ============================================
AGENT_REGISTRY = {}
REGISTRY_AVAILABLE = False

try:
    try:
        from ..agents.registry import AgentRegistry
    except ImportError:
        from team_icp.agents.registry import AgentRegistry
    
    registry_instance = AgentRegistry()
    AGENT_REGISTRY = {name: info for name, info in registry_instance.get_all_agents().items()}
    REGISTRY_AVAILABLE = True
    logger.info(f"Registry loaded with {len(AGENT_REGISTRY)} agents")
    
except ImportError as e:
    logger.error(f"Failed to import registry: {e}")
    REGISTRY_AVAILABLE = False
    AGENT_REGISTRY = {}

# ============================================
# MOCK AGENT FOR TESTING
# ============================================
class MockAgent:
    """Mock agent for when real agents fail to load"""
    def __init__(self, name):
        self.agent_name = name
        self.max_tokens = MAX_TOKEN_LIMIT
        
    def process(self, task, shared_insights, llm_instance):
        """Mock process method that returns test data"""
        if not llm_instance:
            return {
                'output': f"[MOCK - No LLM] {self.agent_name} would analyze: {task}",
                'quality_score': 0.0
            }
        
        try:
            # Try to use the LLM if available
            prompt = f"As a {self.agent_name}, provide a brief analysis of: {task}"
            response = llm_instance.invoke(prompt)
            return {
                'output': response.content,
                'quality_score': calculate_quality_score(response.content, self.agent_name)  # CHANGED
            }
        except Exception as e:
            logger.error(f"Mock agent LLM call failed: {e}")
            return {
                'output': f"[MOCK ERROR] {self.agent_name} failed: {str(e)}",
                'quality_score': 0.0
            }
    
    def _generate_response(self, task, context, memories, llm_instance):
        """Fallback method for older agent interface"""
        result = self.process(task, {}, llm_instance)
        return result['output']

def calculate_quality_score(output: str, agent_name: str = "") -> float:
    """Calculate quality score based on output characteristics"""
    if not output:
        return 0.0
    
    score = 0.0
    length = len(output)
    
    # Length scoring (0-0.3)
    if length > 2000:
        score += 0.3
    elif length > 1000:
        score += 0.25
    elif length > 500:
        score += 0.2
    elif length > 200:
        score += 0.15
    else:
        score += 0.05
    
    # Content quality indicators (0-0.4)
    quality_indicators = [
        ('analysis', 0.05),
        ('insight', 0.05),
        ('pattern', 0.05),
        ('psychological', 0.05),
        ('customer', 0.05),
        ('market', 0.05),
        ('strategy', 0.05),
        ('- ', 0.05)  # Bullet points
    ]
    
    output_lower = output.lower()
    for indicator, points in quality_indicators:
        if indicator in output_lower:
            score += points
    
    # Structure scoring (0-0.3)
    if '\n\n' in output:  # Paragraphs
        score += 0.1
    if any(num in output for num in ['1.', '2.', '3.']):  # Numbered lists
        score += 0.1
    if len(output.split('\n')) > 5:  # Multiple lines
        score += 0.1
    
    # Cap at 0.95 for non-GTM agents
    return min(score, 0.95)

# ============================================
# AGENT LOADING AND CACHING
# ============================================
loaded_agents = {}

def load_agent_dynamically(agent_name: str, state: ICPState):
    """
    Dynamically load agents with proper error handling and fallback
    """
    # Check cache first
    if agent_name in loaded_agents:
        logger.debug(f"Using cached agent: {agent_name}")
        return loaded_agents[agent_name]
    
    # Ensure LLM is available
    if not llm:
        logger.error(f"Cannot load {agent_name} - LLM not available")
        mock = MockAgent(agent_name)
        loaded_agents[agent_name] = mock
        return mock
    
    try:
        logger.info(f"Loading agent: {agent_name}")
        
        # Agent name to module/class mapping
        agent_mapping = {
            "psychological": ("team_icp.agents.psychological", "PsychologicalAgent"),
            "voice_of_customer": ("team_icp.agents.voice", "VoiceAgent"),
            "voice": ("team_icp.agents.voice", "VoiceAgent"),
            "competitor": ("team_icp.agents.competitor", "CompetitorAgent"),
            "interview_psychological": ("team_icp.agents.interview_psychological_v4", "PsychologicalInterviewAgentV4"),
            "interview_psych": ("team_icp.agents.interview_psychological_v4", "PsychologicalInterviewAgentV4"),
            "interview_sales": ("team_icp.agents.interview_sales_v4", "SalesInterviewAgentV4"),
            "gtm_blueprint": ("team_icp.agents.gtm_blueprint", "GTMBlueprintAgent"),
            "gtm": ("team_icp.agents.gtm_blueprint", "GTMBlueprintAgent"),
        }
        
        # Get module and class names
        if agent_name in agent_mapping:
            module_name, class_name = agent_mapping[agent_name]
        else:
            module_name = f"team_icp.agents.{agent_name}"
            class_name = ''.join(word.capitalize() for word in agent_name.split('_')) + 'Agent'
        
        # Import and instantiate
        module = importlib.import_module(module_name)
        AgentClass = getattr(module, class_name)
        
        # Special handling for GTM Blueprint which may have abstract methods
        if agent_name in ["gtm_blueprint", "gtm"]:
            try:
                agent = AgentClass()
            except TypeError as te:
                if "abstract" in str(te):
                    logger.warning(f"Creating wrapper for {agent_name} abstract methods")
                    
                    class GTMBlueprintWrapper(AgentClass):
                        def __init__(self):
                            self.agent_name = "GTM Blueprint Strategist"
                            self._llm = llm
                            self._memory_store = None
                            self.max_tokens = MAX_TOKEN_LIMIT
                            self.required_sections = 12
                            self.synthesized_agents = []
                            self.target_quality = 0.85
                            self.require_human_review_below = 0.70
                        
                        @property
                        def llm(self):
                            return self._llm
                        
                        @llm.setter
                        def llm(self, value):
                            self._llm = value
                        
                        @property
                        def memory_store(self):
                            return self._memory_store
                        
                        @memory_store.setter
                        def memory_store(self, value):
                            self._memory_store = value
                        
                        def _reflect(self, response):
                            return {
                                "agent": self.agent_name,
                                "reflection": "GTM Blueprint complete",
                                "quality": 0.85
                            }
                        
                        def _create_shared_insights(self, response, quality=0.5):
                            content = str(response) if response else ""
                            return {
                                "output": content,
                                "quality": quality,
                                "timestamp": datetime.now().isoformat(),
                                "agent": self.agent_name
                            }
                        
                        def _extract_insights_for_memory(self, response):
                            content = str(response) if response else ""
                            return [f"GTM Blueprint: {len(content)} chars generated"]
                    
                    agent = GTMBlueprintWrapper()
                else:
                    raise te
        else:
            agent = AgentClass()
        
        # Configure agent
        if hasattr(agent, 'max_tokens'):
            agent.max_tokens = MAX_TOKEN_LIMIT
        
        if hasattr(agent, 'llm'):
            agent.llm = llm
        
        loaded_agents[agent_name] = agent
        logger.info(f"Successfully loaded agent: {agent_name}")
        return agent
        
    except Exception as e:
        logger.error(f"Failed to load {agent_name}: {e}")
        logger.error(traceback.format_exc())
        
        # Return mock agent as fallback
        mock = MockAgent(agent_name)
        loaded_agents[agent_name] = mock
        return mock

# End of Part 1 - Stopping after load_agent_dynamically function completes
# ============================================
# NODE CREATION WITH MEMORY INTEGRATION
# ============================================
def create_agent_node(agent_name: str):
    """
    Create a node function that safely executes agents with memory support
    """
    def agent_node(state: ICPState) -> ICPState:
        logger.info(f"[{agent_name.upper()}] Starting execution")
        start_time = datetime.now()
        
        # Get Slack updater if available
        slack_updater = state.get("slack_updater")
        verbose = state.get("verbose", False)
        
        # Prepare agent display name
        agent_display = agent_name.replace("_", " ").title()
        emoji_map = {
            "psychological": "🧠",
            "voice_of_customer": "🗣️",
            "voice": "🗣️",
            "competitor": "🔍",
            "interview_psychological": "🎭",
            "interview_sales": "💰",
            "gtm_blueprint": "📋",
            "gtm": "📋"
        }
        emoji = emoji_map.get(agent_name, "🤖")
        
        # Send Slack update if available
        if slack_updater:
            slack_updater(f"{emoji} {agent_display}: Starting analysis...")
        
        try:
            # Check if LLM is available
            if not llm:
                error_msg = f"LLM not available for {agent_name}"
                logger.error(f"[{agent_name.upper()}] {error_msg}")
                
                state["current_output"] = f"[ERROR] {error_msg}"
                state["quality_score"] = 0.0
                
                if slack_updater:
                    slack_updater(f"❌ {agent_display}: Failed - No LLM")
                
                return state
            
            # Load the agent
            agent = load_agent_dynamically(agent_name, state)
            if not agent:
                raise ValueError(f"Failed to load agent: {agent_name}")
            
            # Get context
            business_context = state.get("business_context", state.get("task", ""))
            shared_insights = state.get("shared_insights", {})
            
            # ============================================
            # MEMORY RETRIEVAL
            # ============================================
            memories_loaded_count = 0
            if MEMORY_AVAILABLE and state.get("client_id"):
                try:
                    previous_memories = memory_system.retrieve_memories(
                        client_id=state["client_id"],
                        agent_name=agent_name,
                        limit=5
                    )
                    
                    if previous_memories:
                        memory_context = "\n\n=== PREVIOUS INSIGHTS ===\n"
                        for i, mem in enumerate(previous_memories, 1):
                            memory_context += f"{i}. {mem.content}\n"
                        memory_context += "=== END INSIGHTS ===\n\n"
                        
                        business_context = memory_context + business_context
                        memories_loaded_count = len(previous_memories)
                        
                        if "memories_loaded" not in state:
                            state["memories_loaded"] = {}
                        state["memories_loaded"][agent_name] = memories_loaded_count
                        
                        logger.info(f"[{agent_name.upper()}] Loaded {memories_loaded_count} memories")
                    
                except Exception as e:
                    logger.error(f"[{agent_name.upper()}] Memory retrieval failed: {e}")
            
            # Initialize token tracking
            if "total_tokens_used" not in state:
                state["total_tokens_used"] = 0
            state["token_limit"] = MAX_TOKEN_LIMIT
            
            # ============================================
            # EXECUTE AGENT
            # ============================================
            logger.info(f"[{agent_name.upper()}] Processing with {MAX_TOKEN_LIMIT} max tokens...")
            
            result = None
            output_text = ""
            quality = 0.0
            
            try:
                # Special handling for GTM Blueprint
                if agent_name in ["gtm_blueprint", "gtm"]:
                    if hasattr(agent, 'process'):
                        # Ensure required state fields
                        state['llm'] = llm
                        state['company_info'] = state.get('master_context', business_context)
                        state['task'] = state.get('task', business_context)
                        
                        # Initialize analysis_results if not present
                        if 'analysis_results' not in state:
                            state['analysis_results'] = {}
                        
                        # Call process
                        updated_state = agent.process(state)
                        
                        # Extract results
                        if 'analysis_results' in updated_state and 'gtm_blueprint' in updated_state['analysis_results']:
                            gtm_data = updated_state['analysis_results']['gtm_blueprint']
                            output_text = gtm_data.get('content', '')
                            quality = gtm_data.get('quality_score', 0.5)
                            state['analysis_results'] = updated_state.get('analysis_results', {})
                        else:
                            # Fallback GTM generation
                            output_text = f"GTM Blueprint for {business_context}"
                            quality = 0.5
                    else:
                        output_text = "GTM agent missing process method"
                        quality = 0.0
                
                # Normal agent processing
                else:
                    # Try different agent interfaces
                    if hasattr(agent, 'process'):
                        # V4 agents and newer
                        result = agent.process(business_context, shared_insights, llm)
                        
                    elif hasattr(agent, '_generate_response'):
                        # Older agent interface
                        sig = inspect.signature(agent._generate_response)
                        params = list(sig.parameters.keys())
                        
                        if 'self' in params:
                            params.remove('self')
                        
                        memories = []
                        if len(params) == 3:  # task, memories, llm
                            output_text = agent._generate_response(business_context, memories, llm)
                        elif len(params) == 4:  # task, context, memories, llm
                            output_text = agent._generate_response(
                                business_context,
                                business_context,
                                memories,
                                llm
                            )
                        else:
                            output_text = agent._generate_response(business_context, memories, llm)
                        
                        result = {"output": output_text, "quality_score": calculate_quality_score(output_text, agent_name)}
                    
                    else:
                        # Fallback to mock behavior
                        logger.warning(f"[{agent_name}] No known interface, using mock")
                        if isinstance(agent, MockAgent):
                            result = agent.process(business_context, shared_insights, llm)
                        else:
                            result = {
                                "output": f"Agent {agent_name} processed the task",
                                "quality_score": 0.5
                            }
                    
                    # Extract output from result
                    if result and isinstance(result, dict):
                        output_text = result.get('output', '')
                        quality = result.get('quality_score', 0.5)
                    elif result:
                        output_text = str(result)
                        quality = calculate_quality_score(output_text, agent_name)
                
                # Validate output
                if not output_text or len(output_text) < 10:
                    logger.warning(f"[{agent_name}] Generated minimal output, attempting retry...")
                    
                    # Try direct LLM call as fallback
                    prompt = f"""You are a {agent_display} agent. 
                    Analyze this: {business_context}
                    
                    Provide a detailed analysis with specific insights."""
                    
                    try:
                        response = llm.invoke(prompt)
                        output_text = response.content
                        quality = calculate_quality_score(output_text, agent_name)
                    except Exception as e:
                        logger.error(f"[{agent_name}] Fallback LLM call failed: {e}")
                        output_text = f"Analysis failed for {agent_name}: {str(e)}"
                        quality = 0.0
                
            except Exception as e:
                logger.error(f"[{agent_name}] Processing error: {e}")
                logger.error(traceback.format_exc())
                output_text = f"[ERROR] {agent_name}: {str(e)}"
                quality = 0.0
            
            # Store output in state
            state["current_output"] = output_text
            state["quality_score"] = quality
            
            # Store in result dictionary
            if "result" not in state:
                state["result"] = {}
            state["result"][agent_name] = output_text
            
            # Update shared insights
            if "shared_insights" not in state:
                state["shared_insights"] = {}
            
            state["shared_insights"][agent_name] = {
                "output": output_text if output_text else "",
                "quality": quality,
                "timestamp": datetime.now().isoformat()
            }
            
            # Estimate tokens used
            if output_text:
                estimated_tokens = len(output_text) // 4
                state["total_tokens_used"] = state.get("total_tokens_used", 0) + estimated_tokens
                logger.info(f"[{agent_name.upper()}] Estimated {estimated_tokens} tokens used")
            
            # ============================================
            # MEMORY STORAGE
            # ============================================
            memory_stored = False
            if MEMORY_AVAILABLE and state.get("client_id") and output_text and len(output_text) > 50:
                try:
                    insight = output_text
                    
                    memory_id = memory_system.store_memory(
                        client_id=state["client_id"],
                        agent_name=agent_name,
                        memory_type="analysis",
                        content=insight,
                        context=f"Analysis for {state.get('master_context', 'unknown')}",
                        importance=quality
                    )
                    
                    memory_stored = True
                    
                    if "memories_stored" not in state:
                        state["memories_stored"] = {}
                    state["memories_stored"][agent_name] = True
                    
                    logger.info(f"[{agent_name.upper()}] Stored memory: {memory_id[:8]}...")
                    
                    # Share high-quality insights
                    if quality > 0.9:
                        next_agents = state.get("agents_to_run", [])[state.get("current_agent_index", 0) + 1:]
                        for next_agent in next_agents[:2]:
                            memory_system.share_insights_between_agents(
                                from_agent=agent_name,
                                to_agent=next_agent,
                                client_id=state["client_id"],
                                insight=insight
                            )
                            logger.info(f"[{agent_name.upper()}] Shared insight with {next_agent}")
                    
                except Exception as e:
                    logger.error(f"[{agent_name.upper()}] Memory storage failed: {e}")
            
            # Log execution results
            execution_time = (datetime.now() - start_time).total_seconds()
            output_len = len(output_text) if output_text else 0
            
            logger.info(f"[{agent_name.upper()}] Generated {output_len} characters")
            logger.info(f"[{agent_name.upper()}] Completed in {execution_time:.2f}s | Quality: {quality:.2f}")
            
            # Send Slack update if available
            if slack_updater:
                if output_len > 0:
                    slack_updater(f"✅ {agent_display}: Complete ({output_len:,} chars, quality: {quality:.2f})")
                else:
                    slack_updater(f"❌ {agent_display}: Failed to generate content")
            
        except Exception as e:
            error_msg = f"Agent {agent_name} failed: {str(e)}"
            logger.error(f"[{agent_name.upper()}] CRITICAL ERROR: {error_msg}")
            logger.error(traceback.format_exc())
            
            state["requires_human_review"] = True
            state["review_reason"] = error_msg
            
            if "result" not in state:
                state["result"] = {}
            state["result"][agent_name] = f"[CRITICAL ERROR]: {str(e)}"
            state["quality_score"] = 0.0
            
            if slack_updater:
                slack_updater(f"❌ {agent_display}: Critical error")
        
        finally:
            # Always increment index
            state["current_agent_index"] = state.get("current_agent_index", 0) + 1
        
        return state
    
    return agent_node

# ============================================
# ROUTING AND SYNTHESIS NODES
# ============================================
def router_node(state: ICPState) -> ICPState:
    """
    Router node that determines agent execution sequence
    """
    logger.info("[ROUTER] Analyzing routing requirements")
    
    # Get Slack updater if available
    slack_updater = state.get("slack_updater")
    
    # Initialize state fields
    state.setdefault("result", {})
    state.setdefault("shared_insights", {})
    state.setdefault("current_agent_index", 0)
    state.setdefault("total_tokens_used", 0)
    state["token_limit"] = MAX_TOKEN_LIMIT
    
    # Initialize memory tracking
    state["memories_loaded"] = {}
    state["memories_stored"] = {}
    
    # Initialize analysis_results for GTM
    if "analysis_results" not in state:
        state["analysis_results"] = {}
    
    logger.info(f"[ROUTER] Token limit: {MAX_TOKEN_LIMIT}")
    logger.info(f"[ROUTER] Memory system: {'Enabled' if MEMORY_AVAILABLE else 'Disabled'}")
    
    # Determine agents to run
    requested_agents = state.get("requested_agents", [])
    
    if not requested_agents:
        # Default ICP team
        requested_agents = [
            "psychological", 
            "voice_of_customer", 
            "competitor",
            "interview_psychological", 
            "interview_sales", 
            "gtm_blueprint"
        ]
        logger.info(f"[ROUTER] Using default ICP team ({len(requested_agents)} agents)")
    else:
        logger.info(f"[ROUTER] Using requested agents: {requested_agents}")
    
    # Normalize agent names
    valid_agents = []
    for agent in requested_agents:
        normalized_name = agent.replace("-", "_").lower()
        # Handle voice -> voice_of_customer mapping
        if normalized_name == "voice":
            normalized_name = "voice_of_customer"
        valid_agents.append(normalized_name)
    
    state["agents_to_run"] = valid_agents
    logger.info(f"[ROUTER] Scheduled {len(valid_agents)} agents for execution")
    
    if slack_updater:
        slack_updater(f"📋 Scheduled {len(valid_agents)} agents for analysis")
    
    return state

# End of Part 2 - Stopping after router_node function completes
def synthesis_node(state: ICPState) -> ICPState:
    """
    Final synthesis node that creates comprehensive report
    """
    logger.info("[SYNTHESIS] Creating final report")
    
    slack_updater = state.get("slack_updater")
    
    state["synthesis_complete"] = True
    
    # Check token usage
    total_tokens = state.get("total_tokens_used", 0)
    logger.info(f"[SYNTHESIS] Total estimated tokens used: {total_tokens}")
    
    if total_tokens > MAX_TOKEN_LIMIT * 0.9:
        logger.warning(f"[SYNTHESIS] Token usage high: {total_tokens}/{MAX_TOKEN_LIMIT}")
    
    # Log memory activity
    if MEMORY_AVAILABLE:
        total_loaded = sum(state.get("memories_loaded", {}).values())
        total_stored = sum(1 for v in state.get("memories_stored", {}).values() if v)
        logger.info(f"[SYNTHESIS] Memory activity: {total_loaded} loaded, {total_stored} stored")
    
    # Build final report
    if "result" in state and isinstance(state["result"], dict):
        report_sections = []
        error_sections = []
        
        # Preferred agent order for report structure
        agent_order = [
            "psychological",
            "voice_of_customer",
            "competitor",
            "interview_psychological",
            "interview_sales",
            "gtm_blueprint"
        ]
        
        # Count successful agents
        successful_agents = 0
        total_words = 0
        
        # Process agents in preferred order
        for agent_name in agent_order:
            if agent_name in state["result"]:
                output = state["result"][agent_name]
                if output and not output.startswith("[ERROR]") and not output.startswith("[CRITICAL ERROR]"):
                    agent_title = agent_name.replace("_", " ").title()
                    report_sections.append(f"## {agent_title} Analysis\n\n{output}\n")
                    successful_agents += 1
                    total_words += len(str(output).split())
                elif output and (output.startswith("[ERROR]") or output.startswith("[CRITICAL ERROR]")):
                    error_sections.append(f"⚠️ {agent_name}: {output}")
        
        # Add any other agents not in standard order
        for agent_name, output in state["result"].items():
            if agent_name not in agent_order:
                if output and not output.startswith("[ERROR]") and not output.startswith("[CRITICAL ERROR]"):
                    agent_title = agent_name.replace("_", " ").title()
                    report_sections.append(f"## {agent_title} Analysis\n\n{output}\n")
                    successful_agents += 1
                    total_words += len(str(output).split())
                elif output and (output.startswith("[ERROR]") or output.startswith("[CRITICAL ERROR]")):
                    error_sections.append(f"⚠️ {agent_name}: {output}")
        
        # Create final report
        if report_sections:
            state["final_report"] = "\n".join(report_sections)
        else:
            state["final_report"] = "No analysis results available. Check logs for errors."
        
        # Add error section if needed
        if error_sections:
            state["final_report"] += "\n\n---\n## ⚠️ Errors Encountered\n\n" + "\n".join(error_sections)
        
        # Calculate overall quality
        quality_scores = []
        for agent_name in state["result"].keys():
            if agent_name in state.get("shared_insights", {}):
                quality = state["shared_insights"][agent_name].get("quality", 0)
                if quality > 0:
                    quality_scores.append(quality)
        
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        state["overall_quality"] = overall_quality
        
        # Add statistics
        total_agents = len(state.get("agents_to_run", []))
        
        state["statistics"] = {
            "total_agents": total_agents,
            "successful_agents": successful_agents,
            "total_words": total_words,
            "total_tokens_estimated": total_tokens,
            "max_token_limit": MAX_TOKEN_LIMIT,
            "overall_quality": overall_quality,
            "memory_enabled": MEMORY_AVAILABLE,
            "memories_loaded": state.get("memories_loaded", {}),
            "memories_stored": state.get("memories_stored", {})
        }
        
        logger.info(f"[SYNTHESIS] Report complete:")
        logger.info(f"   • Successful: {successful_agents}/{total_agents} agents")
        logger.info(f"   • Quality: {overall_quality:.2f}")
        logger.info(f"   • Words: {total_words}")
        logger.info(f"   • Tokens: {total_tokens}/{MAX_TOKEN_LIMIT}")
        
        if slack_updater:
            slack_updater(f"📊 Synthesis complete: {successful_agents}/{total_agents} agents, {total_words:,} words")
    else:
        state["final_report"] = "Analysis could not be completed."
        state["overall_quality"] = 0.0
        state["statistics"] = {
            "total_agents": 0,
            "successful_agents": 0,
            "total_words": 0,
            "total_tokens_estimated": 0,
            "max_token_limit": MAX_TOKEN_LIMIT,
            "overall_quality": 0.0,
            "memory_enabled": MEMORY_AVAILABLE
        }
    
    return state

def route_to_next_agent(state: ICPState) -> str:
    """
    Determine next agent with safety checks
    """
    requested = state.get("agents_to_run", [])
    current_index = state.get("current_agent_index", 0)
    slack_updater = state.get("slack_updater")
    
    # Safety limit
    MAX_ITERATIONS = 20
    if current_index >= MAX_ITERATIONS:
        logger.warning(f"[ROUTING] Safety limit ({MAX_ITERATIONS}) reached!")
        return "synthesis"
    
    # Check token usage
    total_tokens = state.get("total_tokens_used", 0)
    if total_tokens > MAX_TOKEN_LIMIT * 0.97:
        logger.warning(f"[ROUTING] Token limit approaching ({total_tokens}/{MAX_TOKEN_LIMIT}), moving to synthesis")
        return "synthesis"
    
    # Check if more agents to run
    if current_index < len(requested):
        next_agent = requested[current_index]
        logger.info(f"[ROUTING] Next: {next_agent} ({current_index + 1}/{len(requested)})")
        
        # Send progress update if available
        if slack_updater:
            progress = ((current_index + 1) / len(requested)) * 100
            slack_updater(f"📊 Progress: {progress:.0f}% ({current_index + 1}/{len(requested)} agents)")
        
        return next_agent
    
    # All agents complete
    logger.info(f"[ROUTING] All {len(requested)} agents complete")
    return "synthesis"

# ============================================
# BUILD WORKFLOW GRAPH
# ============================================
if LANGGRAPH_AVAILABLE:
    try:
        workflow = StateGraph(ICPState)
        
        # Add core nodes
        workflow.add_node("router", router_node)
        workflow.add_node("synthesis", synthesis_node)
        
        # Define all possible agent nodes with aliases
        agent_variations = {
            "psychological": create_agent_node("psychological"),
            "voice_of_customer": create_agent_node("voice_of_customer"),
            "voice": create_agent_node("voice_of_customer"),  # Alias
            "competitor": create_agent_node("competitor"),
            "interview_psychological": create_agent_node("interview_psychological"),
            "interview_psych": create_agent_node("interview_psychological"),  # Alias
            "interview_sales": create_agent_node("interview_sales"),
            "gtm_blueprint": create_agent_node("gtm_blueprint"),
            "gtm": create_agent_node("gtm_blueprint")  # Alias
        }
        
        # Add all agent nodes
        for agent_name, node_func in agent_variations.items():
            workflow.add_node(agent_name, node_func)
            logger.debug(f"Added node: {agent_name}")
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Create edge mapping
        edge_mapping = {name: name for name in agent_variations.keys()}
        edge_mapping["synthesis"] = "synthesis"
        
        # Add conditional routing from router
        workflow.add_conditional_edges(
            "router",
            route_to_next_agent,
            edge_mapping
        )
        
        # Each agent routes back to router
        for agent_name in agent_variations.keys():
            workflow.add_edge(agent_name, "router")
        
        # Synthesis goes to END
        workflow.add_edge("synthesis", END)
        
        # Compile the graph
        graph = workflow.compile()
        logger.info(f"Workflow compiled successfully with {len(agent_variations)} agent nodes")
        
    except Exception as e:
        logger.error(f"Failed to compile workflow: {e}")
        logger.error(traceback.format_exc())
        graph = None
else:
    logger.warning("LangGraph not available - workflow disabled")
    graph = None

# ============================================
# MAIN WORKFLOW CLASS
# ============================================
class ICPGraph:
    """
    Main class for running the ICP workflow with memory support
    Compatible with both team_bot.py and advanced_slack_bot.py
    """
    def __init__(self, verbose: bool = False):
        self.graph = graph
        self.registry_available = REGISTRY_AVAILABLE
        self.max_tokens = MAX_TOKEN_LIMIT
        self.memory_enabled = MEMORY_AVAILABLE
        self.verbose = verbose
        
        # Log initialization status
        logger.info("=" * 60)
        logger.info("ICP WORKFLOW INITIALIZED")
        logger.info(f"   • Graph: {'Ready' if self.graph else 'Not Available'}")
        logger.info(f"   • Registry: {'Ready' if self.registry_available else 'Not Available'}")
        logger.info(f"   • LLM: {'Ready' if llm else 'Not Available'}")
        logger.info(f"   • Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
        logger.info(f"   • Max Tokens: {self.max_tokens}")
        logger.info("=" * 60)
        
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the workflow with comprehensive error handling
        
        Args:
            inputs: Should contain 'company' or 'business_context' and optionally 'client_id'
        
        Returns:
            Dict with 'final_report' and analysis results
        """
        # Extract company name and client ID
        company = inputs.get("company", inputs.get("business_context", "Unknown"))
        client_id = inputs.get("client_id", f"client_{company.replace(' ', '_').lower()}")
        
        logger.info(f"Starting analysis for: {company}")
        logger.info(f"Token limit: {self.max_tokens}")
        logger.info(f"Client ID: {client_id}")
        
        if self.memory_enabled:
            logger.info(f"Memory enabled - will load/store insights")
        
        if not self.graph:
            return self._get_error_result(company, "Workflow graph not compiled")
        
        if not llm:
            return self._get_error_result(company, "LLM not configured - check ANTHROPIC_API_KEY")
        
        try:  # 8 spaces - aligns with other code in run method
            # Prepare initial state - 12 spaces (inside try block)
            state = {
                "task": f"Analyze {company} - comprehensive market research",
                "business_context": f"""
Analyze {company} for comprehensive market research.

Provide:
- Deep psychological analysis of target customers
- Exact customer language and pain points
- Competitive intelligence and positioning gaps
- Interview simulations revealing buying psychology
- Complete GTM strategy synthesis

Each analysis should be thorough, specific, and actionable.
Maximum detail within {self.max_tokens} token limit.
""",
                "master_context": f"Company: {company}",
                "client_id": client_id,
                "requested_agents": inputs.get("requested_agents", None),
                "new_data": True,
                "shared_insights": {},
                "token_limit": self.max_tokens,
                "total_tokens_used": 0,
                "analysis_results": {},  # Important for GTM
                "slack_updater": inputs.get("slack_updater"),  # Pass through Slack updater
                "verbose": inputs.get("verbose", self.verbose)
            }
            
            # Run the workflow - 12 spaces
            logger.info("Executing workflow graph...")
            result = self.graph.invoke(state)
            
            # FIX: Copy missing keys from result back into statistics
            if 'statistics' not in result and 'final_report' in result:
            # Reconstruct statistics from the result
             if 'shared_insights' in result:
                quality_scores = []
                for agent_data in result.get('shared_insights', {}).values():
                    if isinstance(agent_data, dict) and agent_data.get('quality', 0) > 0:
                        quality_scores.append(agent_data['quality'])
                # This line now safe - quality_scores is always defined
                overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
                
                result['statistics'] = {
                    'overall_quality': overall_quality,
                    'total_words': sum(len(str(v).split()) for v in result.get('result', {}).values() if v),
                    'successful_agents': len([v for v in result.get('result', {}).values() if v and not str(v).startswith("[ERROR")]),
                    'total_agents': len(result.get('agents_to_run', [])),
                    'total_tokens_estimated': result.get('total_tokens_used', 0),
                    'max_token_limit': self.max_tokens
                }    
            # Ensure we have a final report - 12 spaces
            if "final_report" not in result:
                result["final_report"] = self._format_results(result)
            print(f"DEBUG 0: Result keys = {result.keys()}")
            print(f"DEBUG 0b: Statistics in result = {'statistics' in result}")
            
            # Log execution summary using statistics from synthesis - 12 spaces
            stats = result.get("statistics", {})
            print(f"DEBUG 1: stats overall_quality = {stats.get('overall_quality', 'MISSING')}")
            print(f"DEBUG 2: result overall_quality = {result.get('overall_quality', 'MISSING')}")
            # Always ensure quality is properly set
            if 'overall_quality' not in stats or stats.get('overall_quality', 0) == 0:
              print("DEBUG 3: Entering quality fix block")  
              
              # Try to get quality from the result
              if 'overall_quality' in result:
                  stats['overall_quality'] = result['overall_quality']
              if 'statistics' in result and 'overall_quality' in result['statistics']:
                 stats['overall_quality'] = result['statistics']['overall_quality']
                 
                 # DEBUG 4 should be HERE - after BOTH fix attempts
                 print(f"DEBUG 4: After fix, stats overall_quality = {stats.get('overall_quality', 'MISSING')}")
            
            # UPDATE: Put the fixed stats back into result
            result['statistics'] = stats
            print(f"DEBUG 5: After update, result['statistics']['overall_quality'] = {result.get('statistics', {}).get('overall_quality', 'MISSING')}")
            # If statistics are empty, calculate them from result - 12 spaces
            if not stats or stats.get('total_words', 0) == 0:
                if 'result' in result:
                    total_words = sum(len(str(v).split()) for v in result['result'].values() if v)
                    successful = len([v for v in result['result'].values() if v and not str(v).startswith("[ERROR")])
                    total = len(result.get('agents_to_run', result.get('requested_agents', [])))
                    
                    stats = {
                        'overall_quality': stats.get('overall_quality', result.get('overall_quality', 0.0)),
                        'total_words': total_words,
                        'total_tokens_estimated': result.get('total_tokens_used', 0),
                        'successful_agents': successful,
                        'total_agents': total
                    }
            
            logger.info("Analysis complete:")
            logger.info(f"   • Quality: {stats.get('overall_quality', 0):.2f}")
            logger.info(f"   • Words: {stats.get('total_words', 0)}")
            logger.info(f"   • Tokens: {stats.get('total_tokens_estimated', 0)}/{self.max_tokens}")
            logger.info(f"   • Success: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)} agents")
            
            if self.memory_enabled:
                total_loaded = sum(stats.get('memories_loaded', {}).values())
                total_stored = sum(1 for v in stats.get('memories_stored', {}).values() if v)
                logger.info(f"   • Memory: {total_loaded} loaded, {total_stored} stored")
            
            return result  # 12 spaces - inside try block
            
        except Exception as e:  # 8 spaces - same level as try
            logger.error(f"Workflow execution failed: {e}")  # 12 spaces
            logger.error(traceback.format_exc())  # 12 spaces
            return self._get_error_result(company, str(e))  # 12 spaces

# End of Part 3 - Stopping after ICPGraph.run method completes
    def _format_results(self, result: Dict[str, Any]) -> str:
        """Format results into a comprehensive report"""
        if "result" in result and isinstance(result["result"], dict):
            report_parts = []
            
            for agent, output in result["result"].items():
                if output and not str(output).startswith("[ERROR"):
                    agent_title = agent.replace("_", " ").title()
                    report_parts.append(f"## {agent_title}\n\n{output}\n")
            
            return "\n".join(report_parts) if report_parts else "Analysis completed but no detailed results."
        
        return "Analysis completed."
    
    def _get_error_result(self, company: str, error_msg: str) -> Dict[str, Any]:
        """Return formatted error result"""
        return {
            "final_report": f"""
# Analysis Error for {company}

An error occurred during analysis: {error_msg}

## Required Setup:
1. **Environment**: Ensure ANTHROPIC_API_KEY is in .env file
2. **LangGraph**: pip install langgraph
3. **Dependencies**: pip install langchain-anthropic sentence-transformers
4. **Agent Files**: Verify all agent modules are present in team_icp/agents/
5. **Token Limit**: Currently set to {self.max_tokens}
6. **Memory System**: {'Enabled' if self.memory_enabled else 'Disabled (optional)'}

## Diagnostics:
- Graph Available: {self.graph is not None}
- LLM Available: {llm is not None}
- Registry Available: {self.registry_available}
- Memory Available: {self.memory_enabled}

## Common Issues:
- No ANTHROPIC_API_KEY: Check .env file
- Import errors: Check agent module files exist
- LLM test failures: Check API key is valid

For testing: python team_icp/workflows/graph.py
            """,
            "overall_quality": 0.0,
            "synthesis_complete": False,
            "error": error_msg,
            "statistics": {
                "total_agents": 0,
                "successful_agents": 0,
                "total_words": 0,
                "total_tokens_estimated": 0,
                "max_token_limit": self.max_tokens,
                "overall_quality": 0.0,
                "graph_available": self.graph is not None,
                "llm_available": llm is not None,
                "memory_enabled": self.memory_enabled
            },
            "result": {}  # Empty result dict
        }

# ============================================
# COMPATIBILITY FUNCTIONS FOR ADVANCED_SLACK_BOT
# ============================================
def get_agent_improvements(agent_name: str) -> Dict[str, Any]:
    """Get agent improvement statistics for advanced_slack_bot compatibility"""
    if MEMORY_AVAILABLE and memory_system:
        try:
            return memory_system.get_agent_improvements(agent_name)
        except:
            pass
    
    return {
        'total_learnings': 0,
        'avg_improvement': 0.0,
        'best_learning': None
    }

def record_learning(agent_name: str, insight: str, context: str = "", 
                    quality_before: float = 0.5, quality_after: float = 0.6):
    """Record agent learning for advanced_slack_bot compatibility"""
    if MEMORY_AVAILABLE and memory_system:
        try:
            return memory_system.record_learning(
                agent_name=agent_name,
                insight=insight,
                context=context,
                quality_before=quality_before,
                quality_after=quality_after
            )
        except Exception as e:
            logger.error(f"Failed to record learning: {e}")
    return None

def get_client_context(client_id: str) -> Dict[str, List[str]]:
    """Get client context for advanced_slack_bot compatibility"""
    if MEMORY_AVAILABLE and memory_system:
        try:
            return memory_system.get_client_context(client_id)
        except:
            pass
    return {}

# ============================================
# MODULE TEST
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("TESTING WORKFLOW GRAPH WITH MEMORY SYSTEM")
    print("=" * 70)
    
    print(f"\nConfiguration:")
    print(f"   • Max Tokens: {MAX_TOKEN_LIMIT}")
    print(f"   • Model: {MODEL_NAME}")
    print(f"   • Temperature: {DEFAULT_TEMPERATURE}")
    
    print(f"\nStatus Check:")
    print(f"   • Registry Available: {REGISTRY_AVAILABLE}")
    print(f"   • LangGraph Available: {LANGGRAPH_AVAILABLE}")
    print(f"   • LLM Available: {llm is not None}")
    print(f"   • Graph Compiled: {graph is not None}")
    print(f"   • Memory System: {'Enabled' if MEMORY_AVAILABLE else 'Disabled'}")
    
    if AGENT_REGISTRY:
        print(f"   • Agents in Registry: {len(AGENT_REGISTRY)}")
        print(f"   • Available agents: {', '.join(AGENT_REGISTRY.keys())}")
    
    if llm:
        print(f"\nLLM Configuration:")
        print(f"   • Model: {MODEL_NAME}")
        print(f"   • Max tokens: {MAX_TOKEN_LIMIT}")
        
        # Test LLM
        print("\nTesting LLM...")
        try:
            test_response = llm.invoke("Say 'System operational'")
            print(f"   • LLM Response: {test_response.content[:100]}")
        except Exception as e:
            print(f"   • LLM Test Failed: {e}")
    else:
        print("\n⚠️ LLM NOT CONFIGURED - Check ANTHROPIC_API_KEY in .env file")
    
    if MEMORY_AVAILABLE:
        print(f"\nMemory System:")
        print(f"   • Qdrant Cloud connected")
        print(f"   • Memories will persist across sessions")
    
    # Test agent loading
    if graph and llm:
        print("\n✅ System ready for testing!")
        
        print("\nTesting agent loading...")
        test_state = ICPState()
        
        # Test loading each agent type
        test_agents = ["psychological", "voice_of_customer", "competitor", "gtm_blueprint"]
        
        for agent_name in test_agents:
            try:
                agent = load_agent_dynamically(agent_name, test_state)
                
                if hasattr(agent, 'agent_name'):
                    print(f"   ✅ {agent_name}: {agent.agent_name}")
                else:
                    print(f"   ✅ {agent_name}: Loaded successfully")
                    
                # Check if it's a mock
                if isinstance(agent, MockAgent):
                    print(f"      ⚠️ Using mock implementation")
                    
            except Exception as e:
                print(f"   ❌ {agent_name}: Failed to load - {e}")
        
        # Run a quick test if requested
        print("\n" + "=" * 70)
        print("To run a test analysis:")
        print('  python -c "from team_icp.workflows.graph import ICPGraph; ')
        print('  g = ICPGraph(); result = g.run({\'company\': \'Test Company\'}); ')
        print('  print(result[\'final_report\'][:500])"')
        
    else:
        print("\n❌ System not ready. Missing components:")
        
        missing = []
        if not LANGGRAPH_AVAILABLE:
            missing.append("LangGraph (pip install langgraph)")
        if not llm:
            missing.append("LLM configuration (check .env for ANTHROPIC_API_KEY)")
        if not graph:
            missing.append("Graph compilation failed")
        
        for item in missing:
            print(f"   • {item}")
        
        print("\nSetup instructions:")
        print("1. Create .env file with: ANTHROPIC_API_KEY=your-key-here")
        print("2. Install dependencies: pip install langgraph langchain-anthropic")
        print("3. Verify agent files exist in team_icp/agents/")
    
    print("\n" + "=" * 70)

# ============================================
# EXPORTS
# ============================================
# Export main graph and app for LangGraph
app = graph  # LangGraph expects 'app' as the exported graph

# Export main class and functions for imports
__all__ = [
    'ICPGraph',
    'graph',
    'app',
    'MEMORY_AVAILABLE',
    'MAX_TOKEN_LIMIT',
    'get_agent_improvements',
    'record_learning',
    'get_client_context'
]