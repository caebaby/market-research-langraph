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
from team_icp.prompts.interview_prompts import InterviewPrompts


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
            role_prompt="""You are an expert at conducting psychological depth interviews 
            that reveal hidden customer truths. You create unnervingly realistic conversations 
            where defense mechanisms drop and authentic pain emerges. Your interviews feel like 
            actual customer research sessions, not scripted dialogues.""",
            target_quality=0.85,
            require_human_review_below=0.7,
            enable_web_search=True
        )
        self.can_work_independently = True
        
    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate psychological interview simulations"""
        
        # Check if we need to gather context first
        if self._should_gather_context(task, context):
            return json.dumps({
                "tool": "web_search",
                "query": f"{context} customer challenges pain points testimonials"
            })
        
        # Extract psychological insights if available
        psychological_insights = self._extract_psychological_insights(context)
        business_context = self._extract_business_context()
        
        # Get relevant memories
        interview_patterns = self._format_interview_memories(memories, psychological_insights)
        
        # Get the appropriate prompt
        if psychological_insights:
            print(f"[{self.agent_name}] Using psychological insights for interviews")
            interview_prompt = InterviewPrompts.get_psychological_interviews(
                psychological_analysis=psychological_insights
            )
        else:
            print(f"[{self.agent_name}] Creating independent interviews from business context")
            interview_prompt = InterviewPrompts.get_psychological_interviews(
                business_context=business_context
            )
        
        # Enhance with memory patterns
        if interview_patterns:
            interview_prompt += f"\n\n{interview_patterns}"
        
        # Check if we should validate specific phrases
        if "validate" in task.lower() and self.enable_web_search:
            # Generate initial response
            initial_response = llm.invoke(interview_prompt).content
            
            # Look for a phrase to validate
            validation_phrase = self._extract_validation_candidate(initial_response)
            if validation_phrase:
                print(f"[{self.agent_name}] Validating phrase: {validation_phrase}")
                return json.dumps({
                    "tool": "web_search",
                    "query": f'"{validation_phrase}" customer interview'
                })
            
            return initial_response
        
        print(f"[{self.agent_name}] Creating 3 psychological depth interviews...")
        
        # Generate interviews
        response = llm.invoke(interview_prompt)
        return response.content if hasattr(response, 'content') else str(response)
    
    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Evaluate interview quality with robust parsing"""
        
        reflection_prompt = InterviewPrompts.get_interview_reflection_prompt()
        reflection_prompt += f"\n\nINTERVIEWS TO EVALUATE:\n{response[:4000]}..."
        
        reflection_result = llm.invoke(reflection_prompt).content
        
        # Parse score with multiple patterns
        score = None
        critique = reflection_result
        
        score_patterns = [
            r'OVERALL_SCORE:\s*([0-9.]+)',
            r'Overall Score:\s*([0-9.]+)',
            r'Score:\s*([0-9.]+)',
            r'Final Score:\s*([0-9.]+)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, reflection_result, re.MULTILINE | re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    score = max(0.0, min(1.0, score))
                    critique = reflection_result.replace(match.group(0), '').strip()
                    break
                except ValueError:
                    continue
        
        # Intelligent defaulting based on content
        if score is None:
            if any(word in reflection_result.lower() for word in 
                   ["excellent", "outstanding", "masterful", "powerful"]):
                score = 0.88
            elif any(word in reflection_result.lower() for word in 
                     ["poor", "weak", "unrealistic", "shallow"]):
                score = 0.55
            else:
                score = 0.75
            
            critique += "\n⚠️ Score parsing failed - inferred from content"
        
        # Quality indicators check
        quality_indicators = self._check_quality_indicators(response)
        
        # Adjust score based on objective checks
        adjustment = 1.0
        if not quality_indicators["has_3_interviews"]:
            adjustment *= 0.8
            critique += "\n⚠️ Missing complete interviews"
            
        if not quality_indicators["has_timestamps"]:
            adjustment *= 0.95
            critique += "\n⚠️ Missing timestamp progression"
            
        if not quality_indicators["has_authentic_speech"]:
            adjustment *= 0.9
            critique += "\n⚠️ Dialogue needs more authenticity markers"
        
        score = score * adjustment
        
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
            "resistance_patterns": [],
            "psychological_patterns": [],
            "authenticity_markers": [],
            "client_context": self.state.get("client_id", "unknown")
        }
        
        # Extract interviewing techniques
        if "[reframes" in response.lower() or "reframing" in response.lower():
            insights["interview_techniques"].append("Reframing questions unlock new perspectives")
            
        if "[silence]" in response.lower() or "[long pause]" in response.lower():
            insights["interview_techniques"].append("Strategic silence creates breakthrough space")
        
        # Extract effective questions
        questions = re.findall(r'Interviewer: ([^?]+\?)', response)
        powerful_questions = [q for q in questions if any(word in q.lower() for word in 
                             ["feel", "mean", "fear", "want", "wish", "imagine"])]
        if powerful_questions:
            insights["effective_questions"].extend(powerful_questions[:3])
        
        # Extract breakthrough patterns
        if "oh my god" in response.lower() or "holy shit" in response.lower():
            insights["breakthrough_moments"].append("Profanity indicates emotional breakthrough")
            
        if "never realized" in response.lower() or "just hit me" in response.lower():
            insights["breakthrough_moments"].append("Sudden realization pattern effective")
        
        # Extract authenticity markers
        authenticity_phrases = [
            "i guess", "i mean", "sort of", "kind of", "honestly", 
            "look,", "well,", "actually", "..."
        ]
        found_markers = [marker for marker in authenticity_phrases if marker in response.lower()]
        if found_markers:
            insights["authenticity_markers"] = found_markers
        
        # Extract psychological patterns
        if "exhaust" in response.lower():
            insights["psychological_patterns"].append("Exhaustion theme resonates deeply")
            
        if "identity" in response.lower() and ("crisis" in response.lower() or "lost" in response.lower()):
            insights["psychological_patterns"].append("Identity crisis central to customer psychology")
        
        return insights
    
    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights to share with other agents"""
        
        # Extract key findings
        key_findings = []
        
        # Pattern detection across interviews
        patterns = {
            "identity_crisis": response.lower().count("identity") + response.lower().count("who i am"),
            "exhaustion": response.lower().count("exhaust") + response.lower().count("tired"),
            "fear": response.lower().count("afraid") + response.lower().count("scar") + response.lower().count("terrif"),
            "hope": response.lower().count("hope") + response.lower().count("dream") + response.lower().count("wish")
        }
        
        # Top patterns become findings
        top_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        for pattern, count in top_patterns:
            if count > 2:  # Appears multiple times across interviews
                key_findings.append(f"{pattern.replace('_', ' ').title()} theme appears across personas")
        
        # Extract powerful quotes
        quotes = []
        quote_patterns = [
            r'"([^"]{20,100})"',  # Direct quotes 20-100 chars
            r"'([^']{20,100})'"   # Single quotes too
        ]
        
        for pattern in quote_patterns:
            found_quotes = re.findall(pattern, response)
            # Filter for emotional quotes
            emotional_quotes = [q for q in found_quotes if any(word in q.lower() for word in 
                               ["feel", "afraid", "wish", "tired", "lost", "need", "can't"])]
            quotes.extend(emotional_quotes)
        
        # Deduplicate and limit
        quotes = list(set(quotes))[:5]
        
        return {
            "summary": f"Conducted 3 psychological depth interviews with quality score {quality:.2f}. "
                      f"Revealed core patterns: {', '.join([p[0].replace('_', ' ') for p in top_patterns[:2]])}. "
                      f"Interviews show authentic progression from resistance to breakthrough.",
            "key_findings": key_findings,
            "powerful_quotes": quotes[:3],
            "interview_personas": [
                "Exhausted Achiever - successful but dying inside",
                "Skeptical Analyst - using logic to avoid feeling", 
                "Hopeful Dreamer - wants change but fears disappointment"
            ],
            "breakthrough_moments": self._extract_breakthrough_moments(response),
            "quality_score": quality,
            "timestamp": datetime.now().isoformat(),
            "client_id": self.state.get("client_id", "unknown")
        }
    
    def handle_coaching(self, coaching_text: str, improvement_areas: List[str]) -> Dict[str, Any]:
        """Enhanced coaching that uses specific improvement areas"""
        
        # Call parent implementation first
        result = super().handle_coaching(coaching_text, improvement_areas)
        
        if result.get("status") == "success" and self.state:
            # Create targeted improvement prompt
            current_output = self.state.get("current_output", "")
            
            area_prompts = {
                "authenticity": "Add more natural speech patterns, stutters, and self-corrections",
                "depth": "Probe deeper into emotional layers, reach core wounds",
                "breakthrough": "Create more powerful 'aha' moments",
                "resistance": "Show more realistic defense mechanisms",
                "technique": "Improve interviewer's skill in handling difficult moments"
            }
            
            improvement_instructions = []
            for area in improvement_areas:
                for key, instruction in area_prompts.items():
                    if key in area.lower():
                        improvement_instructions.append(instruction)
            
            if improvement_instructions:
                coaching_prompt = f"""
