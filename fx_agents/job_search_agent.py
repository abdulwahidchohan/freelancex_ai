"""FreelanceX.AI Job Search Agent - OpenAI Agents SDK Implementation
Specialized agent for finding and analyzing freelance opportunities
"""

# Import Agent and tool from the package
from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class JobSearchCriteria(BaseModel):
    """Criteria for job search"""
    keywords: str
    budget_range: Optional[str] = "any"
    location: Optional[str] = "remote"
    platforms: Optional[List[str]] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None

class JobListing(BaseModel):
    """Job listing information"""
    title: str
    budget: str
    description: str
    client_rating: str
    posted: str
    platform: str
    url: Optional[str] = None

@tool
def search_jobs(criteria: JobSearchCriteria) -> List[JobListing]:
    """Search for freelance jobs matching the given criteria
    
    Args:
        criteria: The search criteria including keywords, budget range, location, etc.
    
    Returns:
        List of job listings matching the criteria
    """
    try:
        # Simulate job search results (in real implementation, integrate with job boards)
        sample_jobs = [
            JobListing(
                title=f"{criteria.keywords} - Remote Opportunity", 
                budget="$3,000 - $5,000",
                description=f"Looking for experienced {criteria.keywords} for exciting project",
                client_rating="4.8/5",
                posted="2 days ago",
                platform="Upwork",
                url="https://www.upwork.com/jobs/example1"
            ),
            JobListing(
                title=f"Senior {criteria.keywords} Position",
                budget="$5,000 - $8,000", 
                description=f"Established company seeking {criteria.keywords} expert",
                client_rating="4.9/5",
                posted="1 day ago",
                platform="Fiverr",
                url="https://www.fiverr.com/jobs/example2"
            ),
            JobListing(
                title=f"{criteria.keywords} Freelance Project",
                budget="$2,000 - $4,000",
                description=f"Startup looking for talented {criteria.keywords}",
                client_rating="4.6/5", 
                posted="3 hours ago",
                platform="LinkedIn",
                url="https://www.linkedin.com/jobs/example3"
            )
        ]
        
        # Filter by budget if specified
        if criteria.budget_range and criteria.budget_range.lower() != "any":
            if criteria.budget_range.lower() == "low":
                sample_jobs = [job for job in sample_jobs if "$2,000" in job.budget]
            elif criteria.budget_range.lower() == "medium":
                sample_jobs = [job for job in sample_jobs if "$3,000" in job.budget]
            elif criteria.budget_range.lower() == "high":
                sample_jobs = [job for job in sample_jobs if "$5,000" in job.budget]
        
        # Filter by platform if specified
        if criteria.platforms:
            sample_jobs = [job for job in sample_jobs if job.platform in criteria.platforms]
            
        return sample_jobs
        
    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}")
        return []

@tool
def analyze_job_market(keywords: str) -> Dict[str, Any]:
    """Analyze the job market for specific skills or roles
    
    Args:
        keywords: Skills or job roles to analyze (e.g., "Python developer", "UX designer")
    
    Returns:
        Market analysis including demand, average rates, and trends
    """
    try:
        # Simulate market analysis (in real implementation, use actual data sources)
        analysis = {
            "demand_level": "high",
            "avg_hourly_rate": "$45-65",
            "avg_project_rate": "$3,000-$7,000",
            "trending_platforms": ["Upwork", "LinkedIn", "Toptal"],
            "growing_niches": [f"{keywords} for startups", f"AI-assisted {keywords}"],
            "required_skills": ["Communication", "Time management", "Portfolio presentation"],
            "market_outlook": f"The market for {keywords} shows strong growth potential over the next 6-12 months, with increasing demand from tech startups and established companies undergoing digital transformation."
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing job market: {str(e)}")
        return {"error": str(e)}

# Create job search agent
job_search_agent = Agent(
    name="Job Search Agent",
    instructions="""You are a specialized Job Search Agent for FreelanceX.AI, focused on helping freelancers find relevant opportunities.

Your capabilities include:
1. Searching for freelance jobs across multiple platforms based on keywords, budget, and other criteria
2. Analyzing job market trends and demand for specific skills
3. Providing insights on competitive rates and growing niches

When responding to users:
- Always provide structured, easy-to-read job listings
- Include relevant details like budget, client rating, and posting date
- Offer actionable advice on how to apply for promising opportunities
- Suggest improvements to search criteria if results are limited

Use the search_jobs tool to find specific opportunities and the analyze_job_market tool for broader market insights.

Ensure all responses are tailored to freelancers' needs and provide practical next steps.""",
    tools=[search_jobs, analyze_job_market]
)