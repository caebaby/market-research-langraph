#!/usr/bin/env python3
"""
Comprehensive test suite for ALL Level 5 ICP Intelligence System agents
Tests quality scores, word counts, and readiness for production
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import json

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Import all agents
from team_icp.agents.psychological import PsychologicalAgent
from team_icp.agents.voice import VoiceAgent
from team_icp.agents.competitor import CompetitorAgent
from team_icp.agents.interview_psychological import InterviewPsychologicalAgent
from team_icp.agents.interview_sales import InterviewSalesAgent
from team_icp.agents.gtm_blueprint import GTMBlueprintAgent

from langchain_anthropic import ChatAnthropic
from colorama import init, Fore, Style

init(autoreset=True)

class AgentMetricsTester:
    """Test all agents and track metrics"""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4000
        )
        self.results = {}
        
        # Define success criteria for each agent
        self.success_criteria = {
            "Psychological Analyst": {
                "min_quality": 0.85,
                "min_words": 1200,
                "target_words": 1500
            },
            "Voice Alchemist": {
                "min_quality": 0.85,
                "min_words": 1200,
                "target_words": 1500
            },
            "Competitor Analyst": {
                "min_quality": 0.80,
                "min_words": 1200,
                "target_words": 1500
            },
            "Interview Psychological": {
                "min_quality": 0.80,
                "min_words": 1000,
                "target_words": 1200
            },
            "Interview Sales": {
                "min_quality": 0.80,
                "min_words": 1000,
                "target_words": 1200
            },
            "GTM Blueprint Strategist": {
                "min_quality": 0.85,
                "min_words": 2500,
                "target_words": 3000
            }
        }
    
    def test_agent(self, agent_class, agent_name: str, task: str, shared_insights: Dict = None) -> Dict[str, Any]:
        """Test a single agent and return metrics"""
        
        print(f"\n{Fore.CYAN}Testing: {agent_name}{Style.RESET_ALL}")
        print("-" * 40)
        
        try:
            # Initialize agent
            agent = agent_class()
            
            # Prepare shared insights if needed
            if shared_insights is None:
                shared_insights = self._get_default_shared_insights()
            
            # Process task
            if hasattr(agent, 'process'):
                result = agent.process(task, shared_insights, self.llm)
            else:
                result = agent._generate_response(task, self.llm)
            
            # Get output
            if isinstance(result, dict):
                output = result.get('output', str(result))
            else:
                output = str(result)
            
            # Calculate metrics
            word_count = len(output.split())
            
            # Run reflection to get quality score
            reflection = agent._reflect(task, output, self.llm)
            quality_score = reflection.get('score', 0.0)
            
            # Check against criteria
            criteria = self.success_criteria[agent_name]
            meets_quality = quality_score >= criteria["min_quality"]
            meets_words = word_count >= criteria["min_words"]
            
            # Store results
            result_data = {
                "agent": agent_name,
                "word_count": word_count,
                "quality_score": quality_score,
                "meets_quality": meets_quality,
                "meets_words": meets_words,
                "passed": meets_quality and meets_words,
                "criteria": criteria,
                "output_preview": output[:200] + "..."
            }
            
            # Display results
            self._display_agent_results(result_data)
            
            return result_data
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error testing {agent_name}: {str(e)}{Style.RESET_ALL}")
            return {
                "agent": agent_name,
                "error": str(e),
                "passed": False
            }
    
    def _display_agent_results(self, result: Dict[str, Any]):
        """Display results for a single agent"""
        
        criteria = result.get("criteria", {})
        
        # Word count
        word_color = Fore.GREEN if result.get("meets_words") else Fore.YELLOW
        print(f"📝 Words: {word_color}{result['word_count']}{Style.RESET_ALL} "
              f"(min: {criteria['min_words']}, target: {criteria['target_words']})")
        
        # Quality score
        quality_color = Fore.GREEN if result.get("meets_quality") else Fore.YELLOW
        print(f"⭐ Quality: {quality_color}{result['quality_score']:.2f}{Style.RESET_ALL} "
              f"(required: {criteria['min_quality']})")
        
        # Pass/Fail
        if result.get("passed"):
            print(f"{Fore.GREEN}✅ PASSED{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ FAILED{Style.RESET_ALL}")
            if not result.get("meets_words"):
                print(f"   Need {criteria['min_words'] - result['word_count']} more words")
            if not result.get("meets_quality"):
                print(f"   Need {criteria['min_quality'] - result['quality_score']:.2f} quality improvement")
    
    def _get_default_shared_insights(self) -> Dict[str, Any]:
        """Get default shared insights for testing"""
        return {
            'psychological': {
                'summary': 'Deep fear of being blamed for churn. Identity tied to team success.'
            },
            'voice': {
                'summary': 'Language: proactive, at-risk, health score. Never say: automate.'
            },
            'competitor': {
                'summary': 'Gainsight: complex. ChurnZero: lacks AI. Opening: AI-native.'
            }
        }
    
    def run_all_tests(self):
        """Run tests for all agents"""
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"🚀 LEVEL 5 ICP INTELLIGENCE SYSTEM - ALL AGENTS TEST")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        # Define test tasks for each agent
        base_task = """Analyze a B2B SaaS product:
        PRODUCT: AI-powered customer success platform
        TARGET: VP of Customer Success at Series B-D SaaS companies (100-500 employees)
        PROBLEM: Customer churn prediction and prevention at scale"""
        
        test_configs = [
            (PsychologicalAgent, "Psychological Analyst", base_task),
            (VoiceAgent, "Voice Alchemist", base_task),
            (CompetitorAgent, "Competitor Analyst", base_task),
            (InterviewPsychologicalAgent, "Interview Psychological", base_task),
            (InterviewSalesAgent, "Interview Sales", base_task),
            (GTMBlueprintAgent, "GTM Blueprint Strategist", base_task)
        ]
        
        # Run tests
        for agent_class, agent_name, task in test_configs:
            result = self.test_agent(agent_class, agent_name, task)
            self.results[agent_name] = result
        
        # Display summary
        self._display_summary()
        
        # Save detailed report
        self._save_report()
    
    def _display_summary(self):
        """Display summary of all tests"""
        
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        passed_agents = []
        failed_agents = []
        
        for agent_name, result in self.results.items():
            if result.get("error"):
                failed_agents.append((agent_name, "Error", "N/A"))
            elif result.get("passed"):
                passed_agents.append((agent_name, result['quality_score'], result['word_count']))
            else:
                failed_agents.append((agent_name, result['quality_score'], result['word_count']))
        
        # Display passed agents
        if passed_agents:
            print(f"\n{Fore.GREEN}✅ PASSED AGENTS ({len(passed_agents)}/{len(self.results)}):{Style.RESET_ALL}")
            for name, quality, words in passed_agents:
                print(f"   • {name}: Quality={quality:.2f}, Words={words}")
        
        # Display failed agents
        if failed_agents:
            print(f"\n{Fore.RED}❌ FAILED AGENTS ({len(failed_agents)}/{len(self.results)}):{Style.RESET_ALL}")
            for name, quality, words in failed_agents:
                print(f"   • {name}: Quality={quality}, Words={words}")
        
        # Overall status
        all_passed = len(passed_agents) == len(self.results)
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        if all_passed:
            print(f"{Fore.GREEN}🎉 SUCCESS! ALL AGENTS MEET PRODUCTION METRICS!{Style.RESET_ALL}")
            print(f"\n📋 Next Steps:")
            print(f"1. ✅ All agents have quality 'brains' installed")
            print(f"2. ✅ Ready for /analyze endpoint integration")
            print(f"3. ✅ Ready for Slack bot deployment")
            print(f"\n🚀 The system is ready for production use!")
        else:
            print(f"{Fore.YELLOW}⚠️ SOME AGENTS NEED IMPROVEMENT{Style.RESET_ALL}")
            print(f"\n📋 Action Items:")
            for name, quality, words in failed_agents:
                criteria = self.success_criteria.get(name, {})
                if isinstance(quality, float):
                    if quality < criteria.get("min_quality", 0.85):
                        print(f"• {name}: Improve quality from {quality:.2f} to {criteria['min_quality']}")
                    if isinstance(words, int) and words < criteria.get("min_words", 1200):
                        print(f"• {name}: Increase output from {words} to {criteria['min_words']} words")
    
    def _save_report(self):
        """Save detailed report to file"""
        
        report_dir = Path("test_outputs")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"all_agents_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_file}")

def main():
    """Main test execution"""
    
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print(f"{Fore.RED}❌ ERROR: ANTHROPIC_API_KEY not found in environment!{Style.RESET_ALL}")
        return False
    
    # Run tests
    tester = AgentMetricsTester()
    tester.run_all_tests()
    
    # Return success status
    all_passed = all(r.get("passed", False) for r in tester.results.values())
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)