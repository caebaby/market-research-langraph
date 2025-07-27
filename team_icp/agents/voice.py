# team_icp/agents/voice.py
"""
Level 4 Voice of Customer Agent - Journal-level accuracy with memory and learning
"""

from typing import Dict, Any, List
import json
import re
from datetime import datetime
from core.standard_agent import StandardAgentNode
from ..prompts.voice_prompts import VoicePrompts


class VoiceAgent(StandardAgentNode):
    """
    Level 4 Voice Agent that captures customer language at "read their journal" accuracy.
    
    Features:
    - Memory integration for learning patterns
    - Self-improvement from successful copy
    - Real-world validation via search
    - Inter-agent insights from psychological/competitor
    - Reflection with ICP accuracy scoring
    """
    
    def __init__(self):
        # Get role prompt from external prompts file
        role_prompt = VoicePrompts.get_role_prompt()
        
        super().__init__(
            agent_name="Voice of Customer Mind Reader",
            role_prompt=role_prompt,
            target_quality=0.85  # Higher bar for journal-level accuracy
        )
        
        # ICP accuracy validators
        self.icp_validators = {
            "demographic_match": 0.2,
            "psychographic_match": 0.3,
            "situational_match": 0.3,
            "language_sophistication_match": 0.2
        }
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 4 execution with memory and learning
        """
        print(f"[VoiceAgent] Starting journal-level voice analysis")
        
        # Store services for this execution
        self._temp_memory_service = state.get("memory_service")
        self._temp_tool_executor = state.get("tool_executor")
        
        # MEMORY RECALL - Learn from past successful voice captures
        if self._temp_memory_service:
            try:
                business_context = state.get("business_context", "")
                past_voices = self._temp_memory_service.recall(
                    agent_name="voice",
                    context=business_context,
                    limit=5
                )
                
                if past_voices:
                    print(f"[VoiceAgent] Recalled {len(past_voices)} relevant voice analyses")
                    # Add successful patterns to context
                    voice_patterns = self._extract_successful_patterns(past_voices)
                    if voice_patterns:
                        additional_context = f"\n\nSUCCESSFUL VOICE PATTERNS FROM SIMILAR ICPS:\n{voice_patterns}"
                        state["master_context"] = state.get("master_context", "") + additional_context
                        
            except Exception as e:
                print(f"[VoiceAgent] Memory recall error: {e}")
        
        # Execute core analysis
        result = super().__call__(state)
        
        # MEMORY STORAGE - Store successful voice captures for future learning
        if self._temp_memory_service and isinstance(result, dict):
            quality_score = result.get("quality_score", 0)
            if quality_score >= 0.8:  # Only store high-quality outputs
                try:
                    # Extract key voice patterns for future use
                    voice_insights = self._extract_voice_insights(result.get("current_output", ""))
                    
                    self._temp_memory_service.store(
                        agent_name="voice",
                        context=state.get("business_context", ""),
                        insights=voice_insights,
                        quality=quality_score
                    )
                    print(f"[VoiceAgent] Stored high-quality voice insights (score: {quality_score})")
                    
                except Exception as e:
                    print(f"[VoiceAgent] Memory storage error: {e}")
        
        # Clean up
        self._temp_memory_service = None
        self._temp_tool_executor = None
        
        return self._ensure_valid_state_return(result, state)
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """
        Generate voice analysis with memory-enhanced insights
        """
        # Extract insights from other agents
        psychological_insights = self._extract_psychological_insights(context)
        competitor_insights = self._extract_competitor_insights(context)
        
        # Build enhanced context
        enhanced_context = context
        
        # Add psychological insights if available
        if psychological_insights and "No psychological insights" not in psychological_insights:
            enhanced_context += f"\n\nPSYCHOLOGICAL PROFILE:\n{psychological_insights}"
        
        # Add competitor insights if available
        if competitor_insights and "No competitor insights" not in competitor_insights:
            enhanced_context += f"\n\nCOMPETITOR CONTEXT:\n{competitor_insights}"
        
        # Add memory insights if available
        if memories:
            memory_patterns = self._format_memory_patterns(memories)
            enhanced_context += f"\n\nLEARNED VOICE PATTERNS:\n{memory_patterns}"
        
        # Generate language hypothesis
        hypothesis = self._generate_language_hypothesis(enhanced_context, llm)
        
        # Attempt validation if tools available
        validation_data = "No validation available"
        if hasattr(self, '_temp_tool_executor') and self._temp_tool_executor:
            validation_data = self._validate_hypothesis(hypothesis, enhanced_context)
        
        # Build final synthesis
        synthesis_template = VoicePrompts.get_synthesis_template()
        final_prompt = synthesis_template.format(
            business_context=enhanced_context,
            psychological_profile=psychological_insights,
            language_hypothesis=hypothesis,
            validation_data=validation_data,
            competitor_insights=competitor_insights
        )
        
        # Generate voice bible
        response = llm.invoke(final_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _generate_language_hypothesis(self, context: str, llm) -> str:
        """Generate hypothesis about how target ICP speaks privately"""
        hypothesis_template = VoicePrompts.get_language_hypothesis_prompt()
        prompt = hypothesis_template.format(business_context=context)
        
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _validate_hypothesis(self, hypothesis: str, context: str) -> str:
        """Validate language hypothesis with real-world searches"""
        if not self._temp_tool_executor:
            return "No validation available - tool executor not provided"
        
        # Extract key phrases to validate
        key_phrases = self._extract_key_phrases(hypothesis)
        validation_results = []
        
        # Get search query templates
        search_templates = VoicePrompts.get_search_queries()
        
        # Execute targeted searches
        for i, phrase in enumerate(key_phrases[:3]):  # Limit searches
            for template in search_templates[:2]:  # Use first 2 templates
                try:
                    query = template.format(phrase=phrase, business_context=context[:50])
                    print(f"[VoiceAgent] Validating: {query}")
                    
                    result = self._temp_tool_executor.execute("web_search", {"query": query})
                    
                    # Handle different return types
                    if isinstance(result, str):
                        validation_results.append(f"Found: {result[:200]}...")
                    elif isinstance(result, dict):
                        content = result.get('output') or result.get('result') or str(result)
                        validation_results.append(f"Found: {content[:200]}...")
                        
                except Exception as e:
                    print(f"[VoiceAgent] Validation search error: {e}")
        
        return "\n".join(validation_results) if validation_results else "No validation results found"
    
    def _extract_key_phrases(self, hypothesis: str) -> List[str]:
        """Extract quotable phrases from hypothesis"""
        phrases = re.findall(r'"([^"]*)"', hypothesis)
        return [p for p in phrases if len(p) > 5 and len(p) < 50][:10]
    
    def _extract_psychological_insights(self, context: str) -> str:
        """Extract psychological insights from context"""
        if "INSIGHTS FROM OTHER AGENTS" in context:
            try:
                insights_section = context.split("INSIGHTS FROM OTHER AGENTS")[1]
                if "Psychological" in insights_section:
                    psych_start = insights_section.find("Psychological")
                    psych_end = insights_section.find("\n\n", psych_start)
                    return insights_section[psych_start:psych_end if psych_end != -1 else None]
            except:
                pass
        
        # Look for psychological markers
        psych_markers = ["unconscious", "fear", "desire", "identity", "belonging"]
        if any(marker in context.lower() for marker in psych_markers):
            return "Psychological insights detected in context"
        
        return "No psychological insights available"
    
    def _extract_competitor_insights(self, context: str) -> str:
        """Extract competitor insights from context"""
        if "COMPETITIVE INTELLIGENCE" in context:
            try:
                comp_start = context.find("COMPETITIVE INTELLIGENCE")
                comp_end = context.find("\n\n", comp_start + 200)
                return context[comp_start:comp_end if comp_end != -1 else comp_start + 500]
            except:
                pass
        
        return "No competitor insights available"
    
    def _extract_successful_patterns(self, past_voices: List[Dict]) -> str:
        """Extract successful patterns from past voice analyses"""
        patterns = []
        for memory in past_voices:
            if memory.get("quality", 0) >= 0.85:
                insights = memory.get("insights", {})
                if insights.get("golden_phrase"):
                    patterns.append(f"Golden phrase that worked: {insights['golden_phrase']}")
                if insights.get("pain_language"):
                    patterns.append(f"Pain language pattern: {insights['pain_language']}")
        
        return "\n".join(patterns) if patterns else ""
    
    def _extract_voice_insights(self, analysis: str) -> Dict[str, Any]:
        """Extract key insights from voice analysis for memory storage"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "golden_phrase": "",
            "pain_language": [],
            "trigger_phrases": [],
            "successful_headlines": []
        }
        
        # Extract golden phrase
        if "Golden Phrase" in analysis:
            try:
                golden_start = analysis.find("Golden Phrase")
                golden_line = analysis[golden_start:analysis.find("\n", golden_start + 50)]
                golden_match = re.search(r'"([^"]+)"', golden_line)
                if golden_match:
                    insights["golden_phrase"] = golden_match.group(1)
            except:
                pass
        
        # Extract other patterns (simplified for brevity)
        insights["pain_language"] = self._extract_key_phrases(analysis)[:3]
        
        return insights
    
    def _format_memory_patterns(self, memories: List[Dict]) -> str:
        """Format memory patterns for context"""
        patterns = []
        for memory in memories[:3]:  # Most recent/relevant
            content = memory.get("content", "")
            if "golden phrase" in content.lower():
                patterns.append(content[:200])
        
        return "\n---\n".join(patterns) if patterns else "No previous patterns found"
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on voice capture quality with ICP accuracy focus"""
        reflection_criteria = VoicePrompts.get_reflection_criteria()
        
        reflection_prompt = f"""{reflection_criteria}

