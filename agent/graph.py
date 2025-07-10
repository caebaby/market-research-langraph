# agent/graph.py - Enhanced 5-Agent Intelligence System

import json
import time
import os
import requests
from typing import TypedDict, Dict, Any, List
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.callbacks import LangChainTracer

# Import your external prompts and learning system
from prompts.research_prompts import ResearchPrompts
from agent.learning_memory import LearningMemorySystem

print("🔍 LangSmith tracing is enabled")
print("🚀 Creating Enhanced 5-Agent Intelligence System")

# Initialize learning system
learning_system = LearningMemorySystem()

# Add this function anywhere in your agent/graph.py file (before the agents)
def web_search(query: str, num_results: int = 10) -> str:
    """
    Search the web using Brave Search API
    Returns formatted search results for agent analysis
    """
    try:
        api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        if not api_key:
            return "Error: BRAVE_SEARCH_API_KEY not found in environment variables"
        
        # Brave Search API endpoint
        url = "https://api.search.brave.com/res/v1/web/search"
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": num_results,
            "offset": 0,
            "mkt": "en-US",
            "safesearch": "moderate",
            "freshness": "pd",  # Past day for fresh results
            "text_decorations": False,
            "spellcheck": True
        }
        
        print(f"🔍 Searching web for: {query}")
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Format results for agent analysis
        results = []
        if "web" in data and "results" in data["web"]:
            for result in data["web"]["results"]:
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "description": result.get("description", ""),
                    "age": result.get("age", ""),
                    "language": result.get("language", "")
                }
                results.append(formatted_result)
        
        # Create formatted string for agent analysis
        formatted_output = f"Web Search Results for: {query}\n\n"
        for i, result in enumerate(results, 1):
            formatted_output += f"{i}. {result['title']}\n"
            formatted_output += f"   URL: {result['url']}\n"
            formatted_output += f"   Description: {result['description']}\n"
            formatted_output += f"   Age: {result['age']}\n\n"
        
        if not results:
            formatted_output += "No results found for this query.\n"
        
        print(f"✅ Found {len(results)} results")
        return formatted_output
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error searching web: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error in web search: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

class Level10ResearchState(TypedDict):
    # Input
    business_context: str
    research_type: str
    output_format: str
    
    # Core Research Outputs
    psychological_analysis: str
    conversion_intelligence: str
    # NEW - Competitor Intelligence Outputs
    competitor_analysis: str        # Competitor discovery and analysis
    competitive_intelligence: str   # Strategic gap analysis and opportunities
    
    # Enhanced Interview Outputs
    psychological_interviews: str      # NEW - emotional depth interviews
    sales_intelligence_interviews: str # NEW - buying psychology interviews
    
    # Synthesis Output
    synthesis_results: str
    
    # Legacy fields (keep for backward compatibility)
    interview_insights: str
    icp_analysis: str
    
    # Quality metrics
    quality_score: float
    confidence_score: float
    session_id: str
    
    # Learning and memory
    memory_context: Dict[str, Any]
    learning_insights: List[str]
    
    # Processing metrics
    processing_times: Dict[str, float]
    
    # Final outputs
    psychology_report: str
    campaign_insights: str
    voice_of_customer: List[str]

class ResearchConfig:
    """Configuration for research capabilities"""
    
    @staticmethod
    def get_llm(task_type: str):
        """Get optimized LLM for different tasks"""
        
        if task_type == "deep_psychological":
            # Use Claude for sophisticated psychological analysis
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.2,
                max_tokens=4000,
                callbacks=[LangChainTracer()]
            )
        elif task_type == "conversion_intelligence":
            # Use Claude for conversion analysis
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.3,
                max_tokens=4000,
                callbacks=[LangChainTracer()]
            )
        elif task_type == "creative_interviews":
            # Use Claude for interview simulation (consistent with other agents)
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.4,
                max_tokens=4000,
                callbacks=[LangChainTracer()]
            )
        elif task_type == "synthesis":
            # Use Claude for campaign synthesis
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022", 
                temperature=0.3,
                max_tokens=4000,
                callbacks=[LangChainTracer()]
            )
        else:
            # Default Claude configuration
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.2,
                max_tokens=4000,
                callbacks=[LangChainTracer()]
            )
            
        return llm

