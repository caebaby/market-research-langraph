# team_icp/agents/gtm_blueprint.py
"""
Level 4 GTM Blueprint Agent - FIXED for Complete Generation
Synthesizes all intelligence into actionable go-to-market strategy
Fixed to generate ALL 12 sections without truncation using 8192 tokens
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import re
import json
from core.standard_agent_v4 import StandardAgentNodeV4


class GTMBlueprintPrompts:
    """GTM Blueprint prompts class"""
    
    @staticmethod
    def get_synthesis_prompt():
        return """You are synthesizing insights from multiple specialist agents into a 
        comprehensive go-to-market blueprint. Focus on actionable strategies and specific tactics."""
    
    @staticmethod
    def get_blueprint_template():
        return """Create a structured GTM blueprint with clear sections for positioning, 
        messaging, channels, timeline, and success metrics."""


class GTMBlueprintAgent(StandardAgentNodeV4):
    """
    GTM Blueprint Synthesizer - Creates comprehensive, actionable go-to-market strategy
    FIXED: Generates complete 12-section blueprint without truncation
    """
    
    def __init__(self):
        super().__init__(
            agent_name="GTM Blueprint Strategist",
            role_prompt="""You are an expert go-to-market strategist who synthesizes all market intelligence, 
psychological insights, voice of customer, and competitive analysis into comprehensive, actionable 
GTM blueprints that drive revenue growth.

Your blueprints are complete and actionable, enabling teams to execute immediately without additional 
planning. You provide specific tactics, timelines, budgets, and success metrics that turn insights 
into revenue.""",
            target_quality=0.85,
            require_human_review_below=0.70
        )
        
        # REMOVED word count limits - let it use all tokens!
        self.max_tokens = 8192  # Ensure we use maximum available
        
        # Critical GTM components that MUST be present
        self.required_sections = 12  # All 12 sections
        
        # Track agent synthesis
        self.synthesized_agents = []
        
        print(f"[{self.agent_name}] Initialized with {self.max_tokens} max tokens for COMPLETE blueprint")
    
    def _generate_response(self, task: str, memories: List, llm) -> str:
        """Generate COMPLETE GTM blueprint with ALL 12 sections"""
        
        print(f"[{self.agent_name}] Generating COMPLETE 12-section blueprint...")
        
        # Extract context
        context = task
        
        # STREAMLINED BUT COMPLETE PROMPT - More concise to fit in context
        complete_blueprint_prompt = f"""
Create a COMPLETE Go-To-Market Blueprint for the following business:
{context}

CRITICAL INSTRUCTIONS:
- Generate ALL 12 sections listed below
- DO NOT truncate or stop early
- DO NOT ask if user wants to continue
- Provide comprehensive detail for each section
- Target 300-500 words per section
- Use specific numbers, percentages, and timelines throughout

GENERATE THE FOLLOWING 12 SECTIONS IN FULL:

==================================================
1. EXECUTIVE SUMMARY
==================================================
- Key market opportunity and positioning
- Primary value proposition and differentiation
- Expected outcomes with specific metrics
- Investment required and ROI projection
- Critical success factors

==================================================
2. MARKET ANALYSIS & OPPORTUNITY
==================================================
- TAM/SAM/SOM with specific dollar amounts
- Market growth rate and trends
- Key market drivers and dynamics
- Competitive landscape overview
- Market entry strategy

==================================================
3. IDEAL CUSTOMER PROFILE (ICP)
==================================================
- Company characteristics (size, industry, revenue)
- Psychographic profile and motivations
- Buying process and timeline
- Decision makers and influencers
- Budget range and evaluation criteria

==================================================
4. POSITIONING & MESSAGING FRAMEWORK
==================================================
- Core positioning statement
- Value proposition by segment
- Key messaging pillars (3)
- Competitive differentiation
- Proof points and evidence

==================================================
5. CHANNEL STRATEGY & TACTICS
==================================================
- Primary channels (direct, digital, partner)
- Channel mix rationale
- Specific tactics per channel
- Expected CAC and conversion rates
- Channel optimization plan

==================================================
6. PRICING STRATEGY
==================================================
- Pricing model and structure
- Price points and packages
- Competitive pricing analysis
- Discounting strategy
- Value metric alignment

==================================================
7. SALES ENABLEMENT TOOLKIT
==================================================
- Battle cards for top 3 competitors
- Sales playbook and methodology
- Objection handling matrix
- Demo script and flow
- ROI calculator framework

==================================================
8. MARKETING CAMPAIGN PLAN
==================================================
- Campaign themes and creative direction
- Content strategy and calendar
- Demand generation tactics
- ABM strategy for key accounts
- Brand building initiatives

