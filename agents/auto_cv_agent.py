from core.base_agent import BaseAgent

# Updates resume
class AutoCVAgent(BaseAgent):
    def __init__(self):
        super().__init__("AutoCVAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.refresh()

    def refresh(self):
        pass
