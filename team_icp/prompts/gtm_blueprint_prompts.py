# prompts/gtm_blueprint_prompts.py
"""
GTM Blueprint Agent Prompts - The Synthesis
Aligned with 14-Section Market Research Template
"""

from typing import Dict, Any, List

class GTMBlueprintPrompts:
    """
    WHY: Synthesize all insights into actionable GTM strategy
    WHAT: 14-section comprehensive blueprint
    HOW: Each section integrates insights from all agents
    """
    
    def __init__(self):
        self.sections = self._initialize_sections()
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Define synthesis approach for each of the 14 sections"""
        
        return {
            "1_executive_summary": """
            STRATEGIC SYNTHESIS EXECUTIVE SUMMARY (300+ words):
            - Core thesis integrating all insights
            - Why this strategy will win (psychological + competitive + voice)
            - Critical success factors identified
            - Investment required and expected ROI
            - Urgency drivers from all analyses
            - Risk mitigation approach
            - Success probability assessment
            """,
            
            "2_market_context": """
            INTEGRATED MARKET ANALYSIS (200+ words):
            - Market opportunity size and timing
            - Psychological readiness of market
            - Competitive dynamics creating opening
            - Customer voice indicating market shift
            - Technology and business model trends
            - Regulatory and compliance factors
            - Market maturity implications
            """,
            
            "3_target_audience": """
            UNIFIED ICP DEFINITION (200+ words):
            - Primary segments with psychological profiles
            - Secondary expansion segments
            - Anti-ICP (who not to target)
            - Buyer committee dynamics
            - Champion profile synthesis
            - Decision maker characteristics
            - End user considerations
            """,
            
            "4_customer_psychology": """
            PSYCHOLOGICAL STRATEGY INTEGRATION (300+ words):
            - Core psychological insights summary
            - How to leverage key fears
            - Identity reinforcement approach
            - Resistance mitigation tactics
            - Emotional journey design
            - Trust building sequence
            - Transformation narrative
            """,
            
            "5_voice_of_customer": """
            LANGUAGE STRATEGY DEPLOYMENT (250+ words):
            - Key phrases to use everywhere
            - Messaging hierarchy in customer words
            - Pain articulation scripts
            - Success story templates
            - Objection handling language
            - Content themes and hooks
            - SEO keyword strategy from voice
            """,
            
            "6_competitive_landscape": """
            COMPETITIVE STRATEGY SYNTHESIS (250+ words):
            - Positioning against each competitor
            - Differentiation messaging
            - Win strategies by competitor
            - Market gaps to exploit
            - Partnership opportunities
            - Disruption approach
            - Defense strategies
            """,
            
            "7_positioning_strategy": """
            UNIFIED POSITIONING STATEMENT (200+ words):
            - Core positioning integrating all insights
            - Category definition or creation
            - Psychological position owned
            - Competitive differentiation
            - Value proposition hierarchy
            - Proof points and evidence
            - Position defense plan
            """,
            
            "8_messaging_framework": """
            INTEGRATED MESSAGING ARCHITECTURE (300+ words):
            - Core narrative arc
            - Messaging by persona
            - Psychological triggers embedded
            - Competitive differentiators highlighted
            - Customer language incorporated
            - Objection preemption built in
            - Call-to-action frameworks
            """,
            
            "9_product_strategy": """
            PRODUCT ROADMAP FROM INSIGHTS (250+ words):
            - MVP from customer voice
            - Psychological safety features
            - Competitive parity requirements
            - Differentiation features
            - Platform strategy
            - Integration priorities
            - Future vision
            """,
            
            "10_pricing_strategy": """
            PSYCHOLOGY-BASED PRICING (200+ words):
            - Pricing model selection
            - Price points with anchoring
            - Package psychology
            - Competitive positioning
            - ROI articulation approach
            - Discounting guidelines
            - Contract terms
            """,
            
            "11_sales_strategy": """
            UNIFIED SALES PLAYBOOK (300+ words):
            - Sales methodology selection
            - Discovery question framework
            - Demo strategy by persona
            - Objection handling scripts
            - Competitive battle cards
            - Reference story library
            - Closing techniques
            - Channel strategy
            """,
            
            "12_marketing_strategy": """
            INTEGRATED MARKETING PLAN (300+ words):
            - Campaign architecture
            - Content strategy by stage
            - Channel selection and priority
            - Demand generation programs
            - ABM approach
            - Event strategy
            - PR and analyst relations
            - Community building
            """,
            
            "13_success_metrics": """
            COMPREHENSIVE METRICS FRAMEWORK (200+ words):
            - Leading indicators dashboard
            - Lagging indicators targets
            - Psychological engagement metrics
            - Competitive win rates
            - Voice alignment scores
            - Sales efficiency metrics
            - Marketing performance KPIs
            - Customer success metrics
            """,
            
            "14_implementation_roadmap": """
            PHASED IMPLEMENTATION PLAN (300+ words):
            
            PHASE 1 - FOUNDATION (Month 1-2):
            - Team alignment and training
            - Asset creation priorities
            - Pilot customer selection
            - Quick wins identification
            - Systems setup
            
            PHASE 2 - LAUNCH (Month 3-4):
            - Go-to-market activation
            - Campaign launch sequence
            - Sales enablement rollout
            - Partnership activation
            - PR and visibility
            
            PHASE 3 - SCALE (Month 5-6):
            - Expansion initiatives
            - Optimization based on data
            - International considerations
            - Platform development
            - Ecosystem building
            
            QUICK WINS (First 30 days):
            - 5 immediate impact actions
            - Low risk, high visibility
            - Momentum builders
            """
        }
    
    def get_full_prompt(self, company_name: str, context: Dict[str, Any]) -> str:
        """
        Generate the full GTM synthesis prompt
        This is the method called by the GTM Blueprint agent
        """
        # Extract all insights if available
        all_insights = context.get('insights', {})
        search_insights = context.get('search_insights', '')
        
        industry = context.get("industry", "technology")
        segment = context.get("market_segment", "enterprise")
        
        # Format insights for prompt
        insights_summary = self._format_insights(all_insights)
        
        prompt = f"""Create a comprehensive GTM Blueprint for {company_name}

