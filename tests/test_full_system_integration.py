# test_full_system_integration.py
"""Test all 5 operational agents together with inter-agent communication"""

from team_icp.workflows.graph import graph
import json
from datetime import datetime

print("=" * 80)
print("🚀 FULL SYSTEM INTEGRATION TEST - ALL 5 AGENTS")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\nAgents to test:")
print("1. Psychological Analyst")
print("2. Voice of Customer")
print("3. Interview (Psychological)")
print("4. Interview (Sales)")
print("5. Competitor Intelligence")
print("-" * 80)

# Test Case: B2B SaaS for Financial Advisors
business_context = """
B2B SaaS platform helping independent financial advisors (RIAs) adopt AI tools for portfolio management.

Target Customer Profile:
- Independent RIAs managing $10M-$100M in assets
- Age 40-55, established practices
- 50-200 clients
- Feel threatened by robo-advisors but know they need to modernize
- Want to maintain personal relationships while scaling efficiency
- Fear being replaced by technology
- Pride themselves on personal touch and deep client relationships
"""

print("\n📋 BUSINESS CONTEXT:")
print("-" * 40)
print(business_context[:300] + "...")

# Run all 5 agents in sequence
state = {
    'task': 'Complete market analysis with all agents',
    'business_context': business_context,
    'master_context': business_context,
    'requested_agents': ['psychological', 'voice', 'interview', 'sales_interview', 'competitor'],
    'client_id': 'test_full_integration',
    'shared_insights': {}
}

print("\n🔄 STARTING FULL AGENT ORCHESTRATION...")
print("=" * 80)

