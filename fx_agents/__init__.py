# FreelanceX.AI Agents Package
"""
Enhanced AI Agents for FreelanceX.AI with OpenAI Agents SDK Integration
"""

__version__ = "2.0.0"
__author__ = "FreelanceX.AI Team"

# Import main components
from .triage_agent import dynamic_triage_agent, route_request
from .custom_agent import DynamicAgent, AgentResponse, AgentRegistry
from .api_provider import get_api_manager, APIProvider

__all__ = [
    "dynamic_triage_agent",
    "route_request", 
    "DynamicAgent",
    "AgentResponse",
    "AgentRegistry",
    "get_api_manager",
    "APIProvider"
]