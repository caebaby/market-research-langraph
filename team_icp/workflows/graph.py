from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class ICPState(Dict):
    task: str
    context: str
    business_context: Optional[str]
    master_context: Optional[str]
    new_data: bool
    result: Optional[Dict[str, Any]]
    current_output: Optional[str]
    quality_score: Optional[float]
    quality: Optional[float]
    
    # Add requested_agents to state
    requested_agents: Optional[List[str]]
    current_agent_index: Optional[int]
    agents_to_run: Optional[List[str]]
    
    # StandardAgentNode fields
    current_task: Optional[Dict[str, Any]]
    client_id: Optional[str]
    shared_insights: Optional[Dict[str, Any]]
    memory_service: Optional[Any]
    tool_executor: Optional[Any]
    
    # HITL fields
    requires_human_review: Optional[bool]
    review_reason: Optional[str]

# Import all agents
from ..agents.psychological_agent import PsychologicalAgent
from ..agents.competitor_agent import CompetitorAgent
from ..agents.voice_agent import VoiceAgent

# Create agent instances
psychological_agent = PsychologicalAgent()
competitor_agent = CompetitorAgent()
voice_agent = VoiceAgent()

# Create workflow
workflow = StateGraph(ICPState)

# Agent node functions
def psychological_node(state: ICPState) -> ICPState:
    """Wrapper to ensure state is properly updated"""
    logger.info("Running psychological agent")
    
    # Call the agent
    updated_state = psychological_agent(state)
    
    # Safe state merging
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    
    # Store output in result
    if "current_output" in state and state["current_output"]:
        state["result"]["psychological"] = state["current_output"]
    
    return state

def competitor_node(state: ICPState) -> ICPState:
    """Wrapper for competitor agent"""
    logger.info("Running competitor agent")
    state["current_task"] = {
        "description": "Analyze competitive landscape and identify positioning opportunities",
        "is_high_stakes": False
    }
    
    # Call the agent
    updated_state = competitor_agent(state)
    
    # Safe state merging
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    
    # Store output in result
    if "current_output" in state and state["current_output"]:
        state["result"]["competitor"] = state["current_output"]
    
    return state

def voice_node(state: ICPState) -> ICPState:
    """Wrapper for voice of customer agent"""
    logger.info("Running voice agent")
    state["current_task"] = {
        "description": "Extract authentic customer language and create copy-ready phrases",
        "is_high_stakes": False
    }
    
    # Call the agent
    updated_state = voice_agent(state)
    
    # Safe state merging
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    
    # Store output in result
    if "current_output" in state and state["current_output"]:
        state["result"]["voice"] = state["current_output"]
    
    return state

def synthesis_node(state: ICPState) -> ICPState:
    """Simple synthesis - combines all results"""
    logger.info("Running synthesis")
    state["synthesis_complete"] = True
    
    if "result" in state and isinstance(state["result"], dict):
        state["final_report"] = state["result"]
    
    return state

# NEW: Router node to handle dynamic agent selection
def router_node(state: ICPState) -> ICPState:
    """Initialize routing based on requested agents"""
    requested = state.get("requested_agents", [])
    logger.info(f"Router: Requested agents: {requested}")
    
    # Initialize shared state
    state.setdefault("result", {})
    state.setdefault("quality", 0.0)
    state.setdefault("shared_insights", {})
    
    # Initialize routing
    state["current_agent_index"] = 0
    state["agents_to_run"] = requested
    
    return state

# NEW: Dynamic routing function
def route_to_next_agent(state: ICPState) -> str:
    """Determine which agent to run next"""
    requested = state.get("agents_to_run", [])
    current_index = state.get("current_agent_index", 0)
    
    if current_index < len(requested):
        next_agent = requested[current_index]
        # Increment for next iteration
        state["current_agent_index"] = current_index + 1
        logger.info(f"Routing to: {next_agent} (index: {current_index})")
        return next_agent
    else:
        logger.info("All agents complete, routing to synthesis")
        return "synthesis"

# Add nodes
workflow.add_node("router", router_node)
workflow.add_node("psychological", psychological_node)
workflow.add_node("competitor", competitor_node)
workflow.add_node("voice", voice_node)
workflow.add_node("synthesis", synthesis_node)

# Set entry point to router
workflow.set_entry_point("router")

# Add dynamic routing from router
workflow.add_conditional_edges(
    "router",
    route_to_next_agent,
    {
        "psychological": "psychological",
        "competitor": "competitor",
        "voice": "voice",
        "synthesis": "synthesis"
    }
)

# After each agent, route back to check what's next
def route_after_agent(state: ICPState) -> str:
    """After each agent, determine next step"""
    return route_to_next_agent(state)

# Add conditional edges for each agent
for agent in ["psychological", "competitor", "voice"]:
    workflow.add_conditional_edges(
        agent,
        route_after_agent,
        {
            "psychological": "psychological",
            "competitor": "competitor",
            "voice": "voice",
            "synthesis": "synthesis"
        }
    )

# Synthesis always goes to END
workflow.add_edge("synthesis", END)

# Compile the graph
graph = workflow.compile()

# Test function
if __name__ == "__main__":
    # Test with proper state structure
    state = {
        "task": "Test ICP",
        "context": "Testing",
        "business_context": "Tech founders",
        "master_context": "Tech founders",
        "requested_agents": ["voice"],  # Test single agent
        "new_data": True,
        "client_id": "test123"
    }
    
    result = graph.invoke(state)
    print(f"Result: {result.get('result', {})}")
