# team_icp/agents/interview_psychological_v4.py
"""
Level 4 Psychological Interview Agent - Creates unnervingly realistic customer interviews
that reveal deep psychological truths through natural conversation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from core.standard_agent_v4 import StandardAgentNodeV4
from team_icp.prompts.interview_psychological_v4 import InterviewPrompts


class PsychologicalInterviewAgentV4(StandardAgentNodeV4):
   """
   Creates 3 realistic customer interview simulations revealing psychological insights.
   
   Level 4 Capabilities:
   - Memory: Recalls successful interview patterns and phrases
   - Reflection: Self-evaluates interview authenticity and depth
   - HITL: Triggers review if interviews seem unrealistic or shallow
   - Learning: Stores effective questioning techniques
   - Tool Use: Can validate phrases via web search
   - Independent Operation: Can work with or without psychological analysis
   """
   
   def __init__(self):
       super().__init__(
           agent_name="Psychological Interview Specialist",
           role_prompt="""You are an expert at conducting psychological depth interviews that reveal
deep customer truths through natural conversation. You create realistic dialogue with authentic
speech patterns, emotional vulnerability, and breakthrough moments.""",
           target_quality=0.85,
           require_human_review_below=0.7
       )
       
   def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
       """Generate psychological interview simulations with goal decomposition"""
       
       # Goal decomposition for Level 4
       sub_goals = self._decompose_interview_goals(task)
       print(f"[{self.agent_name}] Decomposed into {len(sub_goals)} sub-goals")
   
       # Extract psychological insights if available
       psychological_insights = self._extract_psychological_insights(context)
       if not psychological_insights:
           print(f"[{self.agent_name}] Creating independent interviews from business context")
           psychological_insights = context  # Use full context as fallback
   
       # Format memories if available
       interview_patterns = self._format_interview_memories(memories, psychological_insights)
       
       ## Get the prompt from research_prompts
       try:
           interview_prompt = InterviewPrompts.get_psychological_interviews(psychological_analysis=psychological_insights)
           print(f"[{self.agent_name}] Using interview prompts")
       except Exception as e:
           print(f"[{self.agent_name}] Prompt generation error: {e}, using fallback")
           interview_prompt = self._create_fallback_prompt(context, psychological_insights)
   
       # Enhance prompt with memory patterns
       enhanced_prompt = f"{interview_prompt}\n\n{interview_patterns}" if interview_patterns else interview_prompt
   
       # Web search for validation if needed
       if self.web_search and self._should_gather_context(task, context):
           search_query = f"{self._extract_industry(context)} customer interview challenges pain points testimonials"
           print(f"🔧 {self.agent_name} requesting web search: {search_query}")
           
           search_results = self.web_search(search_query, num_results=5)
           if search_results and "Error" not in search_results:
               enhanced_prompt += f"\n\nREAL CUSTOMER INSIGHTS FROM WEB:\n{search_results[:1000]}"
               print(f"✅ {self.agent_name} incorporated search results")
   
       # Generate interviews
       print(f"[{self.agent_name}] Creating 3 psychological depth interviews...")
       try:
           response = llm.invoke(enhanced_prompt)
           output = response.content if hasattr(response, 'content') else str(response)
       except Exception as e:
           print(f"[{self.agent_name}] LLM error: {e}")
           output = self._create_fallback_interviews(context)
   
       # Debug output
       print(f"[DEBUG] LLM output length: {len(output)}")
       print(f"[DEBUG] First 200 chars: {output[:200]}")
   
       # Validate and enhance output
       if not self._validate_interview_output(output):
           print(f"[{self.agent_name}] Output validation failed, using enhanced fallback")
           output = self._create_fallback_interviews(context)
   
       return output
   
   def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
       """Evaluate interview quality with robust parsing"""
       
       # Build reflection prompt
       reflection_prompt = f"""Evaluate these customer interviews for psychological depth and authenticity.

INTERVIEWS TO EVALUATE:
{response[:4000]}...

EVALUATION CRITERIA:
1. Interview Structure (3 complete interviews with clear personas)
2. Authenticity (Natural speech, hesitations, emotional markers)
3. Psychological Depth (Identity issues, fears, contradictions revealed)
4. Breakthrough Moments (Genuine realizations or emotional shifts)
5. Interviewer Skill (Appropriate techniques, empathy, probing)

