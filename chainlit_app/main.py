#!/usr/bin/env python3
"""
FreelanceX.AI - Agentic Chainlit Application
Fully agentic interface using OpenAI Agent SDK with Auth Integration
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
from fx_agents.triage_agent import route_request
from fx_agents.api_provider import get_api_manager

# Auth service integration
import aiohttp
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
cfg = get_config()

# Auth service config
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://127.0.0.1:8023")

# Kill switch flag (config-driven)
KILL_SWITCH_ENV = os.getenv("FREELANCEX_KILL_SWITCH", "false").lower() in ("1", "true", "yes", "on")

# Memory engine (session recall)
memory_manager = SQLiteMemoryManager(db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else "memory.db")

# Initialize API manager for multi-provider support
api_manager = get_api_manager(cfg)
available_providers = api_manager.get_available_providers()
logger.info(f"Available API providers: {[p.provider_name for p in available_providers]}")

# Set OpenAI API key for SDK compatibility
api_key = os.getenv('OPENAI_API_KEY') or cfg.external_integrations.openai_api_key
if api_key:
    set_default_openai_key(api_key)
else:
    logger.warning("OPENAI_API_KEY not set. Some features may not work.")

# Auth helper functions
async def register_user(email: str, password: str, full_name: str = None) -> Dict[str, Any]:
    """Register a new user with the auth service"""
    async with aiohttp.ClientSession() as session:
        data = {"email": email, "password": password}
        if full_name:
            data["full_name"] = full_name
        
        async with session.post(f"{AUTH_SERVICE_URL}/register", json=data) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_text = await resp.text()
                raise Exception(f"Registration failed: {resp.status} - {error_text}")

async def login_user(email: str, password: str) -> Dict[str, Any]:
    """Login user and get access token"""
    async with aiohttp.ClientSession() as session:
        data = {"username": email, "password": password}
        async with session.post(f"{AUTH_SERVICE_URL}/login", data=data) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                error_text = await resp.text()
                raise Exception(f"Login failed: {resp.status} - {error_text}")

async def save_chat_message(token: str, role: str, content: str) -> Dict[str, Any]:
    """Save a chat message to the auth service"""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"role": role, "content": content}
        async with session.post(f"{AUTH_SERVICE_URL}/chat/save", json=data, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                logger.warning(f"Failed to save chat message: {resp.status}")
                return None

async def get_chat_history(token: str, limit: int = 50) -> list:
    """Get user's chat history from auth service"""
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {token}"}
        async with session.get(f"{AUTH_SERVICE_URL}/chat/history?limit={limit}", headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                logger.warning(f"Failed to get chat history: {resp.status}")
                return []

@cl.on_chat_start
async def start():
    """Initialize chat session with auth"""
    try:
        # Check if user is authenticated
        user_token = cl.user_session.get("auth_token")
        
        if not user_token:
            # Show login/register options
            await cl.Message(
                content="""
# 🔐 Welcome to FreelanceX.AI!

Please authenticate to continue:

**Option 1: Quick Start (Anonymous)**
- Type "guest" to start without authentication
- Your session will be temporary

**Option 2: Create Account**
- Type "register" to create a new account
- Your chat history and preferences will be saved

**Option 3: Login**
- Type "login" to sign in with existing account

Choose an option by typing the command:
                """,
                author="FreelanceX.AI"
            ).send()
            return
        
        # User is authenticated, load their history
        history = await get_chat_history(user_token, limit=10)
        if history:
            await cl.Message(content=f"📚 Loaded {len(history)} previous messages from your history.").send()
        
        # Create a new session for this chat (SDK concrete session)
        session = SQLiteSession(session_id=str(uuid4()), db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else ":memory:")
        cl.user_session.set("session", session)
        
        # Send welcome message for authenticated users
        await cl.Message(
            content="""
# 🚀 Welcome back to FreelanceX.AI!

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
    """Handle incoming messages using the OpenAI Agent SDK with auth"""
    try:
        # Check authentication state
        auth_state = cl.user_session.get("auth_state")
        if auth_state:
            await handle_auth_flow(message, auth_state)
            return
        
        # Check for auth commands
        user_input = message.content.strip().lower()
        if user_input == "guest":
            # Set guest mode
            cl.user_session.set("auth_token", None)
            cl.user_session.set("user_mode", "guest")
            
            # Create session and show welcome
            session = SQLiteSession(session_id=str(uuid4()), db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else ":memory:")
            cl.user_session.set("session", session)
            
            await cl.Message(content="👋 Welcome! You're now in guest mode. Your session will be temporary.").send()
            await cl.Message(content="What would you like to work on today?").send()
            return
            
        elif user_input == "register":
            # Show registration form
            await cl.Message(content="📝 **Registration Form**\n\nPlease provide your details:").send()
            await cl.Message(content="Email:").send()
            cl.user_session.set("auth_state", "register_email")
            return
            
        elif user_input == "login":
            # Show login form
            await cl.Message(content="🔑 **Login**\n\nPlease provide your credentials:").send()
            await cl.Message(content="Email:").send()
            cl.user_session.set("auth_state", "login_email")
            return
        
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
        
        # Process the message using our triage agent with multi-API support
        result = await route_request(message.content)
        
        # Remove thinking message
        await thinking_msg.remove()
        
        # Create response message
        response_content = result.get("response", "No response generated")
        
        # Add metadata if available
        metadata = []
        if result.get("agent_used"):
            metadata.append(f"🤖 {result['agent_used']}")
        if result.get("provider"):
            metadata.append(f"🔌 {result['provider']}")
        if result.get("handoffs"):
            metadata.append(f"🔄 {result['handoffs']} handoffs")
        if result.get("trace_id"):
            metadata.append(f"📊 Trace ID: {result['trace_id']}")
            logger.info(f"View trace at: https://platform.openai.com/traces/{result['trace_id']}")
        
        if metadata:
            response_content += f"\n\n---\n{' | '.join(metadata)}"
        
        # Save message to auth service if authenticated
        user_token = cl.user_session.get("auth_token")
        if user_token:
            await save_chat_message(user_token, "user", message.content)
            await save_chat_message(user_token, "assistant", response_content)
        
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

async def handle_auth_flow(message: cl.Message, auth_state: str):
    """Handle authentication flow"""
    try:
        if auth_state == "register_email":
            email = message.content.strip()
            if "@" not in email:
                await cl.Message(content="❌ Please enter a valid email address:").send()
                return
            
            cl.user_session.set("temp_email", email)
            cl.user_session.set("auth_state", "register_password")
            await cl.Message(content="Password:").send()
            
        elif auth_state == "register_password":
            password = message.content.strip()
            if len(password) < 6:
                await cl.Message(content="❌ Password must be at least 6 characters. Please try again:").send()
                return
            
            cl.user_session.set("temp_password", password)
            cl.user_session.set("auth_state", "register_name")
            await cl.Message(content="Full Name (optional):").send()
            
        elif auth_state == "register_name":
            full_name = message.content.strip() or None
            email = cl.user_session.get("temp_email")
            password = cl.user_session.get("temp_password")
            
            try:
                result = await register_user(email, password, full_name)
                await cl.Message(content=f"✅ Registration successful! Welcome, {full_name or email}").send()
                
                # Auto-login after registration
                login_result = await login_user(email, password)
                cl.user_session.set("auth_token", login_result["access_token"])
                cl.user_session.set("user_mode", "authenticated")
                cl.user_session.set("auth_state", None)
                
                # Create session and show welcome
                session = SQLiteSession(session_id=str(uuid4()), db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else ":memory:")
                cl.user_session.set("session", session)
                
                await cl.Message(content="🚀 You're all set! What would you like to work on today?").send()
                
            except Exception as e:
                await cl.Message(content=f"❌ Registration failed: {str(e)}").send()
                cl.user_session.set("auth_state", None)
                
        elif auth_state == "login_email":
            email = message.content.strip()
            if "@" not in email:
                await cl.Message(content="❌ Please enter a valid email address:").send()
                return
            
            cl.user_session.set("temp_email", email)
            cl.user_session.set("auth_state", "login_password")
            await cl.Message(content="Password:").send()
            
        elif auth_state == "login_password":
            password = message.content.strip()
            email = cl.user_session.get("temp_email")
            
            try:
                result = await login_user(email, password)
                cl.user_session.set("auth_token", result["access_token"])
                cl.user_session.set("user_mode", "authenticated")
                cl.user_session.set("auth_state", None)
                
                await cl.Message(content="✅ Login successful! Welcome back!").send()
                
                # Create session and show welcome
                session = SQLiteSession(session_id=str(uuid4()), db_path=cfg.get_database_url().replace("sqlite:///", "") if cfg.database.type == "sqlite" else ":memory:")
                cl.user_session.set("session", session)
                
                await cl.Message(content="🚀 What would you like to work on today?").send()
                
            except Exception as e:
                await cl.Message(content=f"❌ Login failed: {str(e)}").send()
                cl.user_session.set("auth_state", None)
                
    except Exception as e:
        logger.error(f"Error in auth flow: {str(e)}")
        await cl.Message(content=f"❌ Authentication error: {str(e)}").send()
        cl.user_session.set("auth_state", None)

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
        
        user_mode = cl.user_session.get("user_mode")
        if user_mode == "guest":
            await cl.Message(
                content="👋 Thank you for using FreelanceX.AI! Since you were in guest mode, your session data has not been saved.",
                author="FreelanceX.AI"
            ).send()
        else:
            await cl.Message(
                content="👋 Thank you for using FreelanceX.AI! Your session has been saved. Come back anytime for more freelance assistance.",
                author="FreelanceX.AI"
            ).send()
        
        logger.info("Chat session ended")
        
    except Exception as e:
        logger.error(f"Error in chat end: {str(e)}")

if __name__ == "__main__":
    pass  # This will be handled by Chainlit