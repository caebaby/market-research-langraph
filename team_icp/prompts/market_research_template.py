# prompts/market_research_template.py
"""
Standard 14-Section Market Research Template
All agents must address these sections in their analysis
"""

MARKET_RESEARCH_SECTIONS = [
    "1. EXECUTIVE SUMMARY",           # Key findings and recommendations
    "2. MARKET CONTEXT",              # Industry, segment, timing
    "3. TARGET AUDIENCE",             # ICP definition and segmentation
    "4. CUSTOMER PSYCHOLOGY",         # Mental models, fears, motivations
    "5. VOICE OF CUSTOMER",           # Exact language and phrases
    "6. COMPETITIVE LANDSCAPE",       # Competitors and positioning
    "7. POSITIONING STRATEGY",        # Unique value and differentiation
    "8. MESSAGING FRAMEWORK",         # Core messages and narratives
    "9. PRODUCT STRATEGY",            # Features, packaging, roadmap
    "10. PRICING STRATEGY",           # Models, tiers, justification
    "11. SALES STRATEGY",             # Methodology, enablement, process
    "12. MARKETING STRATEGY",         # Campaigns, channels, content
    "13. SUCCESS METRICS",            # KPIs, targets, measurement
    "14. IMPLEMENTATION ROADMAP"      # Timeline, phases, quick wins
]

def get_section_prompt(section_number: int, agent_focus: str) -> str:
    """
    Get the prompt for a specific section based on agent focus
    """
    # This will be customized per agent
    pass