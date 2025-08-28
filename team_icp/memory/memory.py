# memory/memory.py or memory.py (depending on your structure)

"""
Memory system for agent interactions using Qdrant vector database.
Handles storage, retrieval, and sharing of agent memories/insights.
"""

import os
import uuid
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, 
    VectorParams, 
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
    FilterSelector
)
from sentence_transformers import SentenceTransformer
import numpy as np


class Memory(BaseModel):
    """Memory model with all required fields for Qdrant storage"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: str
    client_id: str
    agent_name: str
    memory_type: str = "insight"  # Types: insight, analysis, shared, reflection
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    accessed_at: Optional[datetime] = None  # Track when memory was last accessed
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None  # Store embedding vector
    
    class Config:
        extra = "ignore"  # Ignore unexpected fields from database
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class MemorySystem:
    """Main memory system for managing agent memories in Qdrant"""
    
    def __init__(
        self,
        qdrant_url: str,
        qdrant_api_key: str,
        collection_name: str = "agent_memories",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """Initialize memory system with Qdrant connection"""
        print(f"🧠 Connecting to Qdrant Cloud: {qdrant_url}")
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_api_key,
            timeout=30
        )
        
        # Initialize embedding model
        print(f"📚 Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model)
        self.vector_size = self.encoder.get_sentence_embedding_dimension()
        
        # Setup collection
        self.collection_name = collection_name
        self._setup_collection()
        
        print("✅ Memory system ready!")
    
    def _setup_collection(self):
        """Create or verify Qdrant collection with proper configuration"""
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if not collection_exists:
                print(f"📦 Creating new collection: {self.collection_name}")
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
            
            # Create indexes for better performance
            self._create_indexes()
            
        except Exception as e:
            print(f"❌ Error setting up collection: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes on frequently searched fields"""
        print("📇 Creating/verifying indexes...")
        
        index_fields = ["client_id", "agent_name", "memory_type", "importance"]
        
        for field in index_fields:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    wait=True
                )
                print(f"   ✓ {field} index created")
            except Exception as e:
                # Index might already exist, that's fine
                if "already exists" not in str(e).lower():
                    print(f"   ⚠️ Could not create index for {field}: {e}")
        
        print("✅ All indexes ready")
    
    def store_memory(
        self,
        content: str,
        client_id: str,
        agent_name: str,
        memory_type: str = "insight",
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """Store a new memory in the vector database"""
        try:
            # Create memory object
            memory = Memory(
                content=content,
                client_id=client_id,
                agent_name=agent_name,
                memory_type=memory_type,
                importance=importance,
                metadata=metadata or {}
            )
            
            # Generate embedding
            embedding = self.encoder.encode(content, convert_to_tensor=False).tolist()
            memory.embedding = embedding
            
            # Create point for Qdrant
            point = PointStruct(
                id=memory.id,
                vector=embedding,
                payload=memory.dict(exclude={"embedding"})
            )
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True
            )
            
            print(f"💾 Stored memory for {agent_name}: {content[:50]}...")
            return memory
            
        except Exception as e:
            print(f"❌ Error storing memory: {e}")
            raise
    
    def retrieve_memories(
        self,
        client_id: str,
        agent_name: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 10,
        importance_threshold: float = 0.0
    ) -> List[Memory]:
        """Retrieve memories based on filters"""
        try:
            # Build filter conditions
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
            
            if importance_threshold > 0:
                must_conditions.append(
                    FieldCondition(
                        key="importance",
                        range={"gte": importance_threshold}
                    )
                )
            
            # Search in Qdrant
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(must=must_conditions),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            # Convert to Memory objects
            memories = []
            for point in results[0]:
                try:
                    # Clean payload data
                    payload = point.payload.copy()
                    
                    # Handle datetime fields
                    if "timestamp" in payload and isinstance(payload["timestamp"], str):
                        payload["timestamp"] = datetime.fromisoformat(payload["timestamp"])
                    
                    if "accessed_at" in payload:
                        if isinstance(payload["accessed_at"], str):
                            payload["accessed_at"] = datetime.fromisoformat(payload["accessed_at"])
                    
                    # Create Memory object
                    memory = Memory(**payload)
                    memories.append(memory)
                    
                except Exception as e:
                    print(f"⚠️ Skipping invalid memory: {e}")
                    continue
            
            # Update accessed_at for retrieved memories
            if memories:
                self._update_access_time([m.id for m in memories])
            
            return memories
            
        except Exception as e:
            print(f"❌ Error retrieving memories: {e}")
            # Return empty list instead of crashing
            return []
    
    def search_similar_memories(
        self,
        query: str,
        client_id: str,
        agent_name: Optional[str] = None,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar memories using semantic search"""
        try:
            # Generate query embedding
            query_vector = self.encoder.encode(query, convert_to_tensor=False).tolist()
            
            # Build filter
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
            
            # Search
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=Filter(must=must_conditions),
                limit=limit,
                score_threshold=score_threshold
            )
            
            # Format results
            results = []
            for hit in search_result:
                payload = hit.payload.copy()
                payload["score"] = hit.score
                results.append(payload)
            
            return results
            
        except Exception as e:
            print(f"❌ Error searching memories: {e}")
            return []
    
    def share_memory_between_agents(
        self,
        memory_id: str,
        from_agent: str,
        to_agent: str,
        client_id: str
    ) -> bool:
        """Share a memory from one agent to another"""
        try:
            # Retrieve original memory
            original = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[memory_id]
            )
            
            if not original:
                print(f"⚠️ Memory {memory_id} not found")
                return False
            
            # Create shared copy
            original_data = original[0].payload.copy()
            shared_memory = Memory(
                content=original_data["content"],
                client_id=client_id,
                agent_name=to_agent,
                memory_type="shared",
                importance=original_data.get("importance", 0.5),
                metadata={
                    **original_data.get("metadata", {}),
                    "shared_from": from_agent,
                    "original_id": memory_id,
                    "shared_at": datetime.now().isoformat()
                }
            )
            
            # Store shared memory
            self.store_memory(
                content=shared_memory.content,
                client_id=shared_memory.client_id,
                agent_name=shared_memory.agent_name,
                memory_type=shared_memory.memory_type,
                importance=shared_memory.importance,
                metadata=shared_memory.metadata
            )
            
            print(f"🤝 {from_agent} → {to_agent}: {shared_memory.content[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error sharing memory: {e}")
            return False
    
    def _update_access_time(self, memory_ids: List[str]):
        """Update the accessed_at timestamp for memories"""
        try:
            now = datetime.now()
            for memory_id in memory_ids:
                self.client.set_payload(
                    collection_name=self.collection_name,
                    payload={"accessed_at": now.isoformat()},
                    points=[memory_id]
                )
        except Exception as e:
            # Non-critical error, just log it
            print(f"⚠️ Could not update access time: {e}")
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[memory_id]
            )
            print(f"🗑️ Deleted memory: {memory_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting memory: {e}")
            return False
    
    def clear_agent_memories(self, client_id: str, agent_name: str) -> int:
        """Clear all memories for a specific agent"""
        try:
            # Get all memories for this agent
            memories = self.retrieve_memories(
                client_id=client_id,
                agent_name=agent_name,
                limit=1000
            )
            
            # Delete them
            if memories:
                memory_ids = [m.id for m in memories]
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=memory_ids
                )
                print(f"🗑️ Cleared {len(memories)} memories for {agent_name}")
                return len(memories)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error clearing memories: {e}")
            return 0