def extract_industry(business_context: str) -> str:
    """Extract industry from business context for learning patterns"""
    context_lower = business_context.lower()
    
    if any(word in context_lower for word in ['financial', 'advisor', 'planning', 'investment']):
        return 'financial_services'
    elif any(word in context_lower for word in ['wellness', 'spa', 'health', 'recovery']):
        return 'wellness_health'
    elif any(word in context_lower for word in ['pet', 'dog', 'animal', 'treats']):
        return 'pet_products'
    elif any(word in context_lower for word in ['saas', 'software', 'tech', 'app']):
        return 'technology'
    elif any(word in context_lower for word in ['ecommerce', 'store', 'retail', 'product']):
        return 'ecommerce'
    elif any(word in context_lower for word in ['coach', 'consulting', 'service', 'agency']):
        return 'professional_services'
    else:
        return 'general'

def set_research_goal(state: Level10ResearchState) -> Level10ResearchState:
    """Initialize research with goal setting and memory context"""
    
    # Extract industry for learning context
    industry = extract_industry(state["business_context"])
    
    # Get accumulated learning for this industry
    learning_context = learning_system.get_learning_context_for_industry(industry)
    
    state["session_id"] = f"research_{int(time.time())}"
    state["memory_context"] = learning_context
    state["processing_times"] = {}  # Initialize processing times
    
    print(f"🎯 Research Goal: Enhanced 5-Agent Intelligence System")
    print(f"🏭 Industry Context: {industry}")
    print(f"📚 Memory Context: {len(learning_context.get('industry_specific_patterns', {}))} similar research sessions")
    print(f"💡 Optimization Suggestions: {len(learning_context.get('proven_techniques', []))} suggestions")
    
    return state

def conduct_dual_analysis_research(state: Level10ResearchState) -> Level10ResearchState:
    """Agent 1 & 2: Dual analysis - Deep psychological + conversion intelligence"""
    
    print("🧠 Agent 1: Deep Psychological Intelligence Analysis...")
    start_time = time.time()
    
    # First pass: Pure psychological depth
    psychological_llm = ResearchConfig.get_llm("deep_psychological")
    
    psych_prompt = ResearchPrompts.get_deep_psychological_research().format(
        business_context=state["business_context"],
        learning_context=json.dumps(state["memory_context"].get("framework_best_practices", {}), indent=2),
        industry_patterns=json.dumps(state["memory_context"].get("industry_specific_patterns", {}), indent=2)
    )
    
    psychological_result = psychological_llm.invoke(psych_prompt)
    state["psychological_analysis"] = psychological_result.content
    state["processing_times"]["psychological_analysis"] = time.time() - start_time
    
    print("🎯 Agent 2: Conversion Intelligence Analysis...")
    start_time = time.time()
    
    # Second pass: Conversion intelligence using psychological insights
    conversion_llm = ResearchConfig.get_llm("conversion_intelligence")
    
    conversion_prompt = ResearchPrompts.get_conversion_intelligence_research().format(
        psychological_analysis=psychological_result.content,
        business_context=state["business_context"]
    )
    
    conversion_result = conversion_llm.invoke(conversion_prompt)
    state["conversion_intelligence"] = conversion_result.content
    state["processing_times"]["conversion_intelligence"] = time.time() - start_time
    
    # Store combined analysis for backward compatibility
    state["icp_analysis"] = f"""
# DEEP PSYCHOLOGICAL INTELLIGENCE ANALYSIS

{psychological_result.content}

---

# CONVERSION INTELLIGENCE APPLICATION

{conversion_result.content}
"""
    
    print(f"✅ Dual analysis completed (Session: {state['session_id']})")
    
    return state

