#!/usr/bin/env python3
"""
FreelanceX.AI Enhanced Proposal Writer Agent - OpenAI Agents SDK Implementation
Dynamic proposal writer agent for creating compelling freelance proposals
"""

from agents import Agent, function_tool as tool
from functools import partial
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

# Use non-strict schema to allow Dict/Any parameters
tool = partial(tool, strict_mode=False)

logger = logging.getLogger(__name__)

class ProposalRequest(BaseModel):
    """Proposal request model"""
    job_title: str = Field(..., description="Job title")
    job_description: str = Field(..., description="Job description")
    client_budget: Optional[str] = Field(None, description="Client's budget range")
    freelancer_skills: List[str] = Field(default_factory=list, description="Freelancer's skills")
    freelancer_experience: str = Field(..., description="Freelancer's experience level")
    project_duration: Optional[str] = Field(None, description="Expected project duration")
    proposal_type: str = Field("standard", description="Type of proposal (standard, detailed, creative)")
    client_requirements: Optional[List[str]] = Field(default_factory=list, description="Specific client requirements")

class ProposalSection(BaseModel):
    """Proposal section model"""
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    order: int = Field(..., description="Section order")

class Proposal(BaseModel):
    """Complete proposal model"""
    title: str = Field(..., description="Proposal title")
    introduction: str = Field(..., description="Introduction section")
    approach: str = Field(..., description="Approach and methodology")
    timeline: str = Field(..., description="Project timeline")
    pricing: str = Field(..., description="Pricing information")
    deliverables: List[str] = Field(default_factory=list, description="Project deliverables")
    qualifications: str = Field(..., description="Qualifications and experience")
    call_to_action: str = Field(..., description="Call to action")
    sections: List[ProposalSection] = Field(default_factory=list, description="Additional sections")

class ProposalAnalysis(BaseModel):
    """Proposal analysis model"""
    strength_score: float = Field(..., description="Overall strength score (0-1)")
    strengths: List[str] = Field(default_factory=list, description="Proposal strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Areas for improvement")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations")
    competitive_advantage: List[str] = Field(default_factory=list, description="Competitive advantages")

