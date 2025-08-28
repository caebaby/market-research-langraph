# core/memory_system_qdrant.py
"""
Qdrant Cloud-based Memory System for Level 4 AI Agents
Vector-based semantic memory with persistent storage
FIXED: Added accessed_at field and proper field handling
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
import numpy as np

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    UpdateStatus,
    PayloadSchemaType
)
from sentence_transformers import SentenceTransformer


@dataclass
class Memory:
    """Memory object structure with proper field handling"""
    client_id: str
    agent_name: str
    memory_type: str  # 'insight', 'learning', 'pattern', 'client_context'
    content: str
    context: Optional[str] = None
    importance: float = 0.5
    quality_impact: float = 0.0
    timestamp: str = None
    access_count: int = 0
    accessed_at: Optional[str] = None  # ADDED: Track when memory was accessed
    
    # Additional fields that might exist in stored memories
    shared_from: Optional[str] = None
    original_id: Optional[str] = None
    shared_at: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert to dictionary, excluding None values"""
        data = asdict(self)
        # Remove None values to keep payload clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]):
        """
        Create Memory from Qdrant payload, handling extra fields gracefully
        
        WHY: Qdrant might return fields we don't expect, so we filter them
        """
        # Get only the fields that Memory expects
        expected_fields = {
            'client_id', 'agent_name', 'memory_type', 'content', 
            'context', 'importance', 'quality_impact', 'timestamp', 
            'access_count', 'accessed_at', 'shared_from', 'original_id', 'shared_at'
        }
        
        # Filter payload to only include expected fields
        filtered_payload = {k: v for k, v in payload.items() if k in expected_fields}
        
        # Ensure required fields have defaults if missing
        filtered_payload.setdefault('client_id', 'unknown')
        filtered_payload.setdefault('agent_name', 'unknown')
        filtered_payload.setdefault('memory_type', 'insight')
        filtered_payload.setdefault('content', '')
        
        return cls(**filtered_payload)


