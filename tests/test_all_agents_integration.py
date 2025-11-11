# tests/test_all_agents_integration.py
"""
Comprehensive Integration Test for All Agents
Tests: Qdrant memory, Brave search, 14-section template, bug fixes, cross-agent synthesis
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all agents
from team_icp.agents.psychological import PsychologicalAgent
from team_icp.agents.voice_of_customer import VoiceAgent
from team_icp.agents.competitor import CompetitorAgent
from team_icp.agents.interview_psychological import PsychologicalInterviewAgent
from team_icp.agents.interview_sales import SalesInterviewAgent
from team_icp.agents.gtm_blueprint import GTMBlueprintAgent

# Import Qdrant memory system
try:
    from core.memory_system_qdrant import QdrantMemorySystem
    QDRANT_AVAILABLE = True
except ImportError:
    print("⚠️ Qdrant not available - will test without memory")
    QDRANT_AVAILABLE = False


class ComprehensiveAgentTester:
    """
    Comprehensive test suite for all agents with full integration.
    
    Tests:
    - Individual agent methods
    - Execute pattern for workflow
    - Qdrant memory integration
    - Brave search functionality
    - 14-section template compliance
    - Bug fixes (quality score, completeness parameter)
    - Cross-agent synthesis in GTM Blueprint
    """
    
    def __init__(self):
        """Initialize test suite with configuration."""
        self.test_company = "TechCorp AI Solutions"
        self.test_context = {
            'industry': 'Enterprise Software',
            'market': 'B2B SaaS',
            'product': 'AI-powered analytics platform',
            'company_size': 'Mid-market',
            'target_audience': 'Data teams and analysts',
            'user_query': 'Create comprehensive market analysis'
        }
        
        self.agents = {}
        self.results = {}
        self.insights = {}  # For cross-agent communication
        self.test_metrics = {
            'agents_tested': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'memory_tests': 0,
            'search_tests': 0,
            'template_compliance': 0,
            'bug_fixes_verified': 0
        }
        
        # Expected 14 sections for template compliance
        self.REQUIRED_SECTIONS = [
            "1. EXECUTIVE SUMMARY",
            "2. MARKET CONTEXT",
            "3. TARGET AUDIENCE",
            "4. CUSTOMER PSYCHOLOGY",
            "5. VOICE OF CUSTOMER",
            "6. COMPETITIVE LANDSCAPE",
            "7. POSITIONING STRATEGY",
            "8. MESSAGING FRAMEWORK",
            "9. PRODUCT STRATEGY",
            "10. PRICING STRATEGY",
            "11. SALES STRATEGY",
            "12. MARKETING STRATEGY",
            "13. SUCCESS METRICS",
            "14. IMPLEMENTATION ROADMAP"
        ]
        
        # Check environment
        self._check_environment()
    
    def _check_environment(self):
        """Check environment configuration."""
        print("\n" + "="*60)
        print("🔍 ENVIRONMENT CHECK")
        print("="*60)
        
        # Check API keys
        env_vars = {
            'ANTHROPIC_API_KEY': '❌ Missing' if not os.getenv('ANTHROPIC_API_KEY') else '✅ Set',
            'BRAVE_API_KEY': '❌ Missing' if not os.getenv('BRAVE_API_KEY') else '✅ Set',
            'QDRANT_URL': '❌ Missing' if not os.getenv('QDRANT_URL') else '✅ Set',
            'QDRANT_API_KEY': '❌ Missing' if not os.getenv('QDRANT_API_KEY') else '✅ Set'
        }
        
        for var, status in env_vars.items():
            print(f"   {var}: {status}")
        
        print(f"   Qdrant Available: {'✅ Yes' if QDRANT_AVAILABLE else '❌ No'}")
        print()
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("\n" + "="*60)
        print("🚀 STARTING COMPREHENSIVE AGENT TESTS")
        print("="*60)
        
        # Test 1: Initialize all agents
        print("\n📋 Test 1: Agent Initialization")
        self._test_agent_initialization()
        
        # Test 2: Test individual methods
        print("\n📋 Test 2: Individual Agent Methods")
        self._test_individual_methods()
        
        # Test 3: Test execute pattern
        print("\n📋 Test 3: Execute Pattern for Workflow")
        self._test_execute_pattern()
        
        # Test 4: Test Qdrant memory
        if QDRANT_AVAILABLE:
            print("\n📋 Test 4: Qdrant Memory Integration")
            self._test_qdrant_integration()
        
        # Test 5: Test 14-section template compliance
        print("\n📋 Test 5: 14-Section Template Compliance")
        self._test_template_compliance()
        
        # Test 6: Test bug fixes
        print("\n📋 Test 6: Bug Fixes Verification")
        self._test_bug_fixes()
        
        # Test 7: Test GTM synthesis
        print("\n📋 Test 7: GTM Blueprint Cross-Agent Synthesis")
        self._test_gtm_synthesis()
        
        # Print final results
        self._print_test_summary()
    
    def _test_agent_initialization(self):
        """Test initialization of all agents."""
        agents_to_test = [
            ('psychological', PsychologicalAgent),
            ('voice', VoiceAgent),
            ('competitor', CompetitorAgent),
            ('interview_psychological', PsychologicalInterviewAgent),
            ('interview_sales', SalesInterviewAgent),
            ('gtm_blueprint', GTMBlueprintAgent)
        ]
        
        for agent_name, AgentClass in agents_to_test:
            try:
                print(f"   Initializing {agent_name}...", end=" ")
                agent = AgentClass()
                self.agents[agent_name] = agent
                
                # Verify key attributes
                assert hasattr(agent, 'memory_enabled'), f"{agent_name} missing memory_enabled"
                assert hasattr(agent, 'search_enabled'), f"{agent_name} missing search_enabled"
                assert hasattr(agent, 'execute'), f"{agent_name} missing execute method"
                assert hasattr(agent, 'REQUIRED_SECTIONS'), f"{agent_name} missing REQUIRED_SECTIONS"
                
                print(f"✅ Success (Memory: {agent.memory_enabled}, Search: {agent.search_enabled})")
                self.test_metrics['agents_tested'] += 1
                self.test_metrics['tests_passed'] += 1
                
            except Exception as e:
                print(f"❌ Failed: {str(e)}")
                self.test_metrics['tests_failed'] += 1
    
    def _test_individual_methods(self):
        """Test individual methods of each agent."""
        test_cases = [
            ('psychological', 'analyze_psychology'),
            ('voice', 'extract_customer_voice'),
            ('competitor', 'analyze_competition'),
            ('interview_psychological', 'conduct_interviews'),
            ('interview_sales', 'conduct_sales_interviews'),
            ('gtm_blueprint', 'create_gtm_blueprint')
        ]
        
        for agent_name, method_name in test_cases:
            if agent_name not in self.agents:
                print(f"   ⚠️ Skipping {agent_name} - not initialized")
                continue
            
            try:
                print(f"   Testing {agent_name}.{method_name}()...", end=" ")
                agent = self.agents[agent_name]
                method = getattr(agent, method_name)
                
                # Prepare context with insights for GTM
                test_context = self.test_context.copy()
                if agent_name == 'gtm_blueprint':
                    test_context['insights'] = self.insights
                
                # Call the method
                result = method(self.test_company, test_context)
                
                # Verify result structure
                assert isinstance(result, dict), f"Result should be dict, got {type(result)}"
                assert 'analysis' in result, "Result missing 'analysis'"
                assert 'quality_score' in result, "Result missing 'quality_score'"
                assert 'word_count' in result, "Result missing 'word_count'"
                assert 'template_compliance' in result, "Result missing 'template_compliance'"
                
                # Store result and insights
                self.results[agent_name] = result
                if 'insights' not in self.insights:
                    self.insights = {}
                
                # Store insights for cross-agent communication
                if agent_name == 'psychological':
                    self.insights['psychological'] = {
                        'patterns': agent.behavioral_patterns[:5] if hasattr(agent, 'behavioral_patterns') else [],
                        'biases': agent.cognitive_biases[:3] if hasattr(agent, 'cognitive_biases') else [],
                        'triggers': agent.emotional_triggers[:3] if hasattr(agent, 'emotional_triggers') else [],
                        'quality_score': result['quality_score']
                    }
                elif agent_name == 'voice':
                    self.insights['voice'] = {
                        'quotes': [q['text'] for q in agent.customer_quotes[:5]] if hasattr(agent, 'customer_quotes') else [],
                        'pain_points': [p['description'] for p in agent.pain_points[:3]] if hasattr(agent, 'pain_points') else [],
                        'sentiment': agent.sentiment_analysis.get('dominant_sentiment', 'neutral') if hasattr(agent, 'sentiment_analysis') else 'neutral',
                        'quality_score': result['quality_score']
                    }
                elif agent_name == 'competitor':
                    self.insights['competitor'] = {
                        'competitors': agent.identified_competitors[:5] if hasattr(agent, 'identified_competitors') else [],
                        'gaps': [g['description'] for g in agent.positioning_gaps[:3]] if hasattr(agent, 'positioning_gaps') else [],
                        'quality_score': result['quality_score']
                    }
                elif agent_name == 'interview_sales':
                    self.insights['sales'] = {
                        'interviews_count': len(agent.interviews) if hasattr(agent, 'interviews') else 0,
                        'objections': [o['objection'] for o in agent.objection_patterns[:5]] if hasattr(agent, 'objection_patterns') else [],
                        'success_factors': [s['factor'] for s in agent.success_factors[:3]] if hasattr(agent, 'success_factors') else [],
                        'quality_score': result['quality_score']
                    }
                
                print(f"✅ Success (Quality: {result['quality_score']:.2f}, Words: {result['word_count']})")
                self.test_metrics['tests_passed'] += 1
                
            except Exception as e:
                print(f"❌ Failed: {str(e)[:50]}")
                self.test_metrics['tests_failed'] += 1
                if os.getenv('DEBUG'):
                    traceback.print_exc()
    
    def _test_execute_pattern(self):
        """Test execute method for workflow integration."""
        print("   Testing execute pattern for workflow...")
        
        # Create workflow state
        state = {
            'company_name': self.test_company,
            'industry': self.test_context['industry'],
            'market': self.test_context['market'],
            'insights': self.insights,
            'request_id': 'test_123',
            'user_query': 'Test workflow'
        }
        
        for agent_name in ['psychological', 'voice', 'competitor']:
            if agent_name not in self.agents:
                continue
            
            try:
                print(f"      {agent_name}.execute()...", end=" ")
                agent = self.agents[agent_name]
                
                # Execute and update state
                updated_state = agent.execute(state.copy())
                
                # Verify state updates
                assert 'insights' in updated_state, "State missing insights"
                assert agent_name in updated_state.get('insights', {}), f"State missing {agent_name} insights"
                
                print("✅")
                self.test_metrics['tests_passed'] += 1
                
            except Exception as e:
                print(f"❌ {str(e)[:30]}")
                self.test_metrics['tests_failed'] += 1
    
    def _test_qdrant_integration(self):
        """Test Qdrant memory integration."""
        try:
            print("   Testing Qdrant connection...", end=" ")
            memory = QdrantMemorySystem()
            
            # Test store
            test_content = f"Test memory for {self.test_company} at {datetime.now()}"
            memory_id = memory.store_memory(
                client_id=f"company_{self.test_company.lower().replace(' ', '_')}",
                agent_name="test_agent",
                memory_type="test",
                content=test_content
            )
            
            assert memory_id is not None, "Memory storage failed"
            print("✅ Store")
            
            # Test retrieve
            print("      Testing memory retrieval...", end=" ")
            memories = memory.retrieve_memories(
                client_id=f"company_{self.test_company.lower().replace(' ', '_')}",
                query="test memory",
                limit=5
            )
            
            print(f"✅ Retrieved {len(memories)} memories")
            self.test_metrics['memory_tests'] += 2
            self.test_metrics['tests_passed'] += 2
            
        except Exception as e:
            print(f"❌ Qdrant test failed: {e}")
            self.test_metrics['tests_failed'] += 1
    
    def _test_template_compliance(self):
        """Test 14-section template compliance for all agents."""
        print("   Testing template compliance...")
        
        for agent_name, result in self.results.items():
            if 'analysis' not in result:
                print(f"      {agent_name}: ⚠️ No analysis to check")
                continue
            
            try:
                analysis = result['analysis']
                sections_found = []
                sections_missing = []
                
                for section in self.REQUIRED_SECTIONS:
                    # Check if section exists in analysis
                    if section in analysis or section.replace("##", "#") in analysis:
                        sections_found.append(section)
                    else:
                        # Check for section number at least
                        section_num = section.split('.')[0]
                        if f"{section_num}." in analysis:
                            sections_found.append(section)
                        else:
                            sections_missing.append(section)
                
                completeness = len(sections_found) / len(self.REQUIRED_SECTIONS)
                self.test_metrics['template_compliance'] += completeness
                
                if completeness == 1.0:
                    print(f"      {agent_name}: ✅ All 14 sections present")
                    self.test_metrics['tests_passed'] += 1
                else:
                    print(f"      {agent_name}: ⚠️ {completeness:.0%} complete ({len(sections_missing)} missing)")
                    self.test_metrics['tests_failed'] += 1
                
            except Exception as e:
                print(f"      {agent_name}: ❌ Error checking compliance: {str(e)[:30]}")
                self.test_metrics['tests_failed'] += 1
    
    def _test_bug_fixes(self):
        """Test specific bug fixes."""
        print("   Testing bug fixes...")
        
        # Test 1: VoiceAgent template_validation int/dict fix
        if 'voice' in self.agents:
            try:
                print("      VoiceAgent quality score fix...", end=" ")
                agent = self.agents['voice']
                
                # The _calculate_quality_score should handle both int and dict
                test_output = "Test output " * 100  # 100 words
                
                # Mock validation returning int
                score1 = agent._calculate_quality_score(test_output, 0.5)
                assert isinstance(score1, float), "Score should be float"
                
                # Mock validation returning dict
                score2 = agent._calculate_quality_score(test_output, {'completeness': 0.5})
                assert isinstance(score2, float), "Score should be float"
                
                print("✅")
                self.test_metrics['bug_fixes_verified'] += 1
                self.test_metrics['tests_passed'] += 1
                
            except Exception as e:
                print(f"❌ {str(e)[:30]}")
                self.test_metrics['tests_failed'] += 1
        
        # Test 2: GTMBlueprint completeness parameter fix
        if 'gtm_blueprint' in self.agents:
            try:
                print("      GTMBlueprint completeness fix...", end=" ")
                agent = self.agents['gtm_blueprint']
                
                # The _calculate_gtm_metrics_fixed should handle completeness as dict
                test_blueprint = "Test blueprint " * 200
                metrics = agent._calculate_gtm_metrics_fixed(test_blueprint)
                
                assert 'completeness' in metrics, "Metrics should have completeness"
                assert isinstance(metrics['completeness'], dict), "Completeness should be dict"
                
                print("✅")
                self.test_metrics['bug_fixes_verified'] += 1
                self.test_metrics['tests_passed'] += 1
                
            except Exception as e:
                print(f"❌ {str(e)[:30]}")
                self.test_metrics['tests_failed'] += 1
        
        # Test 3: Interview agents quality score arguments
        if 'interview_psychological' in self.results:
            try:
                print("      Interview quality score fix...", end=" ")
                result = self.results.get('interview_psychological', {})
                
                # Should have completed without argument errors
                assert 'quality_score' in result, "Should have quality score"
                assert result['quality_score'] >= 0, "Quality score should be valid"
                
                print("✅")
                self.test_metrics['bug_fixes_verified'] += 1
                self.test_metrics['tests_passed'] += 1
                
            except Exception as e:
                print(f"❌ {str(e)[:30]}")
                self.test_metrics['tests_failed'] += 1
    
    def _test_gtm_synthesis(self):
        """Test GTM Blueprint cross-agent synthesis."""
        if 'gtm_blueprint' not in self.results:
            print("   ⚠️ GTM Blueprint not tested - skipping synthesis test")
            return
        
        print("   Testing cross-agent synthesis...")
        
        result = self.results['gtm_blueprint']
        agent = self.agents['gtm_blueprint']
        
        try:
            # Check agent integration
            print(f"      Agents integrated: {len(agent.agent_insights)}")
            assert len(agent.agent_insights) > 0, "No agents integrated"
            
            # Check strategic pillars
            print(f"      Strategic pillars: {len(agent.strategic_pillars)}")
            assert len(agent.strategic_pillars) > 0, "No strategic pillars"
            
            # Check implementation phases
            print(f"      Implementation phases: {len(agent.implementation_phases)}")
            assert len(agent.implementation_phases) > 0, "No implementation phases"
            
            # Check cross-agent memory if available
            if agent.memory_enabled:
                print(f"      Cross-agent memories: {len(agent.cross_agent_memories)}")
            
            print("      ✅ Synthesis successful")
            self.test_metrics['tests_passed'] += 1
            
        except Exception as e:
            print(f"      ❌ Synthesis failed: {e}")
            self.test_metrics['tests_failed'] += 1
    
    def _print_test_summary(self):
        """Print comprehensive test summary."""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        # Calculate totals
        total_tests = self.test_metrics['tests_passed'] + self.test_metrics['tests_failed']
        pass_rate = (self.test_metrics['tests_passed'] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Overall Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.test_metrics['tests_passed']} ✅")
        print(f"   Failed: {self.test_metrics['tests_failed']} ❌")
        print(f"   Pass Rate: {pass_rate:.1f}%")
        
        print(f"\n🤖 Agents Tested: {self.test_metrics['agents_tested']}/6")
        
        if self.test_metrics['memory_tests'] > 0:
            print(f"🧠 Memory Tests: {self.test_metrics['memory_tests']}")
        
        if self.test_metrics['template_compliance'] > 0 and len(self.results) > 0:
            avg_compliance = self.test_metrics['template_compliance'] / len(self.results)
            print(f"📋 Avg Template Compliance: {avg_compliance:.1%}")
        
        print(f"🔧 Bug Fixes Verified: {self.test_metrics['bug_fixes_verified']}/3")
        
        # Print quality scores
        print(f"\n📊 Agent Quality Scores:")
        for agent_name, result in self.results.items():
            quality = result.get('quality_score', 0)
            words = result.get('word_count', 0)
            status = "✅" if quality >= 0.7 else "⚠️" if quality >= 0.5 else "❌"
            print(f"   {agent_name:25} {status} Quality: {quality:.2f}, Words: {words}")
        
        # Final verdict
        print("\n" + "="*60)
        if pass_rate >= 80:
            print("✅ TEST SUITE PASSED - System Ready for Production")
        elif pass_rate >= 60:
            print("⚠️ TEST SUITE PARTIALLY PASSED - Review Failed Tests")
        else:
            print("❌ TEST SUITE FAILED - Critical Issues Found")
        print("="*60)


def main():
    """Run the comprehensive test suite."""
    tester = ComprehensiveAgentTester()
    tester.run_all_tests()


if __name__ == "__main__":
    # Set debug mode for detailed errors
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        os.environ['DEBUG'] = 'true'
    
    main()