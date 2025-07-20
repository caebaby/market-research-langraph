# team_icp/agents/psychological.py

from typing import Dict, Any, List
from core.standard_agent import StandardAgentNode
from team_icp.prompts.research_prompts import ICPResearchPrompts

class PsychologicalAgent(StandardAgentNode):
    """
    Hybrid Psychological Agent that combines:
    - StandardAgentNode infrastructure (memory, tools, communication, HITL)
    - Full sophisticated prompting from ICPResearchPrompts
    - Custom prompt injection for maximum quality
    """
    
    def __init__(self):
        # Basic role for StandardAgent's general use
        agent_name = "Psychological Analyst"
        
        basic_role = """You are an expert psychological researcher specializing in uncovering deep customer insights 
that drive purchasing decisions. Your analysis goes beyond surface-level demographics to reveal the 
unconscious motivations, hidden fears, and unspoken desires of the target audience."""
        
        # Lower threshold based on your testing
        target_quality = 0.75
        
        # Store the sophisticated prompts for later use
        self.sophisticated_prompts = ICPResearchPrompts()
        
        super().__init__(
            agent_name=agent_name,
            role_prompt=basic_role,  # Basic version for general StandardAgent use
            target_quality=target_quality
        )
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """
        Override to use the sophisticated ICPResearchPrompts while maintaining StandardAgent structure
        """
        print(f"[{self.agent_name}] Using sophisticated psychological frameworks...")
        
        # Format memories to match original structure
        memory_patterns = self._format_memories_detailed(memories)
        
        # Extract business context from the full context
        # StandardAgent provides context that includes peer insights
        # We need to separate that out
        business_context = self._extract_business_context(context)
        
        # Get the full sophisticated prompt
        sophisticated_prompt = self.sophisticated_prompts.get_psychological_analysis_prompt()
        
        # DEBUG: Check prompt size
        print(f"DEBUG: Sophisticated prompt length: {len(sophisticated_prompt)} chars")
        
        # Format it with our context
        formatted_prompt = sophisticated_prompt.format(
            business_context=business_context,
            memory_patterns=memory_patterns
        )
        
        # DEBUG: Check formatted prompt
        print(f"DEBUG: Formatted prompt length: {len(formatted_prompt)} chars")
        print(f"DEBUG: Prompt preview: {formatted_prompt[:200]}...")
        
        # Add any strategic insights from learning system if available
        if "INSIGHTS FROM OTHER AGENTS" in context:
            formatted_prompt += f"\n\nCOLLABORATIVE INTELLIGENCE:\n{context.split('INSIGHTS FROM OTHER AGENTS')[1]}"
        
        # Add the specific task
        formatted_prompt += f"\n\nSPECIFIC ANALYSIS TASK:\n{task}"
        
        # Check if we should use tools first
        if self._should_research_first(task, business_context):
            # Return tool call
            return '{"tool_name": "web_search", "tool_input": "' + self._create_search_query(business_context) + '"}'
        
        # Otherwise proceed with analysis
        response = llm.invoke(formatted_prompt)
        actual_response = response.content if hasattr(response, 'content') else str(response)
        
        # DEBUG: Check response
        print(f"DEBUG: Response length: {len(actual_response)} chars")
        print(f"DEBUG: Response starts with: {actual_response[:300]}...")
        
        return actual_response
    
    def _format_memories_detailed(self, memories: List) -> str:
        """Format memories to match the original sophisticated structure"""
        if not memories:
            return "No previous analyses found. This is a fresh analysis."
        
        formatted = "MEMORY-ENHANCED PATTERNS FROM PREVIOUS ANALYSES:\n\n"
        
        for i, memory in enumerate(memories[:5], 1):
            content = memory.get('content', '')
            metadata = memory.get('metadata', {})
            score = metadata.get('score', 'N/A')
            
            formatted += f"Memory {i} (Quality Score: {score}):\n"
            formatted += f"{content[:300]}...\n"
            formatted += "-" * 50 + "\n"
        
        formatted += "\nKEY PATTERNS TO REINFORCE: Look for similar patterns in this analysis."
        
        return formatted
    
    def _extract_business_context(self, full_context: str) -> str:
        """Extract just the business context from StandardAgent's full context"""
        # If context has peer insights, extract just the business part
        if "INSIGHTS FROM OTHER AGENTS" in full_context:
            return full_context.split("INSIGHTS FROM OTHER AGENTS")[0].strip()
        return full_context
    
    def _should_research_first(self, task: str, context: str) -> bool:
        """Determine if we need web research before psychological analysis"""
        research_triggers = [
            "current market",
            "competitor",
            "industry trends",
            "recent changes",
            "market research"
        ]
        
        combined = f"{task} {context}".lower()
        return any(trigger in combined for trigger in research_triggers)
    
    def _create_search_query(self, context: str) -> str:
        """Create focused search query for psychological research"""
        # Extract key terms from context
        if len(context) > 100:
            context = context[:100]
        
        return f"{context} customer psychology behavior patterns"
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """
        Override reflection to use criteria specific to psychological analysis
        """
        print(f"[{self.agent_name}] Evaluating psychological analysis quality...")
        
        # DEBUG: Check what we're evaluating
        print(f"DEBUG: Evaluating response of {len(response)} chars")
        
        reflection_prompt = f"""
As a psychological analysis quality expert, evaluate this response on these SPECIFIC criteria:

1. Psychological Depth (0-1): Are unconscious patterns and hidden motivations revealed?
2. Framework Coverage (0-1): Are multiple psychological frameworks properly applied?
3. Visceral Accuracy (0-1): Would the target customer feel deeply understood?
4. Contradiction Analysis (0-1): Are internal conflicts and contradictions exposed?
5. Voice Authenticity (0-1): Does it capture how they actually speak/think?
6. Actionability (0-1): Can these insights drive marketing/product decisions?
7. Non-Obviousness (0-1): Are the insights surprising and non-surface-level?

TASK: {task}

RESPONSE TO EVALUATE (first 2000 chars):
{response[:2000]}...

Provide a brief critique addressing each criterion.
Then on the LAST LINE ONLY, give an overall score from 0.0 to 1.0.
Remember: {self.target_quality} or higher is considered enterprise-ready.

CRITIQUE:"""
        
        critique_result = llm.invoke(reflection_prompt).content.strip()
        
        # DEBUG: Check critique
        print(f"DEBUG: Full critique result:\n{critique_result}")
        print(f"DEBUG: Last line (should be score): {critique_result.split(chr(10))[-1]}")
        
        try:
            lines = critique_result.split('\n')
            critique_text = '\n'.join(lines[:-1])
            score = float(lines[-1].strip())
            score = max(0.0, min(1.0, score))
        except (ValueError, IndexError):
            critique_text = "Error parsing critique"
            score = 0.5
            
        return {
            "critique": critique_text,
            "score": score
        }
