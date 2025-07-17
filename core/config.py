from langchain_anthropic import ChatAnthropic
import os

class Config:
    LLM_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    TEMP = 0.85  # Deep insights

    @staticmethod
    def get_llm():
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("Add ANTHROPIC_API_KEY to Railway env")
        return ChatAnthropic(model=Config.LLM_MODEL, temperature=Config.TEMP, max_tokens=8000, api_key=key)
