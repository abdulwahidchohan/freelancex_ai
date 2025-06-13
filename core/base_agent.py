import json

class BaseAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self):
        try:
            with open('config/system_prompt.json', 'r') as f:
                config = json.load(f)
                return config.get('SYSTEM_PROMPT', '')
        except FileNotFoundError:
            print("Error: system_prompt.json not found in config directory for BaseAgent.")
            return ""
        except json.JSONDecodeError:
            print("Error: Could not decode system_prompt.json for BaseAgent. Check JSON format.")
            return ""

    def run(self):
        raise NotImplementedError("Each agent must implement its own run method.") 