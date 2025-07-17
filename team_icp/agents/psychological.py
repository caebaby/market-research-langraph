from typing import Dict, Any, List
from datetime import datetime
import os
from dotenv import load_dotenv
from core.config import Config  # ADD THIS IMPORT
from core.memory import HybridMemory
from core.learning import LearningManager
from core.tools import ToolBox
from team_icp.prompts.research_prompts import ICPResearchPrompts

load_dotenv()

class PsychologicalAgent:
    """
    Level 5 Agent with:
    - Autonomous meta-learning and strategy updates
    - Deep reflection and quality scoring
    - Persistent memory with Supabase
    """
    
    def __init__(self):
        self.name = "Psychological_Agent"
        self.role = "Deep psychological ICP analysis with Level 5 capabilities"
        self.llm = Config.get_llm()  # ADD THIS LINE
        self.memory = HybridMemory()
        self.learning = LearningManager(agent_name=self.name)
        self.target_quality = 0.9
        self.max_attempts = 2
    
    def run(self, state: Dict) -> Dict[str, Any]:
        """
        Main execution - Level 5 with autonomous learning
        """
        print(f"\n🧠 {self.name} Starting Analysis...")
        
        self.learning.run_learning_cycle(self.memory.get_all_memories())

        task = state.get("task", "Analyze psychological profile")
        context = state.get("context", "")
        
        best_result, best_score = None, 0
        
        for attempt in range(self.max_attempts):
            print(f"\n📍 Attempt {attempt + 1}/{self.max_attempts}")
            
            result = self._analyze(task, context, state)
            quality = self._reflect(task, result)
            print(f"📊 Quality Score: {quality['score']:.2f}")
            
            if quality['score'] >= self.target_quality:
                print("✅ Target quality achieved!")
                best_result, best_score = result, quality['score']
                break
            
            if quality.get("improvements") and attempt < self.max_attempts - 1:
                print("🔧 Applying improvements...")
                context += f"\n\nImprovement focus: {quality['improvements']}"
            
            if quality['score'] > best_score:
                best_result, best_score = result, quality['score']
        
        if best_score > 0.85:
            self._store_success(task, best_result, best_score, state, context)  # ADD context parameter
            self.learning.update_strategies(best_result, context, best_score)

        return {
            "result": best_result,
            "quality_score": best_score,
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        }

    def _analyze(self, task: str, context: str, state: Dict) -> str:
        memories = self.memory.recall(context, limit=3)
        memory_context = self._format_memories(memories)
        strategic_insights = self.learning.get_strategic_insights(context)  # FIX INDENTATION
        
        prompt = ICPResearchPrompts.get_psychological_analysis_prompt().format(
            business_context=context,
            memory_patterns=memory_context
        )
        
        # Add strategic insights to the prompt
        prompt += f"\n\nSTRATEGIC DIRECTIVES:\n{strategic_insights}"
        
        # This actually sends to the LLM
        response = self.llm.invoke(prompt).content
        return response

    def _reflect(self, task: str, result: str) -> Dict[str, Any]:
        reflection_prompt = f"""
        Evaluate this psychological analysis:
    
        Task: {task}
        Result Preview: {result[:500]}...
    
        Score these criteria (0-1):
        1. Psychological Depth: Are unconscious patterns revealed?
        2. Framework Application: Are multiple frameworks applied?
        3. Visceral Accuracy: Would the customer feel understood?
        4. Actionability: Are next steps clear?
        5. Insight Quality: Are insights profound?
    
        Overall Score: [average of above]
        Improvements Needed: [if score < 0.9, suggest improvements]
        """
    
        # Change ToolBox to self.llm.invoke
        response = self.llm.invoke(reflection_prompt).content.split("\n")
        scores = []
        for line in response:
            if any(f"{i}." in line for i in range(1, 6)):
                try:
                    score = float(line.split(":")[-1].strip().split()[0])
                    if 0 <= score <= 1:
                        scores.append(score)
                except:
                    pass
        overall_score = sum(scores) / len(scores) if scores else 0.7
        improvements = next((line for line in response if "improvements" in line.lower()), "").split(":")[-1].strip()
    
        return {"score": overall_score, "improvements": improvements}

    def _store_success(self, task: str, result: str, score: float, state: Dict, context: str) -> None:  # ADD context parameter
        self.memory.store([{
            "content": result[:1000],
            "metadata": {
                "task": task,
                "score": score,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "team": state.get("team", "icp"),
                "context_summary": context[:100]
            }
        }])
        print(f"💾 Stored successful experience (score: {score:.2f})")

    def _format_memories(self, memories: List[Dict]) -> str:
        if not memories:
            return "No previous analyses found."
        formatted = "RELEVANT PREVIOUS INSIGHTS:\n"
        for i, memory in enumerate(memories):
            formatted += f"{i+1}. {memory.get('content', '')[:200]}...\n"
        return formatted
