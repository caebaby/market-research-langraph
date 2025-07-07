# prompts/research_prompts.py - Updated with dual prompt system

class ResearchPrompts:
    """Dual prompt system for maximum psychological depth + conversion intelligence"""
    
    @staticmethod
    def get_deep_psychological_research():
        """PROMPT 1: Scary deep psychological intelligence - the enhanced version we built"""
        return """
SESSION ISOLATION: Analyze ONLY the current business context below. Do not reference or mix insights from previous business contexts.

LEARNING ENHANCEMENT: Apply accumulated expertise in psychological frameworks and analysis techniques while maintaining complete separation between different business contexts.

BUSINESS CONTEXT TO ANALYZE:
{business_context}

ACCUMULATED EXPERTISE TO APPLY:
{learning_context}

MEMORY PATTERNS FOR THIS INDUSTRY:
{industry_patterns}

COMPREHENSIVE CUSTOMER PSYCHOLOGY ANALYSIS

**OBJECTIVE**: Conduct comprehensive customer psychology analysis using established psychological frameworks and behavioral analysis methodologies. Apply deep strategic thinking to understand customer motivations, pain points, and decision-making patterns.

**ANALYSIS DEPTH STANDARDS**:
- **Comprehensive Coverage**: Apply multiple psychological frameworks for complete customer understanding
- **Behavioral Insights**: Identify specific behavioral patterns and decision-making triggers
- **Language Analysis**: Analyze communication patterns and authentic voice characteristics
- **Strategic Recommendations**: Develop actionable marketing and positioning strategies

**PSYCHOLOGICAL FRAMEWORKS TO APPLY**:
1. **Identity Psychology** - Professional/personal identity conflicts
2. **Practical Operations Analysis** - Daily workflow pain points
3. **Jungian Archetype Analysis** - Core identity patterns
4. **LAB Profile Communication** - How they actually talk about problems
5. **Jobs-To-Be-Done Framework** - Functional, emotional, and social jobs
6. **Cognitive Bias Analysis** - Decision-making shortcuts
7. **Contradiction Pattern Analysis** - Deep psychological contradictions
8. **Voice of Customer Tactical Analysis** - Specific language for different contexts

PART A: FOUNDATIONAL CUSTOMER PSYCHOLOGY

Step 1: Identity and Self-Perception Analysis
- Professional/Personal Identity Conflicts: Gap between intended identity and current reality
- Self-Perception vs. Market Perception: How they see themselves vs. how others see them
- Identity Restoration Needs: What psychological changes would align identity with values
- Status and Recognition Drivers: How recognition affects decision-making
- Identity Defense Mechanisms: How they protect their self-image when challenged

Step 2: Practical Daily Operations Analysis
Daily Workflow Disruptions:
- What specific tasks consume disproportionate time/energy?
- Which operational bottlenecks cause the most frustration?
- What manual processes do they wish were automated?
- Which daily decisions drain their mental energy?

Resource and Capability Gaps:
- What skills/tools do they lack that they need?
- Which resources are they constantly searching for?
- What information gaps slow their decision-making?
- Which capabilities do they outsource or avoid?

Time and Priority Conflicts:
- What important tasks get pushed aside by urgent ones?
- Which competing priorities create the most stress?
- What strategic work gets sacrificed for operational demands?
- Which time drains do they recognize but can't eliminate?

Step 3: Emotional Pain Layering
- Surface Frustrations: Immediate operational annoyances
- Emotional Impacts: How practical problems affect confidence/stress/relationships
- Identity Threats: How operational failures threaten their professional self-image
- Existential Concerns: How daily challenges connect to larger life/career questions

PART B: ADVANCED PSYCHOLOGICAL FRAMEWORK ANALYSIS

Step 4: Jungian Archetype Analysis
- Identity & Self-Perception
- Dominant Archetypes (Hero, Caregiver, Explorer, etc.)
- VoC Language reflecting archetypes

Step 5: LAB Profile Communication Analysis
- Motivation Direction (toward vs away)
- Source (internal vs external reference)
- Decision Style (options vs procedures)
- VoC Language revealing LAB preferences

Step 6: Jobs-To-Be-Done Analysis
Functional Jobs (What they need to accomplish):
- Primary functional outcomes they're trying to achieve
- Secondary functional jobs that support the primary
- Maintenance jobs that keep systems running
- Problem-solving jobs when things go wrong

Emotional Jobs (How they want to feel):
- Professional confidence and competence feelings
- Stress reduction and peace of mind needs
- Recognition and validation desires
- Control and autonomy requirements

Social Jobs (How they want to be perceived):
- Professional reputation and status maintenance
- Peer recognition and respect needs
- Community contribution and leadership roles
- Relationship harmony and team dynamics

Step 7: Psychological Contradiction Patterns (DEEP ANALYSIS)
Identity Contradictions:
- What do they publicly claim to value vs. what their actions demonstrate?
- How does their professional persona conflict with their private beliefs?
- What aspects of their role do they embrace vs. resist?
- Where do their stated priorities conflict with their actual behavior?

Decision-Making Contradictions:
- When do they choose short-term comfort over long-term benefit?
- How do they rationalize decisions that conflict with stated values?
- What triggers them to act against their own best interests?
- Where do emotional decisions override logical analysis?

Communication Contradictions:
- What do they say vs. what their tone/body language conveys?
- How do their public statements differ from private conversations?
- When do they ask for one thing but actually need something else?
- What subtext exists beneath their surface communications?

Behavioral Contradictions:
- Which behaviors do they repeat despite knowing they're counterproductive?
- How do they seek solutions while simultaneously resisting change?
- Where do they desire independence while creating dependencies?
- What patterns do they complain about but continue to enable?

PART C: VOICE OF CUSTOMER TACTICAL ANALYSIS

Step 8: Multi-Context Language Patterns
Professional Language (B2B contexts):
- Industry terminology and formal communication patterns
- How they describe challenges in professional settings
- Language they use when positioning themselves to colleagues/clients
- Specific phrases when discussing ROI, efficiency, or strategic goals

Operational Language (Day-to-day practical discussions):
- How they describe workflow problems and bottlenecks
- Language patterns when discussing resource constraints
- Specific phrases about time management and priority conflicts
- Terms they use for practical solutions and workarounds

Emotional Language (Private/confidential discussions):
- How they express frustration with current situation
- Language patterns when discussing stress and overwhelm
- Specific phrases about professional satisfaction/dissatisfaction
- Terms they use when questioning their choices or direction

Step 9: Pain Point Communication Mapping
Practical Pain Language:
- "I spend too much time on..."
- "I can't find a way to..."
- "This process is killing me..."
- "I'm constantly dealing with..."

Emotional Pain Language:
- "I'm feeling overwhelmed by..."
- "It's frustrating that..."
- "I'm worried about..."
- "I hate that I have to..."

Identity Pain Language:
- "This isn't what I signed up for..."
- "I used to be someone who..."
- "I don't feel like myself when..."
- "I'm not the [role] I meant to be..."

DELIVERABLE REQUIREMENTS:
- Minimum 4,000 words of substantive psychological analysis
- 25+ specific behavioral insights with actionable implications
- 15+ voice of customer examples with psychological context
- Complete framework coverage - all psychological frameworks thoroughly analyzed
- 5+ psychological contradiction patterns identified and explored

DELIVER COMPREHENSIVE CUSTOMER PSYCHOLOGY ANALYSIS THAT REVEALS UNCONSCIOUS PATTERNS AND PROVIDES FOUNDATION FOR SUPERIOR MARKETING STRATEGY.
"""
    
    @staticmethod
    def get_conversion_intelligence_research():
        """PROMPT 2: Marketing conversion intelligence"""
        return """
PSYCHOLOGICAL FOUNDATION CONTEXT:
{psychological_analysis}

BUSINESS CONTEXT:
{business_context}

CONVERSION-DRIVEN MARKETING INTELLIGENCE ANALYSIS

**OBJECTIVE**: Transform psychological insights into actionable marketing intelligence that directly drives high-converting campaigns, ad tests, content strategies, and offer development.

**CONVERSION FOCUS**: Generate intelligence for:
- Micro-budget ad testing hypotheses (MintCRO/Curt Maly style)
- Conversion mechanism design (psychological triggers that drive action)
- Content strategy (short-form and long-form that converts)
- Product/offer development (what they'll actually buy and why)

PART A: CONVERSION PSYCHOLOGY APPLICATION

Step 1: Buying Decision Psychology
Decision Triggers (What makes them buy NOW):
- What specific combination of pain + urgency creates immediate action?
- Which emotional states make them most likely to purchase?
- What logical justifications do they need to rationalize buying?
- Which social proof elements remove final purchase resistance?

Purchase Moment Analysis:
- What thoughts go through their mind right before buying?
- Which final objections need to be overcome at point of purchase?
- What reassurances do they need to feel confident in their decision?
- Which "what if" scenarios create hesitation vs. commitment?

Step 2: Ad Testing Hypothesis Generation
Hook Testing Hypotheses:
- Problem-Focused Hooks: "Struggling with [specific pain]?" vs. "Tired of [different pain]?"
- Outcome-Focused Hooks: "[Specific result] in [timeframe]" vs. "[Different result] without [common obstacle]"
- Identity-Focused Hooks: "For [identity] who want [outcome]" vs. "If you're [different identity descriptor]"
- Urgency-Focused Hooks: "Before [deadline/consequence]" vs. "While [opportunity window]"

Angle Testing Hypotheses:
- Authority Angle: "The [method/system] that [result]" vs. social proof angle
- Transformation Angle: "From [current state] to [desired state]" vs. problem-solving angle
- Exclusive Angle: "Only for [qualifier]" vs. inclusive angle
- Method Angle: "The [#]-step [process]" vs. "The secret to [outcome]"

CTA Testing Hypotheses:
- Action-Oriented: "Get [specific outcome]" vs. "Start [process]"
- Curiosity-Driven: "See how [result]" vs. "Discover [method]"
- Risk-Reversal: "Try [solution] free" vs. "No-risk [outcome]"

Step 3: Content Strategy Intelligence
Short-Form Content Strategy:
- Problem/Solution Reveals: "The real reason you're [problem] + what actually works"
- Myth-Busting: "Everyone thinks [common belief] but here's what actually [truth]"
- Behind-the-Scenes: "What I learned after [experience] that changed everything"
- Social Proof Stories: "Client went from [before] to [after] using [method]"

Long-Form Content Strategy:
- Authority-Building Topics: Complex problems you can solve that competitors can't
- Conversion-Integrated Education: Teaching moments that create "I need help" realizations
- Content-to-Conversion Sequences: Educational content that leads to consultation requests

Step 4: Product/Offer Intelligence
High-Converting Offer Types:
- Done-For-You: What do they want handled completely?
- Done-With-You: What do they want guidance implementing?
- DIY + Support: What can they do themselves with the right system?
- Consulting/Strategy: What requires custom expert analysis?

Price Psychology Analysis:
- Low-Ticket: What problems justify this investment level?
- Mid-Ticket: What transformations feel worth this price?
- High-Ticket: What outcomes justify premium investment?

Step 5: Conversion Sequence Optimization
Awareness → Consideration:
- Which content moves them from problem-aware to solution-aware?
- What education positions your approach as superior?
- Which social proof builds category credibility?

Consideration → Intent:
- What demonstrations prove your solution works?
- Which comparisons highlight your unique advantages?
- What objection handling removes purchase barriers?

Intent → Purchase:
- Which final proof elements overcome last-minute hesitation?
- What urgency/scarcity creates action rather than procrastination?
- Which payment options reduce friction?

DELIVERABLE REQUIREMENTS:
- 25+ specific ad testing hypotheses with psychological rationale
- 15+ content ideas with conversion integration
- 10+ offer concepts with price point justification
- Complete conversion sequence mapping
- Voice of customer language for each funnel stage

DELIVER MARKETING INTELLIGENCE THAT DIRECTLY DRIVES CONVERSIONS, SALES, AND BUSINESS GROWTH.
"""
    
    @staticmethod
    def get_interview_simulation():
        """Interview simulation prompt - enhanced"""
        return """
Based on the psychological analysis: {psychological_analysis}

ENHANCED INTERVIEW SIMULATION

Create 3 HIGHLY REALISTIC customer interview simulations with different personas based on the psychological analysis:

INTERVIEW 1: High-Pain, High-Urgency Persona
- Focus on identity crisis and emotional urgency
- Reveal hidden costs and psychological impact
- Show decision-making under pressure

INTERVIEW 2: Analytical, Risk-Averse Persona  
- Focus on logical evaluation and risk assessment
- Reveal research patterns and decision criteria
- Show systematic approach to change

INTERVIEW 3: Aspirational, Growth-Oriented Persona
- Focus on transformation vision and future state
- Reveal motivation patterns and success drivers
- Show investment mindset and commitment factors

For each interview:
1. Create realistic dialogue with authentic language patterns from psychological analysis
2. Include emotional moments and vulnerability that reveals deeper motivations
3. Show psychological defense mechanisms and contradictions
4. Capture exact phrases and tone they would actually use based on voice analysis
5. Reveal layers of pain and desire through careful psychological probing

Make conversations feel like real customer research sessions where psychological truths emerge naturally.
"""
    
    @staticmethod
    def get_campaign_synthesis():
        """Campaign synthesis prompt - enhanced"""
        return """
Based on:
PSYCHOLOGICAL ANALYSIS: {psychological_analysis}
CONVERSION INTELLIGENCE: {conversion_intelligence}
INTERVIEW INSIGHTS: {interview_insights}

COMPREHENSIVE CAMPAIGN SYNTHESIS

Create comprehensive GTM strategy that combines psychological depth with conversion optimization:

1. CORE POSITIONING STRATEGY
- Identity transformation positioning based on psychological analysis
- Category creation opportunities using contradiction patterns
- Emotional positioning leveraging deepest psychological drivers
- Competitive differentiation using unique psychological insights

2. CONVERSION CAMPAIGN FRAMEWORK
- Multi-channel campaign strategy (paid, organic, content, email)
- Audience segmentation based on psychological profiles
- Creative testing roadmap using conversion hypotheses
- Funnel optimization using psychological conversion triggers

3. MESSAGING ARCHITECTURE
- Core messaging pillars based on identity transformation
- Voice of customer integration for authentic communication
- Objection handling using psychological contradiction analysis
- Social proof framework using peer validation psychology

4. IMPLEMENTATION ROADMAP
- 90-day campaign launch plan
- Testing and optimization schedule
- Budget allocation across channels
- Success metrics and psychological indicators

Focus on creating campaign strategy that leverages psychological depth for superior conversion performance.
"""
