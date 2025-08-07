"""FreelanceX.AI User Experience Agent - OpenAI Agents SDK Implementation
Specialized agent for user interface and experience optimization
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class UserFeedback(BaseModel):
    """Analysis of user feedback"""
    sentiment: str
    key_issues: List[Dict[str, Any]]
    positive_aspects: List[str]
    improvement_opportunities: List[Dict[str, Any]]
    priority_recommendations: List[Dict[str, Any]]

class UXRecommendation(BaseModel):
    """UX improvement recommendation"""
    area: str
    current_state: str
    recommended_changes: List[Dict[str, Any]]
    expected_benefits: List[str]
    implementation_complexity: str
    testing_approach: Optional[Dict[str, Any]] = None

@tool
def analyze_user_feedback(feedback_data: List[Dict[str, Any]]) -> UserFeedback:
    """Analyze user feedback to identify patterns and improvement opportunities
    
    Args:
        feedback_data: List of user feedback entries
    
    Returns:
        Analysis of user feedback with key issues and recommendations
    """
    negatives = [f for f in feedback_data if str(f.get("sentiment", "")).lower() in ("neg", "negative")]
    positives = [f for f in feedback_data if str(f.get("sentiment", "")).lower() in ("pos", "positive")]
    key_issues = [{"issue": f.get("issue", "general") } for f in negatives[:5]]
    improvement = [{"area": "navigation", "change": "simplify menu"}]
    priority = [{"item": "onboarding", "impact": "high"}]
    return UserFeedback(
        sentiment="mixed" if negatives and positives else ("positive" if positives else "negative"),
        key_issues=key_issues,
        positive_aspects=[f.get("highlight", "") for f in positives[:5]],
        improvement_opportunities=improvement,
        priority_recommendations=priority,
    )

@tool
def generate_ux_recommendations(interaction_area: str, current_description: str, user_personas: Optional[List[Dict[str, Any]]] = None) -> UXRecommendation:
    """Generate UX improvement recommendations for a specific interaction area
    
    Args:
        interaction_area: The specific area of user interaction to improve
        current_description: Description of the current user experience
        user_personas: Optional list of user personas to consider
    
    Returns:
        UX recommendation with specific changes and expected benefits
    """
    changes = [
        {"change": "reduce cognitive load", "method": "progressive disclosure"},
        {"change": "improve affordances", "method": "button labels & contrast"},
    ]
    benefits = ["faster task completion", "higher satisfaction"]
    return UXRecommendation(
        area=interaction_area,
        current_state=current_description,
        recommended_changes=changes,
        expected_benefits=benefits,
        implementation_complexity="medium",
        testing_approach={"method": "A/B", "metric": "task success"},
    )

# Create UX agent
ux_agent = Agent(
    name="User Experience Agent",
    instructions="""You are the User Experience Agent for FreelanceX.AI, specialized in optimizing the user interface and experience.

Your primary responsibilities include:
1. Analyzing user feedback to identify UX issues and opportunities
2. Generating specific UX improvement recommendations
3. Ensuring the platform is intuitive and accessible for all users
4. Balancing functionality with simplicity and ease of use

When analyzing user feedback:
- Look for patterns across multiple users
- Consider both explicit feedback and implicit usage patterns
- Prioritize issues by impact on user satisfaction and business goals
- Distinguish between UX issues and other types of feedback

When generating UX recommendations:
- Focus on evidence-based improvements
- Consider different user personas and their specific needs
- Provide specific, actionable changes rather than general principles
- Balance ideal solutions with implementation complexity

You should focus on creating a seamless, intuitive experience that helps freelancers accomplish their goals efficiently.
""",
    tools=[analyze_user_feedback, generate_ux_recommendations]
)