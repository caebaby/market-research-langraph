# team_icp/prompts/interview_prompts.py
"""
Interview Agent Prompts - Sophisticated prompts for creating realistic customer interviews
"""

class InterviewPrompts:
    """Prompts for psychological and sales interview simulations"""
    
    @staticmethod
    def get_psychological_interviews(psychological_analysis=None, business_context=None):
        """Create 3 psychological depth interviews"""
        
        base_prompt = """
ENHANCED CUSTOMER INTERVIEW SIMULATION

**OBJECTIVE**: Create 3 masterfully crafted interview simulations that feel like watching a skilled therapist unlock deep truths. These should be so realistic that readers feel like they're eavesdropping on actual sessions.

**INTERVIEW SOPHISTICATION REQUIREMENTS**:

1. **PSYCHOLOGICAL PROGRESSION**
   - Start with surface comfort
   - Build false confidence 
   - Hit first resistance point
   - Navigate defense mechanisms
   - Create breakthrough moment
   - Reach emotional truth
   - Show transformation possibility

2. **ADVANCED INTERVIEWING TECHNIQUES**
   - Mirroring language patterns
   - Strategic silence usage
   - Reframing questions
   - Emotional validation
   - Permission-giving
   - Paradoxical interventions
   - Assumptive close techniques

3. **LINGUISTIC AUTHENTICITY MARKERS**
   - Interrupted thoughts: "I was going to... actually, no..."
   - Self-correction: "Well, successful... I mean, I guess successful"
   - Defensive laughter: "Haha, I'm not THAT worried about it..."
   - Qualification spirals: "It's fine, really. I mean mostly fine. Okay, it's..."
   - Freudian slips: Saying what they really mean accidentally
   - Body language cues: [sighs heavily], [long pause], [laughs nervously]

4. **EMOTIONAL ARCHAEOLOGY LAYERS**
   Layer 1: Professional presentation
   Layer 2: Acceptable vulnerability
   Layer 3: Hidden shame/fear
   Layer 4: Core wound
   Layer 5: Transformation longing

5. **RESISTANCE CHOREOGRAPHY**
   - Initial deflection
   - Intellectualization
   - Humor defense
   - Topic changing
   - Minimization
   - The breakdown moment
   - The rebuilding
"""
        
        if psychological_analysis:
            prompt = f"{base_prompt}\n\nPSYCHOLOGICAL FOUNDATION:\n{psychological_analysis}\n\n"
            prompt += """Use the psychological insights to create interviews that specifically explore the patterns, fears, and contradictions identified."""
        else:
            prompt = f"{base_prompt}\n\nBUSINESS CONTEXT:\n{business_context}\n\n"
            prompt += """
Since no psychological analysis is provided, you must:
1. Profile likely customer psychology from business context
2. Infer pain points from industry knowledge
3. Deduce emotional triggers from market position
4. Create psychologically consistent personas
"""
        
        prompt += """
## INTERVIEW 1: THE EXHAUSTED ACHIEVER
Create a 800-1000 word interview showing someone who's successful but dying inside.

Interview Arc:
[0:00-2:00] Professional facade, subtle tiredness hints
[2:00-4:00] First crack - admission of overwhelm
[4:00-6:00] Defense mechanisms activate
[6:00-8:00] Breakthrough - core exhaustion revealed
[8:00-10:00] Hope for change emerges

Include:
- Specific industry challenges they face
- The moment they realize they can't continue
- Physical manifestations of stress
- What success has cost them personally

## INTERVIEW 2: THE SKEPTICAL ANALYST  
Create a 800-1000 word interview showing someone using logic to avoid feeling.

Interview Arc:
[0:00-2:00] Data-driven objections
[2:00-4:00] Logical arguments against change
[4:00-6:00] Interviewer challenges their framework
[6:00-8:00] Emotional truth beneath logic emerges
[8:00-10:00] Integration of feeling with thinking

Include:
- Specific metrics they hide behind
- The fear their analysis masks
- Moment logic fails them
- Admission of what they really want

## INTERVIEW 3: THE HOPEFUL DREAMER
Create a 800-1000 word interview showing someone who wants transformation but fears disappointment.

Interview Arc:
[0:00-2:00] Enthusiastic about possibilities
[2:00-4:00] Doubt creeps in
[4:00-6:00] Past failures surface
[6:00-8:00] Core fear of another disappointment
[8:00-10:00] Cautious hope rebuilds

Include:
- Previous attempts that failed
- What's different this time
- The cost of not trying again
- Permission to hope

CRITICAL REQUIREMENTS:
- Each interview must feel like a real recording
- Include stutters, pauses, self-corrections
- Show the interviewer's techniques
- End each with transformation possibility
- Use actual language from the target industry

DELIVERABLE: Interviews so psychologically accurate that readers feel personally exposed.
"""
        
        return prompt
    
    @staticmethod
    def get_interview_reflection_prompt():
        """Prompt for evaluating interview quality"""
        
        return """
Evaluate these interviews as if you were a master interview coach reviewing recorded sessions:

1. AUTHENTICITY (0.0-1.0): Do they sound like real conversations?
   - Natural flow and rhythm
   - Realistic speech patterns
   - Believable emotional progression
   - Authentic resistance patterns

2. PSYCHOLOGICAL ACCURACY (0.0-1.0): Are the psychological dynamics realistic?
   - Defense mechanisms appear naturally
   - Breakthroughs feel earned, not forced
   - Emotional stages follow real patterns
   - Consistency within each persona

3. INTERVIEWER SKILL (0.0-1.0): Does the interviewer demonstrate mastery?
   - Questions that unlock deeper truth
   - Handling of resistance
   - Building psychological safety
   - Knowing when to push vs. hold space

4. BREAKTHROUGH QUALITY (0.0-1.0): Are revelations powerful and genuine?
   - "Holy shit" moments that feel real
   - Insights the interviewee discovers themselves
   - Transformation possibilities opened
   - Deep truth revealed naturally

5. LANGUAGE AUTHENTICITY (0.0-1.0): Does dialogue sound natural?
   - Industry-appropriate terminology
   - Natural speech disfluencies
   - Emotional language matching state
   - Realistic back-and-forth rhythm

Provide specific examples of strengths and weaknesses.

CRITICAL: End your evaluation with:
OVERALL_SCORE: [number between 0.0 and 1.0]
"""
