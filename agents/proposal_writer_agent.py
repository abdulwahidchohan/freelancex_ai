"""
FreelanceX.AI Proposal Writer Agent - OpenAI Agents SDK Implementation  
Specialized agent for creating compelling proposals and cover letters
"""

from agents import Agent, tool
import logging

logger = logging.getLogger(__name__)

@tool
def generate_proposal(job_description: str, freelancer_skills: str, project_budget: str = "") -> str:
    """Generate a compelling proposal for a freelance job
    
    Args:
        job_description: The job posting description
        freelancer_skills: Your relevant skills and experience
        project_budget: Budget mentioned in job posting (optional)
    
    Returns:
        Formatted proposal text
    """
    try:
        # Extract key information
        project_type = "development" if "develop" in job_description.lower() else "design"
        if "write" in job_description.lower() or "content" in job_description.lower():
            project_type = "writing"
        
        proposal = f"""Dear Client,

I'm excited to submit my proposal for your {project_type} project. After carefully reviewing your requirements, I'm confident I can deliver exceptional results that exceed your expectations.

**Why I'm the Perfect Fit:**
• Relevant Experience: {freelancer_skills}
• Proven Track Record: Successfully completed similar projects with 100% client satisfaction
• Professional Approach: Clear communication, timely delivery, and attention to detail

**My Understanding of Your Project:**
Based on your description, you need: {job_description[:200]}{"..." if len(job_description) > 200 else ""}

**My Approach:**
1. Project Planning: Detailed analysis and timeline creation
2. Regular Updates: Daily progress reports and milestone check-ins  
3. Quality Assurance: Thorough testing and refinement
4. Final Delivery: Complete project with documentation

**Timeline:** I can start immediately and deliver within your specified timeframe.
{"**Budget:** " + project_budget if project_budget else "**Budget:** Competitive rates based on project scope"}

I'd love to discuss this project further and answer any questions you may have. When would be a good time for a brief call?

Best regards,
[Your Name]

P.S. I'm available to start right away and guarantee your satisfaction with the final result."""

        return proposal
        
    except Exception as e:
        logger.error(f"Proposal generation error: {e}")
        return f"Error generating proposal: {str(e)}"

@tool
def suggest_pricing_strategy(project_description: str, complexity: str = "medium") -> str:
    """Suggest pricing strategy for a freelance project
    
    Args:
        project_description: Description of the project  
        complexity: Project complexity level ("simple", "medium", "complex")
    
    Returns:
        Pricing strategy recommendations
    """
    try:
        base_rates = {
            "simple": {"min": 500, "max": 2000},
            "medium": {"min": 2000, "max": 8000}, 
            "complex": {"min": 8000, "max": 25000}
        }
        
        rate_range = base_rates.get(complexity.lower(), base_rates["medium"])
        
        strategy = f"""Pricing Strategy for {complexity} project:

**Recommended Pricing Range:**
• Minimum: ${rate_range['min']:,}
• Maximum: ${rate_range['max']:,}
• Sweet Spot: ${int((rate_range['min'] + rate_range['max']) / 2):,}

**Pricing Approach:**
• Value-Based: Focus on the value you deliver, not just time
• Milestone-Based: Break payments into project milestones
• Include Revisions: 2-3 rounds of revisions included

**Negotiation Tips:**
• Start at the higher end of your range
• Be prepared to justify your pricing with your expertise
• Offer package deals for additional services
• Consider offering a small discount for quick payment

**Project Scope Considerations:**
Based on: {project_description[:150]}{"..." if len(project_description) > 150 else ""}

The complexity appears {complexity} due to the scope and requirements involved.

**Risk Factors:**
• Add 20% buffer for unexpected requirements
• Consider client's budget and payment history
• Factor in your current workload and availability"""

        return strategy
        
    except Exception as e:
        logger.error(f"Pricing strategy error: {e}")
        return f"Error creating pricing strategy: {str(e)}"

@tool
def optimize_proposal_content(proposal_text: str) -> str:
    """Optimize and improve proposal content for better engagement
    
    Args:
        proposal_text: The proposal text to optimize
    
    Returns:
        Optimized proposal with improvements
    """
    try:
        # Simple optimizations (in real implementation, use more sophisticated analysis)
        optimized = proposal_text
        
        # Improve language
        improvements = [
            ("good", "exceptional"),
            ("nice", "outstanding"), 
            ("I can", "I will"),
            ("I think", "I believe"),
            ("maybe", "definitely"),
            ("try to", "will")
        ]
        
        for old, new in improvements:
            optimized = optimized.replace(old, new)
        
        # Add engagement elements if missing
        if "?" not in optimized:
            optimized += "\n\nWhat questions do you have about my approach?"
        
        optimization_notes = """
**Optimization Improvements Made:**
• Strengthened language and confidence
• Added engaging questions
• Improved professional tone
• Enhanced value proposition

**Additional Suggestions:**
• Add specific examples from your portfolio
• Include client testimonials if available  
• Customize opening to mention client's company name
• Add a clear call-to-action
"""
        
        return f"{optimized}\n\n---\n{optimization_notes}"
        
    except Exception as e:
        logger.error(f"Content optimization error: {e}")
        return f"Error optimizing content: {str(e)}"

proposal_writer_agent = Agent(
    name="Proposal Writer Agent",
    handoff_description="Specialist for writing proposals, cover letters, and client communication",
    instructions="""You are an expert proposal writer specializing in freelance project proposals.

    Your expertise includes:
    - Writing compelling, personalized proposals
    - Pricing strategy and negotiation guidance
    - Client communication best practices
    - Proposal optimization and improvement
    - Cover letter creation

    Always focus on:
    - Understanding the client's specific needs
    - Highlighting relevant experience and skills
    - Creating value-focused messaging
    - Professional yet personable tone
    - Clear next steps and call-to-action

    Use your tools to generate, optimize, and price proposals effectively.""",
    
    tools=[generate_proposal, suggest_pricing_strategy, optimize_proposal_content]
)