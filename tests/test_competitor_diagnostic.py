# test_competitor_diagnostic.py
"""Diagnostic test for the broken competitor agent"""

import sys
import traceback
from typing import Dict, Any

print("=" * 60)
print("COMPETITOR AGENT DIAGNOSTIC TEST")
print("=" * 60)

# Step 1: Test imports with CORRECT paths
print("\n1. Testing imports...")
try:
    from team_icp.agents.competitor import CompetitorAgent
    print("✅ CompetitorAgent import successful")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from core.standard_agent import StandardAgentNode
    print("✅ StandardAgentNode import successful")
except ImportError as e:
    print(f"❌ StandardAgentNode Import Error: {e}")

# Correct import path for prompts
try:
    from team_icp.prompts.competitor_prompts import CompetitorPrompts
    print("✅ CompetitorPrompts import successful")
except ImportError as e:
    print(f"❌ CompetitorPrompts Import Error: {e}")
    traceback.print_exc()

# Step 2: Test agent initialization
print("\n2. Testing agent initialization...")
try:
    competitor_agent = CompetitorAgent()
    print("✅ CompetitorAgent initialized successfully")
    print(f"   Agent type: {type(competitor_agent)}")
    print(f"   Agent name: {getattr(competitor_agent, 'agent_name', 'No name attribute')}")
except Exception as e:
    print(f"❌ Initialization Error: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test with minimal state
print("\n3. Testing with minimal state...")
minimal_state = {
    'messages': [],
    'client_id': 'test_diagnostic',
    'task': 'Analyze competitors in AI financial advisory space',
    'business_context': 'AI-powered financial advisory platform'
}

try:
    result = competitor_agent(minimal_state)  # Using __call__ method
    print("✅ __call__ method executed")
    print(f"   Result type: {type(result)}")
    if result and isinstance(result, dict):
        print(f"   Result keys: {list(result.keys())}")
        if 'current_output' in result:
            print(f"   Output length: {len(str(result['current_output']))} chars")
except AttributeError as e:
    print(f"❌ AttributeError: {e}")
    print("   Likely missing method or attribute")
    traceback.print_exc()
except Exception as e:
    print(f"❌ Process Error: {type(e).__name__}: {e}")
    traceback.print_exc()

# Step 4: Test with full state including tool_executor
print("\n4. Testing with full state (including tools)...")
full_state = {
    'messages': [],
    'client_id': 'test_full',
    'task': 'Comprehensive competitor analysis for B2B SaaS',
    'business_context': 'B2B SaaS financial advisory AI platform targeting RIAs',
    'master_context': 'Full market analysis including direct and indirect competitors',
    'requested_agents': ['competitor'],
    'memory_service': None,
    'tool_executor': None  # Will be None in test, but checking handling
}

try:
    result = competitor_agent(full_state)
    print("✅ Full state process successful")
    if result and isinstance(result, dict):
        if 'current_output' in result:
            print(f"✅ current_output found: {len(str(result['current_output']))} chars")
        if 'quality_score' in result:
            print(f"   Quality score: {result['quality_score']}")
        if 'agent_name' in result:
            print(f"   Agent name in result: {result['agent_name']}")
except Exception as e:
    print(f"❌ Full State Error: {type(e).__name__}: {e}")
    traceback.print_exc()

# Step 5: Check for required methods and attributes
print("\n5. Checking required methods and attributes...")
required_items = [
    ('__call__', 'method'),
    ('agent_name', 'attribute'),
    ('role_prompt', 'attribute'),
    ('target_quality', 'attribute'),
    ('_perform_competitor_research', 'method'),
    ('_ensure_valid_state_return', 'method'),
    ('_generate_response', 'method'),
    ('_reflect', 'method')
]

for item_name, item_type in required_items:
    if hasattr(competitor_agent, item_name):
        print(f"✅ Has {item_type}: {item_name}")
    else:
        print(f"❌ Missing {item_type}: {item_name}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)