COMPANY CONTEXT:
- Company: {company_name}
- Industry: {industry}
- Target Segment: {segment}

SYNTHESIZED INSIGHTS:
{insights_summary}

MARKET RESEARCH:
{search_insights}

INSTRUCTIONS:
Generate a complete GTM Blueprint following the 14-SECTION MARKET RESEARCH TEMPLATE.
This is the MASTER SYNTHESIS - integrate ALL insights into executable strategy.

MANDATORY SECTIONS (All 14 must be included):
1. EXECUTIVE SUMMARY - Strategic thesis and why this will win
2. MARKET CONTEXT - Market dynamics and opportunity analysis
3. TARGET AUDIENCE - ICP definition with psychological profiles
4. CUSTOMER PSYCHOLOGY - Deep psychological patterns and triggers
5. VOICE OF CUSTOMER - Exact language and phrases to use
6. COMPETITIVE LANDSCAPE - Positioning gaps and differentiation
7. POSITIONING STRATEGY - Unique market position owned
8. MESSAGING FRAMEWORK - Complete messaging architecture
9. PRODUCT STRATEGY - Product roadmap from insights
10. PRICING STRATEGY - Psychology-based pricing model
11. SALES STRATEGY - Complete sales playbook
12. MARKETING STRATEGY - Integrated marketing plan
13. SUCCESS METRICS - KPIs and measurement framework
14. IMPLEMENTATION ROADMAP - Phased rollout with quick wins

REQUIREMENTS:
- Minimum 2500 words total
- Every section must integrate insights from multiple agents
- Specific, actionable recommendations
- Include metrics, timelines, and owners
- Psychological sophistication throughout
- Customer language embedded
- Competitive differentiation clear
- Implementation realistic

