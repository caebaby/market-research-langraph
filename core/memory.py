from supabase import create_client, Client
from typing import List, Dict
import os

class HybridMemory:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        self.client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
        self.table = "agent_memory"

    def store(self, data: List[Dict]):
        if self.client:
            self.client.table(self.table).insert(data).execute()

    def recall(self, query: str, limit: int = 3) -> List[Dict]:
        if self.client:
            return self.client.table(self.table).select("*").limit(limit).execute().data
        return []
