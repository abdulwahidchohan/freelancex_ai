#!/usr/bin/env python3
"""
FreelanceX.AI API Server
FastAPI-based REST API for FreelanceX.AI functionality
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import uuid

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import FreelanceXAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FreelanceX.AI API",
    description="The world's most powerful AI Assistant for Freelancers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global FreelanceX.AI instances (in production, use proper session management)
freelancex_instances: Dict[str, FreelanceXAI] = {}

# Pydantic models for API requests/responses
class JobSearchRequest(BaseModel):
    platforms: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    budget_range: Optional[Dict[str, float]] = None

class JobSearchResponse(BaseModel):
    jobs: List[Dict[str, Any]]
    total_count: int
    search_criteria: Dict[str, Any]

class ResearchRequest(BaseModel):
    topic: str
    research_type: str = "business_strategy"

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    market_insights: Dict[str, Any]
    trend_analysis: Dict[str, Any]

class MathProblemRequest(BaseModel):
    problem_type: str
    problem_data: Dict[str, Any]

class MathProblemResponse(BaseModel):
    solution: str
    steps: List[str]
    answer: Any
    confidence: float
    verification: str

class FinancialAnalysisRequest(BaseModel):
    analysis_type: str
    data: Dict[str, Any]

class FinancialAnalysisResponse(BaseModel):
    analysis_type: str
    results: Dict[str, Any]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]

class UserProfileUpdateRequest(BaseModel):
    section: str
    data: Dict[str, Any]

class WorkHistoryRequest(BaseModel):
    title: str
    description: str
    client: str
    platform: str
    start_date: str
    end_date: Optional[str] = None
    budget: float
    skills_used: List[str] = []
    rating: Optional[float] = None
    feedback: Optional[str] = None
    status: str = "completed"

class LearningGoalRequest(BaseModel):
    skill_name: str
    target_level: str
    target_date: str
    current_progress: float = 0.0
    learning_resources: List[str] = []
    status: str = "active"

class FeedbackRequest(BaseModel):
    feedback_type: str = "general"
    content: str
    rating: Optional[float] = None
    category: str = "general"
    context: Dict[str, Any] = {}

class DailyDigestResponse(BaseModel):
    date: str
    job_market: Dict[str, Any]
    trending_topics: List[Dict[str, Any]]
    recommendations: Dict[str, Any]
    profile_summary: Dict[str, Any]
    system_status: Dict[str, Any]

class SystemStatusResponse(BaseModel):
    total_agents: int
    total_tasks: int
    task_status: Dict[str, int]
    active_negotiations: int
    total_requests: int
    system_health: str

# Dependency to get user ID from token
async def get_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token (simplified for demo)"""
    # In production, validate JWT token and extract user ID
    # For demo purposes, use the token as user ID
    return credentials.credentials

# Dependency to get FreelanceX.AI instance
async def get_freelancex(user_id: str = Depends(get_user_id)) -> FreelanceXAI:
    """Get or create FreelanceX.AI instance for user"""
    if user_id not in freelancex_instances:
        freelancex_instances[user_id] = FreelanceXAI(user_id)
        await freelancex_instances[user_id].initialize()
    
    return freelancex_instances[user_id]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FreelanceX.AI API",
        "version": "1.0.0"
    }

