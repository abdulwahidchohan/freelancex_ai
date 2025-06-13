from core.base_agent import BaseAgent

# Lists digital products
class MerchandiseCreatorAgent(BaseAgent):
    def __init__(self):
        super().__init__("MerchandiseCreatorAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.list()

    def list(self):
        pass
