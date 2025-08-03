#!/usr/bin/env python3
"""
FreelanceX.AI Chainlit Interface
Simple web interface for interacting with the FreelanceX.AI system
"""

import chainlit as cl
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from main import freelancex_ai

@cl.on_chat_start
async def start_chat():
    """Initialize the chat session"""
    try:
        # Start FreelanceX.AI system
        success = await freelancex_ai.start()
        
        if success:
            await cl.Message(
                content="🚀 **FreelanceX.AI is ready!**\n\nI'm your AI-powered freelancing assistant. I can help you with:\n\n"
                "• **Job Search** - Find freelance opportunities\n"
                "• **Proposal Writing** - Create compelling proposals\n"
                "• **Project Planning** - Plan and schedule projects\n"
                "• **Invoicing** - Generate invoices and track payments\n"
                "• **Client Communication** - Manage client relationships\n"
                "• **Market Research** - Research industry trends\n\n"
                "Just tell me what you need help with!"
            ).send()
        else:
            await cl.Message(
                content="❌ **System Error**\n\nSorry, I couldn't start the FreelanceX.AI system. Please check the logs and try again."
            ).send()
            
    except Exception as e:
        await cl.Message(
            content=f"❌ **Initialization Error**\n\nFailed to start the system: {str(e)}"
        ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle user messages"""
    try:
        # Process the message through FreelanceX.AI
        input_data = {
            'type': 'text',
            'content': message.content,
            'user_id': 'chainlit_user'
        }
        
        # Show typing indicator
        async with cl.Step("Processing your request..."):
            result = await freelancex_ai.process_input(input_data)
        
        if result.get('success'):
            # Format the response
            response_content = result.get('result', {})
            
            if isinstance(response_content, dict):
                # Extract relevant information from the result
                analysis = response_content.get('analysis', {})
                recommendations = response_content.get('recommendations', [])
                next_steps = response_content.get('next_steps', [])
                
                # Build response message
                response = f"**Task Analysis:** {analysis.get('task_type', 'Unknown')}\n"
                response += f"**Confidence:** {analysis.get('confidence', 0):.2f}\n"
                response += f"**Priority:** {analysis.get('priority', 5)}/10\n\n"
                
                if recommendations:
                    response += "**Recommendations:**\n"
                    for rec in recommendations:
                        response += f"• {rec}\n"
                    response += "\n"
                
                if next_steps:
                    response += "**Next Steps:**\n"
                    for step in next_steps:
                        response += f"• {step}\n"
                
            else:
                response = str(response_content)
            
            await cl.Message(content=response).send()
            
        else:
            error_msg = result.get('error', 'Unknown error occurred')
            await cl.Message(
                content=f"❌ **Error**\n\nSorry, I encountered an error: {error_msg}"
            ).send()
            
    except Exception as e:
        await cl.Message(
            content=f"❌ **System Error**\n\nAn unexpected error occurred: {str(e)}"
        ).send()

@cl.on_chat_end
async def end_chat():
    """Clean up when chat ends"""
    try:
        await freelancex_ai.stop()
        print("FreelanceX.AI system stopped")
    except Exception as e:
        print(f"Error stopping system: {str(e)}")

if __name__ == "__main__":
    print("Starting FreelanceX.AI Chainlit Interface...")
    print("Access the interface at: http://localhost:8000") 