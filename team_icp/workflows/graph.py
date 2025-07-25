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

# Imports fixed for your structure
from team_icp.agents.psychological import PsychologicalAgent
from team_icp.agents.competitor import CompetitorAgent
from team_icp.agents.voice import VoiceAgent

psychological_agent = PsychologicalAgent()
competitor_agent = CompetitorAgent()
voice_agent = VoiceAgent()

workflow = StateGraph(ICPState)

def psychological_node(state: ICPState) -> ICPState:
    logger.info("Running psychological agent")
    updated_state = psychological_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state["result"]["psychological"] = state["current_output"]
    return state

def competitor_node(state: ICPState) -> ICPState:
    logger.info("Running competitor agent")
    state["current_task"] = {"description": "Analyze competitive landscape and identify positioning opportunities", "is_high_stakes": False}
    updated_state = competitor_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state["result"]["competitor"] = state["current_output"]
    return state

def voice_node(state: ICPState) -> ICPState:
    logger.info("Running voice agent")
    state["current_task"] = {"description": "Extract authentic customer language and create copy-ready phrases", "is_high_stakes": False}
    updated_state = voice_agent(state)
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            if key not in state or value is not None:
                state[key] = value
    if "current_output" in state and state["current_output"]:
        state["result"]["voice"] = state["current_output"]
    return state

def synthesis_node(state: ICPState) -> ICPState:
    logger.info("Running synthesis")
    state["synthesis_complete"] = True
    if "result" in state and isinstance(state["result"], dict):
        state["final_report"] = state["result"]
    return state

def router_node(state: ICPState) -> ICPState:
    requested = state.get("requested_agents", [])
    logger.info(f"Router: Requested agents: {requested}")
    state.setdefault("result", {})
    state.setdefault("quality", 0.0)
    state.setdefault("shared_insights", {})
    state["current_agent_index"] = 0
    state["agents_to_run"] = requested
    return state

def route_to_next_agent(state: ICPState) -> str:
    requested = state.get("agents_to_run", [])
    current_index = state.get("current_agent_index", 0)
    if current_index < len(requested):
        next_agent = requested[current_index]
        state["current_agent_index"] = current_index + 1
        logger.info(f"Routing to: {next_agent} (index: {current_index})")
        return next_agent
    else:
        logger.info("All agents complete, routing to synthesis")
        return "synthesis"

workflow.add_node("router", router_node)
workflow.add_node("psychological", psychological_node)
workflow.add_node("competitor", competitor_node)
workflow.add_node("voice", voice_node)
workflow.add_node("synthesis", synthesis_node)

workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_to_next_agent,
    {"psychological": "psychological", "competitor": "competitor", "voice": "voice", "synthesis": "synthesis"}
)

def route_after_agent(state: ICPState) -> str:
    return route_to_next_agent(state)

for agent in ["psychological", "competitor", "voice"]:
    workflow.add_conditional_edges(
        agent,
        route_after_agent,
        {"psychological": "psychological", "competitor": "competitor", "voice": "voice", "synthesis": "synthesis"}
    )

workflow.add_edge("synthesis", END)

graph = workflow.compile()

if __name__ == "__main__":
    state = {
        "task": "Test ICP",
        "context": "Testing",
        "business_context": "Tech founders",
        "master_context": "Tech founders",
        "requested_agents": ["voice"],
        "new_data": True,
        "client_id": "test123"
    }
    result = graph.invoke(state)
    print(f"Result: {result.get('result', {})}")