# Job Search endpoints
@app.post("/jobs/search", response_model=JobSearchResponse)
async def search_jobs(
    request: JobSearchRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Search for freelance jobs"""
    try:
        jobs = await freelancex.search_jobs(
            platforms=request.platforms,
            keywords=request.keywords,
            budget_range=request.budget_range
        )
        
        return JobSearchResponse(
            jobs=jobs,
            total_count=len(jobs),
            search_criteria={
                "platforms": request.platforms,
                "keywords": request.keywords,
                "budget_range": request.budget_range
            }
        )
    except Exception as e:
        logger.error(f"Error searching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/digest")
async def get_job_digest(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get daily job digest"""
    try:
        digest = await freelancex.job_search_agent.get_daily_job_digest()
        return digest
    except Exception as e:
        logger.error(f"Error getting job digest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Research endpoints
@app.post("/research/conduct", response_model=ResearchResponse)
async def conduct_research(
    request: ResearchRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Conduct research on a specific topic"""
    try:
        research = await freelancex.conduct_research(
            topic=request.topic,
            research_type=request.research_type
        )
        
        if "error" in research:
            raise HTTPException(status_code=500, detail=research["error"])
        
        return ResearchResponse(**research)
    except Exception as e:
        logger.error(f"Error conducting research: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/research/trending")
async def get_trending_topics(
    category: Optional[str] = None,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Get trending topics"""
    try:
        topics = await freelancex.web_search_agent.get_trending_topics(category)
        return {"trending_topics": topics}
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Math and Financial endpoints
@app.post("/math/solve", response_model=MathProblemResponse)
async def solve_math_problem(
    request: MathProblemRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Solve mathematical problems"""
    try:
        solution = await freelancex.solve_math_problem(
            problem_type=request.problem_type,
            problem_data=request.problem_data
        )
        
        if "error" in solution:
            raise HTTPException(status_code=500, detail=solution["error"])
        
        return MathProblemResponse(**solution)
    except Exception as e:
        logger.error(f"Error solving math problem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/financial/analyze", response_model=FinancialAnalysisResponse)
async def conduct_financial_analysis(
    request: FinancialAnalysisRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Conduct financial analysis"""
    try:
        analysis = await freelancex.conduct_financial_analysis(
            analysis_type=request.analysis_type,
            data=request.data
        )
        
        if "error" in analysis:
            raise HTTPException(status_code=500, detail=analysis["error"])
        
        return FinancialAnalysisResponse(**analysis)
    except Exception as e:
        logger.error(f"Error conducting financial analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# User Profile endpoints
@app.get("/profile")
async def get_profile(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get user profile"""
    try:
        profile = await freelancex.user_profile_manager.get_profile_data()
        return profile
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/profile")
async def update_profile(
    request: UserProfileUpdateRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Update user profile"""
    try:
        success = await freelancex.update_user_profile(
            section=request.section,
            data=request.data
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update profile")
        
        return {"status": "success", "message": "Profile updated successfully"}
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/summary")
async def get_profile_summary(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get profile summary"""
    try:
        summary = await freelancex.user_profile_manager.get_profile_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting profile summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/skill-gaps")
async def get_skill_gap_analysis(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get skill gap analysis"""
    try:
        analysis = await freelancex.get_skill_gap_analysis()
        return analysis
    except Exception as e:
        logger.error(f"Error getting skill gap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/profile/recommendations")
async def get_recommendations(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get personalized recommendations"""
    try:
        recommendations = await freelancex.user_profile_manager.get_personalized_recommendations()
        return recommendations
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Work History endpoints
@app.post("/work-history")
async def add_work_history(
    request: WorkHistoryRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Add work history entry"""
    try:
        work_data = request.dict()
        success = await freelancex.add_work_history(work_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add work history")
        
        return {"status": "success", "message": "Work history added successfully"}
    except Exception as e:
        logger.error(f"Error adding work history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/work-history")
async def get_work_history(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get work history"""
    try:
        profile = await freelancex.user_profile_manager.get_profile_data()
        return {"work_history": profile.get("work_history", [])}
    except Exception as e:
        logger.error(f"Error getting work history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Learning Goals endpoints
@app.post("/learning-goals")
async def add_learning_goal(
    request: LearningGoalRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Add learning goal"""
    try:
        goal_data = request.dict()
        success = await freelancex.add_learning_goal(goal_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to add learning goal")
        
        return {"status": "success", "message": "Learning goal added successfully"}
    except Exception as e:
        logger.error(f"Error adding learning goal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/learning-goals")
async def get_learning_goals(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get learning goals"""
    try:
        profile = await freelancex.user_profile_manager.get_profile_data()
        return {"learning_goals": profile.get("learning_goals", {})}
    except Exception as e:
        logger.error(f"Error getting learning goals: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/learning-goals/{goal_id}/progress")
async def update_learning_progress(
    goal_id: str,
    progress: float,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Update learning progress"""
    try:
        success = await freelancex.user_profile_manager.update_learning_progress(goal_id, progress)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update learning progress")
        
        return {"status": "success", "message": "Learning progress updated successfully"}
    except Exception as e:
        logger.error(f"Error updating learning progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Feedback endpoints
@app.post("/feedback")
async def submit_feedback(
    request: FeedbackRequest,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Submit user feedback"""
    try:
        feedback_data = request.dict()
        success = await freelancex.submit_feedback(feedback_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to submit feedback")
        
        return {"status": "success", "message": "Feedback submitted successfully"}
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Daily Digest endpoint
@app.get("/daily-digest", response_model=DailyDigestResponse)
async def get_daily_digest(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get daily digest"""
    try:
        digest = await freelancex.get_daily_digest()
        
        if "error" in digest:
            raise HTTPException(status_code=500, detail=digest["error"])
        
        return DailyDigestResponse(**digest)
    except Exception as e:
        logger.error(f"Error getting daily digest: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System endpoints
@app.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status(freelancex: FreelanceXAI = Depends(get_freelancex)):
    """Get system status"""
    try:
        status = await freelancex.get_system_status()
        
        if "error" in status:
            raise HTTPException(status_code=500, detail=status["error"])
        
        return SystemStatusResponse(**status)
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/collaboration-log")
async def get_collaboration_log(
    limit: int = 100,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Get collaboration log"""
    try:
        log = await freelancex.agent_collaboration_manager.get_collaboration_log(limit)
        return {"collaboration_log": log}
    except Exception as e:
        logger.error(f"Error getting collaboration log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Data export endpoint
@app.get("/export")
async def export_user_data(
    format: str = "json",
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Export user data"""
    try:
        data = await freelancex.export_user_data(format)
        return {"data": data, "format": format}
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task for daily routines
@app.post("/daily-routines/execute")
async def execute_daily_routines(
    background_tasks: BackgroundTasks,
    freelancex: FreelanceXAI = Depends(get_freelancex)
):
    """Execute daily routines"""
    try:
        # Add background task for daily routines
        background_tasks.add_task(execute_morning_routine, freelancex)
        
        return {"status": "success", "message": "Daily routines scheduled"}
    except Exception as e:
        logger.error(f"Error scheduling daily routines: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def execute_morning_routine(freelancex: FreelanceXAI):
    """Execute morning routine tasks"""
    try:
        logger.info("Executing morning routine...")
        
        # Get daily digest
        await freelancex.get_daily_digest()
        
        # Search for new jobs
        await freelancex.search_jobs()
        
        # Get trending topics
        await freelancex.web_search_agent.get_trending_topics()
        
        logger.info("Morning routine completed")
    except Exception as e:
        logger.error(f"Error executing morning routine: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("FreelanceX.AI API Server starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("FreelanceX.AI API Server shutting down...")

if __name__ == "__main__":
    # Run the API server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )