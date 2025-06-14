# Registry of all agents
import yaml
import os
from typing import Any, Dict
from pathlib import Path
# Load SYSTEM_PROMPT from a configuration file
def load_system_prompt() -> str:
    config_path = Path('config/system_prompts.yaml')
    try:
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}")
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Invalid YAML format - expected dictionary")
            return config.get('system_prompt', '')
    except Exception as e:
        print(f"Error loading system prompt: {str(e)}")
        return ''

SYSTEM_PROMPT = load_system_prompt()

# Dictionary to store registered agents
AGENTS: Dict[str, Any] = {}

def register_agent(name: str, agent_instance: Any) -> None:
    """
    Register a new agent in the global AGENTS dictionary.
    
    Args:
        name: Unique identifier for the agent
        agent_instance: The agent object to register
        
    Raises:
        ValueError: If agent name already exists
    """
    if name in AGENTS:
        raise ValueError(f"Agent '{name}' already registered")
    
    AGENTS[name] = agent_instance
    print(f"Agent '{name}' registered successfully")