TASK: {task}

RESPONSE TO EVALUATE:
{response[:2000]}...

Provide a detailed critique addressing each criterion.
Then on the LAST LINE ONLY, output a score from 0.0 to 1.0.

CRITIQUE:"""
        
        critique_response = llm.invoke(reflection_prompt)
        critique_text = critique_response.content if hasattr(critique_response, 'content') else str(critique_response)
        
        # Parse score
        try:
            lines = critique_text.strip().split('\n')
            last_line = lines[-1].strip() if lines else ""
            critique_content = '\n'.join(lines[:-1]) if len(lines) > 1 else critique_text
            
            score_match = re.search(r'(\d*\.?\d+)', last_line)
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))
            else:
                score = 0.0
                
        except Exception as e:
            print(f"[VoiceAgent] Reflection parsing error: {e}")
            critique_content = critique_text
            score = 0.0
        
        return {
            "critique": critique_content,
            "score": score
        }
    
    def _ensure_valid_state_return(self, result: Any, original_state: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure valid state dictionary is returned"""
        if isinstance(result, dict):
            # Preserve all original state fields
            for key in original_state:
                if key not in result:
                    result[key] = original_state[key]
            return result
        elif isinstance(result, str):
            original_state["current_output"] = result
            original_state["agent_name"] = self.agent_name
            return original_state
        else:
            original_state["current_output"] = str(result) if result else "Voice analysis completed"
            original_state["agent_name"] = self.agent_name
            return original_state
