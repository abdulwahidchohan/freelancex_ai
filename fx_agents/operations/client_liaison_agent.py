"""FreelanceX.AI Client Liaison Agent - OpenAI Agents SDK Implementation
Specialized agent for client relationship management
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClientProfile(BaseModel):
    """Client profile information"""
    industry: str = Field(..., description="Client's industry sector")
    company_size: Optional[str] = Field(None, description="Company size category")
    communication_style: str = Field(..., description="Preferred communication style")
    project_history: Optional[List[Dict[str, Any]]] = Field(None, description="Historical project data")
    preferences: Dict[str, Any] = Field(..., description="Client preferences and settings")
    pain_points: List[str] = Field(..., description="Client's main pain points")
    opportunities: List[str] = Field(..., description="Opportunities for improvement")
    relationship_score: float = Field(..., description="Relationship health score (0-1)")
    last_interaction: str = Field(..., description="Last interaction timestamp")
    engagement_level: str = Field(..., description="Client engagement level")

class CommunicationTemplate(BaseModel):
    """Client communication template"""
    subject: Optional[str] = Field(None, description="Email subject line")
    message: str = Field(..., description="Main message content")
    tone: str = Field(..., description="Communication tone")
    key_points_addressed: List[str] = Field(..., description="Key points addressed")
    follow_up_suggestions: Optional[List[str]] = Field(None, description="Suggested follow-up actions")
    urgency_level: str = Field(..., description="Urgency level of the communication")
    expected_response_time: str = Field(..., description="Expected response time")

class ClientStrategy(BaseModel):
    """Client relationship strategy"""
    client_id: str = Field(..., description="Client identifier")
    strategy_type: str = Field(..., description="Type of strategy")
    objectives: List[str] = Field(..., description="Strategy objectives")
    action_items: List[str] = Field(..., description="Specific action items")
    timeline: str = Field(..., description="Implementation timeline")
    success_metrics: List[str] = Field(..., description="Success measurement criteria")

class IssueResolution(BaseModel):
    """Client issue resolution plan"""
    issue_type: str = Field(..., description="Type of issue")
    severity: str = Field(..., description="Issue severity level")
    root_cause: str = Field(..., description="Identified root cause")
    resolution_steps: List[str] = Field(..., description="Steps to resolve the issue")
    prevention_measures: List[str] = Field(..., description="Measures to prevent recurrence")
    communication_plan: str = Field(..., description="Communication strategy for the issue")

@tool
def analyze_client_relationship(client_data: Dict[str, Any]) -> ClientProfile:
    """Analyze client data to create a comprehensive client profile
    
    Args:
        client_data: Raw data about the client and interaction history
    
    Returns:
        Structured client profile with insights and opportunities
    """
    try:
        logger.info("Analyzing client relationship data")
        
        # Extract basic information
        industry = client_data.get("industry", "general")
        company_size = client_data.get("company_size")
        preferences = client_data.get("preferences", {})
        
        # Analyze communication style
        communication_style = "professional"
        if preferences.get("casual_interactions", 0) > preferences.get("formal_interactions", 0):
            communication_style = "casual"
        elif preferences.get("technical_interactions", 0) > preferences.get("general_interactions", 0):
            communication_style = "technical"
        
        # Analyze pain points
        pain_points = client_data.get("pain_points", [])
        if not pain_points:
            # Generate default pain points based on industry
            if industry.lower() in ["technology", "software"]:
                pain_points = ["project delays", "scope creep", "technical complexity"]
            elif industry.lower() in ["finance", "banking"]:
                pain_points = ["compliance requirements", "security concerns", "regulatory changes"]
            else:
                pain_points = ["unclear requirements", "communication gaps", "timeline management"]
        
        # Identify opportunities
        opportunities = []
        project_history = client_data.get("history", [])
        
        if len(project_history) > 0:
            opportunities.extend([
                "regular status updates",
                "clear scope documents",
                "proactive communication"
            ])
        
        # Calculate relationship score
        relationship_score = 0.7  # Base score
        if project_history:
            successful_projects = len([p for p in project_history if p.get("status") == "completed"])
            total_projects = len(project_history)
            relationship_score = min(1.0, successful_projects / total_projects + 0.3)
        
        # Determine engagement level
        engagement_level = "moderate"
        if relationship_score > 0.8:
            engagement_level = "high"
        elif relationship_score < 0.5:
            engagement_level = "low"
        
        return ClientProfile(
            industry=industry,
            company_size=company_size,
            communication_style=communication_style,
            project_history=project_history,
            preferences=preferences,
            pain_points=pain_points,
            opportunities=opportunities,
            relationship_score=relationship_score,
            last_interaction=datetime.now().isoformat(),
            engagement_level=engagement_level
        )
        
    except Exception as e:
        logger.error(f"Error analyzing client relationship: {e}")
        return ClientProfile(
            industry="unknown",
            communication_style="professional",
            preferences={},
            pain_points=["analysis error"],
            opportunities=["review data format"],
            relationship_score=0.0,
            last_interaction=datetime.now().isoformat(),
            engagement_level="unknown"
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
    try:
        logger.info(f"Creating client communication: {request_type}")
        
        # Determine tone and style
        tone = "professional"
        urgency_level = "normal"
        expected_response_time = "2-3 business days"
        
        if client_profile:
            tone = client_profile.communication_style
            if client_profile.relationship_score > 0.8:
                tone = "friendly"
        
        # Generate communication based on type
        subject = None
        message = ""
        key_points = []
        follow_up = []
        
        if request_type.lower() == "update":
            subject = "Project Update - [Project Name]"
            message = f"""Dear [Client Name],

