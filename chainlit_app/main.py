#!/usr/bin/env python3
"""
FreelanceX.AI - Agentic Chainlit Application
Fully agentic interface using OpenAI Agent SDK
"""

import asyncio
import logging
import os
from typing import Dict, Any
from datetime import datetime

import chainlit as cl
from agents import Runner, SQLiteSession, set_default_openai_key
from config.settings import get_config
from memory.sqlite_memory import SQLiteMemoryManager
from uuid import uuid4

# Import our triage agent via the wrapper to avoid collisions
from fx_agents import triage_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
cfg = get_config()

# Kill switch flag (config-driven)
KILL_SWITCH_ENV = os.getenv("FREELANCEX_KILL_SWITCH", "false").lower() in ("1", "true", "yes", "on")

# Memory engine (session recall)
memory_manager = SQLiteMemoryManager(db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else "memory.db")

# Set OpenAI API key
api_key = os.getenv('OPENAI_API_KEY') or cfg.external_integrations.openai_api_key
if not api_key:
    logger.warning("OPENAI_API_KEY not set. Please set it in your environment variables.")
else:
    # Set the default OpenAI API key for the SDK
    set_default_openai_key(api_key)

@cl.on_chat_start
async def start():
    """Initialize chat session"""
    try:
        # Create a new session for this chat (SDK concrete session)
        session = SQLiteSession(session_id=str(uuid4()), db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else ":memory:")
        cl.user_session.set("session", session)
        # Persist session for recall
        await memory_manager.store_session(session_id=str(id(session)), user_id="default", agent_name=triage_agent.name, session=session)
        
        # Send welcome message
        await cl.Message(
            content="""
# 🚀 Welcome to FreelanceX.AI!

I'm your AI assistant designed to help you succeed in the freelance world. Here's what I can do:

## 🎯 **Core Capabilities**
- **Job Search**: Find opportunities across multiple platforms (Upwork, Fiverr, LinkedIn)
- **Proposal Writing**: Create compelling proposals with market research
- **Web Research**: Gather market insights and industry data
- **Financial Management**: Calculate rates, budgets, and tax estimates

## 🛠️ **How to Use**
Simply tell me what you need! For example:
- "Find Python developer jobs on Upwork"
- "Write a proposal for a web development project"
- "Research market rates for React developers"
- "Calculate my project budget for a $50/hour rate"

## 🤖 **How It Works**
I use a hierarchical structure of specialized AI agents powered by the OpenAI Agent SDK:

**Executive & Cognitive Cores**:
- Strategic decision-making and complex reasoning

**Operations Layer**:
- **Job Search Agent**: Finds relevant opportunities
- **Proposal Writer Agent**: Creates compelling proposals
- **Web Research Agent**: Gathers market intelligence
- **Math Agent**: Handles financial calculations
- **Marketing Agent**: Develops marketing strategies
- **Client Liaison Agent**: Manages client relationships
- **Negotiator Agent**: Handles contract negotiations
- **Automation Agent**: Optimizes workflows

**Support Layers**:
- **UX Agent**: Improves user experience
- **Security Agent**: Ensures data protection
- **Expansion Agent**: Develops new capabilities

Ready to get started? What would you like to work on today?
            """,
            author="FreelanceX.AI"
        ).send()
        
    except Exception as e:
        logger.error(f"Error in chat start: {str(e)}")
        await cl.Message(
            content="Welcome to FreelanceX.AI! I'm ready to help you with your freelance needs.",
            author="FreelanceX.AI"
        ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages using the OpenAI Agent SDK"""
    try:
        # Kill switch check
        if KILL_SWITCH_ENV:
            await cl.Message(content="⛔ System is temporarily paused by kill switch.").send()
            return

        # Show typing indicator
        thinking_msg = cl.Message(content="🤔 Analyzing your request...")
        await thinking_msg.send()
        
        # Get the session from user_session
        session = cl.user_session.get("session")
        if not session:
            # Create a new session if one doesn't exist
            session = SQLiteSession(session_id=str(uuid4()), db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else ":memory:")
            cl.user_session.set("session", session)
        
        # Process the message using our triage agent with the session
        result = await Runner.run(triage_agent, message.content, session=session)
        
        # Remove thinking message
        await thinking_msg.remove()
        
        # Create response message
        response_content = result.final_output
        
        # Add metadata if available
        metadata = []
        if hasattr(result, 'last_agent') and result.last_agent:
            metadata.append(f"🤖 {result.last_agent.name}")
        if hasattr(result, 'handoffs') and result.handoffs:
            metadata.append(f"🔄 {len(result.handoffs)} handoffs")
        if hasattr(result, 'trace_id') and result.trace_id:
            metadata.append(f"📊 Trace ID: {result.trace_id}")
            logger.info(f"View trace at: https://platform.openai.com/traces/{result.trace_id}")
        
        if metadata:
            response_content += f"\n\n---\n{' | '.join(metadata)}"
        
        await cl.Message(
            content=response_content,
            author="FreelanceX.AI"
        ).send()
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing message: {str(e)}")
        
        # Check for specific OpenAI Agent SDK errors
        error_message = "I'm sorry, but I encountered an error while processing your request."
        
        if "openai.error.RateLimitError" in str(e):
            error_message = "I've hit my rate limit with OpenAI. Please try again in a moment."
        elif "openai.error.AuthenticationError" in str(e):
            error_message = "There's an issue with the OpenAI API authentication. Please check your API key."
        elif "openai.error.APIError" in str(e):
            error_message = "The OpenAI API is currently experiencing issues. Please try again later."
        elif "openai.error.Timeout" in str(e):
            error_message = "The request to OpenAI timed out. Please try again."
        elif "session" in str(e).lower():
            error_message = "There was an issue with your session. Starting a new conversation might help."
        else:
            error_message += " Please try again or contact support if the issue persists."
        
        # Send error message to user
        await cl.Message(
            content=f"{error_message}\n\nError details: {str(e)}",
            author="FreelanceX.AI"
        ).send()

@cl.on_chat_end
async def end():
    """Handle chat end"""
    try:
        # Get the session
        session = cl.user_session.get("session")
        
        # Log session information if available
        if session:
            logger.info(f"Ending chat session with trace IDs: {session.trace_ids if hasattr(session, 'trace_ids') else 'None'}")
            # Deactivate session in memory
            await memory_manager.delete_session(session_id=str(id(session)))
        
        await cl.Message(
            content="👋 Thank you for using FreelanceX.AI! Your session has been saved. Come back anytime for more freelance assistance.",
            author="FreelanceX.AI"
        ).send()
        
        logger.info("Chat session ended")
        
    except Exception as e:
        logger.error(f"Error in chat end: {str(e)}")

if __name__ == "__main__":
    pass  # This will be handled by Chainlit