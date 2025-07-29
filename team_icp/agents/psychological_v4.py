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
        role_prompt = "You are an expert psychological researcher specializing in uncovering deep customer insights that drive purchasing decisions."
        
        super().__init__(
            agent_name="Psychological Analyst V4",
            role_prompt=role_prompt,
            target_quality=0.80,
            require_human_review_below=0.60
        )
        
        print(f"[L4 CHECK] Agent initialized: {self.agent_name}")
        print(f"[L4 CHECK] Target quality: {self.target_quality}")
        print(f"[L4 CHECK] HITL threshold: {self.review_threshold}")
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate psychological + conversion intelligence analysis"""
    
        # Build memory patterns
        memory_patterns = ""
        if memories:
            memory_patterns = "\n\nRELEVANT PAST ANALYSES:\n"
            for memory in memories[:3]:
                content = memory.get("content", "")
                quality = memory.get("quality", 0)
                memory_patterns += f"\n[Quality: {quality:.2f}] {content[:200]}...\n"
        else:
            memory_patterns = "No previous patterns available"
    
        # FIRST: Deep psychological analysis
        psych_prompt = PsychologicalPrompts.get_psychological_analysis_prompt()
        formatted_psych_prompt = psych_prompt.format(
            business_context=context,
            memory_patterns=memory_patterns
        )
    
        print(f"[DEBUG] Running psychological analysis...")
        psychological_result = llm.invoke(formatted_psych_prompt)
    
        # SECOND: Conversion intelligence using psychological insights
        conversion_prompt = PsychologicalPrompts.get_conversion_intelligence_prompt()  # Need to add this method
        formatted_conversion_prompt = conversion_prompt.format(
            psychological_analysis=psychological_result.content,
            business_context=context
        )
    
        print(f"[DEBUG] Running conversion intelligence analysis...")
        conversion_result = llm.invoke(formatted_conversion_prompt)
    
        # COMBINE both analyses
        combined_analysis = f"""# DEEP PSYCHOLOGICAL INTELLIGENCE ANALYSIS

    {psychological_result.content}

    ---

    # CONVERSION INTELLIGENCE APPLICATION

    {conversion_result.content}"""
    
        return combined_analysis
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Evaluate psychological analysis quality"""
        reflection_prompt = """Evaluate this psychological analysis on these criteria:
        1. Depth of unconscious insights (0-1)
        2. Use of multiple frameworks (0-1)
        3. Accuracy of voice capture (0-1)
        4. Actionability for business (0-1)
        Score 0.0-1.0 on last line."""
        
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
