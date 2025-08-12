#!/usr/bin/env python3
"""
Simple Chainlit test to verify message handling
"""

import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    """Initialize chat session"""
    await cl.Message(
        content="🚀 **Test Chat Started!**\n\nThis is a simple test to verify Chainlit is working properly. Try sending any message!",
        author="Test System"
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Handle incoming messages"""
    try:
        # Simple echo response
        response = f"✅ **Test Response:** You said: '{message.content}'\n\nThis confirms that Chainlit message handling is working correctly!"
        
        await cl.Message(
            content=response,
            author="Test Assistant"
        ).send()
        
        print(f"Test message processed: {message.content}")
        
    except Exception as e:
        print(f"Test error: {str(e)}")
        await cl.Message(
            content=f"❌ **Test Error:** {str(e)}",
            author="Test System"
        ).send()

if __name__ == "__main__":
    print("Starting Chainlit test application...")
