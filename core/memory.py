import chromadb
from typing import List, Dict

class SimpleMemory:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("icp_memory")

    def store(self, data: List[Dict]):
        ids = [str(i) for i in range(len(data))]
        self.collection.add(documents=[d['content'] for d in data], ids=ids)

    def recall(self, query: str, limit: int = 3):
        return self.collection.query(query_texts=[query], n_results=limit)['documents'][0]
