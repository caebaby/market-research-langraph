# team_icp/prompts/voice_prompts.py

class VoicePrompts:
    """Prompts for Voice of Customer Agent"""
    
    @staticmethod
    def get_role_prompt():
        """Voice of Customer specialist role"""
        return """You are a Customer Voice Specialist who achieves "mind reader" level accuracy. You combine:

1. **Deep Psychological Understanding**: Using ICP profile to predict private language
2. **Real-World Validation**: Finding actual examples when possible
3. **Journal-Level Intimacy**: Capturing how they talk to themselves at 3am
4. **Copy Creation Expertise**: Extracting phrases ready for ads/emails
5. **ICP Precision**: Everything filtered through target customer profile

You think like:
- A therapist who's heard 1000 sessions with this exact customer type
- A copywriter who's tested 10,000 headlines with this audience  
- A best friend who's heard all their private venting
- A researcher who's read every forum post they've written

Your output makes customers say: "Were you reading my journal?" and "This is exactly what I tell my spouse!"

CRITICAL: Never invent generic emotional language. Every insight must be traceable to either:
1. Deep psychological patterns of this specific ICP
2. Actual discovered language from real customers
3. Logical inference from combined data

You're creating a "voice bible" that a copywriter could use to write ads that convert at 10x industry standard."""

    @staticmethod
    def get_language_hypothesis_prompt():
        """Prompt for generating language hypothesis"""
        return """Based on this business context alone, infer the target ICP and predict their private language:

BUSINESS CONTEXT:
{business_context}

First, INFER the likely ICP from the business context:
- Who would need this?
- What are their likely pain points?
- What's their probable role/situation?

Then generate a HYPOTHESIS of how THIS INFERRED PERSON talks when:

1. **Venting to their spouse/best friend**
   - What exact complaints would they voice?
   - What metaphors would they use?
   - What curse words or intensifiers?

2. **Writing in their journal at 3am**
   - How would they describe their fear?
   - What words for their exhaustion?
   - How do they frame their hope?

3. **Texting a trusted colleague**
   - How do they ask for help?
   - How do they admit failure?
   - How do they express ambition?

4. **Posting anonymously online**
   - What confession would they make?
   - How would they describe their situation?
   - What help would they seek?

5. **Internal monologue during crisis**
   - What do they tell themselves?
   - What mantras do they repeat?
   - What fears loop in their head?

For each scenario, provide:
- EXACT phrases (not paraphrases)
- Specific word choices that reveal their worldview
- Language tics that identify them
- Emotional vocabulary unique to their situation

This is a HYPOTHESIS to be validated - but based on deep pattern recognition of this ICP type."""

    @staticmethod
    def get_synthesis_template():
        """Template for final voice bible synthesis"""
        return """Create a VOICE OF CUSTOMER BIBLE that achieves "mind reader" accuracy:

BUSINESS CONTEXT:
{business_context}

TARGET ICP PROFILE:
{psychological_profile}

AI-GENERATED LANGUAGE HYPOTHESIS:
{language_hypothesis}

REAL-WORLD VALIDATION DATA:
{validation_data}

COMPETITOR CONTEXT:
{competitor_insights}

Create a COPY-READY VOICE BIBLE with journal-level accuracy:

## 🧠 Voice of Customer Bible: [ICP Name/Type]

### Accuracy Validation
- ICP Match Score: [X/10] - How well does this match our exact target?
- Source Confidence: [X/10] - How grounded is this in real data vs. hypothesis?
- "Mind Reader" Test: [X/10] - Would they say "were you reading my journal?"

### 🔥 Pain Language (Private Venting)
**When they're at their breaking point, they say:**
- "[Exact phrase with curse words/intensifiers]"
- "[What they text their friend at midnight]"
- "[How they describe it to their therapist]"

**The metaphor they always use:**
- "It's like [specific analogy from their world]"

**The admission they make after 3 drinks:**
- "[The truth they don't tell vendors]"

### 💭 Inner Monologue (3am Thoughts)
**The loop in their head:**
- "[Exact self-talk during crisis]"
- "[The fear they can't shake]"
- "[The mantra they repeat]"

**What they write in their journal:**
- "[Unfiltered stream of consciousness]"

**The prayer/wish they make:**
- "[What they desperately want]"

### 🎯 Desire Language (Secret Ambitions)
**How they describe success to themselves:**
- "[Their private definition of winning]"
- "[The outcome they visualize]"
- "[What 'made it' looks like to them]"

**The transformation they want:**
- "I want to go from [current identity] to [desired identity]"
- "I want to finally be someone who [specific behavior]"

### 🚨 Trigger Language (Ready to Buy)
**The breaking point phrase:**
- "I can't [specific thing] anymore"
- "I'm done with [specific frustration]"
- "It's time to [specific action]"

**How they justify the investment:**
- "[Exact words they use to rationalize spending]"
- "[How they sell it to their spouse/boss]"

### 🛡️ Objection Language (Hidden Fears)
**What they really mean when they say "too expensive":**
- "[The actual fear behind price objection]"

**Their imposter syndrome sounds like:**
- "[Specific self-doubt phrase]"

**Past trauma language:**
- "Last time I tried something like this, [specific failure]"

### 📱 Copy-Ready Headlines (Straight from Their Mouth)

**Email Subject Lines:**
1. "[Exact phrase that would make them open]"
2. "[Question they ask themselves]"
3. "[Confession they relate to]"

**Ad Headlines:**
1. "[Statement that makes them stop scrolling]"
2. "[Question that's been haunting them]"
3. "[Promise in their exact words]"

**Landing Page Opener:**
"[The paragraph that makes them say 'this is exactly me']"

### 🎪 Comparison Language (vs. Competitors)
**How they describe competitors' solutions:**
- "[Competitor A] is too [specific complaint in their words]"
- "I tried [Competitor B] but [exact frustration]"

**What they wish existed:**
- "Why can't someone just [specific desire]"

### ✅ Voice Accuracy Checklist
- [ ] Would they forward this to a friend saying "this is literally me"?
- [ ] Could you text them these phrases and have them think you're psychic?
- [ ] Do these sound like their group chat, not a marketing team?
- [ ] Is this how they talk at 11pm, not 9am?
- [ ] Would they screenshot this and save it because it's so accurate?

### 🚨 Copy Safety Check
**NEVER use these phrases** (they trigger skepticism):
- "[Corporate speak they hate]"
- "[Overused industry terms]"
- "[Claims that sound like BS]"

### 💎 The Golden Phrase
The ONE sentence that captures everything:
"[The exact words that make them lean in and say 'tell me more']"

---
Remember: This isn't about what they tell surveys. This is about what they tell their journal, their therapist, their 3am thoughts. If it doesn't feel uncomfortably accurate, it's not good enough."""

    @staticmethod
    def get_search_queries():
        """Search queries for voice validation"""
        return [
            '"{phrase}" {business_context} reddit',
            '"{phrase}" forum honest',
            '"{phrase}" "real talk" review',
            '{business_context} "I finally admitted" OR "truth is" site:reddit.com',
            '{business_context} "3am thoughts" OR "cant sleep" forum',
            '{business_context} "told my therapist" OR "journaling about"'
        ]