I hope this message finds you well. I wanted to provide you with a brief update on our project progress.

{context}

Key highlights:
• [Key achievement 1]
• [Key achievement 2]
• [Next milestone]

Please let me know if you have any questions or if there's anything specific you'd like me to address.

Best regards,
[Your Name]"""
            key_points = ["project progress", "milestones", "next steps"]
            follow_up = ["Schedule a progress review call", "Confirm next milestone timeline"]
            
        elif request_type.lower() == "proposal":
            subject = "Project Proposal - [Project Name]"
            message = f"""Dear [Client Name],

Thank you for the opportunity to work on your project. I'm excited to present our proposal for your consideration.

{context}

Proposal Overview:
• Project Scope: [Brief scope description]
• Timeline: [Estimated timeline]
• Deliverables: [Key deliverables]
• Investment: [Pricing information]

I'm available for a detailed discussion at your convenience to address any questions or concerns.

Best regards,
[Your Name]"""
            key_points = ["project scope", "timeline", "deliverables", "pricing"]
            follow_up = ["Schedule proposal review meeting", "Request additional information"]
            urgency_level = "medium"
            expected_response_time = "1 week"
            
        elif request_type.lower() == "issue":
            subject = "Issue Resolution - [Issue Description]"
            message = f"""Dear [Client Name],

I wanted to bring to your attention an issue we've identified and our proposed resolution plan.

Issue: {context}

Resolution Plan:
• [Step 1 of resolution]
• [Step 2 of resolution]
• [Timeline for resolution]

Impact Assessment:
• [Impact on project timeline]
• [Impact on deliverables]
• [Mitigation strategies]

I'm committed to resolving this quickly and minimizing any disruption to your project.

Best regards,
[Your Name]"""
            key_points = ["issue identification", "resolution plan", "impact assessment"]
            follow_up = ["Schedule urgent call", "Provide status update within 24 hours"]
            urgency_level = "high"
            expected_response_time = "24 hours"
            
        else:  # follow-up
            subject = "Follow-up - [Topic]"
            message = f"""Dear [Client Name],

I hope you're doing well. I wanted to follow up regarding our previous discussion about {context}.

Quick reminder of key points:
• [Point 1]
• [Point 2]
• [Point 3]