Provide:
- Brief critique highlighting strengths and weaknesses
- OVERALL_SCORE: [0.0-1.0] on the last line"""
       
       try:
           reflection_result = llm.invoke(reflection_prompt).content
       except Exception as e:
           print(f"[{self.agent_name}] Reflection error: {e}")
           reflection_result = "Reflection failed"
       
       # Parse score with multiple patterns
       score = self._parse_reflection_score(reflection_result)
       critique = reflection_result
       
       # Quality indicators check
       quality_indicators = self._check_quality_indicators(response)
       
       # Adjust score based on objective checks
       score = self._adjust_score_by_indicators(score, quality_indicators, critique)
       
       print(f"[{self.agent_name}] Reflection score: {score:.2f}")
       print(f"[{self.agent_name}] Quality indicators: {quality_indicators}")
       
       return {
           "critique": critique,
           "score": score,
           "quality_indicators": quality_indicators
       }
   
   def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
       """Extract successful interview patterns for future use"""
       
       insights = {
           "interview_techniques": [],
           "effective_questions": [],
           "breakthrough_moments": [],
           "psychological_patterns": [],
           "authenticity_markers": [],
           "timestamp": datetime.now().isoformat()
       }
       
       # Extract techniques
       techniques = {
           "reframing": "Reframing questions unlock new perspectives",
           "silence": "Strategic silence creates breakthrough space",
           "validation": "Validation builds trust for deeper sharing",
           "permission": "Permission-giving enables vulnerability"
       }
       
       for key, value in techniques.items():
           if key in response.lower():
               insights["interview_techniques"].append(value)
       
       # Extract effective questions
       questions = re.findall(r'(?:Q:|Interviewer:)\s*([^?\n]+\?)', response)
       emotional_questions = [q for q in questions if any(word in q.lower() for word in 
                             ["feel", "mean", "fear", "want", "wish", "imagine", "worry"])]
       insights["effective_questions"] = emotional_questions[:3]
       
       # Extract breakthrough moments
       breakthroughs = self._extract_breakthrough_moments(response)
       insights["breakthrough_moments"] = breakthroughs[:3]
       
       # Extract psychological patterns
       patterns = {
           "exhaustion": "Exhaustion theme resonates deeply",
           "identity": "Identity crisis central to customer psychology",
           "isolation": "Feeling alone despite success",
           "impostor": "Impostor syndrome drives behavior"
       }
       
       for key, value in patterns.items():
           if response.lower().count(key) >= 2:  # Appears multiple times
               insights["psychological_patterns"].append(value)
       
       return insights
   
   def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
       """Create insights to share with other agents"""
       
       # Extract key patterns
       patterns = self._analyze_interview_patterns(response)
       
       # Extract powerful quotes
       quotes = self._extract_powerful_quotes(response)
       
       # Identify personas
       personas = self._identify_personas(response)
       
       return {
           "summary": f"Conducted 3 psychological depth interviews with quality score {quality:.2f}. "
                     f"Core patterns: {', '.join(patterns[:2])}. "
                     f"Interviews revealed authentic customer voice through natural dialogue.",
           "patterns": patterns,
           "powerful_quotes": quotes[:3],
           "interview_personas": personas,
           "breakthrough_moments": self._extract_breakthrough_moments(response)[:2],
           "quality_score": quality,
           "timestamp": datetime.now().isoformat()
       }
   
   # HELPER METHODS
   
   def _decompose_interview_goals(self, task: str) -> List[str]:
       """Decompose interview task into sub-goals for Level 4 goal pursuit"""
       return [
           f"Analyze context for key psychological themes",
           "Design 3 distinct but related customer personas",
           "Create authentic dialogue with natural speech patterns",
           "Engineer breakthrough moments through skilled questioning",
           "Validate insights against real customer language"
       ]
   
   def _format_all_relevant_memories(self, memories: List, psychological_insights: str) -> str:
       """Format all types of relevant memories"""
       return self._format_interview_memories(memories, psychological_insights)
   
   def _extract_industry(self, context: str) -> str:
       """Extract industry from context"""
       context_lower = context.lower()
       
       industries = {
           'coach': 'executive coaching',
           'consult': 'consulting',
           'tech': 'technology',
           'founder': 'startup',
           'financial': 'financial services',
           'health': 'healthcare',
           'wellness': 'wellness',
           'saas': 'software',
           'agency': 'marketing agency'
       }
       
       for key, value in industries.items():
           if key in context_lower:
               return value
               
       return "business"
   
   def _should_gather_context(self, task: str, context: str) -> bool:
       """Determine if we need more context via web search"""
       
       # Don't search if we already have rich context
       if len(context) > 1000:
           return False
           
       # Search if task requests validation
       if any(word in task.lower() for word in ["validate", "verify", "research", "find"]):
           return True
           
       # Search if context is minimal
       if len(context) < 200:
           return True
           
       return False
   
   def _extract_psychological_insights(self, context: str) -> str:
       """Extract psychological analysis from context/shared insights"""
       
       # Check shared insights first
       if self.state and "shared_insights" in self.state:
           shared = self.state["shared_insights"]
           
           # Look for psychological agent output
           for agent_name in ["Psychological Analyst V4", "psychological", "Psychological"]:
               if agent_name in shared:
                   insights = shared[agent_name]
                   if isinstance(insights, dict):
                       return insights.get("summary", "") + "\n" + str(insights.get("patterns", ""))
                   return str(insights)
       
       # Check context for insights section
       if "INSIGHTS FROM OTHER AGENTS:" in context:
           parts = context.split("INSIGHTS FROM OTHER AGENTS:")
           if len(parts) > 1:
               return self._parse_psychological_section(parts[1])
       
       # Check if context itself contains psychological analysis
       psych_keywords = ["identity", "fear", "unconscious", "archetype", "contradiction", "shadow"]
       if any(keyword in context.lower() for keyword in psych_keywords):
           return context
           
       return ""
   
   def _parse_psychological_section(self, insights_text: str) -> str:
       """Parse psychological section from insights text"""
       
       # Find psychological agent section
       for marker in ["psychological:", "Psychological:", "From Psychological"]:
           if marker in insights_text:
               start = insights_text.find(marker)
               section = insights_text[start:]
               
               # Find end (next agent or end of text)
               end_markers = ["\n\nFrom", "\nvoice:", "\nVoice:", "\ncompetitor:"]
               end_pos = len(section)
               
               for end_marker in end_markers:
                   pos = section.find(end_marker)
                   if 0 < pos < end_pos:
                       end_pos = pos
               
               return section[:end_pos].strip()
               
       return ""
   
   def _create_fallback_prompt(self, context: str, psychological_insights: str) -> str:
       """Create fallback prompt when main prompt fails"""
       
       return f"""Create 3 realistic customer interviews about: {context}

