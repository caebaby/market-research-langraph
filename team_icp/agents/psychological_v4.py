# team_icp/agents/psychological_v4.py
"""
Level 4 Psychological Agent - TEST VERSION
Uses new StandardAgentNodeV4 base
"""

from typing import Dict, Any, List
from core.standard_agent_v4 import StandardAgentNodeV4
from ..prompts.research_prompts import ICPResearchPrompts as PsychologicalPrompts


class PsychologicalAgentV4(StandardAgentNodeV4):
    """
    Level 4 Psychological Agent with memory and learning
    """
    
    def __init__(self):
        # Get role from your existing prompts
        role_prompt = PsychologicalPrompts.get_role_prompt()
        
        super().__init__(
            agent_name="Psychological Analyst V4",
            role_prompt=role_prompt,
            target_quality=0.80,
            require_human_review_below=0.60
        )
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate psychological analysis"""
        # Build enhanced context with memories
        enhanced_context = context
        
        if memories:
            memory_context = "\n\nRELEVANT PAST ANALYSES:\n"
            for memory in memories[:3]:
                content = memory.get("content", "")
                quality = memory.get("quality", 0)
                memory_context += f"\n[Quality: {quality:.2f}] {content[:200]}...\n"
            enhanced_context += memory_context
        
        # Get your existing sophisticated prompt
        analysis_prompt = PsychologicalPrompts.get_analysis_prompt()
        
        # Format with context
        formatted_prompt = f"{self.role_prompt}\n\n{analysis_prompt}\n\nCONTEXT:\n{enhanced_context}\n\nTASK:\n{task}"
        
        # Generate response
        response = llm.invoke(formatted_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Evaluate psychological analysis quality"""
        reflection_prompt = PsychologicalPrompts.get_reflection_criteria()
        
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
        """Extract key psychological insights for storage"""
        insights = {
            "frameworks_used": [],
            "key_findings": [],
            "patterns": []
        }
        
        # Simple extraction (enhance based on your needs)
        if "unconscious" in response.lower():
            insights["frameworks_used"].append("Unconscious patterns")
        if "archetype" in response.lower():
            insights["frameworks_used"].append("Jungian archetypes")
        
        # Extract key findings (simplified)
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.')):
                insights["key_findings"].append(line.strip())
        
        return insights
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        # Extract summary (first paragraph or executive summary)
        summary = ""
        if "EXECUTIVE SUMMARY" in response:
            start = response.find("EXECUTIVE SUMMARY")
            end = response.find("\n\n", start + 100)
            summary = response[start:end if end != -1 else start + 500]
        else:
            summary = response[:500] + "..."
        
        return {
            "summary": summary,
            "quality_score": quality,
            "key_insights": self._extract_insights_for_memory(response)
        }
