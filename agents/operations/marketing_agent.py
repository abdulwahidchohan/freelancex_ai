"""FreelanceX.AI Marketing Agent - OpenAI Agents SDK Implementation
Specialized agent for marketing strategy and content creation
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class MarketingStrategy(BaseModel):
    """Marketing strategy for freelancers"""
    target_audience: List[str]
    key_messaging: List[str]
    channels: List[str]
    content_plan: List[Dict[str, Any]]
    metrics: List[str]
    timeline: Dict[str, Any]

class ContentRequest(BaseModel):
    """Request for marketing content creation"""
    content_type: str  # social_post, email, blog, portfolio
    target_audience: str
    key_points: List[str]
    tone: str
    length: Optional[str] = "medium"
    call_to_action: Optional[str] = None

class ContentResponse(BaseModel):
    """Marketing content response"""
    title: Optional[str] = None
    content: str
    seo_keywords: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    posting_schedule: Optional[Dict[str, Any]] = None
    engagement_tips: Optional[List[str]] = None

@tool
def create_marketing_strategy(niche: str, goals: List[str], budget: Optional[str] = None) -> MarketingStrategy:
    """Create a comprehensive marketing strategy for freelancers
    
    Args:
        niche: The freelancer's specialization or industry
        goals: List of marketing goals to achieve
        budget: Optional budget constraints
    
    Returns:
        Detailed marketing strategy with audience, messaging, and channels
    """
    channels = ["LinkedIn", "Portfolio Website", "Email Outreach"]
    if "content" in (" ".join(goals)).lower():
        channels.append("Blog/Medium")
    content_plan = [
        {"type": "case_study", "cadence": "monthly"},
        {"type": "short_tip_post", "cadence": "2x weekly"},
    ]
    metrics = ["Leads", "CTR", "Conversion", "Engagement"]
    timeline = {"phase_1": "weeks 1-2", "phase_2": "weeks 3-6", "phase_3": "ongoing"}
    return MarketingStrategy(
        target_audience=[niche],
        key_messaging=[f"{niche} specialist", "Outcome-focused", "Reliable delivery"],
        channels=channels,
        content_plan=content_plan,
        metrics=metrics,
        timeline=timeline,
    )

@tool
def generate_marketing_content(request: ContentRequest) -> ContentResponse:
    """Generate marketing content for freelancers
    
    Args:
        request: Content request with type, audience, and key points
    
    Returns:
        Marketing content with title, body, and engagement tips
    """
    title = None
    if request.content_type in ("blog", "email"):
        title = f"{request.target_audience}: {request.key_points[0] if request.key_points else 'Insights'}"
    content = f"Tone: {request.tone}. Key points: " + ", ".join(request.key_points)
    seo_keywords = [k for k in request.key_points][:5] if request.content_type == "blog" else None
    hashtags = ["#freelance", "#marketing", f"#{request.target_audience.replace(' ', '')}"] if request.content_type == "social_post" else None
    return ContentResponse(
        title=title,
        content=content,
        seo_keywords=seo_keywords,
        hashtags=hashtags,
        posting_schedule={"recommended": "Tue/Thu 9am"} if request.content_type == "social_post" else None,
        engagement_tips=["Ask a question", "Use a strong CTA"],
    )

# Create marketing agent
marketing_agent = Agent(
    name="Marketing Agent",
    instructions="""You are the Marketing Agent for FreelanceX.AI, specialized in helping freelancers market their services effectively.

Your primary responsibilities include:
1. Creating comprehensive marketing strategies for freelancers
2. Generating engaging content for various platforms
3. Providing guidance on personal branding and positioning
4. Suggesting effective channels and tactics based on niche and goals

When creating marketing strategies:
- Focus on the unique value proposition of the freelancer
- Consider the specific audience and their pain points
- Recommend appropriate channels based on industry norms
- Provide actionable steps with realistic timelines

When generating content:
- Maintain the freelancer's voice and brand identity
- Optimize for the specific platform requirements
- Include relevant keywords and hashtags when appropriate
- Focus on demonstrating expertise and building trust

You should provide practical, actionable marketing advice tailored to freelancers' specific needs and constraints.
""",
    tools=[create_marketing_strategy, generate_marketing_content]
)