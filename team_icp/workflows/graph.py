from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional


class ICPState(Dict):
    task: str
    context: str
    business_context: Optional[str]
    master_context: Optional[str]
    new_data: bool
    result: Optional[Dict[str, Any]]
    current_output: Optional[str]
    quality_score: Optional[float]
    quality: Optional[float]  # Keep for backward compatibility
    
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
from ..agents.psychological import PsychologicalAgent
from ..agents.competitor import CompetitorAgent  # ADD THIS LINE
from src.agents.voice_agent import VoiceAgent

# Create agent instances
psychological_agent = PsychologicalAgent()
competitor_agent = CompetitorAgent()  # ADD THIS LINE
voice_agent = VoiceAgent()  # ADD THIS LINE

# Create workflow
workflow = StateGraph(ICPState)

# Add the psychological node with proper state handling
def psychological_node(state: ICPState) -> ICPState:
    """Wrapper to ensure state is properly updated"""
    # Call the agent
    updated_state = psychological_agent(state)
    
    # Ensure critical fields are preserved
    if isinstance(updated_state, dict):
        # Merge the updated state back into the original
        for key, value in updated_state.items():
            state[key] = value
    
    # Ensure backward compatibility
    if "quality_score" in state and "quality" not in state:
        state["quality"] = state["quality_score"]
    
    if "current_output" in state and "result" not in state:
        state["result"] = {"psychological": state["current_output"]}
    
    return state

# ADD THIS ENTIRE SECTION - Competitor node
def competitor_node(state: ICPState) -> ICPState:
    """Wrapper for competitor agent"""
    # Update task for competitor agent
    state["current_task"] = {
        "description": "Analyze competitive landscape and identify positioning opportunities",
        "is_high_stakes": False
    }
    
    # Call the agent
    updated_state = competitor_agent(state)
    
    # Ensure critical fields are preserved
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            state[key] = value
    
    # Store competitor output in result
    if "current_output" in state:
        if "result" not in state:
            state["result"] = {}
        state["result"]["competitor"] = state["current_output"]
    
    return state

def competitor_node(state: ICPState) -> ICPState:
    # ... existing competitor code ...
    return state

# ADD THIS ENTIRE FUNCTION:
def voice_node(state: ICPState) -> ICPState:
    """Wrapper for voice of customer agent"""
    # Update task for voice agent
    state["current_task"] = {
        "description": "Extract authentic customer language and create copy-ready phrases",
        "is_high_stakes": False
    }
    
    # Call the agent
    updated_state = voice_agent(state)
    
    # Ensure critical fields are preserved
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            state[key] = value
    
    # Store voice output in result
    if "current_output" in state:
        if "result" not in state:
            state["result"] = {}
        state["result"]["voice"] = state["current_output"]
    
    return state

# Add synthesis node (simple for now)
def synthesis_node(state: ICPState) -> ICPState:
    """Simple synthesis - combines all results"""
    # For now, just pass through and mark complete
    state["synthesis_complete"] = True
    
    # If we have multiple agent results, combine them
    if "result" in state and isinstance(state["result"], dict):
        # Future: This will combine insights from all agents
        state["final_report"] = state["result"]
    
    return state

# Add nodes
workflow.add_node("psychological", psychological_node)
workflow.add_node("competitor", competitor_node)  # ADD THIS LINE
workflow.add_node("voice", voice_node)  # ADD THIS LINE
workflow.add_node("synthesis", synthesis_node)

# Set entry point
workflow.set_entry_point("psychological")

# Update edges
workflow.add_edge("psychological", "competitor")  # ADD THIS LINE (changed from psychological → synthesis)
workflow.add_edge("competitor", "voice")   # CHANGE THIS LINE
workflow.add_edge("voice", "synthesis")    # ADD THIS LINE
workflow.add_edge("synthesis", END)

# Compile the graph
graph = workflow.compile()

if __name__ == "__main__":
    # Test with proper state structure
    state = {
        "task": "Financial advisor ICP",
        "context": "Financial services",
        "business_context": "Financial advisors with 7+ years experience",
        "master_context": "Financial advisors with 7+ years experience",
        "current_task": {"description": "Analyze financial advisor customer psychology"},
        "new_data": True,
        "client_id": "test123",
        "shared_insights": {},
        "memory_service": None,
        "tool_executor": None
    }
    
    result = graph.invoke(state)
    print(f"Output: {result.get('current_output', 'No output')}")
    print(f"Quality: {result.get('quality_score', 0.0)}")
    print(f"Synthesis complete: {result.get('synthesis_complete', False)}")
