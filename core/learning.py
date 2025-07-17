import os
from supabase import create_client, Client
from core.tools import ToolBox

class LearningManager:
    """
    Manages meta-learning for the agent
    """
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.strategy_table = "strategies"
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase URL and Key must be set.")
        self.client = create_client(url, key)

    def get_strategic_insights(self, context: str) -> str:
        print("🧠 Retrieving strategic insights...")
        if self.client:
            response = self.client.table(self.strategy_table).select("*").limit(3).execute()
            if response.data:
                insights = "\n".join([f"- {item['strategy_description']}" for item in response.data])
                return f"Apply these strategies:\n{insights}"
        return "No strategies found. Use best practices."

    def update_strategies(self, successful_result: str, context: str, score: float):
        print(f"🔬 Analyzing result (Score: {score})...")
        prompt = f"""
        Analysis scored {score}. Context: {context[:500]}
        Result: {successful_result[:1500]}
        Extract a reusable strategy. Example: 'Focus on contradictions.'
        STRATEGY:
        """
        strategy = ToolBox.use("llm", prompt)
        if strategy:
            print(f"Learned strategy: {strategy}")
            self.client.table(self.strategy_table).insert({
                "agent_name": self.agent_name,
                "strategy_description": strategy,
                "source_context": context,
                "embedding": ToolBox.use("embedding", strategy)
            }).execute()

    def run_learning_cycle(self, all_memories: list):
        print("\n🔄 Checking learning opportunities... (placeholder)")
