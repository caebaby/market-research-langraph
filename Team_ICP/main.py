# main.py
"""
Level 5 ICP Agent - Main Entry Point
Tests the psychological agent with persistent memory
"""

import asyncio
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import your Level 5 agent
from team_icp.agents.psychological import PsychologicalAgent

async def main():
    """Test the Level 5 ICP Psychological Agent with persistent memory"""
    
    print("🚀 Initializing Level 5 ICP Psychological Agent...")
    print("=" * 80)
    
    # Test business context
    test_context = """
    We're targeting financial advisors who are struggling to differentiate 
    themselves in a crowded market. They're typically 35-55 years old, 
    managing $50M-$200M in assets, and feeling pressure from robo-advisors 
    and younger competitors. They value relationships but struggle with 
    digital marketing and feel their expertise isn't valued anymore.
    
    They're saying things like 'I don't want to be just another advisor' 
    and 'My clients trust ME, not some algorithm.' But they're also 
    secretly worried they're becoming obsolete.
    """
    
    # Create a goal for the agent
    analysis_goal = {
        "description": "Extract deep psychological insights about target customer",
        "context": test_context,
        "type": "psychological_analysis",
        "success_criteria": {
            "frameworks": ["jungian", "lab_profile", "jtbd", "cognitive_bias"],
            "depth": "visceral",
            "accuracy": 0.90
        }
    }
    
    print("📋 Goal: Deep psychological analysis of financial advisors")
    print("🧠 Memory System: Active")
    print("=" * 80)
    
    print("\n⏳ Running Level 5 analysis with memory enhancement...")
    state = {"goal": analysis_goal, "new_data": True}
    result = await graph.ainvoke(state)  # Use new graph workflow
    
    # Display results
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    
    if result["result"]["results"]:
        analysis = result["result"]["results"][0].get("analysis", "No analysis found")
        print("\n📊 PSYCHOLOGICAL ANALYSIS:")
        print("-" * 80)
        print(analysis)
        print("-" * 80)
    
    print("\n📈 LEVEL 5 METRICS:")
    print(f"• Success Score: {result['result']['success_score']:.2%}")
    print(f"• Execution Time: {result['result']['execution_time']:.1f} seconds")
    print(f"• Tasks Completed: {result['result']['metrics']['tasks_completed']}")
    
    print("\n💾 MEMORY SYSTEM CHECK:")
    memory_files = ["memory/patterns.json", "memory/experiences.json"]
    for file in memory_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                data = json.load(f)
                if file.endswith("patterns.json"):
                    industries = len(data.get("industries", {}))
                    print(f"• Industry patterns stored: {industries}")
                elif file.endswith("experiences.json"):
                    experiences = len(data)
                    print(f"• Experiences stored: {experiences}")
    
    print("\n🔄 Testing memory recall with new context...")
    new_context = """
    Financial advisors in wealth management struggling with fee compression
    and client acquisition. They're losing younger clients to robo-advisors
    but don't want to compete on price. They value personal relationships
    but feel technology is making them irrelevant.
    """
    new_goal = {
        "description": "Analyze wealth management advisor psychology",
        "context": new_context,
        "type": "psychological_analysis"
    }
    state2 = {"goal": new_goal, "new_data": True}
    result2 = await graph.ainvoke(state2)
    
    print("\n✅ Second analysis complete - Memory system should have recalled patterns!")
    print(f"• This analysis success score: {result2['result']['success_score']:.2%}")
    print(f"• Total experiences in memory: {result2['result']['metrics']['tasks_completed']}")
    
    return result

if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: Please set ANTHROPIC_API_KEY in your .env file")
        exit(1)
    
    # Run the test
    asyncio.run(main())