@tool
def create_proposal(request: ProposalRequest) -> Proposal:
    """Create a compelling freelance proposal based on job requirements
    
    Args:
        request: Proposal request with job details and freelancer information
    
    Returns:
        Complete proposal with all sections
    """
    try:
        # Validate input
        if not request.job_title or not request.job_description:
            return Proposal(
                title="Proposal",
                introduction="Unable to create proposal due to insufficient information",
                approach="Please provide job title and description",
                timeline="N/A",
                pricing="N/A",
                qualifications="N/A",
                call_to_action="Please provide more details to create a proper proposal"
            )
        
        # Dynamic proposal generation based on job type and requirements
        job_lower = request.job_title.lower()
        description_lower = request.job_description.lower()
        
        # Determine proposal type and approach
        if "web" in job_lower or "frontend" in job_lower or "backend" in job_lower:
            project_type = "Web Development"
            approach = f"I'll approach this {project_type} project with a modern, scalable methodology. My process includes requirements analysis, design phase, development with best practices, testing, and deployment. I'll use the latest technologies and ensure responsive, user-friendly results."
        elif "design" in job_lower or "ui" in job_lower or "ux" in job_lower:
            project_type = "Design"
            approach = f"For this {project_type} project, I'll follow a user-centered design approach. This includes research, wireframing, prototyping, user testing, and final design delivery. I'll ensure the design is both beautiful and functional."
        elif "content" in job_lower or "writing" in job_lower or "copy" in job_lower:
            project_type = "Content Creation"
            approach = f"I'll tackle this {project_type} project with a strategic content approach. This includes research, content planning, writing with SEO best practices, editing, and optimization for maximum engagement."
        elif "data" in job_lower or "analysis" in job_lower or "python" in job_lower:
            project_type = "Data Analysis"
            approach = f"For this {project_type} project, I'll use a systematic approach: data collection, cleaning, analysis, visualization, and insights delivery. I'll ensure all findings are actionable and well-documented."
        else:
            project_type = "Project"
            approach = f"I'll approach this {project_type} with a structured methodology tailored to your specific needs. This includes planning, execution, quality assurance, and delivery with regular communication throughout."
        
        # Generate timeline based on project type and duration
        if request.project_duration:
            timeline = f"Based on the project scope, I estimate {request.project_duration} for completion. This includes planning, execution, testing, and delivery phases."
        else:
            timeline = "I'll provide a detailed timeline after understanding the full scope. Typically, projects of this nature take 2-4 weeks for quality delivery."
        
        # Generate pricing based on project type and budget
        if request.client_budget:
            pricing = f"I understand your budget is {request.client_budget}. I'll work within this range to deliver maximum value while ensuring quality results."
        else:
            pricing = "I offer competitive pricing based on project scope and complexity. I'll provide a detailed quote after understanding your specific requirements."
        
        # Generate deliverables based on project type
        deliverables = []
        if "web" in job_lower:
            deliverables = [
                "Fully functional website/application",
                "Responsive design for all devices",
                "Source code and documentation",
                "Testing and quality assurance",
                "Deployment and setup instructions"
            ]
        elif "design" in job_lower:
            deliverables = [
                "High-quality design files",
                "Multiple design concepts",
                "Style guide and brand guidelines",
                "Source files in multiple formats",
                "Design documentation"
            ]
        elif "content" in job_lower:
            deliverables = [
                "SEO-optimized content",
                "Multiple content pieces",
                "Content strategy document",
                "Keyword research and analysis",
                "Content calendar and guidelines"
            ]
        else:
            deliverables = [
                "Project deliverables as specified",
                "Progress reports and updates",
                "Quality assurance and testing",
                "Documentation and instructions",
                "Post-delivery support"
            ]
        
        # Generate qualifications section
        skills_text = ", ".join(request.freelancer_skills) if request.freelancer_skills else "relevant skills"
        qualifications = f"With {request.freelancer_experience} of experience and expertise in {skills_text}, I'm well-equipped to deliver exceptional results for your project. I have a proven track record of successful project completion and client satisfaction."
        
        # Generate call to action
        call_to_action = "I'm excited about the opportunity to work on your project and would love to discuss the details further. Let's schedule a call to explore how I can help bring your vision to life."
        
        # Create proposal sections
        sections = [
            ProposalSection(title="Project Understanding", content=f"I've carefully reviewed your {project_type} requirements and understand the scope and objectives.", order=1),
            ProposalSection(title="My Approach", content=approach, order=2),
            ProposalSection(title="Timeline", content=timeline, order=3),
            ProposalSection(title="Pricing", content=pricing, order=4),
            ProposalSection(title="Deliverables", content="I'll provide: " + "; ".join(deliverables), order=5),
            ProposalSection(title="Why Choose Me", content=qualifications, order=6)
        ]
        
        return Proposal(
            title=f"Proposal for {request.job_title}",
            introduction=f"Thank you for considering me for your {project_type} project. I'm excited about the opportunity to contribute to your success.",
            approach=approach,
            timeline=timeline,
            pricing=pricing,
            deliverables=deliverables,
            qualifications=qualifications,
            call_to_action=call_to_action,
            sections=sections
        )
        
    except Exception as e:
        logger.error(f"Error in proposal creation: {str(e)}")
        return Proposal(
            title="Proposal",
            introduction="I apologize, but I encountered an error while creating your proposal.",
            approach="Please try again with more detailed information.",
            timeline="N/A",
            pricing="N/A",
            qualifications="N/A",
            call_to_action="Please provide the job details again to create a proper proposal."
        )

