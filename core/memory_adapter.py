# core/memory_adapter.py
"""
Adapter to bridge old and new memory interfaces during Level 4 upgrade
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class MemoryAdapter:
    """
    Adapts between old memory interface and new Level 4 interface.
    """
    
    def __init__(self):
        self.service = None
    
    def recall(self, agent_name: str, context: str, limit: int = 5) -> List[Dict]:
        """Recall memories for the agent"""
        if not self.service:
            return []
        
        # If service has a recall method, use it
        if hasattr(self.service, 'recall'):
            return self.service.recall(
                query=f"{agent_name}: {context}",
                limit=limit
            )
        
        # If service has a search method (vector DB style)
        if hasattr(self.service, 'search'):
            results = self.service.search(
                query=context,
                filter={"agent": agent_name},
                limit=limit
            )
            return [r.get("metadata", {}) for r in results]
        
        return []
    
    def store(self, agent_name: str, context: str, insights: Dict, quality: float) -> bool:
        """Store insights in memory"""
        if not self.service:
            return False
        
        memory_entry = {
            "agent_name": agent_name,
            "context": context,
            "insights": insights,
            "quality": quality,
            "timestamp": datetime.now().isoformat()
        }
        
        # If service has a store method
        if hasattr(self.service, 'store'):
            return self.service.store(memory_entry)
        
        # If service has an add method (vector DB style)
        if hasattr(self.service, 'add'):
            self.service.add(
                texts=[json.dumps(insights)],
                metadatas=[memory_entry]
            )
            return True
        
        return False
    
    def get_learning_patterns(self, agent_name: str, min_quality: float = 0.85) -> List[Dict]:
        """Get high-quality patterns for learning"""
        if not self.service:
            return []
        
        # Search for high-quality memories
        if hasattr(self.service, 'search'):
            results = self.service.search(
                query=f"quality>{min_quality}",
                filter={"agent": agent_name, "quality": {"$gte": min_quality}},
                limit=10
            )
            return [r.get("metadata", {}) for r in results]
        
        # Fallback to recall with quality filter
        memories = self.recall(agent_name, "high quality patterns", limit=20)
        return [m for m in memories if m.get("quality", 0) >= min_quality]
    
    def store_coaching(self, agent_name: str, coaching_text: str, improvement_areas: List[str]) -> bool:
        """Store coaching feedback"""
        coaching_entry = {
            "type": "coaching",
            "agent_name": agent_name,
            "coaching": coaching_text,
            "improvements": improvement_areas,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.store(
            agent_name=agent_name,
            context="coaching_session",
            insights=coaching_entry,
            quality=1.0  # Coaching is always high value
        )