Make this blueprint so complete that teams can execute immediately.
"""
        
        # Add section details
        for section_key, section_prompt in self.sections.items():
            section_name = section_key.replace("_", " ").title()
            prompt += f"\n{section_name}:\n{section_prompt}\n"
        
        return prompt
    
    def get_synthesis_prompt(self, 
                           company_name: str,
                           context: Dict[str, Any],
                           all_insights: Dict[str, Any]) -> str:
        """
        Alternative method for synthesis - calls get_full_prompt
        Kept for backward compatibility
        """
        # Add insights to context if not already there
        context['insights'] = all_insights
        return self.get_full_prompt(company_name, context)
    
    def _format_insights(self, insights: Dict) -> str:
        """Format all agent insights for inclusion in prompt"""
        
        if not insights:
            return "No prior insights available - generate comprehensive analysis based on market knowledge."
        
        formatted = ""
        
        if "psychological" in insights:
            formatted += "PSYCHOLOGICAL INSIGHTS:\n"
            for finding in insights["psychological"].get("key_findings", [])[:5]:
                formatted += f"- {finding}\n"
            fears = insights["psychological"].get("fears", [])
            if fears:
                formatted += "Key Fears:\n"
                for fear in fears[:3]:
                    formatted += f"- {fear}\n"
            formatted += "\n"
        
        if "voice" in insights:
            formatted += "VOICE OF CUSTOMER INSIGHTS:\n"
            exact_phrases = insights["voice"].get("exact_phrases", [])
            for phrase in exact_phrases[:10]:
                formatted += f'- "{phrase}"\n'
            phrase_count = insights["voice"].get("phrase_count", 0)
            if phrase_count:
                formatted += f"Total phrases captured: {phrase_count}\n"
            formatted += "\n"
        
        if "competitive" in insights:
            formatted += "COMPETITIVE INSIGHTS:\n"
            gaps = insights["competitive"].get("positioning_gaps", [])
            for gap in gaps[:5]:
                formatted += f"- {gap}\n"
            comp_count = insights["competitive"].get("competitors_count", 0)
            if comp_count:
                formatted += f"Competitors analyzed: {comp_count}\n"
            formatted += "\n"
        
        if "interview_psych" in insights:
            formatted += "PSYCHOLOGICAL INTERVIEW INSIGHTS:\n"
            for insight in insights["interview_psych"].get("key_insights", [])[:5]:
                formatted += f"- {insight}\n"
            depth = insights["interview_psych"].get("emotional_depth", 0)
            if depth:
                formatted += f"Emotional depth score: {depth:.2f}\n"
            formatted += "\n"
        
        if "interview_sales" in insights:
            formatted += "SALES INTERVIEW INSIGHTS:\n"
            formatted += "Buying Signals:\n"
            for signal in insights["interview_sales"].get("buying_signals", [])[:5]:
                formatted += f"- {signal}\n"
            formatted += "Deal Blockers:\n"
            for blocker in insights["interview_sales"].get("deal_blockers", [])[:3]:
                formatted += f"- {blocker}\n"
            formatted += "\n"
        
        return formatted if formatted else "Limited insights available - generate comprehensive strategy based on best practices."
    
    def validate_blueprint(self, blueprint: str) -> Dict[str, Any]:
        """Validate that blueprint contains all required sections"""
        
        validation = {
            "is_complete": True,
            "missing_sections": [],
            "section_scores": {}
        }
        
        required_keywords = {
            "1_executive_summary": ["thesis", "strategy", "ROI"],
            "2_market_context": ["market", "opportunity", "dynamics"],
            "3_target_audience": ["ICP", "segment", "buyer"],
            "4_customer_psychology": ["psychological", "fear", "identity"],
            "5_voice_of_customer": ["phrase", "language", "voice"],
            "6_competitive_landscape": ["competitor", "differentiation", "position"],
            "7_positioning_strategy": ["positioning", "unique", "value"],
            "8_messaging_framework": ["message", "narrative", "story"],
            "9_product_strategy": ["product", "feature", "roadmap"],
            "10_pricing_strategy": ["price", "pricing", "package"],
            "11_sales_strategy": ["sales", "discovery", "close"],
            "12_marketing_strategy": ["marketing", "campaign", "demand"],
            "13_success_metrics": ["metric", "KPI", "measure"],
            "14_implementation_roadmap": ["phase", "implement", "roadmap"]
        }
        
        blueprint_lower = blueprint.lower()
        
        for section, keywords in required_keywords.items():
            section_name = section.split("_", 1)[1].replace("_", " ").title()
            
            # Check if section header exists
            if section_name.lower() not in blueprint_lower:
                validation["missing_sections"].append(section_name)
                validation["is_complete"] = False
                validation["section_scores"][section] = 0
            else:
                # Score based on keyword presence
                keyword_count = sum(1 for kw in keywords if kw in blueprint_lower)
                score = keyword_count / len(keywords)
                validation["section_scores"][section] = score
                
                if score < 0.5:
                    validation["missing_sections"].append(f"{section_name} (incomplete)")
        
        return validation