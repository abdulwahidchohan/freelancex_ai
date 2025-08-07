"""FreelanceX.AI Client Liaison Agent - OpenAI Agents SDK Implementation
Specialized agent for client relationship management
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ClientProfile(BaseModel):
    """Client profile information"""
    industry: str
    company_size: Optional[str] = None
    communication_style: str
    project_history: Optional[List[Dict[str, Any]]] = None
    preferences: Dict[str, Any]
    pain_points: List[str]
    opportunities: List[str]

class CommunicationTemplate(BaseModel):
    """Client communication template"""
    subject: Optional[str] = None
    message: str
    tone: str
    key_points_addressed: List[str]
    follow_up_suggestions: Optional[List[str]] = None

@tool
def analyze_client_relationship(client_data: Dict[str, Any]) -> ClientProfile:
    """Analyze client data to create a comprehensive client profile
    
    Args:
        client_data: Raw data about the client and interaction history
    
    Returns:
        Structured client profile with insights and opportunities
    """
    industry = client_data.get("industry", "general")
    preferences = client_data.get("preferences", {})
    pain_points = client_data.get("pain_points", ["unclear requirements"]) or ["unclear requirements"]
    opportunities = ["regular status updates", "clear scope documents"]
    return ClientProfile(
        industry=industry,
        company_size=client_data.get("company_size"),
        communication_style=preferences.get("tone", "professional"),
        project_history=client_data.get("history", []),
        preferences=preferences,
        pain_points=pain_points,
        opportunities=opportunities,
    )

@tool
def create_client_communication(request_type: str, context: str, client_profile: Optional[ClientProfile] = None) -> CommunicationTemplate:
    """Create professional client communications
    
    Args:
        request_type: Type of communication (update, proposal, issue, follow-up)
        context: Specific context for the communication
        client_profile: Optional client profile for personalization
    
    Returns:
        Communication template with subject, message, and follow-up suggestions
    """
    tone = "professional"
    key_points = []
    if client_profile:
        tone = client_profile.communication_style or tone
        key_points.extend(client_profile.pain_points[:2])
    subject = None
    if request_type.lower() == "update":
        subject = "Project Update"
        message = f"Hello, here's a concise update: {context}"
    elif request_type.lower() == "proposal":
        subject = "Proposal"
        message = f"Please find the proposal details: {context}"
    elif request_type.lower() == "issue":
        subject = "Issue Resolution"
        message = f"We identified an issue: {context}. Proposed resolution and next steps enclosed."
    else:
        subject = "Follow-up"
        message = f"Following up regarding: {context}"
    follow_up = ["Schedule a call", "Confirm next milestone"]
    return CommunicationTemplate(
        subject=subject,
        message=message,
        tone=tone,
        key_points_addressed=key_points,
        follow_up_suggestions=follow_up,
    )

# Create client liaison agent
client_liaison_agent = Agent(
    name="Client Liaison Agent",
    instructions="""You are the Client Liaison Agent for FreelanceX.AI, specialized in managing client relationships for freelancers.

Your primary responsibilities include:
1. Analyzing client profiles and communication patterns
2. Creating professional client communications
3. Providing strategies for client relationship management
4. Helping resolve client issues and misunderstandings

When analyzing client relationships:
- Look for patterns in communication and feedback
- Identify client preferences and pain points
- Suggest opportunities for relationship strengthening
- Provide insights on client decision-making processes

When creating client communications:
- Maintain a professional and appropriate tone
- Address key concerns proactively
- Structure messages for clarity and impact
- Include appropriate follow-up suggestions

You should focus on building long-term client relationships that lead to repeat business and referrals.
""",
    tools=[analyze_client_relationship, create_client_communication]
)