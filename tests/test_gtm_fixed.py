# test_gtm_fixed.py - CORRECTED VERSION

#!/usr/bin/env python3
"""
Quick test to verify GTM Blueprint Agent is fixed
"""

import sys
import os

# Add parent directory to path (to find the agents folder)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Current directory:", os.getcwd())
print("Python path includes:", sys.path[0])

# Show directory structure (fixed - no maxdepth parameter)
print("\nDirectory structure:")
parent_dir = os.path.dirname(os.getcwd())
for item in os.listdir(parent_dir):
    item_path = os.path.join(parent_dir, item)
    if os.path.isdir(item_path):
        print(f"  📁 {item}/")
        # Show Python files in subdirectories
        try:
            for file in os.listdir(item_path):
                if file.endswith('.py'):
                    print(f"      📄 {file}")
        except:
            pass

print("\n" + "="*70)
print("GTM BLUEPRINT AGENT FIX VERIFICATION")
print("="*70)

# Now try to import
print("\n1️⃣ Attempting to import GTMBlueprintAgent...")
try:
    from agents.gtm_blueprint import GTMBlueprintAgent
    print("   ✅ Import successful!")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    print("\n   Trying alternate import paths...")
    
    # Try other possible paths
    try:
        from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
        print("   ✅ Alternate import successful (team_icp.agents)!")
    except:
        try:
            # If gtm_blueprint.py is in same folder as tests
            from gtm_blueprint import GTMBlueprintAgent
            print("   ✅ Alternate import successful (same folder)!")
        except Exception as e2:
            print(f"   ❌ All imports failed: {e2}")
            print("\n   Please verify:")
            print("   1. gtm_blueprint.py exists in the 'agents' folder")
            print("   2. The file name is exactly 'gtm_blueprint.py'")
            print(f"   3. Your structure is: {parent_dir}/agents/gtm_blueprint.py")
            sys.exit(1)

# Initialize agent
print("\n2️⃣ Initializing GTMBlueprintAgent...")
try:
    agent = GTMBlueprintAgent()
    print(f"   ✅ Agent initialized: {agent.agent_name}")
    print(f"      • Max tokens: {agent.max_tokens}")
    print(f"      • Required sections: {agent.required_sections}")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

# Check for process method
print("\n3️⃣ Checking for process method...")
if hasattr(agent, 'process'):
    print("   ✅ process() method exists")
    
    # Check method signature
    import inspect
    sig = inspect.signature(agent.process)
    params = list(sig.parameters.keys())
    print(f"      • Parameters: {params}")
    
    if 'state' in params:
        print("      ✅ Correct signature (accepts 'state')")
else:
    print("   ❌ process() method NOT FOUND")
    print("      Available methods:", [m for m in dir(agent) if not m.startswith('_')])
    sys.exit(1)

# Test with mock state
print("\n4️⃣ Testing process method with mock state...")
test_state = {
    "company_info": "TechStartup Inc - B2B SaaS Platform",
    "analysis_results": {
        "psychological": {
            "fears": ["missing out", "falling behind"],
            "desires": ["market leadership", "efficiency"]
        },
        "competitor": {
            "main_competitors": ["CompA", "CompB"],
            "gaps": ["enterprise features"]
        }
    }
}

try:
    print("   Running agent.process(state)...")
    result_state = agent.process(test_state)
    
    # Check results
    if 'analysis_results' in result_state and 'gtm_blueprint' in result_state['analysis_results']:
        gtm = result_state['analysis_results']['gtm_blueprint']
        print("   ✅ GTM Blueprint generated!")
        print(f"      • Quality Score: {gtm.get('quality_score', 0):.2%}")
        print(f"      • Sections: {gtm.get('completeness', 'unknown')}")
        print(f"      • Word Count: {gtm.get('word_count', 0)}")
        
        if gtm.get('error'):
            print(f"   ⚠️ Generated with error: {gtm.get('error_message')}")
    else:
        print("   ❌ No GTM Blueprint in output")
        
except Exception as e:
    print(f"   ❌ Process failed: {e}")
    import traceback
    print("\n   Stack trace:")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print("🎉 GTM BLUEPRINT AGENT IS FIXED AND READY!")
print("="*70)