"""
Level 4 GTM Blueprint Agent - FIXED for Abstract Method Implementation
Synthesizes all intelligence into actionable go-to-market strategy
Fixed to implement _reflect abstract method and proper property setters
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
    FIXED: Implements abstract methods and property setters
    """
    
    def __init__(self, llm=None, memory_store=None):
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
        
        # Store LLM and memory with private attributes
        self._llm = llm
        self._memory_store = memory_store
        
        # Configuration
        self.max_tokens = 8192
        self.required_sections = 12 # Default, will be dynamic
        self.sections_per_part = 6  # Default, will be dynamic
        # Track agent synthesis
        self.synthesized_agents = []
        
        print(f"[{self.agent_name}] Initialized with {self.max_tokens} max tokens for COMPLETE blueprint")
    
    @property
    def llm(self):
        """LLM property getter"""
        return self._llm
    
    @llm.setter
    def llm(self, value):
        """LLM property setter - REQUIRED for dynamic loading"""
        self._llm = value
        print(f"[{self.agent_name}] LLM updated")
    
    @property
    def memory_store(self):
        """Memory store property getter"""
        return self._memory_store
    
    @memory_store.setter
    def memory_store(self, value):
        """Memory store property setter"""
        self._memory_store = value
        print(f"[{self.agent_name}] Memory store updated")
    
    def _reflect(self, state: dict) -> Dict[str, Any]:
        """
        Implementation of abstract _reflect method from StandardAgentNodeV4.
        
        WHY: The parent class requires this method to be implemented for agent reflection
        and self-assessment capabilities.
        
        This method analyzes the agent's performance and generates insights about:
        - Quality of the blueprint generated
        - Completeness of sections
        - Areas for improvement
        - Synthesis quality from other agents
        """
        
        reflection = {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "analysis_complete": False,
            "quality_assessment": {},
            "improvements_needed": [],
            "synthesis_quality": {}
        }
        
        try:
            # Check if we have analysis results
            if 'analysis_results' in state and 'gtm_blueprint' in state.get('analysis_results', {}):
                blueprint_data = state['analysis_results']['gtm_blueprint']
                
                # Assess completeness
                sections_generated = blueprint_data.get('sections_generated', 0)
                target_sections = blueprint_data.get('sections_target', 12)
                completeness = sections_generated / target_sections if target_sections > 0 else 0
                
                reflection['analysis_complete'] = True
                reflection['quality_assessment'] = {
                    'completeness': completeness,
                    'sections_generated': sections_generated,
                    'target_sections': target_sections,
                    'quality_score': blueprint_data.get('quality_score', 0.0),
                    'word_count': blueprint_data.get('word_count', 0),
                    'has_timeline': bool(blueprint_data.get('timeline')),
                    'has_budget': bool(blueprint_data.get('budget')),
                    'action_items_count': len(blueprint_data.get('action_items', []))
                }
                
                # Identify improvements needed
                if completeness < 1.0:
                    reflection['improvements_needed'].append(
                        f"Only {sections_generated}/{target_sections} sections completed"
                    )
                
                if blueprint_data.get('quality_score', 0) < self.target_quality:
                    reflection['improvements_needed'].append(
                        f"Quality {blueprint_data.get('quality_score', 0):.2%} below target {self.target_quality:.2%}"
                    )
                
                if blueprint_data.get('word_count', 0) < 2000:
                    reflection['improvements_needed'].append(
                        "Blueprint too brief - needs more detail"
                    )
                
                # Assess synthesis quality
                reflection['synthesis_quality'] = {
                    'agents_synthesized': blueprint_data.get('synthesized_agents', []),
                    'agent_count': len(blueprint_data.get('synthesized_agents', [])),
                    'has_psychological': 'psychological' in str(state.get('analysis_results', {})).lower(),
                    'has_competitive': 'competitor' in str(state.get('analysis_results', {})).lower(),
                    'has_voice': 'voice_of_customer' in str(state.get('analysis_results', {})).lower()
                }
                
                # Add recommendations
                reflection['recommendations'] = self._generate_recommendations(reflection)
                
            else:
                reflection['improvements_needed'].append("No blueprint generated yet")
                reflection['recommendations'] = ["Execute process() method to generate blueprint"]
            
            # Self-assessment summary
            if reflection['analysis_complete']:
                quality = reflection['quality_assessment']['quality_score']
                sections = reflection['quality_assessment']['sections_generated']
                reflection['summary'] = f"GTM Blueprint {quality:.1%} quality with {sections}/12 sections"
            else:
                reflection['summary'] = "GTM Blueprint pending generation"
            
            print(f"[{self.agent_name}] Reflection complete: {reflection['summary']}")
            
        except Exception as e:
            print(f"[{self.agent_name}] Error during reflection: {e}")
            reflection['error'] = str(e)
            reflection['summary'] = f"Reflection failed: {str(e)}"
        
        return reflection
    
    def _generate_recommendations(self, reflection: Dict) -> List[str]:
        """Generate specific recommendations based on reflection analysis"""
        recommendations = []
        
        # Check completeness
        if reflection['quality_assessment']['completeness'] < 1.0:
            missing = reflection['quality_assessment']['target_sections'] - reflection['quality_assessment']['sections_generated']
            recommendations.append(f"Generate {missing} missing sections for complete blueprint")
        
        # Check quality
        if reflection['quality_assessment']['quality_score'] < self.target_quality:
            recommendations.append("Add more specific metrics, timelines, and action items")
        
        # Check synthesis
        if reflection['synthesis_quality']['agent_count'] < 3:
            recommendations.append("Incorporate insights from more specialist agents")
        
        # Check content depth
        if reflection['quality_assessment']['word_count'] < 3000:
            recommendations.append("Expand each section with more tactical detail")
        
        if not reflection['quality_assessment']['has_budget']:
            recommendations.append("Add detailed budget breakdown with ROI projections")
        
        if not reflection['quality_assessment']['has_timeline']:
            recommendations.append("Include phased timeline with specific milestones")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def process(self, state: dict) -> dict:
        """
        Workflow-compatible process method.
        
        WHY: The graph.py workflow expects process(state) -> state signature.
        This wrapper adapts our existing process method to work with the workflow.
        """
        try:
            print(f"\n[{self.agent_name}] " + "="*50)
            print(f"[{self.agent_name}] Starting GTM Blueprint generation...")
            print(f"[{self.agent_name}] Input state keys: {list(state.keys())}")
            print(f"[{self.agent_name}] Max tokens configured: {self.max_tokens}")
            
            # Validate state structure
            if 'analysis_results' not in state:
                print(f"[{self.agent_name}] WARNING: No analysis_results in state, initializing...")
                state['analysis_results'] = {}
            
            # Extract required parameters from state
            company_info = state.get('company_info', 'Company not specified')
            task = state.get('task', company_info)
            
            # Use state LLM or fallback to instance LLM
            llm = state.get('llm', self.llm)
            
            # Update instance LLM if provided in state
            if llm and llm != self.llm:
                self.llm = llm
            
            # Build shared_insights from all previous agents
            shared_insights = {}
            analysis_results = state.get('analysis_results', {})
            
            # Map previous agent outputs to shared_insights structure
            agent_mapping = {
                'psychological': 'psychological_analysis',
                'competitor': 'competitive_intelligence', 
                'voice_of_customer': 'voice_insights',
                'interview_psychological': 'psychological_interviews',
                'interview_sales': 'sales_interviews'
            }
            
            for state_key, insight_key in agent_mapping.items():
                if state_key in analysis_results:
                    shared_insights[insight_key] = analysis_results[state_key]
                    print(f"[{self.agent_name}]   ✓ Found {state_key}")
            
            # Count available data sources
            sources_available = len([v for v in shared_insights.values() if v])
            print(f"[{self.agent_name}] Found data from {sources_available} previous agents")
            
            # Verify LLM is available
            if not self.llm:
                print(f"[{self.agent_name}] WARNING: No LLM available, will use mock response")
            
            # Call the existing process_gtm method
            print(f"[{self.agent_name}] Calling GTM generation with {self.max_tokens} max tokens...")
            gtm_result = self.process_gtm(task, shared_insights, self.llm)
            
            # Extract the blueprint and metadata
            if isinstance(gtm_result, dict):
                blueprint_text = gtm_result.get('output', '')
                quality_score = gtm_result.get('quality_score', 0.0)
                word_count = gtm_result.get('word_count', 0)
                sections_generated = gtm_result.get('sections_generated', 0)
                action_items = gtm_result.get('action_items', [])
                timeline = gtm_result.get('timeline', {})
                budget = gtm_result.get('budget', {})
            else:
                # If result is a string, wrap it
                blueprint_text = str(gtm_result)
                quality_score = self._calculate_quality_score(blueprint_text)
                word_count = len(blueprint_text.split())
                sections_generated = self._count_sections(blueprint_text)
                action_items = self._extract_action_items(blueprint_text)
                timeline = self._extract_timeline(blueprint_text)
                budget = self._extract_budget(blueprint_text)
            
            print(f"[{self.agent_name}] Generated {word_count} words, {sections_generated}/12 sections")
            print(f"[{self.agent_name}] Quality Score: {quality_score:.2%}")
            
            # Store in memory if available
            if self.memory_store and blueprint_text:
                try:
                    memory_doc = {
                        "type": "gtm_blueprint",
                        "company": company_info,
                        "content": blueprint_text[:2000],
                        "quality_score": quality_score,
                        "sections": sections_generated,
                        "timestamp": datetime.now().isoformat()
                    }
                    self.memory_store.add_documents([memory_doc])
                    print(f"[{self.agent_name}] ✓ Stored in memory")
                except Exception as e:
                    print(f"[{self.agent_name}] Warning: Could not store in memory: {e}")
            
            # Store complete result in state
            state['analysis_results']['gtm_blueprint'] = {
                'content': blueprint_text,
                'quality_score': quality_score,
                'word_count': word_count,
                'sections_generated': sections_generated,
                'sections_target': 12,
                'completeness': f"{sections_generated}/12",
                'action_items': action_items[:10],
                'timeline': timeline,
                'budget': budget,
                'generated_at': datetime.now().isoformat(),
                'agent': self.agent_name,
                'max_tokens_used': self.max_tokens,
                'synthesized_agents': self.synthesized_agents
            }
            
            # Add quality warning if needed
            if quality_score < self.target_quality:
                print(f"[{self.agent_name}] ⚠️ Quality {quality_score:.2%} below target {self.target_quality:.2%}")
                state['analysis_results']['gtm_blueprint']['quality_warning'] = True
            
            # Check completeness
            if sections_generated < 12:
                print(f"[{self.agent_name}] ⚠️ Only {sections_generated}/12 sections generated")
                state['analysis_results']['gtm_blueprint']['incomplete'] = True
                state['analysis_results']['gtm_blueprint']['missing_sections'] = 12 - sections_generated
            
            # Run reflection for self-assessment
            reflection = self._reflect(state)
            state['analysis_results']['gtm_blueprint']['reflection'] = reflection
            
            print(f"[{self.agent_name}] ✅ GTM Blueprint complete and stored in state")
            print(f"[{self.agent_name}] " + "="*50 + "\n")
            
            return state
            
        except Exception as e:
            print(f"[{self.agent_name}] ❌ ERROR in process: {str(e)}")
            import traceback
            print(f"[{self.agent_name}] Stack trace:\n{traceback.format_exc()}")
            
            # Store error in state but don't crash workflow
            if 'errors' not in state:
                state['errors'] = []
            
            state['errors'].append({
                'agent': self.agent_name,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            })
            
            # Add minimal GTM blueprint so workflow can continue
            if 'analysis_results' not in state:
                state['analysis_results'] = {}
                
            state['analysis_results']['gtm_blueprint'] = {
                'content': f"ERROR: Failed to generate GTM blueprint - {str(e)}",
                'error': True,
                'error_message': str(e),
                'quality_score': 0.0,
                'sections_generated': 0,
                'sections_target': 12,
                'completeness': "0/12",
                'agent': self.agent_name
            }
            
            return state
    
    def determine_section_count(self, company_context: str) -> tuple:
        """
        Dynamically determine section count based on company complexity
        Returns: (total_sections, sections_per_part)
        """
        context_lower = company_context.lower()
        
        # Check for complexity indicators
        complexity_indicators = {
            'enterprise': 3,
            'fortune 500': 3,
            'global': 2,
            'multinational': 2,
            'complex': 2,
            'multi-product': 2,
            'b2b': 1,
            'saas': 1,
            'startup': -1,
            'small': -1,
            'simple': -2
        }
        
        complexity_score = 0
        for indicator, weight in complexity_indicators.items():
            if indicator in context_lower:
                complexity_score += weight
        
        # Determine sections based on complexity
        if complexity_score >= 4:
            # Complex: Full 12 sections in 3 parts
            print(f"[{self.agent_name}] High complexity detected - using 12 sections in 3 parts")
            return 12, 4
        elif complexity_score >= 0:
            # Medium: 10 sections in 2 parts
            print(f"[{self.agent_name}] Medium complexity - using 10 sections in 2 parts")
            return 10, 5
        else:
            # Simple: 8 sections in 2 parts
            print(f"[{self.agent_name}] Low complexity - using 8 sections in 2 parts")
            return 8, 4
        
    def process_gtm(self, task: str, shared_insights: Dict, llm) -> Dict[str, Any]:
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
    
    # [Keep all other methods exactly the same - _generate_response, _count_sections, etc.]
    # [I'm not repeating them here to save space, but they remain unchanged from your original file]
    
    def _generate_response(self, task: str, memories: List, llm) -> str:
     """Generate ADAPTIVE GTM blueprint based on complexity"""
    
     context = task
    
     # Determine complexity and sections needed
     total_sections, sections_per_part = self.determine_section_count(context)
     self.required_sections = total_sections
    
     print(f"[{self.agent_name}] Generating {total_sections}-section blueprint...")
    
     # Define all 12 possible sections
     all_sections = {
        1: ("EXECUTIVE SUMMARY", "Key opportunity, positioning, ROI projection"),
        2: ("MARKET ANALYSIS & OPPORTUNITY", "TAM/SAM/SOM, growth rates, competitive landscape"),
        3: ("IDEAL CUSTOMER PROFILE (ICP)", "Demographics, psychographics, buying process"),
        4: ("POSITIONING & MESSAGING", "Value prop, differentiation, proof points"),
        5: ("CHANNEL STRATEGY", "Distribution mix, CAC, conversion rates"),
        6: ("PRICING STRATEGY", "Model, packages, competitive analysis"),
        7: ("SALES ENABLEMENT", "Battle cards, playbooks, objection handling"),
        8: ("MARKETING CAMPAIGNS", "Themes, content strategy, demand gen"),
        9: ("IMPLEMENTATION TIMELINE", "30/60/90 day plan with milestones"),
        10: ("SUCCESS METRICS", "KPIs, dashboards, benchmarks"),
        11: ("BUDGET ALLOCATION", "Investment breakdown, ROI projections"),
        12: ("RISK MITIGATION", "Top risks, contingency plans")
    }
    
    # Select sections based on total count
     if total_sections == 8:
        # Essential sections only
        selected_sections = [1, 2, 3, 4, 5, 6, 9, 10]
     elif total_sections == 10:
          # Core + important additions
        selected_sections = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
     else:
        # All sections
         selected_sections = list(range(1, 13))
    
     # Calculate parts needed
     num_parts = (total_sections + sections_per_part - 1) // sections_per_part
    
     # Generate parts
     all_parts = []
    
     for part_num in range(num_parts):
        start_idx = part_num * sections_per_part
        end_idx = min(start_idx + sections_per_part, len(selected_sections))
        part_sections = selected_sections[start_idx:end_idx]
        
        # Build prompt for this part
        part_prompt = f"""
Create PART {part_num + 1} of a Go-To-Market Blueprint for:
{context}

Generate SECTIONS {part_sections[0]}-{part_sections[-1]} with EXACTLY 100-150 words per section.
Be concise but comprehensive. Focus on actionable specifics.

"""
        
        # Add section templates
        for section_num in part_sections:
            title, focus = all_sections[section_num]
            part_prompt += f"""
==================================================
{section_num}. {title}
==================================================
Focus: {focus}
Target: 100-150 words with specific metrics and actions

"""
        
        try:
            if llm:
                # Set optimal tokens per part
                original_max = None
                if hasattr(llm, 'max_tokens'):
                    original_max = llm.max_tokens
                    # Adjust tokens based on sections in this part
                    tokens_per_section = 400  # ~100-150 words
                    llm.max_tokens = min(tokens_per_section * len(part_sections) + 500, 4000)
                    print(f"[{self.agent_name}] Part {part_num + 1}: {len(part_sections)} sections, {llm.max_tokens} tokens")
                
                # Generate this part
                print(f"[{self.agent_name}] Generating Part {part_num + 1} (Sections {part_sections[0]}-{part_sections[-1]})...")
                response = llm.invoke(part_prompt)
                
                # Extract content
                if hasattr(response, 'content'):
                    part_content = response.content
                else:
                    part_content = str(response)
                
                # Count results
                words = len(part_content.split())
                sections_found = self._count_sections(part_content)
                print(f"[{self.agent_name}] Part {part_num + 1}: {words} words, {sections_found} sections")
                
                all_parts.append(part_content)
                
                # Restore original max_tokens
                if original_max is not None:
                    llm.max_tokens = original_max
                    
            else:
                all_parts.append(f"[Mock Part {part_num + 1}]")
        
        except Exception as e:
            print(f"[{self.agent_name}] Error in part {part_num + 1}: {e}")
            all_parts.append(f"[Error in Part {part_num + 1}: {str(e)}]")
    
     # Combine all parts
     blueprint = f"""GO-TO-MARKET BLUEPRINT - ADAPTIVE
==================================================
Company Complexity: {'High' if total_sections == 12 else 'Medium' if total_sections == 10 else 'Streamlined'}
Total Sections:{total_sections}
==================================================
"""
    
     for i, part in enumerate(all_parts):
        if i > 0:
            blueprint += f"\n==================================================\nCONTINUED - PART {i + 1}\n==================================================\n\n"
        blueprint += part
    
     blueprint += f"""

==================================================
END OF BLUEPRINT - {total_sections} SECTIONS
=================================================="""
    
    # Verify completeness
     final_word_count = len(blueprint.split())
     final_sections = self._count_sections(blueprint)
    
     print(f"[{self.agent_name}] Final: {final_word_count} words, {final_sections}/{total_sections} sections")
    
     # Quality adjustment based on completeness
     if final_sections >= total_sections:
        quality_modifier = 1.0
     else:
        quality_modifier = final_sections / total_sections
    
     print(f"[{self.agent_name}] Quality modifier: {quality_modifier:.2f}")
    
     return blueprint       
    # Include all the other methods from your original file unchanged...
    # [_count_sections, _build_gtm_context, _identify_agent_inputs, _verify_components, 
    #  _extract_action_items, _extract_timeline, _extract_budget, _calculate_quality_score,
    #  _create_shared_insights, _extract_insights_for_memory, _create_mock_response]
    
    # I'm keeping them all but not repeating to save space - they remain exactly as in your original
    
    def _count_sections(self, blueprint: str) -> int:
        """Count how many of the 12 sections are present"""
        sections_found = 0
        
        # Look for section numbers or headers
        for i in range(1, 13):
            patterns = [
                f"{i}\\.",
                f"{i}\\)",
                f"Section {i}",
                f"#{i}",
                f"Part {i}"
            ]
            
            for pattern in patterns:
                if re.search(pattern, blueprint, re.IGNORECASE):
                    sections_found += 1
                    break
        
        # Also check for section names
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
        
        action_patterns = [
            r'(?:Week \d+:|Day \d+:)\s*([^.\n]+)',
            r'(?:Action:|Task:|Deliverable:)\s*([^.\n]+)',
            r'(?:- )\s*(?:Create|Build|Launch|Develop|Implement|Execute)\s+([^.\n]+)',
            r'(?:PHASE \d+).*?(?:- )([^.\n]+)'
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, blueprint, re.IGNORECASE | re.MULTILINE)
            action_items.extend([m.strip() for m in matches if isinstance(m, str)])
        
        return list(set(action_items[:20]))
    
    def _extract_timeline(self, blueprint: str) -> Dict[str, List[str]]:
        """Extract timeline and milestones"""
        timeline = {
            '30_days': [],
            '60_days': [],
            '90_days': [],
            'ongoing': []
        }
        
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
        
        total_patterns = [
            r'(?:total budget|total investment).*?\$([0-9,]+)(?:[KMB])?',
            r'\$([0-9,]+)(?:[KMB])?\s*(?:total|budget|investment)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, blueprint, re.IGNORECASE)
            if match:
                budget['total'] = match.group(1)
                break
        
        roi_pattern = r'(?:roi|return).*?([0-9]+)%'
        roi_match = re.search(roi_pattern, blueprint, re.IGNORECASE)
        if roi_match:
            budget['roi'] = f"{roi_match.group(1)}%"
        
        return budget
    
    def _calculate_quality_score(self, blueprint: str) -> float:
        """Calculate quality score based on completeness and detail"""
        
        score = 0.40
        
        sections_found = self._count_sections(blueprint)
        # Use dynamic required_sections instead of hardcoded 12
        score += (sections_found / self.required_sections) * 0.40
        
        components = self._verify_components(blueprint)
        components_found = sum(components.values())
        score += (components_found / len(components)) * 0.15
        
        word_count = len(blueprint.split())
        if word_count >= 2000:
            score += 0.05
        if word_count >= 3000:
            score += 0.05
        
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
        
        if len(self.synthesized_agents) >= 3:
            score += 0.05
        
        # Calculate expected word count based on required sections
        min_expected_words = self.required_sections * 100  # Minimum 100 words per section
        target_expected_words = self.required_sections * 125  # Target 125 words per section
        high_quality_words = self.required_sections * 150  # Excellent 150 words per section
        
        if sections_found >= self.required_sections and word_count >= target_expected_words:
            score = max(score, 0.85)
        
        if sections_found >= self.required_sections and word_count >= high_quality_words:
            score = max(score, 0.95)
            
        return min(score, 1.0)
    
    def _create_mock_response(self) -> str:
        """Create a mock GTM response for testing without LLM"""
        return """
==================================================
1. EXECUTIVE SUMMARY
==================================================
Mock GTM strategy for testing. This blueprint provides comprehensive go-to-market strategy.

==================================================
2. MARKET ANALYSIS & OPPORTUNITY
==================================================
TAM: $10B, SAM: $2B, SOM: $200M
Market growing at 25% annually.

==================================================
3. IDEAL CUSTOMER PROFILE (ICP)
==================================================
Target: Mid-market B2B SaaS companies, 100-500 employees, $10M-$50M revenue.

==================================================
4. POSITIONING & MESSAGING FRAMEWORK
==================================================
Position as premium solution for growth-stage companies.

==================================================
5. CHANNEL STRATEGY & TACTICS
==================================================
Primary: Direct sales (60%), Partner channel (30%), Digital (10%).

==================================================
6. PRICING STRATEGY
==================================================
Subscription model: $5K-$25K/month based on usage.

==================================================
7. SALES ENABLEMENT TOOLKIT
==================================================
Battle cards, objection handling, demo scripts provided.

==================================================
8. MARKETING CAMPAIGN PLAN
==================================================
Content-led growth with focus on thought leadership.

==================================================
9. IMPLEMENTATION TIMELINE
==================================================
Phase 1 (Days 1-30): Foundation
Phase 2 (Days 31-60): Launch
Phase 3 (Days 61-90): Scale

==================================================
10. SUCCESS METRICS & KPIs
==================================================
Track: Pipeline velocity, CAC, LTV, conversion rates.

==================================================
11. BUDGET ALLOCATION
==================================================
Total: $500K first year. Sales: 40%, Marketing: 35%, Tech: 25%.

==================================================
12. RISK MITIGATION PLAN
==================================================
Key risks: Competition, market timing, resource constraints.
"""


# Module test
if __name__ == "__main__":
    print("=" * 70)
    print("GTM BLUEPRINT AGENT TEST - WITH ABSTRACT METHOD")
    print("=" * 70)
    
    agent = GTMBlueprintAgent()
    print(f"\n✅ Agent initialized: {agent.agent_name}")
    print(f"  • Max tokens: {agent.max_tokens}")
    print(f"  • Target quality: {agent.target_quality}")
    print(f"  • Required sections: {agent.required_sections}")
    
    # Test methods exist
    print(f"\n🔍 Method Check:")
    print(f"  • Has process: {hasattr(agent, 'process')}")
    print(f"  • Has process_gtm: {hasattr(agent, 'process_gtm')}")
    print(f"  • Has _reflect: {hasattr(agent, '_reflect')}")  # NEW CHECK
    print(f"  • Has _generate_response: {hasattr(agent, '_generate_response')}")
    print(f"  • Has _calculate_quality_score: {hasattr(agent, '_calculate_quality_score')}")
    
    # Test property setters
    print(f"\n🔧 Testing Property Setters:")
    test_llm = "test_llm_instance"
    agent.llm = test_llm
    print(f"  • LLM setter works: {agent.llm == test_llm}")
    
    test_memory = "test_memory_instance"
    agent.memory_store = test_memory
    print(f"  • Memory setter works: {agent.memory_store == test_memory}")
    
    # Test reflection method
    print(f"\n🪞 Testing _reflect method:")
    test_state = {
        "company_info": "Test Company Inc.",
        "analysis_results": {
            "psychological": {"test": "data"},
            "competitor": {"test": "data"},
            "gtm_blueprint": {
                "sections_generated": 10,
                "sections_target": 12,
                "quality_score": 0.75,
                "word_count": 2500,
                "timeline": {"30_days": ["Task 1"]},
                "budget": {"total": "500K"},
                "action_items": ["Action 1", "Action 2"]
            }
        }
    }
    
    reflection = agent._reflect(test_state)
    print(f"  • Reflection executed: {reflection['summary']}")
    print(f"  • Analysis complete: {reflection['analysis_complete']}")
    print(f"  • Improvements needed: {len(reflection['improvements_needed'])} items")
    
    # Test with mock state
    print(f"\n🧪 Testing process method with mock state...")
    
    try:
        result = agent.process(test_state)
        print(f"✅ Process method executed successfully")
        print(f"  • GTM Blueprint added: {'gtm_blueprint' in result.get('analysis_results', {})}")
        print(f"  • Quality score: {result['analysis_results']['gtm_blueprint']['quality_score']:.2%}")
        print(f"  • Sections: {result['analysis_results']['gtm_blueprint']['completeness']}")
        print(f"  • Has reflection: {'reflection' in result['analysis_results']['gtm_blueprint']}")
    except Exception as e:
        print(f"❌ Process method failed: {e}")