I'm looking forward to hearing from you and moving forward with our collaboration.

Best regards,
[Your Name]"""
            key_points = ["previous discussion", "key points", "next steps"]
            follow_up = ["Schedule follow-up call", "Send additional information"]
        
        return CommunicationTemplate(
            subject=subject,
            message=message,
            tone=tone,
            key_points_addressed=key_points,
            follow_up_suggestions=follow_up,
            urgency_level=urgency_level,
            expected_response_time=expected_response_time
        )
        
    except Exception as e:
        logger.error(f"Error creating client communication: {e}")
        return CommunicationTemplate(
            message=f"Error creating communication: {str(e)}",
            tone="professional",
            key_points_addressed=["error"],
            urgency_level="normal",
            expected_response_time="ASAP"
        )

@tool
def develop_client_strategy(client_profile: ClientProfile, business_goals: List[str]) -> ClientStrategy:
    """Develop a comprehensive client relationship strategy
    
    Args:
        client_profile: Client profile information
        business_goals: Business goals for the client relationship
    
    Returns:
        ClientStrategy with detailed action plan
    """
    try:
        logger.info("Developing client relationship strategy")
        
        # Determine strategy type based on relationship score and engagement
        strategy_type = "maintenance"
        if client_profile.relationship_score < 0.5:
            strategy_type = "recovery"
        elif client_profile.relationship_score > 0.8:
            strategy_type = "growth"
        
        # Generate objectives based on strategy type
        objectives = []
        if strategy_type == "recovery":
            objectives = [
                "Rebuild trust and communication",
                "Address pain points proactively",
                "Demonstrate value and reliability"
            ]
        elif strategy_type == "growth":
            objectives = [
                "Expand service offerings",
                "Increase project volume",
                "Generate referrals and testimonials"
            ]
        else:  # maintenance
            objectives = [
                "Maintain high satisfaction levels",
                "Ensure consistent communication",
                "Identify new opportunities"
            ]
        
        # Generate action items
        action_items = [
            "Schedule regular check-in calls",
            "Provide proactive project updates",
            "Address client pain points",
            "Share relevant industry insights",
            "Request feedback and testimonials"
        ]
        
        # Determine timeline
        timeline = "3-6 months"
        if strategy_type == "recovery":
            timeline = "1-3 months"
        elif strategy_type == "growth":
            timeline = "6-12 months"
        
        # Define success metrics
        success_metrics = [
            "Increased relationship score",
            "Higher engagement level",
            "More project opportunities",
            "Positive client feedback",
            "Referral generation"
        ]
        
        return ClientStrategy(
            client_id=client_profile.industry,  # Using industry as client ID for demo
            strategy_type=strategy_type,
            objectives=objectives,
            action_items=action_items,
            timeline=timeline,
            success_metrics=success_metrics
        )
        
    except Exception as e:
        logger.error(f"Error developing client strategy: {e}")
        return ClientStrategy(
            client_id="unknown",
            strategy_type="error",
            objectives=["Review strategy development process"],
            action_items=["Troubleshoot strategy generation"],
            timeline="TBD",
            success_metrics=["Process improvement"]
        )

@tool
def resolve_client_issue(issue_description: str, client_profile: ClientProfile) -> IssueResolution:
    """Develop a comprehensive issue resolution plan
    
    Args:
        issue_description: Description of the client issue
        client_profile: Client profile for context
    
    Returns:
        IssueResolution with detailed resolution plan
    """
    try:
        logger.info("Developing issue resolution plan")
        
        # Analyze issue type and severity
        issue_lower = issue_description.lower()
        
        # Determine issue type
        issue_type = "general"
        if any(word in issue_lower for word in ["delay", "late", "timeline"]):
            issue_type = "timeline"
        elif any(word in issue_lower for word in ["quality", "defect", "bug"]):
            issue_type = "quality"
        elif any(word in issue_lower for word in ["communication", "unclear", "confusion"]):
            issue_type = "communication"
        elif any(word in issue_lower for word in ["scope", "requirement", "change"]):
            issue_type = "scope"
        
        # Determine severity
        severity = "medium"
        if any(word in issue_lower for word in ["urgent", "critical", "emergency"]):
            severity = "high"
        elif any(word in issue_lower for word in ["minor", "small", "slight"]):
            severity = "low"
        
        # Generate resolution steps based on issue type
        resolution_steps = []
        if issue_type == "timeline":
            resolution_steps = [
                "Assess current project status and identify bottlenecks",
                "Develop revised timeline with realistic milestones",
                "Implement additional resources or process improvements",
                "Communicate updated timeline to client with clear rationale"
            ]
        elif issue_type == "quality":
            resolution_steps = [
                "Conduct thorough quality review and testing",
                "Identify root cause of quality issues",
                "Implement quality assurance improvements",
                "Provide detailed quality report to client"
            ]
        elif issue_type == "communication":
            resolution_steps = [
                "Schedule immediate client meeting to clarify requirements",
                "Establish clear communication protocols",
                "Implement regular status update schedule",
                "Create detailed project documentation"
            ]
        elif issue_type == "scope":
            resolution_steps = [
                "Review and document current scope vs. requirements",
                "Assess impact of scope changes on timeline and budget",
                "Present scope options to client with recommendations",
                "Update project plan and get client approval"
            ]
        else:
            resolution_steps = [
                "Investigate issue thoroughly",
                "Develop comprehensive resolution plan",
                "Implement solution with client input",
                "Monitor and follow up on resolution effectiveness"
            ]
        
        # Generate prevention measures
        prevention_measures = [
            "Implement proactive monitoring and early warning systems",
            "Establish clear communication protocols",
            "Create comprehensive project documentation",
            "Schedule regular client check-ins",
            "Develop contingency plans for common issues"
        ]
        
        # Determine communication plan
        communication_plan = "Immediate client notification with detailed resolution plan"
        if severity == "high":
            communication_plan = "Urgent client call within 2 hours with immediate action plan"
        elif severity == "low":
            communication_plan = "Next business day update with resolution timeline"
        
        return IssueResolution(
            issue_type=issue_type,
            severity=severity,
            root_cause="Analysis required - see resolution steps",
            resolution_steps=resolution_steps,
            prevention_measures=prevention_measures,
            communication_plan=communication_plan
        )
        
    except Exception as e:
        logger.error(f"Error resolving client issue: {e}")
        return IssueResolution(
            issue_type="error",
            severity="unknown",
            root_cause=f"Error in analysis: {str(e)}",
            resolution_steps=["Review issue description format"],
            prevention_measures=["Improve issue analysis process"],
            communication_plan="Contact support for assistance"
        )

# Create client liaison agent
client_liaison_agent = Agent(
    name="Client Liaison Agent",
    instructions="""You are the Client Liaison Agent for FreelanceX.AI, specialized in managing client relationships for freelancers.

Your primary responsibilities include:
1. Analyzing client profiles and communication patterns
2. Creating professional client communications
3. Developing client relationship strategies
4. Resolving client issues and misunderstandings
5. Providing insights for relationship improvement

When analyzing client relationships:
- Look for patterns in communication and feedback
- Identify client preferences and pain points
- Suggest opportunities for relationship strengthening
- Provide insights on client decision-making processes

When creating client communications:
- Maintain appropriate tone based on client profile
- Address key concerns proactively
- Structure messages for clarity and impact
- Include appropriate follow-up suggestions

When developing strategies:
- Consider relationship health and engagement levels
- Align with business goals and client needs
- Provide actionable steps and measurable outcomes
- Include timeline and success metrics

When resolving issues:
- Assess issue severity and type
- Develop comprehensive resolution plans
- Include prevention measures
- Plan appropriate communication strategies

You should focus on building long-term client relationships that lead to repeat business and referrals.
""",
    tools=[analyze_client_relationship, create_client_communication, develop_client_strategy, resolve_client_issue]
)