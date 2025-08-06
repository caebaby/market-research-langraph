# team_icp/prompts/interview_sales_v4.py
"""
Sales Interview Agent Prompts - Creates realistic sales discovery interviews
"""

class SalesInterviewPrompts:
    """Prompts for sales intelligence interview simulations"""
    
    @staticmethod
    def get_sales_interviews(psychological_analysis=None, business_context=None):
        """Create 3 sales intelligence interviews focused on objections and buying criteria"""
        
        base_prompt = """
**SALES INTELLIGENCE INTERVIEW SIMULATION**

**OBJECTIVE**: Create 3 realistic customer interviews that extract critical sales intelligence: current problems, pain intensity, desires, solution history, beliefs, objections, and buying criteria. Focus on uncovering what they need to know/believe to invest in change.

**SALES INTELLIGENCE PRIORITIES:**
- **Current Problems**: Specific operational and emotional challenges they face daily
- **Pain Intensity**: How much these problems actually cost them (time, money, stress, relationships)
- **Magic Wand Desires**: What they'd change if they could wave a magic wand
- **Solution History**: What they've tried before and why it didn't work
- **Beliefs About Solutions**: What they think about available options
- **Objections**: What stops them from taking action
- **Buying Criteria**: What they need to know/believe to invest in a solution

**INTERVIEW QUALITY STANDARDS:**
- Natural sales conversation flow
- Gradual trust building
- Realistic objection patterns
- Authentic business language
- Clear buying signals or barriers
"""
        
        if psychological_analysis:
            prompt = f"{base_prompt}\n\nPSYCHOLOGICAL FOUNDATION:\n{psychological_analysis}\n\n"
            prompt += """Use the psychological insights to dig deeper into the emotional drivers behind objections."""
        else:
            prompt = f"{base_prompt}\n\nBUSINESS CONTEXT:\n{business_context}\n\n"
        
        prompt += """
## INTERVIEW 1: CURRENT PROBLEMS & PAIN EXTRACTION

Create a 600-800 word interview focused on understanding their current situation.

**Interviewer**: I'm researching challenges that [industry professionals] face. What would you say are your biggest day-to-day problems right now?

**Customer**: [Start with surface problems, then probe deeper to reveal specific pain points]

Continue the conversation to uncover:
- Specific examples of how problems manifest
- Actual costs (time, money, stress, relationships)
- What they'd fix with a magic wand
- Previous solution attempts
- Current beliefs about available solutions
- What stops them from making changes
- What they'd need to believe to take action

## INTERVIEW 2: SOLUTION BELIEFS & OBJECTION DEEP DIVE

Create a 600-800 word interview exploring their beliefs about solutions and hidden objections.

**Interviewer**: You mentioned you've looked into different approaches. What's your honest opinion about [solution type]?

**Customer**: [Reveal beliefs about solutions, both positive and negative]

Continue probing to discover:
- Specific concerns about the approach
- Past experiences with similar solutions
- What would need to be true for confidence
- Financial vs psychological barriers
- Proof requirements and validation needs

## INTERVIEW 3: BUYING PSYCHOLOGY & DECISION CRITERIA

Create a 600-800 word interview revealing how they make buying decisions.

**Interviewer**: You seem thoughtful about big decisions. How do you typically evaluate major changes to your practice?

**Customer**: [Reveal decision-making process based on psychological patterns]

Explore:
- What would prioritize this change
- Ideal support structure needed
- Questions requiring answers before investing
- Preferred learning/buying process
- Success metrics and expectations

**DELIVERABLE REQUIREMENTS:**
- 3 complete sales intelligence interviews
- Specific problem identification with pain intensity
- Solution history showing what hasn't worked
- Belief system mapping about available solutions
- Objection inventory with underlying drivers
- Buying criteria for confident decision-making
- Conversion psychology insights

End with:

## SALES INTELLIGENCE EXTRACTION

**CURRENT PROBLEMS IDENTIFIED:**
[List specific problems with pain ratings]

**MAGIC WAND DESIRES:**
[What they'd change if they could]

**SOLUTION HISTORY & FAILURES:**
[What they've tried and why it failed]

**PRIMARY OBJECTIONS:**
[Financial, implementation, capability, validation needs]

**BUYING CRITERIA REVEALED:**
[What they need to know/believe to buy]

**CONVERSION INSIGHTS:**
[Urgency drivers, social proof needs, risk reversal requirements]
"""
        
        return prompt
    
    @staticmethod
    def get_sales_reflection_prompt():
        """Prompt for evaluating sales interview quality"""
        
        return """
Evaluate these sales interviews as an expert sales trainer would:

1. PROBLEM DISCOVERY (0.0-1.0): How well do we understand their pain?
   - Specific problems identified
   - Pain intensity understood
   - Cost of inaction clear
   - Emotional impact revealed

2. OBJECTION HANDLING (0.0-1.0): Are real objections uncovered?
   - Surface objections identified
   - Hidden concerns revealed
   - Root causes understood
   - Objection patterns clear

3. BUYING CRITERIA (0.0-1.0): Is their decision process clear?
   - What they need to know
   - What they need to believe
   - Proof requirements
   - Success metrics

4. CONVERSATION QUALITY (0.0-1.0): Does it feel like a real sales call?
   - Natural flow
   - Trust building progression
   - Authentic responses
   - Realistic pacing

5. ACTIONABILITY (0.0-1.0): Can a salesperson use these insights?
   - Clear next steps
   - Specific talking points
   - Objection responses
   - Positioning guidance

Provide specific examples of strengths and weaknesses.

CRITICAL: End your evaluation with:
OVERALL_SCORE: [number between 0.0 and 1.0]
"""
