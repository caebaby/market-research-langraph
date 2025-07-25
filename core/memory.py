# Enhanced src/core/memory.py for Level 4 compliance

from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json

class HybridMemory:
    """Level 4 compliant memory system"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        self.client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
        self.memories_table = "agent_memories"
        self.learnings_table = "agent_learnings"
    
    # LEVEL 4 REQUIREMENT: Agent-specific, context-aware recall
    def recall(self, 
              agent_name: str, 
              context: str, 
              limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recall memories specific to agent and relevant to context
        """
        if not self.client:
            return []
        
        try:
            # Get agent-specific memories that match context
            response = self.client.table(self.memories_table)\
                .select("*")\
                .eq("agent_name", agent_name)\
                .ilike("context", f"%{context[:50]}%")\
                .order("quality_score", desc=True)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Recall error: {e}")
            return []
    
    # LEVEL 4 REQUIREMENT: Store with quality tracking
    def store(self, 
             agent_name: str,
             context: str,
             insights: Dict[str, Any],
             quality_score: float) -> bool:
        """
        Store agent-specific insights with quality score
        """
        if not self.client:
            return False
        
        try:
            data = {
                "agent_name": agent_name,
                "context": context[:500],  # Truncate for storage
                "insights": json.dumps(insights),  # Store as JSON
                "quality_score": quality_score,
                "created_at": datetime.now().isoformat()
            }
            
            self.client.table(self.memories_table).insert(data).execute()
            return True
        except Exception as e:
            print(f"Store error: {e}")
            return False
    
    # LEVEL 4 REQUIREMENT: Learn from coaching feedback
    def store_learning(self,
                      agent_name: str,
                      feedback: str,
                      context: str,
                      improvement_made: Optional[str] = None) -> bool:
        """
        Store coaching feedback as permanent learning
        """
        if not self.client:
            return False
        
        try:
            data = {
                "agent_name": agent_name,
                "feedback": feedback,
                "context": context,
                "improvement_made": improvement_made,
                "created_at": datetime.now().isoformat()
            }
            
            self.client.table(self.learnings_table).insert(data).execute()
            return True
        except Exception as e:
            print(f"Learning store error: {e}")
            return False
    
    # LEVEL 4 REQUIREMENT: Retrieve learnings for improvement
    def get_learnings(self, agent_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent learnings for an agent
        """
        if not self.client:
            return []
        
        try:
            response = self.client.table(self.learnings_table)\
                .select("*")\
                .eq("agent_name", agent_name)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Get learnings error: {e}")
            return []
    
    # LEVEL 4 REQUIREMENT: Track quality over time
    def get_quality_trend(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """
        Analyze quality improvement over time
        """
        if not self.client:
            return {"error": "No client"}
        
        try:
            # Get recent memories
            response = self.client.table(self.memories_table)\
                .select("quality_score, created_at")\
                .eq("agent_name", agent_name)\
                .gte("created_at", 
                     datetime.now().subtract(days=days).isoformat())\
                .order("created_at")\
                .execute()
            
            if not response.data:
                return {"no_data": True}
            
            scores = [r["quality_score"] for r in response.data]
            
            # Calculate trend
            if len(scores) > 1:
                first_half_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
                second_half_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                
                trend = "improving" if second_half_avg > first_half_avg else "declining"
            else:
                trend = "insufficient_data"
            
            return {
                "agent": agent_name,
                "total_memories": len(scores),
                "average_quality": sum(scores) / len(scores),
                "trend": trend,
                "latest_quality": scores[-1] if scores else 0
            }
            
        except Exception as e:
            print(f"Quality trend error: {e}")
            return {"error": str(e)}
