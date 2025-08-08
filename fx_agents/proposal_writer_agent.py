"""
FreelanceX.AI Proposal Writer Agent - OpenAI Agents SDK Implementation  
Specialized agent for creating compelling proposals and cover letters
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ProposalRequest(BaseModel):
    """Request for proposal generation"""
    job_description: str
    freelancer_skills: str
    project_budget: Optional[str] = ""
    client_preferences: Optional[str] = ""
    proposal_tone: Optional[str] = "professional"
    include_portfolio: Optional[bool] = True

class RateCalculationRequest(BaseModel):
    """Request for rate calculation"""
    project_type: str
    experience_level: str
    project_duration: Optional[str] = "medium"
    client_budget: Optional[str] = ""
    market_segment: Optional[str] = "standard"

@tool
def generate_proposal(request: ProposalRequest) -> str:
    """Generate a compelling proposal for a freelance job
    
    Args:
        request: The proposal request containing job description, skills, and preferences
    
    Returns:
        Formatted proposal text
    """
    try:
        # Extract key information
        project_type = "development" if "develop" in request.job_description.lower() else "design"
        if "write" in request.job_description.lower() or "content" in request.job_description.lower():
            project_type = "writing"
        
        proposal = f"""Dear Client,

I'm excited to submit my proposal for your {project_type} project. After carefully reviewing your requirements, I'm confident I can deliver exceptional results that exceed your expectations.

**Why I'm the Perfect Fit:**
• Relevant Experience: {request.freelancer_skills}
• Proven Track Record: Successfully completed similar projects with 100% client satisfaction
• Professional Approach: Clear communication, timely delivery, and attention to detail

**My Understanding of Your Project:**
Based on your description, you need: {request.job_description[:200]}{"..." if len(request.job_description) > 200 else ""}

**My Approach:**
1. Project Planning: Detailed analysis and timeline creation
2. Regular Updates: Consistent communication throughout the project
3. Quality Assurance: Thorough testing and refinement
4. Timely Delivery: Commitment to meeting agreed deadlines
"""

        # Add budget section if provided
        if request.project_budget:
            proposal += f"""

**Investment:**
Based on your budget of {request.project_budget}, I propose a comprehensive solution that provides excellent value while ensuring top-quality deliverables.
"""

        # Add portfolio section if requested
        if request.include_portfolio:
            proposal += """

**Portfolio Highlights:**
• [Project 1]: [Brief description and outcomes]
• [Project 2]: [Brief description and outcomes]
• [Project 3]: [Brief description and outcomes]
"""

        # Add closing
        proposal += """

**Next Steps:**
I'd welcome the opportunity to discuss your project in more detail. Please feel free to schedule a call or ask any questions you might have.

Thank you for considering my proposal. I look forward to the possibility of working together!

Best regards,
[Your Name]
"""

        return proposal
        
    except Exception as e:
        logger.error(f"Error generating proposal: {str(e)}")
        return f"Error generating proposal: {str(e)}"

@tool
def calculate_optimal_rate(request: RateCalculationRequest) -> Dict[str, Any]:
    """Calculate optimal pricing for a freelance project
    
    Args:
        request: The rate calculation request containing project details
    
    Returns:
        Rate calculation results including hourly and project-based options
    """
    try:
        # Base rates by project type (in real implementation, use market data)
        base_rates = {
            "development": {"hourly": 50, "project": 2000},
            "design": {"hourly": 45, "project": 1500},
            "writing": {"hourly": 35, "project": 1000},
            "marketing": {"hourly": 40, "project": 1200},
            "consulting": {"hourly": 60, "project": 2500}
        }
        
        # Experience multipliers
        experience_multipliers = {
            "beginner": 0.7,
            "intermediate": 1.0,
            "expert": 1.5,
            "specialist": 2.0
        }
        
        # Duration factors
        duration_factors = {
            "short": 1.2,  # Short projects command premium
            "medium": 1.0, # Standard
            "long": 0.9    # Discount for long-term work
        }
        
        # Market segment adjustments
        market_adjustments = {
            "budget": 0.7,
            "standard": 1.0,
            "premium": 1.5,
            "enterprise": 2.0
        }
        
        # Get base rate for project type (default to development if not found)
        project_type = request.project_type.lower()
        base_rate = base_rates.get(project_type, base_rates["development"])
        
        # Apply multipliers
        experience_level = request.experience_level.lower()
        experience_multiplier = experience_multipliers.get(experience_level, 1.0)
        
        duration = request.project_duration.lower()
        duration_factor = duration_factors.get(duration, 1.0)
        
        market = request.market_segment.lower()
        market_adjustment = market_adjustments.get(market, 1.0)
        
        # Calculate rates
        hourly_rate = round(base_rate["hourly"] * experience_multiplier * market_adjustment)
        project_rate = round(base_rate["project"] * experience_multiplier * duration_factor * market_adjustment)
        
        # Estimate hours based on project type and duration
        estimated_hours = {
            "short": {"min": 10, "max": 20},
            "medium": {"min": 20, "max": 40},
            "long": {"min": 40, "max": 100}
        }.get(duration, {"min": 20, "max": 40})
        
        # Calculate range based on hourly
        hourly_total = {
            "min": hourly_rate * estimated_hours["min"],
            "max": hourly_rate * estimated_hours["max"]
        }
        
        # Adjust project rate if client budget is provided
        if request.client_budget and request.client_budget.strip():
            try:
                # Extract numeric value from budget string
                budget_value = float(''.join(filter(lambda x: x.isdigit() or x == '.', request.client_budget)))
                
                # Adjust project rate to be competitive but profitable
                if budget_value > project_rate * 1.2:  # If budget is significantly higher
                    project_rate = round(budget_value * 0.9)  # Ask for 90% of budget
                elif budget_value > project_rate:  # If budget is higher but not by much
                    project_rate = round(budget_value * 0.95)  # Ask for 95% of budget
                elif budget_value > project_rate * 0.8:  # If budget is slightly lower
                    project_rate = round(budget_value)  # Match the budget
                # Otherwise keep the calculated rate
            except ValueError:
                # If budget can't be parsed, ignore it
                pass
        
        return {
            "hourly_rate": f"${hourly_rate}",
            "project_rate": f"${project_rate}",
            "estimated_hours": estimated_hours,
            "hourly_total_range": f"${hourly_total['min']} - ${hourly_total['max']}",
            "recommended_option": "hourly" if hourly_total["min"] > project_rate else "project",
            "pricing_strategy": [
                "Present both hourly and project-based options to the client",
                f"Emphasize the value of your {experience_level} expertise",
                "Include a clear scope definition to prevent scope creep",
                "Consider offering tiered packages with different deliverables"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error calculating rate: {str(e)}")
        return {"error": str(e)}

# Create proposal writer agent
proposal_writer_agent = Agent(
    name="Proposal Writer Agent",
    instructions="""You are a specialized Proposal Writer Agent for FreelanceX.AI, focused on helping freelancers create compelling proposals and determine optimal pricing.

Your capabilities include:
1. Generating professional proposals tailored to specific job descriptions
2. Calculating optimal rates based on project type, experience level, and market factors
3. Providing pricing strategies and negotiation advice

When responding to users:
- Create personalized, compelling proposals that highlight relevant skills
- Provide clear pricing recommendations with strategic rationale
- Offer actionable advice on proposal structure and content
- Suggest effective negotiation strategies

Use the generate_proposal tool to create tailored proposals and the calculate_optimal_rate tool for pricing guidance.

Ensure all responses are professional, persuasive, and tailored to the specific job opportunity.""",
    tools=[generate_proposal, calculate_optimal_rate]
)