from core.base_agent import BaseAgent

# Automates passive gigs
class PassiveIncomeAgent(BaseAgent):
    def __init__(self):
        super().__init__("PassiveIncomeAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.automate()

    def automate(self):
        pass
