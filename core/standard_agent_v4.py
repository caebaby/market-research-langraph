# core/standard_agent_v4.py
"""
Level 4 StandardAgentNode with full HITL, memory, and learning capabilities
"""

from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import json
import requests  # ADD THIS
import os       # ADD THIS (if not already there)

from core.memory_adapter import MemoryAdapter


class StandardAgentNodeV4(ABC):
    """
    Level 4 base agent with:
    - Memory integration with learning
    - HITL (Human-in-the-Loop) governance
    - Self-improvement from coaching
    - Quality-based intervention
    - Inter-agent communication
    """
    
    def __init__(self, 
                 agent_name: str,
                 role_prompt: str,
                 target_quality: float = 0.75,
                 require_human_review_below: float = 0.6):
        self.agent_name = agent_name
        self.role_prompt = role_prompt
        self.target_quality = target_quality
        self.review_threshold = require_human_review_below
        
        # HITL settings
        self.allow_coaching = True
        self.pause_on_low_quality = True
        self.learn_from_feedback = True
        
        # Temporary storage during execution
        self.memory = None
        self.state = None
        self.tools = None
        self._llm = None
    
    def web_search(self, query: str, num_results: int = 5) -> str:
        """Search the web using Brave Search API"""
        try:
            api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not api_key:
                return "Error: BRAVE_SEARCH_API_KEY not found in environment variables"
            
            url = "https://api.search.brave.com/res/v1/web/search"
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": api_key
            }
            params = {
                "q": query,
                "count": num_results,
                "text_decorations": False
            }
            
            print(f"🔍 Searching web for: {query}")
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Format results for agent analysis
            formatted_output = f"Web Search Results for: {query}\n\n"
            
            if "web" in data and "results" in data["web"]:
                for i, result in enumerate(data["web"]["results"], 1):
                    formatted_output += f"{i}. {result.get('title', 'No title')}\n"
                    formatted_output += f"   URL: {result.get('url', '')}\n"
                    formatted_output += f"   Description: {result.get('description', '')}\n\n"
            else:
                formatted_output += "No results found.\n"
                
            return formatted_output
            
        except Exception as e:
            return f"Error searching web: {str(e)}"
        
        
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution with Level 4 features"""
        self.state = state
        print(f"\n{'='*50}")
        print(f"🚀 Executing: {self.agent_name}")
        print(f"{'='*50}")
        
        try:
            # 1. MEMORY INITIALIZATION
            if state.get("memory_service"):
                self.memory = MemoryAdapter()
                self.memory.service = state["memory_service"]  # Set it as an attribute instead
                
                # Recall relevant memories
                memories = self._recall_relevant_memories()
                print(f"📚 Recalled {len(memories)} relevant memories")
                
                # Check for coaching to apply
                coaching = self._get_recent_coaching()
                if coaching:
                    print(f"📝 Applying coaching feedback from previous session")
            else:
                memories = []
                coaching = None
                
            # 1.5 TOOLS INITIALIZATION
            if state.get("tool_executor"):
                self.tools = state["tool_executor"]
                print(f"🔧 Tools available for {self.agent_name}")
                
            # 2. EXECUTE CORE ANALYSIS
            business_context = self._extract_business_context()
            task = state.get("current_task", {}).get("description", f"Perform {self.agent_name} analysis")
            
            # Generate response with memory context
            response = self._generate_response(task, business_context, memories, self.llm)
            
            # 2.5 CHECK FOR TOOL REQUEST (NEW!)
            final_response = response
            try:
                tool_request = json.loads(response)
                if isinstance(tool_request, dict) and tool_request.get("tool") == "web_search":
                    print(f"🔧 {self.agent_name} requesting web search: {tool_request.get('query', '')}")
                    
                    # Execute web search
                    search_results = self.web_search(tool_request.get("query", ""))
                    
                    # Re-generate response with search results
                    enhanced_context = f"{business_context}\n\nWEB SEARCH RESULTS:\n{search_results}"
                    final_response = self._generate_response(task, enhanced_context, memories, self.llm)
                    print(f"✅ {self.agent_name} incorporated search results")
            except (json.JSONDecodeError, TypeError):
                # Not a tool request, use original response
                pass
            
            # 3. QUALITY ASSESSMENT & REFLECTION
            reflection = self._reflect(task, response, self.llm)
            quality_score = reflection.get("score", 0.0)
            
            print(f"📊 Quality Score: {quality_score:.2f}")
            
            # 4. HITL DECISION POINT
            requires_review = False
            review_reason = ""
            
            # Check if quality triggers review
            if quality_score < self.review_threshold:
                requires_review = True
                review_reason = f"Low quality score: {quality_score:.2f}"
                print(f"🛑 Human review required: {review_reason}")
                
            # Check if task is high-stakes
            if state.get("current_task", {}).get("is_high_stakes", False):
                requires_review = True
                review_reason = "High-stakes decision requires human review"
                print(f"🛑 Human review required: {review_reason}")
                
            # 5. IMPROVEMENT LOOP (if needed)
            if quality_score < self.target_quality and not requires_review:
                print(f"🔄 Quality below target ({self.target_quality}), attempting improvement...")
                
                # Use reflection to improve
                improvement_prompt = self._create_improvement_prompt(task, response, reflection["critique"])
                improved_response = self.llm.invoke(improvement_prompt).content
                
                # Re-assess quality
                new_reflection = self._reflect(task, improved_response, self.llm)
                new_quality = new_reflection.get("score", 0.0)
                
                if new_quality > quality_score:
                    print(f"✨ Improved quality: {quality_score:.2f} → {new_quality:.2f}")
                    response = improved_response
                    quality_score = new_quality
                    reflection = new_reflection
                    
            # 6. MEMORY STORAGE (only high-quality outputs)
            if self.memory and quality_score >= 0.8:
                insights = self._extract_insights_for_memory(response)
                self.memory.store(
                    agent_name=self.agent_name,
                    context=business_context[:200],  # Truncate for storage
                    insights=insights,
                    quality=quality_score
                )
                print(f"💾 Stored high-quality insights for future learning")
                
            # 7. INTER-AGENT COMMUNICATION
            shared_insights = self._create_shared_insights(response, quality_score)
            
            # 8. UPDATE STATE
            state["current_output"] = final_response
            state["agent_name"] = self.agent_name
            state["quality_score"] = quality_score
            state["reflection"] = reflection
            state["requires_human_review"] = requires_review
            state["review_reason"] = review_reason
            
            # Update shared insights
            if "shared_insights" not in state:
                state["shared_insights"] = {}
            state["shared_insights"][self.agent_name] = shared_insights
            
            # 9. HITL PAUSE POINT (if needed)
            if requires_review and self.pause_on_low_quality:
                state["hitl_pause"] = True
                state["hitl_agent"] = self.agent_name
                state["hitl_options"] = {
                    "approve": "Accept the current output",
                    "coach": "Provide feedback to improve",
                    "override": "Provide your own analysis",
                    "skip": "Skip this agent"
                }
                
            print(f"✅ {self.agent_name} complete (Quality: {quality_score:.2f})")
            
        except Exception as e:
            print(f"❌ Error in {self.agent_name}: {str(e)}")
            state["error"] = str(e)
            state["requires_human_review"] = True
            state["review_reason"] = f"Error: {str(e)}"
            
        return state
    
    def _recall_relevant_memories(self) -> List[Dict]:
        """Recall memories relevant to current context"""
        if not self.memory:
            return []
            
        business_context = self._extract_business_context()
        
        # Get general memories
        memories = self.memory.recall(
            agent_name=self.agent_name,
            context=business_context,
            limit=5
        )
        
        # Also get high-quality patterns for learning
        patterns = self.memory.get_learning_patterns(
            agent_name=self.agent_name,
            min_quality=0.85
        )
        
        # Combine and deduplicate
        all_memories = memories + patterns
        seen = set()
        unique_memories = []
        
        for memory in all_memories:
            key = memory.get("content", "")[:100]
            if key not in seen:
                seen.add(key)
                unique_memories.append(memory)
                
        return unique_memories[:5]  # Limit total
    
    def _get_recent_coaching(self) -> Optional[Dict]:
        """Get most recent coaching feedback"""
        if not self.memory:
            return None
            
        coaching_memories = self.memory.recall(
            agent_name=self.agent_name,
            context="coaching_session",
            limit=3
        )
        
        # Find most recent coaching
        for memory in coaching_memories:
            if memory.get("insights", {}).get("type") == "coaching":
                return memory.get("insights")
                
        return None
    
    def _create_improvement_prompt(self, task: str, response: str, critique: str) -> str:
        """Create prompt to improve based on reflection"""
        return f"""You are {self.agent_name}. Your previous analysis needs improvement.

