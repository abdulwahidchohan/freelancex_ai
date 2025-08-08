"""FreelanceX.AI Agents Package
Hierarchical agent structure for comprehensive freelancer assistance.

Note:
- This package defines and exports FreelanceX agent instances and helper
  modules.
- SDK primitives like `Agent`, `Runner`, `tool`, `Session`, and
  `set_default_openai_key` should be imported from the official
  `agents` package, not from here.
"""

# Export only our agent instances and modules
__all__ = []

# Import agent layers (these files import SDK primitives from `agents`)
from .executive_core import *  # noqa: F401,F403
from .cognitive_core import *  # noqa: F401,F403
from .operations import *  # noqa: F401,F403
from .user_experience import *  # noqa: F401,F403
from .security import *  # noqa: F401,F403
from .expansion import *  # noqa: F401,F403

# Import triage agent (top-level coordinator)
from .triage_agent import triage_agent  # noqa: F401

# Add agent instances to exports
__all__ += [
    # Executive Core Layer
    'executive_agent',
    'governance_agent',
    'system_architect_agent',
    'marketplace_manager_agent',

    # Cognitive Core Layer
    'cognitive_agent',
    'context_manager_agent',
    'shadow_learning_agent',
    'knowledge_graph_agent',

    # Operations Layer
    'job_search_agent',
    'proposal_writer_agent',
    'web_research_agent',
    'math_agent',
    'marketing_agent',
    'client_liaison_agent',
    'negotiator_agent',
    'automation_agent',
    'content_agent',

    # User Experience Layer
    'ux_agent',

    # Security & Reliability Layer
    'security_agent', 'threat_detection_agent', 'self_repair_agent',

    # Expansion Layer
    'expansion_agent',

    # Triage Agent (Coordinator)
    'triage_agent'
]