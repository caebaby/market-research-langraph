# verify_memory.py
from core.memory_system_qdrant import QdrantMemorySystem

# Check that the method exists
memory = QdrantMemorySystem()
print("Available methods:")
print("- store_memory:", hasattr(memory, 'store_memory'))
print("- retrieve_memories:", hasattr(memory, 'retrieve_memories'))
print("- search_memories:", hasattr(memory, 'search_memories'))  # Should be False

# Test it works
memory_id = memory.store_memory(
    client_id="test_company",
    agent_name="test",
    memory_type="test",
    content="Test content"
)
print(f"\nStored: {memory_id}")

memories = memory.retrieve_memories(
    client_id="test_company",
    limit=5
)
print(f"Retrieved: {len(memories)} memories")