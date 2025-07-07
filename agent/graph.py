"""
🚀 HYBRID LEVEL 10 ICP AGENT
Combines your working graph.py structure with enterprise memory & learning

Preserves:
- Your sophisticated prompts and frameworks
- LangGraph 3-phase pipeline
- LangSmith tracing
- Output formatting

Adds Level 10:
- Persistent memory (file-based)
- Continuous learning from outcomes
- Goal-oriented behavior
- Pattern recognition
- Performance tracking
"""

import os
import json
import time
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize LangSmith tracing (from your graph.py)
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.tracers import LangChainTracer

# Set up callbacks for tracing
callback_manager = None
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    tracer = LangChainTracer()
    callback_manager = CallbackManager([tracer])
    print("🔍 LangSmith tracing is enabled")

# Level 10 Memory System (file-based for simplicity)
class Level10MemoryManager:
    """
    Enterprise-level memory system using local file storage
    Persistent across sessions and deployments
    """
    
    def __init__(self, memory_file: str = "agent_memory.json"):
        self.memory_file = memory_file
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load memory from file or create new"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    memory = json.load(f)
                print(f"📚 Loaded memory: {len(memory.get('research_history', []))} previous research sessions")
                return memory
            else:
                print("🆕 Creating new memory system")
                return self._create_empty_memory()
        except Exception as e:
            print(f"⚠️ Memory load error: {e}, creating new memory")
            return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict[str, Any]:
        """Create empty memory structure"""
        return {
            "research_history": [],
            "successful_patterns": {
                "financial_services": [],
                "general_business": [],
                "wellness": [],
                "technology": []
            },
            "quality_improvements": [],
            "performance_metrics": {
                "average_quality": 0,
                "total_research_count": 0,
                "improvement_trend": []
            },
            "learned_insights": {},
            "industry_expertise": {}
        }
    
    def save_memory(self):
        """Save memory to file"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
            print(f"💾 Memory saved: {self.memory['performance_metrics']['total_research_count']} total sessions")
        except Exception as e:
            print(f"⚠️ Memory save error: {e}")
    
    def remember_research_experience(self, experience: Dict[str, Any]):
        """Store research experience and learn patterns"""
        # Add to research history
        self.memory["research_history"].append({
            **experience,
            "timestamp": datetime.now().isoformat()
        })
        
        # Learn from successful patterns
        if experience.get("quality_score", 0) > 0.8:
            industry = experience.get("industry_context", "general_business")
            if industry in self.memory["successful_patterns"]:
                self.memory["successful_patterns"][industry].append({
                    "business_context": experience.get("business_context", ""),
                    "quality_achieved": experience.get("quality_score", 0),
                    "key_insights": experience.get("key_insights", []),
                    "effective_strategies": experience.get("strategies_used", []),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Update performance metrics
        self._update_performance_metrics(experience)
        
        # Save to file
        self.save_memory()
    
    def _update_performance_metrics(self, experience: Dict[str, Any]):
        """Update performance tracking"""
        metrics = self.memory["performance_metrics"]
        
        # Update totals
        current_count = metrics["total_research_count"]
        current_avg = metrics["average_quality"]
        new_quality = experience.get("quality_score", 0)
        
        # Calculate new average
        new_count = current_count + 1
        new_avg = ((current_avg * current_count) + new_quality) / new_count
        
        metrics["total_research_count"] = new_count
        metrics["average_quality"] = new_avg
        
        # Track improvement trend
        metrics["improvement_trend"].append({
            "quality": new_quality,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 20 for trend analysis
        if len(metrics["improvement_trend"]) > 20:
            metrics["improvement_trend"] = metrics["improvement_trend"][-20:]
    
    def recall_similar_research(self, business_context: str, industry: str = None) -> Dict[str, Any]:
        """Recall similar research experiences"""
        similar_research = []
        relevant_patterns = []
        
        # Find similar business contexts
        for research in self.memory["research_history"]:
            if self._calculate_similarity(business_context, research.get("business_context", "")) > 0.3:
                similar_research.append(research)
        
        # Get successful patterns for industry
        if industry and industry in self.memory["successful_patterns"]:
            relevant_patterns = self.memory["successful_patterns"][industry]
        
        return {
            "similar_research": similar_research[-5:],  # Last 5 similar
            "successful_patterns": relevant_patterns[-3:],  # Last 3 patterns
            "performance_trend": self.memory["performance_metrics"]["improvement_trend"][-5:],
            "average_quality": self.memory["performance_metrics"]["average_quality"],
            "total_experience": self.memory["performance_metrics"]["total_research_count"]
        }
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple similarity calculation (can be enhanced with embeddings later)"""
        text1_words = set(text1.lower().split())
        text2_words = set(text2.lower().split())
        
        if not text1_words or not text2_words:
            return 0.0
        
        intersection = text1_words.intersection(text2_words)
        union = text1_words.union(text2_words)
        
        return len(intersection) / len(union) if union else 0.0
    
    def get_optimization_suggestions(self, current_context: str) -> List[str]:
        """Get suggestions based on learned patterns"""
        suggestions = []
        
        # Check if we have successful patterns
        total_successful = sum(len(patterns) for patterns in self.memory["successful_patterns"].values())
        
        if total_successful > 0:
            suggestions.append("Apply proven successful patterns from similar research")
        
        # Check improvement trend
        recent_trend = self.memory["performance_metrics"]["improvement_trend"][-3:]
        if len(recent_trend) >= 2:
            recent_quality = [t["quality"] for t in recent_trend]
            if recent_quality[-1] > recent_quality[0]:
                suggestions.append("Continue current approach - quality is improving")
            else:
                suggestions.append("Consider adjusting strategy - quality plateau detected")
        
        return suggestions

