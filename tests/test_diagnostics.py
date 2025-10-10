# tests/test_diagnostics.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try importing each agent directly
agents_to_test = [
    ("team_icp.agents.psychological", "PsychologicalAnalysisAgent"),
    ("team_icp.agents.voice_of_customer", "VoiceAgent"),
    ("team_icp.agents.competitor", "CompetitorAgent"),
    ("team_icp.agents.interview_psychological", "InterviewPsychologicalAgent"),
    ("team_icp.agents.interview_sales", "InterviewSalesAgent"),
    ("team_icp.agents.gtm_blueprint", "GTMBlueprintAgent"),
]

print("Checking agent imports...")
for module_path, class_name in agents_to_test:
    try:
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        print(f"✅ {module_path}.{class_name}")
    except ImportError as e:
        print(f"❌ Module error: {module_path} - {e}")
    except AttributeError as e:
        print(f"❌ Class error: {class_name} not in {module_path}")