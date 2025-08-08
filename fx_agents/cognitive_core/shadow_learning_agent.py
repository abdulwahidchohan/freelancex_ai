"""FreelanceX.AI Shadow Learning Agent
Observes & improves without user asking
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel
from typing import List, Dict, Any


class LearningInsight(BaseModel):
    pattern: str
    suggestion: str
    expected_impact: str


@tool
def analyze_logs(log_lines: List[str]) -> List[LearningInsight]:
    findings: List[LearningInsight] = []
    if any("timeout" in l.lower() for l in log_lines):
        findings.append(LearningInsight(pattern="timeouts", suggestion="Lower latency model or cache frequent calls", expected_impact="fewer failures"))
    if any("rate limit" in l.lower() for l in log_lines):
        findings.append(LearningInsight(pattern="rate_limits", suggestion="Introduce exponential backoff & batching", expected_impact="higher reliability"))
    return findings


shadow_learning_agent = Agent(
    name="Shadow Learning Agent",
    instructions="""You observe traces and logs to suggest improvements automatically.""",
    tools=[analyze_logs],
)