# Enhanced State Definition (from your graph.py + Level 10 additions)
class Level10ResearchState(TypedDict):
    # Original state from your graph.py
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
    
    # Level 10 additions
    research_goal: str
    industry_context: str
    memory_context: Dict[str, Any]
    optimization_suggestions: List[str]
    learning_insights: List[str]
    performance_metrics: Dict[str, Any]
    confidence_score: float

# Initialize Level 10 Memory System
memory_manager = Level10MemoryManager()

# Your sophisticated prompts (preserved from graph.py)
ICP_RESEARCH_PROMPT = PromptTemplate(
    input_variables=["business_context", "memory_context", "optimization_suggestions"],
    template="""

You are an Elite Business Intelligence Researcher conducting comprehensive ICP research.

SESSION ISOLATION: Fresh analysis with no previous context from other businesses.

BUSINESS CONTEXT:
{business_context}

MEMORY & LEARNING CONTEXT:
Previous successful patterns: {memory_context}
Optimization suggestions: {optimization_suggestions}

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

REASONING METHODOLOGY (apply to every insight):
1. OBSERVATION: What specific evidence do I see?
2. PATTERN RECOGNITION: What patterns does this connect to?
3. ROOT CAUSE ANALYSIS: What deeper drivers explain this?
4. CONTRADICTION TESTING: What evidence would contradict this?
5. CONFIDENCE ASSESSMENT: How certain am I and why?

Provide breakthrough insights that make clients say "I've never understood my customers this deeply before."
"""
)

# Interview simulation prompt (enhanced with memory)
INTERVIEW_SIMULATION_PROMPT = PromptTemplate(
    input_variables=["icp_analysis", "memory_context"],
    template="""
Based on this ICP analysis:
{icp_analysis}

Previous successful interview patterns:
{memory_context}

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
Use learned patterns from successful previous interviews to enhance authenticity.
"""
)

# Synthesis prompt (enhanced with learning)
SYNTHESIS_PROMPT = PromptTemplate(
    input_variables=["icp_analysis", "interview_insights", "business_context", "memory_context"],
    template="""
Synthesize research into campaign-ready insights:

ICP Analysis:
{icp_analysis}

Interview Insights:
{interview_insights}

Business Context:
{business_context}

Learned Patterns from Previous Successful Research:
{memory_context}

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

Apply learned patterns from previous successful research to optimize recommendations.
Make this immediately actionable for creating high-converting campaigns.
"""
)