Each interview should:
1. Have a distinct persona (e.g., "Exhausted Achiever", "Skeptical Analyst", "Hopeful Dreamer")
2. Include timestamps like [2:15] showing progression
3. Use authentic speech patterns: "I guess", "honestly", "I mean", pauses, hesitations
4. Reveal deep psychological truths through natural conversation
5. Include at least one breakthrough moment where defenses drop

Format:
INTERVIEW 1: [Persona Name] - [Brief Description]
[0:00] 
Interviewer: [Opening question]
Customer: [Response with authentic speech]

Continue for 5-7 exchanges per interview, showing emotional progression.

Psychological context to incorporate:
{psychological_insights[:500] if psychological_insights else "Customer faces identity and exhaustion challenges"}
"""
   
   def _create_fallback_interviews(self, context: str) -> str:
       """Create complete fallback interviews when generation fails"""
       
       # Extract first meaningful word for context
       words = context.split()
       industry = next((w for w in words if len(w) > 4 and w.lower() not in ['with', 'from', 'that', 'this']), "Professional")
       
       return f"""INTERVIEW 1: The Exhausted Achiever - Successful {industry} dying inside

[0:00]
Interviewer: Tell me about your current situation with your work.

Customer: *sighs* I mean... from the outside, everything looks great, right? I'm successful, making good money, clients love me. But honestly? I'm exhausted. Like, bone-deep exhausted. I wake up every morning and just... *long pause* ...I don't know who I am anymore.

[2:15]
Interviewer: When you say you don't know who you are anymore, what does that mean to you?

Customer: I guess I've been playing this role for so long - the successful {industry}, the one who has it all together - that I've lost track of what I actually want. I'm just going through the motions. Sometimes I look in the mirror and think, "Who the hell is this person?"

[4:30]
Interviewer: What would it mean to reconnect with who you really are?

Customer: *voice cracks slightly* God, I... I haven't even let myself think about that. I'm terrified that if I stop, if I actually look at my life, the whole thing will fall apart. But I can't keep going like this. I just can't.

INTERVIEW 2: The Skeptical Analyst - Using logic to avoid feeling

[0:00]
Interviewer: What brought you to explore making changes in your {industry} practice?