TASK: {task}

YOUR PREVIOUS RESPONSE:
{response}

CRITIQUE OF YOUR WORK:
{critique}

Please provide an IMPROVED analysis that addresses the critique while maintaining your role and expertise.
Focus on the specific weaknesses identified.

IMPROVED ANALYSIS:"""
    
    def _extract_business_context(self) -> str:
        """Extract business context from state"""
        if not self.state:
            return ""
            
        # Try multiple possible context fields
        context = self.state.get("business_context") or self.state.get("master_context") or ""
        
        # Add any shared insights from other agents
        if self.state.get("shared_insights"):
            insights_text = "\n\nINSIGHTS FROM OTHER AGENTS:\n"
            for agent, insights in self.state["shared_insights"].items():
                if agent != self.agent_name:  # Don't include own insights
                    insights_text += f"\n{agent}:\n{insights.get('summary', 'No summary available')}\n"
            context += insights_text
            
        return context
    
    def handle_coaching(self, coaching_text: str, improvement_areas: List[str]) -> Dict[str, Any]:
        """Handle coaching feedback from human"""
        if not self.memory:
            return {"status": "error", "message": "Memory service not available"}
            
        # Store coaching
        success = self.memory.store_coaching(
            agent_name=self.agent_name,
            coaching_text=coaching_text,
            improvement_areas=improvement_areas
        )
        
        if success:
            # Attempt to apply coaching immediately
            improved_response = self._apply_coaching_feedback(coaching_text)
            
            return {
                "status": "success",
                "message": "Coaching stored and will be applied in future analyses",
                "improved_response": improved_response
            }
        else:
            return {"status": "error", "message": "Failed to store coaching"}
    
    def _apply_coaching_feedback(self, coaching_text: str) -> str:
        """Apply coaching to current analysis"""
        current_output = self.state.get("current_output", "")
        
        coaching_prompt = f"""You are {self.agent_name}. You've received coaching feedback on your analysis.