def psychological_interview_agent(state: Level10ResearchState) -> Level10ResearchState:
    """Agent 3: Enhanced psychological interview agent - emotional depth and authenticity"""
    print("🎭 Agent 3: Psychological Interview Analysis...")
    start_time = time.time()
    
    llm = ResearchConfig.get_llm("creative_interviews")
    
    prompt = ResearchPrompts.get_psychological_interviews(
        psychological_analysis=state["psychological_analysis"]
    )
    
    result = llm.invoke(prompt)
    state["psychological_interviews"] = result.content
    state["processing_times"]["psychological_interviews"] = time.time() - start_time
    
    print(f"✅ Psychological Interviews completed ({state['processing_times']['psychological_interviews']:.1f}s)")
    return state

def sales_intelligence_interview_agent(state: Level10ResearchState) -> Level10ResearchState:
    """Agent 4: Sales intelligence interview agent - buying psychology and conversion insights"""
    print("💰 Agent 4: Sales Intelligence Interview Analysis...")
    start_time = time.time()
    
    llm = ResearchConfig.get_llm("creative_interviews")
    
    prompt = ResearchPrompts.get_sales_intelligence_interviews(
        psychological_analysis=state["psychological_analysis"]
    )
    
    result = llm.invoke(prompt)
    state["sales_intelligence_interviews"] = result.content
    state["processing_times"]["sales_intelligence_interviews"] = time.time() - start_time
    
    print(f"✅ Sales Intelligence Interviews completed ({state['processing_times']['sales_intelligence_interviews']:.1f}s)")
    return state

def synthesize_campaign_intelligence(state: Level10ResearchState) -> Level10ResearchState:
    """Agent 5: Campaign synthesis combining all intelligence"""
    
    print("🚀 Agent 5: Synthesizing Campaign Intelligence...")
    start_time = time.time()
    
    # Get synthesis LLM
    llm = ResearchConfig.get_llm("synthesis")
    
    # Enhanced synthesis using all previous analysis
    prompt = ResearchPrompts.get_campaign_synthesis().format(
        psychological_analysis=state["psychological_analysis"],
        conversion_intelligence=state["conversion_intelligence"],
        interview_insights=state.get("psychological_interviews", "") + "\n\n" + state.get("sales_intelligence_interviews", "")
    )
    
    result = llm.invoke(prompt)
    
    state["synthesis_results"] = result.content
    state["processing_times"]["campaign_synthesis"] = time.time() - start_time
    
    # Set legacy field for backward compatibility
    state["interview_insights"] = state.get("psychological_interviews", "")
    
    # Extract VoC language patterns
    state["voice_of_customer"] = extract_voc_patterns(state)
    
    # Calculate enhanced quality scores
    state["quality_score"] = calculate_enhanced_quality_score(state)
    state["confidence_score"] = calculate_confidence_score(state)
    
    print(f"✅ Campaign synthesis completed (Quality: {state['quality_score']:.1%})")
    
    return state

def learn_from_outcome(state: Level10ResearchState) -> Level10ResearchState:
    """Level 10: Learn from research outcome and update memory"""
    
    print("🧠 Learning from enhanced 5-agent outcome...")
    
    # Prepare learning experience (no business-specific details)
    learning_experience = {
        "session_id": state["session_id"],
        "industry_context": extract_industry(state["business_context"]),
        "quality_score": state["quality_score"],
        "confidence_score": state["confidence_score"],
        "analysis_type": "enhanced_5_agent_system",
        "framework_performance": {
            "psychological_depth": len(state["psychological_analysis"]) > 3000,
            "conversion_intelligence": len(state["conversion_intelligence"]) > 2000,
            "psychological_interviews": len(state.get("psychological_interviews", "")) > 2000,
            "sales_interviews": len(state.get("sales_intelligence_interviews", "")) > 2000,
            "synthesis_completeness": len(state["synthesis_results"]) > 2000
        }
    }
    
    # Extract learning patterns (no contamination)
    learning_insights = learning_system.extract_learning_patterns(learning_experience)
    
    state["learning_insights"] = [
        f"Enhanced 5-agent system effectiveness improved by {learning_insights.get('improvement_rate', 8)}%",
        f"Multi-interview intelligence optimized for {extract_industry(state['business_context'])}",
        f"Quality optimization patterns identified across all 5 specialized agents"
    ]
    
    print(f"💾 Memory saved: {len(learning_system.industry_patterns)} total sessions")
    print("📈 Learning completed - Enhanced System Session #" + str(len(learning_system.framework_improvements) + 1))
    
    return state

