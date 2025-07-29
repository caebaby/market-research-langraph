# team_icp/agents/voice_v4.py

from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
import json
import logging
from core.standard_agent_v4 import StandardAgentNodeV4
from team_icp.prompts.voice_prompts import VoicePrompts

logger = logging.getLogger(__name__)

class VoiceAgentV4(StandardAgentNodeV4):
    """Voice of Customer Agent - Level 4 Implementation
    
    Achieves 'journal-level' accuracy in extracting customer language.
    Creates copy-ready phrases that feel uncomfortably accurate.
    """
    
    def __init__(self):
        super().__init__(
            agent_name="Voice of Customer Specialist",
            role_prompt=VoicePrompts.get_role_prompt()
        )
    
    async def execute_core_analysis(self, state: Dict[str, Any]) -> str:
        """Extract voice of customer with journal-level accuracy"""
        try:
            # Extract business context
            business_context = self._extract_business_context()  # No parameters
            
            # Get shared insights from other agents
            psychological_insights = self._get_shared_insight(state, "psychological")
            competitor_insights = self._get_shared_insight(state, "competitor")
            
            # Generate language hypothesis first
            hypothesis = await self._generate_language_hypothesis(business_context)
            
            # Create comprehensive voice bible
            voice_bible = await self._create_voice_bible(
                business_context=business_context,
                hypothesis=hypothesis,
                psychological_insights=psychological_insights,
                competitor_insights=competitor_insights
            )
            
            # Extract and share key patterns
            patterns = self._extract_key_patterns(voice_bible)
            self._share_insight(state, "voice", {
                "summary": f"Extracted {len(patterns)} authentic language patterns",
                "patterns": patterns,
                "golden_phrase": self._extract_golden_phrase(voice_bible),
                "quality_score": state.get("quality_score", 0.0)
            })
            
            return voice_bible
            
        except Exception as e:
            logger.error(f"Voice analysis error: {str(e)}")
            return self._generate_error_response(str(e))
    
    async def _generate_language_hypothesis(self, business_context: str) -> str:
        """Generate AI hypothesis of customer language"""
        prompt = VoicePrompts.get_language_hypothesis_prompt().format(
            business_context=business_context
        )
        
        llm = self.llm
        result = await llm.ainvoke(prompt)  # FIXED: Changed from synthesis_prompt to prompt
        return result.content

    async def _create_voice_bible(self, business_context: str, hypothesis: str,
                                  psychological_insights: Dict, competitor_insights: Dict) -> str:
        """Create comprehensive voice of customer bible"""
        
        # Format psychological profile
        psych_profile = psychological_insights.get("summary", "Not available yet") if psychological_insights else "Analysis pending"
        
        # Format competitor insights  
        comp_context = competitor_insights.get("summary", "Not available yet") if competitor_insights else "Analysis pending"
        
        # Create synthesis prompt
        synthesis_prompt = VoicePrompts.get_synthesis_template().format(
            business_context=business_context,
            psychological_profile=psych_profile,
            language_hypothesis=hypothesis,
            validation_data="AI-Inferred (real-world validation available in future updates)",
            competitor_insights=comp_context
        )
        
        llm = self.llm
        result = await llm.ainvoke(synthesis_prompt)
        return result.content
    
    def _extract_key_patterns(self, voice_bible: str) -> Dict[str, List[str]]:
        """Extract structured patterns from voice bible"""
        patterns = {
            "frustration_language": [],
            "aspiration_language": [],
            "investment_language": [],
            "inner_monologue": [],
            "objection_language": []
        }
        
        # Simple extraction based on sections
        # In production, this would use more sophisticated parsing
        sections = voice_bible.split("###")
        
        for section in sections:
            if "frustrated with" in section.lower():
                # Extract frustration patterns
                lines = section.split("\n")
                for line in lines:
                    if "→" in line and "frustrated" in line.lower():
                        patterns["frustration_language"].append(line.strip())
            
            elif "looking for" in section.lower():
                # Extract aspiration patterns
                lines = section.split("\n")
                for line in lines:
                    if "→" in line and any(word in line.lower() for word in ["looking", "need", "want"]):
                        patterns["aspiration_language"].append(line.strip())
            
            elif "ready to invest" in section.lower():
                # Extract investment patterns
                lines = section.split("\n")
                for line in lines:
                    if "→" in line and any(word in line.lower() for word in ["invest", "pay", "worth"]):
                        patterns["investment_language"].append(line.strip())
        
        return patterns
    
    def _extract_golden_phrase(self, voice_bible: str) -> str:
        """Extract the golden phrase from voice bible"""
        # Look for the golden phrase section
        if "💎 The Golden Phrase" in voice_bible:
            start = voice_bible.find("💎 The Golden Phrase")
            section = voice_bible[start:start+500]
            lines = section.split("\n")
            for line in lines:
                if line.strip().startswith('"') and line.strip().endswith('"'):
                    return line.strip()
        
        return "Golden phrase extraction pending"
    
    async def reflect_on_output(self, output: str) -> Tuple[float, str]:
        """Evaluate voice analysis quality"""
        reflection_prompt = f"""{VoicePrompts.get_reflection_criteria()}
        
        Analysis to evaluate:
        {output[:2000]}...
        
        Provide numerical scores for each criterion and calculate total."""
        
        try:
            llm = self.llm  
            result = await llm.ainvoke(reflection_prompt)
            
            # Extract score (simple parsing - could be more robust)
            score = 0.75  # Default
            if "total:" in result.content.lower():
                parts = result.content.lower().split("total:")
                if len(parts) > 1:
                    try:
                        score = float(parts[1].split()[0].strip())
                    except:
                        pass
            
            return min(max(score, 0.0), 1.0), result.content
            
        except Exception as e:
            logger.error(f"Reflection error: {str(e)}")
            return 0.7, "Voice analysis complete but quality reflection failed"
    
    def _generate_error_response(self, error: str) -> str:
        """Generate a helpful error response"""
        return f"""Voice of Customer Analysis Error:
        
{error}

The Voice specialist was unable to extract authentic customer language. 
This typically happens when:
1. Business context is too vague
2. ICP is not clearly defined
3. Technical issues with analysis

Please provide more specific business context or try again."""
    
    def _get_shared_insight(self, state: Dict[str, Any], agent_name: str) -> Optional[Dict]:
        """Get insights from another agent"""
        shared_insights = state.get("shared_insights", {})
        return shared_insights.get(agent_name)
    
    def _share_insight(self, state: Dict[str, Any], agent_name: str, insight: Dict):
        """Share insights with other agents"""
        if "shared_insights" not in state:
            state["shared_insights"] = {}
        state["shared_insights"][agent_name] = insight

    def _generate_response(self, task: str, context: str, memories: List, llm) -> str:
        """Generate response matching base class signature"""
        # Store context in state for execute_core_analysis to use
        self.state["business_context"] = context
    
        # For now, run synchronously (we'll handle async later)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.execute_core_analysis(self.state))
        loop.close()
    
        return result

    def _reflect(self, task: str, response: str, llm) -> Dict[str, Any]:
        """Reflect on quality matching base class signature"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        score, critique = loop.run_until_complete(self.reflect_on_output(response))
        loop.close()
    
        return {
            "score": score,
            "critique": critique
        }

    def _extract_insights_for_memory(self, response: str) -> Dict[str, Any]:
        """Extract insights matching base class signature"""
        patterns = self._extract_key_patterns(response)
        return {
            "patterns": patterns,
            "golden_phrase": self._extract_golden_phrase(response),
            "timestamp": datetime.now().isoformat()
        }

    def _create_shared_insights(self, response: str, quality: float) -> Dict[str, Any]:
        """Create insights matching base class signature"""
        patterns = self._extract_key_patterns(response)
        return {
            "summary": f"Extracted {len(patterns)} authentic language patterns",
            "patterns": patterns,
            "golden_phrase": self._extract_golden_phrase(response),
            "quality_score": quality
        }

# Create instance for use in graph
voice_agent_v4 = VoiceAgentV4()
