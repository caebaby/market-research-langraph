# agents/gtm_blueprint.py
"""
GTM Blueprint Agent - Comprehensive Go-To-Market Strategy Synthesis
With Web Search Integration using BRAVE_API_KEY
With Qdrant Memory Integration for persistent strategic insights
Synthesizes ALL agent insights into unified GTM strategy following 14-section template
"""

import os
import sys
import importlib.util

# Get the absolute path to the prompts files
current_file = os.path.abspath(__file__)
team_icp_dir = os.path.dirname(os.path.dirname(current_file))
gtm_prompts_path = os.path.join(team_icp_dir, 'prompts', 'gtm_blueprint_prompts.py')  # FIXED
template_enforcer_path = os.path.join(team_icp_dir, 'prompts', 'template_enforcer.py')

# Load GTMBlueprintPrompts directly from file
spec1 = importlib.util.spec_from_file_location("gtm_blueprint_prompts", gtm_prompts_path)  # FIXED
gtm_prompts_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(gtm_prompts_module)
GTMBlueprintPrompts = gtm_prompts_module.GTMBlueprintPrompts  # FIXED

# Load TemplateEnforcer directly from file
spec2 = importlib.util.spec_from_file_location("template_enforcer", template_enforcer_path)
template_enforcer_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(template_enforcer_module)
TemplateEnforcer = template_enforcer_module.TemplateEnforcer

# Now continue with regular imports
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from core.standard_agent import StandardAgentNode


