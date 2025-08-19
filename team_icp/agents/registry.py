# team_icp/agents/registry.py
"""
Agent Registry System for Level 4 AI Agent System
Manages all 6 agents and their configurations
"""

import os
import sys
from typing import Dict, Any, Optional

# Add parent directory to path to import agents
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class AgentRegistry:
    """Registry for all available agents in the system"""
    
    def __init__(self):
        """Initialize the agent registry"""
        self.agents = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load all available agents"""
        # Define all 6 agents with their configurations
        self.agents = {
            'psychological': {
                'name': 'Psychological Agent',
                'status': 'operational',
                'quality_target': 0.85,
                'current_quality': 0.82,
                'description': 'Analyzes deep psychological patterns and unconscious motivations',
                'emoji': '🧠',
                'capabilities': [
                    'Applies 10+ psychological frameworks',
                    'Identifies identity contradictions',
                    'Reveals unconscious motivations',
                    'Produces 2000+ word analysis'
                ]
            },
            'voice_of_customer': {
                'name': 'Voice of Customer Agent',
                'status': 'operational',
                'quality_target': 0.80,
                'current_quality': 0.92,
                'description': 'Extracts authentic customer language and pain points',
                'emoji': '🗣️',
                'capabilities': [
                    'Extracts 25+ customer phrases',
                    'Captures pain & aspiration language',
                    'Creates copy-ready headlines',
                    'Identifies context-specific terminology'
                ]
            },
            'interview_psychological': {
                'name': 'Interview Agent (Psychological)',
                'status': 'operational',
                'quality_target': 0.75,
                'current_quality': 0.85,
                'description': 'Conducts deep psychological interviews',
                'emoji': '🎭',
                'capabilities': [
                    'Conducts 3 complete interviews',
                    'Natural dialogue flow',
                    '300+ words per interview',
                    'Shows emotional vulnerability'
                ]
            },
            'interview_sales': {
                'name': 'Interview Agent (Sales)',
                'status': 'operational',
                'quality_target': 0.75,
                'current_quality': 0.91,
                'description': 'Uncovers buying psychology and purchase triggers',
                'emoji': '💰',
                'capabilities': [
                    'Focuses on buying psychology',
                    'Identifies purchase triggers',
                    'Reveals decision barriers',
                    'Uncovers objections'
                ]
            },
            'competitor': {
                'name': 'Competitor Analysis Agent',
                'status': 'operational',
                'quality_target': 0.75,
                'current_quality': 0.80,
                'description': 'Provides actionable competitive intelligence',
                'emoji': '🔍',
                'capabilities': [
                    'Identifies 5+ competitors',
                    'Deep analysis on top 3',
                    'Maps positioning gaps',
                    'Finds weaknesses to exploit'
                ]
            },
            'gtm_blueprint': {
                'name': 'GTM Blueprint Agent',
                'status': 'operational',
                'quality_target': 0.85,
                'current_quality': 0.84,
                'description': 'Synthesizes comprehensive go-to-market strategy',
                'emoji': '📋',
                'capabilities': [
                    'Synthesizes all agent insights',
                    'Produces 2500+ word strategy',
                    'Creates specific action plans',
                    'Delivers executive-ready output'
                ]
            }
        }
    
    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered agents"""
        return self.agents
    
    def get_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get a specific agent by name"""
        return self.agents.get(agent_name)
    
    def get_operational_agents(self) -> Dict[str, Dict[str, Any]]:
        """Get only operational agents"""
        return {
            name: agent 
            for name, agent in self.agents.items() 
            if agent['status'] == 'operational'
        }
    
    def get_agents_meeting_quality(self) -> Dict[str, Dict[str, Any]]:
        """Get agents meeting their quality targets"""
        return {
            name: agent 
            for name, agent in self.agents.items() 
            if agent['current_quality'] >= agent['quality_target']
        }
    
    def get_agent_status_summary(self) -> str:
        """Get a summary of all agent statuses"""
        total = len(self.agents)
        operational = len(self.get_operational_agents())
        meeting_quality = len(self.get_agents_meeting_quality())
        
        summary = f"""
🤖 **Agent System Status**
------------------------
Total Agents: {total}
Operational: {operational}/{total}
Meeting Quality Targets: {meeting_quality}/{total}

**Individual Agent Status:**
"""
        for name, agent in self.agents.items():
            quality_indicator = "✅" if agent['current_quality'] >= agent['quality_target'] else "⚠️"
            summary += f"\n{agent['emoji']} **{agent['name']}**"
            summary += f"\n   Status: {agent['status'].upper()}"
            summary += f"\n   Quality: {agent['current_quality']:.2f}/{agent['quality_target']:.2f} {quality_indicator}"
            summary += f"\n   {agent['description']}"
        
        return summary
    
    def update_agent_quality(self, agent_name: str, new_quality: float) -> bool:
        """Update an agent's quality score"""
        if agent_name in self.agents:
            self.agents[agent_name]['current_quality'] = new_quality
            return True
        return False
    
    def add_learning(self, agent_name: str, learning: str) -> bool:
        """Add a learning/improvement to an agent"""
        if agent_name in self.agents:
            if 'learnings' not in self.agents[agent_name]:
                self.agents[agent_name]['learnings'] = []
            self.agents[agent_name]['learnings'].append(learning)
            # Simulate quality improvement
            current = self.agents[agent_name]['current_quality']
            self.agents[agent_name]['current_quality'] = min(1.0, current + 0.05)
            return True
        return False

# For testing the registry directly
if __name__ == "__main__":
    registry = AgentRegistry()
    print("Registered Agents:")
    for name, agent in registry.get_all_agents().items():
        print(f"  - {name}: {agent['name']} ({agent['status']})")
    
    print("\n" + registry.get_agent_status_summary())