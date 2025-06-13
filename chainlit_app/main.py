# Starts Chainlit app
import chainlit as cl
from core.executive_agent import ExecutiveAgent

@cl.on_chat_start
def start():
    cl.user_session.set("executive_agent", ExecutiveAgent())
    cl.Message(content="Welcome to FreelanceX.AI! How can I assist you today?").send()

@cl.on_message
async def main(message: cl.Message):
    executive_agent = cl.user_session.get("executive_agent")
    response = executive_agent.run()
    await cl.Message(content=response).send()