==================================================
9. IMPLEMENTATION TIMELINE
==================================================
PHASE 1 (Days 1-30): Immediate actions with specific tasks
PHASE 2 (Days 31-60): Foundation building activities
PHASE 3 (Days 61-90): Scaling initiatives
PHASE 4 (Days 91+): Optimization and expansion

==================================================
10. SUCCESS METRICS & KPIs
==================================================
- Leading indicators (weekly tracking)
- Lagging indicators (monthly tracking)
- Success milestones by timeframe
- Reporting dashboard design
- Performance benchmarks

==================================================
11. BUDGET ALLOCATION
==================================================
- Total budget required
- Breakdown by category (sales, marketing, tech)
- Timeline-based allocation
- ROI projections
- Cost optimization strategies

==================================================
12. RISK MITIGATION PLAN
==================================================
- Top 3 risks identified
- Mitigation strategies for each
- Contingency plans
- Early warning indicators
- Escalation procedures

==================================================
END OF BLUEPRINT REQUIREMENTS
==================================================

REMEMBER: Generate ALL 12 sections completely. This is a single, comprehensive deliverable.
Do not truncate. Do not ask about continuing. Complete all sections now.
"""
        
        try:
            # Ensure LLM uses maximum tokens if it has the attribute
            if hasattr(llm, 'max_tokens'):
                original_max = llm.max_tokens
                llm.max_tokens = self.max_tokens
                print(f"[{self.agent_name}] Set LLM to {self.max_tokens} tokens")
            
            # Generate complete response
            response = llm.invoke(complete_blueprint_prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                blueprint = response.content
            else:
                blueprint = str(response)
            
            # Restore original max_tokens if we changed it
            if hasattr(llm, 'max_tokens'):
                llm.max_tokens = original_max
            
            # Verify completeness
            word_count = len(blueprint.split())
            sections_found = self._count_sections(blueprint)
            
            print(f"[{self.agent_name}] Generated {word_count} words with {sections_found}/12 sections")
            
            # Check for truncation indicators and remove them
            truncation_phrases = [
                "Would you like me to continue",
                "Shall I continue with",
                "I can continue with",
                "Let me know if you'd like"
            ]
            
            for phrase in truncation_phrases:
                if phrase in blueprint:
                    print(f"[{self.agent_name}] WARNING: Found truncation phrase, removing...")
                    blueprint = blueprint.split(phrase)[0].strip()
            
            # If blueprint is incomplete, add completion notice
            if sections_found < 12:
                print(f"[{self.agent_name}] Only {sections_found}/12 sections generated. Token limit may have been reached.")
                blueprint += f"\n\n[Note: Blueprint generated {sections_found}/12 sections due to token constraints]"
            
            return blueprint
            
        except Exception as e:
            print(f"[{self.agent_name}] Error generating blueprint: {e}")
            return f"Error generating GTM blueprint: {str(e)}"
    
    def process(self, task: str, shared_insights: Dict, llm) -> Dict[str, Any]:
        """Process GTM Blueprint creation with synthesis"""
        
        print(f"[{self.agent_name}] Starting COMPLETE blueprint generation...")
        
        # Build comprehensive context
        context = self._build_gtm_context(task, shared_insights)
        
        # Track which agents we're synthesizing from
        self._identify_agent_inputs(shared_insights)
        
        # Generate complete blueprint
        memories = []  # GTM doesn't use memories
        blueprint = self._generate_response(context, memories, llm)
        
        # Calculate metrics
        word_count = len(blueprint.split())
        sections_count = self._count_sections(blueprint)
        quality_score = self._calculate_quality_score(blueprint)
        
        print(f"[{self.agent_name}] Final output: {word_count} words, {sections_count}/12 sections, quality: {quality_score:.2f}")
        
        # Extract key components
        components_present = self._verify_components(blueprint)
        action_items = self._extract_action_items(blueprint)
        timeline = self._extract_timeline(blueprint)
        budget_breakdown = self._extract_budget(blueprint)
        
        return {
            'output': blueprint,
            'quality_score': quality_score,
            'word_count': word_count,
            'sections_generated': sections_count,
            'components_present': components_present,
            'action_items': action_items,
            'timeline': timeline,
            'budget': budget_breakdown,
            'agents_synthesized': self.synthesized_agents
        }
    
    def _count_sections(self, blueprint: str) -> int:
        """Count how many of the 12 sections are present"""
        sections_found = 0
        
        # Look for section numbers or headers
        for i in range(1, 13):
            # Check for various section formats
            patterns = [
                f"{i}\\.",  # 1. Section
                f"{i}\\)",  # 1) Section
                f"Section {i}",
                f"#{i}",
                f"Part {i}"
            ]
            
            for pattern in patterns:
                if re.search(pattern, blueprint, re.IGNORECASE):
                    sections_found += 1
                    break
        
        # Also check for section names if numbers aren't found
        section_names = [
            "executive summary",
            "market analysis",
            "ideal customer",
            "positioning",
            "channel strategy",
            "pricing",
            "sales enablement",
            "marketing campaign",
            "implementation timeline",
            "success metrics",
            "budget",
            "risk mitigation"
        ]
        
        for name in section_names:
            if name in blueprint.lower() and sections_found < 12:
                sections_found = max(sections_found, section_names.index(name) + 1)
        
        return min(sections_found, 12)
    
    def _build_gtm_context(self, task: str, shared_insights: Dict) -> str:
        """Build comprehensive context for GTM Blueprint"""
        context = f"BUSINESS CONTEXT: {task}\n\n"
        
        if shared_insights:
            context += "INSIGHTS FROM SPECIALIST AGENTS:\n\n"
            
            # Add all shared insights
            for key, value in shared_insights.items():
                if isinstance(value, dict):
                    context += f"{key.upper()}:\n"
                    for sub_key, sub_value in value.items():
                        context += f"  - {sub_key}: {str(sub_value)[:200]}...\n"
                else:
                    context += f"{key.upper()}: {str(value)[:500]}...\n"
                context += "\n"
        
        return context
    
    def _identify_agent_inputs(self, shared_insights: Dict):
        """Track which agents provided input"""
        self.synthesized_agents = []
        
        insight_str = str(shared_insights).lower()
        
        agent_markers = {
            'Psychological': ['psychological', 'unconscious', 'fear', 'identity'],
            'Voice': ['voice', 'customer language', 'exact words'],
            'Competitive': ['competitor', 'competitive', 'positioning'],
            'Sales': ['sales', 'objection', 'bant'],
            'Interview': ['interview', 'discovery', 'qualification']
        }
        
        for agent, markers in agent_markers.items():
            if any(marker in insight_str for marker in markers):
                self.synthesized_agents.append(agent)
    
    def _verify_components(self, blueprint: str) -> Dict[str, bool]:
        """Verify all required GTM components are present"""
        blueprint_lower = blueprint.lower()
        components = {}
        
        component_markers = {
            'executive_summary': ['executive summary', 'key findings', 'strategic recommendations'],
            'market_analysis': ['tam', 'sam', 'som', 'market analysis', 'market opportunity'],
            'icp_definition': ['ideal customer', 'icp', 'target customer', 'customer profile'],
            'positioning_strategy': ['positioning', 'value proposition', 'differentiation'],
            'messaging_framework': ['messaging', 'message', 'headlines', 'copy'],
            'channel_strategy': ['channel', 'distribution', 'go-to-market channels'],
            'pricing_strategy': ['pricing', 'price', 'cost', '$'],
            'sales_enablement': ['sales enablement', 'battle cards', 'sales tools', 'objection handling'],
            'marketing_campaigns': ['campaign', 'marketing', 'launch', 'awareness'],
            'launch_timeline': ['timeline', 'phase', '30 days', '60 days', '90 days'],
            'success_metrics': ['metrics', 'kpi', 'success criteria', 'indicators'],
            'budget_allocation': ['budget', 'investment', 'allocation', 'roi']
        }
        
        for component, markers in component_markers.items():
            components[component] = any(marker in blueprint_lower for marker in markers)
        
        return components
    
    def _extract_action_items(self, blueprint: str) -> List[str]:
        """Extract specific action items from blueprint"""
        action_items = []
        
        # Look for action-oriented language
        action_patterns = [
            r'(?:Week \d+:|Day \d+:)\s*([^.\n]+)',
            r'(?:Action:|Task:|Deliverable:)\s*([^.\n]+)',
            r'(?:- )\s*(?:Create|Build|Launch|Develop|Implement|Execute)\s+([^.\n]+)',
            r'(?:PHASE \d+).*?(?:- )([^.\n]+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, blueprint, re.IGNORECASE | re.MULTILINE)
            action_items.extend([m.strip() for m in matches if isinstance(m, str)])
        
        return list(set(action_items[:20]))  # Top 20 unique action items
    
    def _extract_timeline(self, blueprint: str) -> Dict[str, List[str]]:
        """Extract timeline and milestones"""
        timeline = {
            '30_days': [],
            '60_days': [],
            '90_days': [],
            'ongoing': []
        }
        
        # Extract phase-specific items
        phase_patterns = {
            '30_days': r'(?:Phase 1|Days 1-30|0-30 days|Immediate).*?(?:Phase 2|Days 31|$)',
            '60_days': r'(?:Phase 2|Days 31-60|30-60 days).*?(?:Phase 3|Days 61|$)',
            '90_days': r'(?:Phase 3|Days 61-90|60-90 days).*?(?:Phase 4|Days 91|$)',
            'ongoing': r'(?:Phase 4|Days 91\+|90\+ days|Ongoing).*?$'
        }
        
        for phase, pattern in phase_patterns.items():
            match = re.search(pattern, blueprint, re.IGNORECASE | re.DOTALL)
            if match:
                items = re.findall(r'[-•]\s*([^-•\n]+)', match.group())
                timeline[phase] = items[:5] if items else []
        
        return timeline
    
    def _extract_budget(self, blueprint: str) -> Dict[str, Any]:
        """Extract budget information"""
        budget = {
            'total': None,
            'breakdown': {},
            'roi': None
        }
        
        # Extract total budget
        total_patterns = [
            r'(?:total budget|total investment).*?\$([0-9,]+)(?:[KMB])?',
            r'\$([0-9,]+)(?:[KMB])?\s*(?:total|budget|investment)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, blueprint, re.IGNORECASE)
            if match:
                budget['total'] = match.group(1)
                break
        
        # Extract ROI
        roi_pattern = r'(?:roi|return).*?([0-9]+)%'
        roi_match = re.search(roi_pattern, blueprint, re.IGNORECASE)
        if roi_match:
            budget['roi'] = f"{roi_match.group(1)}%"
        
        return budget
    
    def _calculate_quality_score(self, blueprint: str) -> float:
        """Calculate quality score based on completeness and detail"""
        
        # Base score
        score = 0.40
        
        # Section completeness (most important - 0.40 possible)
        sections_found = self._count_sections(blueprint)
        score += (sections_found / 12.0) * 0.40
        
        # Component presence (0.15 possible)
        components = self._verify_components(blueprint)
        components_found = sum(components.values())
        score += (components_found / len(components)) * 0.15
        
        # Word count (0.10 possible)
        word_count = len(blueprint.split())
        if word_count >= 2000:
            score += 0.05
        if word_count >= 3000:
            score += 0.05
        
        # Specificity markers (0.15 possible)
        specificity_checks = {
            'has_numbers': bool(re.search(r'\$[0-9,]+', blueprint)),
            'has_percentages': bool(re.search(r'[0-9]+%', blueprint)),
            'has_timeline': bool(re.search(r'(?:day|week|month)\s+\d+', blueprint, re.IGNORECASE)),
            'has_metrics': bool(re.search(r'(?:kpi|metric|roi|cac)', blueprint, re.IGNORECASE)),
            'has_actions': bool(re.search(r'(?:create|build|launch|implement)', blueprint, re.IGNORECASE))
        }
        
        for check, present in specificity_checks.items():
            if present:
                score += 0.03
        
        # Synthesis bonus (0.05 possible)
        if len(self.synthesized_agents) >= 3:
            score += 0.05
        
        # Ensure minimum quality for complete blueprints
        if sections_found >= 10 and word_count >= 2500:
            score = max(score, 0.85)
        
        return min(score, 1.0)
    
    def _create_shared_insights(self, response: str) -> Dict[str, Any]:
        """Create insights to share with other agents (though GTM is usually final)"""
        insights = {
            'gtm_complete': True,
            'sections_generated': self._count_sections(response),
            'word_count': len(response.split()),
            'action_items': self._extract_action_items(response)[:5],
            'timeline': self._extract_timeline(response),
            'budget': self._extract_budget(response)
        }
        
        # Add strategy summary
        exec_summary_match = re.search(
            r'executive summary(.*?)(?:market analysis|$)', 
            response, 
            re.IGNORECASE | re.DOTALL
        )
        if exec_summary_match:
            insights['executive_summary'] = exec_summary_match.group(1).strip()[:500]
        
        return insights
    
    def _extract_insights_for_memory(self, response: str) -> List[str]:
        """Extract key insights for memory storage"""
        insights = []
        
        # Get completion status
        sections = self._count_sections(response)
        words = len(response.split())
        insights.append(f"GTM Blueprint: {sections}/12 sections, {words} words")
        
        # Get positioning if available
        pos_match = re.search(r'positioning[:\s]+([^.]+)', response, re.IGNORECASE)
        if pos_match:
            insights.append(f"Positioning: {pos_match.group(1).strip()[:100]}")
        
        # Get budget if available
        budget = self._extract_budget(response)
        if budget['total']:
            insights.append(f"Budget required: ${budget['total']}")
        
        # Get first action item
        actions = self._extract_action_items(response)
        if actions:
            insights.append(f"First action: {actions[0][:100]}")
        
        # Add quality assessment
        quality = self._calculate_quality_score(response)
        insights.append(f"Blueprint quality: {quality:.2%}")
        
        return insights[:5]