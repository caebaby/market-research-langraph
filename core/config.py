# core/config.py
"""
Configuration module for Level 5 ICP Intelligence System.
Provides agent-specific LLM configurations, temperatures, and token limits.
UPDATED: Using Claude Sonnet 4.5 at temperature 0.3
"""

from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    """
    Central configuration for all agents and system components.
    Provides agent-specific configurations for optimal performance.
    """
    
    # Model configuration - UPDATED to Sonnet 4.5
    LLM_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
    
    # UPDATED: All agents now use temperature 0.3 for consistent, focused responses
    AGENT_TEMPERATURES = {
        'psychological': 0.3,           # Focused for reliable insights
        'voice_of_customer': 0.3,       # Consistent language extraction
        'competitor': 0.3,              # Precise competitive analysis
        'interview_psychological': 0.3,  # Structured, consistent interviews
        'interview_sales': 0.3,         # Focused sales conversations
        'gtm_blueprint': 0.3,           # Precise strategy synthesis
        'gtm': 0.3,                     # Alias for gtm_blueprint
        'voice': 0.3                    # Alias for voice_of_customer
    }
    
    # Token limits by use case - UPDATED to 20k max
    MAX_TOKENS = {
        'research': 20000,   # Maximum for deep analysis
        'creative': 20000,   # Maximum for interviews
        'summary': 10000,    # Medium for summaries (half of max)
        'quick': 5000        # Quick responses (quarter of max)
    }
    
    # UPDATED: Default temperature now 0.3
    DEFAULT_TEMPERATURE = 0.3
    
    # Quality thresholds for each agent (unchanged)
    QUALITY_THRESHOLDS = {
        'interview_psychological': 0.80,
        'interview_sales': 0.80,
        'voice_of_customer': 0.75,
        'psychological': 0.75,
        'competitor': 0.70,
        'gtm_blueprint': 0.90,
        'gtm': 0.90,
        'voice': 0.75
    }
    
    # Minimum word counts for validation (unchanged)
    MIN_WORD_COUNTS = {
        'interview_psychological': 2000,
        'interview_sales': 2000,
        'voice_of_customer': 1500,
        'psychological': 1200,
        'competitor': 1000,
        'gtm_blueprint': 2500,
        'gtm': 2500,
        'voice': 1500
    }
    
    # Agent type categorization (unchanged)
    AGENT_TYPES = {
        'analytical': ['psychological', 'competitor'],
        'creative': ['interview_psychological', 'interview_sales'],
        'extraction': ['voice_of_customer', 'voice'],
        'synthesis': ['gtm_blueprint', 'gtm']
    }
    
    @staticmethod
    def get_llm(agent_name: Optional[str] = None, 
                custom_temp: Optional[float] = None,
                custom_tokens: Optional[int] = None) -> ChatAnthropic:
        """
        Get configured LLM instance for specific agent.
        
        Args:
            agent_name: Name of the agent (for agent-specific config)
            custom_temp: Override temperature if needed
            custom_tokens: Override max tokens if needed
            
        Returns:
            Configured ChatAnthropic instance
        """
        # Normalize agent name
        if agent_name:
            agent_name = agent_name.lower().replace('-', '_')
        
        # Get temperature (priority: custom > agent-specific > default)
        # UPDATED: Now defaults to 0.3
        if custom_temp is not None:
            temperature = custom_temp
            print(f"Using custom temperature: {temperature}")
        elif agent_name and agent_name in Config.AGENT_TEMPERATURES:
            temperature = Config.AGENT_TEMPERATURES[agent_name]
            print(f"Using agent '{agent_name}' temperature: {temperature}")
        else:
            temperature = Config.DEFAULT_TEMPERATURE
            print(f"Using default temperature: {temperature}")
        
        # Get max tokens based on agent type
        if custom_tokens is not None:
            max_tokens = custom_tokens
        elif agent_name:
            # Determine token limit based on agent type
            if 'interview' in agent_name:
                max_tokens = Config.MAX_TOKENS['creative']
            elif agent_name in ['gtm_blueprint', 'gtm']:
                max_tokens = Config.MAX_TOKENS['summary']
            else:
                max_tokens = Config.MAX_TOKENS['research']
        else:
            max_tokens = Config.MAX_TOKENS['research']
        
        # Get API key with multiple fallbacks
        api_key = (
            os.getenv("ANTHROPIC_API_KEY") or 
            os.getenv("CLAUDE_API_KEY") or
            os.getenv("level5-team-icp-claude")
        )
        
        if not api_key:
            raise ValueError(
                "Claude API key not found!\n"
                "Please set one of these environment variables:\n"
                "- ANTHROPIC_API_KEY (recommended)\n"
                "- CLAUDE_API_KEY\n"
                "- level5-team-icp-claude"
            )
        
        # Log configuration (useful for debugging)
        logger.info(
            f"Creating LLM for agent '{agent_name}': "
            f"temp={temperature}, tokens={max_tokens}, model={Config.LLM_MODEL}"
        )
        
        # Add warning if using high token count
        if max_tokens > 10000:
            print(f"⚡ Using high token limit: {max_tokens} tokens for {agent_name or 'default'} agent")
        
        try:
            # Create and return configured LLM
            llm = ChatAnthropic(
                model=Config.LLM_MODEL,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key
            )
            print(f"✅ Successfully created LLM with Sonnet 4.5 at temp {temperature}")
            return llm
        except Exception as e:
            print(f"❌ Error creating LLM: {e}")
            raise
    
    @staticmethod
    def get_agent_config(agent_name: str) -> Dict[str, Any]:
        """
        Get complete configuration for an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary with all agent configurations
        """
        agent_name = agent_name.lower().replace('-', '_')
        
        return {
            'temperature': Config.AGENT_TEMPERATURES.get(agent_name, Config.DEFAULT_TEMPERATURE),
            'quality_threshold': Config.QUALITY_THRESHOLDS.get(agent_name, 0.7),
            'min_word_count': Config.MIN_WORD_COUNTS.get(agent_name, 1000),
            'max_tokens': Config._get_tokens_for_agent(agent_name)
        }
    
    @staticmethod
    def _get_tokens_for_agent(agent_name: str) -> int:
        """Helper to determine token limit for agent"""
        if 'interview' in agent_name:
            return Config.MAX_TOKENS['creative']
        elif agent_name in ['gtm_blueprint', 'gtm']:
            return Config.MAX_TOKENS['summary']
        else:
            return Config.MAX_TOKENS['research']
    
    @staticmethod
    def validate_environment() -> bool:
        """
        Validate that all required environment variables are set.
        
        Returns:
            True if all required vars are set, False otherwise
        """
        required_vars = {
            'ANTHROPIC_API_KEY': 'Claude API key',
            'SLACK_BOT_TOKEN': 'Slack bot token (if using Slack)',
            'SLACK_SIGNING_SECRET': 'Slack signing secret (if using Slack)'
        }
        
        missing = []
        for var, description in required_vars.items():
            if not os.getenv(var):
                # Only required if using Slack
                if 'SLACK' in var and not os.getenv('USE_SLACK'):
                    continue
                missing.append(f"- {var}: {description}")
        
        if missing:
            logger.warning(
                "Missing environment variables:\n" + "\n".join(missing)
            )
            return False
        
        return True
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get system configuration information.
        
        Returns:
            Dictionary with system configuration details
        """
        return {
            'model': Config.LLM_MODEL,
            'model_version': 'Claude 3.5 Sonnet 4 (Latest)',
            'default_temperature': Config.DEFAULT_TEMPERATURE,
            'agents_configured': len(Config.AGENT_TEMPERATURES),
            'temperature_range': f"{min(Config.AGENT_TEMPERATURES.values()):.1f}-{max(Config.AGENT_TEMPERATURES.values()):.1f}",
            'max_tokens_range': f"{min(Config.MAX_TOKENS.values())}-{max(Config.MAX_TOKENS.values())}",
            'environment_valid': Config.validate_environment()
        }

# Initialize and validate on module load
if __name__ == "__main__":
    # Test configuration
    print("=" * 60)
    print("CONFIGURATION TEST - SONNET 4.5 @ TEMP 0.3")
    print("=" * 60)
    
    # Validate environment
    if Config.validate_environment():
        print("✅ Environment validation passed")
    else:
        print("⚠️ Some environment variables are missing")
    
    # Show system info
    info = Config.get_system_info()
    print(f"\nSystem Configuration:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test LLM creation for each agent
    print(f"\nTesting LLM creation for all agents:")
    print(f"NOTE: All agents now configured with 20k max tokens")
    for agent_name in Config.AGENT_TEMPERATURES.keys():
        try:
            llm = Config.get_llm(agent_name)
            config = Config.get_agent_config(agent_name)
            print(f"  ✅ {agent_name}: temp={config['temperature']}, tokens={config['max_tokens']}")
        except Exception as e:
            print(f"  ❌ {agent_name}: {e}")
    
    print("=" * 60)

# End of config.py