import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import aiohttp
import requests
from bs4 import BeautifulSoup
import re

@dataclass
class JobListing:
    """Data class for job listing information"""
    id: str
    title: str
    company: str
    platform: str
    budget: float
    description: str
    skills_required: List[str]
    posted_date: datetime
    url: str
    location: str
    job_type: str
    experience_level: str
    estimated_duration: str
    client_rating: Optional[float] = None
    client_reviews: Optional[int] = None
    proposal_count: Optional[int] = None

class JobSearchAgent:
    """
    Enhanced JobSearchAgent for FreelanceX.AI
    
    Primary Role: Scour global platforms for freelance job listings tailored to the user's skills, 
    preferences, and goals.
    
    Features: Real-time job alerts, personalized recommendations, competitive salary analysis.
    Mode of Action: Leverages multiple sources (LinkedIn, Upwork, Fiverr, etc.) for cross-platform synchronization.
    Skills Matching: Recommends roles based on a user's expertise (e.g., AI/ML, web development, graphic design).
    """
    
    def __init__(self, user_profile: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.user_profile = user_profile or {}
        
        # Supported platforms with their API endpoints and scraping configurations
        self.supported_platforms = {
            'upwork': {
                'api_endpoint': 'https://www.upwork.com/api/v2/search/jobs',
                'scraping_enabled': True,
                'rate_limit': 100,  # requests per hour
                'last_request': None
            },
            'fiverr': {
                'api_endpoint': 'https://api.fiverr.com/v1/search/gigs',
                'scraping_enabled': True,
                'rate_limit': 100,
                'last_request': None
            },
            'freelancer': {
                'api_endpoint': 'https://www.freelancer.com/api/projects/0.1/projects',
                'scraping_enabled': True,
                'rate_limit': 100,
                'last_request': None
            },
            'linkedin': {
                'api_endpoint': 'https://api.linkedin.com/v2/jobs',
                'scraping_enabled': True,
                'rate_limit': 50,
                'last_request': None
            },
            'toptal': {
                'api_endpoint': 'https://www.toptal.com/api/jobs',
                'scraping_enabled': True,
                'rate_limit': 50,
                'last_request': None
            }
        }
        
        # Search filters and preferences
        self.search_filters = {
            'keywords': [],
            'skills': [],
            'budget_range': {'min': 0, 'max': float('inf')},
            'job_type': 'All',  # hourly, fixed, recurring
            'experience_level': 'All',  # entry, intermediate, expert
            'location_preference': 'remote',  # remote, onsite, hybrid
            'platforms': list(self.supported_platforms.keys()),
            'exclude_keywords': [],
            'client_rating_min': 0.0,
            'max_proposals': None
        }
        
        # Real-time alert settings
        self.alert_settings = {
            'enabled': True,
            'check_interval': 300,  # 5 minutes
            'notification_channels': ['email', 'push', 'webhook'],
            'last_check': datetime.now()
        }
        
        # Competitive analysis data
        self.market_data = {
            'average_rates': {},
            'demand_trends': {},
            'competition_levels': {},
            'last_updated': None
        }
        
        # Memory for learning from user behavior
        self.user_behavior_memory = {
            'applied_jobs': [],
            'ignored_jobs': [],
            'successful_applications': [],
            'preferences_learned': {}
        }

    def set_user_profile(self, profile: Dict[str, Any]):
        """Update user profile for personalized job matching"""
        self.user_profile = profile
        self.logger.info(f"Updated user profile for {profile.get('name', 'Unknown')}")
        
        # Auto-update search filters based on profile
        if 'skills' in profile:
            self.search_filters['skills'] = profile['skills']
        if 'preferred_rate' in profile:
            self.search_filters['budget_range']['min'] = profile['preferred_rate']
        if 'experience_level' in profile:
            self.search_filters['experience_level'] = profile['experience_level']

    def set_search_filters(self, **kwargs):
        """Set comprehensive search filters for job hunting"""
        for key, value in kwargs.items():
            if key in self.search_filters:
                self.search_filters[key] = value
        self.logger.info(f"Updated search filters: {kwargs}")

    async def find_jobs(self, platforms: Optional[List[str]] = None, 
                       use_ai_matching: bool = True) -> List[JobListing]:
        """
        Search for jobs across supported freelance platforms with AI-powered matching
        
        Args:
            platforms: Specific platforms to search. If None, searches all configured platforms
            use_ai_matching: Whether to use AI for job matching and ranking
            
        Returns:
            List of JobListing objects ranked by relevance
        """
        self.logger.info("Starting comprehensive job search across platforms...")
        
        if platforms:
            platforms = [p.lower() for p in platforms if p.lower() in self.supported_platforms]
        else:
            platforms = self.search_filters['platforms']
        
        all_jobs = []
        
        # Search each platform concurrently
        tasks = [self._search_platform(platform) for platform in platforms]
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for platform, result in zip(platforms, platform_results):
            if isinstance(result, Exception):
                self.logger.error(f"Error searching {platform}: {result}")
                continue
            all_jobs.extend(result)
        
        # Apply filters
        filtered_jobs = self._apply_filters(all_jobs)
        
        # AI-powered matching and ranking
        if use_ai_matching and self.user_profile:
            filtered_jobs = await self._ai_rank_jobs(filtered_jobs)
        
        # Update market data
        await self._update_market_data(filtered_jobs)
        
        self.logger.info(f"Found {len(filtered_jobs)} relevant jobs after filtering")
        return filtered_jobs

    async def _search_platform(self, platform: str) -> List[JobListing]:
        """Search a specific platform for jobs"""
        platform_config = self.supported_platforms[platform]
        
        # Rate limiting check
        if not self._check_rate_limit(platform):
            self.logger.warning(f"Rate limit reached for {platform}")
            return []
        
        try:
            # Try API first, fallback to scraping
            jobs = await self._api_search(platform)
            if not jobs:
                jobs = await self._scrape_platform(platform)
            
            self.supported_platforms[platform]['last_request'] = datetime.now()
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error searching {platform}: {e}")
            return []

    async def _api_search(self, platform: str) -> List[JobListing]:
        """Search platform using official API"""
        # This would implement actual API calls to each platform
        # For now, return sample data
        sample_jobs = [
            JobListing(
                id=f"{platform}_job_1",
                title="AI/ML Engineer",
                company="TechCorp",
                platform=platform,
                budget=5000.0,
                description="Looking for an experienced AI engineer to develop machine learning models",
                skills_required=["Python", "Machine Learning", "TensorFlow", "PyTorch"],
                posted_date=datetime.now() - timedelta(hours=2),
                url=f"https://{platform}.com/job/1",
                location="Remote",
                job_type="Fixed",
                experience_level="Expert",
                estimated_duration="2-3 months",
                client_rating=4.8,
                client_reviews=15,
                proposal_count=5
            ),
            JobListing(
                id=f"{platform}_job_2",
                title="Full-Stack Developer",
                company="StartupXYZ",
                platform=platform,
                budget=3000.0,
                description="Need a full-stack developer for web application development",
                skills_required=["JavaScript", "React", "Node.js", "MongoDB"],
                posted_date=datetime.now() - timedelta(hours=5),
                url=f"https://{platform}.com/job/2",
                location="Remote",
                job_type="Hourly",
                experience_level="Intermediate",
                estimated_duration="1-2 months",
                client_rating=4.5,
                client_reviews=8,
                proposal_count=12
            )
        ]
        
        return sample_jobs

    async def _scrape_platform(self, platform: str) -> List[JobListing]:
        """Fallback to web scraping if API is not available"""
        # This would implement web scraping for each platform
        # For now, return empty list
        return []

    def _apply_filters(self, jobs: List[JobListing]) -> List[JobListing]:
        """Apply comprehensive search filters to job listings"""
        filtered = jobs
        
        # Filter by keywords
        if self.search_filters['keywords']:
            filtered = [
                job for job in filtered
                if any(keyword.lower() in job.title.lower() or 
                      keyword.lower() in job.description.lower()
                      for keyword in self.search_filters['keywords'])
            ]
        
        # Filter by skills
        if self.search_filters['skills']:
            filtered = [
                job for job in filtered
                if any(skill.lower() in [req.lower() for req in job.skills_required]
                      for skill in self.search_filters['skills'])
            ]
        
        # Filter by budget range
        filtered = [
            job for job in filtered
            if self.search_filters['budget_range']['min'] <= job.budget <= self.search_filters['budget_range']['max']
        ]
        
        # Filter by job type
        if self.search_filters['job_type'] != 'All':
            filtered = [
                job for job in filtered
                if job.job_type.lower() == self.search_filters['job_type'].lower()
            ]
        
        # Filter by experience level
        if self.search_filters['experience_level'] != 'All':
            filtered = [
                job for job in filtered
                if job.experience_level.lower() == self.search_filters['experience_level'].lower()
            ]
        
        # Filter by client rating
        filtered = [
            job for job in filtered
            if job.client_rating is None or job.client_rating >= self.search_filters['client_rating_min']
        ]
        
        # Filter by proposal count
        if self.search_filters['max_proposals']:
            filtered = [
                job for job in filtered
                if job.proposal_count is None or job.proposal_count <= self.search_filters['max_proposals']
            ]
        
        # Exclude keywords
        if self.search_filters['exclude_keywords']:
            filtered = [
                job for job in filtered
                if not any(keyword.lower() in job.title.lower() or 
                          keyword.lower() in job.description.lower()
                          for keyword in self.search_filters['exclude_keywords'])
            ]
        
        return filtered

    async def _ai_rank_jobs(self, jobs: List[JobListing]) -> List[JobListing]:
        """Use AI to rank jobs based on user profile and preferences"""
        # This would implement AI-powered job ranking
        # For now, return jobs sorted by budget (highest first)
        return sorted(jobs, key=lambda x: x.budget, reverse=True)

    async def _update_market_data(self, jobs: List[JobListing]):
        """Update market data for competitive analysis"""
        if not jobs:
            return
        
        # Calculate average rates by skill
        skill_rates = {}
        for job in jobs:
            for skill in job.skills_required:
                if skill not in skill_rates:
                    skill_rates[skill] = []
                skill_rates[skill].append(job.budget)
        
        for skill, rates in skill_rates.items():
            self.market_data['average_rates'][skill] = sum(rates) / len(rates)
        
        self.market_data['last_updated'] = datetime.now()

    def _check_rate_limit(self, platform: str) -> bool:
        """Check if we're within rate limits for a platform"""
        config = self.supported_platforms[platform]
        if config['last_request'] is None:
            return True
        
        time_since_last = datetime.now() - config['last_request']
        return time_since_last.total_seconds() >= (3600 / config['rate_limit'])

    async def start_real_time_alerts(self):
        """Start real-time job alert monitoring"""
        if not self.alert_settings['enabled']:
            return
        
        self.logger.info("Starting real-time job alerts...")
        
        while True:
            try:
                new_jobs = await self.find_jobs()
                
                # Filter for truly new jobs since last check
                if self.alert_settings['last_check']:
                    new_jobs = [
                        job for job in new_jobs
                        if job.posted_date > self.alert_settings['last_check']
                    ]
                
                if new_jobs:
                    await self._send_alerts(new_jobs)
                
                self.alert_settings['last_check'] = datetime.now()
                
                # Wait for next check
                await asyncio.sleep(self.alert_settings['check_interval'])
                
            except Exception as e:
                self.logger.error(f"Error in real-time alerts: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _send_alerts(self, jobs: List[JobListing]):
        """Send alerts for new job opportunities"""
        for channel in self.alert_settings['notification_channels']:
            try:
                if channel == 'email':
                    await self._send_email_alert(jobs)
                elif channel == 'push':
                    await self._send_push_alert(jobs)
                elif channel == 'webhook':
                    await self._send_webhook_alert(jobs)
            except Exception as e:
                self.logger.error(f"Error sending {channel} alert: {e}")

    async def _send_email_alert(self, jobs: List[JobListing]):
        """Send email alert for new jobs"""
        # Implementation for email notifications
        pass

    async def _send_push_alert(self, jobs: List[JobListing]):
        """Send push notification for new jobs"""
        # Implementation for push notifications
        pass

    async def _send_webhook_alert(self, jobs: List[JobListing]):
        """Send webhook alert for new jobs"""
        # Implementation for webhook notifications
        pass

    def get_competitive_analysis(self) -> Dict[str, Any]:
        """Get competitive analysis and market insights"""
        return {
            'average_rates': self.market_data['average_rates'],
            'demand_trends': self.market_data['demand_trends'],
            'competition_levels': self.market_data['competition_levels'],
            'last_updated': self.market_data['last_updated'],
            'recommendations': self._generate_market_recommendations()
        }

    def _generate_market_recommendations(self) -> List[str]:
        """Generate market recommendations based on current data"""
        recommendations = []
        
        if self.market_data['average_rates']:
            highest_rate_skill = max(self.market_data['average_rates'].items(), key=lambda x: x[1])
            recommendations.append(f"Highest paying skill: {highest_rate_skill[0]} (${highest_rate_skill[1]:.2f}/project)")
        
        return recommendations

    def learn_from_user_behavior(self, job_id: str, action: str, success: bool = None):
        """Learn from user behavior to improve future recommendations"""
        if action == 'apply':
            self.user_behavior_memory['applied_jobs'].append(job_id)
        elif action == 'ignore':
            self.user_behavior_memory['ignored_jobs'].append(job_id)
        elif action == 'success' and success:
            self.user_behavior_memory['successful_applications'].append(job_id)
        
        # Update learned preferences
        self._update_learned_preferences(job_id, action, success)

    def _update_learned_preferences(self, job_id: str, action: str, success: bool = None):
        """Update learned preferences based on user behavior"""
        # This would implement preference learning logic
        pass

    def get_personalized_recommendations(self) -> List[JobListing]:
        """Get personalized job recommendations based on learned preferences"""
        # This would implement personalized recommendation logic
        return []

    def export_jobs_to_csv(self, jobs: List[JobListing], filename: str = None) -> str:
        """Export job listings to CSV format"""
        import csv
        from io import StringIO
        
        if not filename:
            filename = f"job_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Company', 'Platform', 'Budget', 'Skills Required',
            'Posted Date', 'URL', 'Location', 'Job Type', 'Experience Level',
            'Client Rating', 'Proposal Count'
        ])
        
        # Write data
        for job in jobs:
            writer.writerow([
                job.id, job.title, job.company, job.platform, job.budget,
                ', '.join(job.skills_required), job.posted_date.strftime('%Y-%m-%d %H:%M:%S'),
                job.url, job.location, job.job_type, job.experience_level,
                job.client_rating or 'N/A', job.proposal_count or 'N/A'
            ])
        
        # Save to file
        with open(filename, 'w', newline='') as f:
            f.write(output.getvalue())
        
        return filename