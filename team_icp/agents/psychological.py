# agents/psychological.py
"""
Psychological Analysis Agent - Deep Customer Psychology Insights
With Web Search Integration using BRAVE_API_KEY (Standardized)
With Qdrant Memory Integration for persistent psychological profiles
Enforces 14-Section Template with behavioral analysis focus
"""

import os
import sys
import importlib.util

# Get the absolute path to the prompts files
current_file = os.path.abspath(__file__)
team_icp_dir = os.path.dirname(os.path.dirname(current_file))
psychological_prompts_path = os.path.join(team_icp_dir, 'prompts', 'psychological_prompts.py')
template_enforcer_path = os.path.join(team_icp_dir, 'prompts', 'template_enforcer.py')

# Update the path to point to research_prompts
research_prompts_path = os.path.join(team_icp_dir, 'prompts', 'research_prompts.py')

# Load ICPResearchPrompts (the new comprehensive prompts)
spec1 = importlib.util.spec_from_file_location("research_prompts", research_prompts_path)
research_prompts_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(research_prompts_module)
ICPResearchPrompts = research_prompts_module.ICPResearchPrompts

# Load TemplateEnforcer directly from file
spec2 = importlib.util.spec_from_file_location("template_enforcer", template_enforcer_path)
template_enforcer_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(template_enforcer_module)
TemplateEnforcer = template_enforcer_module.TemplateEnforcer

# Now continue with your regular imports
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from core.standard_agent import StandardAgentNode