Customer: Well, logically speaking, the numbers don't lie. I'm working 60-70 hours a week, my hourly rate is actually decreasing if you factor in all the unpaid work. From a pure ROI perspective, something needs to change.

[2:45]
Interviewer: It sounds like you've done a thorough analysis. How does it feel when you look at those numbers?

Customer: Feel? I... *pause* Look, feelings don't pay the bills. I need practical solutions, not... *trails off* Sorry, I didn't mean to snap. It's just - I've tried the whole "follow your passion" thing before and it didn't work.

[5:00]
Interviewer: What happened when you tried following your passion?

Customer: *quieter* I trusted someone who said they could help. Spent a lot of money, opened up about my dreams... and nothing changed. Actually, that's not true. I felt more lost than before. So now I just focus on what I can control - the data, the facts. It's safer that way.

INTERVIEW 3: The Hopeful Dreamer - Wants change but fears disappointment

[0:00]
Interviewer: What's your vision for where you'd like to be in a year?

Customer: Oh, I have this whole vision board actually! I want to be working with clients who really get me, having actual weekends off, maybe even taking a real vacation. I can see it so clearly sometimes.

[2:30]
Interviewer: That sounds beautiful. What stops you from moving toward that vision?

Customer: *nervous laugh* Everything? I mean, what if I'm just fooling myself? What if this is as good as it gets? I've wanted this for so long, but every time I try to change something, I end up right back where I started. It's like I'm stuck in this loop.

[4:45]
Interviewer: What would need to be true for you to believe real change is possible?

Customer: I guess... I'd need to know I'm not alone in this. That other people have felt this stuck and actually made it to the other side. Not just the highlight reel on social media, but like, the real messy truth of how they did it. Because honestly? I'm scared I'll disappoint myself again.

[6:00]
Customer: *breakthrough moment* Wait, I just realized something. I'm so afraid of being disappointed that I'm already living in disappointment. Holy shit. I'm already living my worst fear.

PSYCHOLOGICAL PATTERNS REVEALED:
- Identity crisis: Success without authenticity
- Exhaustion: Physical and existential
- Trust issues: Past disappointments create resistance
- Hope vs. Fear: Desire for change battling fear of failure

