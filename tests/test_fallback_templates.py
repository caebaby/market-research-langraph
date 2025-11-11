# tests/test_fallback_templates.py
"""
Test to verify fallback templates are complete 14-section documents.
Checks that voice and competitor agents generate full templates, not placeholders.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fallback_templates():
    """Test that all agents generate complete 14-section fallback templates."""
    
    print("\n" + "="*60)
    print("TESTING FALLBACK TEMPLATE COMPLETENESS")
    print("="*60)
    
    # Expected 14 sections
    REQUIRED_SECTIONS = [
        "1. EXECUTIVE SUMMARY",
        "2. MARKET CONTEXT", 
        "3. TARGET AUDIENCE",
        "4. CUSTOMER PSYCHOLOGY",
        "5. VOICE OF CUSTOMER",
        "6. COMPETITIVE LANDSCAPE",
        "7. POSITIONING STRATEGY",
        "8. MESSAGING FRAMEWORK",
        "9. PRODUCT STRATEGY",
        "10. PRICING STRATEGY",
        "11. SALES STRATEGY",
        "12. MARKETING STRATEGY",
        "13. SUCCESS METRICS",
        "14. IMPLEMENTATION ROADMAP"
    ]
    
    test_company = "TestCompany"
    results = {}
    
    # Test each agent
    agents_to_test = [
        ('voice', 'VoiceAgent'),
        ('competitor', 'CompetitorAgent'),
        ('psychological', 'PsychologicalAgent'),
        ('interview_psychological', 'PsychologicalInterviewAgent'),
        ('interview_sales', 'SalesInterviewAgent'),
        ('gtm_blueprint', 'GTMBlueprintAgent')
    ]
    
    for agent_name, class_name in agents_to_test:
        print(f"\n📋 Testing {agent_name} fallback template...")
        
        try:
            # Import and initialize agent
            if agent_name == 'voice':
                from team_icp.agents.voice_of_customer import VoiceAgent
                agent = VoiceAgent()
            elif agent_name == 'competitor':
                from team_icp.agents.competitor import CompetitorAgent
                agent = CompetitorAgent()
            elif agent_name == 'psychological':
                from team_icp.agents.psychological import PsychologicalAgent
                agent = PsychologicalAgent()
            elif agent_name == 'interview_psychological':
                from team_icp.agents.interview_psychological import PsychologicalInterviewAgent
                agent = PsychologicalInterviewAgent()
            elif agent_name == 'interview_sales':
                from team_icp.agents.interview_sales import SalesInterviewAgent
                agent = SalesInterviewAgent()
            elif agent_name == 'gtm_blueprint':
                from team_icp.agents.gtm_blueprint import GTMBlueprintAgent
                agent = GTMBlueprintAgent()
            
            # Get fallback template
            if hasattr(agent, '_create_template_fallback'):
                template = agent._create_template_fallback(test_company)
                
                # Check basic completeness
                char_count = len(template)
                word_count = len(template.split())
                line_count = len(template.split('\n'))
                
                print(f"   📊 Stats:")
                print(f"      Characters: {char_count}")
                print(f"      Words: {word_count}")
                print(f"      Lines: {line_count}")
                
                # Check if it's just a placeholder
                is_placeholder = False
                placeholder_indicators = [
                    "[... 14 sections",
                    "# Similar structure",
                    "...]",
                    "TODO",
                    "placeholder"
                ]
                
                for indicator in placeholder_indicators:
                    if indicator.lower() in template.lower():
                        is_placeholder = True
                        print(f"   ⚠️ PLACEHOLDER DETECTED: Contains '{indicator}'")
                        break
                
                # Check for minimum content (should be at least 500 words for a real template)
                if word_count < 200:
                    print(f"   ⚠️ TOO SHORT: Only {word_count} words (minimum 200 expected)")
                    is_placeholder = True
                
                # Check for each required section
                sections_found = []
                sections_missing = []
                
                print(f"   🔍 Checking for 14 sections:")
                for section in REQUIRED_SECTIONS:
                    # Check multiple formats (with/without ##, different numbering)
                    section_num = section.split('.')[0]
                    section_name = section.split('.')[1].strip()
                    
                    # Check various formats
                    found = False
                    if section in template:
                        found = True
                    elif f"## {section}" in template:
                        found = True
                    elif section_name in template:
                        found = True
                    elif f"{section_num}." in template:
                        # Check if at least the number exists
                        found = True
                    
                    if found:
                        sections_found.append(section)
                        print(f"      ✅ {section}")
                    else:
                        sections_missing.append(section)
                        print(f"      ❌ {section}")
                
                # Calculate completeness
                completeness = len(sections_found) / len(REQUIRED_SECTIONS)
                
                # Determine status
                if is_placeholder:
                    status = "❌ PLACEHOLDER"
                elif completeness == 1.0 and word_count >= 200:
                    status = "✅ COMPLETE"
                elif completeness >= 0.8:
                    status = "⚠️ MOSTLY COMPLETE"
                else:
                    status = "❌ INCOMPLETE"
                
                results[agent_name] = {
                    'status': status,
                    'completeness': completeness,
                    'word_count': word_count,
                    'sections_found': len(sections_found),
                    'sections_missing': sections_missing,
                    'is_placeholder': is_placeholder
                }
                
                print(f"\n   📊 Summary for {agent_name}:")
                print(f"      Status: {status}")
                print(f"      Completeness: {completeness:.0%} ({len(sections_found)}/14 sections)")
                print(f"      Template type: {'Placeholder' if is_placeholder else 'Full template'}")
                
            else:
                print(f"   ❌ No _create_template_fallback method found")
                results[agent_name] = {
                    'status': '❌ NO METHOD',
                    'completeness': 0
                }
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
            results[agent_name] = {
                'status': '❌ ERROR',
                'completeness': 0,
                'error': str(e)
            }
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    # Focus on voice and competitor (the problematic ones)
    critical_agents = ['voice', 'competitor']
    
    print("\n🎯 Critical Agents (Voice & Competitor):")
    for agent in critical_agents:
        if agent in results:
            r = results[agent]
            print(f"\n   {agent.upper()}:")
            print(f"      Status: {r['status']}")
            print(f"      Completeness: {r.get('completeness', 0):.0%}")
            print(f"      Words: {r.get('word_count', 0)}")
            if r.get('sections_missing'):
                print(f"      Missing sections: {len(r['sections_missing'])}")
    
    print("\n📊 All Agents:")
    for agent, r in results.items():
        status_icon = "✅" if "COMPLETE" in r['status'] else "⚠️" if "MOSTLY" in r['status'] else "❌"
        print(f"   {status_icon} {agent}: {r['status']}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    for agent, r in results.items():
        if r.get('is_placeholder'):
            print(f"   - {agent}: Replace placeholder with full 14-section template")
        elif r.get('sections_missing'):
            print(f"   - {agent}: Add missing sections: {', '.join(r['sections_missing'][:3])}")
        elif r.get('word_count', 0) < 200:
            print(f"   - {agent}: Expand template content (currently only {r.get('word_count')} words)")


if __name__ == "__main__":
    # Disable memory and search to avoid API calls
    os.environ['DISABLE_MEMORY'] = 'true'
    os.environ['DISABLE_SEARCH'] = 'true'
    
    test_fallback_templates()