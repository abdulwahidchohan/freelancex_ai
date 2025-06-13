from core.base_agent import BaseAgent

# Learns from failures
class FeedbackLoopAgent(BaseAgent):
    def __init__(self):
        super().__init__("FeedbackLoopAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.update()

    def update(self):
        pass
