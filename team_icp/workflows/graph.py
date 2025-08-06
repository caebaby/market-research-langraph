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

# Import agents
from ..agents.psychological import PsychologicalAgent
from ..agents.interview_psychological_v4 import PsychologicalInterviewAgentV4
from ..agents.interview_sales_v4 import SalesInterviewAgentV4  # ADD THIS LINE
from ..agents.voice import VoiceAgent

psychological_agent = PsychologicalAgent()
interview_agent = PsychologicalInterviewAgentV4()
sales_interview_agent = SalesInterviewAgentV4()  # ADD THIS LINE
voice_agent = VoiceAgent()

workflow = StateGraph(ICPState)

def psychological_node(state: ICPState) -> ICPState:
    logger.info("Running psychological agent")
    state["current_task"] = {
        "description": "Analyze psychological patterns",
        "is_high_stakes": False
    }
    updated_state = psychological_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state.setdefault("result", {})["psychological"] = state["current_output"]

    state["current_agent_index"] = state.get("current_agent_index", 0) + 1
    print(f"[PSYCHOLOGICAL] Incremented index to: {state['current_agent_index']}")
    
    return state

def interview_node(state: ICPState) -> ICPState:
    logger.info("Running interview agent")
    state["current_task"] = {
        "description": "Create psychological customer interviews",
        "is_high_stakes": False
    }
    updated_state = interview_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state.setdefault("result", {})["interview"] = state["current_output"]

    # ADD THESE TWO LINES HERE:
    state["current_agent_index"] = state.get("current_agent_index", 0) + 1
    print(f"[INTERVIEW] Incremented index to: {state['current_agent_index']}")
    
    return state

def sales_interview_node(state: ICPState) -> ICPState:
    logger.info("Running sales interview agent")
    state["current_task"] = {
        "description": "Create sales objection interviews",
        "is_high_stakes": False
    }
    updated_state = sales_interview_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state.setdefault("result", {})["sales_interview"] = state["current_output"]
    state["current_agent_index"] = state.get("current_agent_index", 0) + 1
    print(f"[SALES_INTERVIEW] Incremented index to: {state['current_agent_index']}")
    return state

def voice_node(state: ICPState) -> ICPState:
    logger.info("Running voice agent")
    state["current_task"] = {
        "description": "Extract authentic customer language and create copy-ready phrases",
        "is_high_stakes": False
    }
    updated_state = voice_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state.setdefault("result", {})["voice"] = state["current_output"]

    state["current_agent_index"] = state.get("current_agent_index", 0) + 1
    print(f"[VOICE] Incremented index to: {state['current_agent_index']}")
    
    return state

def synthesis_node(state: ICPState) -> ICPState:
    logger.info("Running synthesis")
    state["synthesis_complete"] = True
    if "result" in state and isinstance(state["result"], dict):
        state["final_report"] = state["result"]
    return state

def router_node(state: ICPState) -> ICPState:
    requested = state.get("requested_agents", [])
    print(f"[DEBUG ROUTER NODE] Received requested_agents: {requested}")  # ADD THIS
    logger.info(f"Router: Requested agents: {requested}")
    state.setdefault("result", {})
    state.setdefault("quality", 0.0)
    state.setdefault("shared_insights", {})
    state.setdefault("current_agent_index", 0)
    state["agents_to_run"] = requested
    print(f"[DEBUG ROUTER NODE] Set agents_to_run to: {state['agents_to_run']}")  # AND THIS
    return state

def route_to_next_agent(state: ICPState) -> str:
    requested = state.get("agents_to_run", [])
    current_index = state.get("current_agent_index", 0)
    
    print(f"[ROUTER DEBUG] Called from: {state.get('agent_name', 'unknown')}")
    print(f"[ROUTER DEBUG] Requested agents: {requested}")
    print(f"[ROUTER DEBUG] Current index: {current_index}")
    
    if current_index >= 10:
        logger.warning("Hit safety limit, routing to synthesis")
        return "synthesis"
    
    if current_index < len(requested):
        next_agent = requested[current_index]
        # REMOVE THIS LINE - routing functions can't modify state!
        # state["current_agent_index"] = current_index + 1
        logger.info(f"Routing to: {next_agent} (index: {current_index})")
        return next_agent
    
    logger.info("All agents complete, routing to synthesis")
    return "synthesis"

workflow.add_node("router", router_node)
workflow.add_node("psychological", psychological_node)
workflow.add_node("interview", interview_node)
workflow.add_node("sales_interview", sales_interview_node)  # ADD THIS LINE
workflow.add_node("voice", voice_node)
workflow.add_node("synthesis", synthesis_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_to_next_agent,
    {"psychological": "psychological", "interview": "interview", "sales_interview": "sales_interview", "voice": "voice", "synthesis": "synthesis"}
)

# Each agent goes back to router for next decision
workflow.add_edge("psychological", "router")
workflow.add_edge("interview", "router")
workflow.add_edge("sales_interview", "router")  # ADD THIS LINE
workflow.add_edge("voice", "router")

graph = workflow.compile()

if __name__ == "__main__":
    state = {
        "task": "Test ICP",
        "context": "Testing",
        "business_context": "Tech founders",
        "master_context": "Tech founders",
        "requested_agents": ["interview"],
        "new_data": True,
        "client_id": "test123"
    }
    result = graph.invoke(state)
    print(f"Result: {result.get('result', {})}")
