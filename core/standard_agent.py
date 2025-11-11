# core/standard_agent.py
"""
Standard Agent Node - Base class for all market research agents.
Enforces 14-Section Market Research Template.
Integrates with Qdrant for persistent, shared company memory.
Supports both individual methods and execute() pattern.
FIXED: Word count, memory storage, quality scoring, and rate limiting issues.
"""

import os
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from abc import ABC, abstractmethod

# Qdrant Memory Integration
try:
    from core.memory_system_qdrant import QdrantMemorySystem
    QDRANT_AVAILABLE = True
    print("✅ Qdrant memory system loaded successfully")
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not available - running in non-memory mode")
except Exception as e:
    QDRANT_AVAILABLE = False
    print(f"⚠️ Qdrant initialization failed: {e} - running in non-memory mode")

# LLM Imports
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

# Web Search Integration - Using custom wrapper
try:
    from core.brave_search_wrapper import BraveSearchResults, BraveSearchWrapper
    BRAVE_SEARCH_AVAILABLE = True
    print("✅ Brave search wrapper loaded")
except ImportError as e:
    BRAVE_SEARCH_AVAILABLE = False
    print(f"⚠️ Brave search not available: {e}")
    
    # Create mock classes
    class BraveSearchResults:
        def __init__(self, *args, **kwargs):
            self.max_results = kwargs.get('max_results', 5)
        
        def run(self, query):
            return f"Mock search results for: {query}"
        
        def search(self, query):
            return [{"content": f"Mock result for {query}", "source": "Mock"}]
    
    class BraveSearchWrapper:
        def __init__(self, *args, **kwargs):
            self.api_key = kwargs.get('api_key')

