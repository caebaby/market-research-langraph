# team_icp/agents/gtm_blueprint.py
# FINAL FIXED VERSION - Override parent's _format_shared_insights method

from typing import Dict, Any, List
import json
import re
from core.standard_agent import StandardAgentNode
from ..prompts.gtm_blueprint_prompts import GTMBlueprintPrompts


class GTMBlueprintAgent(StandardAgentNode):
    """
    GTM Blueprint Agent that synthesizes all insights into comprehensive strategy.
    """
    
    def __init__(self):
        agent_name = "GTM Blueprint Strategist"
        role_prompt = GTMBlueprintPrompts.get_role_prompt()
        
        super().__init__(
            agent_name=agent_name,
            role_prompt=role_prompt,
            target_quality=0.85
        )
    
    def _format_shared_insights(self, shared_insights: Dict[str, Any]) -> str:
        """
        Override parent's method to handle both string and dict formats in shared_insights.
        """
        if not shared_insights:
            return ""
        
        formatted = "\n\nINSIGHTS FROM OTHER AGENTS:\n"
        formatted += "=" * 50 + "\n"
        
        for agent_name, insights in shared_insights.items():
            # Handle different data types
            if isinstance(insights, dict):
                # Extract quality score if available
                quality_score = insights.get('quality_score', 'N/A')
                if isinstance(quality_score, (int, float)):
                    formatted += f"From {agent_name} (Quality Score: {quality_score:.2f}):\n"
                else:
                    formatted += f"From {agent_name}:\n"
                
                # Extract content
                content = insights.get('summary', '') or insights.get('content', '') or str(insights)
            elif isinstance(insights, str):
                # If it's a string, use it directly
                formatted += f"From {agent_name}:\n"
                content = insights
            else:
                # Convert to string if it's something else
                formatted += f"From {agent_name}:\n"
                content = str(insights)
            
            # Add the content
            if content:
                formatted += f"{content[:1000]}...\n" if len(content) > 1000 else f"{content}\n"
            formatted += "-" * 30 + "\n"
        
        return formatted
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process state and synthesize all insights into GTM blueprint.
        """
        print(f"[GTMBlueprintAgent] Starting synthesis")
        print(f"[GTMBlueprintAgent] Available insights: {list(state.get('shared_insights', {}).keys())}")
        
        # Collect all insights from other agents
        all_insights = self._collect_all_insights(state)
        print(f"[GTMBlueprintAgent] Collected insights from {len(state.get('shared_insights', {}))} agents")
        
        # Add insights to master context
        if all_insights:
            current_context = state.get("master_context", "")
            state["master_context"] = f"{current_context}\n\n{all_insights}"
        
        try:
            # Call parent's __call__ method
            result = super().__call__(state)
            
            # Ensure result is a dict
            if not isinstance(result, dict):
                print(f"[GTMBlueprintAgent] WARNING: Parent returned {type(result)}, converting to dict")
                result = {"current_output": str(result)}
            
            # Ensure minimum length for comprehensive strategy
            if result.get("current_output"):
                output_length = len(result["current_output"])
                print(f"[GTMBlueprintAgent] Generated {output_length} characters")
                
                if output_length < 2500:
                    print(f"[GTMBlueprintAgent] Output too short, requesting expansion")
                    result["requires_human_review"] = True
                    result["review_reason"] = f"GTM Blueprint too brief ({output_length} chars, need 2500+)"
            
            # Ensure all state fields are preserved
            for key in state:
                if key not in result:
                    result[key] = state[key]
            
            return result
            
        except Exception as e:
            print(f"[GTMBlueprintAgent] Error in synthesis: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a valid state dict even on error
            error_state = state.copy()
            error_state["current_output"] = f"GTM Blueprint generation failed: {str(e)}"
            error_state["quality_score"] = 0.0
            error_state["requires_human_review"] = True
            error_state["review_reason"] = f"GTM Blueprint error: {str(e)}"
            error_state["agent_name"] = self.agent_name
            return error_state
    
    def _collect_all_insights(self, state: Dict[str, Any]) -> str:
        """
        Collect and format all insights from other agents.
        """
        insights_parts = []
        
        # Get from shared_insights
        shared_insights = state.get("shared_insights", {})
        
        # Get from result
        result = state.get("result", {})
        
        # Priority order for synthesis
        agent_mapping = {
            "psychological": "PSYCHOLOGICAL ANALYSIS",
            "Psychological Analyst": "PSYCHOLOGICAL ANALYSIS",
            "voice": "VOICE OF CUSTOMER",
            "Voice of Customer Mind Reader": "VOICE OF CUSTOMER",
            "competitor": "COMPETITIVE INTELLIGENCE",
            "Competitive Intelligence Analyst": "COMPETITIVE INTELLIGENCE"
        }
        
        # Collect from shared insights
        for key, value in shared_insights.items():
            label = agent_mapping.get(key, key.upper())
            
            if isinstance(value, dict):
                content = value.get('summary', '') or value.get('content', '') or str(value)
            elif isinstance(value, str):
                content = value
            else:
                content = str(value)
            
            if content and len(content) > 50:
                insights_parts.append(f"\n=== {label} ===\n{content[:2000]}\n")
        
        # Also check result dict for any missing insights
        for key in ["psychological", "voice", "competitor"]:
            if key in result and key not in str(insights_parts):
                content = result[key]
                if isinstance(content, str) and len(content) > 50:
                    label = agent_mapping.get(key, key.upper())
                    insights_parts.append(f"\n=== {label} ===\n{content[:2000]}\n")
        
        # Include business context
        if state.get("business_context"):
            insights_parts.insert(0, f"=== BUSINESS CONTEXT ===\n{state['business_context']}\n")
        
        combined = "\n".join(insights_parts) if insights_parts else ""
        print(f"[GTMBlueprintAgent] Combined insights length: {len(combined)} chars")
        return combined
    
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """
        Generate comprehensive GTM blueprint using all insights.
        """
        # Get the synthesis template
        synthesis_template = GTMBlueprintPrompts.get_synthesis_template()
        
        # Get all insights from context
        all_insights = context if "===" in context else self._extract_insights_from_context(context)
        
        # Extract business context from the context string
        business_context = "AI platform for financial advisors"
        if "BUSINESS CONTEXT ===" in context:
            try:
                parts = context.split("BUSINESS CONTEXT ===")
                if len(parts) > 1:
                    business_context = parts[1].split("===")[0].strip()[:1000]
            except:
                pass
        elif "Target:" in context:
            try:
                business_context = context.split("Target:")[1].split("\n")[0].strip()
            except:
                pass
        
        # Format the complete prompt
        try:
            complete_prompt = synthesis_template.format(
                all_insights=all_insights,
                task=task,
                business_context=business_context
            )
        except Exception as e:
            print(f"[GTMBlueprintAgent] Error formatting template: {e}")
            complete_prompt = f"""
            Create a comprehensive GTM Blueprint based on these insights:
            
            {all_insights}
            
            Business Context: {business_context}
            Task: {task}
            
            Provide a detailed go-to-market strategy with all required sections.
            """
        
        # Add role prompt
        full_prompt = f"{self.role_prompt}\n\n{complete_prompt}"
        
        # Generate response
        response = llm.invoke(full_prompt)
        
        # Extract content
        if hasattr(response, 'content'):
            return response.content
        else:
            return str(response)
    
    def _extract_insights_from_context(self, context: str) -> str:
        """
        Extract and organize insights from context.
        """
        if not context:
            return "No context available"
        
        # If already formatted with sections, return as is
        if "===" in context:
            return context
        
        # Otherwise return the raw context
        return f"=== CONTEXT ===\n{context}"
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """
        Reflect on GTM blueprint quality with high standards.
        """
        try:
            # Get quality criteria
            quality_criteria = GTMBlueprintPrompts.get_quality_criteria()
            
            reflection_prompt = f"""{quality_criteria}

TASK: {task}

GTM BLUEPRINT TO EVALUATE (first 3000 chars):
{response[:3000]}...

Provide detailed critique for each criterion.
Then on the LAST LINE ONLY, output a score from 0.0 to 1.0.

CRITIQUE:"""
            
            # Get critique
            critique_response = llm.invoke(reflection_prompt)
            critique_text = critique_response.content if hasattr(critique_response, 'content') else str(critique_response)
            
            # Parse score
            lines = critique_text.strip().split('\n')
            last_line = lines[-1].strip() if lines else ""
            critique_content = '\n'.join(lines[:-1]) if len(lines) > 1 else critique_text
            
            # Extract score
            score_match = re.search(r'(\d*\.?\d+)', last_line)
            
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))
                print(f"[GTMBlueprintAgent] Quality score: {score}")
            else:
                print(f"[GTMBlueprintAgent] No score found, defaulting to 0.7")
                score = 0.7
            
            return {
                "critique": critique_content,
                "score": score
            }
            
        except Exception as e:
            print(f"[GTMBlueprintAgent] Error in reflection: {e}")
            return {
                "critique": f"Reflection error: {str(e)}",
                "score": 0.5
            }