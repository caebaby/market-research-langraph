# test_gtm_fixed.py - Updated version

#!/usr/bin/env python3
"""
Quick test to verify GTM Blueprint Agent is fixed
"""

import sys
import os

# Print current directory structure to debug
print("Current directory:", os.getcwd())
print("\nDirectory contents:")
for root, dirs, files in os.walk(".", maxdepth=1):
    level = root.replace(".", "", 1).count(os.sep)
    indent = " " * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = " " * 2 * (level + 1)
    for file in files[:10]:  # Show first 10 files
        if file.endswith('.py'):
            print(f"{subindent}{file}")

# Try different import paths
import_attempts = [
    ("from gtm_blueprint import GTMBlueprintAgent", "gtm_blueprint"),
    ("from team_icp.agents.gtm_blueprint import GTMBlueprintAgent", "team_icp.agents.gtm_blueprint"),
    ("from agents.gtm_blueprint import GTMBlueprintAgent", "agents.gtm_blueprint"),
]

successful_import = False
for import_statement, module_path in import_attempts:
    try:
        print(f"\nTrying: {import_statement}")
        exec(import_statement)
        print(f"✅ SUCCESS with: {import_statement}")
        successful_import = True
        break
    except ImportError as e:
        print(f"❌ Failed: {e}")

if not successful_import:
    print("\n❌ Could not import GTMBlueprintAgent")
    print("\nPlease check:")
    print("1. Is gtm_blueprint.py in the correct folder?")
    print("2. What's your directory structure?")
    sys.exit(1)

# Continue with testing if import worked...
print("\n" + "="*70)
print("GTM BLUEPRINT AGENT FIX VERIFICATION")
print("="*70)

# Rest of the test...