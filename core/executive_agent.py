from .base_agent import BaseAgent

# The CEO Agent - delegates, prioritizes, governs
class ExecutiveAgent(BaseAgent):
    def __init__(self):
        super().__init__("ExecutiveAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # Print first 50 chars for brevity