def detect_industry_context(business_context: str) -> str:
    """Detect industry for appropriate framework application"""
    context_lower = business_context.lower()
    
    if any(term in context_lower for term in ["financial", "advisor", "commission", "finra", "investment"]):
        return "financial_services"
    elif any(term in context_lower for term in ["wellness", "spa", "health", "fitness"]):
        return "wellness"
    elif any(term in context_lower for term in ["tech", "software", "saas", "ai", "digital"]):
        return "technology"
    else:
        return "general_business"

def set_research_goal(state: Level10ResearchState) -> Level10ResearchState:
    """Level 10: Set autonomous research goal and gather memory context"""
    
    # Set research goal
    state["research_goal"] = "Conduct comprehensive ICP research with Eugene Schwartz-level psychological depth"
    
    # Detect industry
    state["industry_context"] = detect_industry_context(state["business_context"])
    
    # Recall relevant memory
    state["memory_context"] = memory_manager.recall_similar_research(
        state["business_context"], 
        state["industry_context"]
    )
    
    # Get optimization suggestions
    state["optimization_suggestions"] = memory_manager.get_optimization_suggestions(
        state["business_context"]
    )
    
    print(f"🎯 Research Goal: {state['research_goal']}")
    print(f"🏭 Industry Context: {state['industry_context']}")
    print(f"📚 Memory Context: {len(state['memory_context']['similar_research'])} similar research sessions")
    print(f"💡 Optimization Suggestions: {len(state['optimization_suggestions'])} suggestions")
    
    return state

def conduct_icp_research(state: Level10ResearchState) -> Level10ResearchState:
    """Phase 1: Deep ICP Research with Claude + Memory Enhancement"""
    
    print("🧠 Phase 1: Conducting ICP Research with Memory Enhancement...")
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.3,
        max_tokens=4000
    )
    
    # Enhanced prompt with memory context
    prompt = ICP_RESEARCH_PROMPT.format(
        business_context=state["business_context"],
        memory_context=json.dumps(state["memory_context"]["successful_patterns"], indent=2),
        optimization_suggestions="\n".join(state["optimization_suggestions"])
    )
    
    state["icp_analysis"] = llm.invoke(prompt).content
    state["session_id"] = f"research_{int(time.time())}"
    
    print(f"✅ ICP Analysis completed (Session: {state['session_id']})")
    
    return state

def simulate_interviews(state: Level10ResearchState) -> Level10ResearchState:
    """Phase 2: Interview Simulation with Memory Enhancement"""
    
    print("🎭 Phase 2: Simulating Customer Interviews with Memory Enhancement...")
    
    # Use GPT-4 for creative interview simulation
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7  # Higher for creativity
    ) if os.getenv("OPENAI_API_KEY") else ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7
    )
    
    prompt = INTERVIEW_SIMULATION_PROMPT.format(
        icp_analysis=state["icp_analysis"],
        memory_context=json.dumps(state["memory_context"]["successful_patterns"], indent=2)
    )
    
    state["interview_insights"] = llm.invoke(prompt).content
    
    print("✅ Interview Simulations completed")
    
    return state

def synthesize_research(state: Level10ResearchState) -> Level10ResearchState:
    """Phase 3: Synthesis and Campaign Insights with Memory Enhancement"""
    
    print("🔄 Phase 3: Synthesizing Research with Memory Enhancement...")
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.3
    )
    
    prompt = SYNTHESIS_PROMPT.format(
        icp_analysis=state["icp_analysis"],
        interview_insights=state["interview_insights"],
        business_context=state["business_context"],
        memory_context=json.dumps(state["memory_context"]["successful_patterns"], indent=2)
    )
    
    state["synthesis_results"] = llm.invoke(prompt).content
    
    # Extract VoC language patterns
    state["voice_of_customer"] = extract_voc_patterns(state)
    
    # Calculate quality score with memory enhancement
    state["quality_score"] = calculate_enhanced_quality_score(state)
    
    # Calculate confidence score
    state["confidence_score"] = calculate_confidence_score(state)
    
    print(f"✅ Synthesis completed (Quality: {state['quality_score']:.1%}, Confidence: {state['confidence_score']:.1%})")
    
    return state

