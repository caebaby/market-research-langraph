# voice_agent.py
"""
Voice of Customer Agent - Captures journal-level authentic customer language
"""

from typing import Dict, Any, Tuple, List
import json
import logging
from datetime import datetime

from core.standard_agent import StandardAgentNode
from prompts.research_prompts import ICPResearchPrompts

logger = logging.getLogger(__name__)

class VoiceAgent(StandardAgentNode):
    """
    Captures customer language at "read their journal" accuracy level.
    Produces copy-ready phrases that make customers think "how did you read my mind?"
    """
    
    def __init__(self):
        role_prompt = """You are a Customer Voice Specialist who achieves "mind reader" level accuracy. You combine:

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

        super().__init__(
            agent_name="Voice of Customer Mind Reader",
            role_prompt=role_prompt,
            target_quality=0.85  # Higher bar for accuracy
        )
        
        # ICP accuracy weighting system
        self.icp_validators = {
            "demographic_match": 0.2,
            "psychographic_match": 0.3,
            "situational_match": 0.3,
            "language_sophistication_match": 0.2
        }

    async def _execute_core_analysis(self, task_description: str) -> Tuple[str, float]:
        """Execute voice analysis with AI + search hybrid approach"""
        
        # Extract all available context
        business_context = self._extract_business_context()
        
        # Optional enrichment from other agents (but not required)
        psychological_profile = self._extract_shared_insights("psychological")
        competitor_insights = self._extract_shared_insights("competitor")
        
        # If no psychological profile, we can still work with business context alone
        if not psychological_profile:
            psychological_profile = "No psychological profile available - inferring from business context"
        
        if not competitor_insights:
            competitor_insights = "No competitor analysis available - focusing on customer voice independently"
        
        # Step 1: Build ICP-specific language hypothesis using AI
        language_hypothesis = self._generate_language_hypothesis(
            business_context,
            psychological_profile
        )
        
        # Step 2: Attempt to validate/enhance with real-world data
        validation_data = await self._validate_with_real_data(
            business_context,
            language_hypothesis
        )
        
        # Step 3: Synthesize AI insights + real data into voice bible
        voice_analysis_prompt = self._build_synthesis_prompt(
            business_context,
            psychological_profile,
            language_hypothesis,
            validation_data,
            competitor_insights
        )
        
        # Generate final analysis
        response = self.llm.invoke(voice_analysis_prompt)
        
        # Assess quality with ICP accuracy weighting
        quality_score = self._assess_icp_accuracy(response.content, psychological_profile)
        
        return response.content, quality_score
    
    def _generate_language_hypothesis(self, business_context: str, psychological_profile: str) -> str:
        """Use AI to hypothesize how this specific ICP talks privately"""
        
        # Build prompt differently based on available context
        if "No psychological profile available" in psychological_profile:
            hypothesis_prompt = f"""Based on this business context alone, infer the target ICP and predict their private language:

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
        
        return self.llm.invoke(hypothesis_prompt).content
    
    async def _validate_with_real_data(self, business_context: str, language_hypothesis: str) -> str:
        """Attempt to find real examples validating our hypothesis"""
        
        if not self.tool_executor:
            return "No search validation available - relying on AI hypothesis"
        
        # Extract key phrases from hypothesis to search for
        key_phrases = self._extract_search_phrases(language_hypothesis)
        
        validation_results = []
        search_queries = []
        
        # Build targeted searches based on hypothesis
        for phrase in key_phrases[:5]:  # Limit to avoid over-searching
            queries = [
                f'"{phrase}" {business_context} reddit',
                f'"{phrase}" forum honest',
                f'"{phrase}" "real talk" review'
            ]
            search_queries.extend(queries)
        
        # Also search for ICP-specific communities
        search_queries.extend([
            f'{business_context} "I finally admitted" OR "truth is" site:reddit.com',
            f'{business_context} "3am thoughts" OR "cant sleep" forum',
            f'{business_context} "told my therapist" OR "journaling about"'
        ])
        
        # Execute searches with error handling
        for query in search_queries[:8]:  # Limit total searches
            try:
                results = await self.tool_executor.execute("web_search", {"query": query})
                validation_results.append(f"Validation search: {query}\nResults: {results}\n")
            except Exception as e:
                logger.info(f"Search skipped for {query}: {e}")
        
        if not validation_results:
            return "Search validation unavailable - proceeding with AI hypothesis"
        
        return "\n".join(validation_results)
    
    def _extract_search_phrases(self, hypothesis: str) -> List[str]:
        """Extract specific phrases from hypothesis to search for"""
        # This is simplified - in production, would use NLP to extract key phrases
        phrases = []
        lines = hypothesis.split('\n')
        for line in lines:
            if '"' in line:
                import re
                quoted = re.findall(r'"([^"]*)"', line)
                phrases.extend(quoted)
        return phrases[:10]  # Top 10 phrases
    
    def _build_synthesis_prompt(
        self,
        business_context: str,
        psychological_profile: str,
        language_hypothesis: str,
        validation_data: str,
        competitor_insights: str
    ) -> str:
        """Synthesize AI hypothesis + real data into voice bible"""
        
        return f"""Create a VOICE OF CUSTOMER BIBLE that achieves "mind reader" accuracy:

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
    
    def _assess_icp_accuracy(self, analysis: str, psychological_profile: str) -> float:
        """Assess accuracy against specific ICP profile"""
        
        score = 0.0
        
        # Check for specific, non-generic language
        if analysis.count('"') > 30:  # Many exact phrases
            score += 0.25
        
        # Check for journal-level intimacy markers
        intimacy_markers = ["3am", "journal", "therapist", "admit", "confession", "midnight"]
        if sum(1 for marker in intimacy_markers if marker in analysis.lower()) >= 4:
            score += 0.25
        
        # Check for ICP-specific validation
        if "ICP Match Score:" in analysis and "/10" in analysis:
            score += 0.2
        
        # Check for copy-ready output
        if all(section in analysis for section in ["Email Subject Lines:", "Ad Headlines:", "Landing Page Opener:"]):
            score += 0.2
        
        # Check for depth and specificity
        if "Golden Phrase" in analysis and "Breaking point" in analysis:
            score += 0.1
        
        return score
    
    def _create_shared_insights(self, analysis: str) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        
        return {
            "summary": "Journal-level accurate voice of customer captured with copy-ready phrases",
            "key_findings": {
                "pain_language": "Exact phrases from their private venting",
                "trigger_phrases": "Breaking point language that drives action",
                "golden_phrase": "The one sentence that captures everything",
                "copy_headlines": "Ready-to-use ad headlines in their voice"
            },
            "quality_score": self.state.get("quality_score", 0.0),
            "timestamp": datetime.now().isoformat()
        }
