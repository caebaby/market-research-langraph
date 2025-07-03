import os
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json

# State definition matching your CrewAI complexity
class ResearchState(TypedDict):
    # Input
    business_context: str
    research_type: str
    output_format: str
    
    # Research phases
    icp_analysis: str
    interview_insights: str
    synthesis_results: str
    
    # Formatted outputs
    psychology_report: str
    campaign_insights: str
    voice_of_customer: Dict[str, List[str]]
    
    # Metadata
    session_id: str
    quality_score: float

# Your comprehensive ICP prompt from CrewAI
ICP_RESEARCH_PROMPT = PromptTemplate(
    input_variables=["business_context"],
    template="""
You are an Elite Business Intelligence Researcher conducting comprehensive ICP research.

SESSION ISOLATION: Fresh analysis with no previous context.

BUSINESS CONTEXT:
{business_context}

COMPREHENSIVE ICP ANALYSIS FRAMEWORK:

PART A: FOUNDATIONAL ICP DEVELOPMENT

Step 1: Refine & Expand Baseline Profile
- Demographics with nuance (not just age/income)
- Psychographics depth analysis
- Identity and self-perception analysis
- Common misconceptions about this profile

Step 2: Deep Dive - Pains, Problems & Frustrations
- Surface-level operational struggles
- Deeper emotional/strategic pains they hide
- Pains they deny but still feel
- Root causes and cascading consequences
- VoC Language: Exact phrases for each pain level

Step 3: Deep Dive - Desires, Aspirations & Motivations
- Stated goals (what they say they want)
- Actual underlying desires (what they really want)
- Latent needs they don't realize yet
- Core psychological drivers
- VoC Language: How they express aspirations

Step 4: Voice of Customer Language Synthesis
- Key language patterns and recurring themes
- Pain Language Lexicon
- Desire Language Lexicon
- Tone and communication style analysis

PART B: PSYCHOLOGICAL FRAMEWORK ANALYSIS

Step 5: Jungian Archetype Analysis
- Dominant archetypes and shadow aspects
- How they see themselves vs. reality
- Archetype conflicts and resolutions

Step 6: Language & Behavior (LAB) Profile
- Motivation direction (toward/away)
- Decision-making style
- Processing preferences
- Action triggers

Step 7: Deep Desires & Motivational Drivers
- Significance/Recognition needs
- Connection/Love requirements  
- Power/Control desires
- Growth/Contribution drives
- Security/Certainty needs
- Variety/Uncertainty tolerance

Step 8: Jobs-To-Be-Done Purchase Psychology
- Functional jobs
- Social jobs
- Emotional jobs
- Current solution analysis
- Switch triggers

Step 9: Cognitive Biases & Decision Shortcuts
- Authority bias manifestations
- Social proof requirements
- Loss aversion triggers
- Status quo bias strength

Step 10: Influence & Authority Triggers
- Trust-building requirements
- Credibility markers that matter
- Resistance patterns
- Compliance triggers

PART C: VOICE OF CUSTOMER LANGUAGE MAPS

Step 11: Funnel Stage Language Patterns
- TOFU: Problem recognition language
- MOFU: Solution evaluation language  
- BOFU: Decision commitment language

Provide breakthrough insights that make clients say "I've never understood my customers this deeply before."
"""
)

# Interview simulation prompt
INTERVIEW_SIMULATION_PROMPT = PromptTemplate(
    input_variables=["icp_analysis"],
    template="""
Based on this ICP analysis:
{icp_analysis}

Create 3 detailed customer interview simulations:

PERSONA 1: The Skeptical Achiever
- Successful but frustrated with current situation
- High standards, low trust
- Needs proof before believing

PERSONA 2: The Quiet Sufferer  
- Living with the pain for years
- Resigned to the situation
- Needs hope and possibility

PERSONA 3: The Active Seeker
- Tried multiple solutions
- Still searching for the right fit
- Needs differentiation clarity

For each persona, create authentic dialogue:
- Their exact words describing pain points
- How they talk about failed solutions
- What would make them trust a new approach
- Their transformation language
- Objections and hesitations

Capture emotional undertones and subtext.
Make it feel like real interview transcripts.
"""
)

