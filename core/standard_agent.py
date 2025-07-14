# core/agents/base_agent.py
"""
Level 5 Base Agent Template
This is THE template all your agents will inherit from.
Has all Level 5 capabilities built in - just enhance over time.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.memory.persistent import PersistentMemory

class Level5BaseAgent(ABC):
    """
    Base class for ALL Level 5 agents
    
    Level 5 Capabilities:
    1. ✅ Persistent Memory (implemented)
    2. ✅ Goal Management (basic implementation)
    3. ✅ Tool Selection (basic implementation)
    4. ✅ Self-Improvement (basic implementation)
    5. ✅ Communication (basic implementation)
    
    Inherit from this and you get Level 5 structure automatically!
    """
    
    def __init__(self, agent_name: str, agent_role: str):
        # Core identity
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.agent_id = f"{agent_name}_{datetime.now().timestamp()}"
        
        # Level 5 Systems (all agents get these!)
        self.memory = PersistentMemory()
        self.performance_metrics = {
            "tasks_completed": 0,
            "average_success_score": 0.0,
            "total_execution_time": 0.0,
            "improvement_cycles": 0
        }
        
        # Available tools (override in subclass)
        self.available_tools = []
        
        # Communication queue (for inter-agent messaging)
        self.message_queue = []
        
        print(f"🚀 {self.agent_name} initialized as Level 5 agent")
    
    # ==========================================
    # LEVEL 5 CORE METHODS - Don't change these!
    # ==========================================
    
    async def pursue_goal(self, goal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Level 5 Goal Pursuit - The main entry point
        This orchestrates all Level 5 capabilities
        """
        print(f"\n🎯 {self.agent_name} pursuing goal: {goal.get('description', 'Unknown')}")
        
        # 1. DECOMPOSE GOAL (Level 5 feature)
        sub_goals = await self.decompose_goal(goal)
        print(f"📊 Decomposed into {len(sub_goals)} sub-goals")
        
        # 2. RECALL RELEVANT MEMORIES (Level 5 feature)
        relevant_memories = self.memory.recall_similar(
            goal.get('context', ''),
            limit=5
        )
        print(f"🧠 Recalled {len(relevant_memories)} relevant memories")
        
        # 3. SELECT OPTIMAL TOOLS (Level 5 feature)
        selected_tools = await self.select_tools(goal, relevant_memories)
        print(f"🔧 Selected tools: {selected_tools}")
        
        # 4. EXECUTE GOAL WITH MONITORING
        results = []
        start_time = datetime.now()
        
        for sub_goal in sub_goals:
            # Execute with memory context
            result = await self.execute_task(sub_goal, relevant_memories, selected_tools)
            results.append(result)
            
            # Check if we need to adapt (Level 5 feature)
            if result.get('success_score', 0) < 0.7:
                print(f"⚠️ Low success score, adapting approach...")
                selected_tools = await self.adapt_approach(sub_goal, result)
        
        # 5. CALCULATE OVERALL SUCCESS
        overall_success = sum(r.get('success_score', 0) for r in results) / len(results)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # 6. LEARN FROM EXPERIENCE (Level 5 feature)
        experience = {
            "goal": goal,
            "results": results,
            "success_score": overall_success,
            "execution_time": execution_time,
            "tools_used": selected_tools,
            "agent": self.agent_name
        }
        self.memory.store_experience(experience)
        
        # 7. SELF-IMPROVEMENT CHECK (Level 5 feature)
        if overall_success < 0.8:
            await self.trigger_self_improvement(experience)
        
        # 8. UPDATE METRICS
        self._update_metrics(overall_success, execution_time)
        
        # 9. COMMUNICATE RESULTS (Level 5 feature)
        await self.communicate_results(goal, results)
        
        return {
            "goal": goal,
            "results": results,
            "success_score": overall_success,
            "execution_time": execution_time,
            "metrics": self.performance_metrics
        }
    
    # ==========================================
    # LEVEL 5 FEATURES - Override these in subclasses
    # ==========================================
    
    async def decompose_goal(self, goal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Level 5: Goal Decomposition
        Override this with sophisticated decomposition in subclasses
        """
        # Basic implementation - just return the goal as-is
        return [goal]
    
    async def select_tools(self, goal: Dict[str, Any], memories: List[Dict]) -> List[str]:
        """
        Level 5: Dynamic Tool Selection
        Override this with smart tool selection in subclasses
        """
        # Basic implementation - return all available tools
        return self.available_tools
    
    async def adapt_approach(self, goal: Dict[str, Any], result: Dict[str, Any]) -> List[str]:
        """
        Level 5: Adaptive Execution
        Override this with smart adaptation in subclasses
        """
        # Basic implementation - just return current tools
        return self.available_tools
    
    async def trigger_self_improvement(self, experience: Dict[str, Any]) -> None:
        """
        Level 5: Self-Improvement
        Override this with learning algorithms in subclasses
        """
        # Basic implementation - just increment counter
        self.performance_metrics["improvement_cycles"] += 1
        print(f"🔧 Self-improvement cycle #{self.performance_metrics['improvement_cycles']}")
    
    async def communicate_results(self, goal: Dict[str, Any], results: List[Dict]) -> None:
        """
        Level 5: Inter-Agent Communication
        Override this with actual messaging in subclasses
        """
        # Basic implementation - add to message queue
        message = {
            "from": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "goal": goal,
            "results": results
        }
        self.message_queue.append(message)
    
    # ==========================================
    # ABSTRACT METHOD - Must implement in subclasses
    # ==========================================
    
    @abstractmethod
    async def execute_task(
        self, 
        task: Dict[str, Any], 
        memories: List[Dict], 
        tools: List[str]
    ) -> Dict[str, Any]:
        """
        The actual work happens here!
        Each agent type implements their specific logic
        """
        pass
    
    # ==========================================
    # HELPER METHODS
    # ==========================================
    
    def _update_metrics(self, success_score: float, execution_time: float) -> None:
        """Update agent performance metrics"""
        self.performance_metrics["tasks_completed"] += 1
        
        # Update average success score
        total_tasks = self.performance_metrics["tasks_completed"]
        current_avg = self.performance_metrics["average_success_score"]
        new_avg = ((current_avg * (total_tasks - 1)) + success_score) / total_tasks
        self.performance_metrics["average_success_score"] = new_avg
        
        # Update total execution time
        self.performance_metrics["total_execution_time"] += execution_time
