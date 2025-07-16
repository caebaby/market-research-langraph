from langgraph.graph import StateGraph, END
from typing import Dict
from ..agents.psychological import PsychologicalAgent

class ICPState(Dict):
    task: str
    context: str
    new_data: bool
    result: str
    quality: float

agent = PsychologicalAgent()
workflow = StateGraph(ICPState)
workflow.add_node("psychological", agent.run)
workflow.set_entry_point("psychological")
workflow.add_edge("psychological", END)
graph = workflow.compile()

if __name__ == "__main__":
    state = {"task": "Financial advisor ICP", "context": "Financial services", "new_data": True}
    result = graph.invoke(state)
    print(f"Result: {result['result']}, Quality: {result['quality']}")
