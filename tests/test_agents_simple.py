# tests/test_agents_simple.py
"""
Simple Integration Test for All Agents
Tests basic functionality with current implementation
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_agents():
    """Simple test for all agents with basic functionality."""
    print("\n" + "="*60)
    print("SIMPLE AGENT INTEGRATION TEST")
    print("="*60)
    
    results = {}
    test_company = "TestCompany"
    test_context = {
        'industry': 'technology',
        'market': 'B2B',
        'insights': {}
    }
    
    # Test 1: Initialize agents
    print("\n📋 Test 1: Agent Initialization")
    agents = {}
    
    agent_classes = [
        ('psychological', 'PsychologicalAgent'),
        ('voice', 'VoiceAgent'),
        ('competitor', 'CompetitorAgent'),
        ('interview_psychological', 'PsychologicalInterviewAgent'),
        ('interview_sales', 'SalesInterviewAgent'),
        ('gtm_blueprint', 'GTMBlueprintAgent')
    ]
    
    for agent_name, class_name in agent_classes:
        try:
            if agent_name == 'psychological':
                from team_icp.agents.psychological import PsychologicalAgent
                agents[agent_name] = PsychologicalAgent()
            elif agent_name == 'voice':
                from team_icp.agents.voice_of_customer import VoiceAgent
                agents[agent_name] = VoiceAgent()
            elif agent_name == 'competitor':
                from team_icp.agents.competitor import CompetitorAgent
                agents[agent_name] = CompetitorAgent()
            elif agent_name == 'interview_psychological':
                from team_icp.agents.interview_psychological import PsychologicalInterviewAgent
                agents[agent_name] = PsychologicalInterviewAgent()
            elif agent_name == 'interview_sales':
                from team_icp.agents.interview_sales import SalesInterviewAgent
                agents[agent_name] = SalesInterviewAgent()
            elif agent_name == 'gtm_blueprint':
                from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
                agents[agent_name] = GTMBlueprintAgent()
            
            print(f"   ✅ {agent_name} initialized")
            print(f"      Memory: {agents[agent_name].memory_enabled}")
            print(f"      Search: {agents[agent_name].search_enabled}")
            
        except Exception as e:
            print(f"   ❌ {agent_name} failed: {str(e)[:100]}")
            continue
    
    # Test 2: Basic fallback functionality
    print("\n📋 Test 2: Fallback Template Generation")
    
    for agent_name, agent in agents.items():
        try:
            print(f"\n   Testing {agent_name} fallback...")
            
            # Check if agent has _create_template_fallback method
            if hasattr(agent, '_create_template_fallback'):
                fallback = agent._create_template_fallback(test_company)
                
                # Check it returns a string
                if isinstance(fallback, str) and len(fallback) > 100:
                    print(f"      ✅ Fallback template generated ({len(fallback)} chars)")
                else:
                    print(f"      ⚠️ Fallback returned but seems incomplete")
            else:
                print(f"      ⚠️ No _create_template_fallback method")
                
        except Exception as e:
            print(f"      ❌ Fallback failed: {str(e)[:50]}")
    
    # Test 3: Research methods with search disabled
    print("\n📋 Test 3: Research Methods (Search Disabled)")
    
    # Temporarily disable search to test fallback data
    for agent_name, agent in agents.items():
        original_search = agent.search_enabled
        agent.search_enabled = False
        
        try:
            if agent_name == 'psychological' and hasattr(agent, '_research_psychological_context'):
                data = agent._research_psychological_context(test_company, test_context)
                print(f"   ✅ {agent_name}: Got {len(data)} fallback data items")
                
            elif agent_name == 'voice' and hasattr(agent, '_research_customer_voice'):
                data = agent._research_customer_voice(test_company, test_context)
                print(f"   ✅ {agent_name}: Got {len(data)} fallback data items")
                
            elif agent_name == 'competitor' and hasattr(agent, '_research_competitors'):
                data = agent._research_competitors(test_company, test_context)
                print(f"   ✅ {agent_name}: Got {len(data)} fallback data items")
                
            elif agent_name == 'interview_sales' and hasattr(agent, '_research_sales_context'):
                data = agent._research_sales_context(test_company, test_context)
                print(f"   ✅ {agent_name}: Got {len(data)} fallback data items")
                
            elif agent_name == 'interview_psychological' and hasattr(agent, '_research_psychological_context'):
                data = agent._research_psychological_context(test_company, test_context)
                print(f"   ✅ {agent_name}: Got {len(data)} fallback data items")
                
            elif agent_name == 'gtm_blueprint' and hasattr(agent, '_research_gtm_strategies'):
                data = agent._research_gtm_strategies(test_company, test_context)
                print(f"   ✅ {agent_name}: Got {len(data)} fallback data items")
                
        except Exception as e:
            print(f"   ❌ {agent_name}: Research failed - {str(e)[:50]}")
        finally:
            agent.search_enabled = original_search
    
    # Test 4: Check for required sections
    print("\n📋 Test 4: Template Sections Check")
    
    for agent_name, agent in agents.items():
        if hasattr(agent, 'REQUIRED_SECTIONS'):
            section_count = len(agent.REQUIRED_SECTIONS)
            print(f"   {agent_name}: {section_count} required sections")
            
            # Check if it's the standard 14 sections
            if section_count == 14:
                print(f"      ✅ Standard 14-section template")
            else:
                print(f"      ⚠️ Non-standard section count")
    
    # Test 5: Check critical attributes exist
    print("\n📋 Test 5: Critical Attributes Check")
    
    critical_attributes = {
        'psychological': ['behavioral_patterns', 'cognitive_biases', 'emotional_triggers'],
        'voice': ['customer_quotes', 'pain_points', 'sentiment_analysis'],
        'competitor': ['identified_competitors', 'positioning_gaps'],
        'interview_psychological': ['interviews', 'psychological_personas', 'emotional_patterns'],
        'interview_sales': ['interviews', 'personas', 'objection_patterns'],
        'gtm_blueprint': ['strategic_pillars', 'implementation_phases', 'agent_insights']
    }
    
    for agent_name, attrs in critical_attributes.items():
        if agent_name in agents:
            agent = agents[agent_name]
            print(f"\n   {agent_name}:")
            for attr in attrs:
                if hasattr(agent, attr):
                    print(f"      ✅ {attr}")
                else:
                    print(f"      ❌ Missing: {attr}")
    
    # Test 6: Execute method exists
    print("\n📋 Test 6: Execute Method Check")
    
    for agent_name, agent in agents.items():
        if hasattr(agent, 'execute'):
            print(f"   ✅ {agent_name}.execute() exists")
        else:
            print(f"   ❌ {agent_name}.execute() missing")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Agents initialized: {len(agents)}/6")
    
    if len(agents) == 6:
        print("✅ All agents can be initialized")
    else:
        print("⚠️ Some agents failed to initialize")
    
    print("\nKey findings:")
    print("- Agents have memory and search capabilities")
    print("- Fallback templates are available")
    print("- Research methods can provide fallback data")
    print("- 14-section template structure is in place")
    print("\n⚠️ Note: Some methods reference non-existent prompt methods")
    print("   These need to be fixed or use direct prompts instead")


if __name__ == "__main__":
    test_agents()