# Standard Agent Base Class
class StandardAgentNode(ABC):
    """
    Base class for all Level 5 ICP Intelligence agents.
    
    WHY: Enforces consistent 14-section template across all agents
    HOW: Validates output structure, integrates memory, supports dual patterns
    WHAT: Foundation for psychological, voice, competitor, interview, and GTM agents
    """
    
    # 14-SECTION TEMPLATE DEFINITION
    REQUIRED_SECTIONS = [
        "1. EXECUTIVE SUMMARY",
        "2. MARKET CONTEXT", 
        "3. TARGET AUDIENCE",
        "4. CUSTOMER PSYCHOLOGY",
        "5. VOICE OF CUSTOMER",
        "6. COMPETITIVE LANDSCAPE",
        "7. POSITIONING STRATEGY",
        "8. MESSAGING FRAMEWORK",
        "9. PRODUCT STRATEGY",
        "10. PRICING STRATEGY",
        "11. SALES STRATEGY",
        "12. MARKETING STRATEGY",
        "13. SUCCESS METRICS",
        "14. IMPLEMENTATION ROADMAP"
    ]
    
    def __init__(self, agent_name: str = "base_agent", role_prompt: str = ""):
        """
        Initialize the standard agent with MANDATORY Brave search.
        
        Args:
            agent_name: Unique identifier for this agent
            role_prompt: The system prompt defining agent's expertise
        """
        print(f"\n{'='*60}")
        print(f"🤖 Initializing {agent_name} with 14-Section Template")
        print(f"{'='*60}")
        
        # Core Configuration
        self.agent_name = agent_name
        self.role_prompt = self._enhance_prompt_with_template(role_prompt)
        self.quality_threshold = 0.7
        
        # Enhanced word count requirements for proper depth
        if 'interview' in agent_name:
            self.min_word_count = 2500
            self.target_word_count = 3500
        elif 'gtm' in agent_name:
            self.min_word_count = 3000
            self.target_word_count = 4000
        else:
            self.min_word_count = 2000
            self.target_word_count = 2500
            
        self.min_competitors_required = 3  # For CompetitorAgent
        self.min_interviews_required = 3   # For Interview agents
        self.min_patterns_required = 5     # For PsychologicalAgent
        self.min_quotes_required = 10      # For VoiceAgent
        self.max_retries = 3
        
        # Rate limiting for API calls
        self.last_llm_call = 0
        self.min_call_interval = 1.0  # Minimum seconds between calls
        
        # Memory System with Fallback
        self.memory_system = None
        self.memory_enabled = False
        
        if QDRANT_AVAILABLE:
            try:
                self.memory_system = QdrantMemorySystem()
                self.memory_enabled = True
                print(f"✅ Memory system connected for {agent_name}")
            except Exception as e:
                print(f"⚠️ Memory system failed to connect: {e}")
                print(f"   Continuing without memory persistence")
                self.memory_enabled = False
        else:
            print(f"ℹ️ Running {agent_name} without memory persistence")
        
        # LLM Configuration (Anthropic Claude primary, OpenAI fallback)
        self.llm = None
        self.fallback_llm = None
        
        try:
            anthropic_key = os.getenv('ANTHROPIC_API_KEY')
            if anthropic_key:
                self.llm = ChatAnthropic(
                    model="claude-3-5-sonnet-20241022",
                    anthropic_api_key=anthropic_key,
                    temperature=0.7,
                    max_tokens=8192
                )
                print(f"✅ Claude Sonnet initialized for {agent_name}")
        except Exception as e:
            print(f"⚠️ Claude initialization failed: {e}")
        
        # Fallback to OpenAI if Claude unavailable
        if not self.llm:
            try:
                openai_key = os.getenv('OPENAI_API_KEY')
                if openai_key:
                    self.fallback_llm = ChatOpenAI(
                        model="gpt-4-turbo-preview",
                        temperature=0.7,
                        max_tokens=4096
                    )
                    self.llm = self.fallback_llm
                    print(f"✅ GPT-4 fallback initialized for {agent_name}")
            except Exception as e:
                print(f"❌ No LLM available: {e}")
        
        # MANDATORY Brave Search Integration
        self.search_tool = None
        self.search_enabled = False
        self._last_search_used = False
        brave_api_key = os.getenv('BRAVE_API_KEY')
        
        if not brave_api_key:
            raise RuntimeError(
                f"CRITICAL: {agent_name} cannot initialize without BRAVE_API_KEY. "
                f"Brave search is MANDATORY for all agents. Add BRAVE_API_KEY to .env file."
            )
        
        try:
            search_wrapper = BraveSearchWrapper(
                api_key=brave_api_key,
                search_kwargs={"count": 5}
            )
            self.search_tool = BraveSearchResults(
                api_wrapper=search_wrapper,
                max_results=5
            )
            self.search_enabled = True
            print(f"✅ Brave search enabled for {agent_name} (MANDATORY)")
        except Exception as e:
            raise RuntimeError(
                f"CRITICAL: Brave search initialization failed for {agent_name}: {e}. "
                f"Cannot proceed without search capability."
            )
        
        print(f"✅ {agent_name} ready with 14-section template")
        print(f"   Memory: {'Enabled' if self.memory_enabled else 'Disabled'}")
        print(f"   Search: ENABLED (Mandatory)")
        print(f"   LLM: {self.llm.__class__.__name__ if self.llm else 'None'}")
    
    def _enhance_prompt_with_template(self, base_prompt: str) -> str:
        """
        Enhance any role prompt with 14-section template requirements and word count.
        
        WHY: Ensure EVERY agent follows the standard template WITH proper depth
        HOW: Append template instructions with explicit word count requirements
        """
        # Determine word count based on agent type
        if 'interview' in self.agent_name:
            min_words = 3000
            section_words = 250
        elif 'gtm' in self.agent_name:
            min_words = 3500
            section_words = 300
        else:
            min_words = 2500
            section_words = 200
            
        template_instructions = f"""

CRITICAL REQUIREMENTS:
1. Generate a COMPREHENSIVE analysis of AT LEAST {min_words} words total
2. Each section must contain AT LEAST {section_words} words of detailed, specific content
3. DO NOT provide brief summaries - include concrete examples, data, and insights
4. Expand on each point with thorough explanations and context

You MUST structure ALL outputs following this EXACT 14-section template:

1. EXECUTIVE SUMMARY - High-level overview and key insights ({section_words}+ words)
2. MARKET CONTEXT - Industry landscape and current trends ({section_words}+ words)
3. TARGET AUDIENCE - Detailed customer segments and profiles ({section_words}+ words)
4. CUSTOMER PSYCHOLOGY - Mental models, motivations, and behaviors ({section_words}+ words)
5. VOICE OF CUSTOMER - Actual quotes, feedback, and expressions ({section_words}+ words)
6. COMPETITIVE LANDSCAPE - Competitor analysis and positioning ({section_words}+ words)
7. POSITIONING STRATEGY - Unique value proposition and differentiation ({section_words}+ words)
8. MESSAGING FRAMEWORK - Core messages and communication strategy ({section_words}+ words)
9. PRODUCT STRATEGY - Product development and feature priorities ({section_words}+ words)
10. PRICING STRATEGY - Pricing models and monetization approach ({section_words}+ words)
11. SALES STRATEGY - Sales process and enablement tactics ({section_words}+ words)
12. MARKETING STRATEGY - Marketing channels and campaigns ({section_words}+ words)
13. SUCCESS METRICS - KPIs and measurement framework ({section_words}+ words)
14. IMPLEMENTATION ROADMAP - Timeline and action steps ({section_words}+ words)

Each section should be:
- Clearly numbered and titled exactly as shown above
- Comprehensive with detailed analysis (minimum {section_words} words per section)
- Data-driven with specific examples when possible
- Specific to the company being analyzed
- Rich in insights and actionable recommendations

IMPORTANT: Generate the FULL analysis in ONE response. Do not truncate or summarize.
Total output must be AT LEAST {min_words} words to provide proper depth and value.
"""
        return base_prompt + template_instructions
    
    def _validate_output(self, output: str) -> Dict[str, Any]:
        """
        Validate output follows 14-section template.
        
        WHY: Ensure consistency across all agents
        HOW: Check for required sections, calculate completeness
        RETURNS: Dict with validation results
        """
        validation_result = {
            'is_valid': True,
            'completeness_score': 0.0,
            'missing_sections': [],
            'found_sections': [],
            'word_counts': {},
            'completeness': 0.0,  # For compatibility
            'total_words': len(output.split()) if output else 0
        }
        
        # Check each required section
        for section in self.REQUIRED_SECTIONS:
            # Use regex to find section headers (case-insensitive)
            pattern = re.escape(section).replace(r'\d+', r'\d+')
            if re.search(pattern, output, re.IGNORECASE):
                validation_result['found_sections'].append(section)
                
                # Extract section content for word count
                section_num = section.split('.')[0]
                next_num = str(int(section_num) + 1) if int(section_num) < 14 else None
                
                # Find content between this section and next
                if next_num:
                    section_pattern = f"{pattern}(.*?)(?={next_num}\.|$)"
                else:
                    section_pattern = f"{pattern}(.*?)$"
                    
                match = re.search(section_pattern, output, re.IGNORECASE | re.DOTALL)
                
                if match:
                    section_content = match.group(1)
                    word_count = len(section_content.split())
                    validation_result['word_counts'][section] = word_count
            else:
                validation_result['missing_sections'].append(section)
                validation_result['is_valid'] = False
        
        # Calculate completeness score
        found_count = len(validation_result['found_sections'])
        total_count = len(self.REQUIRED_SECTIONS)
        validation_result['completeness_score'] = found_count / total_count
        validation_result['completeness'] = validation_result['completeness_score']
        
        # Log validation results
        print(f"\n   📋 Template Validation:")
        print(f"      Sections Found: {found_count}/{total_count}")
        print(f"      Completeness: {validation_result['completeness_score']:.1%}")
        print(f"      Total Words: {validation_result['total_words']}")
        
        if validation_result['missing_sections']:
            print(f"      ⚠️ Missing: {', '.join([s.split('.')[0] for s in validation_result['missing_sections'][:3]])}")
        
        return validation_result
    
    def _store_memory(self, company_name: str, content: str, memory_type: str = "analysis") -> Optional[str]:
        """
        Store memory in Qdrant with proper metadata handling.
        
        FIX: Pass metadata directly in content or use proper method signature
        """
        if not self.memory_enabled or not self.memory_system:
            return None
        
        try:
            # Create client_id from company_name (shared across all agents)
            client_id = f"company_{company_name.lower().replace(' ', '_')}"
            
            # Embed metadata in content as JSON string
            memory_content = json.dumps({
                "content": content,
                "company": company_name,
                "timestamp": datetime.now().isoformat(),
                "word_count": len(content.split()),
                "agent_version": "v2.1_fixed"
            })
            
            # Store without metadata keyword argument
            memory_id = self.memory_system.store_memory(
                client_id=client_id,
                agent_name=self.agent_name,
                memory_type=memory_type,
                content=memory_content
            )
            
            print(f"   💾 Stored memory for {self.agent_name}: {content[:50]}...")
            return memory_id
            
        except Exception as e:
            print(f"   ⚠️ Memory storage failed: {e}")
            return None
    
    def _retrieve_memories(self, company_name: str, query: str = None, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant memories from Qdrant with proper error handling.
        """
        if not self.memory_enabled or not self.memory_system:
            return []
        
        try:
            client_id = f"company_{company_name.lower().replace(' ', '_')}"
            
            if not query:
                query = f"{company_name} {self.agent_name} insights"
            
            memories = []
            
            # Try retrieve_memories method
            if hasattr(self.memory_system, 'retrieve_memories'):
                memory_objects = self.memory_system.retrieve_memories(
                    client_id=client_id,
                    query=query,
                    limit=limit
                )
                # Convert Memory objects to dictionaries
                if memory_objects:
                    for mem in memory_objects:
                        if hasattr(mem, 'to_dict'):
                            memories.append(mem.to_dict())
                        elif hasattr(mem, '__dict__'):
                            memories.append(mem.__dict__)
                        else:
                            # Try to parse JSON content
                            try:
                                content = str(mem)
                                if content.startswith('{'):
                                    parsed = json.loads(content)
                                    memories.append(parsed)
                                else:
                                    memories.append({'content': content})
                            except:
                                memories.append({'content': str(mem)})
            
            if memories:
                print(f"   ✅ Retrieved {len(memories)} relevant memories")
            
            return memories
                
        except Exception as e:
            print(f"   ⚠️ Memory retrieval failed: {e}")
            return []
    
    def _perform_web_search(self, query: str, company_name: str = None) -> List[Dict]:
        """
        Perform MANDATORY web search using Brave API with rate limiting.
        
        WHY: Real-time data is required for accurate market intelligence
        HOW: Use Brave API with proper error handling
        WHAT: Returns search results or raises error (no fallbacks)
        """
        if not self.search_enabled or not self.search_tool:
            raise RuntimeError(
                f"CRITICAL: {self.agent_name} cannot function without search. "
                f"Brave API is MANDATORY. Check BRAVE_API_KEY in .env"
            )
        
        try:
            # Rate limiting for search API
            time.sleep(0.2)  # Small delay between searches
            
            # Enhance query with company context if provided
            if company_name:
                enhanced_query = f"{company_name} {query}"
            else:
                enhanced_query = query
            
            print(f"   🔍 Searching: {enhanced_query[:50]}...")
            
            # Check if search_tool has search method
            if hasattr(self.search_tool, 'search'):
                results = self.search_tool.search(enhanced_query)
            else:
                results = self.search_tool.run(enhanced_query)
            
            self._last_search_used = True
            
            # Parse results based on type
            if isinstance(results, str):
                return [{"content": results, "source": "Brave Search"}]
            elif isinstance(results, list):
                if not results:
                    raise RuntimeError(f"Search returned no results for: {enhanced_query}")
                return results
            else:
                return [{"content": str(results), "source": "Brave Search"}]
                
        except Exception as e:
            # No fallback - search is mandatory
            raise RuntimeError(
                f"CRITICAL: Search failed for {self.agent_name}: {e}. "
                f"Cannot proceed without search results."
            )
    
    def _validate_search_requirement(self):
        """
        Validate that search is properly configured and available.
        Called before any agent operation that requires search.
        
        WHY: Enforce mandatory search requirement
        HOW: Check configuration and raise error if not available
        """
        if not self.search_enabled:
            raise RuntimeError(
                f"CRITICAL: {self.agent_name} requires search to be enabled. "
                f"Cannot proceed without BRAVE_API_KEY."
            )
        
        if not self.search_tool:
            raise RuntimeError(
                f"CRITICAL: {self.agent_name} search tool not initialized. "
                f"Check BRAVE_API_KEY configuration."
            )
        
        # Test search availability with a simple query
        try:
            test_results = self._perform_web_search("test", None)
            if not test_results:
                raise RuntimeError("Search test failed - no results returned")
        except Exception as e:
            raise RuntimeError(
                f"CRITICAL: Search validation failed for {self.agent_name}: {e}"
            )
    
    def _build_context_with_memories(self, company_name: str, base_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance context with relevant memories.
        """
        enhanced_context = base_context.copy()
        
        # Retrieve relevant memories
        memories = self._retrieve_memories(company_name)
        
        if memories:
            # Format memories for context
            memory_insights = []
            for memory in memories[:3]:  # Use top 3 most relevant
                # Handle both string and dict content
                if isinstance(memory.get("content"), str):
                    try:
                        # Try to parse JSON content
                        if memory["content"].startswith('{'):
                            parsed = json.loads(memory["content"])
                            content = parsed.get("content", memory["content"])
                        else:
                            content = memory["content"]
                    except:
                        content = memory["content"]
                else:
                    content = str(memory.get("content", ""))
                    
                memory_insights.append({
                    "agent": memory.get("agent_name", "unknown"),
                    "insight": content[:500],  # Truncate for context
                    "date": memory.get("timestamp", ""),
                    "relevance": memory.get("score", 0.0)
                })
            
            enhanced_context["historical_insights"] = memory_insights
            enhanced_context["memory_available"] = True
            print(f"   📚 Added {len(memory_insights)} historical insights to context")
        else:
            enhanced_context["memory_available"] = False
        
        return enhanced_context
    
    def _rate_limit_llm_call(self):
        """
        Implement rate limiting for LLM calls to avoid 529 errors.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_llm_call
        
        if time_since_last < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last
            print(f"   ⏳ Rate limiting: waiting {sleep_time:.1f}s...")
            time.sleep(sleep_time)
        
        self.last_llm_call = time.time()
    
    def _create_agent_output(self, 
                        company_name: str,
                        analysis: str,
                        search_results: List[Dict] = None,
                        additional_metrics: Dict = None) -> Dict[str, Any]:
        """
        Create standardized output format for all agents.
        REQUIRES search_results to be non-empty.
        """
        # Validate that search was used
        if not search_results:
            raise RuntimeError(
                f"{self.agent_name} output requires search results. "
                f"No search results provided for {company_name}."
            )
        
        # Validate output
        validation = self._validate_output(analysis)
        
        # Calculate quality score with fixed metric handling
        quality_score = self._calculate_quality_score(
            analysis,
            additional_metrics
        )
        
        # Store in memory if quality is good
        if quality_score >= self.quality_threshold:
            self._store_memory(company_name, analysis, "analysis")
        
        # Build output
        output = {
            "agent": self.agent_name,
            "company": company_name,
            "analysis": analysis,
            "quality_score": quality_score,
            "word_count": len(analysis.split()),
            "search_enabled": True,  # Always true now
            "search_used": True,  # Always true now
            "search_results_count": len(search_results),
            "memory_enabled": self.memory_enabled,
            "timestamp": datetime.now().isoformat(),
            "template_compliance": validation['completeness_score'],
            "memory_used": False  # Will be set by agent if memories were used
        }
        
        # Add search results (mandatory)
        output["search_results"] = search_results[:5]  # Top 5 results
        
        # Add additional metrics if provided
        if additional_metrics:
            output["metrics"] = additional_metrics
        
        return output
    
    def _generate_analysis_chunked(self, company_name: str, context: Dict[str, Any], 
                                   agent_specific_data: List[Dict] = None) -> str:
        """
        Generate analysis in chunks to avoid token limits.
        Universal method for all agents to generate comprehensive 14-section analyses.
        """
        if not self.llm:
            raise RuntimeError("LLM not available")
        
        # Define section groups for chunked generation
        sections_part1 = [
            "1. EXECUTIVE SUMMARY",
            "2. MARKET CONTEXT", 
            "3. TARGET AUDIENCE",
            "4. CUSTOMER PSYCHOLOGY",
            "5. VOICE OF CUSTOMER",
            "6. COMPETITIVE LANDSCAPE",
            "7. POSITIONING STRATEGY"
        ]
        
        sections_part2 = [
            "8. MESSAGING FRAMEWORK",
            "9. PRODUCT STRATEGY",
            "10. PRICING STRATEGY",
            "11. SALES STRATEGY",
            "12. MARKETING STRATEGY",
            "13. SUCCESS METRICS",
            "14. IMPLEMENTATION ROADMAP"
        ]
        
        # Generate Part 1 (Sections 1-7)
        prompt_part1 = self._build_chunk_prompt(
            company_name, context, sections_part1, 
            part_number=1, agent_specific_data=agent_specific_data
        )
        
        print(f"   🤖 Generating Part 1 (Sections 1-7)...")
        response1 = self.llm.invoke([
            {"role": "system", "content": self.role_prompt},
            {"role": "user", "content": prompt_part1}
        ])
        part1 = response1.content if hasattr(response1, 'content') else str(response1)
        
        # Generate Part 2 (Sections 8-14)
        prompt_part2 = self._build_chunk_prompt(
            company_name, context, sections_part2,
            part_number=2, agent_specific_data=agent_specific_data
        )
        
        print(f"   🤖 Generating Part 2 (Sections 8-14)...")
        response2 = self.llm.invoke([
            {"role": "system", "content": self.role_prompt},
            {"role": "user", "content": prompt_part2}
        ])
        part2 = response2.content if hasattr(response2, 'content') else str(response2)
        
        # Combine both parts
        full_analysis = f"{part1}\n\n{part2}"
        
        word_count = len(full_analysis.split())
        print(f"   ✅ Generated {word_count} words total")
        
        return full_analysis

    def _build_chunk_prompt(self, company_name: str, context: Dict[str, Any], 
                        sections: List[str], part_number: int,
                        agent_specific_data: Any = None) -> str:
        """
        Build prompt for specific chunk of sections.
        Override this in each agent for agent-specific prompting.
        """
        # This will be overridden by each agent
        raise NotImplementedError("Each agent must implement _build_chunk_prompt")
    
    
    def _calculate_quality_score(self, output: str, additional_metrics: Dict = None) -> float:
        """
        Calculate quality score with proper metric type handling.
        
        FIX: Handle completeness as dict or float properly
        """
        if not output:
            print(f"   ⚠️ Empty output for quality scoring")
            return 0.0
        
        score = 0.0
        word_count = len(output.split())
        
        # Word count scoring (30% weight) - Updated for better depth
        if word_count >= self.target_word_count:
            score += 0.30
        elif word_count >= self.min_word_count:
            score += 0.25
        elif word_count >= self.min_word_count * 0.75:
            score += 0.15
        elif word_count >= self.min_word_count * 0.5:
            score += 0.10
        else:
            # Proportional score for below minimum
            score += (word_count / self.min_word_count) * 0.10
        
        # Template compliance scoring (40% weight) 
        validation = self._validate_output(output)
        score += validation['completeness_score'] * 0.40
        
        # Structure and formatting (20% weight)
        structure_score = 0.0
        
        # Check for section headers
        if re.findall(r'\d+\.\s+[A-Z\s]+', output):
            structure_score += 0.05
        
        # Check for subsections or bullet points
        if re.findall(r'[•\-\*]\s+', output) or re.findall(r'[a-z]\)', output):
            structure_score += 0.05
        
        # Check for proper paragraphing
        if len(output.split('\n\n')) > 10:
            structure_score += 0.05
        
        # Check for data/evidence (numbers, percentages, quotes)
        if re.findall(r'\d+%|\$\d+|"\w+.*?"', output):
            structure_score += 0.05
        
        score += structure_score
        
        # Agent-specific scoring (10% weight) - FIXED handling
        if additional_metrics:
            agent_score = 0.0
            
            if isinstance(additional_metrics, dict):
                # Handle completeness properly
                if 'completeness' in additional_metrics:
                    completeness = additional_metrics['completeness']
                    # Check if completeness is a dict with completeness_score
                    if isinstance(completeness, dict):
                        agent_score = completeness.get('completeness_score', 0.0) * 0.10
                    # Check if it's a float directly
                    elif isinstance(completeness, (int, float)):
                        agent_score = float(completeness) * 0.10
                    else:
                        agent_score = 0.05  # Default partial score
                        
                elif 'word_count' in additional_metrics and 'min_words' in additional_metrics:
                    ratio = additional_metrics['word_count'] / additional_metrics.get('min_words', 1000)
                    agent_score = min(ratio * 0.10, 0.10)
                    
            elif isinstance(additional_metrics, (int, float)):
                # For simple numeric metrics
                if additional_metrics > 0:
                    normalized = min(additional_metrics / 10, 1.0)
                    agent_score = normalized * 0.10
            
            score += agent_score
        
        # Search usage bonus (if applicable)
        if hasattr(self, '_last_search_used') and self._last_search_used:
            score += 0.05  # Small bonus for using real-time data
        
        # Cap at 1.0 (not just quality threshold)
        final_score = min(score, 1.0)
        
        print(f"   📊 Quality Score: {final_score:.2f} (Words: {word_count}/{self.min_word_count}, Template: {validation['completeness_score']:.1%})")
        
        return final_score
    
    def _call_llm_with_retry(self, messages: List[Dict], max_retries: int = 3) -> Optional[str]:
        """
        Call LLM with retry logic and rate limiting to handle 529 errors.
        """
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self._rate_limit_llm_call()
                
                # Make the call
                response = self.llm.invoke(messages)
                return response.content if hasattr(response, 'content') else str(response)
                
            except Exception as e:
                error_str = str(e)
                if '529' in error_str or 'overloaded' in error_str.lower():
                    wait_time = (attempt + 1) * 2  # Exponential backoff
                    print(f"   ⏳ API overloaded, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                else:
                    print(f"   ❌ LLM call failed: {e}")
                    break
        
        return None
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method for workflow integration.
        Must be implemented by each specific agent.
        
        MUST call _validate_search_requirement() at the beginning.
        MUST use _perform_web_search() for data gathering.
        MUST include search_results in output.
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of agent."""
        return f"<{self.__class__.__name__}(name='{self.agent_name}', memory={self.memory_enabled}, search={self.search_enabled})>"