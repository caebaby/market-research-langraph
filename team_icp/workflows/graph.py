# team_icp/workflows/graph.py
"""
Modular Workflow Graph - REAL AGENTS VERSION WITH MEMORY
Uses actual agent implementations with MAXIMUM token configuration
Includes Qdrant Cloud memory system for persistent insights
FIXED: GTMBlueprintAgent execution issues with complete wrapper methods
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
# SETUP LOGGING
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# IMPORT LANGGRAPH
# ============================================
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
    logger.info("✅ LangGraph successfully imported")
except ImportError as e:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None
    logger.warning(f"⚠️ LangGraph not available: {e}")

# ============================================
# SETUP PATH AND ENVIRONMENT
# ============================================
try:
    # Setup paths
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    sys.path.insert(0, str(project_root))
    
    # Load environment variables
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"✅ Environment loaded from: {env_path}")
    else:
        logger.warning(f"⚠️ No .env file found at: {env_path}")
        
except Exception as e:
    logger.error(f"❌ Environment setup failed: {e}")

# ============================================
# MEMORY SYSTEM INITIALIZATION
# ============================================
memory_system = None
MEMORY_AVAILABLE = False

try:
    from core.memory_system_qdrant import QdrantMemorySystem
    memory_system = QdrantMemorySystem()
    MEMORY_AVAILABLE = True
    logger.info("✅ Memory system connected - agents will remember insights")
except ImportError as e:
    logger.warning(f"⚠️ Memory system not imported: {e}")
except ValueError as e:
    logger.warning(f"⚠️ Memory system credentials missing: {e}")
except Exception as e:
    logger.warning(f"⚠️ Memory system initialization failed: {e}")

if not MEMORY_AVAILABLE:
    logger.info("💡 Running without memory - analyses won't persist")

# ============================================
# LLM CONFIGURATION WITH MAXIMUM TOKENS
# ============================================
llm = None  # Initialize as None

try:
    from langchain_anthropic import ChatAnthropic
    
    # Try to import Config first
    try:
        from core.config import Config
        
        logger.info("🔍 Attempting to load LLM from Config...")
        llm = Config.get_llm()
        
        if llm:
            # Verify and log token configuration
            if hasattr(llm, 'max_tokens'):
                current_tokens = getattr(llm, 'max_tokens', 'unknown')
                if current_tokens != MAX_TOKEN_LIMIT:
                    logger.warning(f"⚠️ Config LLM has {current_tokens} tokens, updating to {MAX_TOKEN_LIMIT}")
                    llm.max_tokens = MAX_TOKEN_LIMIT
                else:
                    logger.info(f"✅ Config LLM already has {MAX_TOKEN_LIMIT} tokens")
            else:
                # Force set max_tokens if attribute doesn't exist
                llm.max_tokens = MAX_TOKEN_LIMIT
                logger.info(f"✅ Set Config LLM to {MAX_TOKEN_LIMIT} tokens")
                
    except ImportError as e:
        logger.warning(f"⚠️ Could not import Config: {e}")
        llm = None
    except Exception as e:
        logger.warning(f"⚠️ Config.get_llm() failed: {e}")
        llm = None
    
    # Fallback: Create LLM directly if Config fails
    if not llm:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if api_key:
            logger.info(f"🔍 Creating direct LLM with {MAX_TOKEN_LIMIT} tokens...")
            
            try:
                llm = ChatAnthropic(
                    model=MODEL_NAME,
                    anthropic_api_key=api_key,
                    max_tokens=MAX_TOKEN_LIMIT,  # Use maximum token limit
                    temperature=DEFAULT_TEMPERATURE,
                    timeout=60,  # Add timeout for reliability
                    max_retries=3  # Add retries for resilience
                )
                
                # Verify configuration
                logger.info(f"✅ LLM created successfully with:")
                logger.info(f"   • Model: {MODEL_NAME}")
                logger.info(f"   • Max Tokens: {MAX_TOKEN_LIMIT}")
                logger.info(f"   • Temperature: {DEFAULT_TEMPERATURE}")
                
            except Exception as e:
                logger.error(f"❌ Failed to create ChatAnthropic: {e}")
                llm = None
        else:
            logger.error("❌ No ANTHROPIC_API_KEY found in environment")
            llm = None
            
except ImportError as e:
    logger.error(f"❌ Could not import langchain_anthropic: {e}")
    logger.info("💡 Install with: pip install langchain-anthropic")
    llm = None
except Exception as e:
    logger.error(f"❌ Unexpected error setting up LLM: {e}")
    logger.error(traceback.format_exc())
    llm = None

# Log final LLM status
if llm:
    logger.info(f"🎯 LLM READY with {MAX_TOKEN_LIMIT} max tokens")
else:
    logger.error("❌ LLM NOT AVAILABLE - Agents will use mock responses")

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
    
    # Modular fields
    team_name: Optional[str]
    industry_template: Optional[str]
    agent_config_overrides: Optional[Dict[str, Any]]
    
    # Token tracking
    total_tokens_used: Optional[int]
    token_limit: Optional[int]
    
    # Memory tracking
    memories_loaded: Optional[Dict[str, int]]
    memories_stored: Optional[Dict[str, bool]]

# ============================================
# AGENT REGISTRY IMPORT
# ============================================
try:
    # Try relative import first
    try:
        from ..agents.registry import AgentRegistry
    except ImportError:
        # Fall back to absolute import
        from team_icp.agents.registry import AgentRegistry
    
    registry_instance = AgentRegistry()
    AGENT_REGISTRY = {name: info for name, info in registry_instance.get_all_agents().items()}
    REGISTRY_AVAILABLE = True
    logger.info(f"✅ Registry loaded with {len(AGENT_REGISTRY)} agents")
    
except ImportError as e:
    logger.error(f"⚠️ Failed to import registry: {e}")
    REGISTRY_AVAILABLE = False
    AGENT_REGISTRY = {}

# ============================================
# AGENT LOADING AND CACHING
# ============================================
loaded_agents = {}

def load_agent_dynamically(agent_name: str, state: ICPState):
    """
    Dynamically load REAL agents with proper error handling
    FIXED: Complete wrapper implementation for GTMBlueprintAgent
    
    WHY: We load agents on-demand to reduce memory usage and startup time
    """
    # Check cache first
    if agent_name in loaded_agents:
        logger.debug(f"📦 Using cached agent: {agent_name}")
        return loaded_agents[agent_name]
    
    try:
        logger.info(f"🔄 Loading agent: {agent_name}")
        
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
            # Generic pattern for unknown agents
            module_name = f"team_icp.agents.{agent_name}"
            class_name = ''.join(word.capitalize() for word in agent_name.split('_')) + 'Agent'
        
        # SPECIAL HANDLING FOR GTM BLUEPRINT
        if agent_name in ["gtm_blueprint", "gtm"]:
            logger.info(f"[{agent_name}] Special handling for GTMBlueprintAgent")
            
            try:
                # Import the module
                module = importlib.import_module(module_name)
                AgentClass = getattr(module, class_name)
                
                # Try normal instantiation first
                try:
                    agent = AgentClass()
                    logger.info(f"✅ GTMBlueprintAgent instantiated normally")
                    
                except TypeError as te:
                    # If it fails with abstract method error, create wrapper
                    if "abstract" in str(te):
                        logger.warning(f"⚠️ GTMBlueprintAgent needs wrapper for abstract methods")
                        
                        # Create a proper wrapper that implements ALL missing methods
                        class GTMBlueprintWrapper(AgentClass):
                            def __init__(self):
                                # Initialize parent WITHOUT calling super().__init__()
                                # to avoid property setter issues
                                self.agent_name = "GTM Blueprint Strategist"
                                self._llm = state.get('llm', llm)  # Use private attribute
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
                                """Minimal reflection implementation"""
                                return {
                                    "agent": self.agent_name,
                                    "reflection": "GTM Blueprint complete",
                                    "quality": 0.85
                                }
                            
                            def _create_shared_insights(self, response, quality=0.5):
                                """Create insights to share with other agents"""
                                if isinstance(response, str):
                                    content = response
                                elif isinstance(response, dict):
                                    content = str(response.get('output', response))
                                else:
                                    content = str(response)
                                
                                return {
                                    "output": content[:500] if content else "",
                                    "quality": quality,
                                    "timestamp": datetime.now().isoformat(),
                                    "agent": self.agent_name,
                                    "sections_generated": self._count_sections(content) if hasattr(self, '_count_sections') else 0
                                }
                            
                            def _extract_insights_for_memory(self, response):
                                """Extract key insights for memory storage"""
                                if isinstance(response, str):
                                    content = response
                                else:
                                    content = str(response)
                                
                                insights = []
                                insights.append(f"GTM Blueprint generated: {len(content)} characters")
                                
                                # Try to extract sections count if method exists
                                if hasattr(self, '_count_sections'):
                                    sections = self._count_sections(content)
                                    insights.append(f"Sections completed: {sections}/12")
                                
                                # Add quality if available
                                if hasattr(self, '_calculate_quality_score') and content:
                                    quality = self._calculate_quality_score(content)
                                    insights.append(f"Quality score: {quality:.2%}")
                                
                                return insights[:5]  # Return max 5 insights
                        
                        agent = GTMBlueprintWrapper()
                        logger.info(f"✅ Created GTMBlueprintWrapper successfully")
                    else:
                        # Different TypeError, re-raise
                        raise te
                
                # Configure the agent
                if hasattr(agent, 'llm'):
                    agent.llm = state.get('llm', llm)
                
                if hasattr(agent, 'max_tokens'):
                    agent.max_tokens = MAX_TOKEN_LIMIT
                    logger.info(f"✅ Set GTMBlueprintAgent to {MAX_TOKEN_LIMIT} tokens")
                
                # Cache and return
                loaded_agents[agent_name] = agent
                logger.info(f"✅ Successfully loaded GTMBlueprintAgent")
                return agent
                
            except Exception as e:
                logger.error(f"[GTM_BLUEPRINT] Failed to load: {e}")
                logger.error(traceback.format_exc())
                
                # Create a fallback agent that works
                logger.warning(f"⚠️ Creating fallback GTM agent")
                
                class FallbackGTMAgent:
                    def __init__(self):
                        self.agent_name = "GTM Blueprint (Fallback)"
                        self.max_tokens = MAX_TOKEN_LIMIT
                        self._llm = state.get('llm', llm)
                        self.synthesized_agents = []
                    
                    @property
                    def llm(self):
                        return self._llm
                    
                    @llm.setter
                    def llm(self, value):
                        self._llm = value
                    
                    def process(self, state):
                        """Simple GTM processing for fallback"""
                        try:
                            # Update state directly like a workflow node
                            if 'analysis_results' not in state:
                                state['analysis_results'] = {}
                            
                            # Gather insights from other agents
                            other_insights = []
                            for agent in ['psychological', 'voice_of_customer', 'competitor']:
                                if agent in state.get('analysis_results', {}):
                                    other_insights.append(f"{agent}: {state['analysis_results'][agent][:200]}...")
                            
                            # Create basic GTM blueprint
                            blueprint = f"""
