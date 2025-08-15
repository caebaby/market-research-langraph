# test_v4_foundation.py
from core.standard_agent_v4 import StandardAgentNodeV4
from core.memory_adapter import MemoryAdapter
from core.config import Config

print("✅ V4 imports work")

# Test config
llm = Config.get_llm()
print(f"✅ LLM configured: {type(llm)}")

# Test memory adapter
adapter = MemoryAdapter()
print("✅ Memory adapter created")

print("\n🎉 Foundation ready!")
