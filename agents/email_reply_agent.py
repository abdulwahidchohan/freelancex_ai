from core.base_agent import BaseAgent

# Replies to emails
class EmailReplyAgent(BaseAgent):
    def __init__(self):
        super().__init__("EmailReplyAgent")

    def run(self):
        print(f'{self.agent_name} online.')
        print(f"System Prompt loaded: {self.system_prompt[:50]}...") # For verification
        self.reply()

    def reply(self):
        pass