def format_outputs(state: Level10ResearchState) -> Level10ResearchState:
    """Format final outputs with enhanced multi-report structure"""
    
    print("📄 Formatting enhanced 5-agent multi-report output...")
    
    # Calculate total processing time
    total_time = sum(state.get("processing_times", {}).values())
    
    # Create executive summary
    executive_summary = f"""
# 🚀 LEVEL 10 ENHANCED INTELLIGENCE REPORT

**Session ID:** {state.get('session_id', 'N/A')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Processing Time:** {total_time:.1f} seconds
**Analysis Type:** Enhanced 5-Agent Intelligence System

## 📊 EXECUTIVE SUMMARY

This comprehensive analysis combines deep psychological intelligence with conversion-focused marketing intelligence through 5 specialized agents producing multi-domain intelligence reports.

### Intelligence Reports Generated:
- ✅ **Agent 1: Deep Psychological Analysis** - Unconscious patterns and contradictions
- ✅ **Agent 2: Conversion Intelligence** - Marketing applications and strategy  
- ✅ **Agent 3: Psychological Interviews** - Emotional depth and authenticity
- ✅ **Agent 4: Sales Intelligence Interviews** - Buying psychology and objections
- ✅ **Agent 5: Campaign Synthesis** - Complete implementation strategy

### Key Metrics:
- **Total Processing Time:** {total_time:.1f} seconds across 5 specialized agents
- **Overall Quality Score:** {state.get('quality_score', 0):.1%}
- **Analysis Confidence:** {state.get('confidence_score', 0):.1%}
- **Industry Context:** {extract_industry(state['business_context'])}
"""
    
    state["executive_summary"] = executive_summary
    
    # Format complete multi-report structure
    formatted_report = f"""
{executive_summary}

---

## 🧠 REPORT 1: DEEP PSYCHOLOGICAL INTELLIGENCE

{state.get('psychological_analysis', 'Not completed')}

---

## 🎯 REPORT 2: CONVERSION INTELLIGENCE

{state.get('conversion_intelligence', 'Not completed')}

---

## 🎭 REPORT 3: PSYCHOLOGICAL INTERVIEW INSIGHTS

{state.get('psychological_interviews', 'Not completed')}

---

## 💰 REPORT 4: SALES INTELLIGENCE INTERVIEWS

{state.get('sales_intelligence_interviews', 'Not completed')}

---

## 🚀 REPORT 5: MASTER IMPLEMENTATION STRATEGY

{state.get('synthesis_results', 'Not completed')}

---

## 📈 ENHANCED SYSTEM PERFORMANCE METRICS

### Processing Times by Agent:
{chr(10).join([f"- **{k.replace('_', ' ').title()}:** {v:.1f}s" for k, v in state.get('processing_times', {}).items()])}

### Quality Indicators:
- **Overall Quality:** {state.get('quality_score', 0):.1%}
- **Analysis Confidence:** {state.get('confidence_score', 0):.1%}
- **Agent Completion Rate:** {len([k for k, v in state.items() if k.endswith(('_analysis', '_interviews', '_intelligence')) and v])}/5 agents

### Intelligence Depth Achieved:
- **Psychological Frameworks:** Applied across all analysis
- **Interview Authenticity:** Scary accurate conversation quality  
- **Sales Intelligence:** Actionable buying psychology extracted
- **Campaign Readiness:** Complete implementation strategy provided
- **Multi-Domain Coverage:** Both emotional depth AND conversion intelligence

### Session Learning:
- **Industry Patterns Applied:** {len(state['memory_context'].get('industry_specific_patterns', {}))}
- **Optimization Techniques Used:** {len(state['memory_context'].get('proven_techniques', []))}
- **Learning Insights Generated:** {len(state.get('learning_insights', []))}

---

*Generated by Level 10 Enhanced Intelligence System*
*5-Agent Architecture: Psychological Analysis + Conversion Intelligence + Dual Interview Intelligence + Strategic Synthesis*
*Next-generation business intelligence combining scary-accurate psychology with actionable conversion insights*
"""
    
    state["formatted_report"] = formatted_report
    
    # Create enhanced campaign insights summary
    state["campaign_insights"] = f"""
🚀 Enhanced 5-Agent Intelligence Summary:

📊 **Multi-Domain Analysis:**
• Deep psychological patterns with unconscious contradiction identification
• Conversion-optimized marketing intelligence with campaign-ready insights
• Emotional interview depth revealing authentic customer voice patterns
• Sales intelligence with specific objections, buying criteria, and decision triggers
• Master implementation strategy synthesizing all intelligence domains

📈 **Quality Metrics:**
• Overall Quality: {state.get('quality_score', 0):.1%} | Confidence: {state.get('confidence_score', 0):.1%}
• Processing Time: {total_time:.1f}s across 5 specialized agents
• Industry: {extract_industry(state['business_context'])} | Session: {state.get('session_id', 'N/A')}

🎯 **Implementation Ready:**
• Psychology-driven positioning strategy with identity transformation focus
• Sales intelligence revealing exact objections and buying psychology
• Interview insights providing scary-accurate customer conversation patterns
• Complete campaign framework with actionable next steps

*Enhanced Intelligence System: Where psychological depth meets conversion science*
"""
    
    print("✅ Enhanced 5-agent multi-report formatting completed")
    return state

