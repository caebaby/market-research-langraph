# tests/test_modular_architecture.py
"""
Comprehensive test suite for modular architecture
Tests all aspects of the dynamic agent system
"""

import os
import sys

from dotenv import load_dotenv
load_dotenv()

import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModularArchitectureTest:
    """Comprehensive test suite for modular architecture"""
    
    def __init__(self):
        self.results = {
            "tests_passed": 0,
            "tests_failed": 0,
            "errors": [],
            "warnings": [],
            "performance": {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_data = self._get_test_data()
    
    def _get_test_data(self) -> Dict[str, Any]:
        """Get test business contexts and configurations"""
        return {
            "contexts": {
                "financial": "AI-powered advisory platform for independent financial advisors managing $10M-$100M AUM, struggling with robo-advisor competition",
                "saas": "B2B SaaS platform for sales automation targeting mid-market companies with 50-500 employees",
                "coaching": "Executive coaching services for tech founders transitioning from technical to CEO roles"
            },
            "teams": ["icp", "sales", "research", "full"],
            "industries": ["financial_services", "saas", "coaching"],
            "custom_agents": ["psychological", "voice", "competitor"]
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete test suite"""
        print("\n" + "=" * 80)
        print("🚀 MODULAR ARCHITECTURE COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"Working Directory: {os.getcwd()}")
        
        # Check environment
        if not self._check_environment():
            return self.results
        
        # Run test modules
        test_modules = [
            ("Registry System", self.test_registry),
            ("Agent Factory", self.test_agent_factory),
            ("Team Configurations", self.test_team_configs),
            ("Industry Templates", self.test_industry_templates),
            ("Dynamic Workflow", self.test_workflow),
            ("Custom Configurations", self.test_custom_config),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        for test_name, test_func in test_modules:
            print(f"\n{'=' * 60}")
            print(f"📋 Testing: {test_name}")
            print("=" * 60)
            
            try:
                start_time = time.time()
                success = test_func()
                elapsed = time.time() - start_time
                
                self.results["performance"][test_name] = elapsed
                
                if success:
                    self.results["tests_passed"] += 1
                    print(f"✅ {test_name} PASSED ({elapsed:.2f}s)")
                else:
                    self.results["tests_failed"] += 1
                    print(f"❌ {test_name} FAILED ({elapsed:.2f}s)")
                    
            except Exception as e:
                self.results["tests_failed"] += 1
                self.results["errors"].append({
                    "test": test_name,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                print(f"❌ {test_name} ERROR: {e}")
        
        # Generate report
        self._generate_report()
        return self.results
    
    def _check_environment(self) -> bool:
        """Check environment setup"""
        print("\n🔍 ENVIRONMENT CHECK")
        print("-" * 40)
        
        checks = []
        
        # Check API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            print("✅ ANTHROPIC_API_KEY: Found")
            checks.append(True)
        else:
            print("❌ ANTHROPIC_API_KEY: Missing")
            self.results["errors"].append({"test": "Environment", "error": "Missing API key"})
            checks.append(False)
        
        # Check imports
        try:
            from team_icp.agents.registry import AgentFactory, AGENT_REGISTRY, TEAM_CONFIGS
            print(f"✅ Registry Import: Success ({len(AGENT_REGISTRY)} agents)")
            checks.append(True)
        except ImportError as e:
            print(f"❌ Registry Import: Failed - {e}")
            self.results["errors"].append({"test": "Environment", "error": f"Import failed: {e}"})
            checks.append(False)
        
        try:
            from team_icp.workflows.graph import graph
            print(f"✅ Workflow Import: Success")
            checks.append(True)
        except ImportError as e:
            print(f"❌ Workflow Import: Failed - {e}")
            self.results["errors"].append({"test": "Environment", "error": f"Import failed: {e}"})
            checks.append(False)
        
        # Check file structure
        required_files = [
            "team_icp/agents/registry.py",
            "team_icp/workflows/graph.py",
            "core/standard_agent_v4.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ File Exists: {file_path}")
                checks.append(True)
            else:
                print(f"❌ File Missing: {file_path}")
                self.results["warnings"].append(f"Missing file: {file_path}")
                checks.append(False)
        
        return all(checks)
    
    def test_registry(self) -> bool:
        """Test agent registry system"""
        try:
            from team_icp.agents.registry import AgentFactory, AGENT_REGISTRY
            
            # Test 1: Registry populated
            print(f"📊 Registry contains {len(AGENT_REGISTRY)} agents")
            assert len(AGENT_REGISTRY) >= 6, "Registry should have at least 6 agents"
            
            # Test 2: List all agents
            agents = AgentFactory.list_available_agents()
            print(f"✅ Available agents: {', '.join(agents)}")
            
            # Test 3: Verify expected agents
            expected = ["psychological", "voice", "competitor", "gtm_blueprint", "interview", "sales_interview"]
            missing = [a for a in expected if a not in agents]
            
            if missing:
                print(f"⚠️ Missing agents: {missing}")
                self.results["warnings"].append(f"Missing agents: {missing}")
                return False
            
            print("✅ All expected agents present")
            return True
            
        except Exception as e:
            logger.error(f"Registry test failed: {e}")
            return False
    
    def test_agent_factory(self) -> bool:
        """Test agent creation factory"""
        try:
            from team_icp.agents.registry import AgentFactory
            
            success_count = 0
            test_agents = ["psychological", "voice", "competitor"]
            
            for agent_name in test_agents:
                try:
                    # Create agent
                    agent = AgentFactory.create_agent(agent_name)
                    
                    # Verify attributes
                    assert hasattr(agent, 'agent_name'), f"{agent_name} missing agent_name"
                    assert hasattr(agent, 'target_quality'), f"{agent_name} missing target_quality"
                    assert hasattr(agent, '__call__'), f"{agent_name} not callable"
                    
                    print(f"✅ Created {agent_name}: {agent.agent_name} (quality: {agent.target_quality})")
                    success_count += 1
                    
                except Exception as e:
                    print(f"❌ Failed to create {agent_name}: {e}")
                    self.results["errors"].append({
                        "test": "Agent Factory",
                        "agent": agent_name,
                        "error": str(e)
                    })
            
            return success_count == len(test_agents)
            
        except Exception as e:
            logger.error(f"Agent factory test failed: {e}")
            return False
    
    def test_team_configs(self) -> bool:
        """Test team configurations"""
        try:
            from team_icp.agents.registry import AgentFactory, TEAM_CONFIGS
            
            print(f"📊 Testing {len(TEAM_CONFIGS)} team configurations")
            
            for team_name, config in TEAM_CONFIGS.items():
                print(f"\n🔍 Team: {team_name}")
                print(f"   Name: {config['name']}")
                print(f"   Agents: {len(config['agents'])}")
                print(f"   Sequence: {' → '.join(config['sequence'][:3])}...")
                
                # Validate sequence
                valid = AgentFactory.validate_agent_sequence(config['agents'])
                if not valid:
                    print(f"   ⚠️ Invalid agent sequence")
                    self.results["warnings"].append(f"Team {team_name} has invalid agents")
                else:
                    print(f"   ✅ Valid sequence")
            
            # Test team creation
            team = AgentFactory.create_team("icp", industry="saas")
            assert "agent_instances" in team, "Team should have agent instances"
            assert len(team["agent_instances"]) > 0, "Team should have agents"
            
            print(f"\n✅ Successfully created team with {len(team['agent_instances'])} agents")
            return True
            
        except Exception as e:
            logger.error(f"Team config test failed: {e}")
            return False
    
    def test_industry_templates(self) -> bool:
        """Test industry templates"""
        try:
            from team_icp.agents.registry import INDUSTRY_TEMPLATES
            
            print(f"📊 Testing {len(INDUSTRY_TEMPLATES)} industry templates")
            
            for industry, template in INDUSTRY_TEMPLATES.items():
                required_keys = ["context_prefix", "psychological_focus", "voice_emphasis"]
                missing = [k for k in required_keys if k not in template]
                
                if missing:
                    print(f"⚠️ {industry}: Missing keys {missing}")
                    self.results["warnings"].append(f"Industry {industry} missing: {missing}")
                else:
                    print(f"✅ {industry}: Complete template")
            
            return True
            
        except Exception as e:
            logger.error(f"Industry template test failed: {e}")
            return False
    
    def test_workflow(self) -> bool:
        """Test dynamic workflow execution"""
        try:
            from team_icp.workflows.graph import graph, run_team_analysis
            
            if not graph:
                print("❌ Workflow graph not compiled")
                return False
            
            print("✅ Workflow graph compiled successfully")
            
            # Test with minimal configuration
            print("\n🔄 Running test workflow...")
            
            state = {
                "task": "Test workflow",
                "business_context": self.test_data["contexts"]["financial"],
                "requested_agents": ["psychological"],
                "client_id": "test_workflow"
            }
            
            start_time = time.time()
            result = graph.invoke(state)
            elapsed = time.time() - start_time
            
            # Validate result
            assert "result" in result, "Result should contain 'result' key"
            assert "psychological" in result["result"], "Result should contain psychological output"
            
            output_length = len(str(result["result"]["psychological"]))
            print(f"✅ Workflow completed in {elapsed:.2f}s")
            print(f"   Output: {output_length} characters")
            
            # Test team analysis helper
            print("\n🔄 Testing team analysis helper...")
            team_result = run_team_analysis(
                business_context=self.test_data["contexts"]["saas"],
                team_name="research",
                industry="saas"
            )
            
            assert "result" in team_result, "Team result should contain outputs"
            print(f"✅ Team analysis completed with {len(team_result.get('result', {}))} agents")
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow test failed: {e}")
            self.results["errors"].append({
                "test": "Workflow",
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return False
    
    def test_custom_config(self) -> bool:
        """Test custom agent configuration"""
        try:
            from team_icp.agents.registry import AgentFactory
            from team_icp.workflows.graph import run_custom_analysis
            
            # Create agent with custom config
            custom_config = {
                "target_quality": 0.95,
                "require_human_review_below": 0.85
            }
            
            agent = AgentFactory.create_agent("psychological", custom_config)
            
            assert agent.target_quality == 0.95, "Custom quality not applied"
            assert agent.review_threshold == 0.85, "Custom threshold not applied"
            
            print(f"✅ Custom configuration applied:")
            print(f"   Target Quality: {agent.target_quality}")
            print(f"   Review Threshold: {agent.review_threshold}")
            
            # Test with workflow
            result = run_custom_analysis(
                business_context=self.test_data["contexts"]["coaching"],
                agents=["psychological"],
                config_overrides={"psychological": custom_config}
            )
            
            print("✅ Custom analysis completed")
            return True
            
        except Exception as e:
            logger.error(f"Custom config test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and recovery"""
        try:
            from team_icp.agents.registry import AgentFactory
            
            # Test 1: Invalid agent name
            try:
                agent = AgentFactory.create_agent("nonexistent_agent")
                print("❌ Should have raised error for invalid agent")
                return False
            except ValueError as e:
                print(f"✅ Correctly caught invalid agent: {e}")
            
            # Test 2: Invalid team name
            try:
                team = AgentFactory.create_team("nonexistent_team")
                print("❌ Should have raised error for invalid team")
                return False
            except ValueError as e:
                print(f"✅ Correctly caught invalid team: {e}")
            
            # Test 3: Workflow with invalid agents
            from team_icp.workflows.graph import graph
            
            if graph:
                state = {
                    "task": "Error test",
                    "business_context": "Test",
                    "requested_agents": ["psychological", "invalid_agent"],
                    "client_id": "test_error"
                }
                
                result = graph.invoke(state)
                
                # Should complete despite invalid agent
                if "result" in result:
                    print("✅ Workflow handled invalid agent gracefully")
                else:
                    print("⚠️ Workflow may not have handled error properly")
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    def test_performance(self) -> bool:
        """Test performance metrics"""
        try:
            from team_icp.agents.registry import AgentFactory
            from team_icp.workflows.graph import graph
            
            print("⏱️ Performance Benchmarks:")
            
            # Agent creation performance
            start = time.time()
            for _ in range(10):
                agent = AgentFactory.create_agent("psychological")
            agent_time = (time.time() - start) / 10
            print(f"   Agent Creation: {agent_time*1000:.2f}ms avg")
            
            # Team creation performance
            start = time.time()
            team = AgentFactory.create_team("icp")
            team_time = time.time() - start
            print(f"   Team Creation: {team_time*1000:.2f}ms")
            
            # Workflow execution (minimal)
            if graph:
                start = time.time()
                state = {
                    "task": "Performance test",
                    "business_context": "Quick test",
                    "requested_agents": ["psychological"],
                    "client_id": "perf_test"
                }
                result = graph.invoke(state)
                workflow_time = time.time() - start
                print(f"   Single Agent Workflow: {workflow_time:.2f}s")
            
            # All metrics should be reasonable
            assert agent_time < 0.1, "Agent creation too slow"
            assert team_time < 1.0, "Team creation too slow"
            
            print("✅ Performance within acceptable limits")
            return True
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return False
    
    def _generate_report(self):
        """Generate final test report"""
        print("\n" + "=" * 80)
        print("📊 TEST REPORT")
        print("=" * 80)
        
        total_tests = self.results["tests_passed"] + self.results["tests_failed"]
        pass_rate = (self.results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📈 Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {self.results['tests_passed']} ({pass_rate:.1f}%)")
        print(f"   Failed: {self.results['tests_failed']}")
        
        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])}):")
            for error in self.results["errors"][:5]:  # Show first 5 errors
                print(f"   • {error.get('test', 'Unknown')}: {error.get('error', 'Unknown error')}")
        
        if self.results["warnings"]:
            print(f"\n⚠️ Warnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:5]:  # Show first 5 warnings
                print(f"   • {warning}")
        
        if self.results["performance"]:
            print(f"\n⏱️ Performance:")
            for test, duration in self.results["performance"].items():
                print(f"   {test}: {duration:.2f}s")
            total_time = sum(self.results["performance"].values())
            print(f"   Total Time: {total_time:.2f}s")
        
        # Final verdict
        print("\n" + "=" * 80)
        if pass_rate == 100:
            print("🎉 PERFECT! Modular architecture is fully operational!")
            print("\n✨ Your system can now:")
            print("   ✅ Dynamically load any agent by name")
            print("   ✅ Configure teams for different use cases")
            print("   ✅ Apply industry-specific templates")
            print("   ✅ Override configurations per client")
            print("   ✅ Add new agents without changing core code")
        elif pass_rate >= 80:
            print("✅ SUCCESS! Modular architecture is mostly working.")
            print(f"   Some minor issues to address ({self.results['tests_failed']} failed tests)")
        elif pass_rate >= 60:
            print("⚠️ PARTIAL SUCCESS. Core functionality works but needs attention.")
        else:
            print("❌ CRITICAL ISSUES. Modular architecture needs debugging.")
        
        # Save report to file
        self._save_report()
    
    def _save_report(self):
        """Save test report to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"modular_test_report_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n💾 Report saved to: {filename}")
        except Exception as e:
            print(f"⚠️ Could not save report: {e}")


def main():
    """Main test execution"""
    # Clear screen for better visibility
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Create and run test suite
    test_suite = ModularArchitectureTest()
    results = test_suite.run_all_tests()
    
    # Return exit code based on results
    if results["tests_failed"] == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()