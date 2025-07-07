# Create: prompts/research_prompts.py

class ResearchPrompts:
    """External prompt library for easy tweaking without code changes"""
    
    @staticmethod
    def get_comprehensive_icp_research():
        """Your original sophisticated research prompt"""
        return """
SESSION ISOLATION: Analyze ONLY the current business context below. Do not reference or mix insights from previous business contexts.

LEARNING ENHANCEMENT: Apply accumulated expertise in psychological frameworks and analysis techniques while maintaining complete separation between different business contexts.

BUSINESS CONTEXT TO ANALYZE:
{business_context}

ACCUMULATED EXPERTISE TO APPLY:
{learning_context}

MEMORY PATTERNS FOR THIS INDUSTRY:
{industry_patterns}

COMPREHENSIVE ICP & PSYCHOLOGICAL FRAMEWORK RESEARCH

PART A: FOUNDATIONAL ICP DEVELOPMENT

Step 1: Refined Baseline Profile
- Core Identity Analysis
- Key Psychographic Patterns  
- Hidden Self-Perception Conflicts

Step 2: Deep Pain Analysis
- Surface Pains
- Hidden Emotional Pains
- Denied Pains
- Root Cause Analysis

Step 3: Desire & Motivation Analysis
- Stated Desires
- Actual Underlying Desires
- Latent Needs

Step 4: Voice of Customer Language Capture
- Pain Language Lexicon
- Desire Language Lexicon
- Tone & Style Analysis

PART B: PSYCHOLOGICAL FRAMEWORK ANALYSIS

Step 5: Jungian Archetype Analysis
- Identity & Self-Perception
- Dominant Archetypes
- VoC Language reflecting archetypes

Step 6: Language & Behavior (LAB) Profile Analysis
- Motivation Direction, Source, Mode, Process
- Proactivity, Communication Style
- VoC Language revealing LAB preferences

Step 7: Deep Desires & Motivational Drivers Analysis
- Analysis across Significance, Connection, Power/Control
- Growth, Security, Variety, Contribution
- Dominant desires and conflicts
- VoC Language expressing desires

Step 8: Jobs-To-Be-Done (JTBD) Purchase Psychology
- Core Job Analysis (Functional, Social, Emotional)
- Competition/Current Solution Analysis
- Triggers & Purchase Commitment Factors
- Objection & Hesitation Analysis
- VoC Language for JTBD, frustrations, readiness

Step 9: Cognitive Biases & Decision Shortcuts
- Authority, Social Proof, Scarcity/Loss Aversion
- Anchoring, Confirmation, Status Quo biases
- VoC Language revealing biases

Step 10: Influence & Authority Triggers
- Authority & Compliance Analysis
- Resistance & Trust-Building Factors
- VoC Language indicating trust, resistance, action

PART C: VOICE OF CUSTOMER LANGUAGE MAPS

Step 11: Voice of Customer Language Map for Funnel Stages

11A: TOFU Language Patterns - Attention & Awareness
- Problem Recognition Language
- Pain Point Articulation
- Initial Solution Seeking
- TOFU Language Map (Direct Quotes, Key Terms, Questions, Tone/Urgency)

11B: MOFU Language Patterns - Consideration & Evaluation
- Solution Evaluation Language
- Comparison Terminology
- Objection Articulation
- MOFU Language Map (Direct Quotes, Evaluation Criteria, Objection Phrases, Trust Indicators)

11C: BOFU Language Patterns - Decision & Action
- Decision Trigger Language
- Commitment Terminology
- Final Hesitation Language
- BOFU Language Map (Direct Quotes, Action Terms, Reassurance Needs, Post-Decision Language)

SECTION 5: FINAL SELF-CRITIQUE
- Review entire analysis for missing insights
- Identify assumptions with highest risk
- Cultural, generational, industry-specific nuances
- Improvement recommendations

SECTION 6: TRANSFER-READY OUTPUT
Synthesize findings into:
- ICP Definition
- Key Pain Points (TOP 3-5)
- Key Desires/Aspirations (TOP 3-5)
- Current Beliefs & Failed Solutions
- Transformation Requirements
- Psychological Drivers
- Voice of Customer Language
- Competitive Landscape

Provide journal-level psychological insights that would make clients say "how did you know that?"
"""
    
    @staticmethod
    def get_interview_simulation():
        """Interview simulation prompt"""
        return """
Based on the ICP research: {icp_analysis}

Conduct 3 simulated customer interviews using the psychological frameworks identified.

For each interview:
1. Create a realistic persona based on the ICP analysis
2. Simulate natural conversation flow with authentic language
3. Reveal deeper psychological layers through probing questions
4. Capture voice of customer language patterns
5. Uncover hidden motivations and fears

Interview Focus Areas:
- Core pain points and emotional triggers
- Decision-making process and criteria
- Past solution attempts and failures
- Ideal future state and transformation desires
- Objections and hesitation points

Output authentic dialogue that sounds like real customer conversations, not AI-generated responses.
"""
    
    @staticmethod
    def get_campaign_synthesis():
        """Campaign synthesis and GTM copy prompt"""
        return """
Based on research: {icp_analysis}
And interviews: {interview_insights}

Create comprehensive GTM strategy including:

1. POSITIONING STRATEGY
- Core positioning statement
- Category creation opportunity
- Differentiation angles
- Competitive positioning

2. MESSAGING FRAMEWORK
- Value proposition hierarchy
- Key messaging pillars
- Proof points and evidence
- Objection handling

3. CONVERSION COPY ASSETS
- Headlines by awareness level (with CTR targets)
- Email subject lines
- Ad copy variations
- Landing page copy blocks
- Social proof statements

4. CAMPAIGN PSYCHOLOGY
- Trust building sequence
- Scarcity/urgency applications
- Social proof strategies
- Authority positioning

5. VOICE OF CUSTOMER INTEGRATION
- Authentic language patterns
- Customer testimonial frameworks
- Case study narratives
- FAQ responses using customer language

Output should be campaign-ready with specific copy and strategic guidance.
"""

# Usage in agent/graph.py:
from prompts.research_prompts import ResearchPrompts

def conduct_icp_research(state):
    prompt_template = ResearchPrompts.get_comprehensive_icp_research()
    # ... rest of agent logic