INTERVIEWER TECHNIQUES DEMONSTRATED:
- Strategic silence to create space for revelation
- Reframing questions to shift perspective
- Permission-giving for emotional expression
- Validation without rescuing"""
   
   def _validate_interview_output(self, output: str) -> bool:
       """Validate that output contains actual interviews"""
       
       if not output or len(output) < 1000:
           return False
           
       # Check for interview markers
       if output.count("INTERVIEW") < 3:
           return False
           
       # Check for dialogue
       if not any(marker in output for marker in ["Customer:", "Interviewer:", "Q:", "A:"]):
           return False
           
       return True
   
   def _parse_reflection_score(self, reflection_text: str) -> float:
       """Parse score from reflection with multiple fallbacks"""
       
       # Try various patterns
       patterns = [
           r'OVERALL_SCORE:\s*([0-9.]+)',
           r'Overall Score:\s*([0-9.]+)',
           r'Score:\s*([0-9.]+)',
           r'Final Score:\s*([0-9.]+)',
           r'Rating:\s*([0-9.]+)',
           r'\b([0-9]\.[0-9]+)\b.*?(?:score|rating)'
       ]
       
       for pattern in patterns:
           match = re.search(pattern, reflection_text, re.IGNORECASE | re.MULTILINE)
           if match:
               try:
                   score = float(match.group(1))
                   return max(0.0, min(1.0, score))
               except ValueError:
                   continue
       
       # Sentiment-based fallback
       positive_words = ["excellent", "outstanding", "powerful", "authentic", "deep", "masterful"]
       negative_words = ["poor", "weak", "shallow", "unrealistic", "superficial", "lacking"]
       
       text_lower = reflection_text.lower()
       positive_count = sum(1 for word in positive_words if word in text_lower)
       negative_count = sum(1 for word in negative_words if word in text_lower)
       
       if positive_count > negative_count:
           return 0.75 + (positive_count * 0.05)
       elif negative_count > positive_count:
           return 0.50 + (negative_count * 0.05)
       else:
           return 0.65  # Neutral
   
   def _check_quality_indicators(self, response: str) -> Dict[str, bool]:
       """Check objective quality indicators"""
       
       return {
           "has_3_interviews": response.count("INTERVIEW") >= 3,
           "has_timestamps": bool(re.search(r'\[\d+:\d+\]', response)) or bool(re.search(r'\(\d+:\d+\)', response)),
           "has_authentic_speech": any(marker in response.lower() for marker in 
               ["i guess", "i mean", "...", "um", "uh", "*pause*", "*sighs*", "honestly"]),
           "has_emotional_depth": any(word in response.lower() for word in 
               ["terrified", "exhausted", "desperate", "ashamed", "lost", "trapped", "dying inside"]),
           "has_breakthrough": any(phrase in response.lower() for phrase in 
               ["oh my god", "just realized", "never thought", "holy shit", "wait,", "breakthrough"]),
           "sufficient_length": len(response) > 3000,
           "has_interviewer_technique": any(technique in response.lower() for technique in 
               ["reframe", "reflect", "validate", "permission", "silence", "what does that mean"])
       }
   
   def _adjust_score_by_indicators(self, base_score: float, indicators: Dict[str, bool], critique: str) -> float:
       """Adjust score based on quality indicators"""
       
       score = base_score
       adjustments = []
       
       if not indicators["has_3_interviews"]:
           score *= 0.7
           adjustments.append("Missing complete interviews")
           
       if not indicators["has_timestamps"]:
           score *= 0.95
           adjustments.append("Missing timestamp progression")
           
       if not indicators["has_authentic_speech"]:
           score *= 0.9
           adjustments.append("Needs more authentic speech patterns")
           
       if not indicators["has_emotional_depth"]:
           score *= 0.85
           adjustments.append("Lacks emotional depth")
           
       if not indicators["sufficient_length"]:
           score *= 0.9
           adjustments.append("Interviews too brief")
       
       if adjustments:
           critique += f"\n\nAdjustments: {', '.join(adjustments)}"
       
       return max(0.1, min(1.0, score))
   
   def _format_interview_memories(self, memories: List, psychological_insights: str) -> str:
       """Format relevant memories for interview generation"""
       
       if not memories:
           return ""
       
       formatted = "\nRELEVANT PATTERNS FROM MEMORY:\n"
       
       interview_memories = []
       for memory in memories:
           if isinstance(memory, dict):
               insights = memory.get("insights", {})
               if any(key in str(insights).lower() for key in ["interview", "question", "breakthrough", "authentic"]):
                   interview_memories.append(memory)
       
       if not interview_memories:
           return ""
       
       # Extract and format key patterns
       all_questions = []
       all_techniques = []
       all_breakthroughs = []
       
       for memory in interview_memories[:5]:
           insights = memory.get("insights", {})
           
           if isinstance(insights, dict):
               questions = insights.get("effective_questions", [])
               all_questions.extend(questions[:2])
               
               techniques = insights.get("interview_techniques", [])
               all_techniques.extend(techniques[:2])
               
               breakthroughs = insights.get("breakthrough_moments", [])
               all_breakthroughs.extend(breakthroughs[:2])
       
       if all_questions:
           formatted += f"\nProven Effective Questions:\n"
           for q in list(set(all_questions))[:3]:
               formatted += f"- {q}\n"
               
       if all_techniques:
           formatted += f"\nSuccessful Techniques:\n"
           for t in list(set(all_techniques))[:3]:
               formatted += f"- {t}\n"
               
       if all_breakthroughs:
           formatted += f"\nBreakthrough Patterns:\n"
           for b in list(set(all_breakthroughs))[:2]:
               formatted += f"- {b}\n"
       
       formatted += "\nApply these patterns while maintaining natural conversation flow.\n"
       
       return formatted
   
   def _analyze_interview_patterns(self, response: str) -> List[str]:
       """Analyze and extract key patterns from interviews"""
       
       patterns = []
       
       # Count theme occurrences
       themes = {
           "exhaustion": ["exhaust", "tired", "worn out", "burned out", "depleted"],
           "identity_crisis": ["who i am", "lost myself", "don't recognize", "identity", "role"],
           "isolation": ["alone", "isolated", "no one understands", "by myself"],
           "fear": ["terrified", "scared", "afraid", "worry", "anxious"],
           "hope": ["dream", "vision", "want to", "wish", "if only"]
       }
       
       theme_counts = {}
       response_lower = response.lower()
       
       for theme, keywords in themes.items():
           count = sum(response_lower.count(keyword) for keyword in keywords)
           if count > 1:  # Appears multiple times
               theme_counts[theme] = count
       
       # Sort by frequency
       sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
       
       for theme, count in sorted_themes[:3]:
           patterns.append(theme.replace("_", " ").title())
       
       return patterns
   
   def _extract_powerful_quotes(self, response: str) -> List[str]:
       """Extract emotionally powerful quotes from interviews"""
       
       quotes = []
       
       # Multiple quote patterns
       patterns = [
           r'Customer: ["\']((?:[^\n"\']{20,150}[.!?]))["\']\s*$',
           r'Customer: ((?:[^\n]{20,150}[.!?]))',
           r'"([^"]{20,150}[.!?])"',
           r"'([^']{20,150}[.!?])'"
       ]
       
       for pattern in patterns:
           found = re.findall(pattern, response, re.MULTILINE)
           quotes.extend(found)
       
       # Filter for emotional content
       emotional_keywords = ["feel", "afraid", "exhausted", "lost", "can't", "trapped", "desperate", "wish"]
       
       emotional_quotes = []
       for quote in quotes:
           if any(keyword in quote.lower() for keyword in emotional_keywords):
               # Clean and add
               clean_quote = quote.strip().replace("Customer: ", "")
               if 20 < len(clean_quote) < 150:
                   emotional_quotes.append(clean_quote)
       
       # Deduplicate and return top quotes
       seen = set()
       unique_quotes = []
       for quote in emotional_quotes:
           if quote not in seen:
               seen.add(quote)
               unique_quotes.append(quote)
       
       return unique_quotes[:5]
   
   def _identify_personas(self, response: str) -> List[str]:
       """Identify and extract persona descriptions"""
       
       personas = []
       
       # Look for interview headers
       persona_patterns = [
           r'INTERVIEW \d+: ([^-\n]+)(?:\s*-\s*([^\n]+))?',
           r'Interview \d+: ([^-\n]+)(?:\s*-\s*([^\n]+))?',
           r'Persona \d+: ([^-\n]+)(?:\s*-\s*([^\n]+))?'
       ]
       
       for pattern in persona_patterns:
           matches = re.findall(pattern, response)
           for match in matches:
               if isinstance(match, tuple):
                   persona_name = match[0].strip()
                   persona_desc = match[1].strip() if len(match) > 1 and match[1] else ""
                   full_persona = f"{persona_name} - {persona_desc}" if persona_desc else persona_name
               else:
                   full_persona = match.strip()
                   
               if full_persona and len(full_persona) > 5:
                   personas.append(full_persona)
       
       # Fallback to defaults if none found
       if not personas:
           personas = [
               "The Exhausted Achiever - Successful but dying inside",
               "The Skeptical Analyst - Using logic to avoid feeling",
               "The Hopeful Dreamer - Wants change but fears disappointment"
           ]
       
       return personas[:3]
   
   def _extract_breakthrough_moments(self, response: str) -> List[str]:
       """Extract breakthrough moments from interviews"""
       
       moments = []
       
       # Patterns that indicate breakthroughs
       breakthrough_patterns = [
           r'([^.!?]*(?:just realized|never thought|oh my god|holy shit|wait)[^.!?]*[.!?])',
           r'([^.!?]*\*breakthrough\*[^.!?]*[.!?])',
           r'Customer: ([^.!?]*(?:I never|I just|Oh god)[^.!?]*[.!?])'
       ]
       
       for pattern in breakthrough_patterns:
           found = re.findall(pattern, response, re.IGNORECASE)
           moments.extend(found)
       
       # Clean and deduplicate
       cleaned_moments = []
       seen = set()
       
       for moment in moments:
           clean = moment.strip()
           if clean not in seen and 20 < len(clean) < 200:
               seen.add(clean)
               cleaned_moments.append(clean)
       
       return cleaned_moments[:3]


# For testing
if __name__ == "__main__":
   agent = PsychologicalInterviewAgentV4()
   
   test_state = {
       "business_context": "Executive coaches for burned-out tech founders transitioning to CEO role",
       "master_context": "Executive coaches for burned-out tech founders transitioning to CEO role",
       "current_task": {
           "description": "Create psychological interviews revealing deep customer truths",
           "is_high_stakes": False
       },
       "shared_insights": {},
       "memory_service": None,
       "tool_executor": None,
       "client_id": "test_interview_v4"
   }
   
   result = agent(test_state)
   print(f"\nOutput preview: {result.get('current_output', 'No output')[:500]}...")
   print(f"Quality Score: {result.get('quality_score', 0)}")
   print(f"Needs Review: {result.get('requires_human_review', False)}")
