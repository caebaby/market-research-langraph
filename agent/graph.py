import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# State definition
class ResearchState(TypedDict):
    business_context: str
    research_output: str

# Enhanced research prompt for Claude
RESEARCH_PROMPT = PromptTemplate(
    input_variables=["business_context"],
    template="""
You are an elite market research psychologist with expertise in Eugene Schwartz-level customer psychology analysis.

SESSION ISOLATION: This is a completely fresh analysis. You have NO memory of any previous research sessions. Each analysis starts with a blank slate.

BUSINESS CONTEXT TO ANALYZE:
{business_context}

Conduct comprehensive ICP research with breakthrough psychological depth:

1. DEEP CUSTOMER PSYCHOLOGY ANALYSIS
   - Unconscious motivations and hidden drivers
   - Emotional triggers they don't consciously recognize
   - Core identity conflicts and resolutions
   - Belief systems and worldview analysis
   - Shadow desires they won't publicly admit

2. AUTHENTIC VOICE OF CUSTOMER CAPTURE
   - Exact phrases that reveal psychological state
   - Language patterns that indicate readiness
   - Emotional vocabulary around pain points
   - Transformation language they use
   - Internal dialogue vs. external expression

3. ADVANCED BUYER PSYCHOLOGY FRAMEWORKS
   - Eugene Schwartz awareness levels with nuance
   - Breakthrough positioning angles competitors miss
   - Decision-making triggers at subconscious level
   - Resistance patterns and how to dissolve them
   - Trust acceleration techniques

4. CAMPAIGN-READY CONVERSION INSIGHTS
   - Headlines that tap deep psychology
   - Messaging that creates "how did you know?" moments
   - Positioning that feels inevitable
   - Copy angles for 25%+ conversion rates

Remember: You're not just analyzing demographics. You're uncovering the hidden psychological landscape that drives buying decisions. Make clients say "I've never thought of my customers this way before."

Focus EXCLUSIVELY on the business context provided above. No references to any other businesses or previous analyses.
"""
)

# Research function with Claude
def conduct_research(state: ResearchState) -> ResearchState:
    """Main research logic with Claude for deeper insights"""
    
    # Use Claude if available, fallback to GPT-4
    use_claude = os.getenv("USE_CLAUDE", "true").lower() == "true"
    
    if use_claude and os.getenv("ANTHROPIC_API_KEY"):
        # Claude for superior psychological insights
        llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",  # Or claude-3-opus for best quality
            temperature=0.3,
            max_tokens=4000
        )
    else:
        # Fallback to OpenAI
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3
        )
    
    # Format prompt
    prompt = RESEARCH_PROMPT.format(
        business_context=state["business_context"]
    )
    
    # Run research
    try:
        research_output = llm.invoke(prompt).content
    except Exception as e:
        # Graceful fallback
        if use_claude and os.getenv("OPENAI_API_KEY"):
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
            research_output = llm.invoke(prompt).content
        else:
            raise e
    
    # Update state
    state["research_output"] = research_output
    return state

# Build graph
def create_graph():
    """Create the research graph"""
    workflow = StateGraph(ResearchState)
    
    # Add single node
    workflow.add_node("research", conduct_research)
    
    # Set entry point
    workflow.set_entry_point("research")
    
    # Add edge to END
    workflow.add_edge("research", END)
    
    return workflow.compile()

# Create the graph instance
graph = create_graph()
