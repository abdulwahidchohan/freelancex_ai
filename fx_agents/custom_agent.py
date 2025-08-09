#!/usr/bin/env python3
"""
FreelanceX.AI Custom Agent Implementation
Supports both OpenAI and Google Gemini APIs through the API manager
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from agents import Agent, Runner, function_tool as tool
from functools import partial
from .api_provider import APIManager, ChatMessage, ChatCompletionRequest, get_api_manager

logger = logging.getLogger(__name__)

# Use non-strict schema to allow Dict/Any parameters in current tools
tool = partial(tool, strict_mode=False)

@dataclass
class CustomAgentConfig:
    """Configuration for custom agent"""
    name: str
    instructions: str
    tools: List[Callable] = None
    handoffs: List[Agent] = None
    model: str = None
    temperature: float = 0.7
    max_tokens: int = 4000

class CustomAgent:
    """Custom agent that can use multiple API providers"""
    
    def __init__(self, config: CustomAgentConfig, api_manager: APIManager = None):
        self.config = config
        self.api_manager = api_manager or get_api_manager()
        self.name = config.name
        
        # Create the underlying OpenAI Agent SDK agent
        self.agent = Agent(
            name=config.name,
            instructions=config.instructions,
            tools=config.tools or [],
            handoffs=config.handoffs or []
        )
    
    async def run(self, user_input: str, session=None) -> Dict[str, Any]:
        """Run the agent with the specified input"""
        try:
            # First, try to use the OpenAI Agent SDK directly
            # This will work if OpenAI is available
            try:
                result = await Runner.run(self.agent, user_input, session=session)
                return {
                    "success": True,
                    "response": result.final_output,
                    "agent_used": self.name,
                    "provider": "openai_sdk",
                    "handoffs": len(result.handoffs) if result.handoffs else 0,
                    "trace_id": getattr(result, 'trace_id', None)
                }
            except Exception as e:
                logger.warning(f"OpenAI Agent SDK failed: {str(e)}")
                
                # Fall back to our custom API manager
                return await self._run_with_api_manager(user_input)
                
        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": f"I apologize, but I encountered an error: {str(e)}"
            }
    
    async def _run_with_api_manager(self, user_input: str) -> Dict[str, Any]:
        """Run the agent using our API manager with fallback support"""
        try:
            # Build the conversation context
            messages = [
                ChatMessage(role="system", content=self.config.instructions),
                ChatMessage(role="user", content=user_input)
            ]
            
            # Create the request
            request = ChatCompletionRequest(
                messages=messages,
                model=self.config.model or "gpt-4o-mini",
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Get response from API manager (with fallback)
            response = await self.api_manager.chat_completion(request)
            
            return {
                "success": True,
                "response": response.content,
                "agent_used": self.name,
                "provider": response.model,
                "handoffs": 0,  # No handoffs in custom implementation
                "trace_id": None
            }
            
        except Exception as e:
            logger.error(f"API manager execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": f"I apologize, but I encountered an error: {str(e)}"
            }

def create_custom_agent(
    name: str,
    instructions: str,
    tools: List[Callable] = None,
    handoffs: List[Agent] = None,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4000
) -> CustomAgent:
    """Factory function to create a custom agent"""
    config = CustomAgentConfig(
        name=name,
        instructions=instructions,
        tools=tools or [],
        handoffs=handoffs or [],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return CustomAgent(config)

# Example usage:
# custom_triage = create_custom_agent(
#     name="Custom Triage Agent",
#     instructions="You are a helpful assistant...",
#     tools=[analyze_request],
#     model="gpt-4o-mini"
# )
