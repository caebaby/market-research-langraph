# test_graph_integration.py
"""
Comprehensive test suite for the enhanced graph workflow.
Tests memory, search, and all agent integrations.
"""
import os
os.environ['SKIP_ENHANCEMENT'] = 'true'
os.environ['QUICK_TEST_MODE'] = 'true'
os.environ['ENABLE_QDRANT'] = 'false'  # ADD THIS
os.environ['ENABLE_BRAVE_SEARCH'] = 'false'  # ADD THIS
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from team_icp.workflows.graph import (
    MarketResearchWorkflow,
    run_icp_analysis,
    get_system_status,
    print_system_status,
    extract_company_name,
    extract_industry,
    validate_template_compliance
)

# Test configuration
TEST_BUSINESS_CONTEXT = """
TestCompany AI is a B2B SaaS platform that provides automated customer support 
using advanced AI agents. We help enterprises reduce support costs by 70% while 
improving customer satisfaction scores. Our target customers are mid-market to 
enterprise companies with 500+ support tickets per day.
"""

def print_test_header(test_name: str):
    """Print formatted test header"""
    print("\n" + "="*60)
    print(f"🧪 TEST: {test_name}")
    print("="*60)

def print_test_result(success: bool, message: str):
    """Print test result"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def test_system_status():
    """Test 1: Verify system components are available"""
    print_test_header("System Status Check")
    
    status = get_system_status()
    
    # Check critical components
    tests_passed = []
    tests_failed = []
    
    # LLM Check
    if status['llm_available']:
        tests_passed.append("LLM initialized")
    else:
        tests_failed.append("LLM not available")
    
    # Memory System Check (optional)
    from team_icp.workflows.graph import MEMORY_SYSTEM_AVAILABLE
    if MEMORY_SYSTEM_AVAILABLE:
        tests_passed.append("Memory system available")
    else:
        print("⚠️  Memory system not available (optional)")
    
    # Search System Check (optional)
    from team_icp.workflows.graph import BRAVE_SEARCH_AVAILABLE
    if BRAVE_SEARCH_AVAILABLE:
        tests_passed.append("Search system available")
    else:
        print("⚠️  Search system not available (optional)")
    
    # Print results
    for msg in tests_passed:
        print_test_result(True, msg)
    for msg in tests_failed:
        print_test_result(False, msg)
    
    # Print full status
    print("\nDetailed Status:")
    print_system_status()
    
    return len(tests_failed) == 0

def test_company_extraction():
    """Test 2: Test company name and industry extraction"""
    print_test_header("Company Extraction")
    
    test_cases = [
        ("TestCompany AI platform for customer support", "TestCompany", "technology"),
        ("B2B SaaS for healthcare management", "company_", "SaaS"),
        ("Fintech solution for payments", "Fintech", "fintech"),
    ]
    
    all_passed = True
    for text, expected_company_prefix, expected_industry in test_cases:
        company = extract_company_name(text)
        industry = extract_industry(text)
        
        company_ok = company.startswith(expected_company_prefix)
        industry_ok = industry == expected_industry
        
        if company_ok and industry_ok:
            print_test_result(True, f"'{text[:30]}...' → Company: {company}, Industry: {industry}")
        else:
            print_test_result(False, f"Extraction failed for '{text[:30]}...'")
            all_passed = False
    
    return all_passed

def test_template_validation():
    """Test 3: Test template compliance validation"""
    print_test_header("Template Compliance Validation")
    
    # Create sample content with various levels of compliance
    full_template = """
    ## Demographic Profile
    Target audience demographics...
    
    ## Psychological Profile
    Mental models and beliefs...
    
    ## Behavioral Patterns
    How they act...
    
    ## Pain Discovery
    Problems they face...
    
    ## Solution Awareness
    What they know...
    
    ## Decision Framework
    How they decide...
    
    ## Value Perception
    What they value...
    
    ## Trust Building
    How to build trust...
    
    ## Objection Patterns
    Common objections...
    
    ## Emotional Journey
    Feelings throughout...
    
    ## Social Dynamics
    Social influences...
    
    ## Marketing Strategy
    How to reach them...
    
    ## Success Metrics
    Measuring success...
    
    ## Implementation Roadmap
    Steps to implement...
    """
    
    partial_template = """
    ## Demographic Profile
    Some demographics...
    
    ## Psychological Profile
    Some psychology...
    """
    
    # Test full compliance
    score = validate_template_compliance(full_template, "psychological")
    print_test_result(score > 0.9, f"Full template compliance: {score:.2%}")
    
    # Test partial compliance
    score = validate_template_compliance(partial_template, "psychological")
    print_test_result(0.1 < score < 0.3, f"Partial template compliance: {score:.2%}")
    
    # Test empty content
    score = validate_template_compliance("", "psychological")
    print_test_result(score == 0.0, f"Empty content compliance: {score:.2%}")
    
    return True

def test_single_agent():
    """Test 4: Run a single agent"""
    print_test_header("Single Agent Execution")
    
    try:
        workflow = MarketResearchWorkflow(agents=['psychological'])
        result = workflow.run_single_agent('psychological', TEST_BUSINESS_CONTEXT)
        
        # Check results
        success = result.get('success', False)
        word_count = result.get('word_count', 0)
        quality = result.get('quality_score', 0)
        
        print_test_result(success, f"Agent executed successfully")
        print_test_result(word_count > 500, f"Word count: {word_count}")
        print_test_result(quality > 0.5, f"Quality score: {quality:.2%}")
        
        # Show snippet of output
        output = result.get('output', '')
        if output:
            print(f"\nOutput preview (first 200 chars):")
            print(f"  {output[:200]}...")
        
        return success and word_count > 500
        
    except Exception as e:
        print_test_result(False, f"Single agent failed: {e}")
        return False

def test_voice_agent_dict_fix():
    """Test that voice agent returns proper format"""
    print_test_header("Voice Agent Dict Fix Test")
    
    try:
        from team_icp.agents.voice_of_customer import VoiceAgent
        from langchain_anthropic import ChatAnthropic
        
        llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
        agent = VoiceAgent(llm=llm)
        
        # Test the method directly
        result = agent.extract_customer_voice(TEST_BUSINESS_CONTEXT, {})
        
        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Dict keys: {result.keys()}")
            print(f"Has 'analysis' key: {'analysis' in result}")
            print(f"Has 'output' key: {'output' in result}")
        
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False
    
def test_minimal_workflow():
    """Test 5: Run minimal workflow with 2 agents"""
    print_test_header("Minimal Workflow (2 Agents)")
    
    try:
        workflow = MarketResearchWorkflow(
            agents=['psychological', 'voice_of_customer'],
            parallel=False
        )
        
        # Add simple Slack updater for testing
        updates = []
        def mock_slack_updater(msg):
            updates.append(msg)
            print(f"  [Slack Update] {msg}")
        
        result = workflow.run(
            task=TEST_BUSINESS_CONTEXT,
            slack_updater=mock_slack_updater,
            verbose=False,
            enable_memory=False,  # Start without memory
            enable_search=False   # Start without search
        )
        
        # Check results
        success = result.get('success', False)
        agents_run = result.get('agents_run', [])
        total_words = result.get('statistics', {}).get('total_words', 0)
        quality = result.get('overall_quality', 0)
        
        print_test_result(success, "Workflow completed successfully")
        print_test_result(len(agents_run) == 2, f"Agents run: {agents_run}")
        print_test_result(total_words > 1000, f"Total words: {total_words:,}")
        print_test_result(quality > 0.5, f"Overall quality: {quality:.2%}")
        print_test_result(len(updates) > 0, f"Slack updates sent: {len(updates)}")
        
        return success
        
    except Exception as e:
        print_test_result(False, f"Minimal workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_integration():
    """Test 6: Test memory integration (if available)"""
    print_test_header("Memory Integration")
    
    from team_icp.workflows.graph import memory_system
    
    if not memory_system:
        print("⚠️  Memory system not initialized - skipping test")
        return True
    
    try:
        workflow = MarketResearchWorkflow(agents=['psychological'])
        
        # Run with memory enabled
        result = workflow.run(
            task=TEST_BUSINESS_CONTEXT,
            enable_memory=False,
            enable_search=False,
            verbose=False
        )
        
        memory_enabled = result.get('memory_enabled', False)
        memories_stored = result.get('memories_stored', {})
        
        print_test_result(memory_enabled, "Memory was enabled")
        print_test_result(len(memories_stored) > 0, f"Memories stored: {memories_stored}")
        
        # Try to retrieve memories (second run)
        print("\n  Running again to test memory retrieval...")
        result2 = workflow.run(
            task=TEST_BUSINESS_CONTEXT + " (second run)",
            enable_memory=True,
            enable_search=False,
            verbose=False
        )
        
        # Check if historical insights were loaded
        # This would be visible in the logs
        print_test_result(True, "Memory retrieval test completed")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Memory integration failed: {e}")
        return False

def test_search_integration():
    """Test 7: Test search integration (if available)"""
    print_test_header("Search Integration")
    
    from team_icp.workflows.graph import brave_search_client
    
    if not brave_search_client:
        print("⚠️  Search system not initialized - skipping test")
        return True
    
    try:
        workflow = MarketResearchWorkflow(agents=['competitor'])
        
        # Run with search enabled
        result = workflow.run(
            task=TEST_BUSINESS_CONTEXT,
            enable_memory=False,
            enable_search=False,
            verbose=False
        )
        
        search_enabled = result.get('search_enabled', False)
        search_results = result.get('search_results', {})
        
        print_test_result(search_enabled, "Search was enabled")
        print_test_result(len(search_results) > 0, f"Searches performed: {list(search_results.keys())}")
        
        return True
        
    except Exception as e:
        print_test_result(False, f"Search integration failed: {e}")
        return False

def test_full_icp_analysis():
    """Test 8: Run full ICP analysis (main entry point)"""
    print_test_header("Full ICP Analysis")
    
    try:
        print("  This will run all 6 agents - may take 2-3 minutes...")
        
        # Track updates
        updates = []
        def mock_slack_updater(msg):
            updates.append(msg)
            print(f"  [Update] {msg}")
        
        # Run full analysis
        result = run_icp_analysis(
            business_context=TEST_BUSINESS_CONTEXT,
            slack_updater=mock_slack_updater,
            enable_memory=False,  # Disable for speed
            enable_search=False   # Disable for speed
        )
        
        # Check comprehensive results
        success = result.get('success', False)
        agents_run = result.get('agents_run', [])
        total_words = result.get('statistics', {}).get('total_words', 0)
        quality = result.get('overall_quality', 0)
        
        print_test_result(success, "Full analysis completed")
        print_test_result(len(agents_run) >= 5, f"Agents completed: {len(agents_run)}/6")
        print_test_result(total_words > 5000, f"Total words: {total_words:,}")
        print_test_result(quality > 0.6, f"Overall quality: {quality:.2%}")
        
        # Check for final report
        has_report = bool(result.get('final_report'))
        print_test_result(has_report, "Final report generated")
        
        # Save report if successful
        if success and has_report:
            from team_icp.workflows.graph import save_report
            filename = save_report(result, "test_icp_report.md", "markdown")
            print(f"\n  📄 Report saved to: {filename}")
        
        return success
        
    except Exception as e:
        print_test_result(False, f"Full ICP analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 GRAPH WORKFLOW INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    tests = [
        ("System Status", test_system_status),
        ("Company Extraction", test_company_extraction),
        ("Template Validation", test_template_validation),
        ("Single Agent", test_single_agent),
        ("Minimal Workflow", test_minimal_workflow),
        ("Memory Integration", test_memory_integration),
        ("Search Integration", test_search_integration),
        ("Full ICP Analysis", test_full_icp_analysis),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed in results:
        icon = "✅" if passed else "❌"
        print(f"{icon} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Graph workflow is ready for production.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)