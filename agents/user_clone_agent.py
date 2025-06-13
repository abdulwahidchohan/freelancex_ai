from core.base_agent import BaseAgent

# Clones user's tone
class UserCloneAgent(BaseAgent):
    def __init__(self):
        super().__init__("UserCloneAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.mimic()

    def mimic(self):
        pass