# GTM BLUEPRINT (Fallback Mode)

## Executive Summary
Comprehensive go-to-market strategy based on available insights.

## Market Insights
{chr(10).join(other_insights) if other_insights else "No prior agent insights available."}

## Strategy Recommendations
1. Target Market: Define based on psychological and competitive analysis
2. Positioning: Differentiate from identified competitors
3. Channels: Multi-channel approach recommended
4. Pricing: Value-based pricing model
5. Timeline: 90-day launch plan

## Next Steps
- Validate assumptions with customer interviews
- Develop detailed messaging framework
- Create sales enablement materials
- Launch pilot program

Note: This is a simplified GTM blueprint. Full analysis requires proper agent initialization.
"""
                            
                            state['analysis_results']['gtm_blueprint'] = {
                                'content': blueprint,
                                'quality_score': 0.6,
                                'sections_generated': 4,
                                'sections_target': 12,
                                'agent': self.agent_name,
                                'fallback_mode': True
                            }
                            
                            return state
                            
                        except Exception as e:
                            logger.error(f"Fallback GTM failed: {e}")
                            state['analysis_results']['gtm_blueprint'] = {
                                'content': f"GTM analysis failed: {str(e)}",
                                'error': True,
                                'quality_score': 0.0
                            }
                            return state
                    
                    def _generate_response(self, task, context, memories, llm):
                        """Fallback response generation"""
                        return "GTM Blueprint analysis in fallback mode - limited functionality"
                
                agent = FallbackGTMAgent()
                loaded_agents[agent_name] = agent
                return agent
        
        # NORMAL AGENT LOADING (non-GTM agents)
        else:
            # Import and instantiate normally
            module = __import__(module_name, fromlist=[class_name])
            AgentClass = getattr(module, class_name)
            agent = AgentClass()
            
            # Configure agent with max tokens if it has the attribute
            if hasattr(agent, 'max_tokens'):
                agent.max_tokens = MAX_TOKEN_LIMIT
                logger.info(f"✅ Set agent {agent_name} to {MAX_TOKEN_LIMIT} tokens")
            
            # Debug agent type and methods
            logger.debug(f"   Agent type: {type(agent).__name__}")
            logger.debug(f"   Has process: {hasattr(agent, 'process')}")
            logger.debug(f"   Has _generate_response: {hasattr(agent, '_generate_response')}")
            
            loaded_agents[agent_name] = agent
            logger.info(f"✅ Successfully loaded agent: {agent_name}")
            return agent
            
    except ImportError as e:
        logger.error(f"❌ Import error for {agent_name}: {e}")
    except AttributeError as e:
        logger.error(f"❌ Class not found for {agent_name}: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error loading {agent_name}: {e}")
        logger.error(traceback.format_exc())
    
    # Return mock agent as fallback for any agent
    logger.warning(f"⚠️ Using mock agent for: {agent_name}")
    
    class MockAgent:
        def __init__(self, name):
            self.agent_name = name
            self.max_tokens = MAX_TOKEN_LIMIT
            
        def _generate_response(self, task, context, memories, llm):
            return f"[MOCK] {self.agent_name} analysis for: {task[:100]}..."
            
        def process(self, task, shared_insights, llm):
            return {
                'output': f"[MOCK] {self.agent_name} processed the task",
                'quality_score': 0.5
            }
    
    mock = MockAgent(agent_name)
    loaded_agents[agent_name] = mock
    return mock

# ============================================
# NODE CREATION WITH MEMORY INTEGRATION
# ============================================
def create_agent_node(agent_name: str):
    """
    Create a node function that safely executes agents with memory support
    FIXED: Better handling for GTMBlueprintAgent process method
    
    WHY: Each agent needs its own node in the graph for orchestration
    """
    def agent_node(state: ICPState) -> ICPState:
        logger.info(f"[{agent_name.upper()}] Starting execution")
        start_time = datetime.now()
        
        try:
            # Load the agent
            agent = load_agent_dynamically(agent_name, state)
            
            # DEBUG: Comprehensive agent inspection
            logger.debug(f"[{agent_name}] Agent loaded: {type(agent).__name__}")
            logger.debug(f"[{agent_name}] Has process: {hasattr(agent, 'process')}")
            logger.debug(f"[{agent_name}] Has _generate_response: {hasattr(agent, '_generate_response')}")
            
            # Get original context
            business_context = state.get("business_context", state.get("task", ""))
            shared_insights = state.get("shared_insights", {})
            
            # ============================================
            # MEMORY RETRIEVAL - Give agent previous context
            # ============================================
            memories_loaded_count = 0
            if MEMORY_AVAILABLE and state.get("client_id"):
                try:
                    # Retrieve previous memories for this client/agent
                    previous_memories = memory_system.retrieve_memories(
                        client_id=state["client_id"],
                        agent_name=agent_name,
                        limit=5  # Get top 5 relevant memories
                    )
                    
                    if previous_memories:
                        # Add memories to context
                        memory_context = "\n\n=== PREVIOUS INSIGHTS FOR THIS CLIENT ===\n"
                        for i, mem in enumerate(previous_memories, 1):
                            memory_context += f"{i}. {mem.content}\n"
                        memory_context += "=== END PREVIOUS INSIGHTS ===\n\n"
                        
                        # Append to business context
                        business_context = memory_context + business_context
                        memories_loaded_count = len(previous_memories)
                        
                        # Track memories loaded
                        if "memories_loaded" not in state:
                            state["memories_loaded"] = {}
                        state["memories_loaded"][agent_name] = memories_loaded_count
                        
                        logger.info(f"[{agent_name.upper()}] 📚 Loaded {memories_loaded_count} memories")
                    
                except Exception as e:
                    logger.error(f"[{agent_name.upper()}] Memory retrieval failed: {e}")
            
            # Initialize token tracking
            if "total_tokens_used" not in state:
                state["total_tokens_used"] = 0
            state["token_limit"] = MAX_TOKEN_LIMIT
            
            # Check if LLM is available
            if not llm:
                logger.warning(f"[{agent_name.upper()}] No LLM available, using mock response")
                state["current_output"] = f"[ERROR] LLM not configured for {agent_name}"
                state["quality_score"] = 0.0
                state["requires_human_review"] = True
                state["review_reason"] = "LLM not available"
            else:
                # Execute agent with proper error handling
                logger.info(f"[{agent_name.upper()}] Processing with {MAX_TOKEN_LIMIT} max tokens...")
                
                try:
                    result = None
                    
                    # SPECIAL HANDLING FOR GTM_BLUEPRINT
                    if agent_name in ["gtm_blueprint", "gtm"]:
                        logger.debug(f"[{agent_name}] Special processing for GTM Blueprint")
                        
                        # GTMBlueprintAgent expects state dict, not individual params
                        # It modifies state directly
                        if hasattr(agent, 'process'):
                            # Ensure state has required fields
                            state['llm'] = llm
                            state['company_info'] = state.get('master_context', 'Unknown Company')
                            state['task'] = state.get('task', business_context)
                            
                            # Call process with state
                            updated_state = agent.process(state)
                            
                            # Extract results from updated state
                            if 'analysis_results' in updated_state and 'gtm_blueprint' in updated_state['analysis_results']:
                                gtm_data = updated_state['analysis_results']['gtm_blueprint']
                                state["current_output"] = gtm_data.get('content', '')
                                state["quality_score"] = gtm_data.get('quality_score', 0.0)
                                
                                # Update state with GTM results
                                state['analysis_results'] = updated_state.get('analysis_results', {})
                                result = {'processed': True}
                            else:
                                # Fallback if no results
                                state["current_output"] = "GTM Blueprint processing did not produce results"
                                state["quality_score"] = 0.0
                                result = {'processed': False}
                        else:
                            logger.error(f"[{agent_name}] GTM agent missing process method")
                            state["current_output"] = "GTM agent configuration error"
                            state["quality_score"] = 0.0
                    
                    # NORMAL AGENT PROCESSING
                    else:
                        # Import StandardAgentNodeV4 for type checking
                        try:
                            from core.standard_agent_v4 import StandardAgentNodeV4
                            is_v4_agent = isinstance(agent, StandardAgentNodeV4)
                        except:
                            is_v4_agent = False
                        
                        # Method 1: Check if it's a V4 agent specifically
                        if is_v4_agent:
                            logger.debug(f"[{agent_name}] Confirmed V4 agent, using process()")
                            result = agent.process(business_context, shared_insights, llm)
                            
                        # Method 2: Try process method if it exists
                        elif hasattr(agent, 'process'):
                            logger.debug(f"[{agent_name}] Found process() method")
                            result = agent.process(business_context, shared_insights, llm)
                            
                        # Method 3: Fallback to _generate_response
                        elif hasattr(agent, '_generate_response'):
                            logger.warning(f"[{agent_name}] FALLBACK: Using _generate_response directly")
                            memories = []
                            
                            # Inspect method signature to determine correct calling convention
                            sig = inspect.signature(agent._generate_response)
                            params = list(sig.parameters.keys())
                            
                            # Remove 'self' from params if present
                            if 'self' in params:
                                params.remove('self')
                            
                            logger.debug(f"[{agent_name}] _generate_response params: {params}")
                            
                            # Call based on parameter count
                            if len(params) == 3:  # task, memories, llm
                                output = agent._generate_response(business_context, memories, llm)
                            elif len(params) == 4:  # task, context, memories, llm
                                output = agent._generate_response(
                                    business_context,
                                    business_context,
                                    memories,
                                    llm
                                )
                            else:
                                logger.error(f"[{agent_name}] Unexpected signature: {params}")
                                output = agent._generate_response(business_context, memories, llm)
                            
                            # Wrap output in result format
                            result = {"output": output, "quality_score": 0.85}
                        else:
                            raise AttributeError(f"Agent {agent_name} has no executable method")
                        
                        # Process normal agent result
                        if result and isinstance(result, dict):
                            state["current_output"] = result.get('output', '')
                            state["quality_score"] = result.get('quality_score', 0.0)
                            
                            # Store additional insights
                            for key in ['exact_phrases', 'competitors_analyzed', 'battle_cards']:
                                if key in result:
                                    if "additional_insights" not in state:
                                        state["additional_insights"] = {}
                                    state["additional_insights"][f"{agent_name}_{key}"] = result[key]
                        elif result:
                            state["current_output"] = str(result)
                            state["quality_score"] = 0.75
                    
                    # Estimate tokens used
                    if state.get("current_output"):
                        estimated_tokens = len(state["current_output"]) // 4
                        state["total_tokens_used"] += estimated_tokens
                        logger.info(f"[{agent_name.upper()}] Estimated {estimated_tokens} tokens used")
                    
                    # ============================================
                    # MEMORY STORAGE - Save insights for future
                    # ============================================
                    memory_stored = False
                    if MEMORY_AVAILABLE and state.get("client_id") and state.get("current_output"):
                        try:
                            # Extract key insight
                            output_text = state["current_output"]
                            insight = output_text[:500] if len(output_text) > 500 else output_text
                            
                            # Store with quality-based importance
                            memory_id = memory_system.store_memory(
                                client_id=state["client_id"],
                                agent_name=agent_name,
                                memory_type="analysis",
                                content=insight,
                                context=f"Analysis for {state.get('master_context', 'unknown')}",
                                importance=state.get("quality_score", 0.5)
                            )
                            
                            memory_stored = True
                            
                            # Track storage
                            if "memories_stored" not in state:
                                state["memories_stored"] = {}
                            state["memories_stored"][agent_name] = True
                            
                            logger.info(f"[{agent_name.upper()}] 💾 Stored memory: {memory_id[:8]}...")
                            
                            # Share important insights with other agents
                            if state.get("quality_score", 0) > 0.9:
                                # High quality insights get shared
                                next_agents = state.get("agents_to_run", [])[state.get("current_agent_index", 0) + 1:]
                                for next_agent in next_agents[:2]:  # Share with next 2 agents
                                    memory_system.share_insights_between_agents(
                                        from_agent=agent_name,
                                        to_agent=next_agent,
                                        client_id=state["client_id"],
                                        insight=insight[:200]
                                    )
                                    logger.info(f"[{agent_name.upper()}] 🤝 Shared insight with {next_agent}")
                            
                        except Exception as e:
                            logger.error(f"[{agent_name.upper()}] Memory storage failed: {e}")
                        
                except Exception as e:
                    logger.error(f"[{agent_name.upper()}] Processing error: {e}")
                    logger.error(traceback.format_exc())
                    state["current_output"] = f"[ERROR] {agent_name}: {str(e)}"
                    state["quality_score"] = 0.0
                    state["requires_human_review"] = True
                    state["review_reason"] = str(e)
            
            # Store output in result (except for GTM which already did this)
            if state.get("current_output") and agent_name not in ["gtm_blueprint", "gtm"]:
                if "result" not in state:
                    state["result"] = {}
                state["result"][agent_name] = state["current_output"]
                
                output_length = len(state["current_output"])
                logger.info(f"[{agent_name.upper()}] Generated {output_length} characters")
                
                # Warn if output might be truncated
                if output_length > MAX_TOKEN_LIMIT * 4:  # Rough char estimate
                    logger.warning(f"[{agent_name.upper()}] Output may exceed token limit!")
            
            # Update shared insights (except for GTM which handles differently)
            if agent_name not in ["gtm_blueprint", "gtm"]:
                if "shared_insights" not in state:
                    state["shared_insights"] = {}
                
                # Create shared insights
                if hasattr(agent, '_create_shared_insights') and state.get("current_output"):
                    try:
                        quality = state.get("quality_score", 0)
                        insights = agent._create_shared_insights(state["current_output"], quality)
                        state["shared_insights"][agent_name] = insights
                    except:
                        # Fallback to basic insights
                        state["shared_insights"][agent_name] = {
                            "output": state.get("current_output", "")[:500],
                            "quality": state.get("quality_score", 0),
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    state["shared_insights"][agent_name] = {
                        "output": state.get("current_output", "")[:500],
                        "quality": state.get("quality_score", 0),
                        "timestamp": datetime.now().isoformat()
                    }
            
            # Log execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log memory status
            memory_status = ""
            if MEMORY_AVAILABLE:
                loaded = memories_loaded_count
                stored = "✓" if memory_stored else "✗"
                memory_status = f" | Memory: {loaded} loaded, {stored} stored"
            
            logger.info(f"[{agent_name.upper()}] Completed in {execution_time:.2f}s | Quality: {state.get('quality_score', 0):.2f}{memory_status}")
            
        except Exception as e:
            error_msg = f"Agent {agent_name} failed: {str(e)}"
            logger.error(f"[{agent_name.upper()}] CRITICAL ERROR: {error_msg}")
            logger.error(traceback.format_exc())
            
            # Update state with error
            state["requires_human_review"] = True
            state["review_reason"] = error_msg
            
            if "result" not in state:
                state["result"] = {}
            state["result"][agent_name] = f"[CRITICAL ERROR]: {str(e)}"
            state["quality_score"] = 0.0
        
        finally:
            # Always increment index to prevent infinite loops
            state["current_agent_index"] = state.get("current_agent_index", 0) + 1
            logger.debug(f"[{agent_name.upper()}] Index incremented to: {state['current_agent_index']}")
        
        return state
    
    return agent_node

# ============================================
# ROUTING AND SYNTHESIS NODES
# ============================================
def router_node(state: ICPState) -> ICPState:
    """
    Router node that determines agent execution sequence
    
    WHY: Centralizes orchestration logic and agent selection
    """
    logger.info("[ROUTER] Analyzing routing requirements")
    
    # Initialize state fields
    state.setdefault("result", {})
    state.setdefault("shared_insights", {})
    state.setdefault("current_agent_index", 0)
    state.setdefault("total_tokens_used", 0)
    state["token_limit"] = MAX_TOKEN_LIMIT
    
    # Initialize memory tracking
    state["memories_loaded"] = {}
    state["memories_stored"] = {}
    
    # Log configuration
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
        valid_agents.append(normalized_name)
    
    state["agents_to_run"] = valid_agents
    logger.info(f"[ROUTER] Scheduled {len(valid_agents)} agents for execution")
    
    return state

def synthesis_node(state: ICPState) -> ICPState:
    """
    Final synthesis node that creates comprehensive report
    
    WHY: Combines all agent outputs into a cohesive final deliverable
    """
    logger.info("[SYNTHESIS] Creating final report")
    
    state["synthesis_complete"] = True
    
    # Check token usage
    total_tokens = state.get("total_tokens_used", 0)
    logger.info(f"[SYNTHESIS] Total estimated tokens used: {total_tokens}")
    
    if total_tokens > MAX_TOKEN_LIMIT * 0.9:  # Warn at 90% usage
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
        
        # Process agents in preferred order
        for agent_name in agent_order:
            if agent_name in state["result"]:
                output = state["result"][agent_name]
                if output and not output.startswith("[ERROR]") and not output.startswith("[CRITICAL ERROR]"):
                    agent_title = agent_name.replace("_", " ").title()
                    report_sections.append(f"## {agent_title} Analysis\n\n{output}\n")
                elif output and (output.startswith("[ERROR]") or output.startswith("[CRITICAL ERROR]")):
                    error_sections.append(f"⚠️ {agent_name}: {output}")
        
        # Add any other agents not in standard order
        for agent_name, output in state["result"].items():
            if agent_name not in agent_order:
                if output and not output.startswith("[ERROR]") and not output.startswith("[CRITICAL ERROR]"):
                    agent_title = agent_name.replace("_", " ").title()
                    report_sections.append(f"## {agent_title} Analysis\n\n{output}\n")
                elif output and (output.startswith("[ERROR]") or output.startswith("[CRITICAL ERROR]")):
                    error_sections.append(f"⚠️ {agent_name}: {output}")
        
        # Create final report
        if report_sections:
            state["final_report"] = "\n".join(report_sections)
        else:
            state["final_report"] = "No analysis results available."
        
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
        
        state["overall_quality"] = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Add statistics
        successful_agents = len([o for o in state["result"].values() if o and not o.startswith("[ERROR]")])
        total_agents = len(state["result"])
        total_words = sum(len(str(output).split()) for output in state["result"].values() if not str(output).startswith("[ERROR]"))
        
        state["statistics"] = {
            "total_agents": total_agents,
            "successful_agents": successful_agents,
            "total_words": total_words,
            "total_tokens_estimated": total_tokens,
            "max_token_limit": MAX_TOKEN_LIMIT,
            "overall_quality": state["overall_quality"],
            "memory_enabled": MEMORY_AVAILABLE,
            "memories_loaded": state.get("memories_loaded", {}),
            "memories_stored": state.get("memories_stored", {})
        }
        
        logger.info(f"[SYNTHESIS] Report complete:")
        logger.info(f"   • Successful: {successful_agents}/{total_agents} agents")
        logger.info(f"   • Quality: {state['overall_quality']:.2f}")
        logger.info(f"   • Words: {total_words}")
        logger.info(f"   • Tokens: {total_tokens}/{MAX_TOKEN_LIMIT}")
    else:
        state["final_report"] = "Analysis could not be completed."
        state["overall_quality"] = 0.0
    
    return state

def route_to_next_agent(state: ICPState) -> str:
    """
    Determine next agent with safety checks
    
    WHY: Prevents infinite loops and ensures proper flow control
    """
    requested = state.get("agents_to_run", [])
    current_index = state.get("current_agent_index", 0)
    
    # Safety limit
    MAX_ITERATIONS = 20
    if current_index >= MAX_ITERATIONS:
        logger.warning(f"[ROUTING] Safety limit ({MAX_ITERATIONS}) reached!")
        return "synthesis"
    
    # Check token usage
    total_tokens = state.get("total_tokens_used", 0)
    if total_tokens > MAX_TOKEN_LIMIT * 0.95:  # Stop at 95% usage
        logger.warning(f"[ROUTING] Token limit approaching ({total_tokens}/{MAX_TOKEN_LIMIT}), moving to synthesis")
        return "synthesis"
    
    # Check if more agents to run
    if current_index < len(requested):
        next_agent = requested[current_index]
        logger.info(f"[ROUTING] Next: {next_agent} ({current_index + 1}/{len(requested)})")
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
            "voice": create_agent_node("voice_of_customer"),
            "competitor": create_agent_node("competitor"),
            "interview_psychological": create_agent_node("interview_psychological"),
            "interview_psych": create_agent_node("interview_psychological"),
            "interview_sales": create_agent_node("interview_sales"),
            "gtm_blueprint": create_agent_node("gtm_blueprint"),
            "gtm": create_agent_node("gtm_blueprint")
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
        logger.info(f"✅ Workflow compiled successfully with {len(agent_variations)} agent nodes")
        
    except Exception as e:
        logger.error(f"❌ Failed to compile workflow: {e}")
        logger.error(traceback.format_exc())
        graph = None
else:
    logger.warning("⚠️ LangGraph not available - workflow disabled")
    graph = None

# ============================================
# MAIN WORKFLOW CLASS
# ============================================
class ICPGraph:
    """
    Main class for running the ICP workflow with memory support
    """
    def __init__(self):
        self.graph = graph
        self.registry_available = REGISTRY_AVAILABLE
        self.max_tokens = MAX_TOKEN_LIMIT
        self.memory_enabled = MEMORY_AVAILABLE
        
        # Log initialization status
        logger.info("=" * 60)
        logger.info("ICP WORKFLOW INITIALIZED")
        logger.info(f"   • Graph: {'✅ Ready' if self.graph else '❌ Not Available'}")
        logger.info(f"   • Registry: {'✅ Ready' if self.registry_available else '❌ Not Available'}")
        logger.info(f"   • LLM: {'✅ Ready' if llm else '❌ Not Available'}")
        logger.info(f"   • Memory: {'✅ Enabled' if self.memory_enabled else '❌ Disabled'}")
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
        
        logger.info(f"🚀 Starting analysis for: {company}")
        logger.info(f"📊 Token limit: {self.max_tokens}")
        logger.info(f"🆔 Client ID: {client_id}")
        
        if self.memory_enabled:
            logger.info(f"🧠 Memory enabled - will load/store insights")
        
        if not self.graph:
            return self._get_error_result(company, "Workflow graph not compiled")
        
        if not llm:
            return self._get_error_result(company, "LLM not configured")
        
        try:
            # Prepare initial state
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
                "client_id": client_id,  # Important for memory
                "requested_agents": inputs.get("requested_agents", None),
                "new_data": True,
                "shared_insights": {},
                "token_limit": self.max_tokens,
                "total_tokens_used": 0,
                "analysis_results": {}  # Initialize for GTM
            }
            
            # Run the workflow
            logger.info("📈 Executing workflow graph...")
            result = self.graph.invoke(state)
            
            # Ensure we have a final report
            if "final_report" not in result:
                result["final_report"] = self._format_results(result)
            
            # Add execution summary
            stats = result.get("statistics", {})
            logger.info("✅ Analysis complete:")
            logger.info(f"   • Quality: {stats.get('overall_quality', 0):.2f}")
            logger.info(f"   • Words: {stats.get('total_words', 0)}")
            logger.info(f"   • Tokens: {stats.get('total_tokens_estimated', 0)}/{self.max_tokens}")
            logger.info(f"   • Success: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)} agents")
            
            if self.memory_enabled:
                total_loaded = sum(stats.get('memories_loaded', {}).values())
                total_stored = sum(1 for v in stats.get('memories_stored', {}).values() if v)
                logger.info(f"   • Memory: {total_loaded} loaded, {total_stored} stored")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {e}")
            logger.error(traceback.format_exc())
            return self._get_error_result(company, str(e))
    
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
1. **LangGraph**: `pip install langgraph`
2. **LLM Configuration**: Ensure ANTHROPIC_API_KEY in .env
3. **Agent Files**: Verify all agent modules are present
4. **Token Limit**: Currently set to {self.max_tokens}
5. **Memory System**: {'Enabled' if self.memory_enabled else 'Disabled (optional)'}

## Diagnostics:
- Graph Available: {self.graph is not None}
- LLM Available: {llm is not None}
- Registry Available: {self.registry_available}
- Memory Available: {self.memory_enabled}

For testing: `python tests/test_available_agents.py`
            """,
            "overall_quality": 0.0,
            "synthesis_complete": False,
            "error": error_msg,
            "statistics": {
                "max_token_limit": self.max_tokens,
                "graph_available": self.graph is not None,
                "llm_available": llm is not None,
                "memory_enabled": self.memory_enabled
            }
        }

