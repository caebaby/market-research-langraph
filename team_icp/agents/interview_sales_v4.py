# team_icp/agents/interview_sales_v4.py
"""
Level 4 Sales Interview Agent - Extracts buying psychology and objections through realistic interviews
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from core.standard_agent_v4 import StandardAgentNodeV4
from team_icp.prompts.interview_sales_v4 import SalesInterviewPrompts


class SalesInterviewAgentV4(StandardAgentNodeV4):
    """
    Creates 3 sales-focused interviews revealing objections, buying criteria, and decision psychology.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Sales Intelligence Interview Specialist",
            role_prompt="""You are an expert at conducting sales discovery interviews that reveal
buying psychology, objections, and decision criteria. You create realistic sales conversations
that uncover what prospects need to know and believe to make a purchase.""",
            target_quality=0.75,
            require_human_review_below=0.6
        )
        
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate sales interview simulations"""
        
        # Extract psychological insights if available
        psychological_insights = self._extract_psychological_insights(context)
        if not psychological_insights:
            psychological_insights = context
    
        # Get the sales interview prompt
        try:
            interview_prompt = SalesInterviewPrompts.get_sales_interviews(psychological_analysis=psychological_insights)
            print(f"[{self.agent_name}] Using sales interview prompts")
        except Exception as e:
            print(f"[{self.agent_name}] Prompt error: {e}, using fallback")
            interview_prompt = self._create_fallback_prompt(context)
    
        # Web search for validation if needed
        if self.web_search and "objection" in task.lower():
            search_query = f"{self._extract_industry(context)} sales objections buying criteria"
            search_results = self.web_search(search_query, num_results=5)
            if search_results and "Error" not in search_results:
                interview_prompt += f"\n\nCOMMON OBJECTIONS FROM WEB:\n{search_results[:1000]}"
    
        # Generate interviews
        print(f"[{self.agent_name}] Creating 3 sales intelligence interviews...")
        response = llm.invoke(interview_prompt)
        output = response.content if hasattr(response, 'content') else str(response)
        
        return output
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Evaluate sales interview quality"""
        
        reflection_prompt = f"""Evaluate these sales interviews for effectiveness:

INTERVIEWS TO EVALUATE:
{response[:4000]}...

CRITERIA:
1. Problem/Pain Extraction - Do we understand their real problems?
2. Objection Discovery - Are hidden objections revealed?
3. Buying Criteria - Is decision process clear?
4. Authenticity - Natural sales conversation flow?
5. Actionability - Can sales team use these insights?

End with OVERALL_SCORE: [0.0-1.0]"""
        
        reflection_result = llm.invoke(reflection_prompt).content
        score = self._parse_reflection_score(reflection_result)
        
        return {
            "critique": reflection_result,
            "score": score
        }
    
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract sales patterns for future use"""
        
        insights = {
            "common_objections": [],
            "buying_triggers": [],
            "decision_criteria": [],
            "pain_points": [],
            "solution_beliefs": []
        }
        
        # Extract objections
        objection_patterns = [
            r"I need to think about it",
            r"too expensive",
            r"not the right time",
            r"need to check with",
            r"tried before and"
        ]
        
        for pattern in objection_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                insights["common_objections"].append(pattern)
        
        # Extract pain points
        if "hours a week" in response:
            insights["pain_points"].append("Time/workload issues")
        if "can't scale" in response or "bottleneck" in response:
            insights["pain_points"].append("Scaling challenges")
            
        return insights
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Share sales intelligence with other agents"""
        
        return {
            "summary": f"Conducted 3 sales interviews revealing objections and buying criteria. Quality: {quality:.2f}",
            "key_objections": self._extract_objections(response),
            "buying_criteria": self._extract_buying_criteria(response),
            "pain_intensity": self._assess_pain_intensity(response),
            "quality_score": quality
        }
    
    # Helper methods
    def _extract_psychological_insights(self, context: str) -> str:
        """Same as psychological interview agent"""
        if self.state and "shared_insights" in self.state:
            shared = self.state["shared_insights"]
            for agent_name in ["Psychological Analyst V4", "psychological"]:
                if agent_name in shared:
                    return str(shared[agent_name].get("summary", ""))
        return ""
    
    def _extract_industry(self, context: str) -> str:
        """Extract industry for targeted search"""
        context_lower = context.lower()
        if 'coach' in context_lower:
            return 'executive coaching'
        elif 'tech' in context_lower:
            return 'technology'
        return 'business'
    
    def _create_fallback_prompt(self, context: str) -> str:
        """Fallback if main prompt fails"""
        return f"""Create 3 sales discovery interviews for {context}.
        
Focus on:
1. Current problems and pain intensity
2. What they've tried before
3. Objections and concerns
4. What they need to believe to buy
5. Decision-making process

Make conversations realistic with natural sales dialogue."""
    
    def _parse_reflection_score(self, reflection_text: str) -> float:
        """Extract score from reflection"""
        patterns = [
            r'OVERALL_SCORE:\s*([0-9.]+)',
            r'Score:\s*([0-9.]+)',
            r'\b([0-9]\.[0-9]+)\b'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, reflection_text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        return 0.7  # Default
    
    def _extract_objections(self, response: str) -> List[str]:
        """Extract main objections from interviews"""
        objections = []
        
        objection_markers = [
            "but", "however", "concern", "worry", "problem with",
            "not sure", "hesitant", "need to think"
        ]
        
        lines = response.split('\n')
        for line in lines:
            if any(marker in line.lower() for marker in objection_markers):
                obj
