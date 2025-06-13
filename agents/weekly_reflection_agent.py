from core.base_agent import BaseAgent

# Weekly summary
class WeeklyReflectionAgent(BaseAgent):
    def __init__(self):
        super().__init__("WeeklyReflectionAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.reflect()

    def reflect(self):
        pass
