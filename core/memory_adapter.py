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
        
        # Determine which service to use
        if supabase_client:
            print("[MemoryAdapter] Using Supabase for memory storage")
            self._use_supabase = True
        elif legacy_memory_service:
            print("[MemoryAdapter] Using legacy memory service")
            self._use_supabase = False
        else:
            print("[MemoryAdapter] WARNING: No memory service available")
            self._use_supabase = False
        
    def recall(self, agent_name: str = None, context: str = None, limit: int = 5, **kwargs) -> List[Dict]:
        """
        New interface that works with old memory service or Supabase.
        Handles the case where legacy service doesn't accept agent_name.
        """
        print(f"[MemoryAdapter] Recalling for {agent_name}, context: {context[:50] if context else ''}..., limit: {limit}, client_id: {self.client_id}")
        
        # Handle backwards compatibility
        if agent_name and not context:
            context = agent_name
            agent_name = "unknown"
            
        # Use Supabase if available
        if self._use_supabase and self.supabase:
            try:
                query = self.supabase.table("agent_memories").select("*")
                
                # Add filters if provided
                if self.client_id:
                    query = query.eq("client_id", self.client_id)
                if agent_name:
                    query = query.eq("agent_name", agent_name)
                if context:
                    query = query.ilike("context", f"%{context}%")
                    
                response = query.limit(limit).execute()
                print(f"[MemoryAdapter] Supabase recall found {len(response.data)} memories")
                return response.data or []
                
            except Exception as e:
                print(f"[MemoryAdapter] Supabase recall error: {e}")
                # Fall through to legacy if Supabase fails
                
        # Use legacy service if available
        if self.legacy:
            try:
                # Legacy HybridMemory only accepts (context, limit)
                # Don't pass agent_name as it doesn't support it
                results = self.legacy.recall(context or "", limit)
                
                # Enhance results with agent_name for consistency
                enhanced_results = []
                for result in results:
                    enhanced_result = dict(result) if isinstance(result, dict) else {"content": str(result)}
                    enhanced_result["agent_name"] = agent_name or "unknown"
                    enhanced_result["recalled_at"] = datetime.now().isoformat()
                    enhanced_results.append(enhanced_result)
                    
                print(f"[MemoryAdapter] Legacy recall found {len(enhanced_results)} memories")
                return enhanced_results
                
            except Exception as e:
                print(f"[MemoryAdapter] Legacy recall error: {e}")
                return []
        
        print("[MemoryAdapter] No memory service available")
        return []
    
    def store(self, agent_name: str, context: str, insights: Dict[str, Any], quality: float) -> bool:
        """
        Store insights in memory with proper column names for Supabase
        """
        print(f"[MemoryAdapter] Storing for {agent_name}, context: {context[:50]}..., quality: {quality}")
        
        # Use Supabase if available
        if self._use_supabase and self.supabase:
            try:
                memory_entry = {
                    "agent_name": agent_name,
                    "client_id": self.client_id,
                    "context": context,
                    "insights": insights,
                    "quality_score": quality,  # Matches Supabase schema
                    "created_at": datetime.now().isoformat()
                }
                
                response = self.supabase.table("agent_memories").insert(memory_entry).execute()
                success = bool(response.data)
                print(f"[MemoryAdapter] Supabase store success: {success}")
                return success
                
            except Exception as e:
                print(f"[MemoryAdapter] Supabase store error: {e}")
                # Fall through to legacy if Supabase fails
                
        # Use legacy service if available
        if self.legacy:
            try:
                # Legacy format - create a list with one entry
                memory_entry = {
                    "content": f"Agent: {agent_name}\nQuality: {quality}\nInsights: {insights}",
                    "metadata": {
                        "agent_name": agent_name,
                        "quality": quality,
                        "context": context,
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
                # Legacy store expects a list
                self.legacy.store([memory_entry])
                print("[MemoryAdapter] Legacy store success")
                return True
                
            except Exception as e:
                print(f"[MemoryAdapter] Legacy store error: {e}")
                return False
                
        print("[MemoryAdapter] No memory service available")
        return False
    
    def get_learning_patterns(self, agent_name: str, min_quality: float = 0.8) -> List[Dict]:
        """
        Retrieve high-quality patterns for learning.
        Works with both quality (legacy) and quality_score (Supabase) fields.
        """
        print(f"[MemoryAdapter] Getting learning patterns for {agent_name}, min_quality: {min_quality}")
        
        # Get all memories for this agent
        all_memories = self.recall(agent_name=agent_name, context="", limit=50)
        
        # Filter by quality
        quality_memories = []
        for memory in all_memories:
            # Check both field names for compatibility
            quality = memory.get("quality_score") or memory.get("quality", 0)
            
            if quality >= min_quality:
                # Check agent name matches
                if memory.get("agent_name") == agent_name or not memory.get("agent_name"):
                    quality_memories.append(memory)
                    
        print(f"[MemoryAdapter] Found {len(quality_memories)} high-quality patterns")
        return quality_memories
    
    def store_coaching(self, agent_name: str, coaching_text: str, improvement_areas: List[str]) -> bool:
        """
        Store coaching feedback for agent improvement
        """
        print(f"[MemoryAdapter] Storing coaching for {agent_name}")
        
        coaching_entry = {
            "type": "coaching",
            "agent_name": agent_name,
            "coaching": coaching_text,
            "improvement_areas": improvement_areas,
            "timestamp": datetime.now().isoformat()
        }
        
        # Store with high quality since coaching is valuable
        return self.store(
            agent_name=agent_name,
            context=f"coaching_session_{datetime.now().strftime('%Y%m%d')}",
            insights=coaching_entry,
            quality=1.0
        )
    
    # Backwards compatibility method
    def get_service(self):
        """For code that needs direct access to underlying service"""
        if self._use_supabase:
            return self.supabase
        return self.legacy
