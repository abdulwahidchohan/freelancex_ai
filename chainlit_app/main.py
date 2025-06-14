# Main application
import chainlit as cl
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.executive_agent import ExecutiveAgent
from typing import Optional
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize executive agent
executive_agent = ExecutiveAgent()

@cl.on_chat_start
async def start_chat():
    """Initialize chat session and send welcome message"""
    try:
        # Set initial chat settings
        await cl.ChatSettings(
            initial_settings={"conversation_started": True}
        ).send()
        
        # Send welcome message with markdown formatting
        welcome_message = """
        # 👋 Welcome to FreelanceX AI!
        
        I'm here to assist you with your freelancing needs.
        How can I help you today?
        """
        await cl.Message(content=welcome_message).send()
        
    except Exception as e:
        logger.error(f"Error in chat initialization: {str(e)}")
        await cl.Message(content="Sorry, there was an error starting the chat. Please try again.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages and generate responses"""
    try:
        # Show typing indicator while processing
        async with cl.Step("Processing your request...") as step:
            # Get response from executive agent
            response = await executive_agent.handle_message(message.content)
            
            # Send response with error handling
            if response:
                await cl.Message(content=response).send()
            else:
                step.error("Empty response received from agent")
                raise ValueError("Empty response received from agent")
                
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        error_message = "I apologize, but I encountered an error processing your request. Please try again."
        await cl.Message(content=error_message).send()
