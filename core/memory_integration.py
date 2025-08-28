# core/memory_integration.py
"""
Memory integration hooks for agents - ready to connect
"""

def extract_key_insights(agent_name: str, output: str) -> list:
    """Extract important insights from agent outputs"""
    insights = []
    
    if agent_name == "psychological":
        # Look for patterns like "fear of...", "identity...", "unconscious..."
        if "fear of" in output.lower():
            start = output.lower().index("fear of")
            insights.append(output[start:start+100])
    
    elif agent_name == "voice_of_customer":
        # Look for quoted customer language
        import re
        quotes = re.findall(r'"([^"]+)"', output)
        insights.extend(quotes[:5])  # Top 5 quotes
    
    elif agent_name == "competitor":
        # Look for competitor names and gaps
        if "gap" in output.lower() or "opportunity" in output.lower():
            insights.append(output[:200])
    
    return insights

def format_memory_for_retrieval(memories: list) -> str:
    """Format memories for agent context"""
    if not memories:
        return "No previous insights available."
    
    formatted = "Previous insights for this client:\n"
    for i, memory in enumerate(memories[:5], 1):
        formatted += f"{i}. {memory}\n"
    return formatted