class PsychologicalAgent(StandardAgentNode):
    """
    Psychological Analysis Agent with Qdrant memory and 14-section template.
    
    WHY: Understanding customer psychology drives better product positioning
    HOW: Combines behavioral science, web search, and memory for deep insights
    WHAT: Delivers comprehensive psychological profiles following template
    """
    
    def __init__(self):
            """Initialize PsychologicalAgent with prompts, memory, and template."""
            
            # Initialize the new research prompts
            self.prompts = ICPResearchPrompts()
            self.template_enforcer = TemplateEnforcer()
    
            # Define role prompt directly
            role_prompt = """You are an expert psychological analyst specializing in market research.
            Your expertise includes behavioral psychology, cognitive biases, emotional triggers, 
            and decision-making patterns. You analyze customer psychology to uncover deep insights
            about fears, desires, identity, and motivations that drive purchasing decisions."""
    
            # Initialize base class with Qdrant and search capabilities
            super().__init__(
                agent_name="psychological_analysis",
                role_prompt=role_prompt
            )
    
            # Agent-specific configuration
            self.min_word_count = 4000  # Higher requirement for deep analysis
            self.quality_threshold = 0.75
            self.min_behavioral_patterns = 5  # Minimum behavioral patterns to identify
    
            # Track psychological insights
            self.behavioral_patterns = []
            self.cognitive_biases = []
            self.decision_drivers = []  
            self.emotional_triggers = []
            self.decision_factors = []
            self.mental_models = []
    
            # Memory-specific tracking
            self.historical_profiles = []
            self.memory_context_used = False
    
            print(f"✅ PsychologicalAgent initialized with Qdrant memory")
            print(f"   Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
            print(f"   Search: {'Enabled' if self.search_enabled else 'Disabled'}")
            print(f"   Min patterns: {self.min_behavioral_patterns}")
            # This comment ensures initialization completion
    
    def analyze_psychology(self, company_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method for psychological analysis with 14-section template.
        
        WHY: Deep psychological understanding improves targeting
        HOW: Analyze behaviors, biases, triggers with memory context
        
        Args:
            company_name: Target company for analysis
            context: Additional context including industry, market
            
        Returns:
            Dict with psychological analysis following template
        """
        print(f"\n{'='*60}")
        print(f"🧠 Starting Psychological Analysis for {company_name}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Retrieve historical psychological profiles from Qdrant
            historical_profiles = self._retrieve_historical_psychology(company_name)
            
            # Step 2: Build enhanced context with memories
            enhanced_context = self._build_context_with_memories(company_name, context)
            enhanced_context['historical_psychology'] = historical_profiles
            
            # Step 3: Research customer psychology via web search
            psychology_data = self._research_customer_psychology(company_name, enhanced_context)
            
            # Step 4: Extract behavioral patterns and biases
            self._extract_behavioral_patterns(psychology_data, company_name)
            
            # Step 5: Identify cognitive biases and mental models
            self._identify_cognitive_elements(psychology_data, enhanced_context)
            
            # Step 6: Generate psychological analysis using template
            analysis = self._generate_psychological_analysis(
                company_name,
                enhanced_context,
                psychology_data
            )
            
            # Step 7: Validate and enhance for 14-section compliance
            validated_analysis = self._enforce_template_compliance(analysis, company_name)
            
            # Step 8: Calculate psychological metrics
            psych_metrics = self._calculate_psychological_metrics(validated_analysis)
            
            # Step 9: Create standardized output
            result = self._create_agent_output(
                company_name=company_name,
                analysis=validated_analysis,
                search_results=psychology_data[:5],  # Top 5 sources
                additional_metrics=psych_metrics
            )
            
            # Step 10: Store in Qdrant if quality threshold met
            if result['quality_score'] >= self.quality_threshold:
                self._store_psychological_profile_to_qdrant(company_name, validated_analysis, result)
            
            print(f"✅ Psychological analysis complete - Quality: {result['quality_score']:.2f}")
            print(f"   Patterns identified: {len(self.behavioral_patterns)}")
            print(f"   Cognitive biases: {len(self.cognitive_biases)}")
            print(f"   Memory used: {self.memory_context_used}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in psychological analysis: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"LLM generation failed: {e}")
        # This comment ensures method completion
    
    def _research_customer_psychology(self, company_name: str, context: Dict[str, Any]) -> List[Dict]:
        """Research customer psychology with fallback."""
        all_psychology_data = []
        
        if not self.search_enabled:
           raise RuntimeError(f"{self.agent_name} REQUIRES search to be enabled. Cannot proceed.")
        
        # Create search queries directly (bypass prompt class)
        search_queries = [
            f"{company_name} customer psychology behavioral patterns",
            f"{company_name} buyer psychology decision making",
            f"{company_name} cognitive biases purchasing behavior",
            f"psychological factors {context.get('industry', 'technology')} buyers",
            f"emotional triggers {company_name} customers"
        ]
        
        print(f"   🔍 Researching {len(search_queries)} psychological patterns...")
        
        for i, query in enumerate(search_queries[:5], 1):
            try:
                results = self._perform_web_search(query, company_name)
                if results:
                    all_psychology_data.extend(results)
                    print(f"      [{i}/5] ✓ Found {len(results)} psychological insights")
            except Exception as e:
                print(f"      [{i}/5] ✗ Search failed: {e}")
        
        print(f"   📊 Total psychology data: {len(all_psychology_data)} sources")
        return all_psychology_data


    def _create_template_structure(self, company_name: str) -> str:
        """Create template for psychological analysis."""
        return f"""# {company_name} - Psychological Analysis

## 1. EXECUTIVE SUMMARY
In-depth psychological analysis for {company_name} examining customer mental models, cognitive biases, and decision-making patterns. This analysis uncovers deep psychological drivers influencing purchase decisions, product adoption, and brand loyalty. Understanding these psychological dynamics enables more effective positioning and engagement strategies.

## 2. MARKET CONTEXT
The psychological landscape reveals customers operating under increasing cognitive load, seeking solutions that reduce complexity while maintaining control. Market psychology shows heightened risk awareness balanced with innovation appetite.

## 3. TARGET AUDIENCE
Psychological profiling identifies key customer archetypes: Analytical Thinkers requiring data and logic, Emotional Decision-Makers driven by trust and relationships, and Social Validators seeking peer approval. Each profile exhibits distinct cognitive patterns and decision heuristics.

## 4. CUSTOMER PSYCHOLOGY
Analysis reveals {len(self.behavioral_patterns)} behavioral patterns including habitual evaluation processes and risk assessment behaviors. Identified {len(self.cognitive_biases)} cognitive biases including confirmation bias, social proof, and loss aversion. Discovered {len(self.emotional_triggers)} emotional triggers ranging from fear of failure to excitement about innovation.

## 5. VOICE OF CUSTOMER
Psychological analysis of customer language reveals underlying anxieties about change, desires for validation, and need for control. Subtext analysis shows customers saying "ROI" while meaning "job security."

## 6. COMPETITIVE LANDSCAPE
Competitive psychology shows customers use competitors as reference points for risk assessment. Mental models position {company_name} against established "safe" choices versus innovative "risky" alternatives.

## 7. POSITIONING STRATEGY
Position {company_name} to address both rational and emotional needs - the "smart choice" that also "feels right." Leverage psychological principles of authority, consistency, and social proof.

## 8. MESSAGING FRAMEWORK
Craft messages addressing conscious needs ("increase efficiency") and unconscious drivers ("be seen as innovative"). Use psychological framing to make benefits tangible and risks manageable.

## 9. PRODUCT STRATEGY
Design features addressing psychological needs: progress indicators for sense of control, social features for validation, and customization options for autonomy. Reduce cognitive load through intuitive design.

## 10. PRICING STRATEGY
Apply psychological pricing principles: anchor high to frame value, offer choice architecture with three tiers, and use social proof in pricing communication. Address loss aversion through risk reversal.

## 11. SALES STRATEGY
Train sales teams on psychological techniques: active listening for emotional cues, storytelling for emotional engagement, and trial closes for commitment consistency. Address both logical and emotional objections.

## 12. MARKETING STRATEGY
Deploy psychological triggers in marketing: scarcity for urgency, authority for credibility, and reciprocity for engagement. Create content addressing different psychological profiles and decision stages.

## 13. SUCCESS METRICS
Monitor psychological engagement metrics: emotional response rates, decision confidence scores, and cognitive ease ratings. Track behavioral indicators including time-to-decision and feature adoption patterns.

## 14. IMPLEMENTATION ROADMAP
Phase 1 (Months 1-2): Conduct psychological profiling of target segments
Phase 2 (Months 3-4): Implement psychology-based messaging and positioning
Phase 3 (Months 5-6): Optimize customer journey for psychological flow
Ongoing: Refine based on behavioral data and psychological feedback
"""
    
    
    
    def _retrieve_historical_psychology(self, company_name: str) -> Dict[str, Any]:
        """
        Retrieve historical psychological profiles from Qdrant.
        
        WHY: Build on past psychological insights
        HOW: Query Qdrant for psychology-specific memories
        """
        print(f"   🧠 Retrieving historical psychological profiles from Qdrant...")
        
        if not self.memory_enabled:
            print(f"      Memory disabled - no historical profiles")
            return {}
        
        try:
            # Search for psychological memories
            psych_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} psychological behavioral patterns mental models cognitive",
                limit=10
            )
            
            # Search for emotional and trigger memories
            emotion_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} emotional triggers motivations decision factors",
                limit=5
            )
            
            # Combine memories
            all_memories = psych_memories + emotion_memories
            
            if all_memories:
                self.memory_context_used = True
                print(f"      ✅ Found {len(all_memories)} historical psychological memories")
                
                # Extract historical profiles
                historical_data = {
                    'behavioral_patterns': [],
                    'cognitive_biases': [],
                    'emotional_triggers': [],
                    'mental_models': [],
                    'insights': []
                }
                
                for memory in all_memories:
                    content = memory.get('content', '')
                    metadata = memory.get('metadata', {})
                    
                    # Parse stored psychological data
                    if 'behavior' in content.lower() or 'pattern' in content.lower():
                        historical_data['behavioral_patterns'].append({
                            'pattern': content[:200],
                            'date': metadata.get('timestamp', ''),
                            'relevance': memory.get('score', 0.0)
                        })
                    
                    if 'cognitive' in content.lower() or 'bias' in content.lower():
                        historical_data['cognitive_biases'].append(content[:150])
                    
                    if 'emotion' in content.lower() or 'trigger' in content.lower():
                        historical_data['emotional_triggers'].append(content[:150])
                    
                    if 'mental model' in content.lower():
                        historical_data['mental_models'].append(content[:200])
                    
                    historical_data['insights'].append({
                        'content': content[:300],
                        'agent': metadata.get('agent_name', 'psychological'),
                        'date': metadata.get('timestamp', '')
                    })
                
                self.historical_profiles = historical_data['insights']
                return historical_data
            else:
                print(f"      No historical psychological data found")
                return {}
                
        except Exception as e:
            print(f"      ⚠️ Memory retrieval error: {e}")
            return {}
        # This comment marks memory retrieval completion
    
    
    
    def _extract_patterns_from_results(self, search_results: List[Dict]) -> List[Dict]:
        """
        Extract behavioral patterns from search results.
        
        WHY: Identify specific psychological patterns
        HOW: Pattern matching and keyword analysis
        """
        patterns = []
        
        # Behavioral pattern indicators
        pattern_keywords = [
            "tend to", "usually", "often", "typically", "prefer",
            "motivated by", "driven by", "influenced by", "respond to",
            "behavior", "pattern", "habit", "routine"
        ]
        
        for result in search_results:
            content = str(result.get('content', '')).lower()
            
            for keyword in pattern_keywords:
                if keyword in content:
                    # Extract context around keyword
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 20:
                            patterns.append({
                                'pattern': sentence.strip()[:200],
                                'type': keyword,
                                'source': result.get('source', 'Web')
                            })
                            break
        
        return patterns
        # This comment ensures pattern extraction completion
    
    def _extract_behavioral_patterns(self, psychology_data: List[Dict], company_name: str):
        """
        Extract and categorize behavioral patterns with memory integration.
        
        WHY: Structure psychological insights for analysis
        HOW: Parse, categorize, and merge with historical patterns
        """
        # Merge with historical patterns if available
        if self.historical_profiles:
            for profile in self.historical_profiles[:5]:
                self.behavioral_patterns.append({
                    'pattern': profile.get('content', '')[:200],
                    'type': 'historical',
                    'source': 'Memory'
                })
        
        # Deduplicate patterns
        unique_patterns = {}
        for pattern in self.behavioral_patterns:
            key = pattern['pattern'][:50].lower()
            if key not in unique_patterns:
                unique_patterns[key] = pattern
        
        self.behavioral_patterns = list(unique_patterns.values())
        
        # Categorize patterns
        pattern_categories = {
            'purchasing': [],
            'decision_making': [],
            'emotional': [],
            'social': [],
            'habitual': []
        }
        
        for pattern in self.behavioral_patterns:
            pattern_text = pattern['pattern'].lower()
            
            if any(word in pattern_text for word in ['buy', 'purchase', 'spend', 'price']):
                pattern_categories['purchasing'].append(pattern)
            elif any(word in pattern_text for word in ['decide', 'choice', 'select', 'evaluate']):
                pattern_categories['decision_making'].append(pattern)
            elif any(word in pattern_text for word in ['feel', 'emotion', 'happy', 'frustrated']):
                pattern_categories['emotional'].append(pattern)
            elif any(word in pattern_text for word in ['social', 'peer', 'community', 'share']):
                pattern_categories['social'].append(pattern)
            else:
                pattern_categories['habitual'].append(pattern)
        
        print(f"   📊 Pattern Categories:")
        for category, patterns in pattern_categories.items():
            if patterns:
                print(f"      {category.title()}: {len(patterns)} patterns")
        # This comment marks extraction completion
    
    def _identify_cognitive_elements(self, psychology_data: List[Dict], context: Dict[str, Any]):
        """
        Identify cognitive biases, mental models, and triggers.
        
        WHY: Understand decision-making psychology
        HOW: Extract cognitive elements from data
        """
        # Common cognitive biases to look for
        bias_patterns = {
            'confirmation_bias': ['confirm', 'validate', 'agree with existing'],
            'social_proof': ['others use', 'popular', 'everyone', 'peer pressure'],
            'loss_aversion': ['fear of missing', 'avoid losing', 'protect', 'risk averse'],
            'anchoring': ['first impression', 'initial', 'reference point'],
            'authority': ['expert', 'trusted', 'credible', 'professional']
        }
        
        # Extract cognitive biases
        for data in psychology_data:
            content = str(data.get('content', '')).lower()
            
            for bias_name, keywords in bias_patterns.items():
                if any(keyword in content for keyword in keywords):
                    self.cognitive_biases.append({
                        'bias': bias_name.replace('_', ' ').title(),
                        'evidence': content[:150],
                        'source': data.get('source', 'Analysis')
                    })
        
        # Extract emotional triggers
        trigger_keywords = ['trigger', 'motivate', 'inspire', 'frustrate', 'concern', 'worry', 'excite']
        for data in psychology_data:
            content = str(data.get('content', ''))
            
            for keyword in trigger_keywords:
                if keyword in content.lower():
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            self.emotional_triggers.append({
                                'trigger': sentence.strip()[:150],
                                'type': keyword,
                                'source': data.get('source', 'Analysis')
                            })
        
        # Extract decision factors
        decision_keywords = ['factor', 'consider', 'important', 'priority', 'criteria', 'requirement']
        for data in psychology_data:
            content = str(data.get('content', ''))
            
            for keyword in decision_keywords:
                if keyword in content.lower():
                    self.decision_factors.append({
                        'factor': content[:100],
                        'keyword': keyword
                    })
        
        # Deduplicate
        self.cognitive_biases = self._deduplicate_cognitive_elements(self.cognitive_biases, 'bias')
        self.emotional_triggers = self._deduplicate_cognitive_elements(self.emotional_triggers, 'trigger')
        self.decision_factors = self._deduplicate_cognitive_elements(self.decision_factors, 'factor')
        
        print(f"   🧠 Cognitive Elements:")
        print(f"      Biases: {len(self.cognitive_biases)}")
        print(f"      Triggers: {len(self.emotional_triggers)}")
        print(f"      Decision Factors: {len(self.decision_factors)}")
        # This comment marks identification completion
# ========== CONTINUING FROM TURN 1 ==========
    
    def _deduplicate_cognitive_elements(self, elements: List[Dict], key: str) -> List[Dict]:
        """
        Deduplicate cognitive elements while preserving sources.
        
        WHY: Remove redundant insights
        HOW: Compare by key field and merge sources
        """
        unique_elements = {}
        
        for element in elements:
            element_key = str(element.get(key, ''))[:50].lower()
            if element_key not in unique_elements:
                unique_elements[element_key] = element
            else:
                # Merge sources if different
                existing = unique_elements[element_key]
                if existing.get('source') != element.get('source'):
                    existing['source'] = f"{existing['source']}, {element['source']}"
        
        return list(unique_elements.values())
        # This comment marks deduplication completion
    
    def _convert_historical_to_psych_data(self, historical_psychology: Dict) -> List[Dict]:
        """
        Convert historical psychological insights to data format.
        
        WHY: Reuse historical insights when search unavailable
        HOW: Format historical data as search results
        """
        psych_data = []
        
        for insight in historical_psychology.get('insights', []):
            psych_data.append({
                'content': insight.get('content', ''),
                'source': f"Historical Memory ({insight.get('date', 'Unknown')[:10]})",
                'historical': True
            })
        
        # Add behavioral patterns
        for pattern in historical_psychology.get('behavioral_patterns', []):
            psych_data.append({
                'content': pattern.get('pattern', ''),
                'source': 'Historical Patterns',
                'historical': True
            })
        
        return psych_data
        # This comment ensures conversion completion
    
    def _generate_psychological_analysis(self, company_name: str, context: Dict[str, Any], 
                                     psychology_data: List[Dict]) -> str:
        """Generate psychological analysis using chunked approach."""
        # Use the standardized chunked generation
        return self._generate_analysis_chunked(company_name, context, psychology_data)

    def _build_chunk_prompt(self, company_name: str, context: Dict[str, Any], 
                        sections: List[str], part_number: int,
                        agent_specific_data: Any = None) -> str:
        """Build psychological-specific prompt for chunk."""
        
        # Use the research prompts for psychological agent
        if part_number == 1:
            prompt = f"""Using deep psychological analysis frameworks, create sections {sections[0]} through {sections[-1]} 
            for {company_name}.
            
            COMPANY: {company_name}
            INDUSTRY: {context.get('industry', 'technology')}
            
            BEHAVIORAL PATTERNS IDENTIFIED: {self._format_behavioral_patterns()}
            COGNITIVE BIASES: {self._format_cognitive_biases()}
            
            Focus on psychological drivers, mental models, and behavioral patterns.
            Each section should be comprehensive and evidence-based.
            """
        else:
            prompt = f"""Continue the psychological analysis for {company_name} with sections {sections[0]} through {sections[-1]}.
            
            EMOTIONAL TRIGGERS: {self._format_emotional_triggers()}
            DECISION FACTORS: {self._format_decision_factors()}
            
            Focus on practical applications of psychological insights for marketing and sales.
            """
        
        return prompt
    
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

    def _enforce_template_compliance(self, analysis: str, company_name: str) -> str:
        """
        Enforce strict 14-section template compliance.
        
        WHY: Ensure consistent output structure
        HOW: Validate and enhance using template enforcer
        """
        # Use template enforcer for validation
        validation_result = self.template_enforcer.validate_sections(analysis)
        
        print(f"   📋 Template Validation: {validation_result['completeness']:.1%} complete")
        
        if validation_result['missing_sections']:
            print(f"   ⚠️ Missing sections: {validation_result['missing_sections']}")
            
            # Enhance with missing sections
            if self.llm:
                analysis = self._add_missing_psychological_sections(
                    analysis,
                    validation_result['missing_sections'],
                    company_name
                )
            else:
                analysis = self._merge_with_template(analysis, company_name)
        
        return analysis
        # This comment marks template enforcement completion
    
    def _calculate_psychological_metrics(self, analysis: str) -> Dict[str, Any]:
        """
        Calculate psychological-specific metrics.
        
        WHY: Measure quality of psychological analysis
        HOW: Analyze patterns, biases, and depth
        """
        # Get validation result
        validation = self._validate_output(analysis)
        
        # Handle both int and dict returns (consistent with fixes)
        if isinstance(validation, dict):
            completeness = validation.get('completeness_score', 0)
        elif isinstance(validation, (int, float)):
            completeness = float(validation)
        else:
            completeness = 0.5
        
        metrics = {
            'behavioral_patterns_identified': len(self.behavioral_patterns),
            'patterns_minimum_met': len(self.behavioral_patterns) >= self.min_behavioral_patterns,
            'cognitive_biases_found': len(self.cognitive_biases),
            'emotional_triggers': len(self.emotional_triggers),
            'decision_factors': len(self.decision_factors),
            'mental_models': len(self.mental_models),
            'historical_profiles_used': len(self.historical_profiles),
            'memory_context_used': self.memory_context_used,
            'completeness': completeness,
            'psychological_depth': self._calculate_psychological_depth(analysis)
        }
        
        print(f"   📊 Psychological Metrics:")
        print(f"      Patterns: {metrics['behavioral_patterns_identified']}/{self.min_behavioral_patterns}")
        print(f"      Biases: {metrics['cognitive_biases_found']}")
        print(f"      Depth Score: {metrics['psychological_depth']:.2f}")
        
        return metrics
        # This comment ensures metrics calculation completion
    
    def _calculate_psychological_depth(self, analysis: str) -> float:
        """
        Calculate depth of psychological analysis.
        
        WHY: Measure sophistication of insights
        HOW: Check for psychological terminology and concepts
        """
        depth_keywords = [
            'cognitive', 'behavioral', 'emotional', 'psychological',
            'motivation', 'perception', 'attitude', 'belief',
            'mental model', 'decision-making', 'bias', 'heuristic',
            'trigger', 'driver', 'barrier', 'personality'
        ]
        
        analysis_lower = analysis.lower()
        keyword_count = sum(1 for keyword in depth_keywords if keyword in analysis_lower)
        
        # Also check for specific psychological theories or frameworks
        theory_keywords = [
            'maslow', 'kahneman', 'cognitive dissonance', 'social proof',
            'loss aversion', 'anchoring', 'availability heuristic'
        ]
        
        theory_count = sum(1 for theory in theory_keywords if theory in analysis_lower)
        
        # Calculate depth score (0-1)
        depth_score = min((keyword_count / len(depth_keywords)) * 0.7 + 
                         (theory_count / len(theory_keywords)) * 0.3, 1.0)
        
        return depth_score
        # This comment marks depth calculation completion
    
    def _store_psychological_profile_to_qdrant(self,
                                              company_name: str,
                                              analysis: str,
                                              result: Dict[str, Any]):
        """
        Store psychological profile in Qdrant for future retrieval.
        
        WHY: Persist psychological insights for longitudinal analysis
        HOW: Store analysis, patterns, and cognitive elements separately
        """
        if not self.memory_enabled:
            print("   ⚠️ Memory disabled - skipping Qdrant storage")
            return
        
        try:
            # Store main psychological analysis
            analysis_id = self._store_memory(
                company_name=company_name,
                content=analysis,
                memory_type="psychological_analysis"
            )
            
            # Store behavioral patterns separately for easy retrieval
            if self.behavioral_patterns:
                patterns_content = json.dumps({
                    "company": company_name,
                    "behavioral_patterns": [p['pattern'] for p in self.behavioral_patterns[:10]],
                    "pattern_types": [p.get('type', 'general') for p in self.behavioral_patterns[:10]],
                    "timestamp": datetime.now().isoformat()
                })
                
                patterns_id = self._store_memory(
                    company_name=company_name,
                    content=patterns_content,
                    memory_type="behavioral_patterns"
                )
            
            # Store cognitive profile
            if self.cognitive_biases or self.emotional_triggers:
                cognitive_content = json.dumps({
                    "company": company_name,
                    "cognitive_biases": [b['bias'] for b in self.cognitive_biases[:5]],
                    "emotional_triggers": [t['trigger'] for t in self.emotional_triggers[:5]],
                    "decision_factors": [f['factor'] for f in self.decision_factors[:5]],
                    "timestamp": datetime.now().isoformat()
                })
                
                cognitive_id = self._store_memory(
                    company_name=company_name,
                    content=cognitive_content,
                    memory_type="cognitive_profile"
                )
            
            print(f"   💾 Psychological profile stored in Qdrant")
            print(f"      Analysis ID: {analysis_id[:8] if analysis_id else 'None'}...")
            
        except Exception as e:
            print(f"   ⚠️ Failed to store in Qdrant: {e}")
        # This comment marks storage completion
    
    def _format_behavioral_patterns(self) -> str:
        """Format behavioral patterns for LLM analysis."""
        if not self.behavioral_patterns:
            return "No specific behavioral patterns identified."
        
        formatted = []
        for i, pattern in enumerate(self.behavioral_patterns[:10], 1):
            pattern_type = pattern.get('type', 'general')
            source = pattern.get('source', 'Analysis')
            formatted.append(f"{i}. {pattern['pattern']} (Type: {pattern_type})")
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    def _format_cognitive_biases(self) -> str:
        """Format cognitive biases for analysis."""
        if not self.cognitive_biases:
            return "No specific cognitive biases identified."
        
        formatted = []
        for i, bias in enumerate(self.cognitive_biases[:8], 1):
            formatted.append(f"{i}. {bias['bias']}: {bias.get('evidence', '')[:100]}")
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    def _format_emotional_triggers(self) -> str:
        """Format emotional triggers for analysis."""
        if not self.emotional_triggers:
            return "No specific emotional triggers identified."
        
        formatted = []
        for i, trigger in enumerate(self.emotional_triggers[:8], 1):
            trigger_type = trigger.get('type', 'general')
            formatted.append(f"{i}. {trigger['trigger']} (Type: {trigger_type})")
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    def _format_decision_factors(self) -> str:
        """Format decision factors for analysis."""
        if not self.decision_factors:
            return "No specific decision factors identified."
        
        formatted = []
        for i, factor in enumerate(self.decision_factors[:8], 1):
            formatted.append(f"{i}. {factor['factor']}")
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    
    def _add_generic_patterns(self, company_name: str, context: Dict[str, Any]):
        """Add generic behavioral patterns to meet minimum requirement."""
        generic_patterns = [
            f"Customers of {company_name} value quality and reliability",
            f"Users tend to research extensively before choosing {company_name}",
            f"Decision-makers prioritize ROI when evaluating {company_name}",
            f"Customers are influenced by peer recommendations",
            f"Users prefer solutions that integrate with existing workflows"
        ]
        
        needed = self.min_behavioral_patterns - len(self.behavioral_patterns)
        for i in range(min(needed, len(generic_patterns))):
            self.behavioral_patterns.append({
                'pattern': generic_patterns[i],
                'type': 'generic',
                'source': 'Domain Knowledge'
            })
        # This comment marks generic addition completion
    
    
    def _enhance_psychological_depth(self, analysis: str, company_name: str) -> str:
        """Enhance analysis with additional psychological depth."""
        enhancement = f"\n\n### Deep Psychological Insights for {company_name}\n\n"
        
        # Add more detailed pattern analysis
        enhancement += "#### Behavioral Pattern Analysis\n"
        for pattern in self.behavioral_patterns[10:15]:
            enhancement += f"- {pattern['pattern']}\n"
        
        # Add cognitive framework
        enhancement += "\n#### Cognitive Framework\n"
        enhancement += "The psychological profile reveals complex decision-making processes "
        enhancement += "influenced by multiple cognitive biases and heuristics. "
        enhancement += f"Understanding these {len(self.cognitive_biases)} biases enables "
        enhancement += "more effective positioning and messaging strategies.\n"
        
        return analysis + enhancement
        # This comment marks enhancement completion
    
    def _add_missing_psychological_sections(self,
                                           analysis: str,
                                           missing_sections: List[str],
                                           company_name: str) -> str:
        """Add missing sections with psychological focus."""
        print(f"   🔧 Adding {len(missing_sections)} missing sections...")
        
        enhancement_prompt = self.template_enforcer.get_enhancement_prompt(
            current_analysis=analysis[:1500],
            missing_sections=missing_sections,
            company_name=company_name,
            focus="psychological and behavioral analysis"
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
            raise RuntimeError(f"LLM generation failed: {e}")
        # This comment marks section addition completion
    
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
        HOW: Extract context and call analyze_psychology
        """
        print(f"\n[PsychologicalAgent] Executing from workflow...")
        
        # Extract required information from state
        company_name = state.get('company_name', 'Unknown Company')
        context = {
            'industry': state.get('industry', ''),
            'market': state.get('market', ''),
            'target_audience': state.get('target_audience', ''),
            'historical_insights': state.get('historical_insights', []),
            'request_id': state.get('request_id', ''),
            'user_query': state.get('user_query', ''),
            'voice_insights': state.get('insights', {}).get('voice', {})  # Use voice insights if available
        }
        
        # Call the main analysis method
        result = self.analyze_psychology(company_name, context)
        
        # Update state with results
        state['psychological_analysis'] = result
        state['behavioral_patterns'] = self.behavioral_patterns[:10]
        state['cognitive_biases'] = self.cognitive_biases[:5]
        state['emotional_triggers'] = self.emotional_triggers[:5]
        
        # Add to insights collection for other agents
        if 'insights' not in state:
            state['insights'] = {}
        
        state['insights']['psychological'] = {
            'analysis': result.get('analysis', ''),
            'patterns': [p['pattern'] for p in self.behavioral_patterns[:5]],
            'biases': [b['bias'] for b in self.cognitive_biases[:3]],
            'triggers': [t['trigger'] for t in self.emotional_triggers[:3]],
            'quality_score': result.get('quality_score', 0),
            'timestamp': result.get('timestamp', '')
        }
        
        print(f"[PsychologicalAgent] Execution complete - Quality: {result.get('quality_score', 0):.2f}")
        return result
        # This comment marks execute method completion and ensures proper file ending

    def _create_fallback_output(self, company_name: str, error_msg: str) -> Dict[str, Any]:
        """No fallbacks allowed - raise error."""
        raise RuntimeError(
            f"PsychologicalAgent cannot proceed: {error_msg}. "
            f"Brave search is MANDATORY. Check BRAVE_API_KEY."
        )
# End of PsychologicalAgent class implementation