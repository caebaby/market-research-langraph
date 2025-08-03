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

# Import V4 agents
from ..agents.psychological_v4 import PsychologicalAgentV4
from ..agents.voice_v4 import VoiceAgentV4
from ..agents.interview_psychological_v4 import PsychologicalInterviewAgentV4

# Create agent instances
psychological_agent = PsychologicalAgentV4()
voice_agent = VoiceAgentV4()
psychological_interview_agent = PsychologicalInterviewAgentV4()

# Create workflow
workflow = StateGraph(ICPState)

# Add the psychological node with proper state handling
def psychological_node(state: ICPState) -> ICPState:
    """Wrapper to ensure state is properly updated"""
    print("[Graph] Executing psychological node")
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

# Voice node
def voice_node(state: ICPState) -> ICPState:
    """Wrapper for voice of customer agent"""
    print("[Graph] Executing voice node")
    
    try:
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
            
    except Exception as e:
        print(f"[Graph] Error in voice node: {e}")
        # Continue with pipeline even if voice fails
        
    return state

def psychological_interview_node(state: ICPState) -> ICPState:
    """Wrapper for psychological interview agent"""
    # Update task
    state["current_task"] = {
        "description": "Create psychological depth interviews based on insights",
        "is_high_stakes": False
    }
    
    # Call the agent
    updated_state = psychological_interview_agent(state)
    
    # Preserve all updates
    if isinstance(updated_state, dict):
        for key, value in updated_state.items():
            state[key] = value
    
    # Store interview output in result
    if "current_output" in state:
        if "result" not in state:
            state["result"] = {}
        state["result"]["psychological_interviews"] = state["current_output"]
    
    return state

# Add synthesis node (simple for now)
def synthesis_node(state: ICPState) -> ICPState:
    """Simple synthesis - combines all results"""
    print("[Graph] Executing synthesis node")
    # For now, just pass through and mark complete
    state["synthesis_complete"] = True
    
    # If we have multiple agent results, combine them
    if "result" in state and isinstance(state["result"], dict):
        # Future: This will combine insights from all agents
        state["final_report"] = state["result"]
    
    return state

# Add nodes
workflow.add_node("psychological", psychological_node)
workflow.add_node("voice", voice_node)
workflow.add_node("psychological_interviews", psychological_interview_node)
workflow.add_node("synthesis", synthesis_node)

# Set entry point
workflow.set_entry_point("psychological")

# Update edges - all agents in sequence
workflow.add_edge("psychological", "voice")
workflow.add_edge("voice", "psychological_interviews")
workflow.add_edge("psychological_interviews", "synthesis")
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
