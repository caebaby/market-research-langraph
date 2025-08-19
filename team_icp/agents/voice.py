# team_icp/agents/voice.py
"""
Level 4 Voice of Customer Agent - Modular Architecture Version
"""

from typing import Dict, Any, List
from datetime import datetime
import re
from core.standard_agent_v4 import StandardAgentNodeV4
from ..prompts.voice_prompts import VoicePrompts


class VoiceAgent(StandardAgentNodeV4):
    """
    Voice of Customer Agent - Journal-level accuracy with modular capabilities
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Voice of Customer Specialist",
            role_prompt=VoicePrompts.get_role_prompt(),
            target_quality=0.80,
            require_human_review_below=0.65
        )
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate voice analysis with memory-enhanced insights"""
        psychological_insights = self._extract_psychological_insights(context)
        competitor_insights = self._extract_competitor_insights(context)
        
        enhanced_context = context
        if psychological_insights:
            enhanced_context += f"\n\nPSYCHOLOGICAL PROFILE:\n{psychological_insights}"
        if competitor_insights:
            enhanced_context += f"\n\nCOMPETITOR CONTEXT:\n{competitor_insights}"
        if memories:
            memory_patterns = self._format_memory_patterns(memories)
            enhanced_context += f"\n\nLEARNED VOICE PATTERNS:\n{memory_patterns}"
        
        hypothesis_template = VoicePrompts.get_language_hypothesis_prompt()
        hypothesis_prompt = hypothesis_template.format(business_context=enhanced_context)
        hypothesis = llm.invoke(hypothesis_prompt).content
        
        synthesis_template = VoicePrompts.get_synthesis_template()
        final_prompt = synthesis_template.format(
            business_context=enhanced_context,
            psychological_profile=psychological_insights or "Analysis pending",
            language_hypothesis=hypothesis,
            validation_data="AI-Inferred patterns",
            competitor_insights=competitor_insights or "Analysis pending"
        )
        
        response = llm.invoke(final_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on voice capture quality"""
        reflection_criteria = VoicePrompts.get_reflection_criteria()
        reflection_prompt = f"{reflection_criteria}\n\nTASK: {task}\n\nRESPONSE:\n{response[:2000]}...\n\nCRITIQUE:"
        
        critique_response = llm.invoke(reflection_prompt)
        critique_text = critique_response.content if hasattr(critique_response, 'content') else str(critique_response)
        
        lines = critique_text.strip().split('\n')
        score = 0.75
        try:
            score_match = re.search(r'(\d*\.?\d+)', lines[-1])
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))
        except:
            pass
        
        return {"critique": '\n'.join(lines[:-1]), "score": score}
    
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract key voice insights for memory storage"""
        return {
            "timestamp": datetime.now().isoformat(),
            "golden_phrases": self._extract_key_phrases(response)[:5],
            "pain_language": self._extract_pain_language(response),
            "trigger_phrases": self._extract_trigger_phrases(response)
        }
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        return {
            "summary": f"Extracted authentic customer language patterns with {quality:.2f} accuracy",
            "golden_phrases": self._extract_key_phrases(response)[:3],
            "quality_score": quality
        }
    
    def _extract_psychological_insights(self, context: str) -> str:
        if "INSIGHTS FROM OTHER AGENTS" in context:
            try:
                insights_section = context.split("INSIGHTS FROM OTHER AGENTS")[1]
                if "Psychological" in insights_section:
                    psych_start = insights_section.find("Psychological")
                    psych_end = insights_section.find("\n\n", psych_start)
                    return insights_section[psych_start:psych_end if psych_end != -1 else None]
            except:
                pass
        return ""
    
    def _extract_competitor_insights(self, context: str) -> str:
        if "COMPETITIVE INTELLIGENCE" in context:
            try:
                comp_start = context.find("COMPETITIVE INTELLIGENCE")
                comp_end = context.find("\n\n", comp_start + 200)
                return context[comp_start:comp_end if comp_end != -1 else comp_start + 500]
            except:
                pass
        return ""
    
    def _format_memory_patterns(self, memories: List[Dict]) -> str:
        patterns = []
        for memory in memories[:3]:
            content = memory.get("content", "")
            if "golden phrase" in content.lower():
                patterns.append(content[:200])
        return "\n---\n".join(patterns) if patterns else "No previous patterns found"
    
    def _extract_key_phrases(self, response: str) -> List[str]:
        phrases = re.findall(r'"([^"]*)"', response)
        return [p for p in phrases if 5 < len(p) < 100][:10]
    
    def _extract_pain_language(self, response: str) -> List[str]:
        pain_keywords = ["frustrated", "tired", "struggling", "exhausted"]
        patterns = []
        for keyword in pain_keywords:
            if keyword in response.lower():
                patterns.append(f"{keyword} with...")
        return patterns[:3]
    
    def _extract_trigger_phrases(self, response: str) -> List[str]:
        trigger_keywords = ["ready to", "need to", "must", "can't continue"]
        patterns = []
        for keyword in trigger_keywords:
            if keyword in response.lower():
                patterns.append(f"{keyword}...")
        return patterns[:3]