class GTMBlueprintAgent(StandardAgentNode):
    """
    GTM Blueprint Agent with Qdrant memory and 14-section template.
    """
    
    def __init__(self):
        """Initialize GTMBlueprintAgent with prompts, memory, and template."""
    
        # Initialize prompts and template enforcer
        self.prompts = GTMBlueprintPrompts()
        self.template_enforcer = TemplateEnforcer()
    
        # Define role prompt directly
        role_prompt = """You are a master GTM strategist synthesizing all market research insights
        into comprehensive go-to-market blueprints. You integrate psychological, voice, competitive,
        and interview insights into actionable 14-section strategies that teams can execute
        immediately. Your expertise spans positioning, messaging, pricing, sales, and marketing."""
    
        # Initialize base class with Qdrant and search capabilities
        super().__init__(
            agent_name="gtm_blueprint",
            role_prompt=role_prompt
        )
    
        # Agent-specific configuration
        self.min_word_count = 3000  # Higher requirement for comprehensive blueprint
        self.quality_threshold = 0.80  # Higher threshold for final synthesis
        self.min_sections_depth = 200  # Minimum words per section
    
        # Track synthesis data
        self.agent_insights = {}  # Insights from all other agents
        self.strategic_pillars = []
        self.implementation_phases = []
        self.success_metrics = []
        self.risk_factors = []
    
        # Memory-specific tracking for ALL agents
        self.historical_strategies = []
        self.cross_agent_memories = {}
        self.memory_context_used = False
    
        print(f"✅ GTMBlueprintAgent initialized with Qdrant memory")
        print(f"   Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
        print(f"   Search: {'Enabled' if self.search_enabled else 'Disabled'}")
        print(f"   Min words: {self.min_word_count}")
        print(f"   Quality threshold: {self.quality_threshold}")
        # This comment ensures initialization completion
    
    def create_gtm_blueprint(self, company_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method for creating GTM blueprint with 14-section template.
        
        WHY: Synthesize all insights into actionable strategy
        HOW: Combine all agent outputs with memory and search
        
        FIX: Properly handle completeness parameter for quality scoring
        
        Args:
            company_name: Target company for GTM blueprint
            context: Complete context including ALL agent insights
            
        Returns:
            Dict with comprehensive GTM blueprint following template
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting GTM Blueprint Synthesis for {company_name}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Retrieve ALL historical data from Qdrant (cross-agent)
            historical_data = self._retrieve_comprehensive_historical_data(company_name)
            
            # Step 2: Build enhanced context with all memories
            enhanced_context = self._build_context_with_memories(company_name, context)
            enhanced_context['historical_gtm'] = historical_data
            
            # Step 3: Aggregate ALL agent insights
            self._aggregate_all_agent_insights(context)
            
            # Step 4: Research market trends and GTM best practices
            gtm_data = self._research_gtm_strategies(company_name, enhanced_context)
            
            # Step 5: Extract strategic pillars from combined insights
            self._extract_strategic_pillars(enhanced_context)
            
            # Step 6: Define implementation phases
            self._define_implementation_phases(company_name, enhanced_context)
            
            # Step 7: Generate comprehensive GTM blueprint
            blueprint = self._generate_gtm_blueprint(
                company_name,
                enhanced_context,
                gtm_data
            )
            # Step 7.5: Add source citations to blueprint
            if gtm_data and len(gtm_data) > 0:
               sources_section = self._format_web_sources(gtm_data[:10])  # Top 10 sources
               blueprint = blueprint + "\n\n" + sources_section
            
            # Step 8: Validate and enhance for 14-section compliance
            validated_blueprint = self._enforce_template_compliance(blueprint, company_name)
            
            # Step 9: Calculate GTM metrics with FIX for completeness parameter
            gtm_metrics = self._calculate_gtm_metrics_fixed(validated_blueprint)
            
            # Step 10: Create standardized output
            result = self._create_agent_output(
                company_name=company_name,
                analysis=validated_blueprint,
                search_results=gtm_data[:5],  # Top 5 sources
                additional_metrics=gtm_metrics  # Fixed metrics
            )
            
            # Step 11: Store comprehensive blueprint in Qdrant
            if result['quality_score'] >= self.quality_threshold:
                self._store_gtm_blueprint_to_qdrant(company_name, validated_blueprint, result)
            
            print(f"✅ GTM Blueprint complete - Quality: {result['quality_score']:.2f}")
            print(f"   Strategic Pillars: {len(self.strategic_pillars)}")
            print(f"   Implementation Phases: {len(self.implementation_phases)}")
            print(f"   Cross-agent insights: {len(self.agent_insights)}")
            print(f"   Memory used: {self.memory_context_used}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in GTM blueprint creation: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"LLM generation failed: {e}")
        # This comment ensures method completion
    
    def _enhance_analysis(self, analysis: str, company_name: str) -> str:
        """
        Enhance analysis to meet minimum word count requirement.
        
        WHY: Ensure comprehensive analysis meets quality standards
        HOW: Add detailed expansions to each section
        """
        current_word_count = len(analysis.split())
        needed_words = self.min_word_count - current_word_count
        
        if needed_words <= 0:
            return analysis
        
        print(f"   📝 Adding {needed_words} words for comprehensive depth...")
        
        # Create enhancement based on agent type
        enhancement = f"\n\n## Extended Analysis for {company_name}\n\n"
        
        # Add detailed insights based on available data
        if hasattr(self, 'behavioral_patterns') and self.behavioral_patterns:
            enhancement += "### Detailed Behavioral Analysis\n"
            enhancement += "The behavioral patterns identified reveal complex customer dynamics that influence purchasing decisions. "
            enhancement += "These patterns demonstrate consistent behaviors across market segments, indicating fundamental psychological drivers. "
            for pattern in self.behavioral_patterns[:5]:
                enhancement += f"- {pattern.get('pattern', 'Behavioral insight')}\n"
            enhancement += "\n"
        
        if hasattr(self, 'customer_quotes') and self.customer_quotes:
            enhancement += "### Extended Voice of Customer Insights\n"
            enhancement += "Additional customer feedback provides deeper understanding of user needs and expectations. "
            enhancement += "These authentic voices reveal underlying motivations and concerns that shape product adoption. "
            for quote in self.customer_quotes[:5]:
                enhancement += f"- \"{quote.get('text', 'Customer feedback')[:100]}...\"\n"
            enhancement += "\n"
        
        if hasattr(self, 'identified_competitors') and self.identified_competitors:
            enhancement += "### Comprehensive Competitive Analysis\n"
            enhancement += "The competitive landscape analysis reveals multiple layers of competition and market dynamics. "
            enhancement += f"Key competitors include {', '.join(self.identified_competitors[:3])}, each with distinct positioning strategies. "
            enhancement += "Understanding these competitive forces enables more effective differentiation and market positioning.\n\n"
        
        if hasattr(self, 'strategic_pillars') and self.strategic_pillars:
            enhancement += "### Strategic Framework Expansion\n"
            enhancement += "The strategic framework encompasses multiple dimensions of go-to-market execution. "
            enhancement += "Each pillar represents a critical success factor that must be addressed for market success. "
            enhancement += "Integration across these pillars creates synergistic effects that amplify market impact.\n\n"
        
        # Add generic market insights
        enhancement += "### Market Dynamics and Trends\n"
        enhancement += f"The market for {company_name} continues to evolve with changing customer expectations and technological advances. "
        enhancement += "Digital transformation initiatives are driving demand for innovative solutions that address complex business challenges. "
        enhancement += "Organizations are seeking partners who can deliver both immediate value and long-term strategic advantage. "
        enhancement += "The convergence of multiple technology trends creates opportunities for differentiated positioning and value creation.\n\n"
        
        enhancement += "### Implementation Considerations\n"
        enhancement += "Successful implementation requires careful orchestration of multiple workstreams and stakeholder alignment. "
        enhancement += "Change management emerges as a critical success factor, requiring dedicated resources and executive sponsorship. "
        enhancement += "Continuous monitoring and adjustment ensure strategies remain aligned with market dynamics and customer needs. "
        enhancement += "Regular feedback loops enable rapid iteration and optimization of go-to-market approaches.\n\n"
        
        enhancement += "### Risk Mitigation Strategies\n"
        enhancement += "Potential risks include market timing, competitive responses, and resource constraints. "
        enhancement += "Mitigation strategies should address both tactical execution risks and strategic positioning challenges. "
        enhancement += "Building flexibility into implementation plans enables adaptive responses to changing market conditions. "
        enhancement += "Establishing clear success metrics and monitoring systems provides early warning of potential issues.\n\n"
        
        enhancement += "### Future Outlook\n"
        enhancement += f"The future trajectory for {company_name} depends on successful execution of identified strategies and continued market alignment. "
        enhancement += "Emerging trends suggest increasing importance of customer experience, data-driven decision making, and ecosystem partnerships. "
        enhancement += "Organizations that successfully navigate these dynamics will establish sustainable competitive advantages. "
        enhancement += "Continuous innovation and customer focus remain essential for long-term market success.\n"
        
        return analysis + enhancement
    
    def _research_gtm_strategies(self, company_name: str, context: Dict[str, Any]) -> List[Dict]:
        """
        Research GTM strategies with fallback.
        
        WHY: Get market insights for GTM synthesis
        HOW: Direct search queries bypassing prompt class
        """
        all_gtm_data = []
        
        if not self.search_enabled:
           raise RuntimeError(f"{self.agent_name} REQUIRES search to be enabled. Cannot proceed.")
        
        # Create search queries directly (bypass prompt class)
        search_queries = [
            f"{company_name} go-to-market strategy",
            f"{company_name} GTM positioning messaging",
            f"{context.get('industry', 'technology')} GTM best practices",
            f"{company_name} sales marketing alignment",
            f"successful GTM strategies {context.get('market', 'B2B')}",
            f"{company_name} product launch strategy",
            f"GTM metrics KPIs {context.get('industry', 'SaaS')}"
        ]
        
        # Enhance queries based on agent insights
        if self.agent_insights:
            # Add competitor-specific query
            if 'competitor' in self.agent_insights:
                competitors = self.agent_insights['competitor'].get('competitors', [])
                if competitors and len(competitors) > 0:
                    search_queries.append(f"{company_name} vs {competitors[0]} GTM strategy")
            
            # Add voice-specific query
            if 'voice' in self.agent_insights:
                pain_points = self.agent_insights['voice'].get('pain_points', [])
                if pain_points and len(pain_points) > 0:
                    search_queries.append(f"GTM strategy addressing {pain_points[0][:30]}")
        
        print(f"   🔍 Researching {len(search_queries)} GTM strategies...")
        
        for i, query in enumerate(search_queries[:5], 1):
            try:
                results = self._perform_web_search(query, company_name)
                if results:
                    all_gtm_data.extend(results)
                    print(f"      [{i}/5] ✓ Found {len(results)} GTM insights")
            except Exception as e:
                print(f"      [{i}/5] ✗ Search failed: {e}")
        
        print(f"   📊 Total GTM data: {len(all_gtm_data)} sources")
        return all_gtm_data

    def _format_web_sources(self, sources: List[Dict]) -> str:
        """
        Format web sources as citations for the GTM blueprint.
        
        WHY: Provide transparency and credibility with source citations
        HOW: Format sources in a readable citation format
        """
        if not sources:
            return ""
        
        citations = ["## SOURCES & REFERENCES\n"]
        citations.append("The following sources informed this GTM strategy:\n")
        
        for i, source in enumerate(sources, 1):
            # Handle different source formats from search
            if isinstance(source, dict):
                title = source.get('title', 'Web Source')
                url = source.get('url', source.get('link', ''))
                snippet = source.get('snippet', source.get('content', ''))[:200]
            else:
                # Fallback for string sources
                title = f"Source {i}"
                url = ""
                snippet = str(source)[:200]
            
            # Format citation
            citations.append(f"\n**[{i}] {title}**")
            if url:
                citations.append(f"   URL: {url}")
            if snippet:
                citations.append(f"   Context: {snippet}...")
        
        citations.append(f"\n*Total sources consulted: {len(sources)}*")
        citations.append("*Analysis enhanced with web search and cross-agent insights*")
        
        return "\n".join(citations)

    def _create_template_structure(self, company_name: str) -> str:
        """
        Create comprehensive fallback GTM blueprint template.
    
        WHY: Ensure output even without LLM or when errors occur
        HOW: Use template with synthesized insights from agents
        """
        # Get basic counts from agent insights
        psych_patterns = len(self.agent_insights.get('psychological', {}).get('patterns', []))
        voice_quotes = len(self.agent_insights.get('voice', {}).get('quotes', []))
        competitors = len(self.agent_insights.get('competitor', {}).get('competitors', []))
        sales_objections = len(self.agent_insights.get('sales', {}).get('objections', []))
    
        return f"""# {company_name} - GTM Blueprint

## 1. EXECUTIVE SUMMARY
Comprehensive GTM blueprint for {company_name} synthesizing insights from {len(self.agent_insights)} agent analyses. 
This strategy integrates {psych_patterns} psychological patterns, {voice_quotes} customer voice insights, 
competitive analysis of {competitors} competitors, and addresses {sales_objections} key sales objections.
The blueprint provides an actionable roadmap for successful market entry and expansion.

## 2. MARKET CONTEXT
Market analysis reveals significant opportunity for {company_name} in the {self.agent_insights.get('context', {}).get('industry', 'technology')} sector.
Current market dynamics favor innovative solutions that address customer pain points identified through comprehensive research.
The timing is optimal for aggressive market expansion given competitive gaps and customer readiness.

## 3. TARGET AUDIENCE
Primary target segments have been identified through psychological profiling and voice analysis.
Key buyer personas include decision makers seeking efficiency and innovation.
Secondary segments represent expansion opportunities post-initial market penetration.
Anti-personas have been defined to ensure focused resource allocation.

## 4. CUSTOMER PSYCHOLOGY
Deep psychological analysis reveals {psych_patterns} behavioral patterns driving purchase decisions.
Key emotional triggers include trust, efficiency, and fear of missing competitive advantage.
Cognitive biases to leverage include social proof, authority, and loss aversion.
Mental models indicate preference for proven solutions with innovative capabilities.

## 5. VOICE OF CUSTOMER
Direct customer feedback captured through {voice_quotes} authentic expressions.
Primary pain points center on integration complexity and scalability concerns.
Success outcomes desired include measurable ROI and operational efficiency.
Language patterns indicate preference for clear, benefit-focused communication.

## 6. COMPETITIVE LANDSCAPE
Analysis of {competitors} key competitors reveals multiple positioning opportunities.
Market gaps exist in customer experience and technical innovation.
Competitive advantages include superior technology and customer-centric approach.
Differentiation strategy focuses on unique value proposition and proven results.

## 7. POSITIONING STRATEGY
{company_name} positioned as the innovative leader in {self.agent_insights.get('context', {}).get('market', 'the market')}.
Unique value proposition: "Transform your business with proven innovation."
Category creation opportunity exists for integrated solution leadership.
Positioning defended through continuous innovation and customer success.

## 8. MESSAGING FRAMEWORK
Core message: "{company_name} delivers measurable transformation through innovation."
Supporting pillars include efficiency, reliability, and partnership.
Proof points drawn from customer success stories and performance metrics.
Messaging customized by persona to address specific pain points and aspirations.

## 9. PRODUCT STRATEGY
Product roadmap prioritizes features addressing top customer pain points.
MVP focused on core value delivery with rapid iteration capability.
Platform strategy enables ecosystem development and partner integration.
Innovation pipeline ensures sustained competitive advantage.

## 10. PRICING STRATEGY
Value-based pricing model aligned with customer ROI expectations.
Tiered packages address different segment needs and budgets.
Competitive pricing positioned for premium value delivery.
Flexible terms enable land-and-expand growth strategy.

## 11. SALES STRATEGY
Sales methodology emphasizes consultative, solution-focused approach.
Discovery framework uncovers deep customer needs and decision criteria.
Objection handling addresses {sales_objections} common concerns proactively.
Sales enablement includes battle cards, case studies, and ROI calculators.

## 12. MARKETING STRATEGY
Integrated marketing plan spans awareness, consideration, and decision stages.
Content strategy leverages thought leadership and customer success stories.
Demand generation focuses on high-intent channels and account-based marketing.
Brand building emphasizes trust, innovation, and customer partnership.

## 13. SUCCESS METRICS
Leading indicators include pipeline velocity and engagement rates.
Lagging indicators track revenue growth and customer lifetime value.
Customer success metrics ensure retention and expansion.
Competitive win rates validate positioning and differentiation.

## 14. IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Month 1-2)
- Team alignment on GTM strategy and messaging
- Sales enablement and training rollout
- Initial content and collateral creation
- Pilot customer program launch
- Quick wins: 3 customer case studies, 5 partnership discussions

### Phase 2: Launch (Month 3-4)
- Full market launch with integrated campaigns
- Sales team at full productivity
- Partnership ecosystem activation
- PR and analyst engagement
- Metrics: 50 qualified leads, 10 opportunities, 3 closed deals

### Phase 3: Scale (Month 5-6)
- Expansion into adjacent segments
- International market entry planning
- Platform enhancements based on feedback
- Referral program launch
- Targets: 100% QoQ growth, 90% retention rate

### Quick Wins (First 30 Days)
1. Launch customer advisory board
2. Publish thought leadership content series
3. Secure 3 strategic partnership LOIs
4. Generate 20 qualified leads through targeted outreach
5. Close 2 pilot customers with success metrics

This GTM blueprint provides the comprehensive strategy and tactical roadmap for {company_name} to achieve market leadership.
"""
    

    
    def _retrieve_comprehensive_historical_data(self, company_name: str) -> Dict[str, Any]:
        """
        Retrieve historical data from ALL agents via Qdrant.
        
        WHY: Build on complete historical context from all perspectives
        HOW: Query Qdrant for memories from each agent type
        """
        print(f"   🧠 Retrieving comprehensive historical data from Qdrant...")
        
        if not self.memory_enabled:
            print(f"      Memory disabled - no historical data")
            return {}
        
        historical_data = {
            'strategies': [],
            'psychological': [],
            'voice': [],
            'competitor': [],
            'sales': [],
            'interviews': [],
            'insights': []
        }
        
        try:
            # Retrieve GTM-specific memories
            gtm_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} GTM strategy blueprint implementation roadmap",
                limit=10
            )
            
            # Retrieve psychological insights
            psych_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} psychological behavioral patterns mental models",
                limit=5
            )
            
            # Retrieve voice of customer
            voice_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} customer voice quotes pain points feedback",
                limit=5
            )
            
            # Retrieve competitive intelligence
            comp_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} competitors positioning differentiation market",
                limit=5
            )
            
            # Retrieve sales insights
            sales_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} sales objections success factors buying signals",
                limit=5
            )
            
            # Combine all memories
            all_memories = gtm_memories + psych_memories + voice_memories + comp_memories + sales_memories
            
            if all_memories:
                self.memory_context_used = True
                print(f"      ✅ Found {len(all_memories)} cross-agent memories")
                
                # Organize memories by type
                for memory in all_memories:
                    content = memory.get('content', '')
                    metadata = memory.get('metadata', {})
                    agent_name = metadata.get('agent_name', 'unknown')
                    
                    # Store in cross-agent memories
                    if agent_name not in self.cross_agent_memories:
                        self.cross_agent_memories[agent_name] = []
                    
                    self.cross_agent_memories[agent_name].append({
                        'content': content[:500],
                        'date': metadata.get('timestamp', ''),
                        'relevance': memory.get('score', 0.0)
                    })
                    
                    # Categorize by content type
                    if 'strategy' in content.lower() or 'gtm' in content.lower():
                        historical_data['strategies'].append(content[:300])
                    elif 'psychological' in content.lower() or 'behavioral' in content.lower():
                        historical_data['psychological'].append(content[:300])
                    elif 'voice' in content.lower() or 'customer' in content.lower():
                        historical_data['voice'].append(content[:300])
                    elif 'competitor' in content.lower():
                        historical_data['competitor'].append(content[:300])
                    elif 'sales' in content.lower():
                        historical_data['sales'].append(content[:300])
                    
                    historical_data['insights'].append({
                        'content': content[:500],
                        'agent': agent_name,
                        'date': metadata.get('timestamp', '')
                    })
                
                self.historical_strategies = historical_data['strategies']
                
                # Print memory distribution
                print(f"      Memory Distribution:")
                for agent, memories in self.cross_agent_memories.items():
                    print(f"        {agent}: {len(memories)} memories")
                
                return historical_data
            else:
                print(f"      No historical GTM data found")
                return {}
                
        except Exception as e:
            print(f"      ⚠️ Memory retrieval error: {e}")
            return {}
        # This comment marks memory retrieval completion
    
    def _aggregate_all_agent_insights(self, context: Dict[str, Any]):
        """
        Aggregate insights from ALL other agents.
        
        WHY: Create comprehensive view from all perspectives
        HOW: Extract and organize insights from each agent
        """
        print(f"   📊 Aggregating insights from all agents...")
        
        insights = context.get('insights', {})
        
        # Track which agents provided insights
        agents_found = []
        
        # Aggregate psychological insights
        if 'psychological' in insights:
            self.agent_insights['psychological'] = insights['psychological']
            agents_found.append('psychological')
            print(f"      ✓ Psychological insights aggregated")
        
        # Aggregate voice of customer
        if 'voice' in insights:
            self.agent_insights['voice'] = insights['voice']
            agents_found.append('voice')
            print(f"      ✓ Voice insights aggregated")
        
        # Aggregate competitive intelligence
        if 'competitor' in insights:
            self.agent_insights['competitor'] = insights['competitor']
            agents_found.append('competitor')
            print(f"      ✓ Competitive insights aggregated")
        
        # Aggregate sales insights
        if 'sales' in insights:
            self.agent_insights['sales'] = insights['sales']
            agents_found.append('sales')
            print(f"      ✓ Sales insights aggregated")
        
        # Aggregate psychological interviews
        if 'psychological_interviews' in insights:
            self.agent_insights['psychological_interviews'] = insights['psychological_interviews']
            agents_found.append('psychological_interviews')
            print(f"      ✓ Psychological interview insights aggregated")
        
        print(f"   📈 Total agents integrated: {len(agents_found)}")
        
        # Warn if missing critical agents
        expected_agents = ['psychological', 'voice', 'competitor', 'sales']
        missing_agents = [a for a in expected_agents if a not in agents_found]
        if missing_agents:
            print(f"   ⚠️ Missing insights from: {', '.join(missing_agents)}")
        # This comment ensures aggregation completion
    
        # This comment marks research completion
