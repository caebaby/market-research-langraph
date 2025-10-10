# prompts/competitor_prompts.py
"""
Competitor Analysis Agent Prompts
Aligned with 14-Section Market Research Template
"""

from typing import Dict, Any, List

class CompetitorPrompts:
    """
    WHY: Systematic competitive analysis across all market dimensions
    WHAT: 14-section template with competitive focus
    HOW: Each section analyzes competitive dynamics
    """
    
    def __init__(self):
        self.sections = self._initialize_sections()
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Define competitive analysis for each of the 14 sections"""
        
        return {
            "1_executive_summary": """
            Competitive landscape executive summary:
            - Market leader positions and share
            - Key competitive threats
            - Major positioning gaps
            - Competitive advantages to exploit
            - Urgent competitive responses needed
            """,
            
            "2_market_context": """
            Competitive market dynamics:
            - Market maturity and consolidation
            - Competitive intensity levels
            - New entrant threats
            - Disruption potential
            - Market share trends
            """,
            
            "3_target_audience": """
            Competitive audience targeting:
            - How competitors segment market
            - Underserved segments identified
            - Audience loyalty patterns
            - Switching behavior analysis
            - Competitive blind spots
            """,
            
            "4_customer_psychology": """
            Psychological competitive analysis:
            - How competitors trigger fears
            - Identity associations with brands
            - Emotional bonds to competitors
            - Psychological switching barriers
            - Mental model disruption opportunities
            """,
            
            "5_voice_of_customer": """
            Competitive voice analysis:
            - What customers say about competitors
            - Complaint patterns about alternatives
            - Praise language for competitors
            - Comparison language used
            - Switching story narratives
            """,
            
            "6_competitive_landscape": """
            Detailed competitive analysis (PRIMARY FOCUS):
            
            DIRECT COMPETITORS (Top 3-5):
            For each competitor provide:
            - Company overview and positioning
            - Market share and growth trajectory
            - Target segment and ICP overlap
            - Pricing model and ranges
            - Key strengths that win deals
            - Critical weaknesses to exploit
            - Recent strategic moves
            - Customer perception analysis
            
            INDIRECT COMPETITORS:
            - Alternative solutions
            - DIY/Internal build options
            - Status quo/Do nothing
            - Adjacent solution providers
            
            EMERGING THREATS:
            - Funded startups
            - Tech giants entering
            - Platform plays
            - New business models
            
            COMPETITIVE POSITIONING MAP:
            - Price vs. Value positions
            - Feature completeness vs. Ease
            - Innovation vs. Stability
            - Market positions visualization
            """,
            
            "7_positioning_strategy": """
            Competitive positioning opportunities:
            - Unoccupied position identification
            - Differentiation vectors available
            - Position defense strategies
            - Repositioning competitors tactics
            - Category creation potential
            """,
            
            "8_messaging_framework": """
            Competitive messaging strategy:
            - Messages competitors can't match
            - Counter-messaging tactics
            - Competitive proof points
            - Trap-setting messages
            - FUD management approach
            """,
            
            "9_product_strategy": """
            Product strategy vs. competition:
            - Feature parity requirements
            - Differentiation features
            - Competitive leapfrog opportunities
            - Partnership advantages
            - Platform strategy implications
            """,
            
            "10_pricing_strategy": """
            Competitive pricing analysis:
            - Competitor pricing models
            - Price positioning strategy
            - Value perception comparison
            - Pricing pressure points
            - Bundling/Unbundling opportunities
            """,
            
            "11_sales_strategy": """
            Competitive sales tactics:
            - Win/loss analysis patterns
            - Competitive displacement playbook
            - Objection handling differentiators
            - Proof points that win
            - Reference customer strategy
            """,
            
            "12_marketing_strategy": """
            Competitive marketing approach:
            - Share of voice analysis
            - Content gap opportunities
            - Channel advantages
            - Campaign differentiation
            - SEO/SEM competition
            """,
            
            "13_success_metrics": """
            Competitive performance metrics:
            - Market share targets
            - Win rate goals
            - Competitive displacement KPIs
            - Relative performance indicators
            - Competitive intelligence metrics
            """,
            
            "14_implementation_roadmap": """
            Competitive response timeline:
            - Immediate competitive actions
            - Quick win opportunities
            - Long-term competitive strategy
            - Defensive measures needed
            - Market entry sequencing
            """
        }
    
    def get_full_prompt(self, company_name: str, context: Dict[str, Any]) -> str:
        """
        Generate complete 14-section competitive analysis prompt
        """
        
        industry = context.get("industry", "technology")
        segment = context.get("market_segment", "enterprise")
        
        prompt = f"""Conduct comprehensive competitive analysis for {company_name}.
        
CONTEXT:
- Company: {company_name}
- Industry: {industry}
- Target Segment: {segment}

Generate complete competitive intelligence following the 14-SECTION MARKET RESEARCH TEMPLATE.
Focus on actionable competitive insights and positioning opportunities.

REQUIREMENTS:
- Minimum 1000 words total
- Identify 5+ specific competitors
- Actionable competitive strategies
- Positioning gap identification
- Use all 14 sections below:

"""
        
        for section_key, section_prompt in self.sections.items():
            section_name = section_key.replace("_", " ").upper()
            prompt += f"\n{section_name}:\n{section_prompt}\n"
        
        prompt += """
Ensure the analysis:
- Names specific competitors
- Identifies real gaps
- Provides win strategies
- Includes market data
- Offers differentiation paths
"""
        
        return prompt