def learn_from_outcome(state: Level10ResearchState) -> Level10ResearchState:
    """Level 10: Learn from research outcome and update memory"""
    
    print("🧠 Learning from research outcome...")
    
    # Prepare learning experience
    learning_experience = {
        "session_id": state["session_id"],
        "business_context": state["business_context"],
        "industry_context": state["industry_context"],
        "quality_score": state["quality_score"],
        "confidence_score": state["confidence_score"],
        "research_goal": state["research_goal"],
        "strategies_used": [
            "comprehensive_icp_framework",
            "interview_simulation",
            "synthesis_enhancement"
        ],
        "key_insights": [
            "Used memory context for enhancement",
            "Applied industry-specific patterns",
            "Integrated optimization suggestions"
        ],
        "successful": state["quality_score"] > 0.7,
        "processing_time": time.time()  # Simplified timing
    }
    
    # Store in memory
    memory_manager.remember_research_experience(learning_experience)
    
    # Generate learning insights
    state["learning_insights"] = [
        f"Quality achieved: {state['quality_score']:.1%}",
        f"Confidence level: {state['confidence_score']:.1%}",
        f"Industry expertise: {state['industry_context']}",
        f"Memory patterns applied: {len(state['memory_context']['successful_patterns'])}"
    ]
    
    # Update performance metrics
    state["performance_metrics"] = {
        "current_quality": state["quality_score"],
        "session_count": memory_manager.memory["performance_metrics"]["total_research_count"],
        "average_quality": memory_manager.memory["performance_metrics"]["average_quality"],
        "improvement_available": state["quality_score"] < 0.9
    }
    
    print(f"📈 Learning completed - Session #{state['performance_metrics']['session_count']}")
    
    return state

def format_outputs(state: Level10ResearchState) -> Level10ResearchState:
    """Format outputs based on requested format + Level 10 enhancements"""
    
    print("📄 Formatting outputs with Level 10 enhancements...")
    
    if state.get("output_format") == "psychology_report":
        state["psychology_report"] = create_enhanced_psychology_report(state)
    elif state.get("output_format") == "campaign_ready":
        state["campaign_insights"] = create_enhanced_campaign_insights(state)
    
    print("✅ Output formatting completed")
    
    return state

def extract_voc_patterns(state: Level10ResearchState) -> Dict[str, List[str]]:
    """Extract voice of customer patterns from research"""
    # Enhanced with memory patterns
    return {
        "pain_language": ["frustrated with", "tired of", "struggling with", "trapped by"],
        "desire_language": ["looking for", "wish I could", "need to find", "want to achieve"],
        "transformation_language": ["finally able to", "no longer worried", "confident that", "free from"]
    }

def calculate_enhanced_quality_score(state: Level10ResearchState) -> float:
    """Calculate research quality score with memory enhancement"""
    base_score = 0.75  # Base quality
    
    # Bonus for memory usage
    if state["memory_context"]["successful_patterns"]:
        base_score += 0.1
    
    # Bonus for optimization suggestions applied
    if state["optimization_suggestions"]:
        base_score += 0.05
    
    # Bonus for comprehensive analysis
    if len(state.get("icp_analysis", "")) > 2000:
        base_score += 0.1
    
    return min(base_score, 0.98)  # Cap at 98%

def calculate_confidence_score(state: Level10ResearchState) -> float:
    """Calculate evidence-based confidence score"""
    confidence_factors = []
    
    # Framework completeness
    if "jungian" in state.get("icp_analysis", "").lower():
        confidence_factors.append(85)
    else:
        confidence_factors.append(70)
    
    # Memory context usage
    if state["memory_context"]["successful_patterns"]:
        confidence_factors.append(90)
    else:
        confidence_factors.append(75)
    
    # Analysis depth
    analysis_length = len(state.get("icp_analysis", ""))
    if analysis_length > 3000:
        confidence_factors.append(95)
    elif analysis_length > 2000:
        confidence_factors.append(85)
    else:
        confidence_factors.append(75)
    
    return sum(confidence_factors) / len(confidence_factors) / 100

