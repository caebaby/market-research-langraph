# core/standard_agent.py

import json
from typing import Dict, Any, List
from datetime import datetime

# These services are expected to be provided by the graph's state
from core.config import Config
from core.memory.interfaces import MemoryInterface
from core.tools.tool_executor import ToolExecutor

class StandardAgentNode:
    """
    The Standard Level 4 Agent Node.
    
    This is the universal template for all specialized agents in the system.
    It provides:
    - Memory access (through state-provided service)
    - Reflection and quality scoring
    - Dynamic tool usage capability
    - Orchestrated communication via shared insights
    - Human-in-the-Loop (HITL) triggers
    - Security through client_id isolation
    
    To create a new agent, inherit from this class and provide:
    1. agent_name: A unique identifier for the agent's role.
    2. role_prompt: The agent's specialized instructions and "job description."
    """
    
    def __init__(self, agent_name: str, role_prompt: str, target_quality: float = 0.9):
        """
        Initializes the standard agent with its identity and role.
        
        Args:
            agent_name: Unique name for this agent (e.g., "Psychological Analyst").
            role_prompt: Detailed instructions defining the agent's expertise and approach.
            target_quality (Optional): The quality score this agent aims to achieve. Defaults to 0.9.
        """
        self.agent_name = agent_name
        self.role_prompt = role_prompt
        self.target_quality = target_quality

    def _get_llm(self, state: Dict[str, Any]):
        """Gets the LLM instance from the state, with a fallback to the central config."""
        llm = state.get("llm")
        if not llm:
            llm = Config.get_llm()
        return llm
        
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """
        Generates a response using the LLM with role, context, and memories.
        The agent can either use a tool (returns JSON) or provide a direct analysis (returns text).
        """
        print(f"[{self.agent_name}] Generating response for task: {task[:50]}...")
        
        memories_str = "\n".join([f"- {m.get('content', '')[:200]}..." for m in memories[:5]])
        if not memories_str:
            memories_str = "No relevant memories found."
            
        prompt = f"""
{self.role_prompt}

You have access to these tools:
- web_search(query: str): Search for current information, competitors, market data.
- code_interpreter(code: str): Run Python for calculations, data analysis, or formatting.

Based on the task, context, and memories, decide your next action:
1. If you need a tool, respond with ONLY a single JSON object: {{"tool_name": "...", "tool_input": {{...}} }}
2. If you can provide a complete analysis, give your detailed response as text.

RELEVANT MEMORIES FROM PAST ANALYSES:
{memories_str}

CURRENT CONTEXT (insights from other agents):
{context}

YOUR TASK:
{task}

Remember: You are {self.agent_name}. Provide insights that match your specialized expertise.
"""
        
        response = llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
        
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """
        Self-evaluates the quality of the generated response.
        Returns a score (0.0-1.0) and a critique.
        """
        print(f"[{self.agent_name}] Reflecting on response quality...")
        
        reflection_prompt = f"""
As a quality assurance expert, evaluate this response on these criteria:
1. Relevance: Does it directly address the task?
2. Depth: Are the insights profound and non-obvious?
3. Expertise: Does it demonstrate {self.agent_name}'s specialized knowledge?
4. Actionability: Can the client use these insights?
5. Clarity: Is it well-structured and clear?

Provide a brief critique, then on the LAST LINE ONLY, give a score from 0.0 to 1.0.
Scores ≥ {self.target_quality} are considered enterprise-ready.

TASK: {task}

RESPONSE TO EVALUATE:
{response[:2000]}...

CRITIQUE:
"""
        
        critique_result = llm.invoke(reflection_prompt).content.strip()
        
        try:
            lines = critique_result.split('\n')
            critique_text = '\n'.join(lines[:-1])
            score = float(lines[-1].strip())
            score = max(0.0, min(1.0, score)) # Clamp score to 0-1 range
        except (ValueError, IndexError):
            critique_text = "Error parsing critique. The response may be malformed."
            score = 0.1 # Assign a low score on parsing failure
            
        return {
            "critique": critique_text,
            "score": score
        }
        
    def _format_shared_insights(self, shared_insights: Dict) -> str:
        """Formats insights from other agents for inclusion in the context."""
        if not shared_insights:
            return "No insights from other agents yet."
            
        formatted = "INSIGHTS FROM OTHER AGENTS:\n\n"
        
        for agent_name, insights in shared_insights.items():
            if agent_name!= self.agent_name: # Don't include own insights
                formatted += f"From {agent_name} (Quality Score: {insights.get('quality_score', 'N/A'):.2f}):\n"
                summary = insights.get("summary", "No summary available.")
                formatted += f"  Summary: {summary}\n\n"
                
        return formatted
        
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for LangGraph integration.
        """
        print(f"\n{'='*50}")
        print(f"🚀 Executing: {self.agent_name}")
        print(f"{'='*50}")
        
        # 1. Extract everything we need from state
        task_details = state.get("current_task", {})
        task_description = task_details.get("description", "Perform analysis.")
        is_high_stakes = task_details.get("is_high_stakes", False)
        
        master_context = state.get("master_context", "")
        business_context = state.get("business_context", "")
        client_id = state.get("client_id")
        
        memory_service: MemoryInterface = state.get("memory_service")
        tool_executor: ToolExecutor = state.get("tool_executor")
        shared_insights = state.get("shared_insights", {})
        
        llm = self._get_llm(state)
        
        # 2. Security check - ensure client isolation
        if not client_id and memory_service:
            raise ValueError("Security Error: client_id is required for memory operations but was not found in the state.")
            
        # 3. Recall relevant memories
        memories =
        if memory_service:
            query = f"{task_description} for {business_context}"
            memories = memory_service.recall(query=query, limit=5, client_id=client_id)
            print(f"📚 Recalled {len(memories)} relevant memories")
        else:
            print("📚 No memory service available")
            
        # 4. Build enhanced context with peer insights
        peer_insights = self._format_shared_insights(shared_insights)
        full_context = f"{master_context}\n\n{peer_insights}"
        
        # 5. Generate response (with a potential tool use loop)
        response = self._generate_response(task_description, full_context, memories, llm)
        
        final_response = response
        tool_was_used = False
        
        try:
            tool_call = json.loads(response)
            if "tool_name" in tool_call and "tool_input" in tool_call:
                tool_was_used = True
                print(f"🔧 Using tool: {tool_call['tool_name']}")
                
                if tool_executor:
                    tool_output = tool_executor.execute(tool_call['tool_name'], tool_call['tool_input'])
                    
                    # Re-generate response with the tool's output added to the context
                    tool_context = full_context + f"\n\nTOOL OUTPUT from {tool_call['tool_name']}:\n{tool_output}"
                    final_response = self._generate_response(task_description, tool_context, memories, llm)
                else:
                    final_response = "Error: Tool execution requested but no tool executor was available in the state."
                    
        except (json.JSONDecodeError, TypeError):
            # Not a tool call, so we use the response as-is
            pass
            
        # 6. Self-reflect on the final response
        reflection = self._reflect(task_description, final_response, llm)
        quality_score = reflection['score']
        
        print(f"📊 Quality Score: {quality_score:.2f}")
        
        # 7. Determine if Human-in-the-Loop is needed
        requires_human_review = False
        review_reason = ""
        
        if quality_score < 0.7:
            requires_human_review = True
            review_reason = f"Low quality score: {quality_score:.2f}"
        elif is_high_stakes:
            requires_human_review = True
            review_reason = "High-stakes decision detected in task definition."
            
        if requires_human_review:
            print(f"🛑 Human review required: {review_reason}")
            
        # 8. Update the main state with the results of this agent's turn
        state.update({
            "current_output": final_response,
            "quality_score": quality_score,
            "critique": reflection['critique'],
            "agent_name": self.agent_name,
            "tool_was_used": tool_was_used,
            "requires_human_review": requires_human_review,
            "review_reason": review_reason,
        })
        
        # 9. Add this agent's output to the shared insights for other agents to use
        if "shared_insights" not in state:
            state["shared_insights"] = {}
            
        key_insights = {
            "summary": final_response[:500] + "..." if len(final_response) > 500 else final_response,
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        }
        
        state["shared_insights"][self.agent_name] = key_insights
        
        print(f"✅ {self.agent_name} complete (Quality: {quality_score:.2f})")
        
        return state
