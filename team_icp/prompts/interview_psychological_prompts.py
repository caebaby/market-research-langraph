# prompts/interview_psychological_prompts.py
"""
Psychological Interview Agent Prompts
Aligned with 14-Section Market Research Template
Deep emotional discovery focus
"""

from typing import Dict, Any, List

class InterviewPsychologicalPrompts:
    """
    WHY: Surface unconscious motivations through psychological interviews
    WHAT: 14-section template via deep psychological dialogue
    HOW: Progressive trust building to reveal hidden drivers
    """
    
    def __init__(self):
        self.sections = self._initialize_sections()
    
    def _initialize_sections(self) -> Dict[str, str]:
        """Define psychological interview approach for each section"""
        
        return {
            "1_executive_summary": """
            Interview Setup & Psychological Safety Building:
            - Create safe, confidential environment
            - Build rapport through vulnerability
            - Set expectations for depth
            - Establish non-judgmental tone
            - Preview emotional exploration
            
            Opening: "This conversation is completely confidential..."
            """,
            
            "2_market_context": """
            Market Psychology Exploration:
            Interviewer: "How does the market pressure affect you personally?"
            - Explore anxiety about market changes
            - Uncover fear of being left behind
            - Identity threat from disruption
            - Personal stakes in market dynamics
            
            Probes: "What keeps you awake?" "What scares you most?"
            """,
            
            "3_target_audience": """
            Identity & Self-Perception:
            Interviewer: "How do you see yourself as a leader?"
            - Professional identity exploration
            - Gap between perception and reality
            - Imposter syndrome manifestations
            - Role-based identity conflicts
            
            Probes: "Who are you trying to be?" "What mask do you wear?"
            """,
            
            "4_customer_psychology": """
            DEEP PSYCHOLOGICAL DISCOVERY (PRIMARY FOCUS - 700+ words):
            
            LAYER 1: SURFACE CONCERNS (Ease into depth)
            Interviewer: "What's your biggest challenge right now?"
            Subject: [Initial defensive response]
            Interviewer: "How is that affecting you personally?"
            Subject: [Beginning to open up]
            
            LAYER 2: EMOTIONAL IMPACT (Going deeper)
            Interviewer: [Long pause] "What's the real cost to you?"
            Subject: "If I'm being honest..."
            Interviewer: "What are you afraid might happen?"
            Subject: [Reveals first fear]
            
            LAYER 3: CORE FEARS (The breakthrough)
            Interviewer: "What's your biggest fear in this role?"
            Subject: "I've never said this out loud, but..."
            Interviewer: "What would failure mean for you?"
            Subject: [Major revelation about identity]
            
            LAYER 4: IDENTITY CRISIS (The truth)
            Interviewer: "Who are you without this success?"
            Subject: [Long pause, emotional response]
            Interviewer: "What are you really fighting for?"
            Subject: "It's not about the company... it's about..."
            
            LAYER 5: RESISTANCE PATTERNS (The insight)
            Interviewer: "Part of you doesn't want to solve this..."
            Subject: "How did you know?"
            Interviewer: "What do you gain from the problem?"
            Subject: [Admits attachment to struggle]
            """,
            
            "5_voice_of_customer": """
            Emotional Expression Capture:
            Interviewer: "Say exactly what you're thinking, unfiltered"
            - Capture raw emotional language
            - Document sighs, pauses, tears
            - Record exact profanity/frustration
            - Note when voice breaks
            
            Key moments: "Can I be completely honest?" "Between you and me..."
            """,
            
            "6_competitive_landscape": """
            Competitive Psychology:
            Interviewer: "How do you really feel about [Competitor]?"
            - Envy and admiration patterns
            - Competitive inadequacy feelings
            - Status anxiety triggers
            - Fear of being surpassed
            
            Probes: "What do you wish you had?" "What threatens you?"
            """,
            
            "7_positioning_strategy": """
            Ideal Vendor Psychology:
            Interviewer: "What kind of partner would make you feel safe?"
            - Trust requirement exploration
            - Control needs assessment
            - Vulnerability comfort levels
            - Power dynamic preferences
            
            Probes: "Who would you trust with your career?"
            """,
            
            "8_messaging_framework": """
            Message Resonance Testing:
            Interviewer: "When I say [message], what happens inside?"
            - Emotional reaction to words
            - Trigger identification
            - Defense activation points
            - Hope activation language
            
            Test phrases for visceral response
            """,
            
            "9_product_strategy": """
            Product Psychology Needs:
            Interviewer: "What features would make you feel confident?"
            - Control requirements
            - Complexity tolerance
            - Safety feature needs
            - Ego protection features
            
            Probes: "What would make you look good?"
            """,
            
            "10_pricing_strategy": """
            Investment Psychology:
            Interviewer: "How do you justify big purchases to yourself?"
            - Self-worth and price correlation
            - Scarcity vs abundance mindset
            - Permission patterns
            - Value perception drivers
            
            Probes: "What makes you feel worth it?"
            """,
            
            "11_sales_strategy": """
            Being Sold To Psychology:
            Interviewer: "Tell me about a time you said yes against logic"
            - Emotional purchase drivers
            - Trust building requirements
            - Manipulation triggers
            - Resistance patterns
            
            Probes: "What made you trust?" "When do you shut down?"
            """,
            
            "12_marketing_strategy": """
            Information Seeking Psychology:
            Interviewer: "How do you really make decisions?"
            - Information gathering rituals
            - Validation seeking patterns
            - Influence susceptibility
            - Decision confidence builders
            
            Probes: "Whose opinion matters?" "What convinces you?"
            """,
            
            "13_success_metrics": """
            Personal Success Psychology:
            Interviewer: "How do you know when you've succeeded?"
            - Internal scorecard revelation
            - External validation needs
            - Achievement addiction patterns
            - Never-enough syndrome
            
            Probes: "What would be enough?" "Who are you trying to impress?"
            """,
            
            "14_implementation_roadmap": """
            Change Readiness Psychology:
            Interviewer: "What would it take for you to really change?"
            - Change capacity assessment
            - Safety requirements
            - Pace tolerance
            - Support needs
            
            Closing: "One last thing you haven't admitted..."
            """
        }
    
    def get_full_prompt(self, company_name: str, context: Dict[str, Any]) -> str:
        """Generate complete psychological interview prompt"""
        
        prompt = f"""Create 3 deep psychological interviews exploring {company_name}'s ICP psychology.

INTERVIEW REQUIREMENTS:
- Minimum 2000 words total
- Progressive psychological depth
- Emotional breakthroughs and revelations
- Cover all 14 sections naturally through dialogue
- Include resistance, tears, long pauses, admissions

PSYCHOLOGICAL TECHNIQUES TO SHOW:
- Silence that prompts revelation
- Reframing that bypasses defenses
- Empathy that enables vulnerability  
- Questions that surface contradictions
- Moments of profound insight

The interviews should feel uncomfortably real with moments like:
- "I've never told anyone this..."
- "Oh my god, you're right..."
- "[Long pause]... I think I'm afraid that..."
- "This is going to sound terrible, but..."

Structure each interview to cover 4-5 sections naturally:
"""
        
        for section_key, section_prompt in self.sections.items():
            prompt += f"\n{section_key.upper()}:\n{section_prompt}\n"
        
        return prompt