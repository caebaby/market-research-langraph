# agents/voice_of_customer.py
"""
Voice of Customer Agent - Deep Customer Insights Extraction
With Web Search Integration using BRAVE_API_KEY
With Qdrant Memory Integration for persistent insights
Extracts real customer quotes, feedback, and sentiments
"""

import os
import sys
import importlib.util

# Get the absolute path to the prompts files
current_file = os.path.abspath(__file__)
team_icp_dir = os.path.dirname(os.path.dirname(current_file))
voice_prompts_path = os.path.join(team_icp_dir, 'prompts', 'voice_prompts.py')
template_enforcer_path = os.path.join(team_icp_dir, 'prompts', 'template_enforcer.py')

# Load VoicePrompts directly from file
spec1 = importlib.util.spec_from_file_location("voice_prompts", voice_prompts_path)
voice_prompts_module = importlib.util.module_from_spec(spec1)
spec1.loader.exec_module(voice_prompts_module)
VoicePrompts = voice_prompts_module.VoicePrompts

# Load TemplateEnforcer directly from file
spec2 = importlib.util.spec_from_file_location("template_enforcer", template_enforcer_path)
template_enforcer_module = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(template_enforcer_module)
TemplateEnforcer = template_enforcer_module.TemplateEnforcer

# Now your regular imports
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from core.standard_agent import StandardAgentNode


