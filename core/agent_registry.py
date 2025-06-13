import json

# Registry of all agents
AGENTS = {}
SYSTEM_PROMPT = ""

def _load_system_prompt_for_registry():
    global SYSTEM_PROMPT
    try:
        with open('config/system_prompt.json', 'r') as f:
            config = json.load(f)
            SYSTEM_PROMPT = config.get('SYSTEM_PROMPT', '')
    except FileNotFoundError:
        print("Error: system_prompt.json not found in config directory for agent registry.")
    except json.JSONDecodeError:
        print("Error: Could not decode system_prompt.json for agent registry. Check JSON format.")

_load_system_prompt_for_registry() # Load prompt on module import