class QdrantMemorySystem:
    """
    Production-ready memory system using Qdrant Cloud
    FIXED: Improved memory retrieval with proper field handling
    
    WHY Qdrant Cloud:
    - Managed service (no Docker needed)
    - Scales automatically
    - Built-in persistence
    - Fast vector similarity search
    - Free tier available
    """
    
    def __init__(self):
        """Initialize connection to Qdrant Cloud"""
        
        # Get credentials from environment
        self.qdrant_url = os.getenv('QDRANT_URL')
        self.api_key = os.getenv('QDRANT_API_KEY')
        self.collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'agent_memories')
        
        if not self.qdrant_url or not self.api_key:
            raise ValueError(
                "Missing Qdrant Cloud credentials!\n"
                "Please set QDRANT_URL and QDRANT_API_KEY in your .env file.\n"
                "Get these from https://cloud.qdrant.io"
            )
        
        print(f"🧠 Connecting to Qdrant Cloud: {self.qdrant_url}")
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.qdrant_url,
            api_key=self.api_key,
            timeout=30,
            prefer_grpc=False  # Use REST API for cloud
        )
        
        # Initialize embedding model
        print("📚 Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Fast and good
        self.vector_size = 384  # Size for MiniLM
        
        # Create collection if it doesn't exist
        self._ensure_collection()
        
        # Cache for frequently accessed memories
        self.cache = {}
        
        print("✅ Memory system ready!")
    
    def _ensure_collection(self):
        """Create collection with proper indexes if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                print(f"📦 Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"✅ Collection created: {self.collection_name}")
            else:
                print(f"✅ Collection exists: {self.collection_name}")
                
                # Get collection info
                info = self.client.get_collection(self.collection_name)
                print(f"   • Points count: {info.points_count}")
                print(f"   • Vector size: {info.config.params.vectors.size}")
            
            # CREATE INDEXES for filtering
            print("📇 Creating/verifying indexes...")
            
            # Define indexes to create
            indexes = [
                ("client_id", PayloadSchemaType.KEYWORD),
                ("agent_name", PayloadSchemaType.KEYWORD),
                ("memory_type", PayloadSchemaType.KEYWORD),
                ("importance", PayloadSchemaType.FLOAT)
            ]
            
            for field_name, field_type in indexes:
                try:
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=field_name,
                        field_schema=field_type,
                        wait=True
                    )
                    print(f"   ✓ {field_name} index created")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ✓ {field_name} index exists")
                    else:
                        print(f"   ⚠️ {field_name} index error: {e}")
            
            print("✅ All indexes ready")
                
        except Exception as e:
            print(f"❌ Error with collection setup: {e}")
            raise
    
    def store_memory(
        self, 
        client_id: str,
        agent_name: str,
        memory_type: str,
        content: str,
        context: Optional[str] = None,
        importance: float = 0.5,
        quality_impact: float = 0.0
    ) -> str:
        """
        Store a memory in Qdrant
        
        WHY: Agents need to remember insights across sessions
        """
        try:
            # Create memory object
            memory = Memory(
                client_id=client_id,
                agent_name=agent_name,
                memory_type=memory_type,
                content=content,
                context=context,
                importance=importance,
                quality_impact=quality_impact
            )
            
            # Generate embedding
            embedding = self.encoder.encode(content).tolist()
            
            # Generate unique ID
            memory_id = hashlib.md5(
                f"{client_id}_{agent_name}_{content}_{datetime.now()}".encode()
            ).hexdigest()
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload=memory.to_dict()
                    )
                ],
                wait=True
            )
            
            print(f"💾 Stored memory for {agent_name}: {content[:50]}...")
            
            # Clear cache for this client/agent
            cache_key = f"{client_id}_{agent_name}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            return memory_id
            
        except Exception as e:
            print(f"❌ Error storing memory: {e}")
            import traceback
            print(traceback.format_exc())
            return None
    
    def retrieve_memories(
        self,
        client_id: str,
        agent_name: Optional[str] = None,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[Memory]:
        """
        Retrieve relevant memories using semantic search
        FIXED: Proper handling of payload fields
        
        WHY: Agents need context-aware memory retrieval
        """
        try:
            # Check cache first
            cache_key = f"{client_id}_{agent_name}_{memory_type}_{query}"
            if cache_key in self.cache:
                print(f"📦 Using cached memories for {cache_key[:30]}...")
                return self.cache[cache_key]
            
            # Build filters
            must_conditions = [
                FieldCondition(
                    key="client_id",
                    match=MatchValue(value=client_id)
                )
            ]
            
            if agent_name:
                must_conditions.append(
                    FieldCondition(
                        key="agent_name",
                        match=MatchValue(value=agent_name)
                    )
                )
            
            if memory_type:
                must_conditions.append(
                    FieldCondition(
                        key="memory_type",
                        match=MatchValue(value=memory_type)
                    )
                )
            
            if min_importance > 0:
                must_conditions.append(
                    FieldCondition(
                        key="importance",
                        range={"gte": min_importance}
                    )
                )
            
            # Perform search
            if query:
                # Semantic search with query
                query_vector = self.encoder.encode(query).tolist()
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    query_filter=Filter(must=must_conditions),
                    limit=limit
                )
            else:
                # Just retrieve with filters
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(must=must_conditions),
                    limit=limit,
                    with_payload=True,
                    with_vectors=False
                )
                results = scroll_result[0]  # Returns (points, next_offset)
            
            # Convert to Memory objects with proper field handling
            memories = []
            for point in results:
                try:
                    # Get payload from the point
                    if hasattr(point, 'payload'):
                        payload = point.payload
                    else:
                        payload = point
                    
                    # Create Memory using from_payload method
                    memory = Memory.from_payload(payload)
                    memories.append(memory)
                    
                    # Update access tracking if we have the point ID
                    if hasattr(point, 'id'):
                        self._update_access_count(point.id)
                        
                except Exception as e:
                    print(f"⚠️ Skipping invalid memory: {e}")
                    continue
            
            # Cache results
            self.cache[cache_key] = memories
            
            print(f"🔍 Retrieved {len(memories)} memories for {client_id}/{agent_name}")
            return memories
            
        except Exception as e:
            print(f"❌ Error retrieving memories: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def _update_access_count(self, point_id: str):
        """Update access count and timestamp for a memory"""
        try:
            # Get current point
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )
            
            if points:
                payload = points[0].payload
                payload['access_count'] = payload.get('access_count', 0) + 1
                payload['accessed_at'] = datetime.now().isoformat()
                
                # Update point
                self.client.set_payload(
                    collection_name=self.collection_name,
                    payload=payload,
                    points=[point_id],
                    wait=True
                )
        except Exception as e:
            # Silent fail for access count updates
            pass
    
    def record_learning(
        self,
        agent_name: str,
        insight: str,
        context: str,
        quality_before: float,
        quality_after: float
    ):
        """
        Record when an agent learns something new
        
        WHY: Track improvements and what causes them
        """
        improvement = quality_after - quality_before
        
        # Store as a special learning memory
        self.store_memory(
            client_id="SYSTEM",  # System-wide learning
            agent_name=agent_name,
            memory_type="learning",
            content=insight,
            context=context,
            importance=min(1.0, 0.5 + improvement),  # Higher importance for bigger improvements
            quality_impact=improvement
        )
        
        print(f"📈 {agent_name} learned: {insight[:50]}... (Quality: {quality_before:.2f} → {quality_after:.2f})")
    
    def get_agent_improvements(self, agent_name: str, days: int = 30) -> Dict[str, Any]:
        """
        Get improvement history for an agent
        
        WHY: Show learning progress over time
        """
        learnings = self.retrieve_memories(
            client_id="SYSTEM",
            agent_name=agent_name,
            memory_type="learning",
            limit=100
        )
        
        if not learnings:
            return {
                "total_learnings": 0,
                "avg_improvement": 0,
                "best_learning": None
            }
        
        improvements = [m.quality_impact for m in learnings if m.quality_impact > 0]
        
        best_learning = max(learnings, key=lambda m: m.quality_impact) if learnings else None
        
        return {
            "total_learnings": len(learnings),
            "avg_improvement": np.mean(improvements) if improvements else 0,
            "total_improvement": sum(improvements),
            "best_learning": best_learning.content if best_learning else None,
            "best_improvement": best_learning.quality_impact if best_learning else 0,
            "recent_learnings": [m.content for m in learnings[:5]]
        }
    
    def share_insights_between_agents(
        self,
        from_agent: str,
        to_agent: str,
        client_id: str,
        insight: str
    ):
        """
        Allow agents to share insights
        
        WHY: Cross-pollination of knowledge improves all agents
        """
        # Store for the receiving agent with metadata
        memory = Memory(
            client_id=client_id,
            agent_name=to_agent,
            memory_type="shared_insight",
            content=insight,
            context=f"Shared by {from_agent}",
            importance=0.7,
            shared_from=from_agent,
            shared_at=datetime.now().isoformat()
        )
        
        # Generate embedding and store
        try:
            embedding = self.encoder.encode(insight).tolist()
            memory_id = hashlib.md5(
                f"{client_id}_{to_agent}_shared_{insight}_{datetime.now()}".encode()
            ).hexdigest()
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload=memory.to_dict()
                    )
                ],
                wait=True
            )
            
            print(f"🤝 {from_agent} → {to_agent}: {insight[:50]}...")
            
        except Exception as e:
            print(f"❌ Error sharing insight: {e}")
    
    def get_client_context(self, client_id: str) -> Dict[str, List[str]]:
        """
        Get all context about a client across all agents
        
        WHY: Comprehensive understanding for better analysis
        """
        context = {}
        
        # Get memories from all agents
        all_memories = self.retrieve_memories(
            client_id=client_id,
            limit=50
        )
        
        # Group by agent
        for memory in all_memories:
            agent = memory.agent_name
            if agent not in context:
                context[agent] = []
            context[agent].append(memory.content)
        
        print(f"📚 Retrieved context for {client_id}: {len(all_memories)} total memories")
        return context
    
    def export_client_memories(self, client_id: str) -> Dict:
        """
        Export all memories for a client (GDPR compliance)
        
        WHY: Users own their data
        """
        memories = self.retrieve_memories(
            client_id=client_id,
            limit=1000  # Get all
        )
        
        return {
            "client_id": client_id,
            "export_date": datetime.now().isoformat(),
            "total_memories": len(memories),
            "memories": [m.to_dict() for m in memories]
        }
    
    def delete_client_memories(self, client_id: str) -> bool:
        """
        Delete all memories for a client (GDPR right to be forgotten)
        
        WHY: Privacy compliance
        """
        try:
            # Get all memories for this client to get their IDs
            all_memories = []
            offset = None
            
            while True:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="client_id",
                                match=MatchValue(value=client_id)
                            )
                        ]
                    ),
                    limit=100,
                    offset=offset
                )
                
                points, next_offset = scroll_result
                if not points:
                    break
                    
                all_memories.extend(points)
                offset = next_offset
                
                if not next_offset:
                    break
            
            if not all_memories:
                print(f"No memories found for {client_id}")
                return True
            
            # Extract IDs
            memory_ids = [point.id for point in all_memories if hasattr(point, 'id')]
            
            if memory_ids:
                # Delete the points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=memory_ids
                )
                print(f"✅ Deleted {len(memory_ids)} memories for {client_id}")
            
            # Clear cache
            self.cache = {k: v for k, v in self.cache.items() if not k.startswith(client_id)}
            
            return True
            
        except Exception as e:
            print(f"❌ Error deleting memories: {e}")
            import traceback
            print(traceback.format_exc())
            return False


# ============================================
# Integration with Agents
# ============================================

class MemoryEnabledAgent:
    """
    Mixin to add memory capabilities to any agent
    
    WHY: Easy integration without modifying existing agents
    """
    
    def __init__(self, memory_system: QdrantMemorySystem):
        self.memory = memory_system
        self.agent_name = self.__class__.__name__
        print(f"🧠 {self.agent_name} memory-enabled")
    
    def remember_insight(self, client_id: str, insight: str, importance: float = 0.5):
        """Store an insight for future use"""
        self.memory.store_memory(
            client_id=client_id,
            agent_name=self.agent_name,
            memory_type="insight",
            content=insight,
            importance=importance
        )
    
    def recall_insights(self, client_id: str, query: Optional[str] = None) -> List[str]:
        """Recall relevant insights"""
        memories = self.memory.retrieve_memories(
            client_id=client_id,
            agent_name=self.agent_name,
            query=query,
            memory_type="insight"
        )
        return [m.content for m in memories]
    
    def learn_from_feedback(self, feedback: str, quality_before: float, quality_after: float):
        """Record learning from feedback"""
        self.memory.record_learning(
            agent_name=self.agent_name,
            insight=feedback,
            context="User coaching",
            quality_before=quality_before,
            quality_after=quality_after
        )


# ============================================
# Usage Example and Test
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Qdrant Cloud Memory System")
    print("=" * 60)
    
    # Initialize system
    memory = QdrantMemorySystem()
    
    # Store some test memories
    memory.store_memory(
        client_id="test_client_001",
        agent_name="psychological",
        memory_type="insight",
        content="Client shows fear of success pattern - scaling anxiety",
        importance=0.9
    )
    
    memory.store_memory(
        client_id="test_client_001",
        agent_name="voice",
        memory_type="pattern",
        content="Uses 'lifestyle business' defensively when discussing growth",
        importance=0.8
    )
    
    # Record learning
    memory.record_learning(
        agent_name="psychological",
        insight="Identity conflicts are more important than surface fears",
        context="Analysis of 50 coaching clients",
        quality_before=0.82,
        quality_after=0.91
    )
    
    # Retrieve memories
    print("\n📚 Retrieving memories for test_client_001:")
    memories = memory.retrieve_memories(
        client_id="test_client_001",
        limit=5
    )
    for mem in memories:
        print(f"   • [{mem.agent_name}] {mem.content}")
    
    # Get agent improvements
    print("\n📈 Psychological agent improvements:")
    improvements = memory.get_agent_improvements("psychological")
    print(f"   • Total learnings: {improvements['total_learnings']}")
    print(f"   • Average improvement: {improvements['avg_improvement']:.2%}")
    print(f"   • Best learning: {improvements['best_learning']}")
    
    # Test cross-agent sharing
    print("\n🤝 Testing cross-agent knowledge sharing:")
    memory.share_insights_between_agents(
        from_agent="psychological",
        to_agent="voice",
        client_id="test_client_001",
        insight="Identity crisis manifests in defensive language about growth"
    )
    
    # Get full client context
    print("\n📊 Full client context:")
    context = memory.get_client_context("test_client_001")
    for agent, insights in context.items():
        print(f"   {agent}: {len(insights)} insights")
    
    print("\n✅ Memory system test complete!")