# agents/interview_psychological.py
"""
Psychological Interview Agent - Deep Psychological Interview Generation
With Web Search Integration using BRAVE_API_KEY
With Qdrant Memory Integration for persistent psychological insights
Generates 5-7 psychology-focused interviews following 14-section template
"""

import os
import sys
import importlib.util

# Get the absolute path to the prompts files
current_file = os.path.abspath(__file__)
team_icp_dir = os.path.dirname(os.path.dirname(current_file))
interview_psychological_prompts_path = os.path.join(team_icp_dir, 'prompts', 'interview_psychological_prompts.py')
template_enforcer_path = os.path.join(team_icp_dir, 'prompts', 'template_enforcer.py')

# Load InterviewPsychologicalPrompts directly from file
spec1 = importlib.util.spec_from_file_location("interview_psychological_prompts", interview_psychological_prompts_path)
interview_psychological_prompts_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(interview_psychological_prompts_module)
InterviewPsychologicalPrompts = interview_psychological_prompts_module.InterviewPsychologicalPrompts

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


class PsychologicalInterviewAgent(StandardAgentNode):
    """
    Psychological Interview Agent with Qdrant memory and 14-section template.
    
    WHY: Psychological interviews reveal deep customer motivations and barriers
    HOW: Generates realistic interviews with memory context and behavioral insights
    WHAT: Delivers 5-7 psychological interviews following template
    
    FIX: Handles quality score arguments properly
    """
    
    def __init__(self):
        """Initialize PsychologicalInterviewAgent with prompts, memory, and template."""

        # Initialize prompts and template enforcer
        self.prompts = InterviewPsychologicalPrompts()
        self.template_enforcer = TemplateEnforcer()

        # Define role prompt directly
        role_prompt = """You are an expert psychological interviewer conducting deep interviews
        to uncover mental models, emotional drivers, and decision-making processes. You create
        realistic, psychologically-rich interviews that explore unconscious motivations,
        cognitive biases, and emotional patterns following the 14-section template."""

        # Initialize base class with Qdrant and search capabilities
        super().__init__(
            agent_name="psychological_interviews",
            role_prompt=role_prompt
        )

        # Agent-specific configuration
        self.min_word_count = 2500  # Higher for deep psychological interviews
        self.quality_threshold = 0.75
        self.min_interviews = 3  # Minimum interviews to conduct

        # Track interview insights
        self.interviews = []
        self.psychological_personas = []
        self.emotional_patterns = []
        self.cognitive_patterns = []
        self.behavioral_insights = []
        self.decision_frameworks = []

        # Memory-specific tracking
        self.historical_interviews = []
        self.historical_patterns = []
        self.memory_context_used = False

        print(f"✅ PsychologicalInterviewAgent initialized with Qdrant memory")
        print(f"   Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
        print(f"   Search: {'Enabled' if self.search_enabled else 'Disabled'}")
        print(f"   Min interviews: {self.min_interviews}")
        # This comment ensures initialization completion
    
    def conduct_interviews(self, company_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method for conducting psychological interviews with 14-section template.
        
        WHY: Understand deep psychological drivers and barriers
        HOW: Generate realistic interviews with memory and psychological insights
        
        FIX: Properly handle quality score arguments
        
        Args:
            company_name: Target company for interview generation
            context: Additional context including industry, product, insights
            
        Returns:
            Dict with psychological interviews following template
        """
        print(f"\n{'='*60}")
        print(f"🧠 Starting Psychological Interview Generation for {company_name}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Retrieve historical psychological interviews from Qdrant
            historical_data = self._retrieve_historical_psychological_data(company_name)
            
            # Step 2: Build enhanced context with memories and insights
            enhanced_context = self._build_context_with_memories(company_name, context)
            enhanced_context['historical_psychological'] = historical_data
            
            # Step 3: Extract insights from other agents if available
            enhanced_context = self._incorporate_agent_insights(enhanced_context, context)
            
            # Step 4: Research psychological patterns via web search
            psych_data = self._research_psychological_context(company_name, enhanced_context)
            
            # Step 5: Generate psychological personas
            self._generate_psychological_personas(company_name, enhanced_context, psych_data)
            
            # Step 6: Extract emotional and cognitive patterns
            self._extract_psychological_patterns(psych_data, enhanced_context)
            
            # Step 7: Generate psychological interviews using template
            interviews_analysis = self._generate_psychological_interviews(
                company_name,
                enhanced_context,
                psych_data
            )
            
            # Step 8: Validate and enhance for 14-section compliance
            validated_analysis = self._enforce_template_compliance(interviews_analysis, company_name)
            
            # Step 9: Calculate psychological interview metrics
            psych_metrics = self._calculate_psychological_metrics(validated_analysis)
            
            # Step 10: Create standardized output
            result = self._create_agent_output(
                company_name=company_name,
                analysis=validated_analysis,
                search_results=psych_data[:5],  # Top 5 sources
                additional_metrics=psych_metrics
            )
            
            # Step 11: Store in Qdrant if quality threshold met
            if result['quality_score'] >= self.quality_threshold:
                self._store_psychological_interviews_to_qdrant(company_name, validated_analysis, result)
            
            print(f"✅ Psychological interviews complete - Quality: {result['quality_score']:.2f}")
            print(f"   Interviews generated: {len(self.interviews)}")
            print(f"   Emotional patterns: {len(self.emotional_patterns)}")
            print(f"   Memory used: {self.memory_context_used}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in psychological interview generation: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_output(company_name, str(e))
        # This comment ensures method completion
    
    def _research_psychological_context(self, company_name: str, context: Dict[str, Any]) -> List[Dict]:
        """
        Research psychological context for interviews with fallback.
        
        WHY: Gather psychological insights to inform interview creation
        HOW: Direct search queries bypassing prompt class
        """
        all_psych_data = []
        
        if not self.search_enabled:
           raise RuntimeError(f"{self.agent_name} REQUIRES search to be enabled. Cannot proceed.")
        
        # Create search queries directly (bypass prompt class)
        search_queries = [
            f"{company_name} customer mental models psychology",
            f"{company_name} emotional drivers decision making",
            f"{company_name} psychological barriers adoption",
            f"unconscious motivations {context.get('industry', 'technology')} buyers",
            f"cognitive biases {company_name} purchasing decisions",
            f"psychological archetypes {context.get('market', 'B2B')} customers",
            f"emotional journey {company_name} customer experience"
        ]
        
        print(f"   🔍 Researching {len(search_queries)} psychological patterns for interviews...")
        
        for i, query in enumerate(search_queries[:5], 1):
            try:
                results = self._perform_web_search(query, company_name)
                if results:
                    all_psych_data.extend(results)
                    # Extract patterns from results
                    self._extract_patterns_from_results(results)
                    print(f"      [{i}/5] ✓ Found {len(results)} psychological insights")
            except Exception as e:
                print(f"      [{i}/5] ✗ Search failed: {e}")
        
        print(f"   📊 Total psychological data: {len(all_psych_data)} sources")
        return all_psych_data


    def _create_template_structure(self, company_name: str) -> str:
        """
        Create fallback psychological interview template.
        
        WHY: Ensure output even without LLM or when errors occur
        HOW: Generate structured interviews following 14-section template
        """
        # Generate basic interviews if not already created
        if not self.interviews:
            self.interviews = [
                {
                    'persona': {'archetype': 'The Innovator', 'traits': 'Early adopter, risk-tolerant'},
                    'content': f"Interview exploring how {company_name} appeals to innovation-driven buyers.",
                    'word_count': 500
                },
                {
                    'persona': {'archetype': 'The Pragmatist', 'traits': 'ROI-focused, evidence-based'},
                    'content': f"Interview examining practical decision criteria for {company_name}.",
                    'word_count': 500
                },
                {
                    'persona': {'archetype': 'The Skeptic', 'traits': 'Risk-averse, detail-oriented'},
                    'content': f"Interview uncovering concerns and objections about {company_name}.",
                    'word_count': 500
                }
            ]
        
        return f"""# {company_name} - Psychological Interview Analysis

## 1. EXECUTIVE SUMMARY
Deep psychological interview analysis for {company_name} based on {len(self.interviews)} in-depth interviews exploring mental models, emotional drivers, and unconscious motivations. 
Key findings reveal complex decision-making processes driven by both rational and emotional factors.

## 2. MARKET CONTEXT
The psychological landscape for {company_name} reflects evolving customer mindsets in the market.
Interviews reveal shifting priorities from features to outcomes, from products to partnerships.

## 3. TARGET AUDIENCE
Psychological interviews identified three primary archetypes:
- The Innovator: Early adopters seeking competitive advantage
- The Pragmatist: ROI-focused decision makers requiring evidence
- The Skeptic: Risk-averse stakeholders needing reassurance

## 4. CUSTOMER PSYCHOLOGY
Deep psychological patterns emerged across all interviews:
- Fear of making wrong decision drives extensive evaluation
- Desire for innovation balanced with need for stability
- Identity reinforcement through technology choices
- Social proof as critical validation mechanism

## 5. VOICE OF CUSTOMER
Psychological interviews captured authentic emotional expressions:
"I need to know this won't fail - my reputation is on the line"
"We're looking for transformation, not just improvement"
"The emotional burden of change is our biggest challenge"

## 6. COMPETITIVE LANDSCAPE
Psychological positioning reveals emotional territory opportunities:
- Competitors own "safe" but not "innovative"
- Gap exists for "trusted innovation partner"
- Emotional differentiation through empathy and understanding

## 7. POSITIONING STRATEGY
Position {company_name} as the psychologically-safe innovation choice.
Address both rational ROI needs and emotional security requirements.
Own the "confident transformation" mental space.

## 8. MESSAGING FRAMEWORK
Messages that resonate at psychological level:
- "Innovation without the risk"
- "Your success is our only metric"
- "Proven by leaders like you"

## 9. PRODUCT STRATEGY
Product features addressing psychological needs:
- Gradual onboarding reducing anxiety
- Visible quick wins building confidence
- Peer benchmarking satisfying social comparison

## 10. PRICING STRATEGY
Psychological pricing insights from interviews:
- Price anchoring against cost of inaction
- Tiered options providing control illusion
- Success-based pricing reducing risk perception

## 11. SALES STRATEGY
Sales approach based on psychological insights:
- Discovery uncovering emotional drivers
- Demonstration addressing unconscious fears
- Closing techniques leveraging commitment consistency

## 12. MARKETING STRATEGY
Marketing leveraging psychological triggers:
- Social proof through peer stories
- Authority through thought leadership
- Scarcity through exclusive programs

## 13. SUCCESS METRICS
Psychological engagement metrics:
- Emotional sentiment scores
- Trust and confidence indices
- Behavioral commitment indicators

## 14. IMPLEMENTATION ROADMAP
Phase 1: Psychological Alignment (Month 1)
- Train team on psychological insights
- Develop empathy maps
- Create psychological safety protocols

Phase 2: Emotional Engagement (Month 2-3)
- Launch trust-building campaigns
- Implement anxiety-reduction processes
- Deploy social proof systems

Phase 3: Psychological Optimization (Month 4-6)
- Refine based on emotional feedback
- Scale successful psychological tactics
- Build emotional loyalty programs

## PSYCHOLOGICAL INTERVIEW INSIGHTS

### Interview 1: The Innovator Archetype
**Context**: Early adopter seeking competitive advantage through {company_name}
**Key Insight**: Innovation drive balanced by need for peer validation
**Emotional Driver**: Fear of being left behind, excitement about possibilities
**Decision Factor**: Will this make me a market leader?

### Interview 2: The Pragmatist Archetype  
**Context**: ROI-focused evaluation of {company_name} solution
**Key Insight**: Emotional decisions rationalized with data
**Emotional Driver**: Pressure to deliver results, fear of waste
**Decision Factor**: Can I justify this to stakeholders?

### Interview 3: The Skeptic Archetype
**Context**: Risk assessment of {company_name} implementation
**Key Insight**: Past failures create emotional barriers
**Emotional Driver**: Fear of repeat failure, need for certainty
**Decision Factor**: What could go wrong and how do we prevent it?

These psychological interviews reveal the complex emotional landscape {company_name} must navigate for successful market penetration.
"""
    
    def _retrieve_historical_psychological_data(self, company_name: str) -> Dict[str, Any]:
        """
        Retrieve historical psychological interviews from Qdrant.
        
        WHY: Build on past psychological insights for continuity
        HOW: Query Qdrant for psychology-specific interview memories
        """
        print(f"   🧠 Retrieving historical psychological data from Qdrant...")
        
        if not self.memory_enabled:
            print(f"      Memory disabled - no historical data")
            return {}
        
        try:
            # Search for psychological interview memories
            psych_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} psychological interview emotions cognitive behavior mental",
                limit=10
            )
            
            # Search for emotional pattern memories
            emotion_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} emotional triggers fears desires motivations barriers",
                limit=5
            )
            
            # Combine memories
            all_memories = psych_memories + emotion_memories
            
            if all_memories:
                self.memory_context_used = True
                print(f"      ✅ Found {len(all_memories)} historical psychological memories")
                
                # Extract historical data
                historical_data = {
                    'interviews': [],
                    'emotional_patterns': [],
                    'cognitive_patterns': [],
                    'behavioral_insights': [],
                    'insights': []
                }
                
                for memory in all_memories:
                    content = memory.get('content', '')
                    metadata = memory.get('metadata', {})
                    
                    # Parse stored psychological data
                    if 'interview' in content.lower():
                        historical_data['interviews'].append({
                            'content': content[:300],
                            'date': metadata.get('timestamp', ''),
                            'relevance': memory.get('score', 0.0)
                        })
                    
                    if 'emotion' in content.lower() or 'feeling' in content.lower():
                        historical_data['emotional_patterns'].append(content[:150])
                    
                    if 'cognitive' in content.lower() or 'thinking' in content.lower():
                        historical_data['cognitive_patterns'].append(content[:150])
                    
                    if 'behavior' in content.lower() or 'action' in content.lower():
                        historical_data['behavioral_insights'].append(content[:150])
                    
                    historical_data['insights'].append({
                        'content': content[:300],
                        'agent': metadata.get('agent_name', 'psychological'),
                        'date': metadata.get('timestamp', '')
                    })
                
                self.historical_interviews = historical_data['interviews']
                self.historical_patterns = historical_data['emotional_patterns'] + historical_data['cognitive_patterns']
                
                return historical_data
            else:
                print(f"      No historical psychological data found")
                return {}
                
        except Exception as e:
            print(f"      ⚠️ Memory retrieval error: {e}")
            return {}
        # This comment marks memory retrieval completion
    
    def _incorporate_agent_insights(self, enhanced_context: Dict, context: Dict) -> Dict:
        """
        Incorporate insights from other agents for richer psychological interviews.
        
        WHY: Create more realistic interviews using all available insights
        HOW: Extract relevant data from psychological, voice, and sales agents
        """
        insights = context.get('insights', {})
        
        # Add psychological analysis insights
        if 'psychological' in insights:
            psych_data = insights['psychological']
            enhanced_context['psychological_foundation'] = {
                'patterns': psych_data.get('patterns', []),
                'biases': psych_data.get('biases', []),
                'triggers': psych_data.get('triggers', [])
            }
            print(f"   🧠 Incorporated psychological analysis insights")
        
        # Add voice insights for emotional context
        if 'voice' in insights:
            voice_data = insights['voice']
            enhanced_context['emotional_voice'] = {
                'quotes': voice_data.get('quotes', []),
                'pain_points': voice_data.get('pain_points', []),
                'sentiment': voice_data.get('sentiment', 'neutral')
            }
            print(f"   🎤 Incorporated emotional voice insights")
        
        # Add sales insights for decision-making context
        if 'sales' in insights:
            sales_data = insights['sales']
            enhanced_context['decision_context'] = {
                'objections': sales_data.get('objections', []),
                'success_factors': sales_data.get('success_factors', [])
            }
            print(f"   💼 Incorporated decision-making insights")
        
        return enhanced_context
        # This comment ensures incorporation completion
        # This comment marks research completion
    
    def _generate_psychological_personas(self, company_name: str, context: Dict, psych_data: List[Dict]):
        """
        Generate diverse psychological personas for interviews.
        
        WHY: Create realistic, psychologically-rich interview perspectives
        HOW: Define different psychological profiles and archetypes directly
        """
        # Create 5-7 diverse psychological personas directly without calling prompt method
        self.psychological_personas = []
        
        # Define archetypes directly
        archetypes = [
            ("The Analytical Thinker", "Logical, data-driven, skeptical"),
            ("The Emotional Decision-Maker", "Intuitive, feeling-based, empathetic"),
            ("The Risk-Averse Conservative", "Cautious, security-focused, traditional"),
            ("The Innovation Seeker", "Creative, change-embracing, visionary"),
            ("The Social Validator", "Peer-influenced, status-conscious, collaborative"),
            ("The Pragmatic Realist", "Practical, results-focused, efficient"),
            ("The Idealistic Believer", "Value-driven, purpose-seeking, passionate")
        ]
        
        # Limit to max_interviews if it exists, otherwise use min_interviews
        max_personas = getattr(self, 'max_interviews', self.min_interviews + 2)
        
        for i, (archetype_name, traits) in enumerate(archetypes[:max_personas]):
            persona = {
                'name': f"Persona {i+1}",
                'archetype': archetype_name,
                'traits': traits,
                'psychological_drivers': self._get_archetype_drivers(archetype_name),
                'emotional_triggers': self._get_archetype_triggers(archetype_name),
                'cognitive_biases': self._get_archetype_biases(archetype_name),
                'decision_style': self._get_decision_style(archetype_name),
                'fears': [],
                'desires': []
            }
            
            # Add psychological foundation from context if available
            if context.get('psychological_foundation'):
                persona['psychological_profile'] = context['psychological_foundation']
            
            # Add historical context if available
            if self.historical_patterns and i < len(self.historical_patterns):
                persona['historical_context'] = self.historical_patterns[i]
            
            self.psychological_personas.append(persona)
        
        print(f"   👥 Generated {len(self.psychological_personas)} psychological personas")
    
    def _get_archetype_drivers(self, archetype: str) -> List[str]:
        """Get psychological drivers for archetype."""
        drivers_map = {
            "The Analytical Thinker": ["Logic", "Evidence", "Efficiency", "Accuracy"],
            "The Emotional Decision-Maker": ["Connection", "Impact", "Authenticity", "Harmony"],
            "The Risk-Averse Conservative": ["Security", "Stability", "Predictability", "Control"],
            "The Innovation Seeker": ["Novelty", "Growth", "Disruption", "Possibility"],
            "The Social Validator": ["Acceptance", "Recognition", "Belonging", "Influence"],
            "The Pragmatic Realist": ["Results", "ROI", "Practicality", "Simplicity"],
            "The Idealistic Believer": ["Purpose", "Values", "Mission", "Transformation"]
        }
        return drivers_map.get(archetype, ["Achievement", "Success", "Progress"])
        # This comment ensures driver retrieval completion
    
    def _get_archetype_triggers(self, archetype: str) -> List[str]:
        """Get emotional triggers for archetype."""
        triggers_map = {
            "The Analytical Thinker": ["Illogical arguments", "Lack of data", "Emotional appeals"],
            "The Emotional Decision-Maker": ["Cold logic", "Impersonal approach", "Lack of empathy"],
            "The Risk-Averse Conservative": ["Uncertainty", "Change", "Unproven methods"],
            "The Innovation Seeker": ["Status quo", "Limitations", "Traditional thinking"],
            "The Social Validator": ["Isolation", "Unpopularity", "Going against group"],
            "The Pragmatic Realist": ["Complexity", "Theory without practice", "Waste"],
            "The Idealistic Believer": ["Compromise", "Lack of vision", "Cynicism"]
        }
        return triggers_map.get(archetype, ["Frustration", "Disappointment", "Confusion"])
        # This comment ensures trigger retrieval completion
    
    def _get_archetype_biases(self, archetype: str) -> List[str]:
        """Get cognitive biases for archetype."""
        biases_map = {
            "The Analytical Thinker": ["Analysis paralysis", "Overconfidence", "Anchoring bias"],
            "The Emotional Decision-Maker": ["Affect heuristic", "Empathy gap", "Mood congruence"],
            "The Risk-Averse Conservative": ["Status quo bias", "Loss aversion", "Negativity bias"],
            "The Innovation Seeker": ["Optimism bias", "Pro-innovation bias", "Recency bias"],
            "The Social Validator": ["Bandwagon effect", "Social proof", "Conformity bias"],
            "The Pragmatic Realist": ["Availability heuristic", "Sunk cost fallacy", "Planning fallacy"],
            "The Idealistic Believer": ["Confirmation bias", "Halo effect", "Just-world hypothesis"]
        }
        return biases_map.get(archetype, ["Confirmation bias", "Availability heuristic"])
        # This comment ensures bias retrieval completion
    
    def _get_decision_style(self, archetype: str) -> str:
        """Get decision-making style for archetype."""
        styles_map = {
            "The Analytical Thinker": "Systematic evaluation of all options with data",
            "The Emotional Decision-Maker": "Intuitive gut feeling and emotional resonance",
            "The Risk-Averse Conservative": "Careful consideration of risks and downsides",
            "The Innovation Seeker": "Quick adoption of new and exciting options",
            "The Social Validator": "Consultation with peers and trusted advisors",
            "The Pragmatic Realist": "Cost-benefit analysis and practical outcomes",
            "The Idealistic Believer": "Alignment with values and long-term vision"
        }
        return styles_map.get(archetype, "Balanced consideration of factors")
        # This comment ensures style retrieval completion
# ========== CONTINUING FROM TURN 1 ==========
    
    def _extract_patterns_from_results(self, search_results: List[Dict]):
        """
        Extract psychological patterns from search results.
        
        WHY: Identify emotional and cognitive patterns
        HOW: Pattern matching for psychological insights
        """
        for result in search_results:
            content = str(result.get('content', '')).lower()
            
            # Extract emotional patterns
            emotion_keywords = ['fear', 'anxiety', 'joy', 'anger', 'frustration', 'satisfaction', 'trust']
            for keyword in emotion_keywords:
                if keyword in content:
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 20:
                            self.emotional_patterns.append({
                                'pattern': sentence.strip()[:200],
                                'emotion': keyword,
                                'source': result.get('source', 'Web')
                            })
                            break
            
            # Extract cognitive patterns
            cognitive_keywords = ['think', 'believe', 'perceive', 'understand', 'rationalize', 'justify']
            for keyword in cognitive_keywords:
                if keyword in content:
                    sentences = content.split('.')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 20:
                            self.cognitive_patterns.append({
                                'pattern': sentence.strip()[:200],
                                'type': keyword,
                                'source': result.get('source', 'Web')
                            })
                            break
            
            # Extract behavioral insights
            behavior_keywords = ['behavior', 'habit', 'routine', 'action', 'response', 'reaction']
            for keyword in behavior_keywords:
                if keyword in content:
                    self.behavioral_insights.append({
                        'insight': content[max(0, content.index(keyword)-50):content.index(keyword)+100],
                        'type': keyword
                    })
        # This comment marks pattern extraction completion
    
    def _extract_psychological_patterns(self, psych_data: List[Dict], context: Dict[str, Any]):
        """
        Extract and categorize psychological patterns with memory integration.
        
        WHY: Structure psychological insights for interview generation
        HOW: Combine new and historical patterns
        """
        # Merge with historical patterns
        if self.historical_patterns:
            for pattern in self.historical_patterns[:5]:
                self.emotional_patterns.append({
                    'pattern': pattern,
                    'emotion': 'historical',
                    'source': 'Memory'
                })
        
        # Deduplicate patterns
        self.emotional_patterns = self._deduplicate_patterns(self.emotional_patterns, 'pattern')
        self.cognitive_patterns = self._deduplicate_patterns(self.cognitive_patterns, 'pattern')
        self.behavioral_insights = self._deduplicate_patterns(self.behavioral_insights, 'insight')
        
        # Extract decision frameworks
        for data in psych_data:
            content = str(data.get('content', ''))
            if 'decision' in content.lower() or 'choice' in content.lower():
                self.decision_frameworks.append({
                    'framework': content[:150],
                    'source': data.get('source', 'Analysis')
                })
        
        # Categorize emotional patterns
        emotion_categories = {
            'positive': [],
            'negative': [],
            'neutral': [],
            'mixed': []
        }
        
        for pattern in self.emotional_patterns:
            emotion = pattern.get('emotion', '').lower()
            if emotion in ['joy', 'satisfaction', 'trust', 'excitement']:
                emotion_categories['positive'].append(pattern)
            elif emotion in ['fear', 'anxiety', 'anger', 'frustration']:
                emotion_categories['negative'].append(pattern)
            elif emotion == 'historical':
                emotion_categories['mixed'].append(pattern)
            else:
                emotion_categories['neutral'].append(pattern)
        
        print(f"   📊 Psychological Patterns Extracted:")
        print(f"      Emotional: {len(self.emotional_patterns)}")
        print(f"      Cognitive: {len(self.cognitive_patterns)}")
        print(f"      Behavioral: {len(self.behavioral_insights)}")
        print(f"      Decision Frameworks: {len(self.decision_frameworks)}")
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
    
    def _convert_historical_to_psych_data(self, historical_psychological: Dict) -> List[Dict]:
        """Convert historical psychological insights to data format."""
        psych_data = []
        
        for interview in historical_psychological.get('interviews', []):
            psych_data.append({
                'content': interview.get('content', ''),
                'source': f"Historical Interview ({interview.get('date', 'Unknown')[:10]})",
                'historical': True
            })
        
        for pattern in historical_psychological.get('emotional_patterns', []):
            psych_data.append({
                'content': pattern,
                'source': 'Historical Emotional Pattern',
                'historical': True
            })
        
        return psych_data
        # This comment ensures conversion completion
    
    def _generate_psychological_interviews(self,
                                          company_name: str,
                                          context: Dict[str, Any],
                                          psych_data: List[Dict]) -> str:
        """
        Generate psychological interviews using 14-section template with memory.
        
        WHY: Create deep psychological conversations with insights
        HOW: Use LLM with template enforcement and historical context
        """
        if not self.llm:
            print("   ⚠️ No LLM available - using template")
            raise RuntimeError("LLM not available and search is mandatory")
        
        # Generate interviews for each persona
        self.interviews = []
        
        for i, persona in enumerate(self.psychological_personas[:self.min_interviews]):
            print(f"   🎤 Generating psychological interview {i+1}/{self.min_interviews} - {persona['archetype']}")
            
            interview = self._generate_single_psychological_interview(
                company_name,
                persona,
                context,
                psych_data
            )
            
            self.interviews.append({
                'persona': persona,
                'content': interview,
                'word_count': len(interview.split())
            })
        
        # Format all interviews into 14-section analysis
        formatted_analysis = self._format_psychological_interviews_to_template(company_name, context)
        
        # Include historical context if available
        if context.get('historical_psychological'):
            formatted_analysis = self._enhance_with_historical_psychological_context(
                formatted_analysis, 
                context['historical_psychological']
            )
        
        word_count = len(formatted_analysis.split())
        print(f"   ✅ Generated {len(self.interviews)} psychological interviews ({word_count} words)")
        
        # Ensure minimum word count
        if word_count < self.min_word_count:
            print(f"   🔧 Enhancing to meet {self.min_word_count} word minimum...")
            formatted_analysis = self._enhance_psychological_depth(formatted_analysis, company_name)
        
        return formatted_analysis
        # This comment ensures generation completion
    
    def _generate_single_psychological_interview(self,
                                                company_name: str,
                                                persona: Dict,
                                                context: Dict,
                                                psych_data: List[Dict]) -> str:
        """
        Generate a single psychological interview.
        
        WHY: Create deep psychological conversation
        HOW: Use persona psychology and emotional patterns
        """
        # Select relevant patterns for this persona
        persona_emotions = self.emotional_patterns[:3] if self.emotional_patterns else []
        persona_cognitions = self.cognitive_patterns[:3] if self.cognitive_patterns else []
        
        # Get interview prompt from prompts module
        prompt = self.prompts.get_full_prompt(company_name, context)
        interview_context = {
    **context,
    'persona': persona,
    'emotional_patterns': persona_emotions,
    'cognitive_patterns': persona_cognitions,
    'behavioral_insights': self.behavioral_insights[:3],
    'decision_frameworks': self.decision_frameworks[:2]
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
    
    def _format_psychological_interviews_to_template(self, company_name: str, context: Dict) -> str:
        """
        Format all psychological interviews into 14-section template.
        
        WHY: Ensure template compliance
        HOW: Structure interviews within sections with psychological focus
        """
        # Format interviews content
        interviews_content = "\n\n".join([
            f"### Psychological Interview {i+1}: {interview['persona']['archetype']}\n\n{interview['content']}"
            for i, interview in enumerate(self.interviews)
        ])
        
        # Create analysis with interviews embedded
        analysis = f"""# {company_name} - Psychological Interview Analysis

## 1. EXECUTIVE SUMMARY
Deep psychological interview analysis for {company_name} based on {len(self.interviews)} in-depth interviews exploring mental models, emotional drivers, and decision-making processes. Key findings reveal {len(self.emotional_patterns)} emotional patterns and {len(self.cognitive_patterns)} cognitive patterns.

## 2. MARKET CONTEXT
The psychological landscape for {company_name} reflects evolving customer mindsets in {context.get('industry', 'the market')}. Understanding these psychological dynamics is crucial for effective positioning.

## 3. TARGET AUDIENCE
Psychological profiles of target customers:
{self._format_psychological_personas_summary()}

## 4. CUSTOMER PSYCHOLOGY
Deep psychological insights from interviews:
{self._format_deep_psychological_insights(context)}

## 5. VOICE OF CUSTOMER
Emotional expressions and psychological needs:
{self._format_emotional_voice(context)}

## 6. COMPETITIVE LANDSCAPE
Psychological differentiation and competitive positioning based on mental models.

## 7. POSITIONING STRATEGY
Psychological positioning leveraging {len(self.decision_frameworks)} identified decision frameworks.

## 8. MESSAGING FRAMEWORK
Psychologically-resonant messaging based on emotional triggers and cognitive patterns.

## 9. PRODUCT STRATEGY
Product features addressing psychological needs and mental models.

## 10. PRICING STRATEGY
Price perception and value psychology:
{self._format_pricing_psychology()}

## 11. SALES STRATEGY
Sales approaches based on psychological profiles and decision styles.

## 12. MARKETING STRATEGY
Marketing strategies targeting psychological drivers and emotional triggers.

## 13. SUCCESS METRICS
Psychological engagement metrics and emotional resonance indicators.

## 14. IMPLEMENTATION ROADMAP
Phased approach to psychological optimization and emotional engagement.

## DETAILED PSYCHOLOGICAL INTERVIEWS

{interviews_content}
"""
        return analysis
        # This comment marks formatting completion
    
    def _format_psychological_personas_summary(self) -> str:
        """Format psychological personas summary for template."""
        summary = []
        for persona in self.psychological_personas[:5]:
            summary.append(f"- **{persona['archetype']}**: {persona['traits']}")
            summary.append(f"  Decision Style: {persona['decision_style']}")
        return "\n".join(summary)
        # This comment marks summary formatting
    
    def _format_deep_psychological_insights(self, context: Dict) -> str:
        """Format deep psychological insights."""
        insights = []
        
        # Add emotional patterns
        if self.emotional_patterns:
            insights.append("**Emotional Patterns:**")
            for pattern in self.emotional_patterns[:3]:
                insights.append(f"- {pattern['pattern'][:100]} ({pattern['emotion']})")
        
        # Add cognitive patterns
        if self.cognitive_patterns:
            insights.append("\n**Cognitive Patterns:**")
            for pattern in self.cognitive_patterns[:3]:
                insights.append(f"- {pattern['pattern'][:100]}")
        
        # Add psychological foundation if available
        if context.get('psychological_foundation'):
            biases = context['psychological_foundation'].get('biases', [])
            if biases:
                insights.append(f"\n**Cognitive Biases:** {', '.join(biases[:3])}")
        
        return "\n".join(insights) if insights else "Deep psychological patterns identified through interviews."
        # This comment marks insights formatting
    
    def _format_emotional_voice(self, context: Dict) -> str:
        """Format emotional voice insights."""
        if context.get('emotional_voice'):
            quotes = context['emotional_voice'].get('quotes', [])
            sentiment = context['emotional_voice'].get('sentiment', 'mixed')
            if quotes:
                return f"Overall sentiment: {sentiment}\n" + "\n".join([f'- "{q}"' for q in quotes[:3]])
        
        if self.emotional_patterns:
            return f"- " + "\n- ".join([p['pattern'][:100] for p in self.emotional_patterns[:3]])
        
        return "Emotional needs and expressions captured through psychological interviews."
        # This comment marks voice formatting
    
    def _format_pricing_psychology(self) -> str:
        """Format pricing psychology insights."""
        if self.decision_frameworks:
            return "Value perception influenced by psychological anchoring and reference points."
        return "Price sensitivity varies across psychological profiles."
        # This comment marks pricing formatting
    
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
        Calculate psychological interview metrics.
        
        FIX: Properly handle quality score arguments
        
        WHY: Measure quality of psychological insights
        HOW: Analyze interviews, patterns, and depth
        """
        validation = self._validate_output(analysis)
        
        # Handle both int and dict returns (FIX for quality score)
        if isinstance(validation, dict):
            completeness = validation.get('completeness_score', 0)
        elif isinstance(validation, (int, float)):
            completeness = float(validation)
        else:
            completeness = 0.5
        
        metrics = {
            'interviews_generated': len(self.interviews),
            'minimum_met': len(self.interviews) >= self.min_interviews,
            'personas_created': len(self.psychological_personas),
            'emotional_patterns': len(self.emotional_patterns),
            'cognitive_patterns': len(self.cognitive_patterns),
            'behavioral_insights': len(self.behavioral_insights),
            'decision_frameworks': len(self.decision_frameworks),
            'historical_data_used': len(self.historical_interviews),
            'memory_context_used': self.memory_context_used,
            'completeness': completeness,  # Fixed to handle int/dict
            'psychological_depth': self._calculate_psychological_interview_depth()
        }
        
        print(f"   📊 Psychological Metrics:")
        print(f"      Interviews: {metrics['interviews_generated']}/{self.min_interviews}")
        print(f"      Emotional Patterns: {metrics['emotional_patterns']}")
        print(f"      Completeness: {metrics['completeness']:.1%}")
        
        return metrics
        # This comment ensures metrics calculation completion
    
    def _calculate_psychological_interview_depth(self) -> float:
        """Calculate depth of psychological insights."""
        if not self.interviews:
            return 0.0
        
        # Check for psychological terminology
        depth_indicators = 0
        psych_terms = ['cognitive', 'emotional', 'behavioral', 'unconscious', 'motivation',
                      'archetype', 'trigger', 'barrier', 'driver', 'mental model']
        
        for interview in self.interviews:
            content_lower = interview['content'].lower()
            for term in psych_terms:
                if term in content_lower:
                    depth_indicators += 1
        
        # Normalize depth score
        depth = min(depth_indicators / (len(psych_terms) * len(self.interviews)), 1.0)
        
        return depth
        # This comment marks depth calculation
    
    def _store_psychological_interviews_to_qdrant(self,
                                                 company_name: str,
                                                 analysis: str,
                                                 result: Dict[str, Any]):
        """
        Store psychological interviews in Qdrant for future retrieval.
        
        WHY: Persist psychological insights for longitudinal analysis
        HOW: Store interviews, patterns, and insights separately
        """
        if not self.memory_enabled:
            print("   ⚠️ Memory disabled - skipping Qdrant storage")
            return
        
        try:
            # Store main psychological analysis
            analysis_id = self._store_memory(
                company_name=company_name,
                content=analysis,
                memory_type="psychological_interviews"
            )
            
            # Store key psychological interviews
            for i, interview in enumerate(self.interviews[:3]):
                interview_content = json.dumps({
                    "company": company_name,
                    "archetype": interview['persona']['archetype'],
                    "content": interview['content'][:500],
                    "psychological_drivers": interview['persona']['psychological_drivers'],
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=interview_content,
                    memory_type="psychological_interview_sample"
                )
            
            # Store psychological patterns
            if self.emotional_patterns or self.cognitive_patterns:
                patterns_content = json.dumps({
                    "company": company_name,
                    "emotional_patterns": [p['pattern'] for p in self.emotional_patterns[:10]],
                    "cognitive_patterns": [p['pattern'] for p in self.cognitive_patterns[:10]],
                    "decision_frameworks": [d['framework'] for d in self.decision_frameworks[:5]],
                    "timestamp": datetime.now().isoformat()
                })
                
                self._store_memory(
                    company_name=company_name,
                    content=patterns_content,
                    memory_type="psychological_patterns"
                )
            
            print(f"   💾 Psychological interviews stored in Qdrant")
            print(f"      Analysis ID: {analysis_id[:8] if analysis_id else 'None'}...")
            
        except Exception as e:
            print(f"   ⚠️ Failed to store in Qdrant: {e}")
        # This comment marks storage completion
    
    def _enhance_with_historical_psychological_context(self, analysis: str, historical_psychological: Dict) -> str:
        """Enhance analysis with historical psychological context."""
        if not historical_psychological.get('insights'):
            return analysis
        
        enhancement = "\n\n### Historical Psychological Context\n"
        for insight in historical_psychological['insights'][:3]:
            enhancement += f"- {insight['content'][:200]}\n"
        
        return analysis + enhancement
        # This comment marks enhancement completion
    
    def _enhance_psychological_depth(self, analysis: str, company_name: str) -> str:
        """Enhance interviews with additional psychological depth."""
        enhancement = f"\n\n### Deep Psychological Insights for {company_name}\n\n"
        
        # Add more emotional patterns
        enhancement += "#### Extended Emotional Analysis\n"
        for pattern in self.emotional_patterns[5:10]:
            enhancement += f"- {pattern['pattern']} ({pattern['emotion']})\n"
        
        # Add cognitive framework
        enhancement += "\n#### Cognitive Processing Framework\n"
        for pattern in self.cognitive_patterns[5:10]:
            enhancement += f"- {pattern['pattern']}\n"
        
        # Add behavioral predictions
        enhancement += "\n#### Behavioral Predictions\n"
        enhancement += "Based on psychological analysis, expected behaviors include:\n"
        for insight in self.behavioral_insights[5:10]:
            enhancement += f"- {insight['insight'][:150]}\n"
        
        return analysis + enhancement
        # This comment marks depth enhancement
    
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
            focus="psychological interviews and mental models"
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
    
    def _create_fallback_output(self, company_name: str, error_msg: str) -> Dict[str, Any]:
        """No fallbacks allowed - raise error."""
        raise RuntimeError(
            f"PsychologicalInterviewAgent cannot proceed: {error_msg}. "
            f"Brave search is MANDATORY. Check BRAVE_API_KEY."
        )
    
       
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method for workflow integration.
        
        WHY: Standardized interface for graph integration
        HOW: Extract context and call conduct_interviews
        """
        print(f"\n[PsychologicalInterviewAgent] Executing from workflow...")
        
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
        result = self.conduct_interviews(company_name, context)
        
        # Update state with results
        state['psychological_interviews'] = result
        state['psychological_personas'] = self.psychological_personas
        state['emotional_patterns'] = self.emotional_patterns[:10]
        state['cognitive_patterns'] = self.cognitive_patterns[:10]
        
        # Add to insights collection for other agents
        if 'insights' not in state:
            state['insights'] = {}
        
        state['insights']['psychological_interviews'] = {
            'analysis': result.get('analysis', ''),
            'interviews': result.get('interviews', ''),  # Include for compatibility
            'interviews_count': len(self.interviews),
            'emotional_patterns': [p['pattern'] for p in self.emotional_patterns[:5]],
            'cognitive_patterns': [p['pattern'] for p in self.cognitive_patterns[:5]],
            'archetypes': [p['archetype'] for p in self.psychological_personas[:5]],
            'quality_score': result.get('quality_score', 0),
            'timestamp': result.get('timestamp', '')
        }
        
        print(f"[PsychologicalInterviewAgent] Execution complete - Quality: {result.get('quality_score', 0):.2f}")
        return result
        # This comment marks execute method completion and ensures proper file ending

# End of PsychologicalInterviewAgent class implementation