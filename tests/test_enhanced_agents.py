# test_enhanced_agents.py
"""
Comprehensive test suite for enhanced Level 4 agents
Tests word count, quality scores, and synthesis capabilities
"""

import sys
import os
import asyncio
from datetime import datetime
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents
from team_icp.agents.psychological import PsychologicalAgent
from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
from team_icp.agents.voice import VoiceAgent
from team_icp.agents.competitor import CompetitorAgent

# Import core components
from core.config import Config
from core.memory import HybridMemory

# Import workflow if available
try:
    from team_icp.workflows.graph import graph, ICPGraph
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False
    print("⚠️ Workflow graph not available, testing agents individually")


def print_separator(title):
    """Print a formatted separator"""
    print("\n" + "="*80)
    print(f"🚀 {title}")
    print("="*80)


def test_psychological_agent():
    """Test the enhanced psychological agent for 2000+ words"""
    print_separator("TESTING PSYCHOLOGICAL AGENT")
    
    # Create rich test context
    test_context = """
    We're targeting executive coaches who charge $5000-10000 per month but are struggling 
    to scale beyond 10-15 clients. They're typically 40-55 years old, have 10+ years 
    of corporate experience, and transitioned to coaching after burnout. They're exhausted 
    from 1-on-1 sessions, feeling like frauds despite their success, desperately want to 
    help more people but feel trapped trading time for money. They wake up at 3am worried 
    about client retention, their own relevance, and whether they're making real impact.
    
    They say things like "I'm successful but dying inside" and "I became a coach to have 
    freedom, but I have less freedom than in corporate." They're terrified of group 
    programs because they think their value is in personal attention. They compare 
    themselves to Tony Robbins but feel like they're playing small. They want to create 
    courses but worry about technology and whether anyone would buy.
    """
    
    # Create state for agent
    state = {
        "business_context": test_context,
        "master_context": test_context,
        "current_task": {
            "description": "Analyze the deep psychological patterns of executive coaches struggling to scale",
            "is_high_stakes": False
        },
        "shared_insights": {},
        "memory_service": None,  # Can add HybridMemory() if configured
        "tool_executor": None,
        "client_id": f"test_psych_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    try:
        # Initialize agent
        agent = PsychologicalAgent()
        print(f"✅ Agent initialized: {agent.agent_name}")
        print(f"   Target quality: {agent.target_quality}")
        print(f"   Min word count: {agent.min_word_count}")
        
        # Execute analysis
        print("\n⏳ Generating psychological analysis...")
        start_time = time.time()
        
        result = agent(state)
        
        execution_time = time.time() - start_time
        
        # Extract results
        output = result.get('current_output', 'No output generated')
        quality_score = result.get('quality_score', 0.0)
        word_count = len(output.split())
        critique = result.get('reflection', {}).get('critique', 'No critique')
        
        # Display results
        print(f"\n📊 RESULTS:")
        print(f"   ✓ Word count: {word_count} words (target: 2000+) {'✅' if word_count >= 2000 else '❌'}")
        print(f"   ✓ Quality score: {quality_score:.2f} (target: 0.85+) {'✅' if quality_score >= 0.85 else '⚠️'}")
        print(f"   ✓ Execution time: {execution_time:.1f} seconds")
        print(f"   ✓ Needs human review: {result.get('requires_human_review', False)}")
        
        # Check frameworks
        frameworks_found = agent._identify_frameworks(output)
        print(f"\n📚 Frameworks applied ({len(frameworks_found)}/10):")
        for framework in frameworks_found:
            print(f"   • {framework}")
        
        # Show sample output
        print(f"\n📝 First 500 characters of output:")
        print("-"*40)
        print(output[:500] + "...")
        print("-"*40)
        
        # Show quality critique
        if critique and len(critique) > 50:
            print(f"\n🔍 Quality critique preview:")
            print(critique[:300] + "...")
        
        # Store in shared insights for next test
        state['shared_insights']['psychological'] = {
            'summary': output[:500],
            'quality_score': quality_score,
            'patterns': frameworks_found[:5],
            'word_count': word_count
        }
        
        return state, quality_score >= 0.85 and word_count >= 2000
        
    except Exception as e:
        print(f"\n❌ Error testing psychological agent: {e}")
        import traceback
        traceback.print_exc()
        return state, False


def test_gtm_blueprint_agent(state=None):
    """Test the enhanced GTM Blueprint agent for 2500+ words"""
    print_separator("TESTING GTM BLUEPRINT AGENT")
    
    # Use state from psychological test or create new
    if not state:
        state = {
            "business_context": "Executive coaching business struggling to scale",
            "master_context": "Executive coaching business struggling to scale",
            "current_task": {
                "description": "Create comprehensive GTM strategy",
                "is_high_stakes": False
            },
            "shared_insights": {
                "psychological": {
                    "summary": "Deep identity crisis between helper and entrepreneur",
                    "quality_score": 0.82
                },
                "voice": {
                    "summary": "They say 'I'm drowning in clients but not making real money'",
                    "quality_score": 0.80
                }
            },
            "memory_service": None,
            "tool_executor": None,
            "client_id": f"test_gtm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
    
    try:
        # Initialize agent
        agent = GTMBlueprintAgent()
        print(f"✅ Agent initialized: {agent.agent_name}")
        print(f"   Target quality: {agent.target_quality}")
        print(f"   Min word count: {agent.min_word_count}")
        
        # Show what insights are available
        print(f"\n📥 Available insights from {len(state.get('shared_insights', {}))} agents:")
        for agent_name in state.get('shared_insights', {}).keys():
            print(f"   • {agent_name}")
        
        # Execute synthesis
        print("\n⏳ Generating GTM blueprint...")
        start_time = time.time()
        
        result = agent(state)
        
        execution_time = time.time() - start_time
        
        # Extract results
        output = result.get('current_output', 'No output generated')
        quality_score = result.get('quality_score', 0.0)
        word_count = len(output.split())
        
        # Display results
        print(f"\n📊 RESULTS:")
        print(f"   ✓ Word count: {word_count} words (target: 2500+) {'✅' if word_count >= 2500 else '❌'}")
        print(f"   ✓ Quality score: {quality_score:.2f} (target: 0.85+) {'✅' if quality_score >= 0.85 else '⚠️'}")
        print(f"   ✓ Execution time: {execution_time:.1f} seconds")
        
        # Check synthesis quality
        agents_referenced = agent._count_agent_references(output)
        print(f"\n🔗 Agent synthesis ({agents_referenced}/5 agents referenced)")
        
        # Check for action items
        action_items = agent._extract_action_items(output)
        print(f"\n📋 Action items found: {len(action_items)} (target: 15+) {'✅' if len(action_items) >= 15 else '⚠️'}")
        if action_items:
            print("   First 3 action items:")
            for item in action_items[:3]:
                print(f"   • {item[:100]}...")
        
        # Show sample output
        print(f"\n📝 First 500 characters of output:")
        print("-"*40)
        print(output[:500] + "...")
        print("-"*40)
        
        return quality_score >= 0.85 and word_count >= 2500
        
    except Exception as e:
        print(f"\n❌ Error testing GTM agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_workflow():
    """Test the complete workflow with all agents"""
    print_separator("TESTING FULL WORKFLOW")
    
    if not GRAPH_AVAILABLE:
        print("❌ Workflow graph not available. Install LangGraph to test full workflow.")
        return False
    
    try:
        # Initialize workflow
        icp_graph = ICPGraph()
        print("✅ Workflow graph initialized")
        
        # Test context
        test_input = {
            "company": "Executive coaching firm struggling to scale beyond 1-on-1 sessions",
            "business_context": """
            Executive coaches charging premium prices but capped at 10-15 clients.
            They want to scale but fear losing personal touch. Technology intimidates them.
            They're exhausted, questioning their impact, comparing themselves to bigger names.
            Need a way to leverage their expertise without burning out.
            """
        }
        
        print("\n⏳ Running full workflow analysis...")
        print("   This will take 2-3 minutes as all agents process sequentially...")
        
        start_time = time.time()
        result = icp_graph.run(test_input)
        execution_time = time.time() - start_time
        
        # Check results
        if "final_report" in result:
            report_length = len(result["final_report"].split())
            print(f"\n✅ Workflow completed in {execution_time:.1f} seconds")
            print(f"   • Final report: {report_length} words")
            print(f"   • Overall quality: {result.get('overall_quality', 0.0):.2f}")
            
            # Show report preview
            print(f"\n📝 Report preview:")
            print("-"*40)
            print(result["final_report"][:1000] + "...")
            print("-"*40)
            
            return True
        else:
            print(f"❌ No final report generated")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing workflow: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_integration():
    """Test memory storage and recall"""
    print_separator("TESTING MEMORY INTEGRATION")
    
    try:
        # Check if memory is configured
        memory = HybridMemory()
        print("✅ Memory service initialized")
        
        # Store a test memory
        test_memory = [{
            "content": "Executive coaches primary fear: becoming irrelevant",
            "metadata": {
                "agent": "psychological",
                "quality": 0.85,
                "timestamp": datetime.now().isoformat()
            }
        }]
        
        memory.store(test_memory)
        print("✅ Test memory stored")
        
        # Recall memories
        recalled = memory.recall("executive coaches", limit=5)
        print(f"✅ Recalled {len(recalled)} memories")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Memory not configured: {e}")
        return False


async def test_async_execution():
    """Test async execution capabilities"""
    print_separator("TESTING ASYNC EXECUTION")
    
    try:
        from app import analyze
        print("✅ API endpoint available for testing")
        
        # Note: This would need the FastAPI app running
        print("   Run 'python app.py' and test via dashboard or API")
        return True
        
    except ImportError:
        print("⚠️ FastAPI app not available for async testing")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 LEVEL 4 ENHANCED AGENTS - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Test 1: Psychological Agent
    state, psych_passed = test_psychological_agent()
    results['Psychological'] = '✅' if psych_passed else '❌'
    
    # Test 2: GTM Blueprint Agent (with psychological insights)
    gtm_passed = test_gtm_blueprint_agent(state)
    results['GTM Blueprint'] = '✅' if gtm_passed else '❌'
    
    # Test 3: Full Workflow
    if GRAPH_AVAILABLE:
        workflow_passed = test_full_workflow()
        results['Full Workflow'] = '✅' if workflow_passed else '❌'
    else:
        results['Full Workflow'] = '⏭️ Skipped (LangGraph not installed)'
    
    # Test 4: Memory Integration
    memory_passed = test_memory_integration()
    results['Memory'] = '✅' if memory_passed else '⚠️'
    
    # Final Report
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    
    for test_name, status in results.items():
        print(f"{status} {test_name}")
    
    # Overall status
    all_passed = all(status == '✅' for status in results.values() if status != '⏭️ Skipped')
    
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Agents are production-ready.")
    else:
        print("⚠️ Some tests need attention. Check the details above.")
    print("="*80)


if __name__ == "__main__":
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: Please set ANTHROPIC_API_KEY in your .env file")
        exit(1)
    
    # Run tests
    main()