from typing import List, Dict, Any, Optional
from datetime import datetime

class MemoryAdapter:
    """
    Adapts between old memory interface and new Level 4 interface.
    Allows gradual migration without breaking existing code.
    """
    
    def __init__(self, legacy_memory_service=None, supabase_client=None, client_id=None):
        self.legacy = legacy_memory_service
        self.supabase = supabase_client
        self.client_id = client_id or "default"
        
        # If no legacy service but Supabase available, use it
        if not self.legacy and self.supabase:
            print("[MemoryAdapter] Using Supabase for memory storage")
            self._use_supabase = True
        else:
            self._use_supabase = False
        
    def recall(self, agent_name: str = None, context: str = None, limit: int = 5, **kwargs) -> List[Dict]:
        """
        New interface that works with old memory service or Supabase
        """
        print(f"[MemoryAdapter] Recalling for {agent_name}, context: {context[:50]}..., limit: {limit}")
        # If called with old style (positional args)
        if agent_name and not context:
            context = agent_name
            agent_name = "unknown"
            
        # Try Supabase first if available
        if self._use_supabase and self.supabase:
            try:
                # Vector search in Supabase with client isolation
                response = self.supabase.table("agent_memories").select("*").eq(
                    "client_id", self.client_id
                ).eq(
                    "agent_name", agent_name
                ).ilike(
                    "context", f"%{context}%"
                ).limit(limit).execute()
                print(f"[MemoryAdapter] Supabase recall response: {response.data}")
                return response.data or []
                
            except Exception as e:
                print(f"[MemoryAdapter] Supabase recall error: {e}")
                # Fall through to legacy
            
        # Use legacy service
        if self.legacy:
            try:
                results = self.legacy.recall(context, limit)
                enhanced_results = []
                for result in results:
                    enhanced_result = dict(result) if isinstance(result, dict) else {"content": str(result)}
                    enhanced_result["agent_name"] = agent_name
                    enhanced_result["recalled_at"] = datetime.now().isoformat()
                    enhanced_results.append(enhanced_result)
                print(f"[MemoryAdapter] Legacy recall success: {len(enhanced_results)} memories")
                return enhanced_results
                
            except Exception as e:
                print(f"[MemoryAdapter] Legacy recall error: {e}")
                return []
        
        return []
    
    def store(self, agent_name: str, context: str, insights: Dict[str, Any], quality: float) -> bool:
        """
        New interface for storing with metadata
        """
        print(f"[MemoryAdapter] Storing for {agent_name}, context: {context[:50]}...")
        # Create enhanced memory entry
        memory_entry = {
            "agent_name": agent_name,
            "client_id": self.client_id,
            "context": context,
            "insights": insights,
            "quality": quality,
            "created_at": datetime.now().isoformat()
        }
        
        # Try Supabase first
        if self._use_supabase and self.supabase:
            try:
                response = self.supabase.table("agent_memories").insert(memory_entry).execute()
                print(f"[MemoryAdapter] Supabase store success: {bool(response.data)}")
                return bool(response.data)
            except Exception as e:
                print(f"[MemoryAdapter] Supabase store error: {e}")
                # Fall through to legacy
                
        # Use legacy service
        if self.legacy:
            try:
                memory_entry["content"] = f"Agent: {agent_name}\nQuality: {quality}\nInsights: {insights}"
                self.legacy.store([memory_entry])
                print("[MemoryAdapter] Legacy store success")
                return True
                
            except Exception as e:
                print(f"[MemoryAdapter] Store error: {e}")
                return False
                
        return False
    
    def get_learning_patterns(self, agent_name: str, min_quality: float = 0.8) -> List[Dict]:
        """
        Retrieve high-quality patterns for learning
        """
        all_memories = self.recall(agent_name=agent_name, context="", limit=50)
        
        quality_memories = []
        for memory in all_memories:
            if memory.get("quality", 0) >= min_quality:
                if memory.get("agent_name") == agent_name or not memory.get("agent_name"):
                    quality_memories.append(memory)
                    
        return quality_memories
    
    def store_coaching(self, agent_name: str, coaching_text: str, improvement_areas: List[str]) -> bool:
        """
        Store coaching feedback for agent improvement
        """
        coaching_entry = {
            "type": "coaching",
            "agent_name": agent_name,
            "coaching": coaching_text,
            "improvement_areas": improvement_areas,
            "created_at": datetime.now().isoformat()
        }
        
        return self.store(
            agent_name=agent_name,
            context=f"coaching_session_{datetime.now().strftime('%Y%m%d')}",
            insights=coaching_entry,
            quality=1.0
        )