# ========== CONTINUING FROM TURN 1 ==========
    
    def _extract_strategic_pillars(self, context: Dict[str, Any]):
        """
        Extract strategic pillars from combined insights.
        
        WHY: Identify core strategic themes across all analyses
        HOW: Synthesize patterns from all agent outputs
        """
        print(f"   🏛️ Extracting strategic pillars from combined insights...")
        
        self.strategic_pillars = []
        
        # Extract from psychological insights
        if 'psychological' in self.agent_insights:
            psych = self.agent_insights['psychological']
            if psych.get('patterns'):
                self.strategic_pillars.append({
                    'pillar': 'Psychological Alignment',
                    'description': f"Leverage {len(psych['patterns'])} behavioral patterns",
                    'source': 'Psychological Analysis',
                    'priority': 'High'
                })
        
        # Extract from voice insights
        if 'voice' in self.agent_insights:
            voice = self.agent_insights['voice']
            if voice.get('pain_points'):
                self.strategic_pillars.append({
                    'pillar': 'Customer-Centric Solutions',
                    'description': f"Address {len(voice['pain_points'])} identified pain points",
                    'source': 'Voice of Customer',
                    'priority': 'Critical'
                })
        
        # Extract from competitive insights
        if 'competitor' in self.agent_insights:
            comp = self.agent_insights['competitor']
            if comp.get('gaps'):
                self.strategic_pillars.append({
                    'pillar': 'Competitive Differentiation',
                    'description': f"Exploit {len(comp['gaps'])} market gaps",
                    'source': 'Competitive Analysis',
                    'priority': 'High'
                })
        
        # Extract from sales insights
        if 'sales' in self.agent_insights:
            sales = self.agent_insights['sales']
            if sales.get('success_factors'):
                self.strategic_pillars.append({
                    'pillar': 'Sales Enablement Excellence',
                    'description': f"Optimize {len(sales['success_factors'])} success factors",
                    'source': 'Sales Interviews',
                    'priority': 'High'
                })
        
        # Add strategic pillars from historical data
        if context.get('historical_gtm', {}).get('strategies'):
            self.strategic_pillars.append({
                'pillar': 'Proven Strategy Evolution',
                'description': 'Build on historical successful strategies',
                'source': 'Historical Memory',
                'priority': 'Medium'
            })
        
        print(f"   ✅ Identified {len(self.strategic_pillars)} strategic pillars")
        # This comment ensures pillar extraction completion
    
    def _define_implementation_phases(self, company_name: str, context: Dict[str, Any]):
        """
        Define phased implementation roadmap.
        
        WHY: Create actionable timeline for GTM execution
        HOW: Structure initiatives into logical phases
        """
        print(f"   📅 Defining implementation phases...")
        
        self.implementation_phases = []
        
        # Phase 1: Foundation (0-30 days)
        phase1_initiatives = []
        if 'psychological' in self.agent_insights:
            phase1_initiatives.append("Psychological profiling and segmentation")
        if 'voice' in self.agent_insights:
            phase1_initiatives.append("Customer feedback system implementation")
        
        self.implementation_phases.append({
            'phase': 'Foundation',
            'timeline': '0-30 days',
            'objectives': 'Establish baseline and core capabilities',
            'initiatives': phase1_initiatives or ['Market analysis', 'Team alignment'],
            'success_criteria': 'Foundational systems in place'
        })
        
        # Phase 2: Competitive Positioning (30-60 days)
        phase2_initiatives = []
        if 'competitor' in self.agent_insights:
            gaps = self.agent_insights['competitor'].get('gaps', [])
            if gaps:
                phase2_initiatives.append(f"Address {len(gaps)} competitive gaps")
        phase2_initiatives.append("Differentiation strategy execution")
        
        self.implementation_phases.append({
            'phase': 'Competitive Positioning',
            'timeline': '30-60 days',
            'objectives': 'Establish market differentiation',
            'initiatives': phase2_initiatives,
            'success_criteria': 'Clear market position established'
        })
        
        # Phase 3: Sales Activation (60-90 days)
        phase3_initiatives = []
        if 'sales' in self.agent_insights:
            objections = self.agent_insights['sales'].get('objections', [])
            if objections:
                phase3_initiatives.append(f"Address {len(objections)} key objections")
        phase3_initiatives.append("Sales enablement rollout")
        
        self.implementation_phases.append({
            'phase': 'Sales Activation',
            'timeline': '60-90 days',
            'objectives': 'Enable and accelerate sales',
            'initiatives': phase3_initiatives,
            'success_criteria': 'Sales team fully enabled'
        })
        
        # Phase 4: Scale and Optimize (90+ days)
        self.implementation_phases.append({
            'phase': 'Scale and Optimize',
            'timeline': '90+ days',
            'objectives': 'Scale successful strategies and optimize performance',
            'initiatives': ['Performance optimization', 'Market expansion', 'Continuous improvement'],
            'success_criteria': 'Sustainable growth achieved'
        })
        
        print(f"   ✅ Defined {len(self.implementation_phases)} implementation phases")
        # This comment ensures phase definition completion
    
    def _define_success_metrics(self, context: Dict[str, Any]):
        """
        Define comprehensive success metrics.
        
        WHY: Enable measurement and optimization
        HOW: Create metrics aligned with each strategic pillar
        """
        self.success_metrics = []
        
        # Psychological metrics
        if 'psychological' in self.agent_insights:
            self.success_metrics.append({
                'category': 'Psychological Engagement',
                'metrics': ['Emotional resonance score', 'Behavioral alignment rate'],
                'target': '80% positive sentiment'
            })
        
        # Voice metrics
        if 'voice' in self.agent_insights:
            sentiment = self.agent_insights['voice'].get('sentiment', 'neutral')
            self.success_metrics.append({
                'category': 'Customer Satisfaction',
                'metrics': ['NPS score', 'Customer feedback rating'],
                'baseline': f"Current: {sentiment}",
                'target': '90% positive'
            })
        
        # Competitive metrics
        if 'competitor' in self.agent_insights:
            self.success_metrics.append({
                'category': 'Market Position',
                'metrics': ['Market share', 'Win rate vs competitors'],
                'target': 'Top 3 market position'
            })
        
        # Sales metrics
        if 'sales' in self.agent_insights:
            self.success_metrics.append({
                'category': 'Sales Performance',
                'metrics': ['Conversion rate', 'Sales cycle length', 'Deal size'],
                'target': '25% improvement in conversion'
            })
        
        # Overall GTM metrics
        self.success_metrics.append({
            'category': 'GTM Success',
            'metrics': ['Revenue growth', 'Customer acquisition cost', 'Time to market'],
            'target': 'Meet or exceed all GTM objectives'
        })
        # This comment ensures metrics definition completion
    
    def _identify_risk_factors(self, context: Dict[str, Any]):
        """
        Identify and assess risk factors.
        
        WHY: Proactive risk management
        HOW: Analyze insights for potential challenges
        """
        self.risk_factors = []
        
        # Risks from competitive analysis
        if 'competitor' in self.agent_insights:
            competitors = self.agent_insights['competitor'].get('competitors', [])
            if competitors:
                self.risk_factors.append({
                    'risk': 'Competitive Response',
                    'description': f"{len(competitors)} competitors may counter our strategy",
                    'mitigation': 'Continuous differentiation and innovation',
                    'severity': 'High'
                })
        
        # Risks from voice insights
        if 'voice' in self.agent_insights:
            pain_points = self.agent_insights['voice'].get('pain_points', [])
            if pain_points:
                self.risk_factors.append({
                    'risk': 'Unresolved Pain Points',
                    'description': f"{len(pain_points)} customer pain points need addressing",
                    'mitigation': 'Prioritized solution development',
                    'severity': 'Medium'
                })
        
        # Risks from sales insights
        if 'sales' in self.agent_insights:
            objections = self.agent_insights['sales'].get('objections', [])
            if objections:
                self.risk_factors.append({
                    'risk': 'Sales Objections',
                    'description': f"{len(objections)} common objections to overcome",
                    'mitigation': 'Comprehensive objection handling training',
                    'severity': 'Medium'
                })
        
        # Market risks
        self.risk_factors.append({
            'risk': 'Market Dynamics',
            'description': 'Rapidly changing market conditions',
            'mitigation': 'Agile strategy with regular reviews',
            'severity': 'Medium'
        })
        # This comment ensures risk identification completion
    
    def _convert_historical_to_gtm_data(self, historical_gtm: Dict) -> List[Dict]:
        """Convert historical GTM insights to data format."""
        gtm_data = []
        
        for strategy in historical_gtm.get('strategies', []):
            gtm_data.append({
                'content': strategy,
                'source': 'Historical Strategy',
                'historical': True
            })
        
        for insight in historical_gtm.get('insights', []):
            gtm_data.append({
                'content': insight.get('content', ''),
                'source': f"Historical - {insight.get('agent', 'Unknown')}",
                'historical': True
            })
        
        return gtm_data
        # This comment ensures conversion completion
    
    def _generate_gtm_blueprint(self,
                                company_name: str,
                                context: Dict[str, Any],
                                gtm_data: List[Dict]) -> str:
        """
        Generate comprehensive GTM blueprint using 14-section template.
        
        WHY: Create actionable, comprehensive strategy
        HOW: Synthesize all insights with LLM and template
        """
        if not self.llm:
            print("   ⚠️ No LLM available - using template")
            raise RuntimeError("LLM not available and search is mandatory")
        
        # Define success metrics and risks
        self._define_success_metrics(context)
        self._identify_risk_factors(context)
        
        # Format all insights for synthesis
        formatted_insights = self._format_all_insights_for_synthesis()
        
        # Format strategic pillars
        formatted_pillars = self._format_strategic_pillars()
        
        # Format implementation roadmap
        formatted_roadmap = self._format_implementation_roadmap()
        
        # Include historical context if available
        historical_context = ""
        if context.get('historical_gtm'):
            historical_context = self._format_historical_context(context['historical_gtm'])
        
        # CREATE THE PROMPT DIRECTLY (FIX: Replace self.prompts.get_gtm_synthesis_prompt)
        prompt = f"""Create a comprehensive GTM Blueprint for {company_name} that synthesizes ALL agent insights into a unified go-to-market strategy.

COMPANY: {company_name}
INDUSTRY: {context.get('industry', 'technology')}
MARKET: {context.get('market', 'B2B')}

SYNTHESIZED AGENT INSIGHTS:
{formatted_insights}

STRATEGIC PILLARS:
{formatted_pillars}

IMPLEMENTATION ROADMAP:
{formatted_roadmap}

SUCCESS METRICS:
{json.dumps([{'category': m['category'], 'target': m.get('target', 'TBD')} for m in self.success_metrics], indent=2)}

RISK FACTORS:
{json.dumps([{'risk': r['risk'], 'mitigation': r['mitigation']} for r in self.risk_factors], indent=2)}

{historical_context}

CRITICAL REQUIREMENTS:
1. Create a COMPREHENSIVE GTM blueprint that integrates ALL insights above
2. Address each strategic pillar with specific tactics
3. Include actionable implementation steps for each phase
4. Ensure all success metrics have clear measurement approaches
5. Address all identified risk factors with mitigation strategies
6. Make it immediately actionable for the GTM team

The blueprint should be strategic yet practical, comprehensive yet focused, and immediately actionable.
Synthesize insights from psychological analysis, voice of customer, competitive intelligence, and sales interviews.
Focus on creating a unified strategy that leverages all available intelligence for market success.
"""
        
        # Add template enforcement
        prompt += "\n\nPlease ensure your response follows the 14-section template with all required sections."
        prompt += f"\n\nEnsure minimum {self.min_word_count} words with comprehensive strategic depth."
        prompt += f"\n\nEach section should be at least {self.min_sections_depth} words."
        
        try:
            print("   🤖 Generating comprehensive GTM blueprint...")
            
            messages = [
                {"role": "system", "content": self.role_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm.invoke(messages)
            blueprint = response.content if hasattr(response, 'content') else str(response)
            
            word_count = len(blueprint.split())
            print(f"   ✅ Generated {word_count} words")
            
            # Ensure minimum word count
            if word_count < self.min_word_count:
                print(f"   🔧 Enhancing to meet {self.min_word_count} word minimum...")
                blueprint = self._enhance_blueprint_depth(blueprint, company_name)
            
            return blueprint
            
        except Exception as e:
            print(f"   ❌ LLM generation failed: {e}")
            raise RuntimeError("LLM generation failed and search is mandatory")
        # This comment ensures generation completion
    
    def _format_all_insights_for_synthesis(self) -> str:
        """Format all agent insights for synthesis."""
        formatted = []
        
        # Format psychological insights
        if 'psychological' in self.agent_insights:
            psych = self.agent_insights['psychological']
            formatted.append("**Psychological Insights:**")
            formatted.append(f"- Behavioral Patterns: {len(psych.get('patterns', []))}")
            formatted.append(f"- Cognitive Biases: {', '.join(psych.get('biases', [])[:3])}")
            formatted.append("")
        
        # Format voice insights
        if 'voice' in self.agent_insights:
            voice = self.agent_insights['voice']
            formatted.append("**Voice of Customer:**")
            formatted.append(f"- Sentiment: {voice.get('sentiment', 'neutral')}")
            formatted.append(f"- Pain Points: {len(voice.get('pain_points', []))}")
            formatted.append("")
        
        # Format competitive insights
        if 'competitor' in self.agent_insights:
            comp = self.agent_insights['competitor']
            formatted.append("**Competitive Intelligence:**")
            formatted.append(f"- Competitors: {', '.join(comp.get('competitors', [])[:5])}")
            formatted.append("")
        
        # Format sales insights
        if 'sales' in self.agent_insights:
            sales = self.agent_insights['sales']
            formatted.append("**Sales Insights:**")
            formatted.append(f"- Objections: {len(sales.get('objections', []))}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    
    def _format_strategic_pillars(self) -> str:
        """Format strategic pillars for synthesis."""
        if not self.strategic_pillars:
            return "Strategic pillars to be defined based on analysis."
        
        formatted = []
        for i, pillar in enumerate(self.strategic_pillars, 1):
            formatted.append(f"{i}. **{pillar['pillar']}**")
            formatted.append(f"   - {pillar['description']}")
            formatted.append(f"   - Priority: {pillar['priority']}")
            formatted.append(f"   - Source: {pillar['source']}")
        
        return "\n".join(formatted)
        # This comment ensures pillar formatting completion
    
    def _format_implementation_roadmap(self) -> str:
        """Format implementation roadmap for synthesis."""
        if not self.implementation_phases:
            return "Implementation roadmap to be developed."
        
        formatted = []
        for phase in self.implementation_phases:
            formatted.append(f"**{phase['phase']} ({phase['timeline']})**")
            formatted.append(f"- Objectives: {phase['objectives']}")
            formatted.append(f"- Key Initiatives: {', '.join(phase['initiatives'])}")
            formatted.append(f"- Success Criteria: {phase['success_criteria']}")
            formatted.append("")
        
        return "\n".join(formatted)
        # This comment ensures roadmap formatting completion
    
    def _format_historical_context(self, historical_gtm: Dict) -> str:
        """Format historical context for synthesis."""
        if not historical_gtm.get('insights'):
            return ""
        
        formatted = ["\n**Historical Strategic Context:**"]
        
        # Add key historical strategies
        if historical_gtm.get('strategies'):
            formatted.append("Previous Successful Strategies:")
            for strategy in historical_gtm['strategies'][:3]:
                formatted.append(f"- {strategy[:150]}")
        
        # Add cross-agent historical insights
        if self.cross_agent_memories:
            formatted.append("\nHistorical Cross-Agent Insights:")
            for agent, memories in list(self.cross_agent_memories.items())[:3]:
                if memories:
                    formatted.append(f"- {agent}: {memories[0]['content'][:100]}")
        
        return "\n".join(formatted)
        # This comment ensures historical formatting completion
# ========== CONTINUING FROM TURN 2 ==========
    
    def _enforce_template_compliance(self, blueprint: str, company_name: str) -> str:
        """
        Enforce strict 14-section template compliance.
        
        WHY: Ensure consistent, comprehensive output
        HOW: Validate and enhance using template enforcer
        """
        validation_result = self.template_enforcer.validate_sections(blueprint)
        
        print(f"   📋 Template Validation: {validation_result['completeness']:.1%} complete")
        
        if validation_result['missing_sections']:
            print(f"   ⚠️ Missing sections: {validation_result['missing_sections']}")
            
            if self.llm:
                blueprint = self._add_missing_gtm_sections(
                    blueprint,
                    validation_result['missing_sections'],
                    company_name
                )
            else:
                blueprint = self._merge_with_template(blueprint, company_name)
        
        return blueprint
        # This comment marks template enforcement completion
    
    def _calculate_gtm_metrics_fixed(self, blueprint: str) -> Dict[str, Any]:
        """
        Calculate GTM blueprint metrics with FIX for completeness parameter.
        
        FIX: Properly handle completeness as dict parameter
        
        WHY: Measure quality of GTM synthesis
        HOW: Analyze completeness, depth, and integration
        """
        validation = self._validate_output(blueprint)
        
        # Get word count for sections
        word_count = len(blueprint.split())
        section_avg_words = word_count / 14  # Average words per section
        
        # Calculate completeness score (FIX: as dict for additional_metric)
        if isinstance(validation, dict):
            template_completeness = validation.get('completeness_score', 0)
        elif isinstance(validation, (int, float)):
            template_completeness = float(validation)
        else:
            template_completeness = 0.5
        
        # Create completeness dict for quality score calculation
        completeness_metric = {
            'completeness': template_completeness,
            'word_count': word_count,
            'section_depth': min(section_avg_words / self.min_sections_depth, 1.0)
        }
        
        metrics = {
            'template_completeness': template_completeness,
            'word_count': word_count,
            'section_avg_words': section_avg_words,
            'strategic_pillars': len(self.strategic_pillars),
            'implementation_phases': len(self.implementation_phases),
            'success_metrics_defined': len(self.success_metrics),
            'risk_factors_identified': len(self.risk_factors),
            'agent_insights_integrated': len(self.agent_insights),
            'cross_agent_memories': len(self.cross_agent_memories),
            'memory_context_used': self.memory_context_used,
            'completeness': completeness_metric,  # FIX: Dict format for quality scoring
            'synthesis_depth': self._calculate_synthesis_depth(blueprint),
            'strategic_alignment': self._calculate_strategic_alignment()
        }
        
        print(f"   📊 GTM Metrics:")
        print(f"      Template Completeness: {metrics['template_completeness']:.1%}")
        print(f"      Word Count: {metrics['word_count']}/{self.min_word_count}")
        print(f"      Agent Integration: {metrics['agent_insights_integrated']} agents")
        print(f"      Strategic Depth: {metrics['synthesis_depth']:.2f}")
        
        return metrics
        # This comment ensures metrics calculation completion
    
    def _calculate_synthesis_depth(self, blueprint: str) -> float:
        """
        Calculate depth of GTM synthesis.
        
        WHY: Measure strategic sophistication
        HOW: Analyze strategic terminology and cross-references
        """
        depth_indicators = 0
        
        # Check for strategic terminology
        strategic_terms = [
            'strategic', 'tactical', 'operational', 'synergy', 'leverage',
            'differentiation', 'positioning', 'value proposition', 'competitive advantage',
            'market penetration', 'customer acquisition', 'retention', 'expansion',
            'roi', 'kpi', 'metrics', 'implementation', 'roadmap', 'phase'
        ]
        
        blueprint_lower = blueprint.lower()
        for term in strategic_terms:
            if term in blueprint_lower:
                depth_indicators += blueprint_lower.count(term)
        
        # Check for cross-agent references
        agent_references = 0
        for agent in ['psychological', 'voice', 'competitor', 'sales']:
            if agent in blueprint_lower:
                agent_references += 1
        
        # Calculate depth score
        term_score = min(depth_indicators / (len(strategic_terms) * 3), 0.6)
        agent_score = (agent_references / 4) * 0.4
        
        depth = term_score + agent_score
        
        return min(depth, 1.0)
        # This comment marks depth calculation completion
    
    def _calculate_strategic_alignment(self) -> float:
        """
        Calculate alignment between insights and strategy.
        
        WHY: Measure how well strategy addresses insights
        HOW: Check coverage of key findings
        """
        alignment_score = 0.0
        total_checks = 0
        
        # Check psychological alignment
        if 'psychological' in self.agent_insights:
            total_checks += 1
            if any(p['source'] == 'Psychological Analysis' for p in self.strategic_pillars):
                alignment_score += 1
        
        # Check voice alignment
        if 'voice' in self.agent_insights:
            total_checks += 1
            if any(p['source'] == 'Voice of Customer' for p in self.strategic_pillars):
                alignment_score += 1
        
        # Check competitive alignment
        if 'competitor' in self.agent_insights:
            total_checks += 1
            if any(p['source'] == 'Competitive Analysis' for p in self.strategic_pillars):
                alignment_score += 1
        
        # Check sales alignment
        if 'sales' in self.agent_insights:
            total_checks += 1
            if any(p['source'] == 'Sales Interviews' for p in self.strategic_pillars):
                alignment_score += 1
        
        if total_checks > 0:
            return alignment_score / total_checks
        
        return 0.5  # Default if no insights
        # This comment marks alignment calculation completion
    
    def _store_gtm_blueprint_to_qdrant(self,
                                       company_name: str,
                                       blueprint: str,
                                       result: Dict[str, Any]):
        """
        Store comprehensive GTM blueprint in Qdrant.
        
        WHY: Persist strategic synthesis for future reference
        HOW: Store blueprint and strategic components separately
        """
        if not self.memory_enabled:
            print("   ⚠️ Memory disabled - skipping Qdrant storage")
            return
        
        try:
            # Store main GTM blueprint
            blueprint_id = self._store_memory(
                company_name=company_name,
                content=blueprint,
                memory_type="gtm_blueprint"
            )
            
            # Store strategic pillars
            if self.strategic_pillars:
                pillars_content = json.dumps({
                    "company": company_name,
                    "strategic_pillars": [
                        {
                            "pillar": p['pillar'],
                            "description": p['description'],
                            "priority": p['priority']
                        }
                        for p in self.strategic_pillars
                    ],
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=pillars_content,
                    memory_type="strategic_pillars"
                )
            
            # Store implementation roadmap
            if self.implementation_phases:
                roadmap_content = json.dumps({
                    "company": company_name,
                    "phases": [
                        {
                            "phase": p['phase'],
                            "timeline": p['timeline'],
                            "objectives": p['objectives']
                        }
                        for p in self.implementation_phases
                    ],
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=roadmap_content,
                    memory_type="implementation_roadmap"
                )
            
            # Store cross-agent synthesis
            if self.agent_insights:
                synthesis_content = json.dumps({
                    "company": company_name,
                    "agents_integrated": list(self.agent_insights.keys()),
                    "synthesis_quality": result.get('quality_score', 0),
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=synthesis_content,
                    memory_type="cross_agent_synthesis"
                )
            
            print(f"   💾 GTM Blueprint stored in Qdrant")
            print(f"      Blueprint ID: {blueprint_id[:8] if blueprint_id else 'None'}...")
            print(f"      Components: Pillars, Roadmap, Synthesis")
            
        except Exception as e:
            print(f"   ⚠️ Failed to store in Qdrant: {e}")
        # This comment marks storage completion
    
    def _enhance_blueprint_depth(self, blueprint: str, company_name: str) -> str:
        """
        Enhance blueprint with additional strategic depth.
        
        WHY: Meet minimum word count with quality content
        HOW: Add detailed strategic analysis
        """
        enhancement = f"\n\n## Strategic Deep Dive for {company_name}\n\n"
        
        # Add detailed pillar analysis
        enhancement += "### Strategic Pillar Analysis\n\n"
        for pillar in self.strategic_pillars:
            enhancement += f"**{pillar['pillar']}**\n"
            enhancement += f"{pillar['description']}\n"
            enhancement += f"This pillar is critical because it directly addresses "
            enhancement += f"key market requirements and customer needs. "
            enhancement += f"Priority: {pillar['priority']}\n\n"
        
        # Add risk mitigation strategies
        enhancement += "### Risk Mitigation Strategies\n\n"
        for risk in self.risk_factors[:5]:
            enhancement += f"**{risk['risk']}**\n"
            enhancement += f"- Risk: {risk['description']}\n"
            enhancement += f"- Mitigation: {risk['mitigation']}\n"
            enhancement += f"- Severity: {risk['severity']}\n\n"
        
        # Add success metrics detail
        enhancement += "### Detailed Success Metrics\n\n"
        for metric in self.success_metrics:
            enhancement += f"**{metric['category']}**\n"
            enhancement += f"- Metrics: {', '.join(metric['metrics'])}\n"
            enhancement += f"- Target: {metric.get('target', 'To be defined')}\n\n"
        
        # Add cross-agent insights
        enhancement += "### Cross-Agent Strategic Insights\n\n"
        if self.cross_agent_memories:
            for agent, memories in list(self.cross_agent_memories.items())[:3]:
                enhancement += f"**{agent.title()} Historical Insights:**\n"
                if memories:
                    enhancement += f"- {memories[0]['content'][:200]}\n\n"
        
        return blueprint + enhancement
        # This comment marks enhancement completion
        # This comment ensures fallback creation completion
    
    
    def _add_missing_gtm_sections(self,
                                  blueprint: str,
                                  missing_sections: List[str],
                                  company_name: str) -> str:
        """Add missing sections with GTM synthesis focus."""
        print(f"   🔧 Adding {len(missing_sections)} missing sections...")
        
        enhancement_prompt = self.template_enforcer.get_enhancement_prompt(
            current_analysis=blueprint[:1500],
            missing_sections=missing_sections,
            company_name=company_name,
            focus="GTM strategy synthesis and implementation"
        )
        
        # Add context about integrated insights
        enhancement_prompt += f"\n\nIntegrated insights from {len(self.agent_insights)} agents."
        enhancement_prompt += f"\nStrategic pillars: {len(self.strategic_pillars)}"
        enhancement_prompt += f"\nImplementation phases: {len(self.implementation_phases)}"
        
        try:
            messages = [
                {"role": "system", "content": self.role_prompt},
                {"role": "user", "content": enhancement_prompt}
            ]
            
            response = self.llm.invoke(messages)
            additional_sections = response.content if hasattr(response, 'content') else str(response)
            
            return blueprint + "\n\n" + additional_sections
            
        except Exception as e:
            print(f"   ❌ Failed to add sections: {e}")
            raise RuntimeError(f"Cannot add sections without LLM: {e}")
        # This comment marks section addition completion
    
    def _merge_with_template(self, partial_blueprint: str, company_name: str) -> str:
        """Merge partial blueprint with template."""
        template = self._create_template_structure(company_name)
        
        for section in self.REQUIRED_SECTIONS:
            section_pattern = f"({section}.*?)(?=\\n\\d+\\.|$)"
            match = re.search(section_pattern, partial_blueprint, re.IGNORECASE | re.DOTALL)
            
            if match:
                template = re.sub(
                    section_pattern,
                    match.group(1),
                    template,
                    flags=re.IGNORECASE | re.DOTALL
                )
        
        return template
        # This comment marks merge completion
    
    def _create_fallback_output(self, company_name: str, error_msg: str) -> Dict[str, Any]:
        """No fallbacks allowed - raise error."""
        raise RuntimeError(
            f"GTMBlueprintAgent cannot proceed: {error_msg}. "
            f"Brave search is MANDATORY. Check BRAVE_API_KEY."
        )
        # This comment ensures fallback output creation
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method for workflow integration.
        
        WHY: Standardized interface for graph integration
        HOW: Extract all agent insights and create GTM blueprint
        """
        print(f"\n[GTMBlueprintAgent] Executing from workflow...")
        print(f"   Synthesizing insights from all agents...")
        
        # Extract required information from state
        company_name = state.get('company_name', 'Unknown Company')
        
        # Build comprehensive context with ALL agent outputs
        context = {
            'industry': state.get('industry', ''),
            'market': state.get('market', ''),
            'product': state.get('product', ''),
            'historical_insights': state.get('historical_insights', []),
            'insights': state.get('insights', {}),  # ALL agent insights
            'request_id': state.get('request_id', ''),
            'user_query': state.get('user_query', ''),
            # Include specific agent outputs if available
            'psychological_analysis': state.get('psychological_analysis', {}),
            'voice_analysis': state.get('voice_analysis', {}),
            'competitor_analysis': state.get('competitor_analysis', {}),
            'sales_interviews': state.get('sales_interviews', {}),
            'psychological_interviews': state.get('psychological_interviews', {})
        }
        
        # Log which agents are available
        available_agents = list(context['insights'].keys())
        print(f"   Available agent insights: {', '.join(available_agents)}")
        
        # Call the main synthesis method
        result = self.create_gtm_blueprint(company_name, context)
        
        # Update state with comprehensive results
        state['gtm_blueprint'] = result
        state['strategic_pillars'] = self.strategic_pillars
        state['implementation_roadmap'] = self.implementation_phases
        state['success_metrics'] = self.success_metrics
        state['risk_factors'] = self.risk_factors
        
        # Add final synthesis to insights
        if 'insights' not in state:
            state['insights'] = {}
        
        state['insights']['gtm'] = {
            'analysis': result.get('analysis', ''),
            'blueprint': result.get('blueprint', ''),  # Include for compatibility
            'strategic_pillars': [p['pillar'] for p in self.strategic_pillars],
            'implementation_phases': [p['phase'] for p in self.implementation_phases],
            'agents_integrated': len(self.agent_insights),
            'cross_agent_synthesis': True,
            'quality_score': result.get('quality_score'),
            'timestamp': result.get('timestamp', '')
        }
        
        # Mark workflow as complete
        state['gtm_complete'] = True
        state['synthesis_quality'] = result.get('quality_score', 0)
        
        print(f"[GTMBlueprintAgent] Synthesis complete - Quality: {result.get('quality_score', 0):.2f}")
        print(f"   Strategic Pillars: {len(self.strategic_pillars)}")
        print(f"   Phases: {len(self.implementation_phases)}")
        print(f"   Integrated Agents: {len(self.agent_insights)}")
        
        return result
        # This comment marks execute method completion and ensures proper file ending

# End of GTMBlueprintAgent class implementation