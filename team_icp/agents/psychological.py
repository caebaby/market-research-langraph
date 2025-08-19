# team_icp/agents/psychological.py
"""
Level 4 Psychological Agent - Modular Architecture Version
"""

from typing import Dict, Any, List
from datetime import datetime
from core.standard_agent_v4 import StandardAgentNodeV4
from team_icp.prompts.research_prompts import ICPResearchPrompts


class PsychologicalAgent(StandardAgentNodeV4):
    """
    Psychological Analysis Agent - Level 4 with full modular capabilities
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Psychological Analyst",
            role_prompt="""You are an expert psychological researcher specializing in uncovering deep customer insights 
that drive purchasing decisions. Your analysis goes beyond surface-level demographics to reveal the 
unconscious motivations, hidden fears, and unspoken desires of the target audience.""",
            target_quality=0.85,
            require_human_review_below=0.70
        )
        self.sophisticated_prompts = ICPResearchPrompts()
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate psychological analysis with sophisticated frameworks"""
        memory_patterns = self._format_memories_detailed(memories)
        business_context = self._extract_business_context_only(context)
        
        sophisticated_prompt = self.sophisticated_prompts.get_psychological_analysis_prompt()
        formatted_prompt = sophisticated_prompt.format(
            business_context=business_context,
            memory_patterns=memory_patterns
        )
        
        if "INSIGHTS FROM OTHER AGENTS" in context:
            formatted_prompt += f"\n\nCOLLABORATIVE INTELLIGENCE:\n{context.split('INSIGHTS FROM OTHER AGENTS')[1]}"
        
        formatted_prompt += f"\n\nSPECIFIC ANALYSIS TASK:\n{task}"
        
        response = llm.invoke(formatted_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on psychological analysis quality"""
        reflection_prompt = """Evaluate this psychological analysis on these criteria:
1. Psychological Depth (0-1): Are unconscious patterns revealed?
2. Framework Coverage (0-1): Multiple frameworks applied?
3. Visceral Accuracy (0-1): Would customer feel deeply understood?
4. Actionability (0-1): Can insights drive decisions?

Score 0.0-1.0 on last line."""
        
        critique_prompt = f"{reflection_prompt}\n\nTASK: {task}\n\nRESPONSE:\n{response[:2000]}...\n\nCRITIQUE:"
        critique = llm.invoke(critique_prompt).content.strip()
        
        lines = critique.split('\n')
        score = 0.75
        try:
            import re
            last_line = lines[-1] if lines else ""
            match = re.search(r'(\d*\.?\d+)', last_line)
            if match:
                score = float(match.group(1))
                score = max(0.0, min(1.0, score))
        except:
            pass
        
        return {"critique": '\n'.join(lines[:-1]), "score": score}
    
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract key psychological insights for storage"""
        return {
            "frameworks_used": ["Jungian", "Lab Profile", "JTBD", "Cognitive Biases"],
            "key_patterns": response[:1000],
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        return {
            "summary": response[:500] + "..." if len(response) > 500 else response,
            "quality_score": quality,
            "psychological_patterns": self._extract_key_patterns(response)
        }
    
    def _format_memories_detailed(self, memories: List) -> str:
        if not memories:
            return "No previous analyses found. This is a fresh analysis."
        formatted = "MEMORY-ENHANCED PATTERNS:\n\n"
        for i, memory in enumerate(memories[:5], 1):
            content = memory.get('content', '')
            formatted += f"Memory {i}: {content[:300]}...\n"
        return formatted
    
    def _extract_business_context_only(self, full_context: str) -> str:
        if "INSIGHTS FROM OTHER AGENTS" in full_context:
            return full_context.split("INSIGHTS FROM OTHER AGENTS")[0].strip()
        return full_context
    
    def _extract_key_patterns(self, response: str) -> List[str]:
        patterns = []
        keywords = ["identity", "fear", "unconscious", "desire", "contradiction"]
        for keyword in keywords:
            if keyword in response.lower():
                patterns.append(f"{keyword.capitalize()} patterns detected")
        return patterns[:5]