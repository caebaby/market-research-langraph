# prompts/voice_prompts.py
"""
Voice of Customer Agent Prompts
Aligned with 14-Section Market Research Template
"""

from typing import Dict, Any, List

class VoicePrompts:
    """
    WHY: Capture authentic customer language across all 14 sections
    WHAT: Template focused on exact phrases and linguistic patterns
    HOW: Each section extracts specific language types
    """
    
    def __init__(self):
        self.sections = self._initialize_sections()
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Define voice extraction for each of the 14 sections"""
        
        return {
            "1_executive_summary": """
            Extract executive-level language:
            - How executives summarize problems
            - Language used in board presentations
            - Executive pain articulation
            - Strategic priority language
            - Urgency expressions from leadership
            Include 5+ exact executive quotes
            """,
            
            "2_market_context": """
            Capture market context language:
            - How customers describe market changes
            - Industry jargon and terminology
            - Competitive landscape descriptions
            - Market pressure articulations
            - Trend discussion language
            Include 10+ exact market-related phrases
            """,
            
            "3_target_audience": """
            Extract audience self-description language:
            - How they describe themselves
            - Role and identity language
            - Team description phrases
            - Capability articulations
            - Professional identity statements
            Include 10+ identity phrases
            """,
            
            "4_customer_psychology": """
            Capture psychological expression language:
            - Fear articulation phrases
            - Frustration expressions
            - Hope and aspiration language
            - Doubt and uncertainty phrases
            - Confidence and pride expressions
            Include 15+ emotional phrases
            """,
            
            "5_voice_of_customer": """
            Deep voice extraction (PRIMARY FOCUS - 40+ phrases minimum):
            
            FRUSTRATION LANGUAGE (10+ phrases):
            - "I'm so tired of..."
            - "It drives me crazy when..."
            - "Why is it so hard to..."
            - "Every day we waste..."
            Extract exact complaint language
            
            ASPIRATION LANGUAGE (10+ phrases):
            - "I wish we could..."
            - "If only we had..."
            - "Imagine if..."
            - "What I really need is..."
            Extract exact desire language
            
            OBJECTION LANGUAGE (10+ phrases):
            - "The problem with solutions like..."
            - "We've tried before and..."
            - "I don't believe..."
            - "Yeah, but what about..."
            Extract exact resistance language
            
            URGENCY LANGUAGE (10+ phrases):
            - "We need to fix this before..."
            - "Can't afford to wait..."
            - "Time is running out..."
            - "Competition is already..."
            Extract exact urgency language
            
            TRANSFORMATION LANGUAGE:
            - Before/after descriptions
            - Success story language
            - Change narrative phrases
            """,
            
            "6_competitive_landscape": """
            Extract competitive comparison language:
            - How they describe competitors
            - Comparison phrases they use
            - Switching consideration language
            - Vendor frustration expressions
            - Alternative evaluation language
            Include 10+ competitive phrases
            """,
            
            "7_positioning_strategy": """
            Capture positioning-relevant language:
            - Category description phrases
            - Differentiation language they use
            - Value articulation patterns
            - Unique benefit descriptions
            - Position preference indicators
            Include 8+ positioning phrases
            """,
            
            "8_messaging_framework": """
            Extract message-ready language:
            - Headlines from their words
            - Tagline-worthy phrases
            - Hook language patterns
            - Benefit descriptions
            - Call-to-action language
            Include 15+ message-ready phrases
            """,
            
            "9_product_strategy": """
            Capture product requirement language:
            - Feature request phrases
            - Capability descriptions
            - Integration requirements
            - Usability expectations
            - Product vision language
            Include 10+ product phrases
            """,
            
            "10_pricing_strategy": """
            Extract pricing and value language:
            - Budget discussion phrases
            - ROI articulation patterns
            - Cost justification language
            - Investment framing words
            - Value perception expressions
            Include 8+ pricing phrases
            """,
            
            "11_sales_strategy": """
            Capture sales interaction language:
            - How they describe sales process
            - Vendor evaluation language
            - Decision-making phrases
            - Objection articulations
            - Commitment expressions
            Include 10+ sales process phrases
            """,
            
            "12_marketing_strategy": """
            Extract marketing-relevant language:
            - Content preferences described
            - Information seeking patterns
            - Channel preferences stated
            - Engagement trigger words
            - Attention-getting phrases
            Include 8+ marketing phrases
            """,
            
            "13_success_metrics": """
            Capture success definition language:
            - How they measure success
            - KPI articulation patterns
            - Goal description phrases
            - Achievement language
            - Failure description words
            Include 8+ success phrases
            """,
            
            "14_implementation_roadmap": """
            Extract implementation language:
            - Timeline expectation phrases
            - Phasing preference language
            - Risk articulation patterns
            - Milestone descriptions
            - Quick win definitions
            Include 8+ implementation phrases
            """
        }
    
    def get_full_prompt(self, company_name: str, context: Dict[str, Any]) -> str:
        """
        Generate complete 14-section voice extraction prompt
        """
        
        industry = context.get("industry", "technology")
        segment = context.get("market_segment", "enterprise")
        
        prompt = f"""Extract authentic customer voice for {company_name}'s target market.
        
CONTEXT:
- Company: {company_name}
- Industry: {industry}
- Target Segment: {segment}

Generate comprehensive voice extraction following the 14-SECTION MARKET RESEARCH TEMPLATE.
Focus on EXACT customer language, not paraphrases or interpretations.

REQUIREMENTS:
- Minimum 1500 words total
- 40+ exact customer phrases in quotation marks
- Emotional authenticity in language
- Copy-ready phrases for marketing
- Use all 14 sections below:

"""
        
        for section_key, section_prompt in self.sections.items():
            section_name = section_key.replace("_", " ").upper()
            prompt += f"\n{section_name}:\n{section_prompt}\n"
        
        prompt += """
CRITICAL RULES:
- Every phrase must be in quotation marks
- Never clean up or paraphrase language
- Include emotional indicators (sighs, pauses)
- Capture industry-specific jargon
- Note where each type of language appears (forums, reviews, support)
"""
        
        return prompt