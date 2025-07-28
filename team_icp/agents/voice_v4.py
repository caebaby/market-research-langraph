# team_icp/agents/voice_v4.py
"""
Level 4 Voice of Customer Agent - TEST VERSION
Uses new StandardAgentNodeV4 base
"""

from typing import Dict, Any, List
from core.standard_agent_v4 import StandardAgentNodeV4
from ..prompts.voice_prompts import VoicePrompts


class VoiceAgentV4(StandardAgentNodeV4):
    """
    Level 4 Voice Agent with memory and learning
    """
    
    def __init__(self):
        # Get role from voice prompts
        role_prompt = VoicePrompts.get_role_prompt()
        
        super().__init__(
            agent_name="Voice of Customer Mind Reader V4",
            role_prompt=role_prompt,
            target_quality=0.85,  # Higher bar for voice accuracy
            require_human_review_below=0.65
        )
        
        print(f"[L4 CHECK] Agent initialized: {self.agent_name}")
        print(f"[L4 CHECK] Target quality: {self.target_quality}")
        print(f"[L4 CHECK] HITL threshold: {self.review_threshold}")
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate voice of customer analysis"""
        # Build enhanced context with memories
        enhanced_context = context
        
        if memories:
            memory_context = "\n\nRELEVANT PAST VOICE ANALYSES:\n"
            for memory in memories[:3]:
                content = memory.get("content", "")
                quality = memory.get("quality", 0)
                memory_context += f"\n[Quality: {quality:.2f}] {content[:200]}...\n"
            enhanced_context += memory_context
        
        # Extract psychological insights if available
        psychological_profile = "No psychological profile available"
        if "EXECUTIVE SUMMARY" in context:
            start = context.find("EXECUTIVE SUMMARY")
            end = context.find("\n\n", start + 500)
            psychological_profile = context[start:end if end != -1 else start + 1000]
        
        # Get voice synthesis template
        synthesis_template = VoicePrompts.get_synthesis_template()
        print(f"[DEBUG] Synthesis template length: {len(synthesis_template)}")
        
        # For testing, create simplified inputs
        language_hypothesis = "Based on context, hypothesizing target customer language patterns..."
        validation_data = "No validation data available in test mode"
        competitor_insights = "No competitor insights available"
        
        # Format the synthesis prompt
        formatted_prompt = synthesis_template.format(
            business_context=enhanced_context,
            psychological_profile=psychological_profile,
            language_hypothesis=language_hypothesis,
            validation_data=validation_data,
            competitor_insights=competitor_insights
        )
        
        # Add role prompt
        full_prompt = f"{self.role_prompt}\n\n{formatted_prompt}"
        print(f"[DEBUG] Total formatted prompt length: {len(full_prompt)}")
        
        # Generate response
        response = llm.invoke(full_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Evaluate voice analysis quality"""
        reflection_prompt = VoicePrompts.get_reflection_criteria()
        
        critique_prompt = f"""{reflection_prompt}

TASK: {task}

RESPONSE TO EVALUATE:
{response[:2000]}...

Provide detailed critique and score (0.0-1.0) on last line.

CRITIQUE:"""
        
        critique = llm.invoke(critique_prompt)
        critique_text = critique.content if hasattr(critique, 'content') else str(critique)
        
        # Parse score from last line
        lines = critique_text.strip().split('\n')
        score = 0.0
        
        try:
            import re
            last_line = lines[-1] if lines else ""
            match = re.search(r'(\d*\.?\d+)', last_line)
            if match:
                score = float(match.group(1))
                score = max(0.0, min(1.0, score))
        except:
            pass
        
        return {
            "critique": '\n'.join(lines[:-1]) if len(lines) > 1 else critique_text,
            "score": score
        }
    
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract key voice patterns for storage"""
        insights = {
            "golden_phrases": [],
            "pain_language": [],
            "trigger_phrases": [],
            "copy_headlines": []
        }
        
        # Extract golden phrase
        if "Golden Phrase" in response:
            try:
                golden_start = response.find("Golden Phrase")
                golden_line = response[golden_start:response.find("\n", golden_start + 50)]
                insights["golden_phrases"].append(golden_line)
            except:
                pass
        
        # Extract pain language
        if "Pain Language" in response:
            try:
                pain_start = response.find("Pain Language")
                pain_section = response[pain_start:pain_start + 500]
                # Simple extraction of quoted phrases
                import re
                quotes = re.findall(r'"([^"]*)"', pain_section)
                insights["pain_language"] = quotes[:5]  # First 5 pain phrases
            except:
                pass
        
        # Extract headlines
        if "Ad Headlines:" in response:
            try:
                headlines_start = response.find("Ad Headlines:")
                headlines_section = response[headlines_start:headlines_start + 500]
                lines = headlines_section.split('\n')
                for line in lines[1:4]:  # Get first 3 headlines
                    if line.strip():
                        insights["copy_headlines"].append(line.strip())
            except:
                pass
        
        return insights
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        # Extract summary focusing on voice findings
        summary = ""
        if "Voice of Customer Bible" in response:
            start = response.find("Voice of Customer Bible")
            end = response.find("###", start + 100)
            summary = response[start:end if end != -1 else start + 500]
        else:
            summary = response[:500] + "..."
        
        # Get extracted insights
        voice_insights = self._extract_insights_for_memory(response)
        
        return {
            "summary": summary,
            "quality_score": quality,
            "key_insights": voice_insights,
            "golden_phrase": voice_insights.get("golden_phrases", [""])[0] if voice_insights.get("golden_phrases") else "",
            "top_pain_phrases": voice_insights.get("pain_language", [])[:3]
        }
