"""FreelanceX.AI Agents Package
Hierarchical agent structure for comprehensive freelancer assistance
"""

# Import OpenAI Agent SDK components
from openai_agents import Agent, tool, Runner, Session, set_default_openai_key

# Export OpenAI Agent SDK components
__all__ = [
    'Agent',
    'tool',
    'Runner',
    'Session',
    'set_default_openai_key'
]

# Import agent layers
from .executive_core import *
from .cognitive_core import *
from .operations import *
from .user_experience import *
from .security import *
from .expansion import *

# Import triage agent (top-level coordinator)
from .triage_agent import triage_agent

# Add agent instances to exports
__all__ += [
    # Executive Core Layer
    'executive_agent',
    
    # Cognitive Core Layer
    'cognitive_agent',
    
    # Operations Layer
    'job_search_agent',
    'proposal_writer_agent', 
    'web_research_agent',
    'math_agent',
    'marketing_agent',
    'client_liaison_agent',
    'negotiator_agent',
    'automation_agent',
    
    # User Experience Layer
    'ux_agent',
    
    # Security & Reliability Layer
    'security_agent',
    
    # Expansion Layer
    'expansion_agent',
    
    # Triage Agent (Coordinator)
    'triage_agent'
]