# Synthesis and campaign insights prompt
SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["icp_analysis", "interview_insights", "business_context"],
    template="""
Synthesize research into campaign-ready insights:

ICP Analysis:
{icp_analysis}

Interview Insights:
{interview_insights}

Business Context:
{business_context}

Create:

1. BREAKTHROUGH POSITIONING
- Market position that feels inevitable
- Differentiation that renders competition irrelevant
- Category design opportunities

2. CONVERSION PSYCHOLOGY FRAMEWORK
- Headlines that stop scrolls (25%+ CTR)
- Messaging hierarchy by awareness level
- Trust acceleration sequence
- Objection dissolution strategy

3. VOICE OF CUSTOMER COPYBANK
- Power phrases for each awareness level
- Emotional trigger language
- Transformation promises that resonate
- Proof elements that matter

4. CAMPAIGN ARCHITECTURE
- Content strategy by buyer journey stage
- Channel-specific messaging adaptations
- Testing priorities for optimization
- Success metrics and benchmarks

Make this immediately actionable for creating high-converting campaigns.
"""
)

def conduct_icp_research(state: ResearchState) -> ResearchState:
    """Phase 1: Deep ICP Research with Claude"""
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.3,
        max_tokens=4000
    )
    
    prompt = ICP_RESEARCH_PROMPT.format(
        business_context=state["business_context"]
    )
    
    state["icp_analysis"] = llm.invoke(prompt).content
    state["session_id"] = f"research_{int(os.urandom(4).hex(), 16)}"
    
    return state

def simulate_interviews(state: ResearchState) -> ResearchState:
    """Phase 2: Interview Simulation"""
    
    # Use GPT-4 for creative interview simulation
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7  # Higher for creativity
    ) if os.getenv("OPENAI_API_KEY") else ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7
    )
    
    prompt = INTERVIEW_SIMULATION_PROMPT.format(
        icp_analysis=state["icp_analysis"]
    )
    
    state["interview_insights"] = llm.invoke(prompt).content
    
    return state

def synthesize_research(state: ResearchState) -> ResearchState:
    """Phase 3: Synthesis and Campaign Insights"""
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.3
    )
    
    prompt = SYNTHESIS_PROMPT.format(
        icp_analysis=state["icp_analysis"],
        interview_insights=state["interview_insights"],
        business_context=state["business_context"]
    )
    
    state["synthesis_results"] = llm.invoke(prompt).content
    
    # Extract VoC language patterns
    state["voice_of_customer"] = extract_voc_patterns(state)
    
    # Calculate quality score
    state["quality_score"] = calculate_quality_score(state)
    
    return state

def format_outputs(state: ResearchState) -> ResearchState:
    """Format outputs based on requested format"""
    
    if state.get("output_format") == "psychology_report":
        state["psychology_report"] = create_psychology_report(state)
    elif state.get("output_format") == "campaign_ready":
        state["campaign_insights"] = create_campaign_insights(state)
    
    return state

def extract_voc_patterns(state: ResearchState) -> Dict[str, List[str]]:
    """Extract voice of customer patterns from research"""
    # This would parse the research and extract actual phrases
    # For now, returning structure
    return {
        "pain_language": ["frustrated with", "tired of", "struggling with"],
        "desire_language": ["looking for", "wish I could", "need to find"],
        "transformation_language": ["finally able to", "no longer worried", "confident that"]
    }

def calculate_quality_score(state: ResearchState) -> float:
    """Calculate research quality score"""
    # Implement scoring logic based on depth, specificity, etc.
    return 0.92  # Placeholder

def create_psychology_report(state: ResearchState) -> str:
    """Create beautiful psychology-focused report"""
    return f"""
# Deep Customer Psychology Intelligence

## Executive Summary
{state.get('synthesis_results', '').split('\n')[0:5]}

## Psychological Profile
{state.get('icp_analysis', '')}

## Voice of Customer Insights
{json.dumps(state.get('voice_of_customer', {}), indent=2)}

## Campaign Psychology
{state.get('synthesis_results', '')}

Quality Score: {state.get('quality_score', 0):.2%}
"""

def create_campaign_insights(state: ResearchState) -> str:
    """Create campaign-ready insights"""
    return state.get('synthesis_results', '')

def create_graph():
    """Create the sophisticated research workflow"""
    workflow = StateGraph(ResearchState)
    
    # Add nodes
    workflow.add_node("icp_research", conduct_icp_research)
    workflow.add_node("interview_simulation", simulate_interviews)
    workflow.add_node("synthesis", synthesize_research)
    workflow.add_node("format_outputs", format_outputs)
    
    # Set entry point
    workflow.set_entry_point("icp_research")
    
    # Add edges
    workflow.add_edge("icp_research", "interview_simulation")
    workflow.add_edge("interview_simulation", "synthesis")
    workflow.add_edge("synthesis", "format_outputs")
    workflow.add_edge("format_outputs", END)
    
    return workflow.compile()

# Create the graph instance
graph = create_graph()
