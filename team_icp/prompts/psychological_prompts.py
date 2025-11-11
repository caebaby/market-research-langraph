# prompts/psychological_prompts.py
"""
Psychological Analysis Agent Prompts
Aligned with 14-Section Market Research Template
"""

from typing import Dict, Any, List

class PsychologicalPrompts:
    """
    WHY: Standardized prompts ensure consistent psychological analysis
    WHAT: 14-section template adapted for psychological focus
    HOW: Each section emphasizes mental models and emotional drivers
    """
    
    def __init__(self):
        self.sections = self._initialize_sections()
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Define prompts for each of the 14 sections"""
        
        return {
            "1_executive_summary": """
            Provide a psychological executive summary covering:
            - Core psychological drivers discovered
            - Key identity and fear patterns
            - Critical emotional triggers
            - Strategic implications for positioning
            - Urgency based on psychological readiness
            """,
            
            "2_market_context": """
            Analyze the psychological context of the market:
            - Industry-specific psychological patterns
            - Generational mindset shifts
            - Cultural factors affecting decisions
            - Psychological impact of market changes
            - Emotional state of the industry
            """,
            
            "3_target_audience": """
            Define target audience through psychological lens:
            - Psychological segmentation (not just demographic)
            - Identity archetypes and personas
            - Emotional maturity levels
            - Change readiness profiles
            - Psychological diversity within ICP
            """,
            
            "4_customer_psychology": """
            Deep dive into customer psychology (PRIMARY FOCUS):
            - CONSCIOUS MOTIVATIONS
              * Stated goals and objectives
              * Rational decision criteria
              * Professional aspirations
            
            - UNCONSCIOUS DRIVERS
              * Hidden fears and anxieties
              * Identity preservation needs
              * Status and social dynamics
              * Defensive mechanisms
            
            - COGNITIVE BIASES
              * Confirmation bias patterns
              * Loss aversion manifestations
              * Anchoring effects
              * Social proof requirements
            
            - EMOTIONAL LANDSCAPE
              * Fear hierarchy (what terrifies them most)
              * Aspiration hierarchy (what they dream of)
              * Shame and guilt triggers
              * Pride and validation needs
            
            - IDENTITY DYNAMICS
              * Professional self-image
              * Imposter syndrome manifestations
              * Role-based identity conflicts
              * Transformation resistance patterns
            """,
            
            "5_voice_of_customer": """
            Connect psychological patterns to language:
            - How psychological states manifest in language
            - Emotional vocabulary they use
            - Metaphors revealing mental models
            - Language patterns showing resistance
            - Words that trigger psychological safety
            """,
            
            "6_competitive_landscape": """
            Psychological analysis of competitive dynamics:
            - How competitors trigger customer fears
            - Psychological positioning of alternatives
            - Emotional associations with competitors
            - Identity implications of vendor choice
            - Switching anxiety factors
            """,
            
            "7_positioning_strategy": """
            Psychology-based positioning recommendations:
            - Identity-reinforcing position
            - Fear-mitigating approach
            - Aspiration-enabling narrative
            - Psychological differentiation
            - Emotional territory to own
            """,
            
            "8_messaging_framework": """
            Psychologically-optimized messaging:
            - Messages that bypass resistance
            - Identity-affirming language
            - Fear-acknowledgment without triggering
            - Aspiration activation phrases
            - Psychological safety builders
            """,
            
            "9_product_strategy": """
            Product implications from psychological insights:
            - Features that provide psychological safety
            - Complexity threshold based on confidence
            - Control needs and customization
            - Gradual transformation capabilities
            - Identity preservation features
            """,
            
            "10_pricing_strategy": """
            Psychological pricing considerations:
            - Price as signal of quality/status
            - Investment vs. cost framing
            - Psychological anchoring points
            - Payment terms and commitment fear
            - ROI beyond financial (ego ROI)
            """,
            
            "11_sales_strategy": """
            Psychologically-informed sales approach:
            - Building psychological safety in sales
            - Addressing unconscious objections
            - Identity-based objection handling
            - Creating vision without threat
            - Psychological closing techniques
            """,
            
            "12_marketing_strategy": """
            Marketing through psychological lens:
            - Content addressing psychological needs
            - Campaigns targeting emotional states
            - Social proof for identity validation
            - Fear-based urgency creation
            - Aspiration-based attraction
            """,
            
            "13_success_metrics": """
            Psychological success indicators:
            - Emotional engagement metrics
            - Identity alignment scores
            - Resistance reduction indicators
            - Psychological safety metrics
            - Transformation readiness tracking
            """,
            
            "14_implementation_roadmap": """
            Psychologically-sequenced implementation:
            - Start with psychological safety
            - Build identity alignment
            - Address fears systematically
            - Create small wins for confidence
            - Escalate transformation gradually
            """
        }
    
    def get_full_prompt(self, company_name: str, context: Dict[str, Any]) -> str:
        """
        Generate complete 14-section prompt for psychological analysis
        """
        
        industry = context.get("industry", "technology")
        segment = context.get("market_segment", "enterprise")
        
        prompt = f"""Conduct a comprehensive psychological analysis of {company_name}'s target market.
        
CONTEXT:
- Company: {company_name}
- Industry: {industry}
- Target Segment: {segment}

Generate a complete analysis following the 14-SECTION MARKET RESEARCH TEMPLATE.
Each section should emphasize psychological insights while maintaining business relevance.

REQUIREMENTS:
- Minimum 1200 words total
- Deep psychological sophistication
- Actionable business implications
- Use all 14 sections below:

"""
        
        for section_key, section_prompt in self.sections.items():
            section_name = section_key.replace("_", " ").upper()
            prompt += f"\n{section_name}:\n{section_prompt}\n"
        
        prompt += """
Ensure the analysis:
- Reveals unconscious motivations
- Identifies identity conflicts
- Maps emotional triggers
- Provides actionable insights
- Uses psychological frameworks
- Maintains business focus
"""
        
        return prompt
    
    def get_section_prompt(self, section_number: int) -> str:
        """Get prompt for specific section"""
        section_key = list(self.sections.keys())[section_number - 1]
        return self.sections[section_key]