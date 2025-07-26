# team_icp/agents/competitor.py

from typing import Dict, Any, List
import json
import re
from core.standard_agent import StandardAgentNode
from ..prompts.competitor_prompts import CompetitorPrompts


class CompetitorAgent(StandardAgentNode):
    """
    Competitive Intelligence Agent that analyzes market competition
    to identify positioning opportunities and differentiation strategies.
    
    Level 4 Features:
    - Reflection and quality scoring
    - Tool usage (web search)
    - Inter-agent communication (reads psychological insights)
    - HITL awareness
    - Future-ready for memory integration
    """
    
    def __init__(self):
        agent_name = "Competitive Intelligence Analyst"
        
        # Get role prompt from dedicated prompts file
        role_prompt = CompetitorPrompts.get_role_prompt()
        
        super().__init__(
            agent_name=agent_name,
            role_prompt=role_prompt,
            target_quality=0.75  # Can be adjusted based on quality requirements
        )
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override to handle web search BEFORE calling parent.
        Ensures proper state management and tool usage.
        """
        print(f"[CompetitorAgent] Starting analysis")
        print(f"[CompetitorAgent] Business context present: {bool(state.get('business_context'))}")
        print(f"[CompetitorAgent] State keys: {list(state.keys())}")
        
        # Store tool executor for this request
        self._temp_tool_executor = state.get("tool_executor")
        print(f"[CompetitorAgent] Tool executor available: {self._temp_tool_executor is not None}")
        
        # Execute competitor research if we have tools and valid context
        if self._temp_tool_executor and state.get("business_context", "").strip():
            self._perform_competitor_research(state)
        else:
            print(f"[CompetitorAgent] Skipping web search - no tools or context")
        
        # Call parent's __call__ method
        result = super().__call__(state)
        
        # Clean up temp storage
        self._temp_tool_executor = None
        
        # CRITICAL: Ensure we return a proper dictionary
        return self._ensure_valid_state_return(result, state)
    
    def _perform_competitor_research(self, state: Dict[str, Any]) -> None:
        """
        Perform web searches for competitor intelligence.
        Updates state with search results.
        """
        business_context = state.get("business_context", "")
        
        # Get search queries from prompts
        search_query_templates = CompetitorPrompts.get_search_queries()
        
        # Format queries with business context (limit to 3 for speed)
        search_queries = [
            q.format(business_context=business_context) 
            for q in search_query_templates[:3]
        ]
        
        # Execute searches and collect results
        search_results = []
        for query in search_queries:
            try:
                print(f"[CompetitorAgent] Searching: {query}")
                results = self._temp_tool_executor.execute("web_search", {"query": query})
                
                if results:
                    search_results.append(f"Results for '{query}':\n{results}\n")
                    print(f"[CompetitorAgent] Search successful - {len(str(results))} chars")
                else:
                    print(f"[CompetitorAgent] No results for: {query}")
                    
            except Exception as e:
                print(f"[CompetitorAgent] Search error for '{query}': {str(e)}")
                # Continue with other searches even if one fails
        
        # Add search results to master context if we found anything
        if search_results:
            additional_context = "\n\nCOMPETITOR RESEARCH RESULTS:\n" + "\n".join(search_results)
            state["master_context"] = state.get("master_context", "") + additional_context
            print(f"[CompetitorAgent] Added {len(search_results)} search results to context")
    
    def _ensure_valid_state_return(self, result: Any, original_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure we always return a valid state dictionary.
        Handles various return types from parent class.
        """
        if isinstance(result, dict):
            # Ensure all original state fields are preserved
            for key in original_state:
                if key not in result:
                    result[key] = original_state[key]
            return result
            
        elif isinstance(result, str):
            # If parent returned a string, treat it as the output
            print(f"[CompetitorAgent] Converting string result to state dict")
            original_state["current_output"] = result
            original_state["agent_name"] = self.agent_name
            return original_state
            
        else:
            # Unexpected type - log and handle gracefully
            print(f"[CompetitorAgent] ERROR: Unexpected result type: {type(result)}")
            original_state["current_output"] = str(result) if result else "Analysis completed but no output generated"
            original_state["agent_name"] = self.agent_name
            original_state["quality_score"] = 0.0  # Flag for review
            original_state["requires_human_review"] = True
            original_state["review_reason"] = "Unexpected output format"
            return original_state
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """
        Generate competitor analysis using enhanced prompts and inter-agent insights.
        """
        # Extract psychological insights from previous agent
        psychological_insights = self._extract_psychological_insights(context)
        
        # Get the analysis template from prompts
        analysis_template = CompetitorPrompts.get_analysis_template()
        
        # Enhance context with psychological insights
        enhanced_context = context
        if psychological_insights:
            enhanced_context = f"{context}\n\nPREVIOUS PSYCHOLOGICAL INSIGHTS:\n{psychological_insights}"
        
        # Include memories if available (future Level 4 feature)
        if memories:
            memory_context = "\n\nRELEVANT PAST COMPETITOR ANALYSES:\n"
            memory_context += "\n---\n".join([m.get("content", "") for m in memories[:3]])
            enhanced_context += memory_context
        
        # Build the complete prompt
        complete_prompt = f"{self.role_prompt}\n\n{analysis_template.format(task=task, context=enhanced_context)}"
        
        # Generate response
        response = llm.invoke(complete_prompt)
        
        # Extract content properly
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    
    def _extract_psychological_insights(self, context: str) -> str:
        """
        Extract psychological insights from context or shared state.
        Supports inter-agent communication.
        """
        insights = []
        
        # Method 1: Look for insights in context (StandardAgentNode includes them)
        if "INSIGHTS FROM OTHER AGENTS" in context:
            try:
                insights_section = context.split("INSIGHTS FROM OTHER AGENTS")[1]
                
                # Extract psychological analyst section
                if "Psychological Analyst" in insights_section:
                    psych_start = insights_section.find("Psychological Analyst")
                    psych_end = insights_section.find("\n\n", psych_start)
                    
                    if psych_end == -1:
                        psych_insights = insights_section[psych_start:]
                    else:
                        psych_insights = insights_section[psych_start:psych_end]
                    
                    insights.append(psych_insights)
            except Exception as e:
                print(f"[CompetitorAgent] Error extracting insights from context: {e}")
        
        # Method 2: Check for specific psychological patterns in context
        psychological_markers = [
            "unconscious", "fear", "desire", "identity", "status",
            "belonging", "psychological", "emotional", "cognitive"
        ]
        
        for marker in psychological_markers:
            if marker in context.lower():
                # Found psychological content in context
                insights.append("Detected psychological analysis in context")
                break
        
        # Return combined insights or default message
        if insights:
            return "\n".join(insights)
        else:
            return "No psychological insights available - conducting independent competitive analysis"
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """
        Reflect on the quality of the competitive analysis.
        Uses strategic criteria from prompts.
        """
        # Get reflection criteria from prompts
        reflection_criteria = CompetitorPrompts.get_reflection_criteria()
        
        reflection_prompt = f"""{reflection_criteria}

TASK: {task}

RESPONSE TO EVALUATE:
{response[:2000]}...

Provide a detailed critique addressing each criterion.
Then on the LAST LINE ONLY, output a score from 0.0 to 1.0.

CRITIQUE:"""
        
        # Get critique from LLM
        critique_response = llm.invoke(reflection_prompt)
        critique_text = critique_response.content if hasattr(critique_response, 'content') else str(critique_response)
        
        # Parse the critique and extract score
        try:
            lines = critique_text.strip().split('\n')
            
            # The score should be on the last line
            last_line = lines[-1].strip() if lines else ""
            
            # Join all other lines as the critique
            critique_content = '\n'.join(lines[:-1]) if len(lines) > 1 else critique_text
            
            # Extract numeric score using regex
            score_match = re.search(r'(\d*\.?\d+)', last_line)
            
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
                print(f"[CompetitorAgent] Quality score: {score}")
            else:
                print(f"[CompetitorAgent] No score found in: '{last_line}' - defaulting to 0.0")
                score = 0.0
                
        except Exception as e:
            print(f"[CompetitorAgent] Error parsing reflection: {e}")
            critique_content = critique_text
            score = 0.0
        
        return {
            "critique": critique_content,
            "score": score
        }
