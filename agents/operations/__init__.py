"""FreelanceX.AI Operations Layer
Specialized task-oriented agents
"""

# Import existing operational agents
from ..job_search_agent import job_search_agent
from ..proposal_writer_agent import proposal_writer_agent
from ..web_research_agent import web_research_agent
from ..math_agent import math_agent

# Import new operational agents
from .marketing_agent import marketing_agent
from .client_liaison_agent import client_liaison_agent
from .negotiator_agent import negotiator_agent
from .automation_agent import automation_agent
from .content_agent import content_agent

__all__ = [
    'job_search_agent',
    'proposal_writer_agent',
    'web_research_agent',
    'math_agent',
    'marketing_agent',
    'client_liaison_agent',
    'negotiator_agent',
    'automation_agent',
    'content_agent'
]