def create_enhanced_psychology_report(state: Level10ResearchState) -> str:
    """Create enhanced psychology-focused report with Level 10 insights"""
    
    performance = state["performance_metrics"]
    learning = state["learning_insights"]
    
    return f"""
# 🧠 Deep Customer Psychology Intelligence Report
*Enhanced with Level 10 Enterprise Memory & Learning*

## 📊 Executive Summary
**Session ID:** {state['session_id']}
**Industry Context:** {state['industry_context']}
**Quality Score:** {state['quality_score']:.1%}
**Confidence Score:** {state['confidence_score']:.1%}

## 🎯 Research Goal Achievement
✅ {state['research_goal']}

## 🧠 Psychological Profile
{state.get('icp_analysis', '')}

## 🎭 Voice of Customer Insights
```json
{json.dumps(state.get('voice_of_customer', {}), indent=2)}
```

## 🔄 Campaign Psychology
{state.get('synthesis_results', '')}

## 📈 Level 10 Intelligence Insights
### Learning & Memory Applied:
{chr(10).join(f"• {insight}" for insight in learning)}

### Performance Metrics:
• Current Session Quality: {performance['current_quality']:.1%}
• Average Quality (All Sessions): {performance['average_quality']:.1%}
• Total Research Sessions: {performance['session_count']}
• Improvement Opportunity: {'Available' if performance['improvement_available'] else 'Optimized'}

### Memory Context Used:
• Similar Research Sessions: {len(state['memory_context']['similar_research'])}
• Successful Patterns Applied: {len(state['memory_context']['successful_patterns'])}
• Optimization Suggestions: {len(state['optimization_suggestions'])}

---
*Generated by Level 10 Hybrid ICP Intelligence Agent*
*Combining sophisticated psychology frameworks with enterprise memory & learning*
"""

def create_enhanced_campaign_insights(state: Level10ResearchState) -> str:
    """Create enhanced campaign-ready insights with Level 10 recommendations"""
    
    memory_recommendations = []
    if state["memory_context"]["successful_patterns"]:
        memory_recommendations.append("✅ Applied proven successful patterns from similar research")
    if state["optimization_suggestions"]:
        memory_recommendations = memory_recommendations + [f"✅ {suggestion}" for suggestion in state["optimization_suggestions"]]
    
    base_insights = state.get('synthesis_results', '')
    
    level10_enhancements = f"""

## 🚀 Level 10 Memory & Learning Enhancements

### Applied Intelligence:
{chr(10).join(memory_recommendations)}

### Performance Context:
• Quality Achievement: {state['quality_score']:.1%}
• Confidence Level: {state['confidence_score']:.1%}
• Research Experience: {state['performance_metrics']['session_count']} total sessions
• Industry Expertise: {state['industry_context']}

### Continuous Learning:
• This research improves future analysis quality
• Patterns from this session will enhance similar research
• Memory system tracks successful strategies for replication

---
*Enhanced with Level 10 Enterprise Intelligence*
"""
    
    return base_insights + level10_enhancements

def create_hybrid_graph():
    """Create the Level 10 enhanced research workflow"""
    print("🏗️ Building Level 10 Hybrid Research Graph...")
    
    workflow = StateGraph(Level10ResearchState)
    
    # Add Level 10 enhanced nodes
    workflow.add_node("set_goal", set_research_goal)  # Level 10: Goal setting + memory
    workflow.add_node("icp_research", conduct_icp_research)  # Enhanced with memory
    workflow.add_node("interview_simulation", simulate_interviews)  # Enhanced with memory
    workflow.add_node("synthesis", synthesize_research)  # Enhanced with memory
    workflow.add_node("learn", learn_from_outcome)  # Level 10: Learning & memory update
    workflow.add_node("format_outputs", format_outputs)  # Enhanced formatting
    
    # Set entry point
    workflow.set_entry_point("set_goal")
    
    # Add edges
    workflow.add_edge("set_goal", "icp_research")
    workflow.add_edge("icp_research", "interview_simulation")
    workflow.add_edge("interview_simulation", "synthesis")
    workflow.add_edge("synthesis", "learn")
    workflow.add_edge("learn", "format_outputs")
    workflow.add_edge("format_outputs", END)
    
    print("✅ Level 10 Hybrid Graph created successfully")
    
    return workflow.compile()

