"""FreelanceX.AI Cognitive Agent - OpenAI Agents SDK Implementation
Central reasoning and decision-making agent
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ReasoningRequest(BaseModel):
    """Request for cognitive reasoning"""
    context: str
    question: str
    constraints: Optional[List[str]] = None
    priority_factors: Optional[List[str]] = None

class ReasoningResponse(BaseModel):
    """Structured reasoning response"""
    conclusion: str
    confidence: float
    reasoning_path: List[str]
    alternatives: Optional[List[Dict[str, Any]]] = None
    next_steps: List[str]

class DecisionRequest(BaseModel):
    """Request for decision making"""
    situation: str
    options: List[Dict[str, Any]]
    criteria: List[Dict[str, float]]
    constraints: Optional[List[str]] = None

class DecisionResponse(BaseModel):
    """Structured decision response"""
    recommended_option: str
    justification: str
    pros: List[str]
    cons: List[str]
    risk_assessment: Dict[str, Any]
    implementation_plan: List[str]

@tool
def analyze_reasoning(request: ReasoningRequest) -> ReasoningResponse:
    """Perform deep reasoning analysis on a complex problem
    
    Args:
        request: The reasoning request with context and question
    
    Returns:
        Structured reasoning response with conclusion and reasoning path
    """
    context_len = len(request.context or "")
    reasoning_path = [
        "Identify the question and constraints",
        "List key facts from context",
        "Evaluate options against constraints and priorities",
        "Select conclusion with rationale",
    ]
    alternatives = [
        {"option": "conservative", "tradeoff": "lower risk, slower impact"},
        {"option": "aggressive", "tradeoff": "higher risk, faster impact"},
    ]
    conclusion = f"Answer derived from {context_len} chars of context focusing on '{request.question[:60]}'."
    next_steps = ["Validate assumptions", "Implement smallest testable change", "Measure outcomes"]
    return ReasoningResponse(
        conclusion=conclusion,
        confidence=0.6,
        reasoning_path=reasoning_path,
        alternatives=alternatives,
        next_steps=next_steps,
    )

@tool
def make_decision(request: DecisionRequest) -> DecisionResponse:
    """Make a structured decision based on options and criteria
    
    Args:
        request: The decision request with options and criteria
    
    Returns:
        Decision response with recommended option and justification
    """
    # Score options by weighted criteria if present
    criteria = request.criteria or []
    def score(option: Dict[str, Any]) -> float:
        total = 0.0
        for crit in criteria:
            for key, weight in crit.items():
                val = float(option.get(key, 0) or 0)
                total += val * float(weight)
        return total

    scored = [(opt.get("name", "option"), score(opt)) for opt in request.options]
    scored.sort(key=lambda x: x[1], reverse=True)
    recommended = scored[0][0] if scored else (request.options[0].get("name", "option") if request.options else "none")
    pros = ["Meets weighted criteria", "Feasible under constraints"]
    cons = ["Assumptions may need validation"]
    risk_assessment = {"execution_risk": "medium", "dependencies": len(request.options)}
    implementation_plan = ["Define success metrics", "Assign owner", "Timeline & checkpoints"]
    return DecisionResponse(
        recommended_option=recommended,
        justification=f"Selected by weighted scoring across {len(criteria)} criteria",
        pros=pros,
        cons=cons,
        risk_assessment=risk_assessment,
        implementation_plan=implementation_plan,
    )

# Create cognitive agent
cognitive_agent = Agent(
    name="Cognitive Core Agent",
    instructions="""You are the Cognitive Core Agent for FreelanceX.AI, responsible for deep reasoning and decision-making.

Your primary responsibilities include:
1. Analyzing complex problems through structured reasoning
2. Making decisions based on multiple criteria and constraints
3. Providing clear reasoning paths for conclusions
4. Assessing risks and alternatives for decisions

When performing reasoning:
- Break down complex problems into manageable components
- Consider multiple perspectives and potential biases
- Evaluate evidence quality and relevance
- Provide confidence levels for conclusions

When making decisions:
- Weigh options against explicit criteria
- Consider short and long-term implications
- Assess risks and develop mitigation strategies
- Provide clear implementation plans

You should maintain logical consistency and transparency in your reasoning process.
""",
    tools=[analyze_reasoning, make_decision]
)