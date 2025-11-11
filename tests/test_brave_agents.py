#!/usr/bin/env python3
"""
Test Suite for Brave-Enabled Agents - FIXED IMPORTS
"""

import os
import sys
import traceback
from datetime import datetime

# Add parent directory to Python path (same as your other test files)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Now we can import using the same pattern as graph.py
import importlib

def load_agent_class(module_path: str, class_name: str):
    """Dynamically load agent class like graph.py does"""
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        print(f"❌ Failed to load {class_name} from {module_path}: {e}")
        return None

# Test each agent individually
def test_agents():
    """Test agents using the same loading mechanism as graph.py"""
    
    print("=" * 60)
    print("Testing Brave Search in All Agents")
    print("=" * 60)
    
    # Use the EXACT mapping from graph.py
    agent_mappings = {
        "psychological": ("team_icp.agents.psychological", "PsychologicalAnalysisAgent"),
        "voice_of_customer": ("team_icp.agents.voice_of_customer", "VoiceAgent"),  
        "competitor": ("team_icp.agents.competitor", "CompetitorAgent"),
        "interview_psychological": ("team_icp.agents.interview_psychological", "InterviewPsychologicalAgent"),
        "interview_sales": ("team_icp.agents.interview_sales", "InterviewSalesAgent"),
        "gtm_blueprint": ("team_icp.agents.gtm_blueprint", "GTMBlueprintAgent"),
    }
    
    # Get LLM
    try:
        from core.config import Config
        llm = Config.get_llm("psychological")
        print(f"[INFO] Using {Config.LLM_MODEL} for all agents\n")
    except Exception as e:
        print(f"[ERROR] Failed to get LLM: {e}")
        return
    
    # Test context
    context = {
        "industry": "SaaS",
        "market_segment": "enterprise",
        "shared_insights": {}
    }
    
    for agent_name, (module_path, class_name) in agent_mappings.items():
        print(f"\n{agent_name}:")
        
        # Check Brave API
        if os.getenv("BRAVE_API_KEY"):
            print(f"  Brave API: ✅ Available")
        else:
            print(f"  Brave API: ❌ Not configured")
        
        try:
            # Load agent class
            AgentClass = load_agent_class(module_path, class_name)
            if not AgentClass:
                print(f"  ❌ Failed to load agent class")
                continue
            
            # Initialize agent  
            print(f"\n[{agent_name}] Starting analysis for Slack")
            agent = AgentClass()
            
            # Get the right method name for each agent
            method_map = {
                "psychological": "analyze_psychology",
                "voice_of_customer": "extract_customer_voice",
                "competitor": "analyze_competition", 
                "interview_psychological": "conduct_interviews",
                "interview_sales": "conduct_sales_interviews",
                "gtm_blueprint": "create_gtm_blueprint"
            }
            
            method_name = method_map.get(agent_name)
            if not method_name or not hasattr(agent, method_name):
                print(f"  ❌ Method {method_name} not found")
                continue
                
            # Call the method
            method = getattr(agent, method_name)
            result = method("Slack", context)
            
            # Show results
            word_count = result.get('word_count', 0)
            quality = result.get('quality_score', 0)
            search = result.get('search_enabled', False)
            
            print(f"  Output: {word_count} words")
            print(f"  Quality: {quality:.2f}")
            print(f"  Search Used: {'Yes' if search else 'No'}")
            
        except Exception as e:
            print(f"\n{agent_name}: ❌ Error - {str(e)}")
            if os.getenv('DEBUG'):
                traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Test Complete!")

if __name__ == "__main__":
    test_agents()