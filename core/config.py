from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    TEMP = 0.85

    @staticmethod
    def get_llm(agent_name=None):
        # Try standard name first, then custom name
        key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("level5-team-icp-claude")
        
        if not key:
            raise ValueError(
                "Claude API key not found!\n"
                "Add ANTHROPIC_API_KEY to environment"
            )
        return ChatAnthropic(
            model=Config.LLM_MODEL, 
            temperature=Config.TEMP, 
            max_tokens=8192 , 
            api_key=key
        )
