# team_icp/agents/competitor.py
"""
Level 4 Competitor Intelligence Agent - Modular Architecture Version
"""

from typing import Dict, Any, List
from datetime import datetime
import re
from core.standard_agent_v4 import StandardAgentNodeV4
from ..prompts.competitor_prompts import CompetitorPrompts


class CompetitorAgent(StandardAgentNodeV4):
    """
    Competitive Intelligence Agent - Level 4 with modular capabilities
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Competitive Intelligence Analyst",
            role_prompt=CompetitorPrompts.get_role_prompt(),
            target_quality=0.75,
            require_human_review_below=0.60
        )
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate competitor analysis using enhanced prompts"""
        psychological_insights = self._extract_psychological_insights(context)
        
        analysis_template = CompetitorPrompts.get_analysis_template()
        enhanced_context = context
        if psychological_insights:
            enhanced_context = f"{context}\n\nPREVIOUS PSYCHOLOGICAL INSIGHTS:\n{psychological_insights}"
        
        if memories:
            memory_context = "\n\nRELEVANT PAST ANALYSES:\n"
            memory_context += "\n---\n".join([m.get("content", "")[:500] for m in memories[:3]])
            enhanced_context += memory_context
        
        complete_prompt = analysis_template.format(task=task, context=enhanced_context)
        response = llm.invoke(complete_prompt)
        
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on competitive analysis quality"""
        reflection_criteria = CompetitorPrompts.get_reflection_criteria()
        reflection_prompt = f"{reflection_criteria}\n\nTASK: {task}\n\nRESPONSE:\n{response[:2000]}...\n\nCRITIQUE:"
        
        critique_response = llm.invoke(reflection_prompt)
        critique_text = critique_response.content if hasattr(critique_response, 'content') else str(critique_response)
        
        lines = critique_text.strip().split('\n')
        score = 0.70
        try:
            score_match = re.search(r'(\d*\.?\d+)', lines[-1])
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))
        except:
            pass
        
        return {"critique": '\n'.join(lines[:-1]), "score": score}
    
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract competitive patterns for future use"""
        return {
            "competitors_identified": self._extract_competitors(response),
            "positioning_gaps": self._extract_gaps(response),
            "attack_vectors": self._extract_vectors(response),
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        return {
            "summary": f"Identified competitive landscape with {quality:.2f} strategic depth",
            "key_competitors": self._extract_competitors(response)[:3],
            "main_opportunity": self._extract_main_opportunity(response),
            "quality_score": quality
        }
    
    def _extract_psychological_insights(self, context: str) -> str:
        if "INSIGHTS FROM OTHER AGENTS" in context:
            try:
                insights_section = context.split("INSIGHTS FROM OTHER AGENTS")[1]
                if "Psychological" in insights_section:
                    psych_end = insights_section.find("\n\n")
                    return insights_section[:psych_end if psych_end != -1 else 500]
            except:
                pass
        return ""
    
    def _extract_competitors(self, response: str) -> List[str]:
        competitors = []
        lines = response.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ["competitor", "compete", "rival"]):
                competitors.append(line.strip()[:100])
        return competitors[:5]
    
    def _extract_gaps(self, response: str) -> List[str]:
        gaps = []
        keywords = ["gap", "opportunity", "weakness", "missing"]
        for keyword in keywords:
            if keyword in response.lower():
                gaps.append(f"{keyword.capitalize()} identified")
        return gaps[:3]
    
    def _extract_vectors(self, response: str) -> List[str]:
        vectors = []
        keywords = ["attack", "position", "differentiate", "strategy"]
        for keyword in keywords:
            if keyword in response.lower():
                vectors.append(f"{keyword.capitalize()} vector")
        return vectors[:3]
    
    def _extract_main_opportunity(self, response: str) -> str:
        if "opportunity" in response.lower():
            lines = response.split('\n')
            for line in lines:
                if "opportunity" in line.lower():
                    return line.strip()[:200]
        return "Competitive analysis reveals strategic opportunities"