YOUR ANALYSIS:
{current_output}

COACHING FEEDBACK:
{coaching_text}

Apply this feedback to improve your analysis. Maintain your expertise while incorporating the human's guidance.

IMPROVED ANALYSIS WITH COACHING APPLIED:"""
        
        improved = self.llm.invoke(coaching_prompt).content
        
        # Update state with improved version
        self.state["current_output"] = improved
        self.state["coaching_applied"] = True
        
        return improved
    
    # ABSTRACT METHODS - Must be implemented by each agent
    
    @abstractmethod
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate agent-specific response"""
        pass
    
    @abstractmethod
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on quality of response"""
        pass
    
    @abstractmethod
    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract key insights to store in memory"""
        pass
    
    @abstractmethod
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        pass
    
    @property
    def llm(self):
        """Get LLM instance from state or config"""
        if self._llm:
            return self._llm
            
        # Try to get from state first
        if self.state and self.state.get("llm"):
            self._llm = self.state["llm"]
            return self._llm
            
        # Fall back to config
        try:
            from core.config import Config
            self._llm = Config.get_llm(self.agent_name)
            return self._llm
        except:
            pass
            
        # Last resort - create a default
        try:
            from langchain.chat_models import ChatAnthropic
            self._llm = ChatAnthropic(
                model="claude-sonnet-4-20250514",  # Sonnet 4 
                temperature=0.7
            )
            
            return self._llm
        except Exception as e:
            raise RuntimeError(f"No LLM available for {self.agent_name}: {e}")
