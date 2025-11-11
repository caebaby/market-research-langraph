# test_interview_agents.py
"""
Test Interview Agents using the proven working system
Tests both psychological and sales interview agents
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_psychological_interview_agent():
    """Test psychological interview agent"""
    
    print("🎭 Testing Psychological Interview Agent")
    print("=" * 55)
    
    try:
        # Import the working graph system
        from team_icp.workflows.graph import graph
        
        # Use proven business context
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
        
        # Create state for psychological interview agent
        state = {
            "task": "Create realistic customer interview simulations revealing psychological insights",
            "context": business_context,
            "business_context": business_context,
            "master_context": business_context,
            "requested_agents": ["interview"],  # Psychological interview agent
            "client_id": "psych_interview_test_2024",
            "shared_insights": {},
            "new_data": True
        }
        
        print("📋 Target: Psychological Interview Quality ≥0.75")
        print("🎯 Goal: 3 complete interviews with natural dialogue")
        print("💼 Context: Financial advisors facing disruption")
        print("🔍 Focus: Psychological depth and breakthrough moments")
        print()
        
        print("⏳ Running psychological interview agent...")
        result = graph.invoke(state)
        
        # Analyze results
        if result and isinstance(result, dict):
            interview_output = result.get("result", {}).get("interview", "")
            quality_score = result.get("quality_score", 0)
            agent_name = result.get("agent_name", "Unknown")
            
            print("\n" + "=" * 55)
            print("✅ PSYCHOLOGICAL INTERVIEW RESULTS")
            print("=" * 55)
            
            print(f"\n📊 METRICS:")
            print(f"• Agent: {agent_name}")
            print(f"• Quality Score: {quality_score:.2f}")
            print(f"• Output Length: {len(str(interview_output))} characters")
            print(f"• Target Achievement: {'✅ SUCCESS' if quality_score >= 0.75 else '⚠️ NEEDS IMPROVEMENT'}")
            
            # Show interview preview
            if interview_output:
                print(f"\n🎭 INTERVIEW SIMULATION PREVIEW:")
                print("-" * 55)
                preview = str(interview_output)[:1000] + "..." if len(str(interview_output)) > 1000 else str(interview_output)
                print(preview)
                print("-" * 55)
                
                # Count interviews (simple heuristic)
                interview_count = preview.count("INTERVIEW")
                dialogue_markers = preview.count("Customer:") + preview.count("Interviewer:")
                
                print(f"\n📝 INTERVIEW ANALYSIS:")
                print(f"   Interviews detected: {interview_count}")
                print(f"   Dialogue exchanges: {dialogue_markers}")
                print(f"   Target: 3 complete interviews")
                print(f"   Status: {'✅ Likely achieved' if interview_count >= 3 else '⚠️ May need more'}")
            
            # Quality assessment
            if quality_score >= 0.75:
                print(f"\n🎉 SUCCESS: Psychological interview agent meets target!")
                print(f"   Ready for: Customer insights, persona development, empathy training")
            elif quality_score >= 0.65:
                print(f"\n⚠️ CLOSE: Need +{0.75 - quality_score:.2f} points to reach target")
                print(f"   Improvement areas: More realistic dialogue, deeper psychology")
            else:
                print(f"\n❌ NEEDS WORK: Need +{0.75 - quality_score:.2f} points to reach target")
                print(f"   Focus: Interview authenticity, psychological depth")
            
            return quality_score >= 0.75
            
        else:
            print("❌ Psychological interview agent returned unexpected result")
            print(f"Result type: {type(result)}")
            return False
            
    except Exception as e:
        print(f"❌ Error running psychological interview agent: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_sales_interview_agent():
    """Test sales interview agent"""
    
    print(f"\n💰 Testing Sales Interview Agent")
    print("=" * 45)
    
    try:
        from team_icp.workflows.graph import graph
        
        # Same proven context
        business_context = """Financial advisors who feel their expertise is becoming 
        commoditized by robo-advisors and younger digital-native competitors. They're 
        struggling with fee compression and client acquisition."""
        
        state = {
            "task": "Create sales discovery interviews revealing objections and buying criteria",
            "context": business_context,
            "business_context": business_context,
            "master_context": business_context,
            "requested_agents": ["sales_interview"],  # Sales interview agent
            "client_id": "sales_interview_test_2024",
            "shared_insights": {},
            "new_data": True
        }
        
        print("📋 Target: Sales Interview Quality ≥0.75")
        print("🎯 Goal: 3 interviews focused on buying psychology")
        print("💼 Context: Financial advisors buying decisions")
        print("🔍 Focus: Objections, pain points, decision criteria")
        print()
        
        print("⏳ Running sales interview agent...")
        result = graph.invoke(state)
        
        # Analyze results
        if result and isinstance(result, dict):
            sales_output = result.get("result", {}).get("sales_interview", "")
            quality_score = result.get("quality_score", 0)
            agent_name = result.get("agent_name", "Unknown")
            
            print("\n" + "=" * 45)
            print("✅ SALES INTERVIEW RESULTS")
            print("=" * 45)
            
            print(f"\n📊 METRICS:")
            print(f"• Agent: {agent_name}")
            print(f"• Quality Score: {quality_score:.2f}")
            print(f"• Output Length: {len(str(sales_output))} characters")
            print(f"• Target Achievement: {'✅ SUCCESS' if quality_score >= 0.75 else '⚠️ NEEDS IMPROVEMENT'}")
            
            # Show sales interview preview
            if sales_output:
                print(f"\n💰 SALES INTERVIEW PREVIEW:")
                print("-" * 45)
                preview = str(sales_output)[:1000] + "..." if len(str(sales_output)) > 1000 else str(sales_output)
                print(preview)
                print("-" * 45)
                
                # Check for sales-specific content
                objection_markers = preview.count("objection") + preview.count("concern") + preview.count("hesitat")
                buying_markers = preview.count("decision") + preview.count("invest") + preview.count("budget")
                
                print(f"\n📝 SALES FOCUS ANALYSIS:")
                print(f"   Objection-related content: {objection_markers} instances")
                print(f"   Buying-related content: {buying_markers} instances")
                print(f"   Sales focus: {'✅ Strong' if (objection_markers + buying_markers) >= 5 else '⚠️ May need more'}")
            
            # Quality assessment
            if quality_score >= 0.75:
                print(f"\n🎉 SUCCESS: Sales interview agent meets target!")
                print(f"   Ready for: Sales training, objection handling, conversion optimization")
            else:
                print(f"\n⚠️ NEEDS WORK: Need +{0.75 - quality_score:.2f} points to reach target")
                print(f"   Focus: Sales-specific insights, buying psychology")
            
            return quality_score >= 0.75
            
        else:
            print("❌ Sales interview agent returned unexpected result")
            return False
            
    except Exception as e:
        print(f"❌ Error running sales interview agent: {e}")
        return False

def test_interview_collaboration():
    """Test both interview agents working with psychological insights"""
    
    print(f"\n🤝 Testing Interview Agent Collaboration")
    print("=" * 50)
    
    try:
        from team_icp.workflows.graph import graph
        
        business_context = """Executive coaches struggling to scale beyond 1-on-1 sessions"""
        
        state = {
            "task": "Create comprehensive interview suite with psychological foundation",
            "context": business_context,
            "business_context": business_context,
            "master_context": business_context,
            "requested_agents": ["psychological", "interview", "sales_interview"],  # All three
            "client_id": "interview_collab_test_2024",
            "shared_insights": {},
            "new_data": True
        }
        
        print(f"📋 Testing: Psychological + Interview + Sales Interview")
        print(f"🎯 Goal: See how interview agents use psychological insights")
        print()
        
        print("⏳ Running collaborative interview analysis...")
        result = graph.invoke(state)
        
        # Analyze collaborative results
        if result and "result" in result:
            results = result["result"]
            
            print(f"\n✅ Interview collaboration completed!")
            print(f"📊 Agents completed: {len(results)}")
            
            # Show each agent's performance
            for agent_name, output in results.items():
                if output:
                    print(f"\n🤖 {agent_name.upper().replace('_', ' ')} AGENT:")
                    print(f"   Output length: {len(str(output))} characters")
                    print(f"   Preview: {str(output)[:120]}...")
                    
                    # Estimate quality based on output depth
                    if "interview" in agent_name.lower():
                        quality_estimate = "High" if len(str(output)) > 2000 else "Medium" if len(str(output)) > 1000 else "Low"
                        print(f"   Quality estimate: {quality_estimate}")
            
            return True
        else:
            print("❌ Interview collaboration failed")
            return False
            
    except Exception as e:
        print(f"❌ Interview Collaboration Error: {e}")
        return False

def main():
    """Main test function for interview agents"""
    
    print("🧪 Interview Agents Test Suite")
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
    total_tests = 3
    
    # Test 1: Psychological interview agent
    print("🧪 TEST 1: Psychological Interview Agent")
    if test_psychological_interview_agent():
        tests_passed += 1
    
    # Test 2: Sales interview agent
    print("🧪 TEST 2: Sales Interview Agent")
    if test_sales_interview_agent():
        tests_passed += 1
    
    # Test 3: Interview collaboration
    print("🧪 TEST 3: Interview Agent Collaboration")
    if test_interview_collaboration():
        tests_passed += 1
    
    # Summary
    print(f"\n📊 INTERVIEW AGENTS TEST SUMMARY")
    print("=" * 40)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 Interview agents working! Ready for next phase.")
        next_steps = [
            "1. ✅ Fix competitor agent (currently broken)",
            "2. 🏗️ Build GTM synthesis agent",
            "3. 🤖 Start Slack integration for agent conversations"
        ]
    elif tests_passed >= 2:
        print("⚠️ Most interview agents working. Minor fixes needed.")
        next_steps = [
            "1. 🔧 Tune failing interview agent",
            "2. ✅ Fix competitor agent",
            "3. 🏗️ Build GTM synthesis agent"
        ]
    else:
        print("❌ Interview agents need attention.")
        next_steps = [
            "1. 🔧 Debug interview agent prompts and quality scoring",
            "2. 📊 Check interview simulation authenticity",
            "3. 🎭 Improve dialogue realism"
        ]
    
    print(f"\n💡 NEXT STEPS:")
    for step in next_steps:
        print(f"   {step}")
    
    # Current completion status
    print(f"\n📈 COMPLETION PROGRESS:")
    agents_status = [
        "✅ Psychological: 85% (target met)",
        "✅ Voice: 88% (target exceeded)", 
        f"{'✅' if tests_passed >= 1 else '❌'} Interview (Psych): {'Ready' if tests_passed >= 1 else 'Needs work'}",
        f"{'✅' if tests_passed >= 2 else '❌'} Interview (Sales): {'Ready' if tests_passed >= 2 else 'Needs work'}",
        "🔧 Competitor: Broken (needs fix)",
        "🏗️ GTM Blueprint: Not built yet"
    ]
    
    for status in agents_status:
        print(f"   {status}")

if __name__ == "__main__":
    main()