try:
    # Track timing
    import time
    start_time = time.time()
    
    # Run the full graph
    result = graph.invoke(state)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("✅ FULL ORCHESTRATION COMPLETE!")
    print("=" * 80)
    
    # Extract results for each agent
    print("\n📊 AGENT PERFORMANCE SUMMARY:")
    print("-" * 40)
    
    # Check what each agent produced
    agents_data = {
        'psychological': {
            'output': result.get('result', {}).get('psychological', ''),
            'quality': None,
            'insights_shared': False
        },
        'voice': {
            'output': result.get('result', {}).get('voice', ''),
            'quality': None,
            'insights_shared': False
        },
        'interview': {
            'output': result.get('result', {}).get('interview', ''),
            'quality': None,
            'insights_shared': False
        },
        'sales_interview': {
            'output': result.get('result', {}).get('sales_interview', ''),
            'quality': None,
            'insights_shared': False
        },
        'competitor': {
            'output': result.get('result', {}).get('competitor', ''),
            'quality': None,
            'insights_shared': False
        }
    }
    
    # Display each agent's contribution
    for i, (agent_name, agent_data) in enumerate(agents_data.items(), 1):
        print(f"\n{i}. {agent_name.upper().replace('_', ' ')} AGENT:")
        print("   " + "-" * 36)
        
        output = agent_data['output']
        if output:
            print(f"   ✅ Output generated: {len(output)} characters")
            
            # Show preview
            preview = output[:200] + "..." if len(output) > 200 else output
            print(f"   📝 Preview: {preview}")
            
            # Check if insights were shared
            if agent_name in result.get('shared_insights', {}):
                print(f"   🔄 Shared insights with other agents: YES")
                agent_data['insights_shared'] = True
        else:
            print(f"   ❌ No output generated")
    
    # Check inter-agent communication
    print("\n🔄 INTER-AGENT COMMUNICATION ANALYSIS:")
    print("-" * 40)
    
    shared_insights = result.get('shared_insights', {})
    if shared_insights:
        print(f"✅ Shared insights pool active: {len(shared_insights)} agents contributed")
        
        for agent, insights in shared_insights.items():
            if insights:
                print(f"\n   {agent.upper()}:")
                preview = str(insights)[:150] + "..." if len(str(insights)) > 150 else str(insights)
                print(f"   {preview}")
    else:
        print("⚠️ No shared insights detected")
    
    # Check for psychological insights in other agents
    print("\n🧠 PSYCHOLOGICAL INTEGRATION CHECK:")
    print("-" * 40)
    
    psych_keywords = ['psychological', 'identity', 'fear', 'unconscious', 'emotional', 'cognitive']
    
    for agent_name, agent_data in agents_data.items():
        if agent_name != 'psychological' and agent_data['output']:
            keywords_found = [kw for kw in psych_keywords if kw.lower() in agent_data['output'].lower()]
            if keywords_found:
                print(f"✅ {agent_name}: Using psychological insights ({', '.join(keywords_found)})")
            else:
                print(f"⚠️ {agent_name}: No psychological integration detected")
    
    # Quality scores
    print("\n📈 QUALITY SCORES:")
    print("-" * 40)
    
    if 'quality_score' in result:
        print(f"Final Quality Score: {result['quality_score']:.2f}")
    
    # Check individual quality scores if available
    quality_met = 0
    quality_total = 0
    
    targets = {
        'psychological': 0.85,
        'voice': 0.80,
        'interview': 0.75,
        'sales_interview': 0.75,
        'competitor': 0.75
    }
    
    print("\nAgent Quality vs Targets:")
    for agent, target in targets.items():
        # Try to find quality score in various places
        quality = None
        
        # Check if there's agent-specific quality
        agent_state_key = f"{agent}_quality"
        if agent_state_key in result:
            quality = result[agent_state_key]
        
        if quality:
            status = "✅" if quality >= target else "⚠️"
            print(f"  {status} {agent}: {quality:.2f} (target: {target})")
            if quality >= target:
                quality_met += 1
            quality_total += 1
    
    if quality_total > 0:
        print(f"\n📊 Targets Met: {quality_met}/{quality_total} agents")
    
    # Execution metrics
    print("\n⏱️ EXECUTION METRICS:")
    print("-" * 40)
    print(f"Total execution time: {execution_time:.2f} seconds")
    print(f"Average per agent: {execution_time/5:.2f} seconds")
    
    # Human review requirements
    if result.get('requires_human_review'):
        print("\n⚠️ HUMAN REVIEW REQUIRED:")
        print(f"Reason: {result.get('review_reason', 'Not specified')}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("📊 FINAL INTEGRATION SUMMARY")
    print("=" * 80)
    
    successful_agents = sum(1 for agent_data in agents_data.values() if agent_data['output'])
    insights_sharing = sum(1 for agent_data in agents_data.values() if agent_data['insights_shared'])
    
    print(f"✅ Agents executed successfully: {successful_agents}/5")
    print(f"🔄 Agents sharing insights: {insights_sharing}/5")
    print(f"⏱️ Total time: {execution_time:.1f}s")
    
    if successful_agents == 5:
        print("\n🎉 FULL SYSTEM INTEGRATION SUCCESS!")
        print("All 5 agents are working together and producing outputs.")
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: {successful_agents}/5 agents produced output")
    
    # Save results to file for analysis
    output_file = f"integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Prepare JSON-serializable version
    save_data = {
        'test_date': datetime.now().isoformat(),
        'execution_time': execution_time,
        'agents_executed': successful_agents,
        'business_context': business_context,
        'agent_outputs': {
            agent: {
                'generated': bool(data['output']),
                'length': len(data['output']) if data['output'] else 0,
                'preview': data['output'][:500] if data['output'] else None
            }
            for agent, data in agents_data.items()
        },
        'shared_insights_active': bool(shared_insights),
        'human_review_required': result.get('requires_human_review', False)
    }
    
    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
except Exception as e:
    print(f"\n❌ ERROR during integration test: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🔬 INTEGRATION TEST COMPLETE")
print("=" * 80)

# Recommendations
print("\n💡 NEXT STEPS:")
print("-" * 40)
print("1. Review the agent outputs for quality and coherence")
print("2. Check if psychological insights are being used by other agents")
print("3. Verify that the competitor agent is using context from other agents")
print("4. Build the GTM Blueprint agent to synthesize all insights")
print("5. Add web search tools to enhance agent capabilities")