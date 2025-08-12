# FreelanceX.AI Memory Package
"""
Enhanced Memory Management for FreelanceX.AI with OpenAI Agents SDK Integration
"""

__version__ = "2.0.0"

# Import main components
from .sqlite_memory import get_memory, create_enhanced_session

__all__ = [
    "get_memory",
    "create_enhanced_session"
] 