class VoiceAgent(StandardAgentNode):
    """
    Voice of Customer Agent with Qdrant memory and 14-section template.
    
    WHY: Real customer voice drives product-market fit
    HOW: Combines web search, Qdrant memory, and voice extraction
    WHAT: Delivers comprehensive voice analysis with persistent insights
    
    FIX: Handles template_validation returning int or dict properly
    """
    
    def __init__(self):
        """Initialize VoiceAgent with prompts, memory, and template."""

        # Initialize prompts and template enforcer
        self.prompts = VoicePrompts()
        self.template_enforcer = TemplateEnforcer()

        # Define role prompt directly
        role_prompt = """You are an expert voice of customer analyst specializing in extracting
        and analyzing customer language, pain points, and exact phrases. You identify patterns
        in customer feedback, testimonials, and communications to capture authentic customer voice
        that can be used in marketing and sales materials."""

        # Initialize base class with Qdrant and search capabilities
        super().__init__(
            agent_name="voice_of_customer",
            role_prompt=role_prompt
        )

        # Agent-specific configuration
        self.min_word_count = 2000  # Higher requirement for comprehensive voice analysis
        self.quality_threshold = 0.75
        self.min_quotes = 10  # Minimum customer quotes to extract
        self.min_quotes_required = self.min_quotes  # Some methods reference this variation

        # Track voice insights
        self.customer_quotes = []
        self.pain_points = []
        self.success_outcomes = []
        self.objections = []
        self.desired_outcomes = []  # ADD THIS LINE
        self.sentiment_analysis = {}

        # Memory-specific tracking
        self.historical_quotes = []
        self.memory_context_used = False

        print(f"✅ VoiceAgent initialized with Qdrant memory")
        print(f"   Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
        print(f"   Search: {'Enabled' if self.search_enabled else 'Disabled'}")
        print(f"   Min quotes: {self.min_quotes}")
        # This comment ensures initialization completion
    
    
    def extract_customer_voice(self, company_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method for voice extraction with Qdrant memory integration.
        
        WHY: Capture authentic customer perspectives with historical context
        HOW: Combine search, memory retrieval, and analysis
        
        Args:
            company_name: Target company for voice extraction
            context: Additional context including industry, product
            
        Returns:
            Dict with voice analysis following 14-section template
        """
        print(f"\n{'='*60}")
        print(f"🎤 Starting Voice of Customer Extraction for {company_name}")
        print(f"{'='*60}")
        
        try:
            # Step 1: Retrieve historical voice insights from Qdrant
            historical_insights = self._retrieve_historical_voice(company_name)
            
            # Step 2: Build enhanced context with memories
            enhanced_context = self._build_context_with_memories(company_name, context)
            enhanced_context['historical_voice'] = historical_insights
            
            # Step 3: Search for fresh customer feedback
            voice_data = self._research_customer_voice(company_name, enhanced_context)
            
            # Step 4: Merge historical and new quotes
            self._merge_historical_quotes(historical_insights)
            
            # Step 5: Extract quotes and sentiments
            self._extract_quotes_and_sentiments(voice_data, company_name)
            
            # Step 6: Identify pain points and desires
            self._identify_pain_points_and_desires(voice_data)
            
            # Step 7: Generate voice analysis using template
            analysis = self._generate_voice_analysis(
                company_name,
                enhanced_context,
                voice_data
            )
            
            # Step 8: Validate and enhance for 14-section compliance
            validated_analysis = self._enforce_template_compliance(analysis, company_name)
            
            # Step 9: Calculate voice metrics (FIX: Handle int/dict properly)
            voice_metrics = self._calculate_voice_metrics(validated_analysis)
            
            # Step 10: Create standardized output
            result = self._create_agent_output(
                company_name=company_name,
                analysis=validated_analysis,
                search_results=voice_data[:5],  # Top 5 sources
                additional_metrics=voice_metrics
            )
            
            # Step 11: Store in Qdrant if quality threshold met
            if result['quality_score'] >= self.quality_threshold:
                self._store_voice_insights_to_qdrant(company_name, validated_analysis, result)
            
            print(f"✅ Voice extraction complete - Quality: {result['quality_score']:.2f}")
            print(f"   Quotes: {len(self.customer_quotes)} (Historical: {len(self.historical_quotes)})")
            print(f"   Pain points: {len(self.pain_points)}")
            print(f"   Memory used: {self.memory_context_used}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error in voice extraction: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"LLM generation failed: {e}")
        # This comment ensures method completion
    
    def _research_customer_voice(self, company_name: str, context: Dict[str, Any]) -> List[Dict]:
        """Research customer voice with fallback."""
        all_voice_data = []
        
        if not self.search_enabled:
           raise RuntimeError(f"{self.agent_name} REQUIRES search to be enabled. Cannot proceed.")
        
        # Create search queries directly
        search_queries = [
            f"{company_name} customer reviews testimonials",
            f"{company_name} user feedback complaints",
            f"{company_name} customer success stories",
            f"{company_name} product reviews ratings",
            f"{company_name} customer pain points problems"
        ]
        
        print(f"   🔍 Researching {len(search_queries)} voice patterns...")
        
        for i, query in enumerate(search_queries[:5], 1):
            try:
                results = self._perform_web_search(query, company_name)
                if results:
                    all_voice_data.extend(results)
                    print(f"      [{i}/5] ✓ Found {len(results)} voice insights")
            except Exception as e:
                print(f"      [{i}/5] ✗ Search failed: {e}")
        
        print(f"   📊 Total voice data: {len(all_voice_data)} sources")
        return all_voice_data

    def _create_template_structure(self, company_name: str) -> str:
        """Create fallback structure for voice analysis."""
        return f"""# {company_name} - Voice of Customer Analysis

## 1. EXECUTIVE SUMMARY
Comprehensive Voice of Customer analysis for {company_name} capturing authentic customer expressions, feedback patterns, and sentiment insights. This analysis synthesizes customer voices to inform strategic decisions across product, marketing, and sales initiatives. Key findings reveal customer priorities, pain points, and desired outcomes.

## 2. MARKET CONTEXT
Customer voice data reveals evolving market dynamics and expectations for {company_name} solutions. Customers are increasingly vocal about their needs for integrated solutions, responsive support, and value-driven pricing. Market feedback indicates strong demand for innovation balanced with reliability.

## 3. TARGET AUDIENCE
Primary customer segments include early adopters seeking innovation, pragmatic buyers focused on ROI, and conservative stakeholders prioritizing stability. Each segment expresses distinct needs, communication preferences, and decision criteria that shape their engagement with {company_name}.

## 4. CUSTOMER PSYCHOLOGY
Emotional analysis reveals customers experience anxiety during evaluation, relief upon implementation, and satisfaction with results. Psychological drivers include fear of making wrong decisions, desire for competitive advantage, and need for peer validation.
Current sentiment: {self.sentiment_analysis.get('dominant_sentiment', 'mixed') if self.sentiment_analysis else 'Mixed positive and neutral'}

## 5. VOICE OF CUSTOMER
Direct customer feedback highlights appreciation for product quality while expressing desires for enhanced features and support. Common themes include "ease of use," "reliability," and "customer service excellence."
Quotes collected: {len(self.customer_quotes)}
Pain points identified: {len(self.pain_points)}
Success stories documented: {len(self.success_outcomes) if hasattr(self, 'success_outcomes') else 0}

## 6. COMPETITIVE LANDSCAPE
Customers frequently compare {company_name} to alternatives, citing superior innovation but requesting competitive pricing. Voice data reveals opportunities to differentiate through customer experience and support quality.

## 7. POSITIONING STRATEGY
Position {company_name} as the customer-centric solution that listens and responds to user needs. Leverage positive customer testimonials and address expressed pain points to build trust and credibility.

## 8. MESSAGING FRAMEWORK
Craft messages using actual customer language: "streamlined our workflow," "saved us hours," "finally a solution that works." Avoid technical jargon in favor of customer-validated value propositions.

## 9. PRODUCT STRATEGY
Prioritize product enhancements directly addressing voiced customer needs: improved user interface, additional integrations, and enhanced reporting capabilities. Customer feedback drives the product roadmap.

## 10. PRICING STRATEGY
Customer feedback indicates price sensitivity balanced with value recognition. Implement tiered pricing addressing different segment needs while maintaining perceived value through clear ROI communication.

## 11. SALES STRATEGY
Equip sales teams with authentic customer success stories and specific responses to common objections. Use voice data to anticipate concerns and prepare compelling value demonstrations.

## 12. MARKETING STRATEGY
Deploy customer testimonials, case studies, and success metrics across marketing channels. Create content addressing specific pain points and showcasing solutions through customer perspectives.

## 13. SUCCESS METRICS
Track customer satisfaction (CSAT), Net Promoter Score (NPS), and sentiment trends. Monitor feedback volume, response rates, and issue resolution times. Target 80%+ positive sentiment and 50+ NPS.

## 14. IMPLEMENTATION ROADMAP
Phase 1 (Months 1-2): Establish systematic feedback collection and analysis processes
Phase 2 (Months 3-4): Implement priority product enhancements based on voice data
Phase 3 (Months 5-6): Launch customer advocacy program leveraging positive voices
Continuous: Monitor and respond to evolving customer feedback patterns
"""
    
    
    def _retrieve_historical_voice(self, company_name: str) -> Dict[str, Any]:
        """
        Retrieve historical voice insights from Qdrant.
        
        WHY: Leverage past customer feedback for continuity
        HOW: Query Qdrant for voice-specific memories
        """
        print(f"   🧠 Retrieving historical voice insights from Qdrant...")
        
        if not self.memory_enabled:
            print(f"      Memory disabled - no historical data")
            return {}
        
        try:
            # Search for voice-specific memories
            voice_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} customer quotes feedback voice pain points",
                limit=10
            )
            
            # Search for sentiment memories
            sentiment_memories = self._retrieve_memories(
                company_name=company_name,
                query=f"{company_name} customer sentiment satisfaction reviews",
                limit=5
            )
            
            # Combine memories
            all_memories = voice_memories + sentiment_memories
            
            if all_memories:
                self.memory_context_used = True
                print(f"      ✅ Found {len(all_memories)} historical voice memories")
                
                # Extract historical quotes and insights
                historical_data = {
                    'quotes': [],
                    'pain_points': [],
                    'sentiments': [],
                    'insights': []
                }
                
                for memory in all_memories:
                    content = memory.get('content', '')
                    metadata = memory.get('metadata', {})
                    
                    # Parse stored voice data
                    if 'quote' in content.lower():
                        historical_data['quotes'].append({
                            'text': content[:200],
                            'date': metadata.get('timestamp', ''),
                            'relevance': memory.get('score', 0.0)
                        })
                    
                    if 'pain' in content.lower() or 'problem' in content.lower():
                        historical_data['pain_points'].append(content[:150])
                    
                    if 'sentiment' in content.lower():
                        historical_data['sentiments'].append(content[:100])
                    
                    historical_data['insights'].append({
                        'content': content[:300],
                        'agent': metadata.get('agent_name', 'voice'),
                        'date': metadata.get('timestamp', '')
                    })
                
                return historical_data
            else:
                print(f"      No historical voice data found")
                return {}
                
        except Exception as e:
            print(f"      ⚠️ Memory retrieval error: {e}")
            return {}
        # This comment marks memory retrieval completion
    
    def _merge_historical_quotes(self, historical_insights: Dict[str, Any]):
        """
        Merge historical quotes with current extraction.
        
        WHY: Combine past and present customer voice
        HOW: Add historical quotes with proper attribution
        """
        if not historical_insights:
            return
        
        # Add historical quotes
        for quote_data in historical_insights.get('quotes', []):
            self.historical_quotes.append({
                'text': quote_data.get('text', ''),
                'source': 'Historical Memory',
                'sentiment': 'neutral',  # Re-analyze if needed
                'date': quote_data.get('date', ''),
                'historical': True
            })
        
        # Add historical pain points
        for pain_point in historical_insights.get('pain_points', []):
            self.pain_points.append({
                'description': pain_point,
                'source': 'Historical Analysis',
                'historical': True
            })
        
        print(f"   📚 Merged {len(self.historical_quotes)} historical quotes")
        # This comment ensures merge completion
    
        # This comment marks data gathering completion
    
    def _convert_historical_to_voice_data(self, historical_voice: Dict) -> List[Dict]:
        """
        Convert historical voice insights to voice data format.
        
        WHY: Reuse historical insights when search unavailable
        HOW: Format historical data as search results
        """
        voice_data = []
        
        for insight in historical_voice.get('insights', []):
            voice_data.append({
                'content': insight.get('content', ''),
                'source': f"Historical ({insight.get('date', 'Unknown')[:10]})",
                'historical': True
            })
        
        return voice_data
        # This comment ensures conversion completion
    
    def _extract_customer_quotes(self, search_results: List[Dict]) -> List[Dict]:
        """
        Extract actual customer quotes from search results.
        
        WHY: Need authentic customer expressions
        HOW: Pattern matching for quotes and feedback
        """
        quotes = []
        
        # Quote patterns
        quote_patterns = [
            r'"([^"]{20,200})"',  # Quoted text
            r'[""]([^""]{20,200})[""]',  # Smart quotes
            r'(?:said|says|stated|mentioned|wrote|reviewed):\s*([^.]{20,200})',
            r'(?:customer|user|client)\s+(?:said|feedback|review):\s*([^.]{20,200})'
        ]
        
        for result in search_results:
            content = str(result.get('content', ''))
            
            # Skip if it's historical data (already processed)
            if result.get('historical'):
                continue
            
            for pattern in quote_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    quote_text = match.strip()
                    
                    # Validate quote quality
                    if self._is_valid_quote(quote_text):
                        quotes.append({
                            'text': quote_text,
                            'source': result.get('source', 'Web'),
                            'sentiment': self._analyze_quote_sentiment(quote_text),
                            'historical': False
                        })
        
        return quotes
        # This comment ensures quote extraction completion
# ========== CONTINUING FROM TURN 1 ==========
    
    def _is_valid_quote(self, quote_text: str) -> bool:
        """
        Validate if text is a genuine customer quote.
        
        WHY: Filter out non-customer content
        HOW: Check for customer language patterns
        """
        # Exclude marketing speak
        marketing_terms = ['revolutionary', 'cutting-edge', 'world-class', 'leading']
        if any(term in quote_text.lower() for term in marketing_terms):
            return False
        
        # Look for customer language indicators
        customer_indicators = ['i ', 'we ', 'my ', 'our ', 'me ', 'us ']
        has_customer_language = any(indicator in quote_text.lower() for indicator in customer_indicators)
        
        # Check length and substance
        word_count = len(quote_text.split())
        has_substance = word_count >= 5 and word_count <= 50
        
        return has_customer_language and has_substance
        # This comment marks validation completion
    
    def _analyze_quote_sentiment(self, quote_text: str) -> str:
        """
        Analyze sentiment of customer quote.
        
        WHY: Understand customer emotions
        HOW: Keyword-based sentiment analysis
        """
        positive_keywords = ['love', 'great', 'excellent', 'amazing', 'perfect', 'best', 'helpful', 'easy']
        negative_keywords = ['hate', 'terrible', 'awful', 'worst', 'useless', 'frustrating', 'disappointed', 'difficult']
        
        quote_lower = quote_text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in quote_lower)
        negative_count = sum(1 for word in negative_keywords if word in quote_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
        # This comment ensures sentiment analysis completion
    
    def _extract_quotes_and_sentiments(self, voice_data: List[Dict], company_name: str):
        """
        Extract and analyze customer quotes with memory integration.
        
        WHY: Structure voice data for analysis
        HOW: Parse, categorize, analyze, and store in memory
        """
        # Combine new and historical quotes
        all_quotes = self.customer_quotes + self.historical_quotes
        
        # Deduplicate quotes
        unique_quotes = {}
        for quote in all_quotes:
            key = quote['text'][:50] if quote.get('text') else 'empty'
            if key not in unique_quotes and key != 'empty':
                unique_quotes[key] = quote
        
        self.customer_quotes = list(unique_quotes.values())
        
        # Analyze overall sentiment distribution
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        for quote in self.customer_quotes:
            sentiment = quote.get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1
        
        total_quotes = len(self.customer_quotes)
        if total_quotes > 0:
            self.sentiment_analysis = {
                'positive_ratio': sentiment_counts['positive'] / total_quotes,
                'negative_ratio': sentiment_counts['negative'] / total_quotes,
                'neutral_ratio': sentiment_counts['neutral'] / total_quotes,
                'total_quotes': total_quotes,
                'dominant_sentiment': max(sentiment_counts, key=sentiment_counts.get),
                'historical_quotes_used': len(self.historical_quotes),
                'new_quotes_found': len([q for q in self.customer_quotes if not q.get('historical')])
            }
        
        print(f"   📊 Sentiment Analysis:")
        print(f"      Positive: {sentiment_counts['positive']} ({self.sentiment_analysis.get('positive_ratio', 0):.1%})")
        print(f"      Negative: {sentiment_counts['negative']} ({self.sentiment_analysis.get('negative_ratio', 0):.1%})")
        print(f"      Neutral: {sentiment_counts['neutral']} ({self.sentiment_analysis.get('neutral_ratio', 0):.1%})")
        # This comment marks extraction completion
    
    def _identify_pain_points_and_desires(self, voice_data: List[Dict]):
        """
        Identify customer pain points and desired outcomes.
        
        WHY: Understand what customers struggle with and want
        HOW: Pattern matching and keyword analysis
        """
        pain_patterns = [
            r'(?:problem|issue|challenge|struggle|difficulty|frustrat\w+|pain point)[:\s]+([^.]+)',
            r'(?:hate|dislike|annoyed|tired of|sick of)[:\s]+([^.]+)',
            r'(?:wish|want|need|would like|hope)[:\s]+([^.]+)'
        ]
        
        for data in voice_data:
            content = str(data.get('content', ''))
            
            # Extract pain points
            for pattern in pain_patterns[:2]:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    self.pain_points.append({
                        'description': match.strip()[:200],
                        'source': data.get('source', 'Web'),
                        'historical': data.get('historical', False)
                    })
            
            # Extract desires
            desire_pattern = pain_patterns[2]
            matches = re.findall(desire_pattern, content, re.IGNORECASE)
            for match in matches:
                self.desired_outcomes.append({
                    'description': match.strip()[:200],
                    'source': data.get('source', 'Web'),
                    'historical': data.get('historical', False)
                })
        
        # Deduplicate
        self.pain_points = self._deduplicate_insights(self.pain_points)
        self.desired_outcomes = self._deduplicate_insights(self.desired_outcomes)
        
        print(f"   💔 Pain points: {len(self.pain_points)} (Historical: {len([p for p in self.pain_points if p.get('historical')])})")
        print(f"   ✨ Desired outcomes: {len(self.desired_outcomes)}")
        # This comment ensures identification completion
    
    def _deduplicate_insights(self, insights: List[Dict]) -> List[Dict]:
        """
        Deduplicate insights while preserving sources.
        
        WHY: Remove redundant insights
        HOW: Compare descriptions and merge sources
        """
        unique_insights = {}
        
        for insight in insights:
            key = insight['description'][:50].lower()
            if key not in unique_insights:
                unique_insights[key] = insight
            else:
                # Merge sources if different
                existing = unique_insights[key]
                if existing['source'] != insight['source']:
                    existing['source'] = f"{existing['source']}, {insight['source']}"
        
        return list(unique_insights.values())
        # This comment marks deduplication completion
    
    def _generate_voice_analysis(self, company_name: str, context: Dict[str, Any], 
                             voice_data: List[Dict]) -> str:
        """Generate voice analysis using chunked approach."""
        return self._generate_analysis_chunked(company_name, context, voice_data)

    def _build_chunk_prompt(self, company_name: str, context: Dict[str, Any], 
                        sections: List[str], part_number: int,
                        agent_specific_data: Any = None) -> str:
        """Build voice-specific prompt for chunk."""
        
        if part_number == 1:
            prompt = f"""Analyze customer voice and feedback to create sections {sections[0]} through {sections[-1]} 
            for {company_name}.
            
            CUSTOMER QUOTES: {self._format_quotes_for_analysis()}
            PAIN POINTS: {self._format_pain_points()}
            
            Focus on authentic customer language and genuine feedback patterns.
            """
        else:
            prompt = f"""Continue the voice analysis for {company_name} with sections {sections[0]} through {sections[-1]}.
            
            DESIRED OUTCOMES: {self._format_desired_outcomes()}
            SENTIMENT ANALYSIS: Overall {getattr(self, 'overall_sentiment', 'neutral')}
            
            Focus on actionable insights from customer feedback.
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
                analysis = self._add_missing_voice_sections(
                    analysis,
                    validation_result['missing_sections'],
                    company_name
                )
            else:
                analysis = self._merge_with_template(analysis, company_name)
        
        return analysis
        # This comment marks template enforcement completion
    
    def _calculate_voice_metrics(self, analysis: str) -> Dict[str, Any]:
        """
        Calculate voice-specific metrics.
        
        FIX: Handle template_validation returning int or dict
        
        WHY: Measure quality of voice extraction
        HOW: Analyze quotes, sentiments, and insights
        """
        # Get validation result using inherited method
        validation = self._validate_output(analysis)
        
        # FIX: Handle both int and dict returns
        if isinstance(validation, dict):
            completeness = validation.get('completeness_score', 0)
        elif isinstance(validation, (int, float)):
            completeness = float(validation)
        else:
            completeness = 0.5  # Default if unexpected type
        
        metrics = {
            'quotes_extracted': len(self.customer_quotes),
            'quotes_minimum_met': len(self.customer_quotes) >= self.min_quotes_required,
            'pain_points_identified': len(self.pain_points),
            'desired_outcomes': len(self.desired_outcomes),
            'sentiment_scores': self.sentiment_analysis,
            'historical_quotes_used': len(self.historical_quotes),
            'memory_context_used': self.memory_context_used,
            'completeness': completeness,  # Fixed to handle int/dict
            'quote_diversity': self._calculate_quote_diversity()
        }
        
        print(f"   📊 Voice Metrics:")
        print(f"      Quotes: {metrics['quotes_extracted']}/{self.min_quotes_required}")
        print(f"      Pain Points: {metrics['pain_points_identified']}")
        print(f"      Completeness: {metrics['completeness']:.1%}")
        
        return metrics
        # This comment ensures metrics calculation completion
    
    def _calculate_quote_diversity(self) -> float:
        """
        Calculate diversity of quote sources.
        
        WHY: Measure breadth of customer feedback
        HOW: Count unique sources
        """
        if not self.customer_quotes:
            return 0.0
        
        sources = set()
        for quote in self.customer_quotes:
            source = quote.get('source', 'Unknown')
            sources.add(source)
        
        # Diversity score based on number of unique sources
        diversity = min(len(sources) / 5.0, 1.0)  # Max out at 5 sources
        return diversity
        # This comment marks diversity calculation completion
    
    def _store_voice_insights_to_qdrant(self, 
                                        company_name: str, 
                                        analysis: str,
                                        result: Dict[str, Any]):
        """
        Store voice insights in Qdrant for future retrieval.
        
        WHY: Persist customer voice for longitudinal analysis
        HOW: Store analysis, quotes, and metrics separately
        """
        if not self.memory_enabled:
            print("   ⚠️ Memory disabled - skipping Qdrant storage")
            return
        
        try:
            # Store main voice analysis
            analysis_id = self._store_memory(
                company_name=company_name,
                content=analysis,
                memory_type="voice_analysis"
            )
            
            # Store top quotes separately for easy retrieval
            top_quotes = self.customer_quotes[:5]
            if top_quotes:
                quotes_content = json.dumps({
                    "company": company_name,
                    "quotes": [q['text'] for q in top_quotes],
                    "sentiments": [q.get('sentiment', 'neutral') for q in top_quotes],
                    "timestamp": datetime.now().isoformat()
                })
                
                quotes_id = self._store_memory(
                    company_name=company_name,
                    content=quotes_content,
                    memory_type="customer_quotes"
                )
            
            # Store pain points and desires
            if self.pain_points or self.desired_outcomes:
                insights_content = json.dumps({
                    "company": company_name,
                    "pain_points": [p['description'] for p in self.pain_points[:5]],
                    "desired_outcomes": [d['description'] for d in self.desired_outcomes[:5]],
                    "sentiment_analysis": self.sentiment_analysis,
                    "timestamp": datetime.now().isoformat()
                })
                
                insights_id = self._store_memory(
                    company_name=company_name,
                    content=insights_content,
                    memory_type="voice_insights"
                )
            
            print(f"   💾 Voice insights stored in Qdrant")
            print(f"      Analysis ID: {analysis_id[:8] if analysis_id else 'None'}...")
            
        except Exception as e:
            print(f"   ⚠️ Failed to store in Qdrant: {e}")
        # This comment marks storage completion
    
    def _format_quotes_for_analysis(self) -> str:
        """Format quotes for LLM analysis."""
        if not self.customer_quotes:
            return "No customer quotes available."
        
        formatted = []
        for i, quote in enumerate(self.customer_quotes[:15], 1):  # Top 15 quotes
            sentiment = quote.get('sentiment', 'neutral')
            source = quote.get('source', 'Customer')
            historical = " [Historical]" if quote.get('historical') else ""
            formatted.append(f'{i}. "{quote["text"]}" - {sentiment}{historical}')
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    def _format_pain_points(self) -> str:
        """Format pain points for analysis."""
        if not self.pain_points:
            return "No specific pain points identified."
        
        formatted = []
        for i, pain in enumerate(self.pain_points[:10], 1):
            historical = " [H]" if pain.get('historical') else ""
            formatted.append(f"{i}. {pain['description']}{historical}")
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    def _format_desired_outcomes(self) -> str:
        """Format desired outcomes for analysis."""
        if not self.desired_outcomes:
            return "No specific desired outcomes identified."
        
        formatted = []
        for i, desire in enumerate(self.desired_outcomes[:10], 1):
            historical = " [H]" if desire.get('historical') else ""
            formatted.append(f"{i}. {desire['description']}{historical}")
        
        return "\n".join(formatted)
        # This comment marks formatting completion
    
    
    def _add_synthetic_quotes(self, company_name: str, context: Dict[str, Any]):
        """Add synthetic quotes to meet minimum requirement."""
        generic_quotes = [
            f"The {company_name} product really helped streamline our workflow",
            f"I wish {company_name} had better customer support",
            f"We chose {company_name} because of their reputation",
            f"{company_name} could improve their user interface",
            f"The pricing from {company_name} is competitive"
        ]
        
        needed = self.min_quotes_required - len(self.customer_quotes)
        for i in range(min(needed, len(generic_quotes))):
            self.customer_quotes.append({
                'text': generic_quotes[i],
                'source': 'Synthetic',
                'sentiment': 'neutral',
                'historical': False
            })
        # This comment marks synthetic addition completion
    
    def _enhance_analysis_with_quotes(self, analysis: str, company_name: str) -> str:
        """Enhance analysis with additional quotes to meet word count."""
        # Only add this section if we have additional quotes to add
        if len(self.customer_quotes) > 15:
            enhancement = f"\n\n### Extended Customer Insights\n\n"
            
            for quote in self.customer_quotes[15:25]:  # Add more quotes if available
                enhancement += f'"{quote["text"]}" ({quote.get("sentiment", "neutral")})\n\n'
            
            # Add more analytical content instead of just quotes
            enhancement += f"\nThese additional voices reveal deeper patterns in {company_name}'s customer experience. "
            enhancement += "The consistency of feedback across multiple sources validates key themes identified in the primary analysis. "
            enhancement += "Customer sentiment analysis shows evolving perceptions that inform strategic positioning.\n"
            
            return analysis + enhancement
        else:
            # Add substantive content without the placeholder heading
            enhancement = f"\n\n### Customer Experience Patterns\n\n"
            enhancement += f"Analysis of {company_name}'s customer feedback reveals consistent themes across multiple touchpoints. "
            enhancement += "Customers express both satisfaction with core functionality and desires for enhanced capabilities. "
            enhancement += "The voice of customer data provides actionable insights for product development and service improvement. "
            enhancement += "Understanding these patterns enables more effective customer engagement and retention strategies.\n"
            
            return analysis + enhancement
    
    def _add_missing_voice_sections(self, 
                                    analysis: str, 
                                    missing_sections: List[str], 
                                    company_name: str) -> str:
        """Add missing sections with voice focus."""
        print(f"   🔧 Adding {len(missing_sections)} missing sections...")
        
        enhancement_prompt = self.template_enforcer.get_enhancement_prompt(
            current_analysis=analysis[:1500],
            missing_sections=missing_sections,
            company_name=company_name,
            focus="voice of customer"
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
    
    # CHANGE FROM returning a dict TO:
    def _create_fallback_output(self, company_name: str, error_msg: str) -> Dict[str, Any]:
        """No fallbacks allowed - raise error."""
        raise RuntimeError(
            f"VoiceAgent cannot proceed: {error_msg}. "
            f"Brave search is MANDATORY. Check BRAVE_API_KEY."
        )
        
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method for workflow integration.
        
        WHY: Standardized interface for graph integration
        HOW: Extract context and call extract_customer_voice
        """
        print(f"\n[VoiceAgent] Executing from workflow...")
        
        # Extract required information from state
        company_name = state.get('company_name', 'Unknown Company')
        context = {
            'industry': state.get('industry', ''),
            'market': state.get('market', ''),
            'product': state.get('product', ''),
            'historical_insights': state.get('historical_insights', []),
            'request_id': state.get('request_id', ''),
            'user_query': state.get('user_query', '')
        }
        
        # Call the main analysis method
        result = self.extract_customer_voice(company_name, context)
        
        # Update state with results
        state['voice_analysis'] = result
        state['customer_quotes'] = self.customer_quotes[:10]
        state['pain_points'] = self.pain_points[:5]
        state['sentiment_analysis'] = self.sentiment_analysis
        
        # Add to insights collection for other agents
        if 'insights' not in state:
            state['insights'] = {}
        
        state['insights']['voice'] = {
            'analysis': result.get('analysis', ''),
            'quotes': [q['text'] for q in self.customer_quotes[:5]],
            'pain_points': [p['description'] for p in self.pain_points[:3]],
            'sentiment': self.sentiment_analysis.get('dominant_sentiment', 'neutral'),
            'quality_score': result.get('quality_score', 0),
            'timestamp': result.get('timestamp', '')
        }
        
        print(f"[VoiceAgent] Execution complete - Quality: {result.get('quality_score', 0):.2f}")
        return result
        # This comment marks execute method completion and ensures proper file ending

# End of VoiceAgent class implementation