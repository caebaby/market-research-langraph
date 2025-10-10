#!/usr/bin/env python
"""
Market Research Workflow Graph
Orchestrates all 6 agents with dynamic configuration from bot
Version 3.0 - Production Ready
"""

import os
# Map our env var to what BraveSearch expects
if os.getenv('BRAVE_API_KEY'):
    os.environ['BRAVE_SEARCH_API_KEY'] = os.getenv('BRAVE_API_KEY')
import sys
import re  # For regex patterns in helper methods
from difflib import SequenceMatcher  # For similarity checking
from pathlib import Path
import logging
import time
from typing import Dict, Any, List, Optional, Callable, TypedDict
from datetime import datetime
import json
import asyncio
from dataclasses import dataclass, field

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# ==============================================
# 1. LOGGING CONFIGURATION
# ==============================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# ==============================================
# 2. IMPORTS FROM LANGGRAPH
# ==============================================

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available - install langgraph package")

# ==============================================
# 3. STATE DEFINITION
# ==============================================

class GraphState(TypedDict):
    """
    State that flows through the workflow graph.
    Designed to work with bot's configuration.
    """
    # Core inputs from bot
    company: str
    business_context: Optional[str]
    template_data: Optional[Dict[str, Any]]
    client_id: str
    request_id: Optional[str]
    
    # Agent configuration from bot
    requested_agents: List[str]
    agent_config: Optional[Dict[str, Any]]  # Contains temps, tokens, get_llm_func
    
    # Search configuration
    search_enabled: bool
    web_sources: Optional[List[Dict]]
    
    # Memory configuration  
    memory_enabled: bool
    memories_loaded: Dict[str, int]
    memories_stored: Dict[str, bool]
    
    # Agent outputs
    agent_outputs: Dict[str, str]
    agent_errors: Dict[str, str]
    agent_metrics: Dict[str, Dict[str, Any]]
    
    # Workflow tracking
    current_agent: Optional[str]
    completed_agents: List[str]
    failed_agents: List[str]
    
    # Progress tracking for Slack
    slack_updater: Optional[Callable]
    progress_messages: List[str]
    
    # Final outputs
    final_report: Optional[str]
    gtm_blueprint: Optional[str]
    statistics: Dict[str, Any]
    quality_scores: Dict[str, float]
    
    # Timing
    start_time: float
    end_time: Optional[float]
    agent_timings: Dict[str, float]
    
    # Additional context
    insights: Dict[str, Dict[str, Any]]  # Cross-agent insights
    analysis_depth: str  # "quick", "standard", "comprehensive"
    source: Optional[str]  # Where request came from

# ==============================================
# 4. WORKFLOW CONFIGURATION
# ==============================================

@dataclass
class WorkflowConfig:
    """Configuration for ICP workflow with MANDATORY systems"""
    
    def __init__(self, **kwargs):
        # Basic settings
        self.verbose = kwargs.get('verbose', False)
        self.timeout_per_agent = kwargs.get('timeout_per_agent', 120)
        self.max_retries = kwargs.get('max_retries', 3)
        
        # MEMORY IS MANDATORY - Cannot be disabled
        self.memory_enabled = True  # Always True, ignore any attempts to disable
        if kwargs.get('memory_enabled') == False:
            logger.warning("⚠️ Memory system is MANDATORY - forcing enabled")
            logger.warning("   Qdrant memory is required for agent persistence")
        
        # SEARCH IS MANDATORY - Cannot be disabled  
        self.search_enabled = True  # Always True, ignore any attempts to disable
        if kwargs.get('search_enabled') == False:
            logger.warning("⚠️ Search system is MANDATORY - forcing enabled")
            logger.warning("   Brave search is required for comprehensive analysis")
        
        # Performance settings
        self.parallel_execution = kwargs.get('parallel_execution', True)
        self.min_word_count = kwargs.get('min_word_count', 1000)
        self.quality_threshold = kwargs.get('quality_threshold', 0.7)
        
        # Agent configurations
        self.temperatures = kwargs.get('temperatures', {
            "psychological": 0.7,
            "voice_of_customer": 0.5,
            "competitor": 0.3,
            "interview_psychological": 0.7,
            "interview_sales": 0.6,
            "gtm_blueprint": 0.4
        })
        
        self.max_tokens = kwargs.get('max_tokens', {
            'research': 8100,
            'creative': 8100,
            'summary': 4000
        })
        
        # Log mandatory configuration
        if self.verbose:
            logger.info("WorkflowConfig initialized with MANDATORY systems:")
            logger.info(f"  Memory: ENABLED (mandatory)")
            logger.info(f"  Search: ENABLED (mandatory)")

# ==============================================
# 5. BASE WORKFLOW CLASS
# ==============================================