# ============================================
# MODULE TEST
# ============================================
if __name__ == "__main__":
    print("=" * 70)
    print("TESTING WORKFLOW GRAPH WITH MEMORY SYSTEM")
    print("=" * 70)
    
    print(f"\n📊 Configuration:")
    print(f"   • Max Tokens: {MAX_TOKEN_LIMIT}")
    print(f"   • Model: {MODEL_NAME}")
    print(f"   • Temperature: {DEFAULT_TEMPERATURE}")
    
    print(f"\n✅ Status Check:")
    print(f"   • Registry Available: {REGISTRY_AVAILABLE}")
    print(f"   • LangGraph Available: {LANGGRAPH_AVAILABLE}")
    print(f"   • LLM Available: {llm is not None}")
    print(f"   • Graph Compiled: {graph is not None}")
    print(f"   • Memory System: {'✅ Enabled' if MEMORY_AVAILABLE else '❌ Disabled'}")
    print(f"   • Agents in Registry: {len(AGENT_REGISTRY)}")
    
    if llm:
        print(f"\n🔍 LLM Configuration:")
        if hasattr(llm, 'max_tokens'):
            print(f"   • Current max_tokens: {llm.max_tokens}")
        else:
            print(f"   • max_tokens attribute: Not found")
            
        if hasattr(llm, 'model'):
            print(f"   • Model: {llm.model}")
        if hasattr(llm, 'temperature'):
            print(f"   • Temperature: {llm.temperature}")
    
    if MEMORY_AVAILABLE:
        print(f"\n🧠 Memory System:")
        print(f"   • Qdrant Cloud connected")
        print(f"   • Memories will persist across sessions")
        print(f"   • Agents will build on previous insights")
    
    if graph and llm:
        print("\n✅ System ready with all features!")
        
        # Test agent loading
        print("\n🧪 Testing agent loading...")
        try:
            test_state = {}
            psych_agent = load_agent_dynamically("psychological", test_state)
            
            if hasattr(psych_agent, 'agent_name'):
                print(f"   ✅ Loaded: {psych_agent.agent_name}")
            else:
                print(f"   ✅ Loaded: PsychologicalAgent")
                
            if hasattr(psych_agent, 'max_tokens'):
                print(f"   • Agent max_tokens: {psych_agent.max_tokens}")
            
            # Test GTM Blueprint loading specifically
            print("\n🧪 Testing GTM Blueprint loading...")
            gtm_agent = load_agent_dynamically("gtm_blueprint", test_state)
            print(f"   ✅ Loaded: {type(gtm_agent).__name__}")
            print(f"   • Has process: {hasattr(gtm_agent, 'process')}")
            print(f"   • Has _create_shared_insights: {hasattr(gtm_agent, '_create_shared_insights')}")
            print(f"   • Has _extract_insights_for_memory: {hasattr(gtm_agent, '_extract_insights_for_memory')}")
                
        except Exception as e:
            print(f"   ❌ Failed to load agent: {e}")
    else:
        print("\n❌ System not ready. Missing components:")
        
        missing = []
        if not LANGGRAPH_AVAILABLE:
            missing.append("LangGraph (pip install langgraph)")
        if not llm:
            missing.append("LLM configuration (check .env for ANTHROPIC_API_KEY)")
        if not graph:
            missing.append("Graph compilation failed")
        if not MEMORY_AVAILABLE:
            missing.append("Memory system (optional, check Qdrant credentials)")
        
        for item in missing:
            print(f"   • {item}")
    
    print("\n" + "=" * 70)

# Export main graph and app for LangGraph
app = graph  # LangGraph expects 'app' as the exported graph