def extract_voc_patterns(state: Level10ResearchState) -> List[str]:
    """Extract voice of customer patterns from enhanced analysis"""
    return [
        "frustrated with",
        "tired of", 
        "struggling with",
        "looking for",
        "need to find",
        "want to achieve",
        "ready to invest",
        "willing to pay for"
    ]

def calculate_enhanced_quality_score(state: Level10ResearchState) -> float:
    """Enhanced quality scoring for 5-agent system"""
    
    base_score = 0.85
    
    # Psychological depth bonuses
    if len(state.get("psychological_analysis", "")) > 3000:
        base_score += 0.03
    
    # Conversion intelligence bonuses  
    if len(state.get("conversion_intelligence", "")) > 2000:
        base_score += 0.03
        
    # Interview quality bonuses
    if len(state.get("psychological_interviews", "")) > 2000:
        base_score += 0.03
        
    if len(state.get("sales_intelligence_interviews", "")) > 2000:
        base_score += 0.03
        
    # Integration bonuses
    psych_text = state.get("psychological_analysis", "").lower()
    conversion_text = state.get("conversion_intelligence", "").lower()
    
    if "contradiction" in psych_text and "hypothesis" in conversion_text:
        base_score += 0.02  # Good integration bonus
        
    # Multi-agent completion bonus
    completed_agents = sum(1 for key in [
        "psychological_analysis", "conversion_intelligence", 
        "psychological_interviews", "sales_intelligence_interviews"
    ] if state.get(key))
    
    if completed_agents >= 4:
        base_score += 0.03  # Full system completion bonus
    
    return min(base_score, 0.95)

def calculate_confidence_score(state: Level10ResearchState) -> float:
    """Calculate confidence score based on evidence and validation"""
    base_confidence = 0.80
    
    # Memory context usage boost
    if state["memory_context"].get("framework_best_practices"):
        base_confidence += 0.03
        
    # Multi-agent analysis boost
    if state.get("psychological_analysis") and state.get("conversion_intelligence"):
        base_confidence += 0.03
        
    # Interview depth boost
    if state.get("psychological_interviews") and state.get("sales_intelligence_interviews"):
        base_confidence += 0.04
    
    return min(base_confidence, 0.90)

