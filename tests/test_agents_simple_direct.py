#!/usr/bin/env python3
"""
Simple direct test for agents - focus on what works
Test each agent using its process method
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import inspect  # Add this for signature checking

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from langchain_anthropic import ChatAnthropic
from colorama import init, Fore, Style

init(autoreset=True)

def test_gtm_blueprint():
    """Test GTM Blueprint agent directly"""
    print(f"\n{Fore.CYAN}Testing GTM Blueprint Agent{Style.RESET_ALL}")
    print("-" * 50)
    
    from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
    
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.7,
        max_tokens=4000
    )
    
    agent = GTMBlueprintAgent()
    
    task = """Create GTM strategy for AI-powered customer success platform targeting VPs at Series B-D SaaS companies."""
    
    shared_insights = {
        'psychological': {'summary': 'Fear of churn blame. Identity tied to team success.'},
        'voice': {'summary': 'Language: proactive, at-risk. Never: automate.'},
        'competitor': {'summary': 'Gainsight: complex. ChurnZero: lacks AI.'}
    }
    
    try:
        result = agent.process(task, shared_insights, llm)
        output = result if isinstance(result, str) else str(result)
        word_count = len(output.split())
        
        print(f"✅ Success! Generated {word_count} words")
        print(f"   Target: 2500-3000 words")
        print(f"   Status: {'PASSED' if word_count >= 2500 else 'NEEDS MORE'}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_psychological():
    """Test Psychological agent directly"""
    print(f"\n{Fore.CYAN}Testing Psychological Agent{Style.RESET_ALL}")
    print("-" * 50)
    
    try:
        from team_icp.agents.psychological import PsychologicalAgent
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4000
        )
        
        agent = PsychologicalAgent()
        
        task = """Analyze the psychology of VPs of Customer Success at Series B-D SaaS companies."""
        
        shared_insights = {}
        
        # Try different methods
        if hasattr(agent, 'process'):
            result = agent.process(task, shared_insights, llm)
        elif hasattr(agent, '_generate_response'):
            # Check the signature to call it correctly
            import inspect
            sig = inspect.signature(agent._generate_response)
            params = list(sig.parameters.keys())
            
            if 'memories' in params:
                # New signature with memories
                memories = []
                result = agent._generate_response(task, memories, llm)
            else:
                # Old signature without memories
                result = agent._generate_response(task, llm)
        else:
            print("   No suitable method found")
            return False
            
        output = result if isinstance(result, str) else str(result)
        word_count = len(output.split())
        
        print(f"✅ Success! Generated {word_count} words")
        print(f"   Target: 1200-1500 words")
        print(f"   Status: {'PASSED' if word_count >= 1200 else 'NEEDS MORE'}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice():
    """Test Voice agent directly"""
    print(f"\n{Fore.CYAN}Testing Voice Agent{Style.RESET_ALL}")
    print("-" * 50)
    
    try:
        from team_icp.agents.voice import VoiceAgent
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4000
        )
        
        agent = VoiceAgent()
        
        task = """Create voice patterns for messaging to VPs of Customer Success."""
        
        shared_insights = {'psychological': {'summary': 'Fear-driven, identity tied to metrics.'}}
        
        # Try different methods
        if hasattr(agent, 'process'):
            result = agent.process(task, shared_insights, llm)
        elif hasattr(agent, '_generate_response'):
            # Check the signature to call it correctly
            sig = inspect.signature(agent._generate_response)
            params = list(sig.parameters.keys())
            
            if 'memories' in params:
                # New signature with memories
                memories = []
                result = agent._generate_response(task, memories, llm)
            else:
                # Old signature without memories
                result = agent._generate_response(task, llm)
        else:
            print("   No suitable method found")
            return False
            
        output = result if isinstance(result, str) else str(result)
        word_count = len(output.split())
        
        print(f"✅ Success! Generated {word_count} words")
        print(f"   Target: 1200-1500 words")
        print(f"   Status: {'PASSED' if word_count >= 1200 else 'NEEDS MORE'}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_competitor():
    """Test Competitor agent directly"""
    print(f"\n{Fore.CYAN}Testing Competitor Agent{Style.RESET_ALL}")
    print("-" * 50)
    
    try:
        from team_icp.agents.competitor import CompetitorAgent
        
        llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4000
        )
        
        agent = CompetitorAgent()
        
        task = """Analyze competitive landscape for AI customer success platforms."""
        
        shared_insights = {}
        
        # Try different methods
        if hasattr(agent, 'process'):
            result = agent.process(task, shared_insights, llm)
        elif hasattr(agent, '_generate_response'):
            # Check the signature to call it correctly
            sig = inspect.signature(agent._generate_response)
            params = list(sig.parameters.keys())
            
            if 'memories' in params:
                # New signature with memories
                memories = []
                result = agent._generate_response(task, memories, llm)
            else:
                # Old signature without memories
                result = agent._generate_response(task, llm)
        else:
            print("   No suitable method found")
            return False
            
        output = result if isinstance(result, str) else str(result)
        word_count = len(output.split())
        
        print(f"✅ Success! Generated {word_count} words")
        print(f"   Target: 1200-1500 words")
        print(f"   Status: {'PASSED' if word_count >= 1200 else 'NEEDS MORE'}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print("🚀 SIMPLE DIRECT AGENT TESTING")
    print("Testing each agent's ability to generate content")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    results = {
        "GTM Blueprint": test_gtm_blueprint(),
        "Psychological": test_psychological(),
        "Voice": test_voice(),
        "Competitor": test_competitor()
    }
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for agent, success in results.items():
        status = f"{Fore.GREEN}✅ WORKING{Style.RESET_ALL}" if success else f"{Fore.RED}❌ NEEDS FIX{Style.RESET_ALL}"
        print(f"{agent}: {status}")
    
    print(f"\n{passed}/{total} agents are generating content")
    
    if passed == total:
        print(f"\n{Fore.GREEN}🎉 ALL AGENTS WORKING!{Style.RESET_ALL}")
        print("\nNext steps:")
        print("1. Run full quality tests")
        print("2. Test /analyze endpoint")
        print("3. Deploy to Slack")
    else:
        print(f"\n{Fore.YELLOW}⚠️ Some agents need fixes{Style.RESET_ALL}")
        print("\nThe _generate_response method needs to match StandardAgentNodeV4 signature:")
        print("def _generate_response(self, task: str, memories: List, llm) -> str")

if __name__ == "__main__":
    main()