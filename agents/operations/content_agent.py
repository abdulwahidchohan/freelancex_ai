"""FreelanceX.AI Content Agent
Writes, designs, edits, localizes content beyond proposals/marketing
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Optional


class ContentTask(BaseModel):
    kind: str  # blog, case_study, landing, doc, localization
    topic: str
    audience: str
    length: Optional[str] = "medium"


@tool
def create_content(task: ContentTask) -> str:
    outline = ["Intro", "Problem", "Solution", "Proof", "CTA"]
    return f"Content ({task.kind}) for {task.audience} on {task.topic}. Outline: {', '.join(outline)}."


content_agent = Agent(
    name="Content Agent",
    instructions="""You create non-proposal content: blogs, case studies, landing pages, and localizations.""",
    tools=[create_content],
)


