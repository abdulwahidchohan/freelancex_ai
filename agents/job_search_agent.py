import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import aiohttp
from dataclasses import dataclass
from enum import Enum
import json
import os

class JobPlatform(Enum):
    UPWORK = "upwork"
    FREELANCER = "freelancer"
    FIVERR = "fiverr"
    LINKEDIN = "linkedin"
    TOP_TAL = "toptal"
    GURU = "guru"
    PEOPLE_PER_HOUR = "peopleperhour"

@dataclass
class JobListing:
    id: str
    title: str
    description: str
    platform: JobPlatform
    budget_min: float
    budget_max: float
    skills_required: List[str]
    posted_date: datetime
    client_rating: Optional[float]
    project_type: str
    experience_level: str
    location: str
    url: str
    is_featured: bool = False
    proposal_count: int = 0

class JobSearchAgent:
    """
    Enhanced JobSearchAgent that scours global platforms for freelance job listings
    with real-time alerts, personalized recommendations, and competitive analysis.
    """
    
    def __init__(self, user_profile: Dict[str, Any]):
        self.user_profile = user_profile
        self.logger = logging.getLogger(__name__)
        self.supported_platforms = [platform.value for platform in JobPlatform]
        self.search_filters = self._initialize_filters()
        self.job_cache = {}
        self.alert_subscribers = []
        self.competitive_analysis_data = {}
        
    def _initialize_filters(self) -> Dict[str, Any]:
        """Initialize search filters based on user profile"""
        return {
            'keywords': self.user_profile.get('skills', []),
            'budget_range': {
                'min': self.user_profile.get('min_hourly_rate', 0) * 160,  # Monthly equivalent
                'max': self.user_profile.get('max_hourly_rate', float('inf')) * 160
            },
            'job_type': self.user_profile.get('preferred_job_types', ['All']),
            'experience_level': self.user_profile.get('experience_level', 'All'),
            'location_preference': self.user_profile.get('location_preference', 'Remote'),
            'excluded_keywords': self.user_profile.get('excluded_keywords', [])
        }
    
    async def search_jobs(self, platforms: Optional[List[str]] = None, 
                         keywords: Optional[List[str]] = None,
                         budget_range: Optional[Dict[str, float]] = None) -> List[JobListing]:
        """
        Search for jobs across multiple platforms with real-time data
        
        Args:
            platforms: List of platforms to search (None for all)
            keywords: Additional keywords to search for
            budget_range: Custom budget range override
            
        Returns:
            List of matching job listings
        """
        self.logger.info(f"Starting job search across platforms: {platforms or 'all'}")
        
        search_platforms = platforms or self.supported_platforms
        search_keywords = keywords or self.search_filters['keywords']
        search_budget = budget_range or self.search_filters['budget_range']
        
        all_jobs = []
        
        # Search each platform concurrently
        tasks = []
        for platform in search_platforms:
            if platform in self.supported_platforms:
                task = self._search_platform(platform, search_keywords, search_budget)
                tasks.append(task)
        
        # Wait for all platform searches to complete
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine and filter results
        for result in platform_results:
            if isinstance(result, list):
                all_jobs.extend(result)
            else:
                self.logger.error(f"Platform search failed: {result}")
        
        # Apply advanced filtering and ranking
        filtered_jobs = self._apply_advanced_filters(all_jobs)
        ranked_jobs = self._rank_jobs_by_relevance(filtered_jobs)
        
        self.logger.info(f"Found {len(ranked_jobs)} relevant jobs")
        return ranked_jobs
    
    async def _search_platform(self, platform: str, keywords: List[str], 
                             budget_range: Dict[str, float]) -> List[JobListing]:
        """Search a specific platform for jobs"""
        try:
            # In a real implementation, this would use platform-specific APIs
            # For now, we'll simulate the search with realistic data
            
            if platform == JobPlatform.UPWORK.value:
                return await self._search_upwork(keywords, budget_range)
            elif platform == JobPlatform.FREELANCER.value:
                return await self._search_freelancer(keywords, budget_range)
            elif platform == JobPlatform.FIVERR.value:
                return await self._search_fiverr(keywords, budget_range)
            elif platform == JobPlatform.LINKEDIN.value:
                return await self._search_linkedin(keywords, budget_range)
            else:
                return await self._search_generic_platform(platform, keywords, budget_range)
                
        except Exception as e:
            self.logger.error(f"Error searching {platform}: {str(e)}")
            return []
    
    async def _search_upwork(self, keywords: List[str], budget_range: Dict[str, float]) -> List[JobListing]:
        """Simulate Upwork job search"""
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        sample_jobs = [
            JobListing(
                id="upwork_001",
                title="Senior AI/ML Engineer for E-commerce Platform",
                description="We need an experienced AI engineer to develop recommendation systems...",
                platform=JobPlatform.UPWORK,
                budget_min=8000,
                budget_max=15000,
                skills_required=["Python", "Machine Learning", "TensorFlow", "E-commerce"],
                posted_date=datetime.now() - timedelta(hours=2),
                client_rating=4.8,
                project_type="Fixed-price",
                experience_level="Expert",
                location="Remote",
                url="https://upwork.com/jobs/001",
                is_featured=True,
                proposal_count=12
            ),
            JobListing(
                id="upwork_002",
                title="Full-Stack Developer for SaaS Application",
                description="Looking for a skilled developer to build a modern SaaS platform...",
                platform=JobPlatform.UPWORK,
                budget_min=5000,
                budget_max=12000,
                skills_required=["React", "Node.js", "PostgreSQL", "AWS"],
                posted_date=datetime.now() - timedelta(hours=6),
                client_rating=4.5,
                project_type="Hourly",
                experience_level="Intermediate",
                location="Remote",
                url="https://upwork.com/jobs/002",
                is_featured=False,
                proposal_count=8
            )
        ]
        
        return self._filter_jobs_by_criteria(sample_jobs, keywords, budget_range)
    
    async def _search_freelancer(self, keywords: List[str], budget_range: Dict[str, float]) -> List[JobListing]:
        """Simulate Freelancer.com job search"""
        await asyncio.sleep(0.3)
        
        sample_jobs = [
            JobListing(
                id="freelancer_001",
                title="Data Scientist for Financial Analysis",
                description="Need a data scientist to analyze financial data and create predictive models...",
                platform=JobPlatform.FREELANCER,
                budget_min=6000,
                budget_max=10000,
                skills_required=["Python", "Pandas", "Scikit-learn", "Financial Analysis"],
                posted_date=datetime.now() - timedelta(hours=1),
                client_rating=4.7,
                project_type="Fixed-price",
                experience_level="Expert",
                location="Remote",
                url="https://freelancer.com/jobs/001",
                is_featured=True,
                proposal_count=15
            )
        ]
        
        return self._filter_jobs_by_criteria(sample_jobs, keywords, budget_range)
    
    async def _search_fiverr(self, keywords: List[str], budget_range: Dict[str, float]) -> List[JobListing]:
        """Simulate Fiverr job search"""
        await asyncio.sleep(0.2)
        
        sample_jobs = [
            JobListing(
                id="fiverr_001",
                title="Logo Design and Brand Identity Package",
                description="Looking for a creative designer to create a complete brand identity...",
                platform=JobPlatform.FIVERR,
                budget_min=200,
                budget_max=500,
                skills_required=["Adobe Illustrator", "Logo Design", "Brand Identity"],
                posted_date=datetime.now() - timedelta(hours=3),
                client_rating=4.9,
                project_type="Fixed-price",
                experience_level="Intermediate",
                location="Remote",
                url="https://fiverr.com/gigs/001",
                is_featured=False,
                proposal_count=25
            )
        ]
        
        return self._filter_jobs_by_criteria(sample_jobs, keywords, budget_range)
    
    async def _search_linkedin(self, keywords: List[str], budget_range: Dict[str, float]) -> List[JobListing]:
        """Simulate LinkedIn job search"""
        await asyncio.sleep(0.4)
        
        sample_jobs = [
            JobListing(
                id="linkedin_001",
                title="Senior Software Engineer - Remote",
                description="Join our growing team as a senior software engineer...",
                platform=JobPlatform.LINKEDIN,
                budget_min=120000,
                budget_max=180000,
                skills_required=["Java", "Spring Boot", "Microservices", "Kubernetes"],
                posted_date=datetime.now() - timedelta(hours=4),
                client_rating=4.6,
                project_type="Full-time",
                experience_level="Senior",
                location="Remote",
                url="https://linkedin.com/jobs/001",
                is_featured=True,
                proposal_count=45
            )
        ]
        
        return self._filter_jobs_by_criteria(sample_jobs, keywords, budget_range)
    
    async def _search_generic_platform(self, platform: str, keywords: List[str], 
                                     budget_range: Dict[str, float]) -> List[JobListing]:
        """Generic platform search implementation"""
        await asyncio.sleep(0.3)
        return []
    
    def _filter_jobs_by_criteria(self, jobs: List[JobListing], keywords: List[str], 
                                budget_range: Dict[str, float]) -> List[JobListing]:
        """Filter jobs based on keywords and budget"""
        filtered = []
        
        for job in jobs:
            # Check budget range
            if not (budget_range['min'] <= job.budget_max <= budget_range['max']):
                continue
            
            # Check keywords
            if keywords:
                job_text = f"{job.title} {job.description}".lower()
                if not any(keyword.lower() in job_text for keyword in keywords):
                    continue
            
            # Check excluded keywords
            if self.search_filters['excluded_keywords']:
                job_text = f"{job.title} {job.description}".lower()
                if any(excluded.lower() in job_text for excluded in self.search_filters['excluded_keywords']):
                    continue
            
            filtered.append(job)
        
        return filtered
    
    def _apply_advanced_filters(self, jobs: List[JobListing]) -> List[JobListing]:
        """Apply advanced filtering based on user preferences"""
        filtered = jobs
        
        # Filter by experience level
        if self.search_filters['experience_level'] != 'All':
            filtered = [
                job for job in filtered
                if job.experience_level.lower() == self.search_filters['experience_level'].lower()
            ]
        
        # Filter by location preference
        if self.search_filters['location_preference'] == 'Remote':
            filtered = [
                job for job in filtered
                if 'remote' in job.location.lower() or job.location.lower() == 'remote'
            ]
        
        return filtered
    
    def _rank_jobs_by_relevance(self, jobs: List[JobListing]) -> List[JobListing]:
        """Rank jobs by relevance score based on multiple factors"""
        def calculate_relevance_score(job: JobListing) -> float:
            score = 0.0
            
            # Skills match (40% weight)
            user_skills = set(self.user_profile.get('skills', []))
            job_skills = set(job.skills_required)
            skill_match_ratio = len(user_skills.intersection(job_skills)) / len(job_skills) if job_skills else 0
            score += skill_match_ratio * 0.4
            
            # Budget fit (25% weight)
            user_avg_rate = (self.user_profile.get('min_hourly_rate', 0) + self.user_profile.get('max_hourly_rate', 100)) / 2
            job_avg_budget = (job.budget_min + job.budget_max) / 2
            budget_fit = min(1.0, job_avg_budget / (user_avg_rate * 160)) if user_avg_rate > 0 else 0.5
            score += budget_fit * 0.25
            
            # Recency (15% weight)
            hours_ago = (datetime.now() - job.posted_date).total_seconds() / 3600
            recency_score = max(0, 1 - (hours_ago / 24))  # Decay over 24 hours
            score += recency_score * 0.15
            
            # Client rating (10% weight)
            score += (job.client_rating or 0) / 5.0 * 0.1
            
            # Featured bonus (5% weight)
            if job.is_featured:
                score += 0.05
            
            # Competition factor (5% weight)
            competition_score = max(0, 1 - (job.proposal_count / 50))  # Fewer proposals = better
            score += competition_score * 0.05
            
            return score
        
        # Sort by relevance score
        ranked_jobs = sorted(jobs, key=calculate_relevance_score, reverse=True)
        return ranked_jobs
    
    async def get_competitive_analysis(self, job: JobListing) -> Dict[str, Any]:
        """Analyze competition for a specific job"""
        analysis = {
            'job_id': job.id,
            'total_proposals': job.proposal_count,
            'competition_level': self._assess_competition_level(job.proposal_count),
            'recommended_bid_range': self._calculate_bid_range(job),
            'time_to_apply': self._calculate_urgency_score(job),
            'success_probability': self._estimate_success_probability(job),
            'market_demand': self._assess_market_demand(job.skills_required)
        }
        
        return analysis
    
    def _assess_competition_level(self, proposal_count: int) -> str:
        """Assess competition level based on proposal count"""
        if proposal_count < 5:
            return "Low"
        elif proposal_count < 15:
            return "Medium"
        elif proposal_count < 30:
            return "High"
        else:
            return "Very High"
    
    def _calculate_bid_range(self, job: JobListing) -> Dict[str, float]:
        """Calculate recommended bid range"""
        avg_budget = (job.budget_min + job.budget_max) / 2
        
        # Competitive bidding strategy
        if job.proposal_count < 10:
            # Low competition - can bid higher
            return {
                'min': avg_budget * 0.8,
                'max': avg_budget * 1.1,
                'recommended': avg_budget * 0.95
            }
        else:
            # High competition - bid competitively
            return {
                'min': avg_budget * 0.7,
                'max': avg_budget * 0.9,
                'recommended': avg_budget * 0.8
            }
    
    def _calculate_urgency_score(self, job: JobListing) -> float:
        """Calculate urgency score for job application"""
        hours_ago = (datetime.now() - job.posted_date).total_seconds() / 3600
        
        if hours_ago < 2:
            return 1.0  # Very urgent
        elif hours_ago < 6:
            return 0.8  # Urgent
        elif hours_ago < 24:
            return 0.6  # Moderate
        else:
            return 0.3  # Low urgency
    
    def _estimate_success_probability(self, job: JobListing) -> float:
        """Estimate probability of winning the job"""
        base_probability = 0.3
        
        # Adjust based on skills match
        user_skills = set(self.user_profile.get('skills', []))
        job_skills = set(job.skills_required)
        skill_match_ratio = len(user_skills.intersection(job_skills)) / len(job_skills) if job_skills else 0
        base_probability += skill_match_ratio * 0.3
        
        # Adjust based on competition
        if job.proposal_count < 5:
            base_probability += 0.2
        elif job.proposal_count > 20:
            base_probability -= 0.1
        
        # Adjust based on client rating
        if job.client_rating and job.client_rating > 4.5:
            base_probability += 0.1
        
        return min(1.0, max(0.0, base_probability))
    
    def _assess_market_demand(self, skills: List[str]) -> Dict[str, str]:
        """Assess market demand for required skills"""
        # This would typically use real market data
        demand_levels = {}
        for skill in skills:
            # Simulate demand assessment
            if skill.lower() in ['python', 'machine learning', 'ai', 'react']:
                demand_levels[skill] = "High"
            elif skill.lower() in ['javascript', 'node.js', 'aws']:
                demand_levels[skill] = "Medium"
            else:
                demand_levels[skill] = "Moderate"
        
        return demand_levels
    
    async def setup_job_alerts(self, alert_criteria: Dict[str, Any]) -> str:
        """Set up real-time job alerts"""
        alert_id = f"alert_{len(self.alert_subscribers) + 1}"
        
        alert_config = {
            'id': alert_id,
            'criteria': alert_criteria,
            'created_at': datetime.now(),
            'is_active': True
        }
        
        self.alert_subscribers.append(alert_config)
        self.logger.info(f"Job alert created: {alert_id}")
        
        return alert_id
    
    async def get_daily_job_digest(self) -> Dict[str, Any]:
        """Generate daily job digest for user"""
        # Get jobs from the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        
        # This would typically query cached job data
        recent_jobs = []  # Placeholder for actual implementation
        
        digest = {
            'date': datetime.now().date(),
            'total_jobs_found': len(recent_jobs),
            'top_opportunities': recent_jobs[:5],
            'market_trends': self._analyze_market_trends(),
            'recommendations': self._generate_recommendations(recent_jobs)
        }
        
        return digest
    
    def _analyze_market_trends(self) -> Dict[str, Any]:
        """Analyze current market trends"""
        return {
            'hot_skills': ['AI/ML', 'React', 'Python', 'DevOps'],
            'rising_demand': ['Blockchain', 'Cybersecurity', 'Data Science'],
            'average_rates': {
                'entry_level': 25,
                'intermediate': 45,
                'expert': 85
            }
        }
    
    def _generate_recommendations(self, jobs: List[JobListing]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not jobs:
            recommendations.append("Consider expanding your search criteria or updating your skills")
        
        if len(jobs) < 5:
            recommendations.append("Market seems slow - focus on networking and skill development")
        
        recommendations.append("Update your portfolio with recent projects to increase visibility")
        
        return recommendations