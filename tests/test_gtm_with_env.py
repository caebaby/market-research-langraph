"""
Test GTM Blueprint Agent with proper environment loading
"""

import sys
import os
from pathlib import Path

# IMPORTANT: Load .env file BEFORE importing anything else
from dotenv import load_dotenv

# Load from parent directory's .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Verify the key loaded
print(f"API Key loaded: {'Yes' if os.getenv('ANTHROPIC_API_KEY') else 'No'}")
print(f"First 10 chars: {os.getenv('ANTHROPIC_API_KEY', 'NOT FOUND')[:10]}...")

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
from langchain_anthropic import ChatAnthropic

def test_gtm_blueprint():
    """Test the GTM Blueprint agent"""
    
    print("\n" + "="*60)
    print("🚀 TESTING GTM BLUEPRINT AGENT")
    print("="*60)
    
    # Initialize the agent
    agent = GTMBlueprintAgent()
    
    # Initialize LLM - it should pick up ANTHROPIC_API_KEY from environment
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",  # Using the model from your .env
        temperature=0.7,
        max_tokens=4000
        # Don't specify api_key - let it pick from environment
    )
    
    # Test task
    task = """Create a comprehensive GTM strategy for a B2B SaaS product:
    PRODUCT: AI-powered customer success platform
    TARGET: VP of Customer Success at Series B-D SaaS companies"""
    
    # Minimal shared insights
    shared_insights = {
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
    
    print("\n📝 Generating GTM Blueprint...")
    print(f"Using model: claude-3-5-sonnet-20241022")
    
    try:
        # Process the task
        result = agent.process(
            task=task,
            shared_insights=shared_insights,
            llm=llm
        )
        
        # Get output
        if isinstance(result, dict):
            output = result.get('output', '')
        else:
            output = str(result)
        
        # Calculate metrics
        word_count = len(output.split())
        
        print(f"\n✅ Generated {word_count} words")
        
        if word_count >= 2500:
            print("✅ SUCCESS: Met word count requirement!")
        else:
            print(f"⚠️  Need {2500-word_count} more words")
        
        # Show preview
        print("\n📄 Preview:")
        print("-"*40)
        print(output[:500] + "...")
        
        # Save output
        os.makedirs("test_outputs", exist_ok=True)
        with open("test_outputs/gtm_blueprint.md", 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\n💾 Saved to: test_outputs/gtm_blueprint.md")
        
        return word_count >= 2500
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gtm_blueprint()
    sys.exit(0 if success else 1)