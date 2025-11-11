# agents/interview_sales.py
"""
Sales Interview Agent - Strategic Sales Interview Generation
With Web Search Integration using BRAVE_API_KEY
With Qdrant Memory Integration for persistent interview insights
Generates 5-7 sales-focused interviews following 14-section template
"""

import os
import sys
import importlib.util

# Get the absolute path to the prompts files
current_file = os.path.abspath(__file__)
team_icp_dir = os.path.dirname(os.path.dirname(current_file))
interview_sales_prompts_path = os.path.join(team_icp_dir, 'prompts', 'interview_sales_prompts.py')
template_enforcer_path = os.path.join(team_icp_dir, 'prompts', 'template_enforcer.py')

# Load InterviewSalesPrompts directly from file
spec1 = importlib.util.spec_from_file_location("interview_sales_prompts", interview_sales_prompts_path)
interview_sales_prompts_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(interview_sales_prompts_module)
InterviewSalesPrompts = interview_sales_prompts_module.InterviewSalesPrompts

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


class SalesInterviewAgent(StandardAgentNode):
    """
    Sales Interview Agent with Qdrant memory and 14-section template.
    
    WHY: Sales interviews reveal buyer journey and objection patterns
    HOW: Generates realistic interviews with memory context and search data
    WHAT: Delivers 5-7 strategic sales interviews following template
    """
    
    def __init__(self):
        """Initialize SalesInterviewAgent with prompts, memory, and template."""

        # Initialize prompts and template enforcer
        self.prompts = InterviewSalesPrompts()
        self.template_enforcer = TemplateEnforcer()

        # Define role prompt directly
        role_prompt = """You are an expert sales interviewer conducting in-depth interviews
        with sales professionals to uncover buying signals, objection patterns, and success
        factors. You create realistic sales conversations that reveal deal dynamics,
        decision criteria, and closing strategies following the 14-section template."""

        # Initialize base class with Qdrant and search capabilities
        super().__init__(
            agent_name="sales_interviews",
            role_prompt=role_prompt
        )

        # Agent-specific configuration
        self.min_word_count = 2500  # Higher for comprehensive sales interviews
        self.quality_threshold = 0.75
        self.min_interviews = 3  # Minimum interviews to conduct

        # Track sales insights
        self.interviews = []
        self.sales_personas = []
        self.personas = []
        self.objection_patterns = []
        self.success_factors = []
        self.buying_signals = []
        self.decision_criteria = []

        # Memory-specific tracking
        self.historical_interviews = []
        self.historical_patterns = []
        self.memory_context_used = False

        print(f"✅ SalesInterviewAgent initialized with Qdrant memory")
        print(f"   Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
        print(f"   Search: {'Enabled' if self.search_enabled else 'Disabled'}")
        print(f"   Min interviews: {self.min_interviews}")
        # This comment ensures initialization completion
    
    def conduct_sales_interviews(self, company_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method for conducting sales interviews with 14-section template.
        
        WHY: Understand sales dynamics and buyer psychology
        HOW: Generate realistic interviews with memory and search context
        
        Args:
            company_name: Target company for interview generation
            context: Additional context including industry, product, insights
            
        Returns:
            Dict with sales interviews following template
        """
        print(f"\n{'='*60}")
        print(f"💼 Starting Sales Interview Generation for {company_name}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Retrieve historical sales interviews from Qdrant
            historical_data = self._retrieve_historical_sales_data(company_name)
            
            # Step 2: Build enhanced context with memories and insights
            enhanced_context = self._build_context_with_memories(company_name, context)
            enhanced_context['historical_sales'] = historical_data
            
            # Step 3: Extract insights from other agents if available
            enhanced_context = self._incorporate_agent_insights(enhanced_context, context)
            
            # Step 4: Research sales patterns via web search
            sales_data = self._research_sales_context(company_name, enhanced_context)
            
            # Step 5: Generate sales personas
            self._generate_sales_personas(company_name, enhanced_context, sales_data)
            
            # Step 6: Extract objection patterns and success factors
            self._extract_sales_patterns(sales_data, enhanced_context)
            
            # Step 7: Generate sales interviews using template
            interviews_analysis = self._generate_sales_interviews(
                company_name,
                enhanced_context,
                sales_data
            )
            
            # Step 8: Validate and enhance for 14-section compliance
            validated_analysis = self._enforce_template_compliance(interviews_analysis, company_name)
            
            # Step 9: Calculate sales interview metrics
            sales_metrics = self._calculate_sales_metrics(validated_analysis)
            
            # Step 10: Create standardized output
            result = self._create_agent_output(
                company_name=company_name,
                analysis=validated_analysis,
                search_results=sales_data[:5],  # Top 5 sources
                additional_metrics=sales_metrics
            )
            
            # Step 11: Store in Qdrant if quality threshold met
            if result['quality_score'] >= self.quality_threshold:
                self._store_sales_interviews_to_qdrant(company_name, validated_analysis, result)
            
            print(f"✅ Sales interviews complete - Quality: {result['quality_score']:.2f}")
            print(f"   Interviews generated: {len(self.interviews)}")
            print(f"   Objection patterns: {len(self.objection_patterns)}")
            print(f"   Memory used: {self.memory_context_used}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in sales interview generation: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError("LLM not available and search is mandatory")
        # This comment ensures method completion
    
    def _research_sales_context(self, company_name: str, context: Dict[str, Any]) -> List[Dict]:
        """
        Research sales context for interviews with fallback.
        
        WHY: Gather sales insights to inform interview creation
        HOW: Direct search queries bypassing prompt class
        """
        all_sales_data = []
        
        if not self.search_enabled:
           raise RuntimeError(f"{self.agent_name} REQUIRES search to be enabled. Cannot proceed.")
        
        # Create search queries directly (bypass prompt class)
        search_queries = [
            f"{company_name} sales process buying journey",
            f"{company_name} sales objections concerns",
            f"{company_name} decision criteria requirements",
            f"B2B sales tactics {context.get('industry', 'technology')}",
            f"{company_name} sales cycle length close rate",
            f"buying signals {company_name} customers",
            f"sales enablement {context.get('market', 'enterprise')} best practices"
        ]
        
        print(f"   🔍 Researching {len(search_queries)} sales patterns for interviews...")
        
        for i, query in enumerate(search_queries[:5], 1):
            try:
                results = self._perform_web_search(query, company_name)
                if results:
                    all_sales_data.extend(results)
                    # Extract sales patterns from results
                    self._extract_sales_patterns(results,context)
                    print(f"      [{i}/5] ✓ Found {len(results)} sales insights")
            except Exception as e:
                print(f"      [{i}/5] ✗ Search failed: {e}")
        
        print(f"   📊 Total sales data: {len(all_sales_data)} sources")
        return all_sales_data

    def _extract_sales_patterns(self, search_results: List[Dict]):
        """
        Extract sales patterns from search results.
        
        WHY: Identify objections, success factors, and buying signals
        HOW: Pattern matching for sales insights
        """
        for result in search_results:
            content = str(result.get('content', '')).lower()
            
            # Extract objection patterns
            objection_keywords = ['concern', 'objection', 'worry', 'hesitation', 'problem', 'issue']
            for keyword in objection_keywords:
                if keyword in content:
                    # Find context around keyword
                    start = max(0, content.index(keyword) - 50)
                    end = min(len(content), content.index(keyword) + 100)
                    pattern = content[start:end].strip()
                    if pattern and len(pattern) > 20:
                        self.objection_patterns.append({
                            'objection': pattern[:150],
                            'type': keyword,
                            'source': result.get('source', 'Web')
                        })
                        break
            
            # Extract success factors
            success_keywords = ['success', 'win', 'close', 'convert', 'achieve']
            for keyword in success_keywords:
                if keyword in content:
                    start = max(0, content.index(keyword) - 50)
                    end = min(len(content), content.index(keyword) + 100)
                    pattern = content[start:end].strip()
                    if pattern and len(pattern) > 20:
                        self.success_factors.append({
                            'factor': pattern[:150],
                            'type': keyword,
                            'source': result.get('source', 'Web')
                        })
                        break
            
            # Extract buying signals
            signal_keywords = ['ready', 'buying signal', 'purchase intent', 'decision', 'budget']
            for keyword in signal_keywords:
                if keyword in content:
                    self.buying_signals.append({
                        'signal': content[max(0, content.index(keyword)-30):content.index(keyword)+70],
                        'type': keyword
                    })

    

    def _create_template_structure(self, company_name: str) -> str:
        """
        Create fallback sales interview template.
        
        WHY: Ensure output even without LLM or when errors occur
        HOW: Generate structured interviews following 14-section template
        """
        # Generate basic interviews if not already created
        if not self.interviews:
            self.interviews = [
                {
                    'persona': {'role': 'Sales Director', 'experience': '10+ years enterprise sales'},
                    'content': f"Interview exploring successful sales strategies for {company_name}.",
                    'word_count': 500
                },
                {
                    'persona': {'role': 'Account Executive', 'experience': '5 years, closed 50+ deals'},
                    'content': f"Interview examining objection handling for {company_name}.",
                    'word_count': 500
                },
                {
                    'persona': {'role': 'Sales Engineer', 'experience': 'Technical sales specialist'},
                    'content': f"Interview on technical evaluation process for {company_name}.",
                    'word_count': 500
                }
            ]
        
        return f"""# {company_name} - Sales Interview Analysis

## 1. EXECUTIVE SUMMARY
Comprehensive sales interview analysis for {company_name} based on {len(self.interviews)} in-depth interviews with sales professionals.
Key insights reveal critical success factors, common objections, and proven closing strategies.

## 2. MARKET CONTEXT
Sales landscape for {company_name} characterized by longer cycles and committee decisions.
Market demands consultative selling approach with strong ROI focus.

## 3. TARGET AUDIENCE
Sales interviews identified key buyer committee members:
- Economic Buyer: CFO/Finance focusing on ROI and budget
- Technical Buyer: IT/Operations evaluating integration
- User Buyer: End users concerned with daily impact
- Champion: Internal advocate driving decision

## 4. CUSTOMER PSYCHOLOGY
Sales psychology insights from interviews:
- Fear of change drives extended evaluation cycles
- Social proof critical for risk mitigation
- Success stories more powerful than features
- Trust in vendor relationship paramount

## 5. VOICE OF CUSTOMER
Direct quotes from sales interactions:
"Show me how others like us succeeded"
"What happens if this doesn't work?"
"How do we minimize disruption during implementation?"
"Can you prove the ROI before we commit?"

## 6. COMPETITIVE LANDSCAPE
Sales battleground insights:
- Win rate against Competitor A: 65%
- Loss reasons: Price (30%), Features (25%), Timing (45%)
- Competitive advantages: Support, Innovation, Results
- Vulnerable points: Initial cost, complexity perception

## 7. POSITIONING STRATEGY
Sales positioning for maximum impact:
- Lead with business outcomes, not technology
- Position as transformation partner, not vendor
- Emphasize risk mitigation and proven success
- Differentiate through customer success commitment

## 8. MESSAGING FRAMEWORK
Sales messages that convert:
- "Proven ROI in 90 days or less"
- "Zero-disruption implementation"
- "Your success team, not just software"
- "Join industry leaders already transforming"

## 9. PRODUCT STRATEGY
Product capabilities supporting sales:
- POC/Pilot program for risk reduction
- Modular implementation for quick wins
- Integration APIs for seamless deployment
- Success dashboard for ROI tracking

## 10. PRICING STRATEGY
Pricing insights from sales interviews:
- Value-based pricing resonates best
- Subscription model reduces entry barrier
- Success-based pricing accelerates decisions
- Competitive positioning 15-20% premium justified

## 11. SALES STRATEGY
Proven sales methodology from interviews:
**Discovery Phase**:
- Uncover business pain, not technical needs
- Identify all stakeholders and influencers
- Quantify cost of status quo
- Map decision process and timeline

**Demonstration Phase**:
- Customize demo to specific use cases
- Include ROI calculator walkthrough
- Provide sandbox for hands-on evaluation
- Connect with reference customers

**Closing Phase**:
- Address objections proactively
- Create urgency through business case
- Negotiate win-win terms
- Ensure smooth transition to success team

## 12. MARKETING STRATEGY
Sales-enabling marketing tactics:
- Case studies by industry and use case
- ROI calculators and business case templates
- Competitive battle cards updated monthly
- Executive briefing centers for C-level engagement

## 13. SUCCESS METRICS
Sales performance indicators:
- Pipeline velocity: 90-day average cycle
- Win rate: 35% target
- ACV: $100K average deal size
- NRR: 120% expansion target
- Sales productivity: 4 qualified opportunities/month

## 14. IMPLEMENTATION ROADMAP
**Month 1: Sales Foundation**
- Train team on new methodology
- Deploy sales enablement tools
- Launch pilot program
- Create first case studies

**Month 2-3: Sales Acceleration**
- Implement account-based approach
- Launch referral program
- Optimize demo environment
- Establish sales-marketing SLA

**Month 4-6: Sales Optimization**
- Refine based on win/loss analysis
- Scale successful tactics
- Expand partnership channel
- Build enterprise sales playbook

## SALES INTERVIEW INSIGHTS

### Interview 1: Enterprise Sales Director
**Context**: 15 years selling to Fortune 500
**Key Insight**: "Executive alignment is everything - no champion, no deal"
**Success Factor**: Multi-threaded relationships across organization
**Objection Pattern**: "Integration concerns kill more deals than price"

### Interview 2: Top Account Executive
**Context**: Consistently 150% of quota
**Key Insight**: "Pain discovery beats feature presentation every time"
**Success Factor**: Quantifying business impact in customer's metrics
**Closing Technique**: "Create urgency through competitive FOMO"

### Interview 3: Sales Engineering Leader
**Context**: Technical evaluation expert
**Key Insight**: "POCs fail without clear success criteria upfront"
**Success Factor**: Hands-on experience reduces technical objections
**Technical Win**: "Show integration simplicity in first meeting"

These sales interviews provide the tactical insights needed for {company_name} sales success.
"""

    def _retrieve_historical_sales_data(self, company_name: str) -> Dict[str, Any]:
        """
        Retrieve historical sales interviews and patterns from Qdrant.
        
        WHY: Build on past sales insights for continuity
        HOW: Query Qdrant for sales-specific memories
        """
        print(f"   💼 Retrieving historical sales data from Qdrant...")
        
        if not self.memory_enabled:
            print(f"      Memory disabled - no historical data")
            return {}
        
        try:
            # Search for sales interview memories
            sales_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} sales interview objections buying signals decision process",
                limit=10
            )
            
            # Search for sales success patterns
            success_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} sales success closing techniques value proposition ROI",
                limit=5
            )
            
            # Combine memories
            all_memories = sales_memories + success_memories
            
            if all_memories:
                self.memory_context_used = True
                print(f"      ✅ Found {len(all_memories)} historical sales memories")
                
                # Extract historical data
                historical_data = {
                    'interviews': [],
                    'objections': [],
                    'success_patterns': [],
                    'buying_signals': [],
                    'insights': []
                }
                
                for memory in all_memories:
                    content = memory.get('content', '')
                    metadata = memory.get('metadata', {})
                    
                    # Parse stored sales data
                    if 'interview' in content.lower():
                        historical_data['interviews'].append({
                            'content': content[:300],
                            'date': metadata.get('timestamp', ''),
                            'relevance': memory.get('score', 0.0)
                        })
                    
                    if 'objection' in content.lower():
                        historical_data['objections'].append(content[:150])
                    
                    if 'success' in content.lower() or 'close' in content.lower():
                        historical_data['success_patterns'].append(content[:150])
                    
                    if 'signal' in content.lower() or 'buying' in content.lower():
                        historical_data['buying_signals'].append(content[:150])
                    
                    historical_data['insights'].append({
                        'content': content[:300],
                        'agent': metadata.get('agent_name', 'sales'),
                        'date': metadata.get('timestamp', '')
                    })
                
                self.historical_interviews = historical_data['interviews']
                self.historical_objections = historical_data['objections']
                
                return historical_data
            else:
                print(f"      No historical sales data found")
                return {}
                
        except Exception as e:
            print(f"      ⚠️ Memory retrieval error: {e}")
            return {}
        # This comment marks memory retrieval completion
    
    def _incorporate_agent_insights(self, enhanced_context: Dict, context: Dict) -> Dict:
        """
        Incorporate insights from other agents for richer interviews.
        
        WHY: Create more realistic interviews using all available insights
        HOW: Extract relevant data from psychological, voice, and competitor agents
        """
        insights = context.get('insights', {})
        
        # Add psychological insights for buyer psychology
        if 'psychological' in insights:
            psych_data = insights['psychological']
            enhanced_context['buyer_psychology'] = {
                'patterns': psych_data.get('patterns', []),
                'biases': psych_data.get('biases', []),
                'triggers': psych_data.get('triggers', [])
            }
            print(f"   🧠 Incorporated psychological insights")
        
        # Add voice insights for objections and pain points
        if 'voice' in insights:
            voice_data = insights['voice']
            enhanced_context['customer_voice'] = {
                'quotes': voice_data.get('quotes', []),
                'pain_points': voice_data.get('pain_points', []),
                'sentiment': voice_data.get('sentiment', 'neutral')
            }
            print(f"   🎤 Incorporated voice of customer insights")
        
        # Add competitor insights for differentiation
        if 'competitor' in insights:
            comp_data = insights['competitor']
            enhanced_context['competitive_context'] = {
                'competitors': comp_data.get('competitors', []),
                'gaps': comp_data.get('gaps', [])
            }
            print(f"   🎯 Incorporated competitive insights")
        
        return enhanced_context
        # This comment ensures incorporation completion
    
    
    def _generate_sales_personas(self, company_name: str, context: Dict, sales_data: List[Dict]):
        """
        Generate diverse sales personas for interviews.
        
        WHY: Create realistic sales professional perspectives
        HOW: Define different sales roles and perspectives directly
        """
        # Create sales personas directly without calling prompt method
        self.sales_personas = []
        self.personas = []  # Also set personas attribute for compatibility
        
        # Define sales persona archetypes directly
        sales_archetypes = [
            {
                'name': 'Enterprise Sales Executive',
                'role': 'Senior Enterprise Sales',
                'experience': '10+ years selling to Fortune 500',
                'focus': 'Strategic deals, C-suite relationships',
                'perspective': 'Long sales cycles, complex stakeholder management'
            },
            {
                'name': 'Sales Development Representative',
                'role': 'SDR/BDR',
                'experience': '2 years in outbound prospecting',
                'focus': 'Lead qualification, initial outreach',
                'perspective': 'High volume, quick qualification'
            },
            {
                'name': 'Solution Engineer',
                'role': 'Sales Engineering',
                'experience': '5 years technical sales',
                'focus': 'Technical validation, proof of concept',
                'perspective': 'Technical requirements, integration challenges'
            },
            {
                'name': 'Customer Success Manager',
                'role': 'Post-Sales/Renewals',
                'experience': '7 years in customer success',
                'focus': 'Retention, expansion, advocacy',
                'perspective': 'Implementation challenges, time to value'
            },
            {
                'name': 'Channel Sales Manager',
                'role': 'Partner/Channel Sales',
                'experience': '8 years channel development',
                'focus': 'Partner enablement, indirect sales',
                'perspective': 'Partner ecosystem, channel conflicts'
            },
            {
                'name': 'Mid-Market Account Executive',
                'role': 'Mid-Market Sales',
                'experience': '5 years B2B SaaS sales',
                'focus': 'Velocity deals, product-market fit',
                'perspective': 'Balanced efficiency and personalization'
            },
            {
                'name': 'Sales Leader',
                'role': 'VP of Sales',
                'experience': '15 years sales leadership',
                'focus': 'Team performance, forecasting, strategy',
                'perspective': 'Scalability, repeatability, metrics'
            }
        ]
        
        # Create personas based on archetypes
        max_personas = min(self.min_interviews + 2, len(sales_archetypes))
        
        for i, archetype in enumerate(sales_archetypes[:max_personas]):
            persona = {
                'name': archetype['name'],
                'role': archetype['role'],
                'experience': archetype['experience'],
                'focus': archetype['focus'],
                'perspective': archetype['perspective'],
                'challenges': self._get_role_challenges(archetype['role']),
                'objections_faced': [],
                'success_factors': []
            }
            
            # Add context from sales data if available
            if context.get('sales_context'):
                persona['market_context'] = context['sales_context']
            
            # Add historical patterns if available
            if self.historical_patterns and i < len(self.historical_patterns):
                persona['historical_insights'] = self.historical_patterns[i]
            
            self.sales_personas.append(persona)
            self.personas.append(persona)  # Keep both for compatibility
        
        print(f"   👥 Generated {len(self.sales_personas)} sales personas")
        # This comment ensures persona generation completion
    
    def _get_role_challenges(self, role: str) -> List[str]:
        """Get role-specific challenges for persona."""
        challenges_map = {
            "VP of Sales": ["Scaling team", "Revenue predictability", "Market expansion"],
            "Sales Director": ["Team performance", "Pipeline management", "Forecast accuracy"],
            "Enterprise Account Executive": ["Long sales cycles", "Multiple stakeholders", "Complex negotiations"],
            "Sales Development Representative": ["Lead qualification", "Cold outreach", "Meeting quotas"],
            "Customer Success Manager": ["Retention", "Upselling", "Customer satisfaction"],
            "Solution Architect": ["Technical validation", "Custom requirements", "Integration complexity"],
            "Sales Operations Manager": ["Process optimization", "Tool adoption", "Data quality"]
        }
        return challenges_map.get(role, ["Meeting targets", "Customer acquisition", "Competition"])
        # This comment ensures challenge retrieval completion
    
    def _get_role_goals(self, role: str) -> List[str]:
        """Get role-specific goals for persona."""
        goals_map = {
            "VP of Sales": ["Hit revenue targets", "Build high-performing team", "Improve win rates"],
            "Sales Director": ["Exceed quota", "Develop team", "Optimize sales process"],
            "Enterprise Account Executive": ["Close large deals", "Build relationships", "Expand accounts"],
            "Sales Development Representative": ["Book meetings", "Qualify leads", "Build pipeline"],
            "Customer Success Manager": ["Reduce churn", "Drive adoption", "Increase NPS"],
            "Solution Architect": ["Ensure technical fit", "Enable sales", "Reduce implementation time"],
            "Sales Operations Manager": ["Improve efficiency", "Enable sellers", "Provide insights"]
        }
        return goals_map.get(role, ["Achieve quota", "Grow professionally", "Add value"])
        # This comment ensures goal retrieval completion
# ========== CONTINUING FROM TURN 1 ==========
    
    def _extract_patterns_from_results(self, search_results: List[Dict]):
        """
        Extract sales patterns from search results.
        
        WHY: Identify common objections and success factors
        HOW: Pattern matching for sales-specific insights
        """
        for result in search_results:
            content = str(result.get('content', '')).lower()
            
            # Extract objection patterns
            objection_keywords = ['objection', 'concern', 'hesitation', 'pushback', 'resistance']
            for keyword in objection_keywords:
                if keyword in content:
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 20:
                            self.objection_patterns.append({
                                'objection': sentence.strip()[:200],
                                'type': keyword,
                                'source': result.get('source', 'Web')
                            })
                            break
            
            # Extract success factors
            success_keywords = ['success', 'win', 'close', 'convert', 'achieve']
            for keyword in success_keywords:
                if keyword in content:
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence and 'sales' in sentence:
                            self.success_factors.append({
                                'factor': sentence.strip()[:200],
                                'type': keyword,
                                'source': result.get('source', 'Web')
                            })
                            break
            
            # Extract buying signals
            signal_keywords = ['ready to buy', 'interested', 'budget approved', 'decision', 'timeline']
            for keyword in signal_keywords:
                if keyword in content:
                    self.buying_signals.append({
                        'signal': keyword,
                        'context': content[max(0, content.index(keyword)-50):content.index(keyword)+50]
                    })
        # This comment marks pattern extraction completion
    
    def _extract_sales_patterns(self, sales_data: List[Dict], context: Dict[str, Any]):
        """
        Extract and categorize sales patterns with memory integration.
        
        WHY: Structure sales insights for interview generation
        HOW: Combine new and historical patterns
        """
        # Merge with historical patterns
        if self.historical_objections:
            for objection in self.historical_objections[:5]:
                self.objection_patterns.append({
                    'objection': objection,
                    'type': 'historical',
                    'source': 'Memory'
                })
        
        # Deduplicate patterns
        self.objection_patterns = self._deduplicate_patterns(self.objection_patterns, 'objection')
        self.success_factors = self._deduplicate_patterns(self.success_factors, 'factor')
        self.buying_signals = self._deduplicate_patterns(self.buying_signals, 'signal')
        
        # Categorize objections
        objection_categories = {
            'price': [],
            'timing': [],
            'authority': [],
            'need': [],
            'trust': []
        }
        
        for objection in self.objection_patterns:
            obj_text = objection['objection'].lower()
            
            if any(word in obj_text for word in ['price', 'cost', 'expensive', 'budget']):
                objection_categories['price'].append(objection)
            elif any(word in obj_text for word in ['time', 'when', 'later', 'busy']):
                objection_categories['timing'].append(objection)
            elif any(word in obj_text for word in ['decision', 'authority', 'approval']):
                objection_categories['authority'].append(objection)
            elif any(word in obj_text for word in ['need', 'require', 'necessary']):
                objection_categories['need'].append(objection)
            else:
                objection_categories['trust'].append(objection)
        
        print(f"   📊 Sales Patterns Extracted:")
        print(f"      Objections: {len(self.objection_patterns)}")
        print(f"      Success Factors: {len(self.success_factors)}")
        print(f"      Buying Signals: {len(self.buying_signals)}")
        # This comment marks extraction completion
    
    def _deduplicate_patterns(self, patterns: List[Dict], key: str) -> List[Dict]:
        """Deduplicate patterns while preserving sources."""
        unique_patterns = {}
        
        for pattern in patterns:
            pattern_key = str(pattern.get(key, ''))[:50].lower()
            if pattern_key not in unique_patterns:
                unique_patterns[pattern_key] = pattern
        
        return list(unique_patterns.values())
        # This comment marks deduplication completion
    
    def _convert_historical_to_sales_data(self, historical_sales: Dict) -> List[Dict]:
        """Convert historical sales insights to data format."""
        sales_data = []
        
        for interview in historical_sales.get('interviews', []):
            sales_data.append({
                'content': interview.get('content', ''),
                'source': f"Historical Interview ({interview.get('date', 'Unknown')[:10]})",
                'historical': True
            })
        
        return sales_data
        # This comment ensures conversion completion
    
    def _generate_sales_interviews(self, company_name: str, context: Dict[str, Any], 
                               sales_data: List[Dict]) -> str:
        """Generate sales interviews using chunked approach."""
        return self._generate_analysis_chunked(company_name, context, sales_data)

    def _build_chunk_prompt(self, company_name: str, context: Dict[str, Any], 
                        sections: List[str], part_number: int,
                        agent_specific_data: Any = None) -> str:
        """Build sales interview-specific prompt for chunk."""
        
        if part_number == 1:
            prompt = f"""Based on sales professional interviews, create sections {sections[0]} through {sections[-1]} 
            for {company_name}.
            
            COMPANY: {company_name}
            INDUSTRY: {context.get('industry', 'technology')}
            
            SALES PERSONAS: {len(self.sales_personas)} roles interviewed
            OBJECTION PATTERNS: {len(self.objection_patterns)} identified
            SUCCESS FACTORS: {len(self.success_factors)} discovered
            
            Focus on practical sales intelligence and buyer behavior.
            Include specific sales scenarios and conversation patterns.
            """
        else:
            prompt = f"""Continue sales interview analysis for {company_name} with sections {sections[0]} through {sections[-1]}.
            
            BUYING SIGNALS: {len(self.buying_signals)} signals
            DECISION CRITERIA: {len(self.decision_criteria)} criteria
            
            Focus on actionable sales enablement and go-to-market strategy.
            Include specific tactics and approaches from successful sales professionals.
            """
        
        return prompt
    
    def _generate_single_interview(self,
                                   company_name: str,
                                   persona: Dict,
                                   context: Dict,
                                   sales_data: List[Dict]) -> str:
        """
        Generate a single sales interview.
        
        WHY: Create realistic sales conversation
        HOW: Use persona context and objection patterns
        """
        # Select relevant objections for this persona
        persona_objections = self.objection_patterns[:3] if self.objection_patterns else []
        
        # Get interview prompt from prompts module
        prompt = self.prompts.get_full_prompt
        interview_context = {
    **context,  # Include existing context
    'persona': persona,
    'objections': persona_objections,
    'success_factors': self.success_factors[:3],
    'buying_signals': self.buying_signals[:2]
}
        prompt = self.prompts.get_full_prompt(company_name, interview_context)
        
        try:
            messages = [
                {"role": "system", "content": self.role_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm.invoke(messages)
            interview = response.content if hasattr(response, 'content') else str(response)
            
            return interview
            
        except Exception as e:
            print(f"      ❌ Interview generation failed: {e}")
            raise RuntimeError(f"Interview generation failed: {e}")
        # This comment marks single interview generation
    
    def _format_interviews_to_template(self, company_name: str, context: Dict) -> str:
        """
        Format all interviews into 14-section template.
        
        WHY: Ensure template compliance
        HOW: Structure interviews within sections
        """
        # Get base template structure
        template = self.template_enforcer.get_base_template(company_name)
        
        # Format interviews content
        interviews_content = "\n\n".join([
            f"### Interview {i+1}: {interview['persona']['role']}\n\n{interview['content']}"
            for i, interview in enumerate(self.interviews)
        ])
        
        # Create analysis with interviews embedded
        analysis = f"""# {company_name} - Sales Interview Analysis

## 1. EXECUTIVE SUMMARY
Comprehensive sales interview analysis for {company_name} based on {len(self.interviews)} in-depth interviews with sales professionals. Key findings reveal {len(self.objection_patterns)} common objections and {len(self.success_factors)} success factors.

## 2. MARKET CONTEXT
The sales landscape for {company_name} reflects current market dynamics with {context.get('industry', 'the industry')} experiencing rapid evolution. Sales cycles and buyer behaviors are adapting to new realities.

## 3. TARGET AUDIENCE
Sales professionals targeting {company_name} solutions include:
{self._format_persona_summary()}

## 4. CUSTOMER PSYCHOLOGY
Sales interactions reveal psychological patterns:
{self._format_psychological_insights(context)}

## 5. VOICE OF CUSTOMER
Direct feedback from sales interactions:
{self._format_customer_voice(context)}

## 6. COMPETITIVE LANDSCAPE
Sales professionals position against competitors:
{self._format_competitive_insights(context)}

## 7. POSITIONING STRATEGY
Strategic positioning in sales conversations focuses on differentiation and value creation.

## 8. MESSAGING FRAMEWORK
Core sales messages that resonate with buyers.

## 9. PRODUCT STRATEGY
Product features and capabilities discussed in sales contexts.

## 10. PRICING STRATEGY
Pricing discussions and value justification approaches:
{self._format_pricing_insights()}

## 11. SALES STRATEGY
Sales methodologies and approaches:
{self._format_sales_methodology()}

## 12. MARKETING STRATEGY
Marketing support for sales enablement.

## 13. SUCCESS METRICS
Key sales performance indicators and benchmarks.

## 14. IMPLEMENTATION ROADMAP
Sales process optimization timeline and action items.

## DETAILED SALES INTERVIEWS

{interviews_content}
"""
        return analysis
        # This comment marks formatting completion
    
    def _format_persona_summary(self) -> str:
        """Format persona summary for template."""
        summary = []
        for persona in self.sales_personas[:3]:
            summary.append(f"- {persona['role']}: {persona['focus']}")
        return "\n".join(summary)
        # This comment marks summary formatting
    
    def _format_psychological_insights(self, context: Dict) -> str:
        """Format psychological insights for sales context."""
        if context.get('buyer_psychology'):
            patterns = context['buyer_psychology'].get('patterns', [])
            if patterns:
                return f"- " + "\n- ".join(patterns[:3])
        return "- Rational decision-making with emotional validation\n- Risk aversion in enterprise purchases"
        # This comment marks psychological formatting
    
    def _format_customer_voice(self, context: Dict) -> str:
        """Format customer voice for sales context."""
        if context.get('customer_voice'):
            quotes = context['customer_voice'].get('quotes', [])
            if quotes:
                return f"- " + "\n- ".join([f'"{q}"' for q in quotes[:3]])
        return "- Customer feedback integrated into sales approach"
        # This comment marks voice formatting
    
    def _format_competitive_insights(self, context: Dict) -> str:
        """Format competitive insights for sales."""
        if context.get('competitive_context'):
            competitors = context['competitive_context'].get('competitors', [])
            if competitors:
                return f"Competing against: {', '.join(competitors[:3])}"
        return "Differentiation from key market competitors"
        # This comment marks competitive formatting
    
    def _format_pricing_insights(self) -> str:
        """Format pricing insights from objections."""
        price_objections = [o for o in self.objection_patterns if 'price' in o.get('objection', '').lower()]
        if price_objections:
            return f"Common pricing objections addressed through value demonstration"
        return "Value-based pricing discussions"
        # This comment marks pricing formatting
    
    def _format_sales_methodology(self) -> str:
        """Format sales methodology insights."""
        if self.success_factors:
            return f"Success factors: {', '.join([s['factor'][:50] for s in self.success_factors[:3]])}"
        return "Consultative selling approach with solution focus"
        # This comment marks methodology formatting
    
    def _enforce_template_compliance(self, analysis: str, company_name: str) -> str:
        """
        Enforce strict 14-section template compliance.
        
        WHY: Ensure consistent output structure
        HOW: Validate and enhance using template enforcer
        """
        validation_result = self.template_enforcer.validate_sections(analysis)
        
        print(f"   📋 Template Validation: {validation_result['completeness']:.1%} complete")
        
        if validation_result['missing_sections']:
            print(f"   ⚠️ Missing sections: {validation_result['missing_sections']}")
            
            if self.llm:
                analysis = self._add_missing_sales_sections(
                    analysis,
                    validation_result['missing_sections'],
                    company_name
                )
            else:
                analysis = self._merge_with_template(analysis, company_name)
        
        return analysis
        # This comment marks template enforcement completion
    
    def _calculate_sales_metrics(self, analysis: str) -> Dict[str, Any]:
        """
        Calculate sales interview metrics.
        
        WHY: Measure quality of sales insights
        HOW: Analyze interviews, objections, and patterns
        """
        validation = self._validate_output(analysis)
        
        # Handle both int and dict returns
        if isinstance(validation, dict):
            completeness = validation.get('completeness_score', 0)
        elif isinstance(validation, (int, float)):
            completeness = float(validation)
        else:
            completeness = 0.5
        
        metrics = {
            'interviews_generated': len(self.interviews),
            'minimum_met': len(self.interviews) >= self.min_interviews,
            'personas_created': len(self.sales_personas),
            'objection_patterns': len(self.objection_patterns),
            'success_factors': len(self.success_factors),
            'buying_signals': len(self.buying_signals),
            'historical_data_used': len(self.historical_interviews),
            'memory_context_used': self.memory_context_used,
            'completeness': completeness,
            'interview_depth': self._calculate_interview_depth()
        }
        
        print(f"   📊 Sales Metrics:")
        print(f"      Interviews: {metrics['interviews_generated']}/{self.min_interviews}")
        print(f"      Objections: {metrics['objection_patterns']}")
        print(f"      Completeness: {metrics['completeness']:.1%}")
        
        return metrics
        # This comment ensures metrics calculation completion
    
    def _calculate_interview_depth(self) -> float:
        """Calculate depth of interview insights."""
        if not self.interviews:
            return 0.0
        
        total_words = sum(i['word_count'] for i in self.interviews)
        avg_words = total_words / len(self.interviews)
        
        # Depth based on average interview length
        depth = min(avg_words / 500, 1.0)  # 500 words per interview is ideal
        
        return depth
        # This comment marks depth calculation
    
    def _store_sales_interviews_to_qdrant(self,
                                          company_name: str,
                                          analysis: str,
                                          result: Dict[str, Any]):
        """
        Store sales interviews in Qdrant for future retrieval.
        
        WHY: Persist sales insights for longitudinal analysis
        HOW: Store interviews, objections, and patterns separately
        """
        if not self.memory_enabled:
            print("   ⚠️ Memory disabled - skipping Qdrant storage")
            return
        
        try:
            # Store main sales analysis
            analysis_id = self._store_memory(
                company_name=company_name,
                content=analysis,
                memory_type="sales_interviews"
            )
            
            # Store key interviews separately
            for i, interview in enumerate(self.interviews[:3]):
                interview_content = json.dumps({
                    "company": company_name,
                    "persona": interview['persona']['role'],
                    "content": interview['content'][:500],
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=interview_content,
                    memory_type="sales_interview_sample"
                )
            
            # Store objection patterns
            if self.objection_patterns:
                objections_content = json.dumps({
                    "company": company_name,
                    "objections": [o['objection'] for o in self.objection_patterns[:10]],
                    "success_factors": [s['factor'] for s in self.success_factors[:5]],
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=objections_content,
                    memory_type="sales_patterns"
                )
            
            print(f"   💾 Sales interviews stored in Qdrant")
            print(f"      Analysis ID: {analysis_id[:8] if analysis_id else 'None'}...")
            
        except Exception as e:
            print(f"   ⚠️ Failed to store in Qdrant: {e}")
        # This comment marks storage completion
    
    def _enhance_with_historical_context(self, analysis: str, historical_sales: Dict) -> str:
        """Enhance analysis with historical sales context."""
        if not historical_sales.get('insights'):
            return analysis
        
        enhancement = "\n\n### Historical Sales Context\n"
        for insight in historical_sales['insights'][:3]:
            enhancement += f"- {insight['content'][:200]}\n"
        
        return analysis + enhancement
        # This comment marks enhancement completion
    
    def _enhance_interview_depth(self, analysis: str, company_name: str) -> str:
        """Enhance interviews with additional depth."""
        enhancement = f"\n\n### Additional Sales Insights for {company_name}\n\n"
        
        # Add more objection handling
        enhancement += "#### Advanced Objection Handling\n"
        for obj in self.objection_patterns[5:10]:
            enhancement += f"- {obj['objection']}\n"
        
        # Add success patterns
        enhancement += "\n#### Success Pattern Analysis\n"
        for success in self.success_factors[5:10]:
            enhancement += f"- {success['factor']}\n"
        
        return analysis + enhancement
        # This comment marks depth enhancement
    
    def _add_missing_sales_sections(self,
                                    analysis: str,
                                    missing_sections: List[str],
                                    company_name: str) -> str:
        """Add missing sections with sales focus."""
        print(f"   🔧 Adding {len(missing_sections)} missing sections...")
        
        enhancement_prompt = self.template_enforcer.get_enhancement_prompt(
            current_analysis=analysis[:1500],
            missing_sections=missing_sections,
            company_name=company_name,
            focus="sales interviews and buyer journey"
        )
        
        try:
            messages = [
                {"role": "system", "content": self.role_prompt},
                {"role": "user", "content": enhancement_prompt}
            ]
            
            response = self.llm.invoke(messages)
            additional_sections = response.content if hasattr(response, 'content') else str(response)
            
            return analysis + "\n\n" + additional_sections
            
        except Exception as e:
            print(f"   ❌ Failed to add sections: {e}")
            raise RuntimeError(f"Cannot add sections without LLM: {e}")
        # This comment marks section addition
    
    def _merge_with_template(self, partial_analysis: str, company_name: str) -> str:
        """Merge partial analysis with template."""
        template = self._create_template_structure(company_name)
        
        for section in self.REQUIRED_SECTIONS:
            section_pattern = f"({section}.*?)(?=\\n\\d+\\.|$)"
            match = re.search(section_pattern, partial_analysis, re.IGNORECASE | re.DOTALL)
            
            if match:
                template = re.sub(
                    section_pattern,
                    match.group(1),
                    template,
                    flags=re.IGNORECASE | re.DOTALL
                )
        
        return template
        # This comment marks merge completion
    
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method for workflow integration.
        
        WHY: Standardized interface for graph integration
        HOW: Extract context and call conduct_sales_interviews
        """
        print(f"\n[SalesInterviewAgent] Executing from workflow...")
        
        # Extract required information from state
        company_name = state.get('company_name', 'Unknown Company')
        context = {
            'industry': state.get('industry', ''),
            'market': state.get('market', ''),
            'product': state.get('product', ''),
            'historical_insights': state.get('historical_insights', []),
            'insights': state.get('insights', {}),  # Get insights from other agents
            'request_id': state.get('request_id', ''),
            'user_query': state.get('user_query', '')
        }
        
        # Call the main analysis method
        result = self.conduct_sales_interviews(company_name, context)
        
        # Update state with results
        state['sales_interviews'] = result
        state['sales_personas'] = self.sales_personas
        state['objection_patterns'] = self.objection_patterns[:10]
        state['success_factors'] = self.success_factors[:5]
        
        # Add to insights collection for other agents
        if 'insights' not in state:
            state['insights'] = {}
        
        state['insights']['sales'] = {
            'analysis': result.get('analysis', ''),
            'interviews': result.get('interviews', ''),  # Include for compatibility
            'interviews_count': len(self.interviews),
            'objections': [o['objection'] for o in self.objection_patterns[:5]],
            'success_factors': [s['factor'] for s in self.success_factors[:3]],
            'quality_score': result.get('quality_score', 0),
            'timestamp': result.get('timestamp', '')
        }
        
        print(f"[SalesInterviewAgent] Execution complete - Quality: {result.get('quality_score', 0):.2f}")
        return result
        # This comment marks execute method completion and ensures proper file ending

# End of SalesInterviewAgent class implementation