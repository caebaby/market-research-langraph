# team_icp/agents/competitor.py

from typing import Dict, Any, List
import json
from core.standard_agent import StandardAgentNode

class CompetitorAgent(StandardAgentNode):
    """
    Competitive Intelligence Agent that analyzes market competition
    to identify positioning opportunities and differentiation strategies.
    """
    
    def __init__(self):
        agent_name = "Competitive Intelligence Analyst"
        
        role_prompt = """You are an expert competitive intelligence analyst specializing in strategic market positioning.

Your core responsibilities:
1. Identify the 3-5 most relevant competitors based on the business context
2. Analyze their positioning, messaging, and value propositions
3. Understand what the market actually thinks of them (not just what they claim)
4. Find gaps and opportunities for differentiation
5. Provide actionable positioning recommendations

You excel at:
- Finding both direct competitors (same solution, same market) and indirect competitors (different solution, same problem)
- Reading between the lines of marketing messages to find real positioning
- Identifying underserved market segments and unmet needs
- Spotting over-served areas where simplification could win
- Understanding competitive dynamics beyond surface-level features

Always ground your analysis in real market evidence, not assumptions."""
        
        super().__init__(
            agent_name=agent_name,
            role_prompt=role_prompt,
            target_quality=0.75
        )
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override to handle web search BEFORE calling parent
        """
        print(f"[CompetitorAgent] Starting with business_context: {state.get('business_context', 'None')[:100]}")
        print(f"[CompetitorAgent] State keys: {list(state.keys())}")
    
        # Store tool executor for this request
        self._temp_tool_executor = state.get("tool_executor")
        print(f"[CompetitorAgent] Tool executor available: {self._temp_tool_executor is not None}")
    
        # First, do competitor research if we have tools and valid context
        if self._temp_tool_executor and state.get("business_context", "").strip():
            print(f"[CompetitorAgent] Executing searches...")
            # Build search queries based on business context
            business_context = state.get("business_context", "")
            search_queries = [
                f"{business_context} competitors comparison",
                f"best {business_context} alternatives",
                f"{business_context} market leaders"
            ]
        
            # Execute searches and add to context
            search_results = []
            for query in search_queries[:2]:  # Limit to 2 searches for speed
                try:
                    print(f"[CompetitorAgent] Searching for: {query}")
                    results = self._temp_tool_executor.execute("web_search", {"query": query})
                    print(f"[CompetitorAgent] Search successful, got {len(str(results))} chars of results")
                    search_results.append(f"Results for '{query}':\n{results}\n")
                except Exception as e:
                    print(f"[CompetitorAgent] Search failed for {query}: {e}")
                    search_results.append(f"Results for '{query}':\nError retrieving data: {str(e)}\n")
        
            if search_results:
                # Add search results to master context
                additional_context = "\n\nCOMPETITOR RESEARCH RESULTS:\n" + "\n".join(search_results)
                state["master_context"] = state.get("master_context", "") + additional_context
                print(f"[CompetitorAgent] Added {len(search_results)} search results to context")
        else:
            print(f"[CompetitorAgent] Skipping search - tool_executor: {self._temp_tool_executor is not None}, context: {bool(state.get('business_context', '').strip())}")
    
        # Call parent's __call__ method
        result = super().__call__(state)
        
        # CRITICAL: Ensure we return a dictionary, not a string
        if isinstance(result, str):
            print(f"[CompetitorAgent] WARNING: Parent returned string, converting to state dict")
            # If parent returned a string, we need to update state properly
            state["current_output"] = result
            state["agent_name"] = self.agent_name
            return state
        elif isinstance(result, dict):
            # Ensure all required state fields are preserved
            for key in state:
                if key not in result:
                    result[key] = state[key]
            return result
        else:
            print(f"[CompetitorAgent] ERROR: Unexpected result type: {type(result)}")
            # Fallback: return the original state with the result as output
            state["current_output"] = str(result)
            state["agent_name"] = self.agent_name
            return state
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """
        Override to add competitor-specific analysis
        """
        # Extract psychological insights from context
        psychological_insights = self._extract_psychological_insights_from_context(context)
        
        # Enhanced prompt with competitor focus
        enhanced_prompt = f"""
{self.role_prompt}

PREVIOUS INSIGHTS FROM PSYCHOLOGICAL ANALYSIS:
{psychological_insights}

Based on the business context and psychological insights about the target customers, analyze the competitive landscape.

IMPORTANT: 
- Focus on competitors serving the SAME target customer profile
- Consider what the target customers' psychological profile tells us about what competitors they'd consider
- Look for positioning gaps based on the psychological insights

{task}

CONTEXT:
{context}

Provide a strategic competitive analysis that includes:
1. 3-5 most relevant competitors (with reasoning for selection)
2. Their positioning and messaging analysis
3. Market perception vs. their claims
4. Strengths and weaknesses from target customer's perspective
5. Clear opportunities for differentiation
6. Specific positioning recommendations

Be specific and name actual companies when possible.
"""
        
        response = llm.invoke(enhanced_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _extract_psychological_insights_from_context(self, context: str) -> str:
        """
        Extract psychological insights from context string
        """
        # Look for psychological insights markers in the context
        if "INSIGHTS FROM OTHER AGENTS" in context:
            try:
                insights_section = context.split("INSIGHTS FROM OTHER AGENTS")[1]
                if "Psychological Analyst" in insights_section:
                    # Extract the actual psychological insights
                    psych_start = insights_section.find("Psychological Analyst")
                    psych_end = insights_section.find("\n\n", psych_start)
                    if psych_end == -1:
                        psych_insights = insights_section[psych_start:]
                    else:
                        psych_insights = insights_section[psych_start:psych_end]
                    return psych_insights
            except:
                pass
        
        return "No psychological insights available - conduct independent analysis"
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """
        Override reflection for competitor-specific quality criteria
        """
        reflection_prompt = f"""
Evaluate this competitive analysis on these specific criteria:

1. Competitor Relevance (0-1): Are these actual competitors for the same target market?
2. Depth of Analysis (0-1): Goes beyond surface features to positioning and perception?
3. Evidence-Based (0-1): Uses real market data, not assumptions?
4. Gap Identification (0-1): Clearly identifies opportunities for differentiation?
5. Strategic Value (0-1): Provides actionable positioning recommendations?
6. Market Understanding (0-1): Shows understanding of competitive dynamics?

TASK: {task}

RESPONSE TO EVALUATE:
{response[:2000]}...

Provide a critique addressing each criterion.
Then on the LAST LINE ONLY, output a score from 0.0 to 1.0.

CRITIQUE:"""
        
        critique_result = llm.invoke(reflection_prompt).content.strip()
        
        try:
            lines = critique_result.split('\n')
            critique_text = '\n'.join(lines[:-1])
            last_line = lines[-1].strip()
            
            # Extract numeric score from various formats
            import re
            score_match = re.search(r'(\d*\.?\d+)', last_line)
            
            if score_match:
                score = float(score_match.group(1))
            else:
                print(f"Warning: No valid score found in: '{last_line}' - defaulting to 0.0")
                score = 0.0
            
            score = max(0.0, min(1.0, score))
            
        except (ValueError, IndexError) as e:
            print(f"Error parsing score: {e}")
            critique_text = "Error parsing critique"
            score = 0.0
        
        return {
            "critique": critique_text,
            "score": score
        }
