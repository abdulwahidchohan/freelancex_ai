from core.base_agent import BaseAgent

# Monitors health
class WellnessMonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__("WellnessMonitorAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.check()

    def check(self):
        pass
