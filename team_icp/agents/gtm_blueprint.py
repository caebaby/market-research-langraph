# team_icp/agents/gtm_blueprint.py
"""
Level 4 GTM Blueprint Agent - Modular Architecture Version
"""

from typing import Dict, Any, List
from datetime import datetime
import re
from core.standard_agent_v4 import StandardAgentNodeV4
from ..prompts.gtm_blueprint_prompts import GTMBlueprintPrompts


class GTMBlueprintAgent(StandardAgentNodeV4):
    """
    GTM Blueprint Synthesis Agent - Level 4 with modular capabilities
    """
    
    def __init__(self):
        super().__init__(
            agent_name="GTM Blueprint Strategist",
            role_prompt=GTMBlueprintPrompts.get_role_prompt(),
            target_quality=0.85,
            require_human_review_below=0.75
        )
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate comprehensive GTM blueprint using all insights"""
        all_insights = self._collect_all_insights_from_context(context)
        business_context = self._extract_business_context(context)
        
        synthesis_template = GTMBlueprintPrompts.get_synthesis_template()
        complete_prompt = synthesis_template.format(
            all_insights=all_insights,
            task=task,
            business_context=business_context
        )
        
        response = llm.invoke(complete_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on GTM blueprint quality"""
        quality_criteria = GTMBlueprintPrompts.get_quality_criteria()
        reflection_prompt = f"{quality_criteria}\n\nTASK: {task}\n\nBLUEPRINT:\n{response[:3000]}...\n\nCRITIQUE:"
        
        critique_response = llm.invoke(reflection_prompt)
        critique_text = critique_response.content if hasattr(critique_response, 'content') else str(critique_response)
        
        lines = critique_text.strip().split('\n')
        score = 0.80
        try:
            score_match = re.search(r'(\d*\.?\d+)', lines[-1])
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))
        except:
            pass
        
        return {"critique": '\n'.join(lines[:-1]), "score": score}
    
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract GTM strategy patterns for future use"""
        return {
            "strategy_components": self._extract_strategy_components(response),
            "key_recommendations": self._extract_recommendations(response),
            "success_metrics": self._extract_metrics(response),
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create final synthesis insights"""
        return {
            "summary": f"Created comprehensive GTM blueprint with {quality:.2f} strategic coherence",
            "key_strategies": self._extract_strategy_components(response)[:3],
            "immediate_actions": self._extract_immediate_actions(response),
            "quality_score": quality
        }
    
    def _collect_all_insights_from_context(self, context: str) -> str:
        insights_parts = []
        
        if "BUSINESS CONTEXT" in context:
            insights_parts.append(f"=== BUSINESS CONTEXT ===\n{self._extract_business_context(context)}\n")
        
        if "INSIGHTS FROM OTHER AGENTS" in context:
            insights_section = context.split("INSIGHTS FROM OTHER AGENTS")[1]
            insights_parts.append(f"=== AGENT INSIGHTS ===\n{insights_section}\n")
        
        return "\n".join(insights_parts) if insights_parts else context
    
    def _extract_business_context(self, context: str) -> str:
        if "BUSINESS CONTEXT ===" in context:
            try:
                parts = context.split("BUSINESS CONTEXT ===")
                if len(parts) > 1:
                    return parts[1].split("===")[0].strip()[:1000]
            except:
                pass
        return context[:500]
    
    def _extract_strategy_components(self, response: str) -> List[str]:
        components = []
        keywords = ["positioning", "messaging", "channel", "pricing", "launch"]
        for keyword in keywords:
            if keyword in response.lower():
                components.append(f"{keyword.capitalize()} strategy")
        return components[:5]
    
    def _extract_recommendations(self, response: str) -> List[str]:
        recs = []
        lines = response.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ["recommend", "should", "must"]):
                recs.append(line.strip()[:150])
        return recs[:5]
    
    def _extract_metrics(self, response: str) -> List[str]:
        metrics = []
        keywords = ["metric", "kpi", "measure", "target", "goal"]
        for keyword in keywords:
            if keyword in response.lower():
                metrics.append(f"{keyword.upper()} identified")
        return metrics[:3]
    
    def _extract_immediate_actions(self, response: str) -> List[str]:
        actions = []
        if "immediate" in response.lower() or "next step" in response.lower():
            lines = response.split('\n')
            for line in lines:
                if any(word in line.lower() for word in ["immediate", "tomorrow", "first", "next"]):
                    actions.append(line.strip()[:100])
        return actions[:3]