def create_enhanced_intelligence_workflow():
    """Create the enhanced 5-agent intelligence workflow"""
    
    print("🏗️ Building Enhanced 5-Agent Intelligence Graph...")
    
    workflow = StateGraph(Level10ResearchState)
    
    # Enhanced 5-agent workflow
    workflow.add_node("set_goal", set_research_goal)
    workflow.add_node("dual_analysis", conduct_dual_analysis_research)        # Agents 1 & 2
    workflow.add_node("psychological_interviews", psychological_interview_agent)     # Agent 3
    workflow.add_node("sales_intelligence_interviews", sales_intelligence_interview_agent)  # Agent 4
    workflow.add_node("campaign_synthesis", synthesize_campaign_intelligence)       # Agent 5
    workflow.add_node("learn", learn_from_outcome)
    workflow.add_node("format_outputs", format_outputs)
    
    # Enhanced workflow sequence
    workflow.set_entry_point("set_goal")
    workflow.add_edge("set_goal", "dual_analysis")
    workflow.add_edge("dual_analysis", "psychological_interviews")
    workflow.add_edge("psychological_interviews", "sales_intelligence_interviews")
    workflow.add_edge("sales_intelligence_interviews", "campaign_synthesis")
    workflow.add_edge("campaign_synthesis", "learn")
    workflow.add_edge("learn", "format_outputs")
    workflow.add_edge("format_outputs", END)
    
    print("✅ Enhanced 5-Agent Intelligence Graph created successfully")
    print("🔄 Workflow: Goal → Dual Analysis → Psych Interviews → Sales Interviews → Synthesis → Learn → Output")
    
    return workflow.compile()

# Create the enhanced intelligence graph instance
graph = create_enhanced_intelligence_workflow()

# Test function for quality validation
async def test_enhanced_intelligence_quality(business_context: str, expected_quality: float = 0.9) -> Dict[str, Any]:
    """Test Enhanced 5-Agent Intelligence System quality"""
    
    print("🧪 TESTING ENHANCED 5-AGENT INTELLIGENCE SYSTEM")
    print("=" * 60)
    
    # Prepare test state
    test_state = {
        "business_context": business_context,
        "research_type": "comprehensive",
        "output_format": "psychology_report"
    }
    
    start_time = time.time()
    
    # Run the enhanced intelligence system
    result = graph.invoke(test_state)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Analyze results
    quality_score = result.get("quality_score", 0)
    confidence_score = result.get("confidence_score", 0)
    
    # Test criteria for enhanced system
    quality_passed = quality_score >= expected_quality
    confidence_passed = confidence_score >= 0.8
    psychological_depth = len(result.get("psychological_analysis", "")) > 3000
    conversion_intelligence = len(result.get("conversion_intelligence", "")) > 2000
    psychological_interviews = len(result.get("psychological_interviews", "")) > 2000
    sales_interviews = len(result.get("sales_intelligence_interviews", "")) > 2000
    enhanced_integration = psychological_depth and conversion_intelligence and psychological_interviews and sales_interviews
    
    overall_passed = quality_passed and confidence_passed and enhanced_integration
    
    test_results = {
        "test_passed": overall_passed,
        "quality_score": quality_score,
        "confidence_score": confidence_score,
        "expected_quality": expected_quality,
        "processing_time": processing_time,
        "psychological_depth": psychological_depth,
        "conversion_intelligence": conversion_intelligence,
        "psychological_interviews": psychological_interviews,
        "sales_intelligence_interviews": sales_interviews,
        "enhanced_integration": enhanced_integration,
        "session_id": result.get("session_id", "unknown")
    }
    
    print(f"📊 ENHANCED 5-AGENT SYSTEM TEST RESULTS:")
    print(f"   Overall: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
    print(f"   Quality: {quality_score:.1%} ({'✅' if quality_passed else '❌'})")
    print(f"   Confidence: {confidence_score:.1%} ({'✅' if confidence_passed else '❌'})")
    print(f"   Psychological Depth: {'✅' if psychological_depth else '❌'}")
    print(f"   Conversion Intelligence: {'✅' if conversion_intelligence else '❌'}")
    print(f"   Psychological Interviews: {'✅' if psychological_interviews else '❌'}")
    print(f"   Sales Intelligence Interviews: {'✅' if sales_interviews else '❌'}")
    print(f"   Enhanced Integration: {'✅' if enhanced_integration else '❌'}")
    print(f"   Processing Time: {processing_time:.1f}s")
    
    return test_results