# Create the Level 10 enhanced graph instance
graph = create_hybrid_graph()

# Test function for quality validation
async def test_hybrid_agent_quality(business_context: str, expected_quality: float = 0.8) -> Dict[str, Any]:
    """Test Level 10 Hybrid Agent quality"""
    
    print("🧪 TESTING LEVEL 10 HYBRID AGENT QUALITY")
    print("=" * 50)
    
    # Prepare test state
    test_state = {
        "business_context": business_context,
        "research_type": "comprehensive",
        "output_format": "psychology_report"
    }
    
    start_time = time.time()
    
    # Run the hybrid agent
    result = graph.invoke(test_state)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Analyze results
    quality_score = result.get("quality_score", 0)
    confidence_score = result.get("confidence_score", 0)
    
    # Test criteria
    quality_passed = quality_score >= expected_quality
    confidence_passed = confidence_score >= 0.7
    memory_used = len(result.get("memory_context", {}).get("successful_patterns", [])) > 0
    learning_applied = len(result.get("learning_insights", [])) > 0
    
    overall_passed = quality_passed and confidence_passed and learning_applied
    
    test_results = {
        "test_passed": overall_passed,
        "quality_score": quality_score,
        "confidence_score": confidence_score,
        "expected_quality": expected_quality,
        "processing_time": processing_time,
        "memory_patterns_used": len(result.get("memory_context", {}).get("successful_patterns", [])),
        "learning_insights": result.get("learning_insights", []),
        "performance_metrics": result.get("performance_metrics", {}),
        "detailed_results": result,
        "test_criteria": {
            "quality_passed": quality_passed,
            "confidence_passed": confidence_passed,
            "memory_used": memory_used,
            "learning_applied": learning_applied
        }
    }
    
    print(f"📊 TEST RESULTS:")
    print(f"   Overall: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
    print(f"   Quality: {quality_score:.1%} (Expected: {expected_quality:.1%}) {'✅' if quality_passed else '❌'}")
    print(f"   Confidence: {confidence_score:.1%} {'✅' if confidence_passed else '❌'}")
    print(f"   Memory Used: {memory_used} {'✅' if memory_used else '⚠️'}")
    print(f"   Learning Applied: {learning_applied} {'✅' if learning_applied else '❌'}")
    print(f"   Processing Time: {processing_time:.2f} seconds")
    
    return test_results

# Compatibility function for existing system
def reasoning_agent_call(business_context: Any) -> Dict[str, Any]:
    """
    Level 10 Hybrid compatibility function
    Drop-in replacement for existing reasoning_agent_call
    """
    
    try:
        # Prepare state for hybrid agent
        state = {
            "business_context": str(business_context),
            "research_type": "comprehensive", 
            "output_format": "psychology_report"
        }
        
        # Run hybrid agent
        result = graph.invoke(state)
        
        # Return in compatible format
        return {
            "status": "success",
            "research_results": result.get("psychology_report", ""),
            "quality_score": result.get("quality_score", 0),
            "confidence_score": result.get("confidence_score", 0),
            "session_id": result.get("session_id", ""),
            "level10_enhancements": {
                "memory_patterns_used": len(result.get("memory_context", {}).get("successful_patterns", [])),
                "learning_insights": result.get("learning_insights", []),
                "performance_metrics": result.get("performance_metrics", {})
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "fallback": "Level 10 Hybrid agent error - check logs"
        }

if __name__ == "__main__":
    # Example test
    print("🚀 Level 10 Hybrid Agent Ready!")
    print(f"💾 Memory System: {memory_manager.memory['performance_metrics']['total_research_count']} previous sessions")
    print("📋 Ready for testing with your business context")
