from core.base_agent import BaseAgent

# Handles invoices & taxes
class InvoiceTaxAgent(BaseAgent):
    def __init__(self):
        super().__init__("InvoiceTaxAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.process()

    def process(self):
        pass
