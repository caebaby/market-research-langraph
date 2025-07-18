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
        
        try:
            prompt = f"""
            Analysis scored {score}. Context: {context[:500]}
            Result: {successful_result[:1500]}
            Extract a reusable strategy. Example: 'Focus on contradictions.'
            STRATEGY:
            """
            
            # Get strategy from LLM
            strategy = ToolBox.use("llm", prompt)
            
            # Clean up the strategy (remove extra whitespace, limit length)
            if strategy:
                strategy = strategy.strip()[:500]  # Limit to 500 chars
                print(f"Learned strategy: {strategy}")
                
                # Prepare data for insertion
                insert_data = {
                    "strategy_description": strategy,
                    "context": str(context)[:1000],  # Limit context length
                    "score": float(score)
                }
                
                # Check if agent_name column exists in your table
                # If it does, add it:
                # insert_data["agent_name"] = self.agent_name
                
                # Try to get embedding, but don't fail if it doesn't work
                try:
                    embedding = ToolBox.use("embedding", strategy)
                    if embedding:
                        insert_data["embedding"] = embedding
                except Exception as e:
                    print(f"⚠️ Embedding generation failed: {e}")
                
                # Insert into Supabase
                response = self.client.table(self.strategy_table).insert(insert_data).execute()
                print("✅ Strategy stored successfully!")
                
            else:
                print("⚠️ No strategy extracted from LLM")
                
        except Exception as e:
            print(f"❌ Failed to update strategies: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            # Don't re-raise - let the agent continue working
    
    def run_learning_cycle(self, all_memories: list):
        print("\n🔄 Checking learning opportunities... (placeholder)")
