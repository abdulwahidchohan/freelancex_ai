import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from core.base_agent import BaseAgent, AgentStatus
import re

@dataclass
class JobListing:
    """Structured job listing data"""
    id: str
    title: str
    company: str
    platform: str
    budget: float
    currency: str
    description: str
    skills_required: List[str]
    posted_date: str
    deadline: Optional[str]
    job_type: str
    experience_level: str
    location: str
    remote_allowed: bool
    hourly_rate: Optional[float]
    fixed_price: Optional[float]
    estimated_hours: Optional[int]
    client_rating: Optional[float]
    proposals_count: Optional[int]
    match_score: float = 0.0

class JobSearchAgent(BaseAgent):
    """
    Enhanced JobSearchAgent for FreelanceX.AI
    Features: Real-time job alerts, cross-platform synchronization, AI-powered skills matching
    """
    
    def __init__(self):
        super().__init__("JobSearchAgent", "job_search")
        
        # Platform configurations
        self.supported_platforms = {
            'upwork': {
                'api_endpoint': 'https://www.upwork.com/api/profiles/v1/jobs/search',
                'auth_required': True,
                'rate_limit': 100,  # requests per hour
                'last_request': None
            },
            'freelancer': {
                'api_endpoint': 'https://www.freelancer.com/api/projects/0.1/projects',
                'auth_required': True,
                'rate_limit': 1000,
                'last_request': None
            },
            'fiverr': {
                'api_endpoint': 'https://api.fiverr.com/v1/gigs/search',
                'auth_required': True,
                'rate_limit': 500,
                'last_request': None
            },
            'linkedin': {
                'api_endpoint': 'https://api.linkedin.com/v2/jobPostings',
                'auth_required': True,
                'rate_limit': 200,
                'last_request': None
            },
            'toptal': {
                'api_endpoint': 'https://www.toptal.com/api/v1/jobs',
                'auth_required': True,
                'rate_limit': 50,
                'last_request': None
            }
        }
        
        # Search configuration
        self.search_filters = {
            'keywords': [],
            'budget_range': {'min': 0, 'max': float('inf')},
            'job_type': 'All',
            'experience_level': 'All',
            'location': 'All',
            'remote_only': False,
            'min_client_rating': 0.0,
            'max_proposals': float('inf'),
            'posted_within_days': 30
        }
        
        # User profile for AI-powered matching
        self.user_profile = {
            'skills': [],
            'experience_years': 0,
            'preferred_hourly_rate': 0,
            'preferred_project_size': 'medium',
            'industries': [],
            'certifications': [],
            'portfolio_keywords': [],
            'success_rate': 0.0,
            'past_projects': []
        }
        
        # Real-time alert system
        self.alert_subscribers = {}
        self.alert_frequency = 300  # 5 minutes
        self.last_alert_check = datetime.now()
        
        # Job cache and analytics
        self.job_cache: Dict[str, JobListing] = {}
        self.search_analytics = {
            'total_searches': 0,
            'jobs_found': 0,
            'successful_matches': 0,
            'platforms_searched': [],
            'avg_match_score': 0.0
        }
        
        self.logger.info("JobSearchAgent initialized with multi-platform support")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute job search related tasks"""
        start_time = datetime.now()
        task_type = task.get('type', 'search')
        
        try:
            if task_type == 'search_jobs':
                result = await self._search_jobs(task.get('filters', {}))
            elif task_type == 'get_job_details':
                result = await self._get_job_details(task.get('job_id'))
            elif task_type == 'setup_alerts':
                result = await self._setup_alerts(task.get('alert_config'))
            elif task_type == 'update_profile':
                result = await self._update_user_profile(task.get('profile_data'))
            elif task_type == 'analyze_market':
                result = await self._analyze_job_market(task.get('criteria'))
            else:
                result = {"status": "error", "message": f"Unknown task type: {task_type}"}
                
            # Update performance metrics
            response_time = (datetime.now() - start_time).total_seconds()
            success = result.get('status') == 'success'
            self.update_performance_metrics(success, response_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def self_diagnose(self) -> Dict[str, Any]:
        """Perform self-diagnosis for the JobSearchAgent"""
        diagnosis = {
            "agent_health": "healthy",
            "needs_repair": False,
            "issues": [],
            "recommendations": []
        }
        
        # Check API connectivity
        for platform, config in self.supported_platforms.items():
            if not await self._test_platform_connectivity(platform):
                diagnosis["issues"].append(f"Cannot connect to {platform}")
                diagnosis["agent_health"] = "degraded"
        
        # Check cache size
        if len(self.job_cache) > 10000:
            diagnosis["recommendations"].append("Clear job cache to improve performance")
            
        # Check search performance
        if self.performance_metrics["success_rate"] < 0.8:
            diagnosis["needs_repair"] = True
            diagnosis["recommendations"].append("Review and update search algorithms")
            
        return diagnosis

    async def _search_jobs(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search for jobs across all platforms with AI-powered matching"""
        self.status = AgentStatus.BUSY
        
        # Update search filters
        self._update_search_filters(filters)
        
        all_jobs = []
        search_results = {}
        
        # Search across all platforms
        for platform in self.supported_platforms.keys():
            try:
                platform_jobs = await self._search_platform(platform)
                all_jobs.extend(platform_jobs)
                search_results[platform] = len(platform_jobs)
                self.logger.info(f"Found {len(platform_jobs)} jobs on {platform}")
                
            except Exception as e:
                self.logger.error(f"Failed to search {platform}: {str(e)}")
                search_results[platform] = 0
        
        # Apply AI-powered skills matching
        matched_jobs = self._apply_ai_matching(all_jobs)
        
        # Sort by match score
        matched_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        # Update analytics
        self.search_analytics['total_searches'] += 1
        self.search_analytics['jobs_found'] += len(matched_jobs)
        self.search_analytics['platforms_searched'] = list(search_results.keys())
        if matched_jobs:
            self.search_analytics['avg_match_score'] = sum(job.match_score for job in matched_jobs) / len(matched_jobs)
        
        self.status = AgentStatus.IDLE
        
        return {
            "status": "success",
            "jobs": [self._job_to_dict(job) for job in matched_jobs[:50]],  # Return top 50
            "total_found": len(matched_jobs),
            "platform_results": search_results,
            "search_timestamp": datetime.now().isoformat()
        }

    async def _search_platform(self, platform: str) -> List[JobListing]:
        """Search jobs on a specific platform"""
        if platform not in self.supported_platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Check rate limiting
        if not self._check_rate_limit(platform):
            self.logger.warning(f"Rate limit exceeded for {platform}")
            return []
        
        # For demo purposes, return mock data
        # In production, this would make actual API calls
        mock_jobs = await self._get_mock_jobs(platform)
        
        # Update last request time
        self.supported_platforms[platform]['last_request'] = datetime.now()
        
        return mock_jobs

    async def _get_mock_jobs(self, platform: str) -> List[JobListing]:
        """Generate mock job listings for demonstration"""
        mock_jobs_data = [
            {
                "id": f"{platform}_job_001",
                "title": "Senior AI/ML Engineer",
                "company": "TechCorp AI",
                "budget": 8000,
                "currency": "USD",
                "description": "Looking for an experienced AI/ML engineer to develop cutting-edge machine learning models for our SaaS platform. Must have experience with Python, TensorFlow, and MLOps.",
                "skills_required": ["Python", "Machine Learning", "TensorFlow", "MLOps", "Data Science"],
                "posted_date": (datetime.now() - timedelta(days=1)).isoformat(),
                "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
                "job_type": "Contract",
                "experience_level": "Expert",
                "location": "Remote",
                "remote_allowed": True,
                "hourly_rate": 75.0,
                "estimated_hours": 120,
                "client_rating": 4.8,
                "proposals_count": 12
            },
            {
                "id": f"{platform}_job_002", 
                "title": "Full Stack Developer - React & Node.js",
                "company": "StartupXYZ",
                "budget": 5000,
                "currency": "USD",
                "description": "We need a full-stack developer to build our MVP. Experience with React, Node.js, and modern web technologies required.",
                "skills_required": ["React", "Node.js", "JavaScript", "PostgreSQL", "REST APIs"],
                "posted_date": (datetime.now() - timedelta(hours=6)).isoformat(),
                "deadline": (datetime.now() + timedelta(days=21)).isoformat(),
                "job_type": "Fixed Price",
                "experience_level": "Intermediate",
                "location": "Remote",
                "remote_allowed": True,
                "fixed_price": 5000.0,
                "estimated_hours": 80,
                "client_rating": 4.2,
                "proposals_count": 8
            },
            {
                "id": f"{platform}_job_003",
                "title": "Data Analysis & Visualization Expert",
                "company": "Analytics Pro",
                "budget": 3000,
                "currency": "USD", 
                "description": "Need help with data analysis and creating interactive dashboards. Python and Tableau experience preferred.",
                "skills_required": ["Python", "Data Analysis", "Tableau", "SQL", "Statistics"],
                "posted_date": (datetime.now() - timedelta(hours=2)).isoformat(),
                "deadline": (datetime.now() + timedelta(days=14)).isoformat(),
                "job_type": "Contract",
                "experience_level": "Intermediate",
                "location": "US Only",
                "remote_allowed": True,
                "hourly_rate": 45.0,
                "estimated_hours": 60,
                "client_rating": 4.5,
                "proposals_count": 5
            }
        ]
        
        jobs = []
        for job_data in mock_jobs_data:
            job = JobListing(
                id=job_data["id"],
                title=job_data["title"],
                company=job_data["company"],
                platform=platform,
                budget=job_data["budget"],
                currency=job_data["currency"],
                description=job_data["description"],
                skills_required=job_data["skills_required"],
                posted_date=job_data["posted_date"],
                deadline=job_data.get("deadline"),
                job_type=job_data["job_type"],
                experience_level=job_data["experience_level"],
                location=job_data["location"],
                remote_allowed=job_data["remote_allowed"],
                hourly_rate=job_data.get("hourly_rate"),
                fixed_price=job_data.get("fixed_price"),
                estimated_hours=job_data.get("estimated_hours"),
                client_rating=job_data.get("client_rating"),
                proposals_count=job_data.get("proposals_count")
            )
            jobs.append(job)
            
        return jobs

    def _apply_ai_matching(self, jobs: List[JobListing]) -> List[JobListing]:
        """Apply AI-powered skills matching to job listings"""
        user_skills = set(skill.lower() for skill in self.user_profile['skills'])
        
        for job in jobs:
            job.match_score = self._calculate_match_score(job, user_skills)
            
        return [job for job in jobs if job.match_score >= 0.3]  # Minimum 30% match

    def _calculate_match_score(self, job: JobListing, user_skills: set) -> float:
        """Calculate AI-powered match score for a job"""
        score = 0.0
        
        # Skills matching (40% weight)
        job_skills = set(skill.lower() for skill in job.skills_required)
        if job_skills:
            skill_match = len(user_skills.intersection(job_skills)) / len(job_skills)
            score += skill_match * 0.4
        
        # Budget compatibility (25% weight)
        if job.hourly_rate and self.user_profile['preferred_hourly_rate']:
            rate_diff = abs(job.hourly_rate - self.user_profile['preferred_hourly_rate'])
            rate_score = max(0, 1 - (rate_diff / self.user_profile['preferred_hourly_rate']))
            score += rate_score * 0.25
        
        # Experience level match (20% weight)
        exp_match = self._match_experience_level(job.experience_level)
        score += exp_match * 0.2
        
        # Client quality (10% weight)
        if job.client_rating:
            client_score = job.client_rating / 5.0
            score += client_score * 0.1
        
        # Competition level (5% weight)
        if job.proposals_count is not None:
            competition_score = max(0, 1 - (job.proposals_count / 50))  # Less competition is better
            score += competition_score * 0.05
        
        return min(1.0, score)

    def _match_experience_level(self, job_level: str) -> float:
        """Match user experience with job requirements"""
        user_years = self.user_profile['experience_years']
        
        level_mapping = {
            'entry': (0, 2),
            'intermediate': (2, 5),
            'expert': (5, float('inf'))
        }
        
        job_level_key = job_level.lower()
        if job_level_key in level_mapping:
            min_years, max_years = level_mapping[job_level_key]
            if min_years <= user_years <= max_years:
                return 1.0
            elif user_years > max_years:
                return 0.8  # Overqualified
            else:
                return 0.3  # Underqualified
        
        return 0.5  # Unknown level

    def _check_rate_limit(self, platform: str) -> bool:
        """Check if platform rate limit allows new request"""
        config = self.supported_platforms[platform]
        if not config['last_request']:
            return True
            
        time_since_last = datetime.now() - config['last_request']
        # Simple rate limiting - allow one request per minute
        return time_since_last.total_seconds() >= 60

    async def _test_platform_connectivity(self, platform: str) -> bool:
        """Test connectivity to a platform"""
        try:
            # Mock connectivity test
            await asyncio.sleep(0.1)  # Simulate network call
            return True
        except:
            return False

    def _update_search_filters(self, new_filters: Dict[str, Any]):
        """Update search filters with new criteria"""
        for key, value in new_filters.items():
            if key in self.search_filters:
                self.search_filters[key] = value

    async def _update_user_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile for better job matching"""
        try:
            for key, value in profile_data.items():
                if key in self.user_profile:
                    self.user_profile[key] = value
            
            # Store in memory with user consent
            self.store_memory("user_profile", self.user_profile, user_consent=True)
            
            return {"status": "success", "message": "Profile updated successfully"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _setup_alerts(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup real-time job alerts"""
        try:
            alert_id = f"alert_{datetime.now().timestamp()}"
            self.alert_subscribers[alert_id] = {
                "filters": alert_config.get("filters", {}),
                "frequency": alert_config.get("frequency", 3600),  # 1 hour default
                "email": alert_config.get("email"),
                "webhook": alert_config.get("webhook"),
                "created_at": datetime.now().isoformat(),
                "last_sent": None
            }
            
            return {"status": "success", "alert_id": alert_id, "message": "Alert setup successfully"}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _analyze_job_market(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze job market trends and provide insights"""
        try:
            # Perform market analysis based on cached jobs
            analysis = {
                "total_jobs_analyzed": len(self.job_cache),
                "average_budget": 0,
                "top_skills": {},
                "platform_distribution": {},
                "experience_level_demand": {},
                "remote_job_percentage": 0,
                "trends": []
            }
            
            if self.job_cache:
                jobs = list(self.job_cache.values())
                
                # Average budget
                budgets = [job.budget for job in jobs if job.budget > 0]
                if budgets:
                    analysis["average_budget"] = sum(budgets) / len(budgets)
                
                # Top skills
                skills_count = {}
                for job in jobs:
                    for skill in job.skills_required:
                        skills_count[skill] = skills_count.get(skill, 0) + 1
                
                analysis["top_skills"] = dict(sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10])
                
                # Platform distribution
                platform_count = {}
                for job in jobs:
                    platform_count[job.platform] = platform_count.get(job.platform, 0) + 1
                analysis["platform_distribution"] = platform_count
                
                # Remote job percentage
                remote_count = sum(1 for job in jobs if job.remote_allowed)
                analysis["remote_job_percentage"] = (remote_count / len(jobs)) * 100
            
            return {"status": "success", "analysis": analysis}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _job_to_dict(self, job: JobListing) -> Dict[str, Any]:
        """Convert JobListing to dictionary"""
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "platform": job.platform,
            "budget": job.budget,
            "currency": job.currency,
            "description": job.description,
            "skills_required": job.skills_required,
            "posted_date": job.posted_date,
            "deadline": job.deadline,
            "job_type": job.job_type,
            "experience_level": job.experience_level,
            "location": job.location,
            "remote_allowed": job.remote_allowed,
            "hourly_rate": job.hourly_rate,
            "fixed_price": job.fixed_price,
            "estimated_hours": job.estimated_hours,
            "client_rating": job.client_rating,
            "proposals_count": job.proposals_count,
            "match_score": job.match_score
        }

    async def check_and_send_alerts(self):
        """Check for new jobs and send alerts to subscribers"""
        current_time = datetime.now()
        
        for alert_id, alert_config in self.alert_subscribers.items():
            try:
                # Check if it's time to send alert
                last_sent = alert_config.get("last_sent")
                frequency = alert_config.get("frequency", 3600)
                
                if last_sent:
                    last_sent_time = datetime.fromisoformat(last_sent)
                    if (current_time - last_sent_time).total_seconds() < frequency:
                        continue
                
                # Search for jobs with alert filters
                alert_result = await self._search_jobs(alert_config["filters"])
                
                if alert_result["status"] == "success" and alert_result["jobs"]:
                    # Send alert (email, webhook, etc.)
                    await self._send_alert(alert_config, alert_result["jobs"])
                    alert_config["last_sent"] = current_time.isoformat()
                    
            except Exception as e:
                self.logger.error(f"Failed to process alert {alert_id}: {str(e)}")

    async def _send_alert(self, alert_config: Dict[str, Any], jobs: List[Dict[str, Any]]):
        """Send job alert to user"""
        # In a real implementation, this would send emails or webhook notifications
        self.logger.info(f"Sending alert with {len(jobs)} new jobs")
        
        # Store alert in memory for user to retrieve
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "job_count": len(jobs),
            "top_jobs": jobs[:5]  # Top 5 matches
        }
        
        self.store_memory(f"alert_{datetime.now().timestamp()}", alert_data)