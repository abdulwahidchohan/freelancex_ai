"""FreelanceX.AI Knowledge Graph Agent
Dynamic skill linking & inference
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel
from typing import List, Dict


class SkillRelation(BaseModel):
    source: str
    target: str
    relation: str


@tool
def infer_related_skills(skills: List[str]) -> List[SkillRelation]:
    rels: List[SkillRelation] = []
    for s in skills:
        if s.lower() == "python":
            rels.append(SkillRelation(source="python", target="pydantic", relation="uses"))
            rels.append(SkillRelation(source="python", target="fastapi", relation="popular_with"))
        if s.lower() == "react":
            rels.append(SkillRelation(source="react", target="nextjs", relation="framework"))
    return rels


knowledge_graph_agent = Agent(
    name="Knowledge Graph Agent",
    instructions="""You relate skills and concepts to help routing and recommendations.""",
    tools=[infer_related_skills],
)


