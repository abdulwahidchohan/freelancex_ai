from core.base_agent import BaseAgent

# Creates podcast content
class PodcastBotAgent(BaseAgent):
    def __init__(self):
        super().__init__("PodcastBotAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.generate()

    def generate(self):
        pass
