from core.config import Config
from core.memory import SimpleMemory
from core.learning import SimpleLearning
from core.tools import ToolBox
from apscheduler.schedulers.background import BackgroundScheduler
from ratelimit import limits
from typing import Dict
from prompts.research_prompts import ResearchPrompts

class PsychologicalAgent:
    def __init__(self):
        self.name = "Psychological"
        self.role = "Perform deep psychological ICP analysis"
        self.llm = Config.get_llm()
        self.memory = SimpleMemory()
        self.learning = SimpleLearning()
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self._auto_run, 'interval', hours=1)
        self.scheduler.start()

    @limits(calls=20, period=86400)
    def _auto_run(self, state: Dict):
        if state.get('new_data'):
            return self.run(state)

    def _plan(self, task: str, context: str) -> str:
        past = self.memory.recall(context)
        prompt = ResearchPrompts.get_deep_psychological_research().format(
            business_context=context,
            learning_context=past,
            industry_patterns=past
        )
        response = self.llm.invoke(prompt).content
        if "web" in response.lower():
            return ToolBox.use("web", task)
        return response

    def _reflect(self, task: str, response: str) -> Dict[str, Any]:
        prompt = f"Score (0-1) and improve: Task: {task}\nResponse: {response}"
        critique = self.llm.invoke(prompt).content.split('\n')
        score = float(critique[0].split()[0])
        return {"score": score, "improve": critique[1] if score < 0.9 else None}

    def run(self, state: Dict) -> Dict[str, Any]:
        print(f"\n--- {self.name} Running ---")
        task = state.get('task', 'Default')
        context = state.get('context', '')

        response = self._plan(task, context)
        reflection = self._reflect(task, response)
        print(f"{self.name} Score: {reflection['score']:.2f}")

        if reflection['improve']:
            state['context'] += f" [Tuned: {reflection['improve']}]"
            response = self._plan(task, state['context'])

        self.memory.store([{"content": response}])
        state.update({"result": response, "quality": reflection['score']})
        return state
