# prompts/template_enforcer.py
"""
Template Enforcement Utilities
Ensures all agents follow the 14-section structure
"""

from typing import Dict, List, Any
import re

class TemplateEnforcer:
    """
    WHY: Consistency across all agent outputs
    WHAT: Validates and enforces 14-section template
    HOW: Checks structure and completeness
    """
    
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
    
    @classmethod
    def validate_output(cls, output: str, agent_name: str) -> Dict[str, Any]:
        """
        Validate that output contains all 14 sections
        """
        
        validation_result = {
            "agent": agent_name,
            "is_valid": True,
            "missing_sections": [],
            "section_word_counts": {},
            "total_word_count": len(output.split()),
            "completeness_score": 0.0
        }
        
        # Check each required section
        for section in cls.REQUIRED_SECTIONS:
            # Create regex pattern for section
            pattern = re.escape(section).replace(r"\.", r"\.?")
            
            if not re.search(pattern, output, re.IGNORECASE):
                validation_result["missing_sections"].append(section)
                validation_result["is_valid"] = False
            else:
                # Extract section content and count words
                section_content = cls._extract_section(output, section)
                word_count = len(section_content.split())
                validation_result["section_word_counts"][section] = word_count
        
        # Calculate completeness score
        sections_found = 14 - len(validation_result["missing_sections"])
        validation_result["completeness_score"] = sections_found / 14
        
        return validation_result
    
    @classmethod
    def _extract_section(cls, output: str, section: str) -> str:
        """Extract content of a specific section"""
        
        # Find start of section
        pattern = re.escape(section).replace(r"\.", r"\.?")
        match = re.search(pattern, output, re.IGNORECASE)
        
        if not match:
            return ""
        
        start_pos = match.end()
        
        # Find start of next section
        next_section_idx = cls.REQUIRED_SECTIONS.index(section) + 1
        if next_section_idx < len(cls.REQUIRED_SECTIONS):
            next_section = cls.REQUIRED_SECTIONS[next_section_idx]
            next_pattern = re.escape(next_section).replace(r"\.", r"\.?")
            next_match = re.search(next_pattern, output[start_pos:], re.IGNORECASE)
            
            if next_match:
                end_pos = start_pos + next_match.start()
                return output[start_pos:end_pos]
        
        # Last section - return to end
        return output[start_pos:]
    
    @classmethod
    def enforce_structure(cls, prompt: str) -> str:
        """
        Add structure enforcement to any prompt
        """
        
        enforcement = """
        
MANDATORY STRUCTURE REQUIREMENT:
You MUST organize your response into these EXACT 14 sections:

1. EXECUTIVE SUMMARY
2. MARKET CONTEXT
3. TARGET AUDIENCE
4. CUSTOMER PSYCHOLOGY
5. VOICE OF CUSTOMER
6. COMPETITIVE LANDSCAPE
7. POSITIONING STRATEGY
8. MESSAGING FRAMEWORK
9. PRODUCT STRATEGY
10. PRICING STRATEGY
11. SALES STRATEGY
12. MARKETING STRATEGY
13. SUCCESS METRICS
14. IMPLEMENTATION ROADMAP

Each section MUST:
- Be clearly labeled with the section number and name
- Contain substantive analysis (not just placeholders)
- Connect to other sections coherently
- Provide actionable insights

FAILURE TO INCLUDE ALL 14 SECTIONS WILL REQUIRE REGENERATION.
"""
        
        return prompt + enforcement
    
    @classmethod
    def create_section_guide(cls, agent_focus: str) -> str:
        """
        Create a guide for how each agent should approach sections
        """
        
        guides = {
            "psychological": """
            Focus each section through psychological lens:
            - Unconscious motivations
            - Identity implications  
            - Emotional drivers
            - Resistance patterns
            """,
            
            "voice_of_customer": """
            Extract exact language for each section:
            - Direct quotes
            - Specific phrases
            - Emotional expressions
            - Natural vocabulary
            """,
            
            "competitor": """
            Analyze competition in each section:
            - Competitive positions
            - Differentiation opportunities
            - Market gaps
            - Win strategies
            """,
            
            "interview": """
            Explore each section through dialogue:
            - Progressive discovery
            - Emotional revelation
            - Resistance and breakthrough
            - Authentic conversation
            """,
            
            "gtm_blueprint": """
            Synthesize all insights in each section:
            - Integrate all agents
            - Create actionable strategy
            - Specify next steps
            - Define success metrics
            """
        }
        
        return guides.get(agent_focus, "")
    
    @classmethod
    def validate_sections(cls, analysis: str) -> Dict[str, Any]:
        """
        Validate that all 14 sections are present in the analysis.
        
        WHY: Agents need to check template compliance
        HOW: Check for presence of each section
        WHAT: Return completeness score and missing sections
        
        Returns:
            Dict with 'completeness' percentage and 'missing_sections' list
        """
        sections_found = []
        missing_sections = []
        
        for section in cls.REQUIRED_SECTIONS:
            # Check multiple variations of section headers
            section_patterns = [
                section,  # Exact match
                section.replace(".", ""),  # Without period
                f"## {section}",  # With markdown header
                f"# {section}",  # With h1 header
                section.upper(),  # All caps
                section.lower()  # All lowercase
            ]
            
            # Check if any pattern matches
            section_found = False
            for pattern in section_patterns:
                if pattern in analysis or pattern.replace("##", "#") in analysis:
                    section_found = True
                    break
            
            if section_found:
                sections_found.append(section)
            else:
                missing_sections.append(section)
        
        completeness = len(sections_found) / len(cls.REQUIRED_SECTIONS) if cls.REQUIRED_SECTIONS else 0
        
        return {
            'completeness': completeness,
            'missing_sections': missing_sections,
            'sections_found': sections_found,
            'total_sections': len(cls.REQUIRED_SECTIONS)
        }

    @classmethod  
    def get_enhancement_prompt(cls, 
                              current_analysis: str, 
                              missing_sections: List[str], 
                              company_name: str,
                              focus: str = "general") -> str:
        """
        Generate prompt to add missing sections.
        
        WHY: Help agents complete their analysis
        HOW: Create targeted prompt for missing sections
        """
        sections_list = "\n".join([f"- {section}" for section in missing_sections])
        
        return f"""
        The following sections are missing from the {company_name} analysis:
        {sections_list}
        
        Please add these missing sections with {focus} focus.
        Each section should contain substantive analysis, not placeholders.
        Maintain consistency with the existing analysis.
        
        Current partial analysis (first 1500 chars):
        {current_analysis[:1500]}
        
        Add the missing sections below:
        """

    @classmethod
    def get_base_template(cls, company_name: str) -> str:
        """
        Get base template structure.
        
        WHY: Provide starting template for agents
        HOW: Return empty template with all sections
        """
        template = f"# {company_name} - Analysis\n\n"
        for section in cls.REQUIRED_SECTIONS:
            template += f"## {section}\n\n[Content to be added]\n\n"
        return template