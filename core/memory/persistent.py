# core/memory/persistent.py
"""Level 5 Memory System - Start simple, upgrade to Supabase later"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class PersistentMemory:
    """Level 5 persistent memory across sessions"""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        self.patterns_file = os.path.join(memory_dir, "patterns.json")
        self.experiences_file = os.path.join(memory_dir, "experiences.json")
        self._load_memory()
    
    def _load_memory(self):
        """Load existing memory from disk"""
        # Load patterns
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                self.patterns = json.load(f)
        else:
            self.patterns = {"industries": {}, "successful_approaches": []}
        
        # Load experiences
        if os.path.exists(self.experiences_file):
            with open(self.experiences_file, 'r') as f:
                self.experiences = json.load(f)
        else:
            self.experiences = []
    
    def store_experience(self, experience: Dict[str, Any]) -> None:
        """Store a complete experience"""
        experience['timestamp'] = datetime.now().isoformat()
        experience['id'] = f"exp_{len(self.experiences)}"
        
        self.experiences.append(experience)
        self._save_experiences()
        
        # Extract patterns from successful experiences
        if experience.get('success_score', 0) > 0.8:
            self._extract_and_store_patterns(experience)
    
    def recall_similar(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recall similar experiences - simple keyword matching for now"""
        # Extract keywords from context
        keywords = set(context.lower().split())
        
        # Score each experience
        scored_experiences = []
        for exp in self.experiences:
            exp_text = f"{exp.get('context', '')} {exp.get('industry', '')}".lower()
            exp_keywords = set(exp_text.split())
            
            # Simple similarity score
            common_keywords = keywords.intersection(exp_keywords)
            score = len(common_keywords) / max(len(keywords), 1)
            
            if score > 0.1:  # Minimum threshold
                scored_experiences.append((score, exp))
        
        # Sort by score and return top matches
        scored_experiences.sort(key=lambda x: x[0], reverse=True)
        return [exp for _, exp in scored_experiences[:limit]]
    
    def get_industry_patterns(self, industry: str) -> List[Dict[str, Any]]:
        """Get successful patterns for an industry"""
        return self.patterns["industries"].get(industry.lower(), [])
    
    def _extract_and_store_patterns(self, experience: Dict[str, Any]) -> None:
        """Extract patterns from successful experience"""
        industry = experience.get('industry', 'general').lower()
        
        if industry not in self.patterns["industries"]:
            self.patterns["industries"][industry] = []
        
        # Extract pattern
        pattern = {
            "type": experience.get('analysis_type', 'general'),
            "approach": experience.get('approach_used', 'standard'),
            "success_score": experience.get('success_score', 0),
            "key_insights": experience.get('key_insights', []),
            "timestamp": datetime.now().isoformat()
        }
        
        self.patterns["industries"][industry].append(pattern)
        self._save_patterns()
    
    def _save_experiences(self):
        """Save experiences to disk"""
        with open(self.experiences_file, 'w') as f:
            json.dump(self.experiences, f, indent=2)
    
    def _save_patterns(self):
        """Save patterns to disk"""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
