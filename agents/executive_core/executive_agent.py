"""FreelanceX.AI Executive Agent - OpenAI Agents SDK Implementation
Top-level strategic agent that oversees the entire system
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StrategicDecision(BaseModel):
    """Strategic decision for business operations"""
    decision_type: str
    priority: str
    reasoning: str
    implementation_steps: List[str]
    expected_outcomes: List[str]

class BusinessMetrics(BaseModel):
    """Key business metrics and performance indicators"""
    revenue_growth: float
    client_satisfaction: float
    operational_efficiency: float
    market_position: str
    recommendations: List[str]

@tool
def analyze_business_strategy(current_state: str, goals: List[str]) -> StrategicDecision:
    """Analyze current business state and provide strategic direction
    
    Args:
        current_state: Description of current business situation
        goals: List of business goals to achieve
    
    Returns:
        Strategic decision with implementation steps
    """
    # Lightweight heuristic implementation to make the tool usable
    prioritized_goals = goals[:]
    # Simple prioritization: goals containing growth/retention/security first
    priority_order = ["growth", "revenue", "retention", "security", "scalability"]
    prioritized_goals.sort(key=lambda g: next((i for i, k in enumerate(priority_order) if k in g.lower()), 99))

    implementation_steps = [
        "Define success metrics and baseline current KPIs",
        "Allocate owners and timelines for each strategic goal",
        "Sequence initiatives by impact vs. effort",
        "Set up weekly review and risk tracking",
    ]
    expected_outcomes = [
        "Improved focus on high-impact goals",
        "Clear accountability and execution cadence",
        "Early risk detection and mitigation",
    ]

    return StrategicDecision(
        decision_type="strategic_plan",
        priority=", ".join(prioritized_goals[:3]) if prioritized_goals else "stability",
        reasoning=f"Based on current_state length {len(current_state)} and goals provided, ordered by common business priorities.",
        implementation_steps=implementation_steps,
        expected_outcomes=expected_outcomes,
    )

@tool
def evaluate_performance(metrics: Dict[str, Any]) -> BusinessMetrics:
    """Evaluate business performance based on provided metrics
    
    Args:
        metrics: Dictionary of business metrics
    
    Returns:
        Analysis of business metrics with recommendations
    """
    revenue_growth = float(metrics.get("revenue_growth", 0.0) or 0.0)
    csat = float(metrics.get("client_satisfaction", 0.0) or 0.0)
    efficiency = float(metrics.get("operational_efficiency", 0.0) or 0.0)

    recommendations: List[str] = []
    if revenue_growth < 0:
        recommendations.append("Address negative revenue trend with pricing and pipeline initiatives")
    if csat < 4.2:
        recommendations.append("Improve client satisfaction via communication cadences and QA gates")
    if efficiency < 0.7:
        recommendations.append("Automate repetitive tasks and remove bottlenecks")
    if not recommendations:
        recommendations.append("Maintain momentum; invest in scalable systems")

    market_position = metrics.get("market_position", "stable")

    return BusinessMetrics(
        revenue_growth=revenue_growth,
        client_satisfaction=csat,
        operational_efficiency=efficiency,
        market_position=str(market_position),
        recommendations=recommendations,
    )

# Create executive agent
executive_agent = Agent(
    name="Executive Core Agent",
    instructions="""You are the Executive Core Agent for FreelanceX.AI, responsible for high-level strategic decisions.

Your primary responsibilities include:
1. Analyzing business metrics and providing strategic direction
2. Coordinating between different agent layers
3. Ensuring alignment with business goals and user needs
4. Making high-level decisions about resource allocation

When making strategic decisions, consider:
- Long-term business sustainability
- User satisfaction and retention
- Market trends and competitive landscape
- Operational efficiency and scalability

You should maintain a strategic perspective while delegating tactical decisions to specialized agents.
""",
    tools=[analyze_business_strategy, evaluate_performance]
)