Apply this coaching to improve your interviews:

ORIGINAL INTERVIEWS:
{current_output[:2000]}...

COACHING FEEDBACK: {coaching_text}

SPECIFIC IMPROVEMENTS NEEDED:
{chr(10).join(f"- {inst}" for inst in improvement_instructions)}

Generate improved versions focusing on these specific areas.
"""
                
                improved = self.llm.invoke(coaching_prompt).content
                result["improved_response"] = improved
                
                # Store area-specific improvements
                if self.memory:
                    for area in improvement_areas:
                        self.memory.store(
                            agent_name=self.agent_name,
                            context=f"coaching_improvement_{area}",
                            insights={
                                "area": area,
                                "technique": improvement_instructions,
                                "example": self._extract_improvement_example(improved, area)
                            },
                            quality=1.0,
                            client_id=self.state.get("client_id")
                        )
        
        return result
    
    # Helper methods
    
    def _should_gather_context(self, task: str, context: str) -> bool:
        """Determine if we need more context via web search"""
        
        # If context is too short
        if len(context) < 200:
            return True
            
        # If task requests research
        if any(word in task.lower() for word in ["research", "find", "gather", "discover"]):
            return True
            
        # If no business context or psychological insights
        if not self._extract_business_context() and not self._extract_psychological_insights(context):
            return True
            
        return False
    
    def _extract_psychological_insights(self, context: str) -> str:
        """Extract psychological analysis from context/shared insights"""
        
        # Check shared insights first
        if "INSIGHTS FROM OTHER AGENTS:" in context:
            parts = context.split("INSIGHTS FROM OTHER AGENTS:")
            if len(parts) > 1:
                insights_section = parts[1]
                
                # Look for psychological agent's output
                for marker in ["psychological:", "Psychological:", "Psychological Specialist:"]:
                    if marker in insights_section:
                        start = insights_section.find(marker)
                        section = insights_section[start:]
                        
                        # Find end of this agent's section
                        end_markers = ["\n\n", "voice:", "Voice:", "competitor:", "Competitor:"]
                        end = len(section)
                        for end_marker in end_markers:
                            pos = section.find(end_marker)
                            if pos > 0 and pos < end:
                                end = pos
                        
                        return section[:end]
        
        # Fallback: look for psychological content
        if len(context) > 500 and any(word in context.lower() for word in 
            ["identity", "fear", "desire", "unconscious", "archetype", "shadow"]):
            return context
            
        return ""
    
    def _extract_business_context(self) -> str:
        """Extract clean business context"""
        
        if not self.state:
            return ""
            
        # Get base context
        context = self.state.get("business_context") or self.state.get("master_context") or ""
        
        # Don't include shared insights in business context
        if "INSIGHTS FROM OTHER AGENTS:" in context:
            context = context.split("INSIGHTS FROM OTHER AGENTS:")[0].strip()
            
        return context
    
    def _check_quality_indicators(self, response: str) -> Dict[str, bool]:
        """Check objective quality indicators"""
        
        return {
            "has_3_interviews": response.count("INTERVIEW") >= 3,
            "has_timestamps": bool(re.search(r'\[\d+:\d+\]', response)),
            "has_authentic_speech": any(marker in response.lower() for marker in 
                ["i guess", "i mean", "...", "um", "uh", "[pause]", "[sighs]"]),
            "has_emotional_depth": any(word in response.lower() for word in 
                ["terrified", "exhausted", "desperate", "ashamed", "lost", "trapped"]),
            "has_breakthrough": any(phrase in response.lower() for phrase in 
                ["oh my god", "just realized", "never thought", "holy shit", "wait,"]),
            "sufficient_length": len(response) > 5000,
            "has_interviewer_technique": any(technique in response.lower() for technique in 
                ["reframe", "reflect", "validate", "permission", "normalize"])
        }
    
    def _extract_validation_candidate(self, response: str) -> Optional[str]:
        """Extract a customer phrase worth validating"""
        
        # Look for emotional customer quotes
        quotes = re.findall(r'Customer: "([^"]+)"', response)
        
        for quote in quotes:
            # Find quotes with strong emotional language
            if len(quote) > 30 and any(word in quote.lower() for word in 
                ["exhausted", "terrified", "desperate", "can't", "drowning", "trapped"]):
                return quote
                
        return None
    
    def _format_interview_memories(self, memories: List, psychological_insights: str) -> str:
        """Format relevant memories for interview generation"""
        
        if not memories:
            return ""
        
        # Score memories by relevance
        scored_memories = []
        
        keywords = {
            "interview": 3.0,
            "conversation": 2.5,
            "dialogue": 2.5,
            "breakthrough": 3.0,
            "authentic": 2.0,
            "resistance": 2.0,
            "technique": 2.0,
            "question": 1.5
        }
        
        for memory in memories:
            score = 0.0
            content = str(memory).lower()
            
            # Keyword scoring
            for keyword, weight in keywords.items():
                if keyword in content:
                    score += weight
            
            # Client match bonus
            if memory.get("client_id") == self.state.get("client_id"):
                score *= 1.5
                
            # Psychological relevance bonus
            if psychological_insights and any(concept in content for concept in 
                ["identity", "fear", "exhaust"] if concept in psychological_insights.lower()):
                score *= 1.3
                
            scored_memories.append((score, memory))
        
        # Sort and filter
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        relevant_memories = [m for s, m in scored_memories[:5] if s > 2.0]
        
        if not relevant_memories:
            return ""
        
        # Format for use
        formatted = "\nPROVEN INTERVIEW PATTERNS FROM MEMORY:\n\n"
        
        for memory in relevant_memories:
            insights = memory.get("insights", {})
            
            if insights.get("effective_questions"):
                formatted += "Effective Questions:\n"
                for q in insights["effective_questions"][:2]:
                    formatted += f"- {q}\n"
                    
            if insights.get("breakthrough_moments"):
                formatted += "\nBreakthrough Triggers:\n"
                for b in insights["breakthrough_moments"][:2]:
                    formatted += f"- {b}\n"
                    
            if insights.get("authenticity_markers"):
                formatted += f"\nAuthenticity Markers: {', '.join(insights['authenticity_markers'][:5])}\n"
        
        formatted += "\nApply these patterns while maintaining natural conversation flow.\n"
        
        return formatted
    
    def _extract_breakthrough_moments(self, response: str) -> List[str]:
        """Extract breakthrough moments from interviews"""
        
        moments = []
        
        # Look for breakthrough indicators
        breakthrough_patterns = [
            r"(Customer: .*?(?:just realized|never thought|oh my god|holy shit|wait,)[^.!?]*[.!?])",
            r"(\[.*?breakthrough.*?\][^.!?]*[.!?])",
            r"(Customer: .*?I've never admitted[^.!?]*[.!?])"
        ]
        
        for pattern in breakthrough_patterns:
            found = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
            moments.extend(found)
        
        # Clean and deduplicate
        moments = list(set([m.strip() for m in moments]))[:3]
        
        return moments
    
    def _extract_improvement_example(self, improved_text: str, area: str) -> str:
        """Extract example of improvement for specific area"""
        
        if "authenticity" in area.lower():
            # Find authentic speech marker
            match = re.search(r'(.*?(?:I guess|I mean|honestly|look,).*?)(?:\.|!|\?)', improved_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        elif "depth" in area.lower():
            # Find emotional depth
            match = re.search(r'(.*?(?:terrified|exhausted|desperate|ashamed).*?)(?:\.|!|\?)', improved_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
                
        return "Improvement applied throughout interviews"


# For testing
if __name__ == "__main__":
    agent = PsychologicalInterviewAgentV4()
    
    # Test with minimal context
    test_state = {
        "business_context": "AI coaching platform for burned out executive coaches",
        "master_context": "AI coaching platform for burned out executive coaches",
        "current_task": {
            "description": "Create psychological interviews revealing deep customer truths",
            "is_high_stakes": False
        },
        "shared_insights": {},
        "memory_service": None,
        "tool_executor": None,
        "client_id": "test_psych_interview"
    }
    
    result = agent(test_state)
    print(f"\nOutput preview: {result.get('current_output', 'No output')[:500]}...")
    print(f"Quality Score: {result.get('quality_score', 0)}")
    print(f"Needs Review: {result.get('requires_human_review', False)}")
