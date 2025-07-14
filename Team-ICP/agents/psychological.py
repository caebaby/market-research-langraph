# teams/icp/agents/psychological.py
"""
Level 5 ICP Psychological Agent
Inherits ALL Level 5 capabilities from base agent!
"""

from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic

# Import our Level 5 base template
from core.agents.base_agent import Level5BaseAgent

class Level5PsychologicalAgent(Level5BaseAgent):
    """
    ICP Psychological Analysis Agent with FULL Level 5 capabilities
    
    This agent:
    - ✅ Has persistent memory (from base)
    - ✅ Can decompose goals (from base) 
    - ✅ Selects tools dynamically (from base)
    - ✅ Self-improves (from base)
    - ✅ Communicates with other agents (from base)
    
    We just need to implement the execute_task method!
    """
    
    def __init__(self):
        # Initialize with agent identity
        super().__init__(
            agent_name="ICP_Psychological_Analyst",
            agent_role="Deep psychological and behavioral analysis"
        )
        
        # Set up this agent's specific tools
        self.available_tools = [
            "psychological_frameworks",
            "voice_extraction",
            "belief_archaeology",
            "contradiction_detection"
        ]
        
        # Initialize Claude
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.8,
            max_tokens=4000
        )
    
    async def execute_task(
        self, 
        task: Dict[str, Any], 
        memories: List[Dict], 
        tools: List[str]
    ) -> Dict[str, Any]:
        """
        The actual psychological analysis happens here
        This is the ONLY method we need to implement!
        """
        # Get context from task
        business_context = task.get('context', '')
        
        # Build prompt with memory enhancement
        prompt = self._build_psychological_prompt(business_context, memories)
        
        # Execute analysis
        response = await self.llm.ainvoke(prompt)
        
        # Calculate success score based on response quality
        success_score = self._assess_analysis_quality(response.content)
        
        return {
            "task": task,
            "analysis": response.content,
            "success_score": success_score,
            "tools_used": tools,
            "insights_extracted": self._extract_insights(response.content)
        }
    
    def _build_psychological_prompt(self, context: str, memories: List[Dict]) -> str:
        """Build the psychological analysis prompt"""
        
        # Add memory context if available
        memory_context = ""
        if memories:
            memory_context = "\n\nRELEVANT PAST ANALYSES:\n"
            for memory in memories[:3]:
                insights = memory.get('insights_extracted', [])
                if insights:
                    memory_context += f"- Previous insights: {', '.join(insights[:2])}\n"
        
        return f"""You are a Level 5 Psychological Intelligence Agent analyzing customer psychology.

BUSINESS CONTEXT:
{context}
{memory_context}

Conduct deep psychological analysis using:
1. Jungian Archetypes - What unconscious patterns drive them?
2. Lab Profile - What meta-programs control their decisions?
3. Voice Extraction - What exact words would they use?
4. Belief Archaeology - What hidden beliefs drive behavior?
5. Contradiction Detection - Where do they contradict themselves?

Focus on insights that would make them say "How did you know that about me?"

Provide viscerally accurate psychological insights."""
    
    def _assess_analysis_quality(self, analysis: str) -> float:
        """Assess the quality of the analysis"""
        score = 0.7  # Base score
        
        # Check for framework mentions
        frameworks = ["jungian", "archetype", "meta-program", "belief", "contradiction"]
        for framework in frameworks:
            if framework.lower() in analysis.lower():
                score += 0.05
        
        # Check for depth indicators
        depth_indicators = ["unconscious", "hidden", "underlying", "deeper"]
        for indicator in depth_indicators:
            if indicator in analysis.lower():
                score += 0.03
        
        return min(score, 0.95)
    
    def _extract_insights(self, analysis: str) -> List[str]:
        """Extract key insights from analysis"""
        # Simple extraction - enhance later
        insights = []
        lines = analysis.split('\n')
        for line in lines:
            if len(line) > 50 and any(word in line.lower() for word in ['they', 'their', 'them']):
                insights.append(line.strip())
        return insights[:5]
    
    # ====================================
    # OPTIONAL: Override Level 5 methods for agent-specific behavior
    # ====================================
    
    async def decompose_goal(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Override to add psychological-specific goal decomposition"""
        # For now, use base implementation
        # Later, add sophisticated decomposition
        return await super().decompose_goal(goal)
    
    async def select_tools(self, goal: Dict[str, Any], memories: List[Dict]) -> List[str]:
        """Override to add smart tool selection based on context"""
        # For now, use base implementation
        # Later, add intelligent tool selection
        return await super().select_tools(goal, memories)
