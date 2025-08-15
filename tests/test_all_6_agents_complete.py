# test_all_6_agents_complete.py
"""Ultimate test - ALL 6 agents working together in full orchestration"""

from team_icp.workflows.graph import graph
import json
from datetime import datetime
import time

print("=" * 80)
print("🚀 ULTIMATE SYSTEM TEST - ALL 6 AGENTS")
print("=" * 80)
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n📋 AGENTS TO TEST:")
print("1. Psychological Analyst (Target: ≥0.85)")
print("2. Voice of Customer (Target: ≥0.80)")
print("3. Interview - Psychological (Target: ≥0.75)")
print("4. Interview - Sales (Target: ≥0.75)")
print("5. Competitor Intelligence (Target: ≥0.75)")
print("6. GTM Blueprint Synthesizer (Target: ≥0.85)")
print("-" * 80)

# Comprehensive business context
business_context = """
AI-Powered Advisory Platform for Independent Financial Advisors

Target Customer: Independent RIAs (Registered Investment Advisors)
- AUM: $10M-$100M
- Age: 40-55 years old
- Client base: 50-200 clients
- Location: Primarily US-based
- Tech adoption: Moderate, forced by market pressure

Core Problem: Financial advisors are caught between robo-advisors commoditizing basic services 
and enterprise firms with superior technology. They need AI tools that enhance rather than 
replace their personal touch, while dramatically improving efficiency.

Our Solution: AI co-pilot that handles portfolio optimization, compliance, and reporting 
while preserving and amplifying the advisor's personal relationship advantage.

Key Differentiator: First AI platform that reinforces advisor identity rather than threatening it.
"""

print("\n📊 BUSINESS CONTEXT:")
print("-" * 40)
print(business_context[:300] + "...")

# Run ALL 6 agents
state = {
    'task': 'Complete market analysis and GTM strategy with all agents',
    'business_context': business_context,
    'master_context': f"Comprehensive analysis for: {business_context}",
    'requested_agents': [
        'psychological', 
        'voice', 
        'interview',           # Psychological interview
        'sales_interview',     # Sales interview
        'competitor', 
        'gtm_blueprint'
    ],
    'client_id': 'test_all_6_agents',
    'shared_insights': {}
}

print("\n🔄 STARTING COMPLETE 6-AGENT ORCHESTRATION...")
print("=" * 80)

try:
    start_time = time.time()
    
    # Run the full graph with all agents
    result = graph.invoke(state)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE ORCHESTRATION FINISHED!")
    print("=" * 80)
    
    # Performance summary for each agent
    print("\n📊 INDIVIDUAL AGENT PERFORMANCE:")
    print("-" * 40)
    
    agent_results = {
        'psychological': {'target': 0.85, 'output_key': 'psychological'},
        'voice': {'target': 0.80, 'output_key': 'voice'},
        'interview': {'target': 0.75, 'output_key': 'interview'},
        'sales_interview': {'target': 0.75, 'output_key': 'sales_interview'},
        'competitor': {'target': 0.80, 'output_key': 'competitor'},
        'gtm_blueprint': {'target': 0.85, 'output_key': 'gtm_blueprint'}
    }
    
    agents_successful = 0
    quality_targets_met = 0
    total_output_length = 0
    
    for agent_name, config in agent_results.items():
        output = result.get('result', {}).get(config['output_key'], '')
        
        if output:
            agents_successful += 1
            output_length = len(output)
            total_output_length += output_length
            
            print(f"\n{agents_successful}. {agent_name.upper().replace('_', ' ')}:")
            print(f"   ✅ Generated: {output_length:,} characters")
            
            # Show preview
            preview = output[:150] + "..." if len(output) > 150 else output
            print(f"   📝 Preview: {preview}")
            
        else:
            print(f"\n❌ {agent_name.upper()}: No output generated")
    
    # Check shared insights
    print("\n🔄 INTER-AGENT COMMUNICATION:")
    print("-" * 40)
    
    shared_insights = result.get('shared_insights', {})
    if shared_insights:
        print(f"✅ Insights shared between {len(shared_insights)} agents:")
        for agent in list(shared_insights.keys())[:6]:
            print(f"   • {agent}")
    else:
        print("⚠️ No shared insights detected")
    
    # Quality summary
    print("\n📈 QUALITY METRICS:")
    print("-" * 40)
    
    final_quality = result.get('quality_score', 0)
    print(f"Final System Quality Score: {final_quality:.2f}")
    
    if final_quality >= 0.85:
        print("✅ Meets enterprise quality standard (≥0.85)")
        quality_targets_met += 1
    elif final_quality >= 0.75:
        print("🟡 Good quality, approaching enterprise standard")
    else:
        print("⚠️ Below quality targets")
    
    # Execution metrics
    print("\n⏱️ PERFORMANCE METRICS:")
    print("-" * 40)
    print(f"Total execution time: {execution_time:.1f} seconds")
    print(f"Average per agent: {execution_time/6:.1f} seconds")
    print(f"Total content generated: {total_output_length:,} characters")
    
    # GTM Blueprint check
    gtm_output = result.get('result', {}).get('gtm_blueprint', '')
    if gtm_output:
        print("\n🎯 GTM BLUEPRINT STATUS:")
        print("-" * 40)
        print(f"✅ Length: {len(gtm_output):,} characters")
        if len(gtm_output) >= 2500:
            print("✅ Meets minimum length requirement (2,500+)")
        else:
            print("⚠️ Below minimum length")
    
    # Save complete results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save GTM Blueprint
    if gtm_output:
        gtm_filename = f"complete_gtm_blueprint_{timestamp}.txt"
        with open(gtm_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPLETE 6-AGENT GTM BLUEPRINT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(gtm_output)
        print(f"💾 GTM Blueprint saved to: {gtm_filename}")
    
    # Save complete analysis
    analysis_filename = f"complete_6_agent_analysis_{timestamp}.json"
    save_data = {
        'test_date': datetime.now().isoformat(),
        'execution_time': execution_time,
        'agents_run': 6,
        'agents_successful': agents_successful,
        'total_output_length': total_output_length,
        'final_quality_score': final_quality,
        'business_context': business_context,
        'agent_outputs': {
            agent: {
                'generated': bool(result.get('result', {}).get(config['output_key'])),
                'length': len(result.get('result', {}).get(config['output_key'], ''))
            }
            for agent, config in agent_results.items()
        }
    }
    
    with open(analysis_filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, indent=2)
    print(f"💾 Complete analysis saved to: {analysis_filename}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("🏆 FINAL SYSTEM REPORT")
    print("=" * 80)
    
    success_rate = (agents_successful / 6) * 100
    print(f"✅ Agent Success Rate: {agents_successful}/6 ({success_rate:.0f}%)")
    print(f"📝 Total Content Generated: {total_output_length:,} characters")
    print(f"⏱️ Total Time: {execution_time:.1f} seconds")
    print(f"📊 System Quality Score: {final_quality:.2f}")
    
    if agents_successful == 6:
        print("\n🎉 PERFECT RUN! All 6 agents executed successfully!")
        print("🚀 Your AI orchestration system is fully operational!")
    elif agents_successful >= 5:
        print("\n✅ STRONG RUN! Most agents working well.")
    else:
        print(f"\n⚠️ Some agents need attention ({6-agents_successful} failed)")
    
except Exception as e:
    print(f"\n❌ Error during test: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🔬 COMPLETE 6-AGENT INTEGRATION TEST FINISHED")
print("=" * 80)