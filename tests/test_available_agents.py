# test_available_agents.py
"""
Complete test suite for Level 5 ICP Intelligence System
Tests all 6 agents with proper module detection and quality scoring
"""

import os
import sys
import json
import importlib
import inspect
import re
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

# Define the complete list of 6 agents with CORRECT module paths
AGENT_MODULES = [
    ('team_icp.agents.psychological', 'PsychologicalAgent'),
    ('team_icp.agents.voice', 'VoiceAgent'),
    ('team_icp.agents.competitor', 'CompetitorAgent'),
    ('team_icp.agents.interview_psychological_v4', 'PsychologicalInterviewAgentV4'),
    ('team_icp.agents.interview_sales_v4', 'SalesInterviewAgentV4'),
    ('team_icp.agents.gtm_blueprint', 'GTMBlueprintAgent'),
]

# Quality and word count requirements per agent type
AGENT_REQUIREMENTS = {
    'PsychologicalAgent': {
        'min_words': 1200,
        'target_words': 1500,
        'max_words': 1800,
        'min_quality': 0.85,
        'name': 'Psychological Analyst'
    },
    'VoiceAgent': {
        'min_words': 1200,
        'target_words': 1500,
        'max_words': 1800,
        'min_quality': 0.85,
        'name': 'Voice Alchemist'
    },
    'CompetitorAgent': {
        'min_words': 1200,
        'target_words': 1500,
        'max_words': 1800,
        'min_quality': 0.80,
        'name': 'Competitor Analyst'
    },
    'PsychologicalInterviewAgentV4': {
        'min_words': 2000,
        'target_words': 2500,
        'max_words': 3000,
        'min_quality': 0.80,
        'name': 'Interview Psychological'
    },
    'SalesInterviewAgentV4': {
        'min_words': 2000,
        'target_words': 2500,
        'max_words': 3000,
        'min_quality': 0.80,
        'name': 'Interview Sales'
    },
    'GTMBlueprintAgent': {
        'min_words': 2500,
        'target_words': 3000,
        'max_words': 3500,
        'min_quality': 0.85,
        'name': 'GTM Blueprint Strategist'
    }
}