@tool
def analyze_proposal(proposal: Proposal, job_requirements: List[str]) -> ProposalAnalysis:
    """Analyze a proposal for strengths, weaknesses, and improvement opportunities
    
    Args:
        proposal: The proposal to analyze
        job_requirements: List of job requirements to match against
    
    Returns:
        Detailed analysis of the proposal
    """
    try:
        # Validate input
        if not proposal or not job_requirements:
            return ProposalAnalysis(
                strength_score=0.0,
                strengths=[],
                weaknesses=["Insufficient information for analysis"],
                recommendations=["Provide complete proposal and job requirements"],
                competitive_advantage=[]
            )
        
        # Dynamic analysis based on proposal content and requirements
        strengths = []
        weaknesses = []
        recommendations = []
        competitive_advantages = []
        
        # Analyze proposal completeness
        if proposal.introduction and len(proposal.introduction) > 50:
            strengths.append("Strong introduction that shows understanding")
        else:
            weaknesses.append("Introduction could be more detailed")
            recommendations.append("Expand introduction to show deeper understanding")
        
        # Analyze approach section
        if proposal.approach and len(proposal.approach) > 100:
            strengths.append("Detailed approach methodology")
        else:
            weaknesses.append("Approach section needs more detail")
            recommendations.append("Provide more specific methodology and process")
        
        # Analyze timeline
        if proposal.timeline and "timeline" in proposal.timeline.lower():
            strengths.append("Clear timeline provided")
        else:
            weaknesses.append("Timeline could be more specific")
            recommendations.append("Provide detailed timeline with milestones")
        
        # Analyze pricing
        if proposal.pricing and "budget" in proposal.pricing.lower():
            strengths.append("Budget-conscious pricing approach")
        else:
            weaknesses.append("Pricing could be more transparent")
            recommendations.append("Provide clear pricing structure")
        
        # Analyze deliverables
        if proposal.deliverables and len(proposal.deliverables) >= 3:
            strengths.append("Comprehensive deliverables list")
        else:
            weaknesses.append("Deliverables could be more detailed")
            recommendations.append("List specific deliverables with descriptions")
        
        # Analyze qualifications
        if proposal.qualifications and len(proposal.qualifications) > 80:
            strengths.append("Strong qualifications presentation")
        else:
            weaknesses.append("Qualifications section needs enhancement")
            recommendations.append("Add specific achievements and relevant experience")
        
        # Match against job requirements
        requirements_covered = 0
        for requirement in job_requirements:
            if any(req.lower() in proposal.approach.lower() or req.lower() in proposal.qualifications.lower() for req in [requirement]):
                requirements_covered += 1
        
        if requirements_covered >= len(job_requirements) * 0.8:
            strengths.append("Good coverage of job requirements")
        else:
            weaknesses.append("Some job requirements not addressed")
            recommendations.append("Address all job requirements specifically")
        
        # Generate competitive advantages
        if len(proposal.deliverables) > 4:
            competitive_advantages.append("Comprehensive deliverables")
        if "experience" in proposal.qualifications.lower():
            competitive_advantages.append("Demonstrated experience")
        if "quality" in proposal.approach.lower():
            competitive_advantages.append("Quality-focused approach")
        
        # Calculate strength score
        total_criteria = 6  # introduction, approach, timeline, pricing, deliverables, qualifications
        met_criteria = len(strengths)
        strength_score = min(1.0, met_criteria / total_criteria)
        
        # Add general recommendations
        if strength_score < 0.7:
            recommendations.append("Consider adding client testimonials or portfolio examples")
            recommendations.append("Include specific metrics or achievements")
        
        return ProposalAnalysis(
            strength_score=strength_score,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            competitive_advantage=competitive_advantages
        )
        
    except Exception as e:
        logger.error(f"Error in proposal analysis: {str(e)}")
        return ProposalAnalysis(
            strength_score=0.0,
            strengths=[],
            weaknesses=["Analysis failed due to technical error"],
            recommendations=["Retry analysis with complete information"],
            competitive_advantage=[]
        )

# Create dynamic proposal writer agent
proposal_writer_agent = Agent(
    name="Proposal Writer Agent",
    instructions="""You are the Proposal Writer Agent for FreelanceX.AI, specialized in creating compelling freelance proposals.

Your role is to:
1. Create professional and persuasive proposals based on job requirements
2. Analyze proposals for strengths and improvement opportunities
3. Provide recommendations for proposal enhancement
4. Help freelancers stand out in competitive markets

Use the available tools to:
- create_proposal: Create a complete proposal based on job details and freelancer information
- analyze_proposal: Analyze existing proposals for strengths and areas of improvement

Always focus on creating proposals that are professional, persuasive, and tailored to specific job requirements.
""",
    tools=[create_proposal, analyze_proposal]
)