class ICPGraph:
    """
    Main workflow orchestrator for market research.
    Integrates with bot's dynamic configuration.
    """
    
    def __init__(self, config: Optional[WorkflowConfig] = None, verbose: bool = False):
        """
        Initialize the ICP workflow with MANDATORY memory and search systems.
        Args:
            config: Optional workflow configuration
            verbose: Enable verbose logging
        """
        # Use provided config or create default with mandatory systems
        self.config = config or WorkflowConfig()
        
        # Override verbose if specified
        if verbose:
            self.config.verbose = True
        self.verbose = self.config.verbose
        
        # Force mandatory systems in config
        self.config.memory_enabled = True
        self.config.search_enabled = True
        
        logger.info("=" * 80)
        logger.info("INITIALIZING ICPGraph WITH MANDATORY SYSTEMS")
        logger.info("=" * 80)
        
        # ==============================================
        # MANDATORY SYSTEM 1: Memory (Qdrant)
        # ==============================================
        
        print("🔒 Initializing MANDATORY memory system...")
        self.memory_system = None
        
        try:
            # Check credentials first
            if not os.getenv('QDRANT_URL') or not os.getenv('QDRANT_API_KEY'):
                raise ValueError(
                    "QDRANT_URL and QDRANT_API_KEY are REQUIRED. "
                    "Get credentials from https://cloud.qdrant.io"
                )
            
            from core.memory_system_qdrant import QdrantMemorySystem
            
            self.memory_system = QdrantMemorySystem()
            
            # Test the connection
            test_id = f"init_test_{time.time()}"
            self.memory_system.store_memory(
                client_id=test_id,
                agent_name="system",
                memory_type="test",
                content="Initialization test",
                importance=0.1
            )
            
            logger.info("✅ Memory system connected and verified (MANDATORY)")
            print("✅ Memory system connected (MANDATORY)")
            
        except ImportError as e:
            error_msg = f"Memory system module not found: {e}. Run: pip install qdrant-client"
            logger.error(f"❌ FATAL: {error_msg}")
            raise RuntimeError(f"Cannot proceed without memory system: {error_msg}")
            
        except Exception as e:
            error_msg = f"Memory system initialization failed: {e}"
            logger.error(f"❌ FATAL: {error_msg}")
            raise RuntimeError(f"Cannot proceed without memory system: {error_msg}")
        
        # ==============================================
        # MANDATORY SYSTEM 2: Search (Brave)
        # ==============================================
        
        print("🔒 Initializing MANDATORY search system...")
        self.search_system = None
        
        try:
            # Check API key first
            if not os.getenv('BRAVE_API_KEY'):
                raise ValueError(
                    "BRAVE_API_KEY is REQUIRED. "
                    "Get API key from https://brave.com/search/api/"
                )
            
            from langchain_community.tools.brave_search.tool import BraveSearch as BraveSearchResults
            
            self.search_system = BraveSearchResults(
                api_key=os.getenv('BRAVE_API_KEY'),
                search_kwargs={"count": 5}
            )
            
            # Test the search
            test_result = self.search_system.run("test")
            if not test_result:
                raise ValueError("Search test failed - no results returned")
            
            logger.info("✅ Search system connected and verified (MANDATORY)")
            print("✅ Search system connected (MANDATORY)")
            
        except ImportError as e:
            error_msg = f"Search module not found: {e}. Run: pip install langchain-community"
            logger.error(f"❌ FATAL: {error_msg}")
            raise RuntimeError(f"Cannot proceed without search system: {error_msg}")
            
        except Exception as e:
            error_msg = f"Search system initialization failed: {e}"
            logger.error(f"❌ FATAL: {error_msg}")
            raise RuntimeError(f"Cannot proceed without search system: {error_msg}")
        
        # ==============================================
        # Initialize Agents (existing code)
        # ==============================================
        
        self.agents = {}
        self._initialize_agents()
        
        # ==============================================
        # Build Workflow Graph (existing code)
        # ==============================================
        
        self.graph = None
        self.compiled_graph = None
        
        if LANGGRAPH_AVAILABLE:
            self._build_graph()
        else:
            logger.warning("LangGraph not available - will use mock execution")
        
        logger.info("=" * 80)
        logger.info(f"ICPGraph initialized successfully")
        logger.info(f"  Memory: ✅ MANDATORY (Connected)")
        logger.info(f"  Search: ✅ MANDATORY (Connected)")
        logger.info(f"  Agents: {len(self.agents)} initialized")
        logger.info(f"  Graph: {'Compiled' if self.compiled_graph else 'Mock mode'}")
        logger.info("=" * 80)
    
    def _initialize_memory_system(self):
        """Initialize memory system if available"""
        if not self.config.memory_enabled:
            logger.info("Memory system disabled in config")
            return
        
        try:
            from core.memory_system_qdrant import QdrantMemorySystem
            self.memory_system = QdrantMemorySystem()
            logger.info("✅ Memory system initialized")
        except ImportError:
            logger.warning("Memory system not available - QdrantMemorySystem not found")
        except Exception as e:
            logger.warning(f"Memory system initialization failed: {e}")
    
    def _initialize_search_system(self):
        """Initialize search system if available"""
        if not self.config.search_enabled:
            logger.info("Search system disabled in config")
            return
        
        try:
            from langchain_community.tools import BraveSearchResults
            api_key = os.getenv("BRAVE_API_KEY")
            
            if api_key:
                self.search_system = BraveSearchResults(
                    api_key=api_key,
                    search_kwargs={"count": 5}
                )
                logger.info("✅ Search system initialized")
            else:
                logger.warning("Brave API key not found")
        except ImportError:
            logger.warning("Search system not available - langchain-community not installed")
        except Exception as e:
            logger.warning(f"Search system initialization failed: {e}")
    
    def _initialize_agents(self):
        """Initialize agent instances - placeholder for Turn 2"""
        logger.info("Initializing agents...")
        # Will be implemented in Turn 2
        pass
    
    def _build_graph(self):
        """Build the workflow graph - placeholder for Turn 3"""
        if not LANGGRAPH_AVAILABLE:
            logger.error("LangGraph not available - cannot build workflow")
            return
        
        logger.info("Building workflow graph...")
        # Will be implemented in Turn 3
        pass
    
    def _get_llm_for_agent(self, agent_name: str, state: GraphState):
        """
        Get LLM instance for specific agent using bot's configuration.
        
        Args:
            agent_name: Name of the agent
            state: Current graph state containing config
            
        Returns:
            LLM instance configured for the agent
        """
        # Check if bot provided a get_llm_func
        if state.get("agent_config") and "get_llm_func" in state["agent_config"]:
            get_llm_func = state["agent_config"]["get_llm_func"]
            if callable(get_llm_func):
                return get_llm_func(agent_name)
        
        # Fallback to creating our own
        return self._create_default_llm(agent_name)
    
    def _create_default_llm(self, agent_name: str):
        """Create default LLM if bot didn't provide function"""
        try:
            from langchain_anthropic import ChatAnthropic
            
            # Get temperature for agent
            temperature = self.config.temperatures.get(
                agent_name, 
                self.config.default_temperature
            )
            
            # Get max tokens based on agent type
            if agent_name in ["psychological", "interview_psychological", "interview_sales"]:
                max_tokens = self.config.max_tokens.get("creative", 8100)
            elif agent_name in ["gtm_blueprint", "gtm"]:
                max_tokens = self.config.max_tokens.get("summary", 4000)
            else:
                max_tokens = self.config.max_tokens.get("research", 8100)
            
            if self.verbose:
                logger.info(f"Creating LLM for {agent_name}: temp={temperature}, tokens={max_tokens}")
            
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=60
            )
        except Exception as e:
            logger.error(f"Failed to create LLM for {agent_name}: {e}")
            return None
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the workflow with MANDATORY systems verification.
        
        Args:
            inputs: Input configuration dictionary
            
        Returns:
            Analysis results dictionary
            
        Raises:
            RuntimeError: If mandatory systems are not available
        """
        # ==============================================
        # MANDATORY SYSTEMS CHECK
        # ==============================================
        
        if not self.memory_system:
            raise RuntimeError(
                "❌ Memory system is MANDATORY but not initialized. "
                "Check QDRANT_URL and QDRANT_API_KEY in .env"
            )
        
        if not self.search_system:
            raise RuntimeError(
                "❌ Search system is MANDATORY but not initialized. "
                "Check BRAVE_API_KEY in .env"
            )
        
        # Create initial state with mandatory systems forced ON
        state = self._create_initial_state(inputs)
        
        # FORCE mandatory systems to be enabled regardless of input
        state["memory_enabled"] = True  # FORCE ENABLED
        state["search_enabled"] = True  # FORCE ENABLED
        
        # Override any attempt to disable them from inputs
        if inputs.get("memory_enabled") == False:
            logger.warning("⚠️ Attempt to disable memory blocked - Memory is MANDATORY")
        if inputs.get("search_enabled") == False:
            logger.warning("⚠️ Attempt to disable search blocked - Search is MANDATORY")
        
        # Log mandatory systems status
        logger.info("=" * 60)
        logger.info("EXECUTING WORKFLOW WITH MANDATORY SYSTEMS")
        logger.info(f"Company: {state.get('company', 'Unknown')}")
        logger.info(f"Client ID: {state.get('client_id', 'Unknown')}")
        logger.info(f"Memory: ✅ ENABLED (mandatory)")
        logger.info(f"Search: ✅ ENABLED (mandatory)")
        logger.info(f"Requested Agents: {state.get('requested_agents', [])}")
        logger.info("=" * 60)
        
        # Track start time
        start_time = time.time()
        
        try:
            # Verify systems are working before proceeding
            self._verify_mandatory_systems(state)
            
            # Execute workflow
            if self.compiled_graph:
                # Use compiled graph
                if self.verbose:
                    logger.info("Executing with compiled graph...")
                
                result_state = self.compiled_graph.invoke(
                    state,
                    config={"recursion_limit": 50}
                )
            else:
                # Use mock execution
                if self.verbose:
                    logger.info("Executing with mock workflow...")
                
                result_state = self._mock_execution(state)
            
            # Calculate execution time
            elapsed = time.time() - start_time
            
            # Add mandatory systems usage statistics
            if "statistics" not in result_state:
                result_state["statistics"] = {}
            
            result_state["statistics"]["memory_system"] = "ENABLED (mandatory)"
            result_state["statistics"]["search_system"] = "ENABLED (mandatory)"
            result_state["statistics"]["execution_time"] = elapsed
            
            # Log completion
            logger.info(f"✅ Workflow completed in {elapsed:.2f} seconds")
            logger.info(f"   Memory operations: {result_state.get('memories_loaded', {})}")
            logger.info(f"   Search queries: {len(result_state.get('web_sources', []))}")
            
            # Format and return results
            return self._format_results(result_state)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            
            # Return error result with partial data if available
            return self._create_error_result(
                f"Workflow failed: {str(e)}", 
                state if 'state' in locals() else None
            )

    def _verify_mandatory_systems(self, state: Dict[str, Any]):
        """
        Verify mandatory systems are operational before workflow execution.
        
        Args:
            state: Current workflow state
            
        Raises:
            RuntimeError: If any mandatory system fails verification
        """
        client_id = state.get('client_id', 'test')
        
        # Verify memory system
        try:
            test_memory = self.memory_system.store_memory(
                client_id=f"{client_id}_test",
                agent_name="system",
                memory_type="verification",
                content=f"Workflow verification at {datetime.now().isoformat()}",
                importance=0.1
            )
            if self.verbose:
                logger.info("✓ Memory system verified")
        except Exception as e:
            raise RuntimeError(f"Memory system verification failed: {e}")
        
        # Verify search system
        try:
            test_search = self.search_system.run("test verification")
            if not test_search:
                raise RuntimeError("Search returned no results")
            if self.verbose:
                logger.info("✓ Search system verified")
        except Exception as e:
            raise RuntimeError(f"Search system verification failed: {e}")
    
    def _create_initial_state(self, inputs: Dict[str, Any]) -> GraphState:
        """Convert bot inputs to graph state"""
        return {
            # Core inputs
            "company": inputs.get("company", "Unknown"),
            "business_context": inputs.get("business_context"),
            "template_data": inputs.get("template_data"),
            "client_id": inputs.get("client_id", "default"),
            "request_id": inputs.get("request_id"),
            
            # Configuration
            "requested_agents": inputs.get("requested_agents", [
                "psychological", "voice_of_customer", "competitor",
                "interview_psychological", "interview_sales", "gtm_blueprint"
            ]),
            "agent_config": inputs.get("agent_config"),
            
            # Features
            "search_enabled": inputs.get("search_enabled", self.config.search_enabled),
            "web_sources": inputs.get("web_sources", []),
            "memory_enabled": self.memory_system is not None,
            "memories_loaded": {},
            "memories_stored": {},
            
            # Initialize collections
            "agent_outputs": {},
            "agent_errors": {},
            "agent_metrics": {},
            "completed_agents": [],
            "failed_agents": [],
            "insights": {},
            "quality_scores": {},
            
            # Progress
            "current_agent": None,
            "slack_updater": inputs.get("slack_updater"),
            "progress_messages": [],
            
            # Timing
            "start_time": time.time(),
            "end_time": None,
            "agent_timings": {},
            
            # Settings
            "analysis_depth": inputs.get("analysis_depth", "comprehensive"),
            "source": inputs.get("source", "unknown"),
            
            # Results
            "final_report": None,
            "gtm_blueprint": None,
            "statistics": {}
        }
# ==============================================
    # 6. AGENT INITIALIZATION METHODS
    # ==============================================
    
    def _initialize_agents(self):
        """Initialize all agent instances with proper configuration"""
        logger.info("Initializing agent instances...")
        
        # Define agent registry
        agent_classes = {
            "psychological": "PsychologicalAgent",
            "voice_of_customer": "VoiceAgent",
            "competitor": "CompetitorAgent",
            "interview_psychological": "PsychologicalInterviewAgent",
            "interview_sales": "SalesInterviewAgent",
            "gtm_blueprint": "GTMBlueprintAgent"
        }
        
        # Try to import and initialize each agent
        for agent_name, class_name in agent_classes.items():
            try:
                # Dynamic import based on agent name
                if agent_name == "psychological":
                    from team_icp.agents.psychological import PsychologicalAgent
                    self.agents[agent_name] = PsychologicalAgent()
                    
                elif agent_name == "voice_of_customer":
                    from team_icp.agents.voice_of_customer import VoiceAgent
                    self.agents[agent_name] = VoiceAgent()
                    
                elif agent_name == "competitor":
                    from team_icp.agents.competitor import CompetitorAgent
                    self.agents[agent_name] = CompetitorAgent()
                    
                elif agent_name == "interview_psychological":
                    from team_icp.agents.interview_psychological import PsychologicalInterviewAgent
                    self.agents[agent_name] = PsychologicalInterviewAgent()
                    
                elif agent_name == "interview_sales":
                    from team_icp.agents.interview_sales import SalesInterviewAgent
                    self.agents[agent_name] = SalesInterviewAgent()
                    
                elif agent_name == "gtm_blueprint":
                    from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
                    self.agents[agent_name] = GTMBlueprintAgent()
                
                # Configure agent with workflow settings
                if agent_name in self.agents:
                    self._configure_agent(self.agents[agent_name], agent_name)
                    logger.info(f"  ✅ {agent_name} initialized")
                    
            except ImportError as e:
                logger.warning(f"  ⚠️ Could not import {agent_name}: {e}")
            except Exception as e:
                logger.error(f"  ❌ Failed to initialize {agent_name}: {e}")
        
        logger.info(f"Initialized {len(self.agents)} agents successfully")
        # This comment ensures _initialize_agents completion
    
    def _configure_agent(self, agent_instance, agent_name: str):
        """
        Configure an agent instance with workflow settings.
        
        Args:
            agent_instance: The agent object to configure
            agent_name: Name of the agent for settings lookup
        """
        try:
            # Set memory system if available
            if self.memory_system and hasattr(agent_instance, 'memory_system'):
                agent_instance.memory_system = self.memory_system
                agent_instance.memory_enabled = True
                print(f"   ✓ Memory configured for {agent_name}")
            
            # Set search system if available
            if self.search_system and hasattr(agent_instance, 'search_tool'):
                agent_instance.search_tool = self.search_system
                agent_instance.search_enabled = True
                print(f"   ✓ Search configured for {agent_name}")
            
            # Check if agent has LLM
            if hasattr(agent_instance, 'llm'):
                if agent_instance.llm is None:
                    print(f"   ⚠️ WARNING: {agent_name} has no LLM configured!")
                    # Try to set one
                    agent_instance.llm = self._create_default_llm(agent_name)
                    print(f"   ✓ LLM created and set for {agent_name}")
            else:
                print(f"   ⚠️ WARNING: {agent_name} has no 'llm' attribute!")
            
            # Set temperature if configurable
            if hasattr(agent_instance, 'temperature'):
                agent_instance.temperature = self.config.temperatures.get(
                    agent_name,
                    0.5  # Default temperature
                )
                print(f"   ✓ Temperature set to {agent_instance.temperature} for {agent_name}")
            
            # Set max tokens if configurable
            if hasattr(agent_instance, 'max_tokens'):
                if agent_name in ["psychological", "interview_psychological", "interview_sales"]:
                    agent_instance.max_tokens = self.config.max_tokens.get("creative", 8100)
                elif agent_name in ["gtm_blueprint"]:
                    agent_instance.max_tokens = self.config.max_tokens.get("summary", 4000)
                else:
                    agent_instance.max_tokens = self.config.max_tokens.get("research", 8100)
                print(f"   ✓ Max tokens set to {agent_instance.max_tokens} for {agent_name}")
            
            # Set verbose mode
            if hasattr(agent_instance, 'verbose'):
                agent_instance.verbose = self.verbose
                
        except Exception as e:
            logger.error(f"Error configuring {agent_name}: {e}")
            import traceback
            traceback.print_exc()
    
    def _execute_agent(self, state: GraphState, agent_name: str) -> GraphState:
        """
        Execute agent with ABSOLUTELY MANDATORY search and intelligent method detection.

        WHY: We need to prevent ANY agent execution without search results,
        AND handle both 'execute' and 'invoke' method names gracefully.
        """
        import time
        from typing import Dict, List

        start_time = time.time()

        try:
            # ============================================
            # STEP 1: VALIDATE MANDATORY SYSTEMS
            # ============================================
            print(f"\n{'='*60}")
            print(f"🎯 EXECUTING AGENT: {agent_name}")
            print(f"{'='*60}")

            # Check search system exists
            if not self.search_system:
                error_msg = f"FATAL: Search system not initialized for {agent_name}"
                print(f"❌ {error_msg}")

                # Mark agent as failed with clear reason
                state["failed_agents"].append(agent_name)
                state["agent_outputs"][agent_name] = f"[BLOCKED] No search system available"

                # Don't continue - this is a critical failure
                raise RuntimeError(error_msg)

            # ============================================
            # STEP 2: PERFORM MANDATORY PRE-SEARCH
            # ============================================
            print(f"\n📡 MANDATORY SEARCH PHASE")
            print(f"   Company: {state.get('company', 'Unknown')}")

            # Force search enabled in state
            state["search_enabled"] = True

            # Build targeted queries for this specific agent
            mandatory_queries = self._build_agent_specific_queries(
                company=state.get("company", ""),
                agent_name=agent_name
            )

            # Execute searches with retry logic
            search_results = []
            failed_searches = []

            for idx, query in enumerate(mandatory_queries[:3], 1):  # At least 3 searches
                try:
                    print(f"   [{idx}/3] Searching: '{query}'")

                    # Perform search with timeout
                    results = self._perform_web_search_with_retry(
                        state=state,
                        agent_name=agent_name,
                        query=query,
                        max_retries=2,
                        timeout=10
                    )

                    if results:
                        search_results.extend(results)
                        print(f"   ✅ Found {len(results)} results")
                    else:
                        print(f"   ⚠️ Empty results for query")
                        failed_searches.append(query)

                except Exception as e:
                    print(f"   ❌ Search error: {str(e)}")
                    failed_searches.append(query)

            # Validate we have minimum search results
            if len(search_results) < 2:  # Minimum threshold
                print(f"\n⚠️ WARNING: Only {len(search_results)} search results found")
                print(f"   Failed queries: {failed_searches}")

                # Still continue but mark as degraded
                state["search_quality"] = "degraded"
            else:
                print(f"\n✅ Search complete: {len(search_results)} total results")
                state["search_quality"] = "good"

            # Store search results in state
            if "web_sources" not in state:
                state["web_sources"] = []
            state["web_sources"].extend(search_results)

            # ============================================
            # STEP 3: PREPARE AGENT CONTEXT
            # ============================================
            print(f"\n🔧 PREPARING AGENT CONTEXT")

            agent_context = {
                "company_name": state.get("company", ""),
                "client_id": state.get("client_id", ""),
                "user_query": state.get("company", ""),

                # MANDATORY features - no optionals
                "search_enabled": True,
                "search_results": search_results,  # Direct results for this agent
                "web_sources": state.get("web_sources", []),  # All accumulated sources
                "search_quality": state.get("search_quality", "unknown"),

                "memory_enabled": True,
                "memory_results": state.get("memory_results", []),

                # Additional context
                "business_context": state.get("business_context", ""),
                "previous_outputs": {
                    agent: output
                    for agent, output in state.get("agent_outputs", {}).items()
                    if agent != agent_name  # Don't include self
                }
            }

            print(f"   ✓ Context prepared with {len(search_results)} search results")

            # ============================================
            # STEP 4: AGENT METHOD DETECTION & EXECUTION
            # ============================================
            print(f"\n🚀 EXECUTING AGENT LOGIC")

            # Get the agent
            agent = self.agents.get(agent_name)
            if not agent:
                raise ValueError(f"Agent '{agent_name}' not found in agents registry")

            # DEBUG: Inspect agent methods
            print(f"\n🔍 AGENT METHOD DETECTION:")
            print(f"   Agent class: {agent.__class__.__name__}")

            # Get all callable methods (excluding private ones)
            available_methods = [
                method for method in dir(agent)
                if not method.startswith('_') and callable(getattr(agent, method))
            ]
            print(f"   Available methods: {available_methods[:10]}")  # Show first 10

            # Detect execution method
            execution_method = None
            method_name = None

            # Priority order: execute > invoke > run > analyze > process
            method_priority = ['execute', 'invoke', 'run', 'analyze', 'process']

            for method in method_priority:
                if hasattr(agent, method) and callable(getattr(agent, method)):
                    execution_method = getattr(agent, method)
                    method_name = method
                    print(f"   ✅ Found method: '{method}' (priority method)")
                    break

            # If no standard method found, look for any method that might work
            if not execution_method:
                # Look for methods containing keywords
                execution_keywords = ['exec', 'run', 'process', 'analyze', 'perform']
                for method in available_methods:
                    if any(keyword in method.lower() for keyword in execution_keywords):
                        execution_method = getattr(agent, method)
                        method_name = method
                        print(f"   ⚠️ Using alternative method: '{method}'")
                        break

            # Final check
            if not execution_method:
                error_msg = (
                    f"Agent '{agent_name}' ({agent.__class__.__name__}) has no suitable execution method.\n"
                    f"Available methods: {available_methods}\n"
                    f"Expected one of: {method_priority}"
                )
                print(f"   ❌ {error_msg}")
                raise AttributeError(error_msg)

            print(f"   → Calling agent.{method_name}(context)")

# Execute the agent with the detected method
            try:
                print(f"\n📝 PRE-EXECUTION VALIDATION:")
                
                # Check if agent has necessary components
                if hasattr(agent, 'llm'):
                    if agent.llm is None:
                        print(f"   ⚠️ Agent has no LLM! Creating one...")
                        agent.llm = self._create_default_llm(agent_name)
                
                # Log what we're sending
                print(f"   Context keys: {list(agent_context.keys())}")
                print(f"   Search results: {len(agent_context.get('search_results', []))}")
                print(f"   Company: {agent_context.get('company_name', 'MISSING')}")
                
                # Execute
                print(f"\n   → Calling agent.{method_name}(context)...")
                start_exec = time.time()
                result = execution_method(agent_context)
                exec_duration = time.time() - start_exec
                print(f"   ✓ Agent.{method_name}() completed in {exec_duration:.2f}s")
                
                # VALIDATION: Check if execution was too fast (suspicious)
                if exec_duration < 0.5:  # Less than half a second is suspicious
                    print(f"   ⚠️ WARNING: Execution very fast ({exec_duration:.2f}s) - may be mock/empty")
            except TypeError as e:
                # Method might not accept our context format
                print(f"   ⚠️ Method signature mismatch, trying without context...")
                try:
                    # Try calling without arguments
                    result = execution_method()
                    print(f"   ✓ Agent.{method_name}() completed (no args)")
                except Exception:
                    # Try with just the company name
                    result = execution_method(state.get("company", ""))
                    print(f"   ✓ Agent.{method_name}() completed (company only)")

# ============================================
            # STEP 5: PROCESS RESULTS
            # ============================================
            print(f"\n📊 PROCESSING RESULTS")

            # Handle different result formats
            output = None

            if isinstance(result, dict):
                # Standard dictionary response
                output = result.get("output") or result.get("analysis") or result.get("content") or result.get("result")
                if not output and result:
                    # If no standard key, take the first substantial value
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 100:
                            output = value
                            print(f"   Using result['{key}'] as output")
                            break
            elif isinstance(result, str):
                # Direct string response
                output = result
            elif result is None:
                print(f"   ⚠️ Agent returned None")
                output = "[ERROR] Agent returned no result"
            else:
                # Unknown format - convert to string
                output = str(result)
                print(f"   ⚠️ Unusual result type: {type(result)}")

            # Store the output
            if output and len(output) > 50:  # Minimum viable output
                # ADDITIONAL VALIDATION
                print(f"\n🔍 OUTPUT VALIDATION:")
                print(f"   Length: {len(output)} chars")
                print(f"   Words: {len(output.split())} words")
                print(f"   Lines: {len(output.splitlines())} lines")
                
                # Check for common failure patterns
                failure_patterns = [
                    "[MOCK",
                    "ERROR",
                    "would go here",
                    "placeholder",
                    "not implemented",
                    "TODO"
                ]
                
                has_failure_pattern = any(pattern in output for pattern in failure_patterns)
                if has_failure_pattern:
                    print(f"   ⚠️ WARNING: Output contains failure patterns!")
                
                # Check if output is repetitive (sign of error)
                lines = output.splitlines()
                if len(lines) > 5:
                    unique_lines = len(set(lines))
                    if unique_lines < len(lines) / 2:
                        print(f"   ⚠️ WARNING: Output seems repetitive ({unique_lines}/{len(lines)} unique lines)")
                
                # Check for actual content vs boilerplate
                boilerplate_phrases = [
                    "I will analyze",
                    "Let me examine",
                    "I'll provide",
                    "Based on the search"
                ]
                
                content_score = 100
                for phrase in boilerplate_phrases:
                    if phrase.lower() in output.lower():
                        content_score -= 10
                
                print(f"   Content score: {content_score}% (lower = more boilerplate)")
                
                # Final decision
                if len(output) < 500 or content_score < 50 or has_failure_pattern:
                    print(f"   ❌ OUTPUT QUALITY CHECK FAILED")
                    print(f"   First 200 chars: {output[:200]}")
                    
                    # Try to understand why
                    if hasattr(agent, 'llm') and agent.llm is None:
                        print(f"   💡 Likely cause: Agent has no LLM configured")
                    elif len(search_results) == 0:
                        print(f"   💡 Likely cause: No search results provided")
                    else:
                        print(f"   💡 Likely cause: Agent implementation issue")
                    
                    state["agent_outputs"][agent_name] = f"[QUALITY CHECK FAILED] Output too short or low quality: {output[:500]}"
                    state["failed_agents"].append(agent_name)
                else:
                    print(f"   ✅ Output passes quality checks")
                    state["agent_outputs"][agent_name] = output
                    state["completed_agents"].append(agent_name)
            else:
                print(f"   ❌ Agent failed to generate sufficient output")
                print(f"   Output preview: {output[:200] if output else 'None'}")
                state["agent_outputs"][agent_name] = f"[ERROR] Insufficient output: {output[:100] if output else 'None'}"
                state["failed_agents"].append(agent_name)
            
            # ============================================
            # STEP 6: UPDATE STATE FOR NEXT AGENT
            # ============================================
            execution_time = time.time() - start_time
            print(f"\n⏱️ Execution time: {execution_time:.2f}s")

            # Update metrics
            if "metrics" not in state:
                state["metrics"] = {}
            state["metrics"][agent_name] = {
                "execution_time": execution_time,
                "search_results_count": len(search_results),
                "search_quality": state.get("search_quality", "unknown"),
                "method_used": method_name,
                "output_length": len(output) if output else 0
            }

            # Clear next_agent to allow router to decide
            state["next_agent"] = None

            return state

        except Exception as e:
            # Comprehensive error handling
            print(f"\n❌ CRITICAL ERROR in {agent_name}: {str(e)}")
            import traceback
            print(f"Traceback:\n{traceback.format_exc()}")

            # Mark agent as failed
            if agent_name not in state.get("failed_agents", []):
                state["failed_agents"].append(agent_name)
            state["agent_outputs"][agent_name] = f"[ERROR] {str(e)}"

            # Don't crash entire workflow
            return state
    
    def _prepare_agent_context(self, state: GraphState, agent_name: str) -> Dict[str, Any]:
        """
        Prepare context dictionary for agent execution.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent being executed
            
        Returns:
            Context dictionary for agent
        """
        context = {
            "company_name": state["company"],
            "client_id": state["client_id"],
            "request_id": state.get("request_id"),
            "user_query": state["company"],  # For compatibility
            
            # Include business context if available
            "business_context": state.get("business_context", ""),
            "template_data": state.get("template_data", {}),
            
            # Include insights from other agents
            "insights": state.get("insights", {}),
            "historical_insights": [],  # Will be populated from memory
            
            # Configuration
            "search_enabled": state["search_enabled"],
            "memory_enabled": state["memory_enabled"],
            
            # Web sources if available
            "web_sources": state.get("web_sources", []),
            
            # Analysis settings
            "analysis_depth": state.get("analysis_depth", "comprehensive")
        }
        
        # Add industry and market from template if available
        if state.get("template_data"):
            context["industry"] = state["template_data"].get("industry", "")
            context["market"] = state["template_data"].get("business_type", "")
            context["product"] = state["template_data"].get("product_service", "")
            context["target_audience"] = state["template_data"].get("target_customer", "")
        
        # Add previous agent outputs for cross-referencing
        for completed_agent in state["completed_agents"]:
            if completed_agent in state["agent_outputs"]:
                # Add to insights for other agents to use
                if completed_agent not in state["insights"]:
                    state["insights"][completed_agent] = {}
                
                output = state["agent_outputs"][completed_agent]
                # Extract key insights based on agent type
                state["insights"][completed_agent] = self._extract_agent_insights(
                    completed_agent, 
                    output
                )
        
        context["insights"] = state["insights"]
        
        return context
        # This comment ensures _prepare_agent_context completion
    
    def _extract_agent_insights(self, agent_name: str, output: str) -> Dict[str, Any]:
        """
        Extract key insights from agent output for cross-agent sharing.
        
        Args:
            agent_name: Name of the agent
            output: Agent's output text
            
        Returns:
            Dictionary of extracted insights
        """
        insights = {
            "analysis": output[:1000] if output else "",  # First 1000 chars
            "quality_score": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Agent-specific extraction
        if agent_name == "psychological":
            # Extract patterns, biases, triggers
            insights["patterns"] = self._extract_patterns(output, ["behavioral", "pattern", "tendency"])
            insights["biases"] = self._extract_patterns(output, ["bias", "cognitive", "heuristic"])
            insights["triggers"] = self._extract_patterns(output, ["trigger", "driver", "motivation"])
            
        elif agent_name == "voice_of_customer":
            # Extract quotes, pain points, sentiment
            insights["quotes"] = self._extract_quotes(output)
            insights["pain_points"] = self._extract_patterns(output, ["pain", "problem", "challenge"])
            insights["sentiment"] = self._detect_sentiment(output)
            
        elif agent_name == "competitor":
            # Extract competitors, gaps, advantages
            insights["competitors"] = self._extract_competitors(output)
            insights["gaps"] = self._extract_patterns(output, ["gap", "opportunity", "weakness"])
            insights["advantages"] = self._extract_patterns(output, ["advantage", "strength", "differentiator"])
            
        elif agent_name == "interview_psychological":
            # Extract emotional patterns, vulnerabilities
            insights["emotional_patterns"] = self._extract_patterns(output, ["emotion", "feel", "anxiety"])
            insights["vulnerabilities"] = self._extract_patterns(output, ["vulnerable", "fear", "concern"])
            
        elif agent_name == "interview_sales":
            # Extract objections, success factors
            insights["objections"] = self._extract_patterns(output, ["objection", "concern", "hesitation"])
            insights["success_factors"] = self._extract_patterns(output, ["success", "win", "close"])
            
        elif agent_name == "gtm_blueprint":
            # Extract strategic pillars, tactics
            insights["strategic_pillars"] = self._extract_patterns(output, ["strategy", "pillar", "focus"])
            insights["tactics"] = self._extract_patterns(output, ["tactic", "action", "implement"])
        
        return insights
        # This comment ensures _extract_agent_insights completion
    
    def _extract_patterns(self, text: str, keywords: List[str]) -> List[str]:
        """Extract patterns based on keywords"""
        patterns = []
        if not text:
            return patterns
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in keywords):
                cleaned = sentence.strip()
                if len(cleaned) > 20 and len(cleaned) < 200:
                    patterns.append(cleaned)
                    if len(patterns) >= 5:  # Limit to 5 patterns
                        break
        
        return patterns
        # This comment ensures _extract_patterns completion
    
    def _extract_quotes(self, text: str) -> List[str]:
        """Extract quoted text from output"""
        import re
        quotes = []
        if not text:
            return quotes
        
        # Find text in quotes
        pattern = r'"([^"]{20,200})"'
        matches = re.findall(pattern, text)
        
        for match in matches[:5]:  # Limit to 5 quotes
            quotes.append(match)
        
        return quotes
        # This comment ensures _extract_quotes completion
    
    def _extract_competitors(self, text: str) -> List[str]:
        """Extract competitor names from text"""
        competitors = []
        if not text:
            return competitors
        
        # Look for common competitor patterns
        import re
        patterns = [
            r'competitors?:?\s*([\w\s,]+)',
            r'competing with\s*([\w\s,]+)',
            r'alternatives?:?\s*([\w\s,]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Split by commas and clean
                names = match.split(',')
                for name in names[:5]:
                    cleaned = name.strip()
                    if len(cleaned) > 2 and len(cleaned) < 50:
                        competitors.append(cleaned)
        
        return competitors[:5]  # Limit to 5 competitors
        # This comment ensures _extract_competitors completion
    
    def _detect_sentiment(self, text: str) -> str:
        """Detect overall sentiment from text"""
        if not text:
            return "neutral"
        
        text_lower = text.lower()
        
        positive_words = ["positive", "good", "great", "excellent", "happy", "satisfied", "love"]
        negative_words = ["negative", "bad", "poor", "terrible", "unhappy", "frustrated", "hate"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
        # This comment ensures _detect_sentiment completion
# ==============================================
    # 8. GRAPH BUILDING METHODS
    # ==============================================
    
    def _build_graph(self):
        """Build the workflow graph with nodes and edges"""
        if not LANGGRAPH_AVAILABLE:
            logger.error("LangGraph not available - cannot build workflow")
            return
        
        try:
            # Create the state graph
            self.graph = StateGraph(GraphState)
            
            # Add nodes for each agent
            self._add_agent_nodes()
            
            # Add control nodes
            self._add_control_nodes()
            
            # Add edges and conditional routing
            self._add_edges()
            
            # Compile the graph
            self._compile_graph()
            
            logger.info("✅ Workflow graph built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build graph: {e}")
            self.graph = None
            self.compiled_graph = None
        # This comment ensures _build_graph completion
    
    def _add_agent_nodes(self):
        """Add nodes for each initialized agent"""
        for agent_name in self.agents.keys():
            # Create a node function for each agent
            node_func = self._create_agent_node(agent_name)
            self.graph.add_node(agent_name, node_func)
            
            if self.verbose:
                logger.info(f"  Added node: {agent_name}")
        # This comment ensures _add_agent_nodes completion
    
    def _add_control_nodes(self):
        """Add control flow nodes"""
        # Start node - initializes workflow
        self.graph.add_node("start", self._start_node)
        
        # Router node - decides which agent to run next
        self.graph.add_node("router", self._router_node)
        
        # Synthesizer node - combines all agent outputs
        self.graph.add_node("synthesizer", self._synthesizer_node)
        
        # Quality check node
        self.graph.add_node("quality_check", self._quality_check_node)
        
        # Finalize node - prepares final output
        self.graph.add_node("finalize", self._finalize_node)
        
        if self.verbose:
            logger.info("  Added control nodes: start, router, synthesizer, quality_check, finalize")
        # This comment ensures _add_control_nodes completion
    
    def _add_edges(self):
        """Add edges and conditional routing to the graph"""
        # Entry point
        self.graph.set_entry_point("start")
        
        # From start to router
        self.graph.add_edge("start", "router")
        
        # Router decides which agent to run
        self.graph.add_conditional_edges(
            "router",
            self._route_to_agent,
            {
                "psychological": "psychological",
                "voice_of_customer": "voice_of_customer",
                "competitor": "competitor",
                "interview_psychological": "interview_psychological",
                "interview_sales": "interview_sales",
                "gtm_blueprint": "gtm_blueprint",
                "synthesizer": "synthesizer",
                "end": END
            }
        )
        
        # Each agent goes back to router
        for agent_name in self.agents.keys():
            self.graph.add_edge(agent_name, "router")
        
        # Synthesizer to quality check
        self.graph.add_edge("synthesizer", "quality_check")
        
        # Quality check to finalize or back to router for retries
        self.graph.add_conditional_edges(
            "quality_check",
            self._check_quality,
            {
                "finalize": "finalize",
                "retry": "router",
                "end": END
            }
        )
        
        # Finalize to end
        self.graph.add_edge("finalize", END)
        
        if self.verbose:
            logger.info("  Added edges and routing logic")
        # This comment ensures _add_edges completion
    
    def _compile_graph(self):
        """Compile the graph for execution"""
        try:
            
            self.compiled_graph = self.graph.compile()
            
            if self.verbose:
                logger.info("  Graph compiled successfully")
                
        except Exception as e:
            logger.error(f"Failed to compile graph: {e}")
            self.compiled_graph = None
        # This comment ensures _compile_graph completion
    
    # ==============================================
    # 9. NODE IMPLEMENTATION FUNCTIONS
    # ==============================================
    
    def _create_agent_node(self, agent_name: str):
        """
        Create a node function for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Node function for the agent
        """
        def agent_node(state: GraphState) -> GraphState:
            """Execute agent and update state"""
            # Send progress update
            self._send_progress_update(
                state, 
                f"🔄 {agent_name.replace('_', ' ').title()} analyzing..."
            )
            
            # Execute the agent
            return self._execute_agent(state, agent_name)
        
        return agent_node
        # This comment ensures _create_agent_node completion
    
    def _start_node(self, state: GraphState) -> GraphState:
        """
        Initialize the workflow.
        
        Args:
            state: Initial state
            
        Returns:
            Updated state
        """
        # Send initial progress
        self._send_progress_update(state, "🚀 Starting market research workflow...")
        
        # Log configuration
        if self.verbose:
            logger.info("Workflow configuration:")
            logger.info(f"  Company: {state['company']}")
            logger.info(f"  Requested agents: {state['requested_agents']}")
            logger.info(f"  Memory enabled: {state['memory_enabled']}")
            logger.info(f"  Search enabled: {state['search_enabled']}")
            logger.info(f"  Analysis depth: {state['analysis_depth']}")
        
        # Initialize timing
        state["start_time"] = time.time()
        
        # Load global memories if available
        if state["memory_enabled"] and self.memory_system:
            try:
                context = self.memory_system.get_client_context(state["client_id"])
                if context:
                    total_memories = sum(len(insights) for insights in context.values())
                    self._send_progress_update(
                        state, 
                        f"💾 Found {total_memories} memories from previous analyses"
                    )
            except Exception as e:
                logger.warning(f"Could not load global memories: {e}")
        
        return state
        # This comment ensures _start_node completion
    
    def _router_node(self, state: GraphState) -> GraphState:
        """
        Route to the next agent or finish.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with routing decision
        """
        # Determine next agent to run
        remaining_agents = [
            agent for agent in state["requested_agents"]
            if agent not in state["completed_agents"] 
            and agent not in state["failed_agents"]
        ]
        
        if self.verbose:
            logger.info(f"Router: {len(remaining_agents)} agents remaining")
            logger.info(f"  Completed: {state['completed_agents']}")
            logger.info(f"  Failed: {state['failed_agents']}")
        
        # Store next agent in state for routing
        if remaining_agents:
            state["next_agent"] = remaining_agents[0]
        else:
            state["next_agent"] = None
        
        return state
        # This comment ensures _router_node completion
    
    def _route_to_agent(self, state: GraphState) -> str:
        """
        Determine which node to route to based on state.
        
        WHY: The router wasn't forcing agent execution when no next_agent was set,
        causing agents to be skipped entirely.
        """
        next_agent = state.get("next_agent")
        
        # Debug logging to understand routing decisions
        print(f"🔀 ROUTER DEBUG:")
        print(f"   - next_agent: {next_agent}")
        print(f"   - requested_agents: {state.get('requested_agents', [])}")
        print(f"   - completed_agents: {state.get('completed_agents', [])}")
        print(f"   - failed_agents: {state.get('failed_agents', [])}")
        
        # If explicit next_agent is set and valid
        if next_agent and next_agent in self.agents:
            print(f"   ✓ Routing to explicit agent: {next_agent}")
            return next_agent
        
        # Get remaining agents to execute
        requested = set(state.get("requested_agents", []))
        completed = set(state.get("completed_agents", []))
        failed = set(state.get("failed_agents", []))
        remaining = requested - completed - failed
        
        print(f"   - remaining agents: {remaining}")
        
        # If we have agents left to execute, pick the first one
        if remaining:
            # Sort for consistent ordering
            next_to_run = sorted(remaining)[0]
            print(f"   ✓ Auto-routing to next agent: {next_to_run}")
            return next_to_run
        
        # All agents done, check if we should synthesize
        if completed and len(completed) > 0:
            print(f"   ✓ All agents complete, routing to synthesizer")
            return "synthesizer"
        
        # Edge case: No agents completed but none remaining
        if not completed and not remaining and requested:
            print(f"   ⚠️ WARNING: All requested agents failed!")
            return "synthesizer"  # Still try to synthesize
        
        print(f"   ✓ Workflow complete, routing to end")
        return "end"
        # This comment ensures _route_to_agent completion
    
    def _synthesizer_node(self, state: GraphState) -> GraphState:
        """
        Synthesize outputs from all agents.
        
        Args:
            state: Current state with agent outputs
            
        Returns:
            State with synthesized report
        """
        self._send_progress_update(state, "📊 Synthesizing insights from all agents...")
        
        try:
            # Check if GTM Blueprint agent ran
            if "gtm_blueprint" in state["agent_outputs"]:
                # GTM Blueprint already synthesizes
                state["gtm_blueprint"] = state["agent_outputs"]["gtm_blueprint"]
                state["final_report"] = state["gtm_blueprint"]
            else:
                # Create synthesis from individual agents
                synthesis = self._create_synthesis(state)
                state["final_report"] = synthesis
            
            # Calculate overall statistics
            state["statistics"] = self._calculate_statistics(state)
            
            if self.verbose:
                logger.info(f"Synthesis complete: {len(state['final_report'])} chars")
                
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            state["final_report"] = "Synthesis failed - see individual agent outputs"
        
        return state
        # This comment ensures _synthesizer_node completion
    
    def _quality_check_node(self, state: GraphState) -> GraphState:
        """
        Check quality of the analysis.
        
        Args:
            state: Current state with outputs
            
        Returns:
            State with quality assessment
        """
        self._send_progress_update(state, "✅ Checking analysis quality...")
        
        try:
            # Calculate quality scores for each agent
            for agent_name, output in state["agent_outputs"].items():
                if output and not output.startswith("[ERROR"):
                    score = self._calculate_quality_score(output, agent_name)
                    state["quality_scores"][agent_name] = score
            
            # Calculate overall quality
            if state["quality_scores"]:
                avg_quality = sum(state["quality_scores"].values()) / len(state["quality_scores"])
            else:
                avg_quality = 0.0
            
            state["statistics"]["overall_quality"] = avg_quality
            
            # Determine if quality is acceptable
            if avg_quality >= self.config.quality_threshold:
                state["quality_passed"] = True
                if self.verbose:
                    logger.info(f"Quality check passed: {avg_quality:.2%}")
            else:
                state["quality_passed"] = False
                if self.verbose:
                    logger.warning(f"Quality check failed: {avg_quality:.2%}")
            
        except Exception as e:
            logger.error(f"Quality check error: {e}")
            state["quality_passed"] = True  # Continue anyway
        
        return state
        # This comment ensures _quality_check_node completion
    
    def _check_quality(self, state: GraphState) -> str:
        """
        Determine routing based on quality check.
        
        Args:
            state: Current state
            
        Returns:
            Next node name
        """
        # For now, always proceed to finalize
        # In future, could implement retry logic for low quality
        return "finalize"
        # This comment ensures _check_quality completion
    
    def _finalize_node(self, state: GraphState) -> GraphState:
        """
        Finalize the analysis and prepare output.
        
        Args:
            state: Current state
            
        Returns:
            Final state with all outputs prepared
        """
        self._send_progress_update(state, "📝 Finalizing analysis...")
        
        try:
            # Set end time
            state["end_time"] = time.time()
            elapsed = state["end_time"] - state["start_time"]
            
            # Add timing to statistics
            state["statistics"]["execution_time"] = elapsed
            state["statistics"]["agent_timings"] = state["agent_timings"]
            
            # Count successful agents
            state["statistics"]["total_agents"] = len(state["requested_agents"])
            state["statistics"]["successful_agents"] = len(state["completed_agents"])
            state["statistics"]["failed_agents"] = len(state["failed_agents"])
            
            # Word count
            total_words = sum(
                len(output.split()) 
                for output in state["agent_outputs"].values() 
                if output and not output.startswith("[ERROR")
            )
            state["statistics"]["total_words"] = total_words
            
            # Memory statistics
            state["statistics"]["memories_loaded"] = state["memories_loaded"]
            state["statistics"]["memories_stored"] = state["memories_stored"]
            
            # Final message
            self._send_progress_update(
                state,
                f"✅ Analysis complete! {len(state['completed_agents'])} agents, {elapsed:.1f}s"
            )
            
            if self.verbose:
                logger.info("Workflow finalized successfully")
                logger.info(f"  Total time: {elapsed:.2f}s")
                logger.info(f"  Successful agents: {state['statistics']['successful_agents']}")
                logger.info(f"  Total words: {total_words}")
                
        except Exception as e:
            logger.error(f"Finalization error: {e}")
        
        return state
        # This comment ensures _finalize_node completion
# ==============================================
    # 10. MEMORY SYSTEM INTEGRATION
    # ==============================================
    
    def _load_agent_memories(self, state: GraphState, agent_name: str) -> int:
        """
        Load memories for a specific agent.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent to load memories for
            
        Returns:
            Number of memories loaded
        """
        if not self.memory_system or not state.get("memory_enabled"):
            return 0
        
        try:
            client_id = state["client_id"]
            company = state["company"]
            
            # Build query based on agent type and context
            query = self._build_memory_query(state, agent_name)
            
            # Retrieve memories
            memories = self.memory_system.retrieve_memories(
                client_id=client_id,
                agent_name=agent_name,
                query=query,
                limit=10  # Limit to most relevant memories
            )
            
            if memories:
                # Add memories to agent context
                if "insights" not in state:
                    state["insights"] = {}
                
                if agent_name not in state["insights"]:
                    state["insights"][agent_name] = {}
                
                # Store memories in insights for agent to use
                state["insights"][agent_name]["memories"] = [
                    {
                        "content": mem.content,
                        "importance": mem.importance,
                        "timestamp": mem.timestamp.isoformat() if hasattr(mem, 'timestamp') else None
                    }
                    for mem in memories
                ]
                
                if self.verbose:
                    logger.info(f"  Loaded {len(memories)} memories for {agent_name}")
                
                return len(memories)
            
            return 0
            
        except Exception as e:
            logger.warning(f"Could not load memories for {agent_name}: {e}")
            return 0
        # This comment ensures _load_agent_memories completion
    
    def _store_agent_memories(self, state: GraphState, agent_name: str, result: Dict[str, Any]) -> bool:
        """
        Store agent results as memories.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent
            result: Agent execution results
            
        Returns:
            True if memories were stored successfully
        """
        if not self.memory_system or not state.get("memory_enabled"):
            return False
        
        try:
            client_id = state["client_id"]
            
            # Get the main analysis output
            analysis = result.get("analysis", "")
            if not analysis:
                # Try alternative keys
                analysis = result.get("output", result.get("content", ""))
            
            if not analysis or len(analysis) < 100:
                return False
            
            # Store main analysis
            memory_stored = False
            
            # Store primary analysis
            if analysis:
                self.memory_system.store_memory(
                    client_id=client_id,
                    agent_name=agent_name,
                    memory_type="analysis",
                    content=analysis[:2000],  # Limit size
                    importance=0.8
                )
                memory_stored = True
            
            # Store specific insights based on agent type
            if agent_name == "psychological" and "patterns" in result:
                for pattern in result.get("patterns", [])[:3]:
                    self.memory_system.store_memory(
                        client_id=client_id,
                        agent_name=agent_name,
                        memory_type="pattern",
                        content=f"Psychological pattern: {pattern}",
                        importance=0.7
                    )
            
            elif agent_name == "voice_of_customer" and "quotes" in result:
                for quote in result.get("quotes", [])[:3]:
                    self.memory_system.store_memory(
                        client_id=client_id,
                        agent_name=agent_name,
                        memory_type="quote",
                        content=f"Customer quote: {quote}",
                        importance=0.7
                    )
            
            elif agent_name == "competitor" and "competitors" in result:
                competitors_list = result.get("competitors", [])[:5]
                if competitors_list:
                    self.memory_system.store_memory(
                        client_id=client_id,
                        agent_name=agent_name,
                        memory_type="competitors",
                        content=f"Competitors identified: {', '.join(competitors_list)}",
                        importance=0.7
                    )
            
            if memory_stored and self.verbose:
                logger.info(f"  Stored memories for {agent_name}")
            
            return memory_stored
            
        except Exception as e:
            logger.warning(f"Could not store memories for {agent_name}: {e}")
            return False
        # This comment ensures _store_agent_memories completion
    
    def _build_memory_query(self, state: GraphState, agent_name: str) -> str:
        """
        Build memory query based on context and agent type.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent
            
        Returns:
            Query string for memory retrieval
        """
        company = state["company"]
        
        # Base query with company
        query_parts = [company]
        
        # Add template context if available
        if state.get("template_data"):
            template = state["template_data"]
            if template.get("industry"):
                query_parts.append(template["industry"])
            if template.get("product_service"):
                query_parts.append(template["product_service"][:50])
        
        # Add agent-specific keywords
        agent_keywords = {
            "psychological": ["behavior", "psychology", "patterns", "mental", "cognitive"],
            "voice_of_customer": ["customer", "voice", "quote", "feedback", "complaint"],
            "competitor": ["competitor", "competition", "alternative", "market", "position"],
            "interview_psychological": ["interview", "emotional", "psychological", "vulnerability"],
            "interview_sales": ["sales", "objection", "budget", "decision", "buying"],
            "gtm_blueprint": ["strategy", "gtm", "go-to-market", "positioning", "messaging"]
        }
        
        if agent_name in agent_keywords:
            query_parts.extend(agent_keywords[agent_name][:2])
        
        return " ".join(query_parts)
        # This comment ensures _build_memory_query completion
    
    # ==============================================
    # 11. SEARCH SYSTEM INTEGRATION
    # ==============================================
    
    def _perform_web_search(self, state: GraphState, agent_name: str, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search for an agent.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent performing search
            query: Search query
            
        Returns:
            List of search results
        """
        if not self.search_system or not state.get("search_enabled"):
            return []
        
        try:
            # Check if we already have web sources from bot
            if state.get("web_sources"):
                # Use provided sources if relevant
                return state["web_sources"]
            
            # Perform new search
            if self.verbose:
                logger.info(f"  Searching: {query}")
            
            results = self.search_system.run(query)
            
            # Parse results
            if isinstance(results, str):
                import json
                try:
                    results = json.loads(results)
                except:
                    results = []
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results[:5], 1):
                formatted_results.append({
                    "id": f"{agent_name}_source_{i}",
                    "title": result.get("title", "Unknown"),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "content": result.get("snippet", "")  # Use snippet as content
                })
            
            # Add to state's web sources
            if "web_sources" not in state:
                state["web_sources"] = []
            state["web_sources"].extend(formatted_results)
            
            if self.verbose:
                logger.info(f"  Found {len(formatted_results)} search results")
            
            return formatted_results
            
        except Exception as e:
            logger.warning(f"Search failed for {agent_name}: {e}")
            return []
        # This comment ensures _perform_web_search completion
    
    
    
    def _enhance_context_with_search(self, state: GraphState, agent_name: str) -> str:
        """
        Enhance agent context with web search results.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent
            
        Returns:
            Enhanced context string
        """
        if not state.get("search_enabled"):
            return ""
        
        company = state["company"]
        industry = state.get("template_data", {}).get("industry", "")
        
        # Build agent-specific search queries
        search_queries = self._build_search_queries(company, industry, agent_name)
        
        enhanced_context = []
        all_sources = []
        
        for query in search_queries[:2]:  # Limit searches to avoid rate limits
            results = self._perform_web_search(state, agent_name, query)
            
            if results:
                enhanced_context.append(f"\n=== Web Research: {query} ===")
                for result in results[:3]:
                    enhanced_context.append(f"""
Source: {result['title']}
URL: {result['url']}
Content: {result['snippet']}
---""")
                all_sources.extend(results)
                
                # Rate limiting
                time.sleep(0.5)
        
        # Store sources for agent
        if all_sources and "insights" not in state:
            state["insights"] = {}
        if agent_name not in state["insights"]:
            state["insights"][agent_name] = {}
        state["insights"][agent_name]["sources"] = all_sources
        
        return "\n".join(enhanced_context)
        # This comment ensures _enhance_context_with_search completion
    
    def _build_agent_specific_queries(self, company: str, agent_name: str) -> List[str]:
        """
        Build comprehensive search queries with variations and industry terms.
        
        WHY: Different search engines and contexts require query variations
        to get comprehensive results. Industry-specific terms improve relevance.
        """
        import datetime
        current_year = datetime.datetime.now().year
        
        # Get industry context if available
        industry_terms = self._get_industry_specific_terms(company)
        
        # ============================================
        # BASE QUERIES - Every agent needs these
        # ============================================
        base_queries = [
            # Company overview variations
            f"{company}",
            f"{company} company profile",
            f"{company} business overview {current_year}",
            f'"{company}" about company',
            
            # Recent updates variations  
            f"{company} news {current_year}",
            f"{company} latest developments",
            f"{company} recent announcements",
            f'"{company}" press releases {current_year}',
        ]
        
        # ============================================
        # AGENT-SPECIFIC QUERY SETS
        # ============================================
        agent_queries = {
            "competitor": [
                # Direct competitor queries
                f"{company} competitors",
                f"{company} vs competitors analysis",
                f'"{company}" main competitors {current_year}',
                f"{company} competitive landscape",
                f"{company} market share competitors",
                
                # Competitive advantage variations
                f"{company} competitive advantages",
                f"{company} unique selling proposition",
                f"{company} differentiation strategy",
                f'"{company}" moat competitive edge',
                
                # Market position queries
                f"{company} market position ranking",
                f"{company} industry ranking {current_year}",
                f'"{company}" market leader challenger',
                
                # Add industry-specific competitor terms
                *[f"{company} {term} competitors" for term in industry_terms.get("competitor_terms", [])]
            ],
            
            "market_trends": [
                # Industry trend queries
                f"{company} industry trends {current_year}",
                f"{company} market trends analysis",
                f"{company} sector outlook {current_year}",
                f'"{company}" industry forecasts',
                
                # Growth and opportunity queries
                f"{company} market opportunities",
                f"{company} growth potential analysis",
                f"{company} TAM total addressable market",
                f"{company} market size growth rate",
                
                # Disruption and innovation queries
                f"{company} industry disruption",
                f"{company} emerging technologies impact",
                f"{company} digital transformation",
                f'"{company}" innovation trends',
                
                # Regulatory and macro queries
                f"{company} regulatory environment",
                f"{company} industry regulations changes",
                f"{company} macroeconomic factors impact",
                
                # Industry-specific trend terms
                *[f"{company} {term}" for term in industry_terms.get("trend_terms", [])]
            ],
            
            "financial": [
                # Financial performance queries
                f"{company} financial results {current_year}",
                f"{company} earnings revenue {current_year}",
                f"{company} financial statements",
                f'"{company}" quarterly results',
                f"{company} annual report {current_year-1}",
                
                # Financial metrics variations
                f"{company} revenue growth rate",
                f"{company} profit margins EBITDA",
                f"{company} cash flow analysis",
                f"{company} balance sheet strength",
                
                # Valuation and investment queries
                f"{company} valuation metrics",
                f"{company} stock price performance",
                f"{company} investment analysis",
                f'"{company}" analyst ratings',
                
                # Financial health queries
                f"{company} debt equity ratio",
                f"{company} financial stability",
                f"{company} credit rating",
                
                # Industry-specific financial terms
                *[f"{company} {term}" for term in industry_terms.get("financial_terms", [])]
            ],
            
            "customer": [
                # Customer feedback queries
                f"{company} customer reviews {current_year}",
                f"{company} customer satisfaction score",
                f'"{company}" user feedback testimonials',
                f"{company} NPS net promoter score",
                
                # Customer experience queries
                f"{company} customer experience",
                f"{company} customer service quality",
                f"{company} customer complaints issues",
                f'"{company}" customer support rating',
                
                # Customer base queries
                f"{company} customer demographics",
                f"{company} target audience market",
                f"{company} customer retention rate",
                f"{company} customer acquisition strategy",
                
                # Platform-specific reviews
                f"{company} Trustpilot reviews",
                f"{company} Google reviews rating",
                f"{company} Glassdoor reviews",
                f'"{company}" Better Business Bureau',
                
                # Industry-specific customer terms
                *[f"{company} {term}" for term in industry_terms.get("customer_terms", [])]
            ],
            
            "product": [
                # Product portfolio queries
                f"{company} products services list",
                f"{company} product catalog portfolio",
                f'"{company}" main offerings',
                f"{company} flagship products",
                
                # Product innovation queries
                f"{company} new product launches {current_year}",
                f"{company} product innovation R&D",
                f"{company} product development pipeline",
                f'"{company}" patents technology',
                
                # Product quality queries
                f"{company} product quality reviews",
                f"{company} product features benefits",
                f"{company} product pricing strategy",
                f'"{company}" product comparison',
                
                # Product market fit queries
                f"{company} product market fit",
                f"{company} product differentiation",
                f"{company} unique features advantages",
                
                # Industry-specific product terms
                *[f"{company} {term}" for term in industry_terms.get("product_terms", [])]
            ],
            
            "technology": [
                # Tech stack queries
                f"{company} technology stack",
                f"{company} tech infrastructure",
                f'"{company}" engineering blog',
                f"{company} API documentation",
                
                # Innovation queries
                f"{company} AI machine learning",
                f"{company} automation technology", 
                f"{company} digital capabilities",
                f'"{company}" tech innovation',
                
                # Industry-specific tech terms
                *[f"{company} {term}" for term in industry_terms.get("tech_terms", [])]
            ]
        }
        
        # ============================================
        # COMBINE AND FILTER QUERIES
        # ============================================
        
        # Get base queries
        all_queries = base_queries.copy()
        
        # Add agent-specific queries
        if agent_name in agent_queries:
            all_queries.extend(agent_queries[agent_name])
        else:
            # Fallback for unknown agents - use a mix
            print(f"   ⚠️ Unknown agent '{agent_name}', using mixed queries")
            for queries in agent_queries.values():
                all_queries.extend(queries[:2])  # Take first 2 from each
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in all_queries:
            if query.lower() not in seen:
                seen.add(query.lower())
                unique_queries.append(query)
        
        # Limit to reasonable number (too many can be counterproductive)
        max_queries = 15
        if len(unique_queries) > max_queries:
            print(f"   📝 Trimmed from {len(unique_queries)} to {max_queries} queries")
            unique_queries = unique_queries[:max_queries]
        
        print(f"   ✅ Generated {len(unique_queries)} unique queries for {agent_name}")
        return unique_queries

    def _get_industry_specific_terms(self, company: str) -> Dict[str, List[str]]:
            """
            Get industry-specific search terms based on company context.
    
            WHY: Different industries have unique terminology. Tech companies
            need different search terms than retail or healthcare companies.
            """
            # Try to detect industry from company name or context
            company_lower = company.lower()
    
            # Default terms that apply to most industries
            default_terms = {
                "competitor_terms": ["market share", "competitive analysis"],
                "trend_terms": ["industry outlook", "market forecast"],
                "financial_terms": ["earnings report", "financial performance"],
                "customer_terms": ["customer satisfaction", "user experience"],
                "product_terms": ["product lineup", "service offerings"],
                "tech_terms": ["digital transformation", "technology adoption"]
            }
    
            # Industry-specific term sets
            industry_terms = {
                "technology": {
                    "competitor_terms": ["tech rivals", "platform competition", "ecosystem battle"],
                    "trend_terms": ["AI adoption", "cloud migration", "cybersecurity trends", "DevOps practices"],
                    "financial_terms": ["SaaS metrics", "ARR annual recurring revenue", "burn rate", "unit economics"],
                    "customer_terms": ["developer experience", "user adoption", "churn rate", "MAU DAU"],
                    "product_terms": ["API features", "SDK", "platform capabilities", "integrations"],
                    "tech_terms": ["microservices", "kubernetes", "machine learning models", "data pipeline"]
                },
    
                "finance": {
                    "competitor_terms": ["fintech disruption", "banking rivals", "market makers"],
                    "trend_terms": ["DeFi trends", "open banking", "regulatory compliance", "Basel III"],
                    "financial_terms": ["tier 1 capital", "loan portfolio", "net interest margin", "AUM"],
                    "customer_terms": ["account holders", "wealth management clients", "retail banking"],
                    "product_terms": ["financial instruments", "lending products", "investment solutions"],
                    "tech_terms": ["blockchain adoption", "payment processing", "risk algorithms"]
                },
    
                "retail": {
                    "competitor_terms": ["retail competitors", "e-commerce rivals", "market penetration"],
                    "trend_terms": ["omnichannel retail", "D2C direct to consumer", "retail apocalypse"],
                    "financial_terms": ["same-store sales", "inventory turnover", "gross margin", "GMROI"],
                    "customer_terms": ["shopper behavior", "customer loyalty", "foot traffic", "conversion rate"],
                    "product_terms": ["SKU performance", "private label", "merchandise mix", "seasonal items"],
                    "tech_terms": ["POS systems", "inventory management", "mobile commerce", "RFID"]
                },
    
                "healthcare": {
                    "competitor_terms": ["pharma competitors", "biotech rivals", "hospital networks"],
                    "trend_terms": ["telehealth adoption", "precision medicine", "value-based care"],
                    "financial_terms": ["R&D pipeline", "drug pricing", "reimbursement rates", "EBITDA margins"],
                    "customer_terms": ["patient outcomes", "clinical trials", "provider networks"],
                    "product_terms": ["drug portfolio", "medical devices", "therapeutic areas", "FDA approval"],
                    "tech_terms": ["EHR systems", "clinical AI", "genomics platform", "digital therapeutics"]
                },
    
                "automotive": {
                    "competitor_terms": ["auto manufacturers", "EV competitors", "mobility rivals"],
                    "trend_terms": ["electric vehicles", "autonomous driving", "mobility as service"],
                    "financial_terms": ["vehicle sales", "production capacity", "dealer inventory"],
                    "customer_terms": ["driver experience", "safety ratings", "brand loyalty", "JD Power"],
                    "product_terms": ["vehicle lineup", "powertrain technology", "ADAS features"],
                    "tech_terms": ["battery technology", "connected car", "V2X communication", "lidar sensors"]
                },
    
                "energy": {
                    "competitor_terms": ["energy rivals", "renewable competitors", "utility companies"],
                    "trend_terms": ["renewable transition", "carbon neutral", "grid modernization"],
                    "financial_terms": ["production costs", "commodity prices", "capex spending", "PPA"],
                    "customer_terms": ["energy consumers", "industrial clients", "grid reliability"],
                    "product_terms": ["energy portfolio", "generation capacity", "transmission assets"],
                    "tech_terms": ["smart grid", "energy storage", "solar efficiency", "wind turbines"]
                }
            }
    
            # Try to detect industry
            detected_industry = None
    
            # Simple keyword detection (you can make this more sophisticated)
            tech_keywords = ["tech", "software", "cloud", "saas", "ai", "data", "cyber", "digital"]
            finance_keywords = ["bank", "financial", "capital", "investment", "insurance", "fintech"]
            retail_keywords = ["retail", "store", "shop", "commerce", "fashion", "apparel"]
            healthcare_keywords = ["health", "medical", "pharma", "bio", "clinical", "therapeutics"]
            auto_keywords = ["auto", "car", "vehicle", "motor", "automotive", "mobility"]
            energy_keywords = ["energy", "power", "oil", "gas", "renewable", "solar", "wind"]
    
            # Check company name for industry indicators
            if any(keyword in company_lower for keyword in tech_keywords):
                detected_industry = "technology"
            elif any(keyword in company_lower for keyword in finance_keywords):
                detected_industry = "finance"
            elif any(keyword in company_lower for keyword in retail_keywords):
                detected_industry = "retail"
            elif any(keyword in company_lower for keyword in healthcare_keywords):
                detected_industry = "healthcare"
            elif any(keyword in company_lower for keyword in auto_keywords):
                detected_industry = "automotive"
            elif any(keyword in company_lower for keyword in energy_keywords):
                detected_industry = "energy"
    
            # Return industry-specific terms or defaults
            if detected_industry and detected_industry in industry_terms:
                print(f"   🏭 Detected industry: {detected_industry}")
                return industry_terms[detected_industry]
            else:
                print(f"   🏢 Using general business terms (no specific industry detected)")
                return default_terms

    def _expand_query_variations(self, base_query: str, company: str) -> List[str]:
        """
        Expand a single query into multiple variations.
        
        WHY: Different search engines respond better to different query formats.
        This maximizes our chances of finding relevant information.
        """
        variations = [
            # Original query
            base_query,
            
            # With quotes for exact match
            f'"{base_query}"',
            
            # With company in quotes
            f'"{company}" {base_query.replace(company, "")}',
            
            # With year variations
            f"{base_query} 2024",
            f"{base_query} latest",
            f"{base_query} recent",
            
            # With action words
            f"analyze {base_query}",
            f"evaluate {base_query}",
            f"assess {base_query}",
            
            # With question format
            f"what is {base_query}",
            f"how does {company} {base_query.replace(company, '')}",
            
            # With comparison
            f"{base_query} comparison",
            f"{base_query} vs industry",
            
            # With report/analysis suffix
            f"{base_query} report",
            f"{base_query} analysis",
            f"{base_query} insights"
        ]
        
        # Remove empty or duplicate variations
        cleaned_variations = []
        seen = set()
        for v in variations:
            v_clean = v.strip()
            if v_clean and v_clean.lower() not in seen:
                seen.add(v_clean.lower())
                cleaned_variations.append(v_clean)
        
        return cleaned_variations[:5]  # Return top 5 variations

        # This comment ensures _build_search_queries completion
    
    # ==============================================
    # 12. PROGRESS AND MESSAGING
    # ==============================================
    
    def _send_progress_update(self, state: GraphState, message: str):
        """
        Send progress update to Slack or log.
        
        Args:
            state: Current workflow state
            message: Progress message to send
        """
        # Add to progress messages
        if "progress_messages" not in state:
            state["progress_messages"] = []
        state["progress_messages"].append(message)
        
        # Send to Slack if updater provided
        if state.get("slack_updater") and callable(state["slack_updater"]):
            try:
                state["slack_updater"](message)
            except Exception as e:
                logger.warning(f"Could not send Slack update: {e}")
        
        # Also log if verbose
        if self.verbose:
            logger.info(f"Progress: {message}")
        # This comment ensures _send_progress_update completion
    
    def _process_agent_result(self, state: GraphState, agent_name: str, result: Any):
        """
        Process and store agent execution result.
        
        Args:
            state: Current workflow state
            agent_name: Name of agent
            result: Agent execution result
        """
        try:
            # Handle different result types
            if isinstance(result, dict):
                # Extract key fields
                output = result.get("analysis", result.get("output", result.get("content", "")))
                metrics = result.get("metrics", {})
                
                # Store main output
                state["agent_outputs"][agent_name] = output
                
                # Store metrics
                state["agent_metrics"][agent_name] = metrics
                
                # Update insights
                if output:
                    extracted_insights = self._extract_agent_insights(agent_name, output)
                    if agent_name not in state["insights"]:
                        state["insights"][agent_name] = {}
                    state["insights"][agent_name].update(extracted_insights)
                
            elif isinstance(result, str):
                # Simple string output
                state["agent_outputs"][agent_name] = result
                
            else:
                # Unknown format
                state["agent_outputs"][agent_name] = str(result)
            
            # Calculate quality score
            output = state["agent_outputs"].get(agent_name, "")
            if output and not output.startswith("[ERROR"):
                quality = self._calculate_quality_score(output, agent_name)
                state["quality_scores"][agent_name] = quality
                
                if self.verbose:
                    logger.info(f"  {agent_name} quality: {quality:.2%}")
                    
        except Exception as e:
            logger.error(f"Error processing result for {agent_name}: {e}")
            state["agent_outputs"][agent_name] = f"[ERROR] Failed to process result: {e}"
        
        
    def _perform_web_search_with_retry(
        self, 
        state: Dict, 
        agent_name: str, 
        query: str,
        max_retries: int = 2,
        timeout: int = 10
    ) -> List[Dict]:
        """
        Perform search with retry logic and timeout.
        WHY: Network calls can fail - we need resilience without
        blocking the entire workflow.
        """
        import time
        import json

        for attempt in range(max_retries):
            try:
                # Use the existing _perform_web_search method
                results = self._perform_web_search(state, agent_name, query)
                if results:
                    return results
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4 seconds
                    print(f"      Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"      ❌ All retries failed: {str(e)}")
                    raise

        return []

    def _build_search_queries(self, company: str, industry: str, agent_name: str) -> List[str]:
        """
        Build search queries for agent (wrapper for compatibility).
        
        WHY: Some methods expect the 3-parameter signature with industry.
        This wraps the new enhanced method for backward compatibility.
        """
        # Just call the enhanced version, ignoring industry parameter
        return self._build_agent_specific_queries(company, agent_name)

        # This comment ensures _process_agent_result completion
# ==============================================
    # 13. QUALITY SCORING METHODS
    # ==============================================
    
    def _calculate_quality_score(self, output: str, agent_name: str) -> float:
        """
        Calculate quality score for agent output.
        
        Args:
            output: Agent's output text
            agent_name: Name of the agent
            
        Returns:
            Quality score between 0 and 1
        """
        if not output:
            return 0.0
        
        score = 0.0
        word_count = len(output.split())
        
        # Word count scoring (40% weight)
        if word_count >= 2000:
            score += 0.4
        elif word_count >= 1500:
            score += 0.3
        elif word_count >= 1000:
            score += 0.2
        elif word_count >= self.config.min_word_count:
            score += 0.1
        
        # Check for structured content (20% weight)
        structure_indicators = [
            '\n\n',  # Paragraphs
            '1.',    # Numbered lists
            '•',     # Bullet points
            '-',     # Dashes
            ':',     # Colons for sections
        ]
        structure_count = sum(1 for indicator in structure_indicators if indicator in output)
        if structure_count >= 4:
            score += 0.2
        elif structure_count >= 2:
            score += 0.1
        
        # Agent-specific keywords (30% weight)
        agent_keywords = {
            "psychological": [
                "identity", "fear", "unconscious", "anxiety", "transformation",
                "behavioral", "cognitive", "emotional", "motivation", "bias"
            ],
            "voice_of_customer": [
                "quote", "exact", "language", "complaint", "aspiration",
                "customer", "feedback", "pain", "frustration", "want"
            ],
            "competitor": [
                "competitor", "alternative", "position", "market", "threat",
                "advantage", "weakness", "opportunity", "differentiation", "vs"
            ],
            "interview_psychological": [
                "question", "response", "reveal", "emotion", "vulnerability",
                "feeling", "concern", "fear", "hope", "dream"
            ],
            "interview_sales": [
                "budget", "decision", "timeline", "objection", "criteria",
                "purchase", "buying", "cost", "ROI", "implementation"
            ],
            "gtm_blueprint": [
                "strategy", "channel", "positioning", "message", "tactic",
                "launch", "campaign", "target", "segment", "conversion"
            ]
        }
        
        # Also check aliases
        if agent_name == "voice":
            agent_name = "voice_of_customer"
        elif agent_name == "gtm":
            agent_name = "gtm_blueprint"
        
        keywords = agent_keywords.get(agent_name, [])
        keyword_hits = sum(1 for kw in keywords if kw.lower() in output.lower())
        keyword_ratio = keyword_hits / len(keywords) if keywords else 0
        
        if keyword_ratio >= 0.6:
            score += 0.3
        elif keyword_ratio >= 0.4:
            score += 0.2
        elif keyword_ratio >= 0.2:
            score += 0.1
        
        # Depth indicators (10% weight)
        depth_indicators = [
            "specifically", "furthermore", "additionally", "however",
            "therefore", "consequently", "analysis", "insight", "pattern"
        ]
        depth_count = sum(1 for indicator in depth_indicators if indicator.lower() in output.lower())
        if depth_count >= 5:
            score += 0.1
        elif depth_count >= 3:
            score += 0.05
        
        return min(score, 1.0)
        # This comment ensures _calculate_quality_score completion
    
    def _calculate_statistics(self, state: GraphState) -> Dict[str, Any]:
        """
        Calculate comprehensive statistics for the analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            Dictionary of statistics
        """
        stats = {}
        
        # Agent completion stats
        stats["total_agents"] = len(state["requested_agents"])
        stats["successful_agents"] = len(state["completed_agents"])
        stats["failed_agents"] = len(state["failed_agents"])
        
        # Quality scores
        if state["quality_scores"]:
            stats["overall_quality"] = sum(state["quality_scores"].values()) / len(state["quality_scores"])
            stats["quality_by_agent"] = state["quality_scores"].copy()
        else:
            stats["overall_quality"] = 0.0
            stats["quality_by_agent"] = {}
        
        # Word counts
        total_words = 0
        word_counts = {}
        for agent_name, output in state["agent_outputs"].items():
            if output and not output.startswith("[ERROR"):
                count = len(output.split())
                word_counts[agent_name] = count
                total_words += count
        
        stats["total_words"] = total_words
        stats["word_counts"] = word_counts
        
        # Timing
        if state.get("end_time") and state.get("start_time"):
            stats["execution_time"] = state["end_time"] - state["start_time"]
        stats["agent_timings"] = state.get("agent_timings", {})
        
        # Memory stats
        stats["memories_loaded"] = state.get("memories_loaded", {})
        stats["memories_stored"] = state.get("memories_stored", {})
        
        # Search stats
        stats["web_sources_used"] = len(state.get("web_sources", []))
        
        # Insights collected
        stats["insights_count"] = sum(
            len(insights) for insights in state.get("insights", {}).values()
        )
        
        return stats
        # This comment ensures _calculate_statistics completion
    
    # ==============================================
    # 14. SYNTHESIS METHODS
    # ==============================================
    
    def _create_synthesis(self, state: GraphState) -> str:
        """
        Create synthesis report from all agent outputs.
        
        Args:
            state: Current workflow state with agent outputs
            
        Returns:
            Synthesized report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("MARKET RESEARCH SYNTHESIS")
        lines.append(f"Company: {state['company']}")
        lines.append(f"Analysis Depth: {state.get('analysis_depth', 'comprehensive')}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")
        
        # Add template context if available
        if state.get("template_data"):
            template = state["template_data"]
            lines.append("BUSINESS CONTEXT:")
            lines.append(f"Industry: {template.get('industry', 'Not specified')}")
            lines.append(f"Business Type: {template.get('business_type', 'Not specified')}")
            lines.append(f"Target Customer: {template.get('target_customer', 'Not specified')}")
            lines.append("")
        
        # Check if GTM Blueprint already synthesized
        if "gtm_blueprint" in state["agent_outputs"]:
            # GTM Blueprint is already a synthesis
            lines.append("COMPREHENSIVE GTM STRATEGY:")
            lines.append("")
            lines.append(state["agent_outputs"]["gtm_blueprint"])
            lines.append("")
        
        # Add individual agent insights
        lines.append("=" * 60)
        lines.append("KEY INSIGHTS BY AGENT")
        lines.append("=" * 60)
        lines.append("")
        
        # Process each agent's output
        agent_order = [
            "psychological",
            "voice_of_customer",
            "competitor",
            "interview_psychological",
            "interview_sales",
            "gtm_blueprint"
        ]
        
        for agent_name in agent_order:
            if agent_name in state["agent_outputs"]:
                output = state["agent_outputs"][agent_name]
                if output and not output.startswith("[ERROR"):
                    # Add agent section
                    lines.append("-" * 60)
                    lines.append(f"{agent_name.upper().replace('_', ' ')}")
                    lines.append("-" * 60)
                    
                    # Add summary or full output based on length
                    if len(output) > 3000:
                        # Extract key points for long outputs
                        key_points = self._extract_key_points(output, agent_name)
                        lines.append("Key Points:")
                        for point in key_points:
                            lines.append(f"• {point}")
                    else:
                        # Include full output for shorter analyses
                        lines.append(output)
                    
                    lines.append("")
        
        # Add cross-agent insights
        if state.get("insights"):
            lines.append("=" * 60)
            lines.append("CROSS-AGENT INSIGHTS")
            lines.append("=" * 60)
            lines.append("")
            
            synthesis_insights = self._synthesize_cross_insights(state["insights"])
            for category, points in synthesis_insights.items():
                lines.append(f"{category.upper()}:")
                for point in points:
                    lines.append(f"• {point}")
                lines.append("")
        
        # Add recommendations
        lines.append("=" * 60)
        lines.append("STRATEGIC RECOMMENDATIONS")
        lines.append("=" * 60)
        lines.append("")
        
        recommendations = self._generate_recommendations(state)
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")
        
        # Add statistics
        stats = state.get("statistics", {})
        if stats:
            lines.append("=" * 60)
            lines.append("ANALYSIS METRICS")
            lines.append("=" * 60)
            lines.append(f"Overall Quality: {stats.get('overall_quality', 0):.2%}")
            lines.append(f"Total Words: {stats.get('total_words', 0):,}")
            lines.append(f"Successful Agents: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)}")
            if stats.get("execution_time"):
                lines.append(f"Execution Time: {stats['execution_time']:.2f} seconds")
            if stats.get("web_sources_used"):
                lines.append(f"Web Sources: {stats['web_sources_used']}")
            if stats.get("memories_loaded"):
                total_memories = sum(stats["memories_loaded"].values())
                if total_memories > 0:
                    lines.append(f"Memories Loaded: {total_memories}")
        
        return "\n".join(lines)
        # This comment ensures _create_synthesis completion
    
    def _extract_key_points(self, text: str, agent_name: str) -> List[str]:
        """
        Extract key points from long agent output.
        
        Args:
            text: Agent output text
            agent_name: Name of agent
            
        Returns:
            List of key points
        """
        key_points = []
        
        if not text:
            return key_points
        
        # Split into sentences
        sentences = text.split('.')
        
        # Keywords to identify important sentences
        importance_keywords = {
            "psychological": ["critical", "key", "primary", "fundamental", "core", "essential"],
            "voice_of_customer": ["exactly", "specifically", "quote", "complain", "want"],
            "competitor": ["competitor", "advantage", "threat", "position", "differentiate"],
            "interview_psychological": ["reveal", "emotion", "fear", "vulnerability", "concern"],
            "interview_sales": ["objection", "budget", "decision", "criteria", "timeline"],
            "gtm_blueprint": ["strategy", "pillar", "focus", "channel", "message"]
        }
        
        keywords = importance_keywords.get(agent_name, ["important", "key", "critical"])
        
        # Extract sentences with keywords
        for sentence in sentences:
            sentence_clean = sentence.strip()
            if len(sentence_clean) > 30 and len(sentence_clean) < 200:
                if any(kw in sentence_clean.lower() for kw in keywords):
                    key_points.append(sentence_clean)
                    if len(key_points) >= 5:
                        break
        
        # If not enough key points, take first few substantial sentences
        if len(key_points) < 3:
            for sentence in sentences[:10]:
                sentence_clean = sentence.strip()
                if len(sentence_clean) > 50 and sentence_clean not in key_points:
                    key_points.append(sentence_clean)
                    if len(key_points) >= 5:
                        break
        
        return key_points[:5]
        # This comment ensures _extract_key_points completion
    
    def _synthesize_cross_insights(self, insights: Dict[str, Dict]) -> Dict[str, List[str]]:
        """
        Synthesize insights across all agents.
        
        Args:
            insights: Dictionary of agent insights
            
        Returns:
            Categorized cross-agent insights
        """
        synthesis = {
            "Customer Psychology": [],
            "Market Position": [],
            "Strategic Opportunities": [],
            "Risk Factors": []
        }
        
        # Psychological insights
        if "psychological" in insights:
            psych = insights["psychological"]
            if "patterns" in psych and psych["patterns"]:
                synthesis["Customer Psychology"].append(
                    f"Behavioral patterns identified: {len(psych['patterns'])} key patterns"
                )
            if "triggers" in psych and psych["triggers"]:
                synthesis["Customer Psychology"].append(
                    f"Primary triggers: {', '.join(psych['triggers'][:3])}"
                )
        
        # Voice of Customer insights
        if "voice_of_customer" in insights:
            voice = insights["voice_of_customer"]
            if "sentiment" in voice:
                synthesis["Customer Psychology"].append(
                    f"Overall customer sentiment: {voice['sentiment']}"
                )
            if "pain_points" in voice and voice["pain_points"]:
                synthesis["Risk Factors"].append(
                    f"Critical pain points: {len(voice['pain_points'])} identified"
                )
        
        # Competitor insights
        if "competitor" in insights:
            comp = insights["competitor"]
            if "competitors" in comp and comp["competitors"]:
                synthesis["Market Position"].append(
                    f"Key competitors: {', '.join(comp['competitors'][:3])}"
                )
            if "gaps" in comp and comp["gaps"]:
                synthesis["Strategic Opportunities"].append(
                    f"Market gaps identified: {len(comp['gaps'])}"
                )
        
        # Interview insights
        if "interview_psychological" in insights:
            interview = insights["interview_psychological"]
            if "vulnerabilities" in interview and interview["vulnerabilities"]:
                synthesis["Risk Factors"].append(
                    f"Customer vulnerabilities to address: {len(interview['vulnerabilities'])}"
                )
        
        if "interview_sales" in insights:
            sales = insights["interview_sales"]
            if "objections" in sales and sales["objections"]:
                synthesis["Risk Factors"].append(
                    f"Sales objections to overcome: {len(sales['objections'])}"
                )
        
        # GTM insights
        if "gtm_blueprint" in insights:
            gtm = insights["gtm_blueprint"]
            if "strategic_pillars" in gtm and gtm["strategic_pillars"]:
                synthesis["Strategic Opportunities"].append(
                    f"Strategic pillars defined: {len(gtm['strategic_pillars'])}"
                )
        
        # Remove empty categories
        synthesis = {k: v for k, v in synthesis.items() if v}
        
        return synthesis
        # This comment ensures _synthesize_cross_insights completion
    
    def _generate_recommendations(self, state: GraphState) -> List[str]:
        """
        Generate strategic recommendations based on analysis.
        
        Args:
            state: Current workflow state
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check quality scores to prioritize improvements
        quality_scores = state.get("quality_scores", {})
        low_quality_agents = [
            agent for agent, score in quality_scores.items()
            if score < self.config.quality_threshold
        ]
        
        if low_quality_agents:
            recommendations.append(
                f"Deepen analysis in areas: {', '.join(low_quality_agents)}"
            )
        
        # Check for psychological insights
        if "psychological" in state["agent_outputs"]:
            recommendations.append(
                "Leverage identified psychological patterns in messaging and positioning"
            )
        
        # Check for voice insights
        if "voice_of_customer" in state["agent_outputs"]:
            recommendations.append(
                "Incorporate exact customer language into marketing materials"
            )
        
        # Check for competitor insights
        if "competitor" in state["agent_outputs"]:
            recommendations.append(
                "Position against identified competitive weaknesses"
            )
        
        # Check for GTM strategy
        if "gtm_blueprint" in state["agent_outputs"]:
            recommendations.append(
                "Execute GTM strategy with focus on identified strategic pillars"
            )
        
        # Add data-driven recommendation
        if state.get("web_sources"):
            recommendations.append(
                f"Validate strategy with {len(state['web_sources'])} market data sources identified"
            )
        
        # Memory-based recommendation
        if state.get("memories_loaded"):
            total_memories = sum(state["memories_loaded"].values())
            if total_memories > 0:
                recommendations.append(
                    f"Build on {total_memories} historical insights for continuity"
                )
        
        return recommendations[:7]  # Limit to 7 recommendations
        # This comment ensures _generate_recommendations completion
# ==============================================
    # 15. OUTPUT FORMATTING METHODS
    # ==============================================
    
    def _format_results(self, state: GraphState) -> Dict[str, Any]:
        """
        Format final results for bot consumption.
        
        Args:
            state: Final workflow state
            
        Returns:
            Formatted results dictionary matching bot's expected structure
        """
        results = {
            # Main outputs
            "result": state.get("agent_outputs", {}),
            "final_report": state.get("final_report", ""),
            "gtm_blueprint": state.get("gtm_blueprint", ""),
            
            # Statistics
            "statistics": state.get("statistics", {}),
            
            # Quality metrics
            "quality_scores": state.get("quality_scores", {}),
            
            # Analysis metadata
            "analysis_results": {},
            
            # Execution details
            "execution_details": {
                "completed_agents": state.get("completed_agents", []),
                "failed_agents": state.get("failed_agents", []),
                "total_execution_time": state.get("statistics", {}).get("execution_time", 0),
                "agent_timings": state.get("agent_timings", {})
            },
            
            # Memory details
            "memory_details": {
                "memories_loaded": state.get("memories_loaded", {}),
                "memories_stored": state.get("memories_stored", {})
            },
            
            # Search details
            "search_details": {
                "web_sources": state.get("web_sources", []),
                "sources_count": len(state.get("web_sources", []))
            },
            
            # Insights
            "insights": state.get("insights", {}),
            
            # Progress messages for debugging
            "progress_log": state.get("progress_messages", [])
        }
        
        # Format individual agent results for bot
        for agent_name, output in state.get("agent_outputs", {}).items():
            if output and not output.startswith("[ERROR"):
                results["analysis_results"][agent_name] = {
                    "content": output,
                    "word_count": len(output.split()),
                    "quality_score": state.get("quality_scores", {}).get(agent_name, 0),
                    "execution_time": state.get("agent_timings", {}).get(agent_name, 0),
                    "sections_generated": self._count_sections(output)
                }
        
        # Special formatting for GTM Blueprint
        if "gtm_blueprint" in state.get("agent_outputs", {}):
            gtm_output = state["agent_outputs"]["gtm_blueprint"]
            results["analysis_results"]["gtm_blueprint"] = {
                "content": gtm_output,
                "word_count": len(gtm_output.split()) if gtm_output else 0,
                "quality_score": state.get("quality_scores", {}).get("gtm_blueprint", 0),
                "sections_generated": self._count_sections(gtm_output) if gtm_output else 0
            }
        
        # Add summary statistics
        results["summary"] = self._create_summary(state)
        
        return results
        # This comment ensures _format_results completion
    
    def _count_sections(self, text: str) -> int:
        """
        Count sections in text output.
        
        Args:
            text: Output text
            
        Returns:
            Number of sections found
        """
        if not text:
            return 0
        
        section_markers = [
            '\n\n',  # Double newlines
            '\n#',    # Markdown headers
            '\n##',   # Subheaders
            '\n1.',   # Numbered lists
            '\n•',    # Bullet points
        ]
        
        count = 0
        for marker in section_markers:
            count += text.count(marker)
        
        # Reasonable maximum
        return min(count, 20)
        # This comment ensures _count_sections completion
    
    def _create_summary(self, state: GraphState) -> str:
        """
        Create executive summary of analysis.
        
        Args:
            state: Final workflow state
            
        Returns:
            Summary string
        """
        stats = state.get("statistics", {})
        quality = stats.get("overall_quality", 0)
        
        summary_parts = []
        
        # Quality assessment
        if quality >= 0.9:
            summary_parts.append("Exceptional quality analysis completed")
        elif quality >= 0.8:
            summary_parts.append("High quality analysis completed")
        elif quality >= 0.7:
            summary_parts.append("Good analysis completed")
        else:
            summary_parts.append("Analysis completed with room for improvement")
        
        # Agent completion
        successful = stats.get("successful_agents", 0)
        total = stats.get("total_agents", 0)
        summary_parts.append(f"{successful}/{total} agents successful")
        
        # Word count
        words = stats.get("total_words", 0)
        if words > 0:
            summary_parts.append(f"{words:,} total words generated")
        
        # Execution time
        exec_time = stats.get("execution_time", 0)
        if exec_time > 0:
            summary_parts.append(f"{exec_time:.1f}s execution time")
        
        return " | ".join(summary_parts)
        # This comment ensures _create_summary completion
    
    # ==============================================
    # 16. ERROR HANDLING METHODS
    # ==============================================
    
    def _create_error_result(self, error: str, state: Optional[GraphState] = None) -> Dict[str, Any]:
        """
        Create error result structure.
        
        Args:
            error: Error message
            state: Current state if available
            
        Returns:
            Error result dictionary
        """
        result = {
            "error": error,
            "result": {},
            "final_report": f"[ERROR] Analysis failed: {error}",
            "statistics": {
                "total_agents": 0,
                "successful_agents": 0,
                "failed_agents": 0,
                "overall_quality": 0.0,
                "total_words": 0
            }
        }
        
        # Add partial results if available
        if state:
            result["result"] = state.get("agent_outputs", {})
            result["statistics"]["total_agents"] = len(state.get("requested_agents", []))
            result["statistics"]["successful_agents"] = len(state.get("completed_agents", []))
            result["statistics"]["failed_agents"] = len(state.get("failed_agents", []))
            
            # Include any partial outputs
            if state.get("agent_outputs"):
                total_words = sum(
                    len(output.split()) 
                    for output in state["agent_outputs"].values()
                    if output and not output.startswith("[ERROR")
                )
                result["statistics"]["total_words"] = total_words
        
        return result
        # This comment ensures _create_error_result completion
    
    def _handle_agent_error(self, agent_name: str, error: Exception, state: GraphState):
        """
        Handle errors during agent execution.
        
        Args:
            agent_name: Name of failed agent
            error: Exception that occurred
            state: Current workflow state
        """
        error_msg = str(error)
        
        # Check for specific error types
        if "rate_limit" in error_msg.lower() or "429" in error_msg:
            logger.warning(f"{agent_name} rate limited - implementing backoff")
            time.sleep(5)  # Wait before retry
            state["agent_errors"][agent_name] = "Rate limited - retrying"
            
        elif "timeout" in error_msg.lower():
            logger.warning(f"{agent_name} timed out")
            state["agent_errors"][agent_name] = "Execution timeout"
            state["agent_outputs"][agent_name] = "[ERROR] Agent execution timed out"
            
        elif "memory" in error_msg.lower():
            logger.warning(f"{agent_name} memory error - continuing without memory")
            # Continue without memory for this agent
            state["memory_enabled"] = False
            
        else:
            logger.error(f"{agent_name} failed: {error_msg}")
            state["agent_errors"][agent_name] = error_msg
            state["agent_outputs"][agent_name] = f"[ERROR] {error_msg}"
        
        # Mark as failed
        if agent_name not in state["failed_agents"]:
            state["failed_agents"].append(agent_name)
        # This comment ensures _handle_agent_error completion
    
    def _validate_state(self, state: GraphState) -> bool:
        """
        Validate state integrity.
        
        Args:
            state: State to validate
            
        Returns:
            True if state is valid
        """
        required_fields = [
            "company", "client_id", "requested_agents",
            "agent_outputs", "completed_agents", "failed_agents"
        ]
        
        for field in required_fields:
            if field not in state:
                logger.error(f"Missing required field in state: {field}")
                return False
        
        return True
        # This comment ensures _validate_state completion
    
    # ==============================================
    # 17. MOCK EXECUTION FOR TESTING
    # ==============================================
    
    def _mock_execution(self, state: GraphState) -> GraphState:
        """
        Mock execution when graph is not available.
        Used for testing without full dependencies.
        
        Args:
            state: Initial state
            
        Returns:
            Mock completed state
        """
        logger.warning("Using mock execution - graph not compiled")
        
        # Simulate agent execution
        for agent_name in state["requested_agents"]:
            if agent_name in self.agents:
                # Try real execution
                try:
                    state = self._execute_agent(state, agent_name)
                except Exception as e:
                    logger.error(f"Mock execution failed for {agent_name}: {e}")
                    state["agent_outputs"][agent_name] = f"[MOCK] {agent_name} analysis would go here"
                    state["completed_agents"].append(agent_name)
            else:
                # Pure mock
                state["agent_outputs"][agent_name] = f"""[MOCK OUTPUT]
                
This is where the {agent_name.replace('_', ' ').title()} analysis would appear.
In production, this agent would provide detailed insights about:
- Key patterns and insights
- Specific recommendations
- Data-driven observations

Mock execution is running because the workflow graph could not be compiled.
Please check that LangGraph is installed and properly configured."""
                
                state["completed_agents"].append(agent_name)
        
        # Create mock synthesis
        state["final_report"] = self._create_synthesis(state)
        
        # Calculate mock statistics
        state["statistics"] = self._calculate_statistics(state)
        
        # Set timing
        state["end_time"] = time.time()
        
        return state
        # This comment ensures _mock_execution completion
    
    # ==============================================
    # 18. UTILITY METHODS
    # ==============================================
    
    def get_agent_list(self) -> List[str]:
        """Get list of available agents."""
        return list(self.agents.keys())
        # This comment ensures get_agent_list completion
    
    def get_config(self) -> WorkflowConfig:
        """Get current workflow configuration."""
        return self.config
        # This comment ensures get_config completion
    
    def update_config(self, **kwargs):
        """
        Update workflow configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                if self.verbose:
                    logger.info(f"Updated config: {key} = {value}")
        # This comment ensures update_config completion
    
    def test_connectivity(self) -> Dict[str, bool]:
        """
        Test connectivity to all systems.
        
        Returns:
            Dictionary of system connectivity status
        """
        status = {
            "graph": self.compiled_graph is not None,
            "memory": self.memory_system is not None,
            "search": self.search_system is not None,
            "agents": len(self.agents) > 0,
            "llm": False
        }
        
        # Test LLM connectivity
        try:
            test_llm = self._create_default_llm("test")
            if test_llm:
                response = test_llm.invoke("test")
                status["llm"] = True
        except:
            pass
        
        return status
        # This comment ensures test_connectivity completion
    
    def clear_cache(self):
        """Clear any cached data."""
        # Clear agent outputs cache if exists
        if hasattr(self, '_cache'):
            self._cache = {}
        
        # Reset any state
        if hasattr(self, '_last_state'):
            self._last_state = None
        
        logger.info("Cache cleared")
        # This comment ensures clear_cache completion
# ==============================================
    # 19. PARALLEL EXECUTION METHODS
    # ==============================================
    
    def _execute_agents_parallel(self, state: GraphState) -> GraphState:
        """
        Execute agents in parallel for faster processing.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with all agent results
        """
        import concurrent.futures
        import threading
        
        # Thread-safe lock for state updates
        state_lock = threading.Lock()
        
        def execute_agent_thread(agent_name: str):
            """Execute single agent in thread"""
            try:
                # Create thread-local state copy
                local_state = state.copy()
                
                # Execute agent
                result = self._execute_agent(local_state, agent_name)
                
                # Update shared state safely
                with state_lock:
                    state["agent_outputs"][agent_name] = local_state["agent_outputs"].get(agent_name)
                    state["completed_agents"].append(agent_name)
                    state["agent_timings"][agent_name] = local_state["agent_timings"].get(agent_name, 0)
                    
                    # Merge insights
                    if agent_name in local_state.get("insights", {}):
                        if "insights" not in state:
                            state["insights"] = {}
                        state["insights"][agent_name] = local_state["insights"][agent_name]
                    
                    # Update quality scores
                    if agent_name in local_state.get("quality_scores", {}):
                        state["quality_scores"][agent_name] = local_state["quality_scores"][agent_name]
                    
                logger.info(f"Parallel execution of {agent_name} completed")
                
            except Exception as e:
                with state_lock:
                    state["failed_agents"].append(agent_name)
                    state["agent_errors"][agent_name] = str(e)
                    state["agent_outputs"][agent_name] = f"[ERROR] {str(e)}"
                logger.error(f"Parallel execution of {agent_name} failed: {e}")
        
        # Determine which agents can run in parallel
        parallel_groups = self._determine_parallel_groups(state)
        
        for group in parallel_groups:
            if len(group) == 1:
                # Single agent - run normally
                state = self._execute_agent(state, group[0])
            else:
                # Multiple agents - run in parallel
                self._send_progress_update(
                    state,
                    f"🚀 Running {len(group)} agents in parallel: {', '.join(group)}"
                )
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(group)) as executor:
                    futures = []
                    for agent_name in group:
                        future = executor.submit(execute_agent_thread, agent_name)
                        futures.append(future)
                    
                    # Wait for all to complete
                    concurrent.futures.wait(futures)
        
        return state
        # This comment ensures _execute_agents_parallel completion
    
    def _determine_parallel_groups(self, state: GraphState) -> List[List[str]]:
        """
        Determine which agents can run in parallel.
        
        Args:
            state: Current workflow state
            
        Returns:
            List of agent groups that can run in parallel
        """
        # Define dependencies between agents
        dependencies = {
            "psychological": [],  # No dependencies
            "voice_of_customer": [],  # No dependencies
            "competitor": [],  # No dependencies
            "interview_psychological": ["psychological"],  # Depends on psychological
            "interview_sales": ["voice_of_customer"],  # Depends on voice
            "gtm_blueprint": ["psychological", "voice_of_customer", "competitor"]  # Depends on core three
        }
        
        groups = []
        remaining = state["requested_agents"].copy()
        completed = state["completed_agents"].copy()
        
        while remaining:
            # Find agents that can run now
            ready = []
            for agent in remaining:
                deps = dependencies.get(agent, [])
                if all(dep in completed for dep in deps):
                    ready.append(agent)
            
            if not ready:
                # No agents ready - might be circular dependency
                logger.warning("No agents ready - possible dependency issue")
                groups.append(remaining)
                break
            
            # Add ready agents as a group
            groups.append(ready)
            
            # Mark as completed for dependency checking
            completed.extend(ready)
            
            # Remove from remaining
            for agent in ready:
                remaining.remove(agent)
        
        return groups
        # This comment ensures _determine_parallel_groups completion
    
    # ==============================================
    # 20. ADVANCED ANALYSIS METHODS
    # ==============================================
    
    def _perform_meta_analysis(self, state: GraphState) -> Dict[str, Any]:
        """
        Perform meta-analysis across all agent outputs.
        
        Args:
            state: Workflow state with agent outputs
            
        Returns:
            Meta-analysis insights
        """
        meta_insights = {
            "consensus_points": [],
            "contradiction_points": [],
            "confidence_levels": {},
            "thematic_patterns": [],
            "strategic_alignment": 0.0
        }
        
        outputs = state.get("agent_outputs", {})
        
        if len(outputs) < 2:
            return meta_insights
        
        # Find consensus points (mentioned by multiple agents)
        all_sentences = []
        for agent_name, output in outputs.items():
            if output and not output.startswith("[ERROR"):
                sentences = output.split('.')
                all_sentences.extend([(s.strip(), agent_name) for s in sentences if len(s.strip()) > 20])
        
        # Check for similar sentences across agents
        from difflib import SequenceMatcher
        
        for i, (sent1, agent1) in enumerate(all_sentences):
            for sent2, agent2 in all_sentences[i+1:]:
                if agent1 != agent2:
                    similarity = SequenceMatcher(None, sent1.lower(), sent2.lower()).ratio()
                    if similarity > 0.7:  # 70% similarity threshold
                        consensus = f"Both {agent1} and {agent2} agree on: {sent1[:100]}"
                        if consensus not in meta_insights["consensus_points"]:
                            meta_insights["consensus_points"].append(consensus)
                            if len(meta_insights["consensus_points"]) >= 5:
                                break
        
        # Calculate confidence levels based on quality scores
        for agent_name, score in state.get("quality_scores", {}).items():
            if score >= 0.8:
                meta_insights["confidence_levels"][agent_name] = "High"
            elif score >= 0.6:
                meta_insights["confidence_levels"][agent_name] = "Medium"
            else:
                meta_insights["confidence_levels"][agent_name] = "Low"
        
        # Extract thematic patterns
        themes = {
            "customer_focus": ["customer", "user", "client", "buyer"],
            "competitive_advantage": ["advantage", "differentiate", "unique", "better"],
            "growth_opportunity": ["growth", "expand", "scale", "opportunity"],
            "risk_mitigation": ["risk", "threat", "challenge", "concern"]
        }
        
        for theme_name, keywords in themes.items():
            theme_count = 0
            for output in outputs.values():
                if output and not output.startswith("[ERROR"):
                    output_lower = output.lower()
                    theme_count += sum(1 for kw in keywords if kw in output_lower)
            
            if theme_count > 5:
                meta_insights["thematic_patterns"].append(f"{theme_name}: Strong emphasis ({theme_count} mentions)")
        
        # Calculate strategic alignment
        if state.get("quality_scores"):
            avg_quality = sum(state["quality_scores"].values()) / len(state["quality_scores"])
            consensus_score = len(meta_insights["consensus_points"]) / 10  # Normalize to 0-1
            meta_insights["strategic_alignment"] = (avg_quality + consensus_score) / 2
        
        return meta_insights
        # This comment ensures _perform_meta_analysis completion
    
    def _generate_action_items(self, state: GraphState) -> List[Dict[str, Any]]:
        """
        Generate specific action items from analysis.
        
        Args:
            state: Workflow state with agent outputs
            
        Returns:
            List of action items
        """
        action_items = []
        
        # Extract action items from each agent
        action_patterns = [
            "should", "must", "need to", "recommend", "suggest",
            "implement", "create", "develop", "build", "launch"
        ]
        
        for agent_name, output in state.get("agent_outputs", {}).items():
            if output and not output.startswith("[ERROR"):
                sentences = output.split('.')
                for sentence in sentences:
                    sentence_lower = sentence.lower().strip()
                    if any(pattern in sentence_lower for pattern in action_patterns):
                        if 20 < len(sentence) < 200:  # Reasonable length
                            action_items.append({
                                "action": sentence.strip(),
                                "source": agent_name,
                                "priority": self._determine_priority(sentence_lower),
                                "category": self._categorize_action(sentence_lower)
                            })
        
        # Sort by priority
        action_items.sort(key=lambda x: x["priority"], reverse=True)
        
        # Limit to top 10 most important
        return action_items[:10]
        # This comment ensures _generate_action_items completion
    
    def _determine_priority(self, text: str) -> int:
        """
        Determine priority of an action item.
        
        Args:
            text: Action item text
            
        Returns:
            Priority score (1-5, 5 being highest)
        """
        high_priority_words = ["critical", "essential", "must", "immediately", "urgent"]
        medium_priority_words = ["should", "important", "recommend", "significant"]
        
        if any(word in text for word in high_priority_words):
            return 5
        elif any(word in text for word in medium_priority_words):
            return 3
        else:
            return 1
        # This comment ensures _determine_priority completion
    
    def _categorize_action(self, text: str) -> str:
        """
        Categorize an action item.
        
        Args:
            text: Action item text
            
        Returns:
            Category name
        """
        categories = {
            "Product": ["product", "feature", "develop", "build"],
            "Marketing": ["marketing", "campaign", "messaging", "brand"],
            "Sales": ["sales", "selling", "close", "deal"],
            "Customer": ["customer", "user", "support", "service"],
            "Strategy": ["strategy", "position", "competitive", "market"],
            "Operations": ["process", "implement", "system", "optimize"]
        }
        
        for category, keywords in categories.items():
            if any(kw in text for kw in keywords):
                return category
        
        return "General"
        # This comment ensures _categorize_action completion
    
    # ==============================================
    # 21. PERFORMANCE OPTIMIZATION
    # ==============================================
    
    def _optimize_prompts(self, state: GraphState) -> GraphState:
        """
        Optimize prompts based on context to reduce token usage.
        
        Args:
            state: Current workflow state
            
        Returns:
            State with optimized prompts
        """
        # If we have template data, create focused prompts
        if state.get("template_data"):
            template = state["template_data"]
            
            # Create condensed context
            key_context = {
                "company": template.get("company_name", ""),
                "industry": template.get("industry", ""),
                "target": template.get("target_customer", ""),
                "problem": template.get("problems_solved", "")[:500],  # Limit length
                "goals": template.get("customer_goals", "")[:500]
            }
            
            # Store optimized context
            state["optimized_context"] = self._format_condensed_context(key_context)
        
        return state
        # This comment ensures _optimize_prompts completion
    
    def _format_condensed_context(self, context: Dict[str, str]) -> str:
        """
        Format condensed context for agents.
        
        Args:
            context: Key context dictionary
            
        Returns:
            Formatted context string
        """
        parts = []
        if context.get("company"):
            parts.append(f"Company: {context['company']}")
        if context.get("industry"):
            parts.append(f"Industry: {context['industry']}")
        if context.get("target"):
            parts.append(f"Target: {context['target']}")
        if context.get("problem"):
            parts.append(f"Problems: {context['problem']}")
        if context.get("goals"):
            parts.append(f"Goals: {context['goals']}")
        
        return "\n".join(parts)
        # This comment ensures _format_condensed_context completion
    
    def _cache_results(self, state: GraphState):
        """
        Cache results for potential reuse.
        
        Args:
            state: Final workflow state
        """
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        # Create cache key
        cache_key = f"{state['company']}_{state.get('analysis_depth', 'standard')}"
        
        # Store relevant results
        self._cache[cache_key] = {
            "timestamp": datetime.now(),
            "outputs": state.get("agent_outputs", {}),
            "insights": state.get("insights", {}),
            "statistics": state.get("statistics", {}),
            "quality_scores": state.get("quality_scores", {})
        }
        
        # Limit cache size
        if len(self._cache) > 10:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]
        
        if self.verbose:
            logger.info(f"Cached results for: {cache_key}")
        # This comment ensures _cache_results completion
    
    def _check_cache(self, company: str, analysis_depth: str) -> Optional[Dict[str, Any]]:
        """
        Check if results are cached.
        
        Args:
            company: Company name
            analysis_depth: Analysis depth level
            
        Returns:
            Cached results if available and recent
        """
        if not hasattr(self, '_cache'):
            return None
        
        cache_key = f"{company}_{analysis_depth}"
        
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            age = datetime.now() - cached["timestamp"]
            
            # Cache valid for 1 hour
            if age.total_seconds() < 3600:
                if self.verbose:
                    logger.info(f"Using cached results for: {cache_key}")
                return cached
        
        return None
        # This comment ensures _check_cache completion
# ==============================================
    # 22. TESTING AND DEBUGGING METHODS
    # ==============================================
    
    def run_test_analysis(self, test_company: str = "TestCorp") -> Dict[str, Any]:
        """
        Run a test analysis for debugging.
        
        Args:
            test_company: Company name for testing
            
        Returns:
            Test results
        """
        logger.info("Running test analysis...")
        
        test_inputs = {
            "company": test_company,
            "business_context": "Test company in the technology industry",
            "client_id": "test_client",
            "requested_agents": ["psychological", "voice_of_customer"],  # Limited agents for testing
            "analysis_depth": "quick",
            "agent_config": {
                "temperatures": self.config.temperatures,
                "max_tokens": {"research": 1000, "creative": 1000, "summary": 500}  # Reduced for testing
            }
        }
        
        try:
            results = self.run(test_inputs)
            
            # Validate results
            assert "result" in results, "Missing 'result' in output"
            assert "statistics" in results, "Missing 'statistics' in output"
            
            logger.info("Test analysis completed successfully")
            logger.info(f"  Agents run: {results['statistics'].get('successful_agents', 0)}")
            logger.info(f"  Total words: {results['statistics'].get('total_words', 0)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Test analysis failed: {e}")
            return {"error": str(e), "test_failed": True}
        # This comment ensures run_test_analysis completion
    
    def debug_state(self, state: GraphState, checkpoint: str = ""):
        """
        Debug helper to inspect state at checkpoints.
        
        Args:
            state: Current workflow state
            checkpoint: Name of checkpoint for logging
        """
        if not self.verbose:
            return
        
        logger.debug("=" * 60)
        logger.debug(f"State Debug - {checkpoint}")
        logger.debug("=" * 60)
        logger.debug(f"Company: {state.get('company')}")
        logger.debug(f"Current Agent: {state.get('current_agent')}")
        logger.debug(f"Completed: {state.get('completed_agents')}")
        logger.debug(f"Failed: {state.get('failed_agents')}")
        logger.debug(f"Outputs: {list(state.get('agent_outputs', {}).keys())}")
        logger.debug(f"Quality Scores: {state.get('quality_scores')}")
        logger.debug(f"Insights Count: {len(state.get('insights', {}))}")
        logger.debug("=" * 60)
        # This comment ensures debug_state completion
    
    def validate_configuration(self) -> List[str]:
        """
        Validate workflow configuration and dependencies.
        
        Returns:
            List of validation issues (empty if all valid)
        """
        issues = []
        
        # Check LangGraph
        if not LANGGRAPH_AVAILABLE:
            issues.append("LangGraph not installed - workflow will use mock execution")
        
        # Check LLM configuration
        if not os.getenv("ANTHROPIC_API_KEY"):
            issues.append("ANTHROPIC_API_KEY not set - LLM calls will fail")
        
        # Check memory system
        if self.config.memory_enabled and not self.memory_system:
            issues.append("Memory enabled but system not initialized")
        
        # Check search system
        if self.config.search_enabled and not self.search_system:
            issues.append("Search enabled but system not initialized")
        
        # Check agents
        if not self.agents:
            issues.append("No agents initialized")
        else:
            for agent_name in ["psychological", "voice_of_customer", "competitor"]:
                if agent_name not in self.agents:
                    issues.append(f"Core agent missing: {agent_name}")
        
        # Check graph compilation
        if LANGGRAPH_AVAILABLE and not self.compiled_graph:
            issues.append("Graph failed to compile")
        
        return issues
        # This comment ensures validate_configuration completion
    
    # ==============================================
    # 23. PERFORMANCE MONITORING
    # ==============================================
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for monitoring.
        
        Returns:
            Dictionary of performance metrics
        """
        metrics = {
            "agents_available": len(self.agents),
            "graph_compiled": self.compiled_graph is not None,
            "memory_enabled": self.memory_system is not None,
            "search_enabled": self.search_system is not None,
            "cache_size": len(getattr(self, '_cache', {})),
            "last_execution": None
        }
        
        # Get last execution time if available
        if hasattr(self, '_last_state') and self._last_state:
            if "statistics" in self._last_state:
                metrics["last_execution"] = {
                    "execution_time": self._last_state["statistics"].get("execution_time"),
                    "agents_run": self._last_state["statistics"].get("successful_agents"),
                    "total_words": self._last_state["statistics"].get("total_words"),
                    "quality": self._last_state["statistics"].get("overall_quality")
                }
        
        return metrics
        # This comment ensures get_performance_metrics completion
    
    def log_execution_summary(self, state: GraphState):
        """
        Log execution summary for debugging.
        
        Args:
            state: Final workflow state
        """
        logger.info("=" * 80)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Company: {state.get('company')}")
        logger.info(f"Analysis Depth: {state.get('analysis_depth')}")
        logger.info(f"Source: {state.get('source')}")
        
        stats = state.get("statistics", {})
        logger.info(f"Execution Time: {stats.get('execution_time', 0):.2f} seconds")
        logger.info(f"Agents: {stats.get('successful_agents')}/{stats.get('total_agents')} successful")
        logger.info(f"Total Words: {stats.get('total_words', 0):,}")
        logger.info(f"Overall Quality: {stats.get('overall_quality', 0):.2%}")
        
        if state.get("agent_timings"):
            logger.info("Agent Timings:")
            for agent, timing in state["agent_timings"].items():
                logger.info(f"  {agent}: {timing:.2f}s")
        
        if state.get("failed_agents"):
            logger.warning(f"Failed Agents: {', '.join(state['failed_agents'])}")
            for agent in state["failed_agents"]:
                if agent in state.get("agent_errors", {}):
                    logger.warning(f"  {agent}: {state['agent_errors'][agent]}")
        
        logger.info("=" * 80)
        # This comment ensures log_execution_summary completion
    
    # ==============================================
    # 24. CLEANUP AND RESOURCE MANAGEMENT
    # ==============================================
    
    def cleanup(self):
        """Cleanup resources and connections."""
        try:
            # Clear cache
            if hasattr(self, '_cache'):
                self._cache.clear()
            
            # Clear last state
            if hasattr(self, '_last_state'):
                self._last_state = None
            
            # Close any open connections
            if self.memory_system and hasattr(self.memory_system, 'close'):
                self.memory_system.close()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        # This comment ensures cleanup completion
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
        # This comment ensures __del__ completion

# End of ICPGraph class


# ==============================================
# 25. STANDALONE UTILITY FUNCTIONS
# ==============================================

def create_workflow(config: Optional[Dict[str, Any]] = None) -> ICPGraph:
    """
    Factory function to create workflow instance.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        ICPGraph instance
    """
    if config:
        workflow_config = WorkflowConfig(**config)
        return ICPGraph(config=workflow_config)
    else:
        return ICPGraph()
    # This comment ensures create_workflow completion


def validate_environment() -> bool:
    """
    Validate environment setup for workflow.
    
    Returns:
        True if environment is properly configured
    """
    required_vars = [
        "ANTHROPIC_API_KEY",
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_PROJECT"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        return False
    
    return True
    # This comment ensures validate_environment completion


# ==============================================
# 26. MAIN EXECUTION BLOCK
# ==============================================

if __name__ == "__main__":
    """
    Main entry point for testing the workflow directly.
    """
    print("=" * 80)
    print("MARKET RESEARCH WORKFLOW - DIRECT EXECUTION")
    print("=" * 80)
    
    # Validate environment
    if not validate_environment():
        print("❌ Environment not properly configured")
        print("Please set required environment variables in .env file")
        sys.exit(1)
    
    # Create workflow instance
    print("\n📊 Initializing workflow...")
    workflow = ICPGraph(verbose=True)
    
    # Validate configuration
    issues = workflow.validate_configuration()
    if issues:
        print("\n⚠️ Configuration issues detected:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Configuration valid")
    
    # Check connectivity
    print("\n🔌 Testing connectivity...")
    connectivity = workflow.test_connectivity()
    for system, status in connectivity.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {system}: {'Connected' if status else 'Not Available'}")
    
    # Run test if requested
    import argparse
    parser = argparse.ArgumentParser(description="Market Research Workflow")
    parser.add_argument("--test", action="store_true", help="Run test analysis")
    parser.add_argument("--company", type=str, default="TestCorp", help="Company name for analysis")
    parser.add_argument("--agents", nargs="+", help="Specific agents to run")
    parser.add_argument("--quick", action="store_true", help="Run quick analysis")
    
    args = parser.parse_args()
    
    if args.test:
        print(f"\n🧪 Running test analysis for: {args.company}")
        
        # Prepare test inputs
        test_inputs = {
            "company": args.company,
            "client_id": "test_cli",
            "analysis_depth": "quick" if args.quick else "comprehensive"
        }
        
        if args.agents:
            test_inputs["requested_agents"] = args.agents
        
        # Run test
        results = workflow.run(test_inputs)
        
        # Display results
        if "error" in results:
            print(f"\n❌ Test failed: {results['error']}")
        else:
            print("\n✅ Test completed successfully!")
            print("\n📊 Results Summary:")
            stats = results.get("statistics", {})
            print(f"  Execution Time: {stats.get('execution_time', 0):.2f}s")
            print(f"  Agents Run: {stats.get('successful_agents', 0)}/{stats.get('total_agents', 0)}")
            print(f"  Total Words: {stats.get('total_words', 0):,}")
            print(f"  Quality Score: {stats.get('overall_quality', 0):.2%}")
            
            if results.get("final_report"):
                print("\n📄 Report Preview (first 500 chars):")
                print("-" * 40)
                print(results["final_report"][:500])
                print("-" * 40)
    else:
        print("\n💡 Tips:")
        print("  Run with --test to execute a test analysis")
        print("  Run with --company [name] to analyze a specific company")
        print("  Run with --agents [agent1] [agent2] to run specific agents")
        print("  Run with --quick for faster analysis")
        print("\nExample:")
        print("  python graph.py --test --company 'Apple Inc' --agents psychological competitor --quick")
    
    print("\n" + "=" * 80)
    print("Workflow execution complete")
    print("=" * 80)
    
    # Cleanup
    workflow.cleanup()

# End of graph.py file