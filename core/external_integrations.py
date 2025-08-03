#!/usr/bin/env python3
"""
FreelanceX.AI External Integrations
Connects to third-party services for job boards, research tools, and payment gateways
"""

import asyncio
import logging
import aiohttp
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import os
from urllib.parse import urlencode, quote

class IntegrationType(Enum):
    """Types of external integrations"""
    JOB_BOARD = "job_board"
    RESEARCH_TOOL = "research_tool"
    PAYMENT_GATEWAY = "payment_gateway"
    SOCIAL_MEDIA = "social_media"
    ANALYTICS = "analytics"

@dataclass
class JobListing:
    """Job listing data structure"""
    job_id: str
    title: str
    description: str
    platform: str
    budget: Optional[float]
    budget_type: str  # hourly, fixed, range
    skills_required: List[str]
    experience_level: str
    location: str
    posted_date: datetime
    deadline: Optional[datetime]
    client_rating: Optional[float]
    job_type: str  # full-time, part-time, contract
    url: str
    raw_data: Dict[str, Any]

@dataclass
class ResearchResult:
    """Research result data structure"""
    result_id: str
    title: str
    content: str
    source: str
    url: str
    published_date: Optional[datetime]
    relevance_score: float
    source_type: str  # article, paper, blog, news
    tags: List[str]
    raw_data: Dict[str, Any]

