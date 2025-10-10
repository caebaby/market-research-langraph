# prompts/interview_sales_prompts.py
"""
Sales Interview Agent Prompts
Aligned with 14-Section Market Research Template
Strategic sales discovery focus
"""

from typing import Dict, Any, List

class InterviewSalesPrompts:
    """
    WHY: Uncover buying dynamics through sales discovery
    WHAT: 14-section template via strategic sales dialogue
    HOW: Progressive qualification to close commitment
    """
    
    def __init__(self):
        self.sections = self._initialize_sections()
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Define sales interview approach for each section"""
        
        return {
            "1_executive_summary": """
            Sales Call Opening & Credibility:
            - Establish expertise quickly
            - Set business value focus
            - Confirm decision authority
            - Create urgency context
            - Get permission to explore deeply
            
            Opening: "I've helped 3 similar companies achieve..."
            """,
            
            "2_market_context": """
            Market Pressure Discovery:
            Sales: "What market changes are keeping leadership awake?"
            - Competitive pressures
            - Industry transformation
            - Regulatory requirements
            - Growth imperatives
            
            Probes: "What happens if you don't adapt?" "Cost of inaction?"
            """,
            
            "3_target_audience": """
            Stakeholder Mapping:
            Sales: "Walk me through your decision process"
            - Decision makers identification
            - Influence dynamics
            - Veto powers
            - Champion development
            
            Probes: "Who could kill this?" "Who benefits most?"
            """,
            
            "4_customer_psychology": """
            Business Pain Discovery:
            Sales: "What's the real problem you're solving?"
            - Surface pain vs root cause
            - Quantified impact
            - Personal stakes
            - Urgency drivers
            
            Probes: "What's this costing you?" "Why now?"
            """,
            
            "5_voice_of_customer": """
            Language Capture:
            Sales: "How do you describe this internally?"
            - Exact terminology used
            - Elevator pitch version
            - Board presentation language
            - Team communication style
            
            Note exact phrases for proposals
            """,
            
            "6_competitive_landscape": """
            COMPETITIVE DISCOVERY (PRIMARY FOCUS - 700+ words):
            
            CURRENT STATE ASSESSMENT:
            Sales: "What are you using today?"
            Buyer: "We have [current solution]..."
            Sales: "What's working well?"
            Buyer: [Lists positives - important for later]
            Sales: "What gaps are you experiencing?"
            Buyer: [Critical pain points]
            
            ALTERNATIVES EVALUATION:
            Sales: "Who else are you considering?"
            Buyer: "We're looking at [Competitor X, Y]"
            Sales: "What do you like about X?"
            Buyer: [Reveals decision criteria]
            Sales: "What concerns do you have?"
            Buyer: [Reveals differentiation opportunities]
            
            DECISION CRITERIA:
            Sales: "If you had to rank criteria, what's most important?"
            Buyer: "First would be... then... finally..."
            Sales: "What would disqualify a vendor?"
            Buyer: "Deal breakers would be..."
            Sales: "What would make this a no-brainer?"
            Buyer: "If someone could guarantee..."
            
            COMPETITIVE POSITIONING:
            Sales: "Where do others fall short?"
            Buyer: "X is too complex, Y is too expensive..."
            Sales: "What unique capability would excite you?"
            Buyer: "Something that could..."
            """,
            
            "7_positioning_strategy": """
            Category Discovery:
            Sales: "How do you categorize this solution?"
            - Budget allocation category
            - Internal positioning
            - Success metrics alignment
            - Strategic initiative connection
            
            Probes: "What bucket does this fall into?"
            """,
            
            "8_messaging_framework": """
            Message Testing:
            Sales: "If I told you we could [value prop]..."
            - Reaction assessment
            - Resonance testing
            - Objection surfacing
            - Interest indicators
            
            Test different angles for response
            """,
            
            "9_product_strategy": """
            Requirements Discovery:
            Sales: "Walk me through your ideal solution"
            - Must-have capabilities
            - Nice-to-have features
            - Integration requirements
            - User experience needs
            
            Probes: "What's negotiable?" "What's critical?"
            """,
            
            "10_pricing_strategy": """
            BUDGET QUALIFICATION (Critical section):
            
            BUDGET EXISTENCE:
            Sales: "Is there budget allocated for this?"
            Buyer: "We have budget if..."
            Sales: "What range were you planning?"
            Buyer: "We were thinking..."
            
            ROI REQUIREMENTS:
            Sales: "How do you calculate ROI?"
            Buyer: "We need to show..."
            Sales: "What payback period?"
            Buyer: "Typically 12-18 months"
            
            PRICE ANCHORING:
            Sales: "Companies your size typically invest $X-Y"
            Buyer: "That's higher/lower than expected"
            Sales: "Let me show you the value..."
            """,
            
            "11_sales_strategy": """
            SALES PROCESS ALIGNMENT (Critical section):
            
            TIMELINE DISCOVERY:
            Sales: "What's your evaluation timeline?"
            Buyer: "We need to decide by..."
            Sales: "What drives that date?"
            Buyer: "Because [compelling event]"
            
            PROCESS MAPPING:
            Sales: "What steps are required?"
            Buyer: "We need to... then... finally..."
            Sales: "Who's involved at each step?"
            Buyer: "First my team, then..."
            
            ACCELERATION:
            Sales: "What would speed this up?"
            Buyer: "If we could..."
            """,
            
            "12_marketing_strategy": """
            Information Needs:
            Sales: "What information do you need?"
            - Proof points required
            - Case study preferences
            - Content consumption style
            - Stakeholder materials
            
            Probes: "What would convince the CFO?"
            """,
            
            "13_success_metrics": """
            Success Definition:
            Sales: "How will you measure success?"
            - Business metrics
            - Personal metrics
            - Timeline expectations
            - Promotion criteria
            
            Probes: "What makes you a hero?"
            """,
            
            "14_implementation_roadmap": """
            Implementation Planning & Close:
            Sales: "Assuming we move forward, what's the plan?"
            - Resource availability
            - Change management
            - Rollout strategy
            - Success milestones
            
            Closing: "What questions remain?" "Ready to proceed?"
            """
        }
    
    def get_full_prompt(self, company_name: str, context: Dict[str, Any]) -> str:
        """Generate complete sales interview prompt"""
        
        prompt = f"""Create 3 strategic sales discovery interviews with prospects evaluating {company_name}.

INTERVIEW REQUIREMENTS:
- Minimum 2000 words total
- Progressive discovery and qualification
- Objection handling throughout
- Cover all 14 sections naturally through dialogue
- Include specific numbers, timelines, budgets

SALES TECHNIQUES TO DEMONSTRATE:
- SPIN questioning methodology
- MEDDIC qualification
- Challenger insights
- Objection reframing
- Trial closes
- Urgency creation

The interviews should include realistic moments:
- "I need to be frank with you..."
- "Our budget is tight but..."
- "My boss will ask..."
- "Compared to [Competitor]..."
- "What would it take to..."

Structure each interview to cover 4-5 sections naturally:
"""
        
        for section_key, section_prompt in self.sections.items():
            prompt += f"\n{section_key.upper()}:\n{section_prompt}\n"
        
        return prompt