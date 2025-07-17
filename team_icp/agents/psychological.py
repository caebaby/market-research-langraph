from typing import Dict, Any, List
from datetime import datetime
import os
from dotenv import load_dotenv
from core.memory import HybridMemory
from core.learning import SimpleLearning
from core.tools import ToolBox
from team_icp.prompts.research_prompts import ICPResearchPrompts

load_dotenv()

class PsychologicalAgent:
    """
    Level 4+ Agent with:
    - Deep reflection and quality scoring (Level 4)
    - Memory integration with Supabase (Level 4)
    - Dynamic tool selection (Level 4)
    - Simple learning loops (approaching Level 5)
    - Clean, testable implementation
    """
    
    def __init__(self):
        self.name = "Psychological_Agent"
        self.role = "Deep psychological ICP analysis with Level 4+ capabilities"
        self.memory = HybridMemory()
        self.learning = SimpleLearning()
        self.target_quality = 0.9
        self.max_attempts = 2
    
    def run(self, state: Dict) -> Dict[str, Any]:
        """
        Main execution - Level 4 with quality focus
        """
        print(f"\n🧠 {self.name} Starting Analysis...")
        
        task = state.get("task", "Analyze psychological profile")
        context = state.get("context", "")
        
        best_result = None
        best_score = 0
        
        for attempt in range(self.max_attempts):
            print(f"\n📍 Attempt {attempt + 1}/{self.max_attempts}")
            
            result = self._analyze(task, context, state)
            
            quality = self._reflect(task, result)
            print(f"📊 Quality Score: {quality['score']:.2f}")
            
            if quality['score'] >= self.target_quality:
                print("✅ Target quality achieved!")
                best_result = result
                best_score = quality['score']
                break
            
            if quality.get("improvements") and attempt < self.max_attempts - 1:
                print("🔧 Applying improvements...")
                context += f"\n\nImprovement focus: {quality['improvements']}"
            
            if quality['score'] > best_score:
                best_result = result
                best_score = quality['score']
        
        if best_score > 0.85:
            self._store_success(task, best_result, best_score, state)
        
        return {
            "result": best_result,
            "quality_score": best_score,
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        }

    def _analyze(self, task: str, context: str, state: Dict) -> str:
        memories = self.memory.recall(context, limit=5)
        memory_context = self._format_memories(memories)
        patterns = self._extract_patterns(memories)
        memory_context += f"\n\nPROVEN PATTERNS:\n{patterns}"
        
        tools = self._select_tools(task, context)
        if tools:
            print(f"🔧 Using tools: {tools}")
        
        prompt = ICPResearchPrompts.get_psychological_analysis_prompt().format(
            business_context=context,
            memory_patterns=memory_context
        )
        prompt += """
        
        LEVEL 4 REQUIREMENTS:
        - Apply multiple psychological frameworks (Jungian, Lab Profile, JTBD, etc.)
        - Achieve visceral accuracy - insights that make them say 'how did you know?'
        - Extract hidden contradictions and unspoken fears
        - Provide actionable insights with high confidence
        - Focus on depth over breadth
        """
        
        response = ToolBox.use("llm", prompt)
        
        if "web" in tools:
            search_query = f"{task[:50]} psychology insights"
            web_results = ToolBox.use("web", search_query)
            if web_results:
                response += f"\n\nAdditional Market Insights:\n{web_results}"
        
        return response

    def _reflect(self, task: str, result: str) -> Dict[str, Any]:
        reflection_prompt = f"""
        Evaluate this psychological analysis:
        
        Task: {task}
        Result Preview: {result[:500]}...
        
        Score these criteria (0-1):
        1. Psychological Depth: Are unconscious patterns revealed?
        2. Framework Application: Are multiple frameworks properly applied?
        3. Visceral Accuracy: Would the customer feel truly understood?
        4. Actionability: Are next steps clear and valuable?
        5. Insight Quality: Are the insights profound vs obvious?
        
        Overall Score: [average of above]
        Improvements Needed: [if score < 0.9, what specifically would improve it?]
        """
        
        response = ToolBox.use("llm", reflection_prompt).split("\n")
        scores = []
        
        for line in response:
            if any(f"{i}." in line for i in range(1, 6)):
                try:
                    score_part = line.split(":")[-1].strip()
                    for word in score_part.split():
                        try:
                            score = float(word)
                            if 0 <= score <= 1:
                                scores.append(score)
                                break
                        except:
                            continue
                except:
                    pass
        
        overall_score = sum(scores) / len(scores) if scores else 0.7
        improvements = ""
        for i, line in enumerate(response):
            if "improvements" in line.lower():
                improvements = " ".join(response[i:i+3])
                break
        
        return {
            "score": overall_score,
            "criteria_scores": scores,
            "improvements": improvements.strip()
        }

    def _select_tools(self, task: str, context: str) -> List[str]:
        tools = []
        combined_text = f"{task} {context}".lower()
        
        if any(word in combined_text for word in ["market", "competitor", "industry"]):
            tools.append("web")
        
        return tools

    def _store_success(self, task: str, result: str, score: float, state: Dict) -> None:
        self.memory.store([{
            "content": result[:1000],
            "metadata": {
                "task": task,
                "score": score,
                "timestamp": datetime.now().isoformat(),
                "agent": self.name,
                "team": state.get("team", "icp")
            }
        }])
        print(f"💾 Stored successful pattern (score: {score:.2f})")

    def _format_memories(self, memories: List[Dict]) -> str:
        if not memories:
            return "No previous analyses found for this context."
        
        formatted = "RELEVANT PREVIOUS INSIGHTS:\n"
        for i, memory in enumerate(memories[:3]):
            content = memory.get("content", "")[:200]
            formatted += f"{i+1}. {content}...\n"
        
        return formatted

    def _extract_patterns(self, memories: List[Dict]) -> str:
        patterns = []
        
        for memory in memories:
            if memory.get("metadata", {}).get("score", 0) > 0.85:
                patterns.append(f"High-scoring approach (score: {memory['metadata']['score']})")
        
        return f"Successful patterns: {len(patterns)} found" if patterns else "No proven patterns yet"
