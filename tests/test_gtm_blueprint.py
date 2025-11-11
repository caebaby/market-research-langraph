# test_gtm_blueprint.py
"""Test the new GTM Blueprint agent"""

from team_icp.workflows.graph import graph
import json
from datetime import datetime

print("=" * 80)
print("🚀 GTM BLUEPRINT AGENT TEST")
print("=" * 80)

# Test with all agents feeding into GTM
state = {
    'task': 'Create comprehensive GTM strategy',
    'business_context': """
    B2B SaaS platform helping independent financial advisors adopt AI tools.
    Target: RIAs managing $10M-$100M, age 40-55, feeling threatened by robo-advisors.
    Product: AI-powered portfolio management that enhances (not replaces) human advisors.
    """,
    'master_context': 'Create go-to-market strategy for AI platform targeting financial advisors',
    'requested_agents': ['psychological', 'voice', 'competitor', 'gtm_blueprint'],
    'client_id': 'test_gtm_blueprint'
}

print("🔄 Running GTM Blueprint synthesis with supporting agents...")
print("-" * 80)

try:
    import time
    start_time = time.time()
    
    result = graph.invoke(state)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n✅ GTM BLUEPRINT GENERATED!")
    print("=" * 80)
    
    # Check GTM output
    gtm_output = result.get('result', {}).get('gtm_blueprint', '')
    
    if gtm_output:
        print(f"📊 GTM Blueprint Length: {len(gtm_output)} characters")
        print(f"📊 Quality Score: {result.get('quality_score', 'N/A')}")
        print(f"⏱️ Execution Time: {execution_time:.1f} seconds")
        
        # Show preview
        print("\n📄 GTM BLUEPRINT PREVIEW:")
        print("-" * 40)
        print(gtm_output[:1500] + "...")
        
        # Check if it meets length requirement
        if len(gtm_output) >= 2500:
            print(f"\n✅ Length requirement met ({len(gtm_output)}/2500 chars)")
        else:
            print(f"\n⚠️ Below length requirement ({len(gtm_output)}/2500)")
        
        # Check quality
        if result.get('quality_score', 0) >= 0.85:
            print("✅ Quality target met (≥0.85)")
        else:
            print(f"⚠️ Below quality target ({result.get('quality_score', 0)}/0.85)")
        
        # Save the output
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"gtm_blueprint_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(gtm_output)
        print(f"\n💾 Full GTM Blueprint saved to: {filename}")
            
    else:
        print("❌ No GTM Blueprint generated")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🏁 TEST COMPLETE")
print("=" * 80)

# Final status
if 'gtm_output' in locals() and gtm_output:
    print("\n🎊 SUCCESS! Your 6-agent system is now complete!")
    print("All agents working together to create comprehensive GTM strategies.")
else:
    print("\n⚠️ Check the error above for troubleshooting.")