class AgentTester:
    """Test harness for Level 5 ICP Intelligence System agents"""
    
    def __init__(self):
        """Initialize the test environment"""
        # Setup API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        print("✅ API Key loaded successfully")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=api_key
        )
        
        # Results storage
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'agents_tested': [],
            'agents_passed': [],
            'agents_failed': [],
            'agents_missing': [],
            'detailed_results': {}
        }
        
        # Ensure output directory exists
        self.output_dir = Path("test_outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def detect_available_agents(self) -> List[Tuple[Any, str, Dict]]:
        """Detect which agents are available and can be instantiated"""
        available_agents = []
        
        print("\n🔍 Detecting available agents...")
        
        for module_path, class_name in AGENT_MODULES:
            try:
                # Try to import the module
                module = importlib.import_module(module_path)
                
                # Try to get the agent class
                if hasattr(module, class_name):
                    agent_class = getattr(module, class_name)
                    requirements = AGENT_REQUIREMENTS.get(class_name, {})
                    agent_name = requirements.get('name', class_name)
                    print(f"   ✅ Found: {agent_name}")
                    available_agents.append((agent_class, class_name, requirements))
                else:
                    print(f"   ⚠️  Class not found: {class_name} in {module_path}")
                    self.results['agents_missing'].append(f"{module_path}.{class_name}")
                    
            except ImportError as e:
                print(f"   ⏭️  Module not found: {module_path} ({str(e)})")
                self.results['agents_missing'].append(f"{module_path}.{class_name}")
            except Exception as e:
                print(f"   ❌ Error loading {module_path}: {str(e)}")
                self.results['agents_missing'].append(f"{module_path}.{class_name}")
        
        print(f"\n📊 Found {len(available_agents)} agents to test")
        return available_agents
    
    def test_agent(self, agent_class: Any, class_name: str, requirements: Dict) -> Dict[str, Any]:
        """Test a single agent's capabilities"""
        agent_name = requirements.get('name', class_name)
        
        print(f"\nTesting: {agent_name}")
        print("-" * 40)
        
        result = {
            'agent_name': agent_name,
            'class_name': class_name,
            'status': 'FAILED',
            'word_count': 0,
            'quality_score': 0.0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Instantiate agent
            agent = agent_class()
            
            # Test task
            task = """Analyze a B2B SaaS company selling AI-powered customer service automation 
            to enterprise contact centers. Focus on psychological drivers, pain points, 
            and decision-making factors. Provide actionable insights."""
            
            # Shared insights for context
            shared_insights = {
                'market_size': '$15B enterprise contact center market',
                'key_pain': 'High agent turnover and training costs',
                'budget_range': '$100K-500K annual',
                'decision_makers': 'VP Customer Success, CTO, CFO'
            }
            
            # Process task based on agent's available methods
            output = None
            
            # Try different method signatures based on what the agent supports
            if hasattr(agent, 'process'):
                # Standard process method
                memories = []
                output = agent.process(task, shared_insights, self.llm)
            elif hasattr(agent, '_generate_response'):
                # Check signature of _generate_response
                sig = inspect.signature(agent._generate_response)
                params = list(sig.parameters.keys())
                
                if len(params) == 3 and 'memories' in params:
                    # New signature: (task, memories, llm)
                    memories = []
                    output = agent._generate_response(task, memories, self.llm)
                elif len(params) == 4 and 'context' in params:
                    # Old signature: (task, context, memories, llm)
                    context = json.dumps(shared_insights)
                    memories = []
                    output = agent._generate_response(task, context, memories, self.llm)
                else:
                    # Unknown signature
                    result['errors'].append(f"Unknown _generate_response signature: {params}")
                    return result
            else:
                result['errors'].append("No suitable processing method found")
                return result
            
            # Extract output string if needed
            if isinstance(output, dict):
                output_text = output.get('output', output.get('result', str(output)))
            else:
                output_text = str(output)
            
            # Calculate metrics
            word_count = len(output_text.split())
            result['word_count'] = word_count
            
            # Get quality score
            quality_score = self._calculate_quality_score(agent, task, output_text)
            result['quality_score'] = quality_score
            
            # Check requirements
            min_words = requirements.get('min_words', 1000)
            target_words = requirements.get('target_words', 1500)
            min_quality = requirements.get('min_quality', 0.75)
            
            # Display results
            print(f"📝 Words: {word_count} (min: {min_words}, target: {target_words})")
            print(f"⭐ Quality: {quality_score:.2f} (required: {min_quality})")
            
            # Determine pass/fail
            word_pass = word_count >= min_words
            quality_pass = quality_score >= min_quality
            
            if word_pass and quality_pass:
                print("✅ PASSED")
                result['status'] = 'PASSED'
                self.results['agents_passed'].append(agent_name)
            else:
                print("❌ FAILED")
                if not word_pass:
                    diff = min_words - word_count
                    print(f"   Need {diff} more words")
                    result['warnings'].append(f"Need {diff} more words")
                if not quality_pass:
                    diff = min_quality - quality_score
                    print(f"   Need {diff:.2f} quality improvement")
                    result['warnings'].append(f"Need {diff:.2f} quality improvement")
                self.results['agents_failed'].append(agent_name)
            
            # Store sample output
            result['sample_output'] = output_text[:500] + "..." if len(output_text) > 500 else output_text
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            result['errors'].append(str(e))
            result['status'] = 'ERROR'
            self.results['agents_failed'].append(agent_name)
        
        self.results['agents_tested'].append(agent_name)
        self.results['detailed_results'][agent_name] = result
        return result
    
    def _calculate_quality_score(self, agent: Any, task: str, output: str) -> float:
        """Calculate quality score for agent output"""
        try:
            if hasattr(agent, '_reflect'):
                # Use agent's built-in reflection
                reflection = agent._reflect(task, output, self.llm)
                
                # Extract score from reflection
                if isinstance(reflection, dict):
                    return float(reflection.get('score', 0.5))
                elif isinstance(reflection, (int, float)):
                    return float(reflection)
                elif isinstance(reflection, str):
                    # Try to extract score from string
                    score_match = re.search(r'(?:score|quality)[:\s]*([0-9]\.[0-9]+)', reflection.lower())
                    if score_match:
                        return float(score_match.group(1))
                    
                    # Look for percentage
                    pct_match = re.search(r'([0-9]+)%', reflection)
                    if pct_match:
                        return float(pct_match.group(1)) / 100
            
            # Fallback: Basic heuristic scoring
            score = 0.5  # Base score
            
            # Word count bonus
            word_count = len(output.split())
            if word_count > 1000:
                score += 0.1
            if word_count > 1500:
                score += 0.1
            
            # Content quality indicators
            if any(word in output.lower() for word in ['insight', 'analysis', 'recommend']):
                score += 0.1
            if any(word in output.lower() for word in ['psychology', 'emotional', 'cognitive']):
                score += 0.05
            if any(word in output.lower() for word in ['action', 'implement', 'strategy']):
                score += 0.05
            
            return min(score, 1.0)
            
        except Exception as e:
            print(f"   ⚠️  Quality scoring error: {str(e)}")
            return 0.5  # Default middle score
    
    def run_tests(self) -> Dict[str, Any]:
        """Run tests on all available agents"""
        print("\n" + "="*60)
        print("🚀 LEVEL 5 ICP INTELLIGENCE SYSTEM - AGENT TESTING")
        print("="*60)
        
        # Detect available agents
        available_agents = self.detect_available_agents()
        
        if not available_agents:
            print("\n❌ No agents found to test!")
            return self.results
        
        # Test each agent
        for agent_class, class_name, requirements in available_agents:
            self.test_agent(agent_class, class_name, requirements)
        
        # Generate summary
        self._generate_summary()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*60)
        print("📊 FINAL SUMMARY")
        print("="*60)
        
        total_agents = len(AGENT_MODULES)
        tested = len(self.results['agents_tested'])
        passed = len(self.results['agents_passed'])
        failed = len(self.results['agents_failed'])
        missing = len(self.results['agents_missing'])
        
        # Show passed agents
        if self.results['agents_passed']:
            print(f"\n✅ PASSED AGENTS ({passed}/{tested}):")
            for agent in self.results['agents_passed']:
                details = self.results['detailed_results'][agent]
                print(f"   • {agent}: Quality={details['quality_score']:.2f}, Words={details['word_count']}")
        
        # Show failed agents
        if self.results['agents_failed']:
            print(f"\n❌ FAILED AGENTS ({failed}/{tested}):")
            for agent in self.results['agents_failed']:
                if agent in self.results['detailed_results']:
                    details = self.results['detailed_results'][agent]
                    print(f"   • {agent}: Quality={details['quality_score']:.2f}, Words={details['word_count']}")
        
        # Show missing agents
        if self.results['agents_missing']:
            print(f"\n⚠️ MISSING AGENTS (not found):")
            for module in self.results['agents_missing']:
                # Extract just the class name for cleaner display
                class_name = module.split('.')[-1]
                if class_name in AGENT_REQUIREMENTS:
                    print(f"   • {AGENT_REQUIREMENTS[class_name]['name']}")
                else:
                    print(f"   • {module}")
        
        # Overall status
        print("\n" + "="*60)
        if passed == total_agents:
            print("🎉 SUCCESS! All agents are working perfectly!")
        elif passed == tested and tested > 0:
            print(f"✅ All available agents ({tested}/{total_agents}) are working!")
            if missing > 0:
                print(f"   {missing} agents are missing/not implemented")
        elif passed > 0:
            print(f"⚠️ PARTIAL SUCCESS: {passed}/{total_agents} agents working")
        else:
            print("❌ CRITICAL: No agents are fully functional")
        
        # Action items
        if failed > 0 or missing > 0:
            print("\n📋 Action Items:")
            
            for agent in self.results['agents_failed']:
                if agent in self.results['detailed_results']:
                    details = self.results['detailed_results'][agent]
                    for warning in details.get('warnings', []):
                        print(f"   • {agent}: {warning}")
            
            if missing > 0:
                print(f"   • Implement/fix {missing} missing agents")
    
    def _save_results(self):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"agents_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {filename}")


def main():
    """Main test execution"""
    try:
        tester = AgentTester()
        results = tester.run_tests()
        
        # Return exit code based on results
        if len(results['agents_passed']) == len(AGENT_MODULES):
            return 0  # All tests passed
        elif len(results['agents_passed']) > 0:
            return 1  # Some tests passed
        else:
            return 2  # All tests failed
            
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)