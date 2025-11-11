# test_agents_fixed.py
"""
Test script to verify all agent fixes are working correctly.
Tests that agents use fallback methods instead of non-existent prompt methods.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any

def test_agent_initialization():
    """Test that all agents can be initialized without errors."""
    print("\n" + "="*60)
    print("TESTING AGENT INITIALIZATION")
    print("="*60)
    
    agents = []
    errors = []
    
    # Test 1: Psychological Agent
    try:
        from team_icp.agents.psychological import PsychologicalAgent
        psych_agent = PsychologicalAgent()
        agents.append(("Psychological", psych_agent))
        print("✅ PsychologicalAgent initialized successfully")
    except Exception as e:
        print(f"❌ PsychologicalAgent failed: {e}")
        errors.append(("Psychological", str(e)))
    
    # Test 2: Voice Agent
    try:
        from team_icp.agents.voice_of_customer import VoiceAgent
        voice_agent = VoiceAgent()
        agents.append(("Voice", voice_agent))
        print("✅ VoiceAgent initialized successfully")
    except Exception as e:
        print(f"❌ VoiceAgent failed: {e}")
        errors.append(("Voice", str(e)))
    
    # Test 3: Competitor Agent
    try:
        from team_icp.agents.competitor import CompetitorAgent
        comp_agent = CompetitorAgent()
        agents.append(("Competitor", comp_agent))
        print("✅ CompetitorAgent initialized successfully")
    except Exception as e:
        print(f"❌ CompetitorAgent failed: {e}")
        errors.append(("Competitor", str(e)))
    
    # Test 4: Sales Interview Agent
    try:
        from team_icp.agents.interview_sales import SalesInterviewAgent
        sales_agent = SalesInterviewAgent()
        agents.append(("Sales Interview", sales_agent))
        print("✅ SalesInterviewAgent initialized successfully")
    except Exception as e:
        print(f"❌ SalesInterviewAgent failed: {e}")
        errors.append(("Sales Interview", str(e)))
    
    # Test 5: Psychological Interview Agent
    try:
        from team_icp.agents.interview_psychological import PsychologicalInterviewAgent
        psych_int_agent = PsychologicalInterviewAgent()
        agents.append(("Psychological Interview", psych_int_agent))
        print("✅ PsychologicalInterviewAgent initialized successfully")
    except Exception as e:
        print(f"❌ PsychologicalInterviewAgent failed: {e}")
        errors.append(("Psychological Interview", str(e)))
    
    # Test 6: GTM Blueprint Agent
    try:
        from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
        gtm_agent = GTMBlueprintAgent()
        agents.append(("GTM Blueprint", gtm_agent))
        print("✅ GTMBlueprintAgent initialized successfully")
    except Exception as e:
        print(f"❌ GTMBlueprintAgent failed: {e}")
        errors.append(("GTM Blueprint", str(e)))
    
    print(f"\n📊 Results: {len(agents)}/6 agents initialized successfully")
    
    if errors:
        print("\n⚠️ Errors found:")
        for agent_name, error in errors:
            print(f"  - {agent_name}: {error}")
    
    return agents, errors


def test_agent_methods(agents):
    """Test that agents use correct fallback methods."""
    print("\n" + "="*60)
    print("TESTING AGENT METHODS (Fallback Behavior)")
    print("="*60)
    
    test_company = "TestCompany"
    test_context = {
        'industry': 'technology',
        'market': 'B2B',
        'insights': {}
    }
    
    method_tests = []
    
    for agent_name, agent in agents:
        print(f"\n📝 Testing {agent_name} Agent...")
        
        # Check for duplicate methods
        print(f"   Checking for duplicate methods...")
        
        # Check _create_template_fallback
        if hasattr(agent, '_create_template_fallback'):
            # Try to call it to see if it uses non-existent template_enforcer methods
            try:
                result = agent._create_template_fallback(test_company)
                if 'get_fallback_template' in str(result):
                    print(f"   ⚠️ {agent_name} might still call template_enforcer.get_fallback_template")
                else:
                    print(f"   ✅ _create_template_fallback returns direct template")
            except AttributeError as e:
                if 'get_fallback_template' in str(e):
                    print(f"   ❌ {agent_name} calls non-existent template_enforcer.get_fallback_template")
                    method_tests.append((agent_name, "template_fallback", False))
                else:
                    raise
            except Exception as e:
                print(f"   ⚠️ Unexpected error: {e}")
        
        # Check research methods
        if agent_name == "Psychological":
            if hasattr(agent, '_research_psychological_context'):
                try:
                    # This should work with direct queries
                    result = agent._research_psychological_context(test_company, test_context)
                    print(f"   ✅ _research_psychological_context works (direct queries)")
                    method_tests.append((agent_name, "research", True))
                except Exception as e:
                    print(f"   ❌ _research_psychological_context failed: {e}")
                    method_tests.append((agent_name, "research", False))
        
        elif agent_name == "Voice":
            if hasattr(agent, '_research_customer_voice'):
                try:
                    result = agent._research_customer_voice(test_company, test_context)
                    print(f"   ✅ _research_customer_voice works (direct queries)")
                    method_tests.append((agent_name, "research", True))
                except Exception as e:
                    print(f"   ❌ _research_customer_voice failed: {e}")
                    method_tests.append((agent_name, "research", False))
        
        elif agent_name == "Competitor":
            if hasattr(agent, '_research_competitors'):
                try:
                    result = agent._research_competitors(test_company, test_context)
                    print(f"   ✅ _research_competitors works (direct queries)")
                    method_tests.append((agent_name, "research", True))
                except Exception as e:
                    print(f"   ❌ _research_competitors failed: {e}")
                    method_tests.append((agent_name, "research", False))
        
        elif agent_name == "Sales Interview":
            if hasattr(agent, '_research_sales_context'):
                try:
                    result = agent._research_sales_context(test_company, test_context)
                    print(f"   ✅ _research_sales_context works (direct queries)")
                    method_tests.append((agent_name, "research", True))
                except Exception as e:
                    print(f"   ❌ _research_sales_context failed: {e}")
                    method_tests.append((agent_name, "research", False))
        
        elif agent_name == "Psychological Interview":
            if hasattr(agent, '_research_psychological_context'):
                try:
                    result = agent._research_psychological_context(test_company, test_context)
                    print(f"   ✅ _research_psychological_context works (direct queries)")
                    method_tests.append((agent_name, "research", True))
                except Exception as e:
                    print(f"   ❌ _research_psychological_context failed: {e}")
                    method_tests.append((agent_name, "research", False))
        
        elif agent_name == "GTM Blueprint":
            if hasattr(agent, '_research_gtm_strategies'):
                try:
                    result = agent._research_gtm_strategies(test_company, test_context)
                    print(f"   ✅ _research_gtm_strategies works (direct queries)")
                    method_tests.append((agent_name, "research", True))
                except Exception as e:
                    print(f"   ❌ _research_gtm_strategies failed: {e}")
                    method_tests.append((agent_name, "research", False))
    
    # Summary
    successful = sum(1 for _, _, success in method_tests if success)
    total = len(method_tests)
    
    print(f"\n📊 Method Tests: {successful}/{total} passed")
    
    return method_tests


def test_main_execution():
    """Test main execution methods with fallback."""
    print("\n" + "="*60)
    print("TESTING MAIN EXECUTION METHODS")
    print("="*60)
    
    test_state = {
        'company_name': 'TestCompany',
        'industry': 'technology',
        'market': 'B2B SaaS',
        'insights': {}
    }
    
    execution_tests = []
    
    # Test each agent's main method
    agents_to_test = [
        ("Psychological", "analyze_psychology"),
        ("Voice", "extract_customer_voice"),
        ("Competitor", "analyze_competition"),
        ("Sales Interview", "conduct_sales_interviews"),
        ("Psychological Interview", "conduct_interviews"),
        ("GTM Blueprint", "create_gtm_blueprint")
    ]
    
    for agent_name, method_name in agents_to_test:
        print(f"\n🔧 Testing {agent_name}.{method_name}()...")
        
        try:
            # Import and initialize
            if agent_name == "Psychological":
                from team_icp.agents.psychological import PsychologicalAgent
                agent = PsychologicalAgent()
            elif agent_name == "Voice":
                from team_icp.agents.voice_of_customer import VoiceAgent
                agent = VoiceAgent()
            elif agent_name == "Competitor":
                from team_icp.agents.competitor import CompetitorAgent
                agent = CompetitorAgent()
            elif agent_name == "Sales Interview":
                from team_icp.agents.interview_sales import SalesInterviewAgent
                agent = SalesInterviewAgent()
            elif agent_name == "Psychological Interview":
                from team_icp.agents.interview_psychological import PsychologicalInterviewAgent
                agent = PsychologicalInterviewAgent()
            elif agent_name == "GTM Blueprint":
                from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
                agent = GTMBlueprintAgent()
            
            # Get the method
            method = getattr(agent, method_name)
            
            # Call with test data
            result = method(test_state['company_name'], test_state)
            
            # Check result structure
            if isinstance(result, dict) and 'analysis' in result:
                print(f"   ✅ {agent_name}.{method_name}() executed successfully")
                print(f"      Word count: {result.get('word_count', 0)}")
                print(f"      Quality score: {result.get('quality_score', 0):.2f}")
                execution_tests.append((agent_name, True))
            else:
                print(f"   ⚠️ {agent_name}.{method_name}() returned unexpected format")
                execution_tests.append((agent_name, False))
                
        except AttributeError as e:
            if 'get_' in str(e) and 'prompts' in str(e):
                print(f"   ❌ {agent_name} still calls non-existent prompt method: {e}")
                execution_tests.append((agent_name, False))
            else:
                print(f"   ❌ {agent_name} AttributeError: {e}")
                execution_tests.append((agent_name, False))
        except Exception as e:
            print(f"   ❌ {agent_name} failed with: {type(e).__name__}: {e}")
            execution_tests.append((agent_name, False))
    
    # Summary
    successful = sum(1 for _, success in execution_tests if success)
    total = len(execution_tests)
    
    print(f"\n📊 Execution Tests: {successful}/{total} passed")
    
    return execution_tests


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("TESTING AGENT FIXES - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Test 1: Initialization
    agents, init_errors = test_agent_initialization()
    
    # Test 2: Methods
    if agents:
        method_results = test_agent_methods(agents)
    
    # Test 3: Main execution
    execution_results = test_main_execution()
    
    # Final Summary
    print("\n" + "="*70)
    print("FINAL TEST SUMMARY")
    print("="*70)
    
    if not init_errors and all(success for _, success in execution_results):
        print("✅ ALL TESTS PASSED! Agents are working correctly.")
    else:
        print("⚠️ Some issues remain. Please review the errors above.")
        
        if init_errors:
            print("\nInitialization errors to fix:")
            for agent, error in init_errors:
                print(f"  - {agent}: {error}")
        
        failed_executions = [agent for agent, success in execution_results if not success]
        if failed_executions:
            print("\nExecution failures to fix:")
            for agent in failed_executions:
                print(f"  - {agent}")


if __name__ == "__main__":
    main()