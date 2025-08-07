"""FreelanceX.AI Context Manager Agent
Session continuity & personalization
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import Dict, Any, List


class ContextSnapshot(BaseModel):
    user_id: str
    preferences: Dict[str, Any]
    recent_topics: List[str]


@tool
def build_context(user_id: str, last_messages: List[str]) -> ContextSnapshot:
    topics = [m.split()[0].lower() for m in last_messages[-5:] if m]
    prefs = {"tone": "professional"}
    return ContextSnapshot(user_id=user_id, preferences=prefs, recent_topics=topics)


context_manager_agent = Agent(
    name="Context Manager Agent",
    instructions="""You maintain session context and preferences for personalization.""",
    tools=[build_context],
)


