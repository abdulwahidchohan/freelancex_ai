#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script demonstrating how to use the OpenAI Agent SDK with FreelanceX.AI agents.

This script shows how to:
1. Create a session
2. Run the triage agent
3. Access trace information
4. Handle errors

Usage:
    python agent_sdk_example.py "Your message here"
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the freelancex_ai package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import FreelanceX.AI components
from agents import triage_agent
from openai_agents import Runner, Session, set_default_openai_key

# Load environment variables from .env file if it exists
load_dotenv()

# Set up logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    # Get the OpenAI API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        print("Error: Please set the OPENAI_API_KEY environment variable")
        return
    
    # Set the default OpenAI API key for the SDK
    set_default_openai_key(api_key)
    
    # Get the user message from command line arguments
    if len(sys.argv) < 2:
        print("Usage: python agent_sdk_example.py \"Your message here\"")
        return
    
    user_message = sys.argv[1]
    print(f"\nProcessing message: {user_message}\n")
    
    try:
        # Create a new session for this conversation
        session = Session()
        
        # Run the triage agent with the user message
        print("🤔 Analyzing your request...")
        result = await Runner.run(triage_agent, user_message, session=session)
        
        # Print the result
        print("\n🤖 Response:")
        print(result.final_output)
        
        # Print metadata if available
        metadata = []
        if hasattr(result, 'last_agent') and result.last_agent:
            metadata.append(f"🤖 Last Agent: {result.last_agent.name}")
        if hasattr(result, 'handoffs') and result.handoffs:
            metadata.append(f"🔄 Handoffs: {len(result.handoffs)}")
        if hasattr(result, 'trace_id') and result.trace_id:
            metadata.append(f"📊 Trace ID: {result.trace_id}")
            print(f"\nView the trace at: https://platform.openai.com/traces/{result.trace_id}")
        
        if metadata:
            print("\n📝 Metadata:")
            for item in metadata:
                print(f"  {item}")
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())