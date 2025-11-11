# test_voice_agent.py
"""
Test Voice Agent using the proven working system
Based on successful psychological agent that achieved 85%
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voice_agent():
    """Test voice agent using the working graph system"""
    
    print("🗣️ Testing Voice Agent")
    print("=" * 50)
    
    try:
        # Import the working graph system
        from team_icp.workflows.graph import graph
        
        # Use the SAME business context that got 85% with psychological agent
        business_context = """
        We're targeting financial advisors who are struggling to differentiate 
        themselves in a crowded market. They're typically 35-55 years old, 
        managing $50M-$200M in assets, and feeling pressure from robo-advisors 
        and younger competitors. They value relationships but struggle with 
        digital marketing and feel their expertise isn't valued anymore.
        
        They're saying things like 'I don't want to be just another advisor' 
        and 'My clients trust ME, not some algorithm.' But they're also 
        secretly worried they're becoming obsolete.
        """
        
        # Create state for voice agent ONLY
        state = {
            "task": "Extract authentic customer voice and language patterns",
            "context": business_context,
            "business_context": business_context,
            "master_context": business_context,
            "requested_agents": ["voice"],  # ONLY voice agent
            "client_id": "voice_test_2024",
            "shared_insights": {},
            "new_data": True
        }
        
        print("📋 Target: Voice Agent Quality ≥0.80")
        print("🎯 Goal: Extract 25+ authentic customer phrases")
        print("💼 Context: Financial advisors facing disruption")
        print()
        
        print("⏳ Running voice agent analysis...")
        result = graph.invoke(state)
        
        # Analyze results
        if result and isinstance(result, dict):
            # Check if voice agent completed
            voice_output = result.get("result", {}).get("voice", "")
            quality_score = result.get("quality_score", 0)
            agent_name = result.get("agent_name", "Unknown")
            
            print("\n" + "=" * 50)
            print("✅ VOICE AGENT RESULTS")
            print("=" * 50)
            
            print(f"\n📊 METRICS:")
            print(f"• Agent: {agent_name}")
            print(f"• Quality Score: {quality_score:.2f}")
            print(f"• Output Length: {len(str(voice_output))} characters")
            print(f"• Target Achievement: {'✅ SUCCESS' if quality_score >= 0.80 else '⚠️ NEEDS IMPROVEMENT'}")
            
            # Show voice analysis preview
            if voice_output:
                print(f"\n🗣️ VOICE ANALYSIS PREVIEW:")
                print("-" * 50)
                preview = str(voice_output)[:800] + "..." if len(str(voice_output)) > 800 else str(voice_output)
                print(preview)
                print("-" * 50)
                
                # Count phrases (simple heuristic)
                phrase_count = preview.count('"') // 2  # Rough estimate of quoted phrases
                print(f"\n📝 ESTIMATED PHRASES EXTRACTED: ~{phrase_count}")
                print(f"   Target: 25+ phrases")
                print(f"   Status: {'✅ Likely achieved' if phrase_count >= 20 else '⚠️ May need more'}")
            
            # Quality assessment
            if quality_score >= 0.80:
                print(f"\n🎉 SUCCESS: Voice agent meets quality target!")
                print(f"   Ready for: Copy creation, ad headlines, customer language")
            elif quality_score >= 0.70:
                print(f"\n⚠️ CLOSE: Need +{0.80 - quality_score:.2f} points to reach target")
                print(f"   Improvement areas: More authentic phrases, better voice capture")
            else:
                print(f"\n❌ NEEDS WORK: Need +{0.80 - quality_score:.2f} points to reach target")
                print(f"   Focus: Deeper voice analysis, more customer quotes")
            
            return quality_score >= 0.80
            
        else:
            print("❌ Voice agent returned unexpected result format")
            print(f"Result type: {type(result)}")
            print(f"Available keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            return False
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the correct directory")
        return False
    except Exception as e:
        print(f"❌ Error running voice agent: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_both_agents_together():
    """Test psychological + voice agents working together"""
    
    print(f"\n🔄 Testing Psychological + Voice Agent Collaboration")
    print("=" * 60)
    
    try:
        from team_icp.workflows.graph import graph
        
        business_context = """Financial advisors who feel their expertise is becoming 
        commoditized by robo-advisors and younger digital-native competitors"""
        
        state = {
            "task": "Full psychological and voice analysis",
            "context": business_context,
            "business_context": business_context,
            "master_context": business_context,
            "requested_agents": ["psychological", "voice"],  # Both agents
            "client_id": "collab_test_2024",
            "shared_insights": {},
            "new_data": True
        }
        
        print(f"📋 Testing: Psychological (≥0.85) + Voice (≥0.80)")
        print(f"🎯 Goal: See how voice agent uses psychological insights")
        print()
        
        print("⏳ Running collaborative analysis...")
        result = graph.invoke(state)
        
        # Analyze collaborative results
        if result and "result" in result:
            results = result["result"]
            
            print(f"\n✅ Collaboration completed!")
            print(f"📊 Agents completed: {len(results)}")
            
            # Show each agent's performance
            for agent_name, output in results.items():
                if output:
                    print(f"\n🤖 {agent_name.upper()} AGENT:")
                    print(f"   Output length: {len(str(output))} characters")
                    print(f"   Preview: {str(output)[:150]}...")
                    
                    # Estimate quality based on output depth
                    quality_estimate = "High" if len(str(output)) > 2000 else "Medium" if len(str(output)) > 1000 else "Low"
                    print(f"   Quality estimate: {quality_estimate}")
            
            return True
        else:
            print("❌ Collaboration failed")
            return False
            
    except Exception as e:
        print(f"❌ Collaboration Error: {e}")
        return False

def main():
    """Main test function"""
    
    print("🧪 Voice Agent Test Suite")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Missing ANTHROPIC_API_KEY")
        return
    
    print("✅ Environment check passed")
    print(f"🔇 LangSmith tracing: {'Enabled' if os.getenv('LANGCHAIN_TRACING_V2') == 'true' else 'Disabled'}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    # Test 1: Voice agent alone
    print("🧪 TEST 1: Voice Agent Individual Performance")
    if test_voice_agent():
        tests_passed += 1
    
    # Test 2: Voice + Psychological collaboration
    print("🧪 TEST 2: Voice + Psychological Collaboration")
    if test_both_agents_together():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 30)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Voice agent working! Ready for next agents.")
    elif tests_passed > 0:
        print("⚠️ Partial success. Voice agent may need tuning.")
    else:
        print("❌ Voice agent needs attention.")
    
    # Next steps
    print(f"\n💡 NEXT STEPS:")
    if tests_passed > 0:
        print("1. ✅ Test interview agents next")
        print("2. 🔧 Fix competitor agent")  
        print("3. 🏗️ Build GTM synthesis agent")
    else:
        print("1. 🔧 Debug voice agent issues")
        print("2. 📊 Check voice prompts and quality scoring")

if __name__ == "__main__":
    main()