class ExternalIntegrations:
    """
    External integrations manager for FreelanceX.AI
    Handles connections to job boards, research tools, and other services
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.logger = logging.getLogger("FreelanceX.ExternalIntegrations")
        
        # API clients
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_keys = self._load_api_keys()
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.last_requests: Dict[str, float] = {}
        
        # Cache for API responses
        self.response_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=15)
        
        # Integration status
        self.integration_status = {
            'upwork': False,
            'fiverr': False,
            'freelancer': False,
            'google_scholar': False,
            'medium': False,
            'linkedin': False,
            'stripe': False
        }
        
        self.logger.info("External Integrations initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for external integrations"""
        return {
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1,
            'cache_enabled': True,
            'rate_limiting': {
                'upwork': {'requests_per_minute': 60, 'requests_per_hour': 1000},
                'fiverr': {'requests_per_minute': 30, 'requests_per_hour': 500},
                'freelancer': {'requests_per_minute': 45, 'requests_per_hour': 800},
                'google_scholar': {'requests_per_minute': 10, 'requests_per_hour': 100},
                'medium': {'requests_per_minute': 20, 'requests_per_hour': 300}
            }
        }
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables"""
        return {
            'upwork': os.getenv('UPWORK_API_KEY'),
            'fiverr': os.getenv('FIVERR_API_KEY'),
            'freelancer': os.getenv('FREELANCER_API_KEY'),
            'stripe': os.getenv('STRIPE_API_KEY'),
            'linkedin': os.getenv('LINKEDIN_API_KEY'),
            'google_scholar': None,  # No API key required
            'medium': None  # No API key required
        }
    
    async def initialize(self):
        """Initialize the external integrations"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config['timeout'])
        )
        
        # Test connections
        await self._test_integrations()
        
        self.logger.info("External integrations initialized successfully")
    
    async def _test_integrations(self):
        """Test all integrations to verify connectivity"""
        test_tasks = [
            self._test_upwork_connection(),
            self._test_fiverr_connection(),
            self._test_freelancer_connection(),
            self._test_google_scholar_connection(),
            self._test_medium_connection()
        ]
        
        results = await asyncio.gather(*test_tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            integration_name = list(self.integration_status.keys())[i]
            if isinstance(result, Exception):
                self.logger.warning(f"Integration {integration_name} failed: {str(result)}")
                self.integration_status[integration_name] = False
            else:
                self.integration_status[integration_name] = True
    
    async def _test_upwork_connection(self) -> bool:
        """Test Upwork API connection"""
        if not self.api_keys['upwork']:
            return False
        
        try:
            # Test API endpoint (this would be the actual Upwork API endpoint)
            headers = {'Authorization': f'Bearer {self.api_keys["upwork"]}'}
            async with self.session.get('https://api.upwork.com/api/v2/jobs', headers=headers) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Upwork connection test failed: {str(e)}")
            return False
    
    async def _test_fiverr_connection(self) -> bool:
        """Test Fiverr API connection"""
        if not self.api_keys['fiverr']:
            return False
        
        try:
            # Test API endpoint
            headers = {'Authorization': f'Bearer {self.api_keys["fiverr"]}'}
            async with self.session.get('https://api.fiverr.com/v1/jobs', headers=headers) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Fiverr connection test failed: {str(e)}")
            return False
    
    async def _test_freelancer_connection(self) -> bool:
        """Test Freelancer API connection"""
        if not self.api_keys['freelancer']:
            return False
        
        try:
            # Test API endpoint
            headers = {'Authorization': f'Bearer {self.api_keys["freelancer"]}'}
            async with self.session.get('https://api.freelancer.com/projects', headers=headers) as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Freelancer connection test failed: {str(e)}")
            return False
    
    async def _test_google_scholar_connection(self) -> bool:
        """Test Google Scholar connection"""
        try:
            # Test basic connectivity
            async with self.session.get('https://scholar.google.com') as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Google Scholar connection test failed: {str(e)}")
            return False
    
    async def _test_medium_connection(self) -> bool:
        """Test Medium API connection"""
        try:
            # Test basic connectivity
            async with self.session.get('https://medium.com') as response:
                return response.status == 200
        except Exception as e:
            self.logger.error(f"Medium connection test failed: {str(e)}")
            return False
    
    async def search_jobs(self, platform: str, query: str, filters: Dict[str, Any] = None) -> List[JobListing]:
        """Search for jobs on specified platform"""
        if not self.integration_status.get(platform, False):
            self.logger.warning(f"Platform {platform} is not available")
            return []
        
        # Check rate limits
        if not self._check_rate_limit(platform):
            self.logger.warning(f"Rate limit exceeded for {platform}")
            return []
        
        try:
            if platform == 'upwork':
                return await self._search_upwork_jobs(query, filters)
            elif platform == 'fiverr':
                return await self._search_fiverr_jobs(query, filters)
            elif platform == 'freelancer':
                return await self._search_freelancer_jobs(query, filters)
            else:
                self.logger.error(f"Unsupported platform: {platform}")
                return []
                
        except Exception as e:
            self.logger.error(f"Job search failed for {platform}: {str(e)}")
            return []
    
    async def _search_upwork_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[JobListing]:
        """Search jobs on Upwork"""
        if not self.api_keys['upwork']:
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_keys["upwork"]}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'q': query,
                'limit': filters.get('limit', 20),
                'offset': filters.get('offset', 0)
            }
            
            if filters:
                if 'budget_min' in filters:
                    params['budget_min'] = filters['budget_min']
                if 'budget_max' in filters:
                    params['budget_max'] = filters['budget_max']
                if 'skills' in filters:
                    params['skills'] = ','.join(filters['skills'])
            
            async with self.session.get(
                'https://api.upwork.com/api/v2/jobs',
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_upwork_jobs(data)
                else:
                    self.logger.error(f"Upwork API error: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Upwork job search failed: {str(e)}")
            return []
    
    async def _search_fiverr_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[JobListing]:
        """Search jobs on Fiverr"""
        if not self.api_keys['fiverr']:
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_keys["fiverr"]}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'query': query,
                'limit': filters.get('limit', 20),
                'offset': filters.get('offset', 0)
            }
            
            async with self.session.get(
                'https://api.fiverr.com/v1/jobs',
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_fiverr_jobs(data)
                else:
                    self.logger.error(f"Fiverr API error: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Fiverr job search failed: {str(e)}")
            return []
    
    async def _search_freelancer_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[JobListing]:
        """Search jobs on Freelancer"""
        if not self.api_keys['freelancer']:
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_keys["freelancer"]}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'query': query,
                'limit': filters.get('limit', 20),
                'offset': filters.get('offset', 0)
            }
            
            async with self.session.get(
                'https://api.freelancer.com/projects',
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_freelancer_jobs(data)
                else:
                    self.logger.error(f"Freelancer API error: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Freelancer job search failed: {str(e)}")
            return []
    
    def _parse_upwork_jobs(self, data: Dict[str, Any]) -> List[JobListing]:
        """Parse Upwork API response"""
        jobs = []
        try:
            for job_data in data.get('jobs', []):
                job = JobListing(
                    job_id=job_data.get('id'),
                    title=job_data.get('title'),
                    description=job_data.get('description'),
                    platform='upwork',
                    budget=job_data.get('budget'),
                    budget_type=job_data.get('budget_type', 'fixed'),
                    skills_required=job_data.get('skills', []),
                    experience_level=job_data.get('experience_level', 'intermediate'),
                    location=job_data.get('location', 'Remote'),
                    posted_date=datetime.fromisoformat(job_data.get('posted_date')),
                    deadline=datetime.fromisoformat(job_data.get('deadline')) if job_data.get('deadline') else None,
                    client_rating=job_data.get('client_rating'),
                    job_type=job_data.get('job_type', 'contract'),
                    url=job_data.get('url'),
                    raw_data=job_data
                )
                jobs.append(job)
        except Exception as e:
            self.logger.error(f"Failed to parse Upwork jobs: {str(e)}")
        
        return jobs
    
    def _parse_fiverr_jobs(self, data: Dict[str, Any]) -> List[JobListing]:
        """Parse Fiverr API response"""
        jobs = []
        try:
            for job_data in data.get('jobs', []):
                job = JobListing(
                    job_id=job_data.get('id'),
                    title=job_data.get('title'),
                    description=job_data.get('description'),
                    platform='fiverr',
                    budget=job_data.get('budget'),
                    budget_type=job_data.get('budget_type', 'fixed'),
                    skills_required=job_data.get('skills', []),
                    experience_level=job_data.get('experience_level', 'intermediate'),
                    location=job_data.get('location', 'Remote'),
                    posted_date=datetime.fromisoformat(job_data.get('posted_date')),
                    deadline=datetime.fromisoformat(job_data.get('deadline')) if job_data.get('deadline') else None,
                    client_rating=job_data.get('client_rating'),
                    job_type=job_data.get('job_type', 'contract'),
                    url=job_data.get('url'),
                    raw_data=job_data
                )
                jobs.append(job)
        except Exception as e:
            self.logger.error(f"Failed to parse Fiverr jobs: {str(e)}")
        
        return jobs
    
    def _parse_freelancer_jobs(self, data: Dict[str, Any]) -> List[JobListing]:
        """Parse Freelancer API response"""
        jobs = []
        try:
            for job_data in data.get('projects', []):
                job = JobListing(
                    job_id=job_data.get('id'),
                    title=job_data.get('title'),
                    description=job_data.get('description'),
                    platform='freelancer',
                    budget=job_data.get('budget'),
                    budget_type=job_data.get('budget_type', 'fixed'),
                    skills_required=job_data.get('skills', []),
                    experience_level=job_data.get('experience_level', 'intermediate'),
                    location=job_data.get('location', 'Remote'),
                    posted_date=datetime.fromisoformat(job_data.get('posted_date')),
                    deadline=datetime.fromisoformat(job_data.get('deadline')) if job_data.get('deadline') else None,
                    client_rating=job_data.get('client_rating'),
                    job_type=job_data.get('job_type', 'contract'),
                    url=job_data.get('url'),
                    raw_data=job_data
                )
                jobs.append(job)
        except Exception as e:
            self.logger.error(f"Failed to parse Freelancer jobs: {str(e)}")
        
        return jobs
    
    async def search_research(self, query: str, sources: List[str] = None) -> List[ResearchResult]:
        """Search for research content across multiple sources"""
        if not sources:
            sources = ['google_scholar', 'medium']
        
        results = []
        
        for source in sources:
            if not self.integration_status.get(source, False):
                continue
            
            if not self._check_rate_limit(source):
                continue
            
            try:
                if source == 'google_scholar':
                    source_results = await self._search_google_scholar(query)
                elif source == 'medium':
                    source_results = await self._search_medium(query)
                else:
                    continue
                
                results.extend(source_results)
                
            except Exception as e:
                self.logger.error(f"Research search failed for {source}: {str(e)}")
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results
    
    async def _search_google_scholar(self, query: str) -> List[ResearchResult]:
        """Search Google Scholar"""
        try:
            # Note: This is a simplified implementation
            # In production, you'd need to handle Google Scholar's anti-bot measures
            search_url = f"https://scholar.google.com/scholar?q={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    # Parse HTML response (simplified)
                    # In production, you'd use BeautifulSoup or similar
                    return self._parse_google_scholar_results(await response.text())
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Google Scholar search failed: {str(e)}")
            return []
    
    async def _search_medium(self, query: str) -> List[ResearchResult]:
        """Search Medium articles"""
        try:
            # Note: This is a simplified implementation
            # In production, you'd use Medium's API or RSS feeds
            search_url = f"https://medium.com/search?q={quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(search_url, headers=headers) as response:
                if response.status == 200:
                    # Parse HTML response (simplified)
                    return self._parse_medium_results(await response.text())
                else:
                    return []
                    
        except Exception as e:
            self.logger.error(f"Medium search failed: {str(e)}")
            return []
    
    def _parse_google_scholar_results(self, html_content: str) -> List[ResearchResult]:
        """Parse Google Scholar HTML results"""
        # This is a placeholder implementation
        # In production, you'd use BeautifulSoup to parse the HTML
        results = []
        
        # Simplified parsing (placeholder)
        # You would extract actual data from the HTML here
        
        return results
    
    def _parse_medium_results(self, html_content: str) -> List[ResearchResult]:
        """Parse Medium HTML results"""
        # This is a placeholder implementation
        # In production, you'd use BeautifulSoup to parse the HTML
        results = []
        
        # Simplified parsing (placeholder)
        # You would extract actual data from the HTML here
        
        return results
    
    def _check_rate_limit(self, platform: str) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        rate_config = self.config['rate_limiting'].get(platform, {})
        
        if platform not in self.rate_limits:
            self.rate_limits[platform] = {
                'requests': [],
                'last_reset': now
            }
        
        rate_data = self.rate_limits[platform]
        
        # Clean old requests
        rate_data['requests'] = [req_time for req_time in rate_data['requests'] 
                               if now - req_time < 60]  # 1 minute window
        
        # Check limits
        requests_per_minute = rate_config.get('requests_per_minute', 60)
        if len(rate_data['requests']) >= requests_per_minute:
            return False
        
        # Add current request
        rate_data['requests'].append(now)
        self.last_requests[platform] = now
        
        return True
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        return {
            'integrations': self.integration_status,
            'api_keys_configured': {k: bool(v) for k, v in self.api_keys.items()},
            'rate_limits': self.rate_limits,
            'last_requests': self.last_requests
        }
    
    async def shutdown(self):
        """Shutdown external integrations"""
        if self.session:
            await self.session.close()
        self.logger.info("External integrations shutdown complete")