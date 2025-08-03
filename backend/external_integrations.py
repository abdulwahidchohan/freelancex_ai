#!/usr/bin/env python3
"""
FreelanceX.AI External Integrations
Comprehensive integration layer for job boards, research tools, and third-party services
Features: Job board APIs, research platforms, social media, payment systems
"""

import asyncio
import aiohttp
import logging
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from urllib.parse import urlencode, quote
import base64
import hashlib
import hmac
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExternalJob:
    """Standardized job data structure from external sources"""
    id: str
    title: str
    description: str
    company: str
    platform: str
    url: str
    budget: Optional[float] = None
    currency: str = "USD"
    job_type: str = "contract"
    skills_required: List[str] = None
    location: str = "Remote"
    posted_date: str = None
    deadline: Optional[str] = None
    client_rating: Optional[float] = None
    proposals_count: Optional[int] = None

@dataclass
class ResearchResult:
    """Standardized research result structure"""
    title: str
    content: str
    url: str
    source: str
    published_date: str
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None

class ExternalIntegration(ABC):
    """Base class for external integrations"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.session = None
        self.rate_limits = {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
            "last_request_time": 0,
            "request_count": 0
        }
    
    async def _init_session(self):
        """Initialize HTTP session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _rate_limit_check(self):
        """Check and enforce rate limits"""
        current_time = datetime.now().timestamp()
        
        # Reset counters if needed
        if current_time - self.rate_limits["last_request_time"] > 60:
            self.rate_limits["request_count"] = 0
        
        # Check rate limits
        if self.rate_limits["request_count"] >= self.rate_limits["requests_per_minute"]:
            sleep_time = 60 - (current_time - self.rate_limits["last_request_time"])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.rate_limits["request_count"] += 1
        self.rate_limits["last_request_time"] = current_time
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to external service"""
        pass
    
    async def __aenter__(self):
        await self._init_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_session()

class UpworkIntegration(ExternalIntegration):
    """Integration with Upwork API"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        super().__init__(api_key, "https://www.upwork.com/api")
        self.api_secret = api_secret
    
    async def test_connection(self) -> bool:
        """Test Upwork API connection"""
        try:
            await self._init_session()
            # Test endpoint
            url = f"{self.base_url}/profiles/v1/metadata/categories"
            headers = await self._get_auth_headers()
            
            async with self.session.get(url, headers=headers) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Upwork connection test failed: {str(e)}")
            return False
    
    async def _get_auth_headers(self) -> Dict[str, str]:
        """Get OAuth headers for Upwork API"""
        # This would implement proper OAuth for Upwork
        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "FreelanceX.AI/1.0"
        }
    
    async def search_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[ExternalJob]:
        """Search for jobs on Upwork"""
        try:
            await self._rate_limit_check()
            await self._init_session()
            
            # Build search parameters
            params = {
                "q": query,
                "sort": "recency",
                "api_key": self.api_key
            }
            
            if filters:
                if filters.get("budget_min"):
                    params["budget"] = f"${filters['budget_min']}-"
                if filters.get("job_type"):
                    params["job_type"] = filters["job_type"]
                if filters.get("duration"):
                    params["duration"] = filters["duration"]
            
            url = f"{self.base_url}/profiles/v1/search/jobs"
            headers = await self._get_auth_headers()
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_upwork_jobs(data)
                else:
                    logger.error(f"Upwork API error: {response.status}")
                    return []
        
        except Exception as e:
            logger.error(f"Upwork job search error: {str(e)}")
            return []
    
    def _parse_upwork_jobs(self, data: Dict[str, Any]) -> List[ExternalJob]:
        """Parse Upwork API response to ExternalJob objects"""
        jobs = []
        
        for job_data in data.get("jobs", []):
            try:
                job = ExternalJob(
                    id=job_data.get("id", ""),
                    title=job_data.get("title", ""),
                    description=job_data.get("snippet", ""),
                    company=job_data.get("client", {}).get("name", ""),
                    platform="Upwork",
                    url=job_data.get("url", ""),
                    budget=self._parse_budget(job_data.get("budget")),
                    currency="USD",
                    job_type=job_data.get("job_type", "contract"),
                    skills_required=job_data.get("skills", []),
                    location=job_data.get("client", {}).get("location", {}).get("country", ""),
                    posted_date=job_data.get("date_created", ""),
                    client_rating=job_data.get("client", {}).get("feedback", 0.0),
                    proposals_count=job_data.get("proposals", 0)
                )
                jobs.append(job)
            except Exception as e:
                logger.warning(f"Error parsing Upwork job: {str(e)}")
                continue
        
        return jobs
    
    def _parse_budget(self, budget_data: Any) -> Optional[float]:
        """Parse budget information from Upwork"""
        if isinstance(budget_data, dict):
            return budget_data.get("amount", 0.0)
        elif isinstance(budget_data, str):
            # Extract number from budget string
            import re
            match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', budget_data)
            if match:
                return float(match.group(1).replace(',', ''))
        return None

class FreelancerIntegration(ExternalIntegration):
    """Integration with Freelancer.com API"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key, "https://www.freelancer.com/api")
    
    async def test_connection(self) -> bool:
        """Test Freelancer.com API connection"""
        try:
            await self._init_session()
            url = f"{self.base_url}/projects/0.1/projects"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with self.session.get(url, headers=headers) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Freelancer connection test failed: {str(e)}")
            return False
    
    async def search_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[ExternalJob]:
        """Search for projects on Freelancer.com"""
        try:
            await self._rate_limit_check()
            await self._init_session()
            
            params = {
                "query": query,
                "compact": "true"
            }
            
            if filters:
                if filters.get("min_price"):
                    params["min_price"] = filters["min_price"]
                if filters.get("max_price"):
                    params["max_price"] = filters["max_price"]
                if filters.get("project_type"):
                    params["project_type"] = filters["project_type"]
            
            url = f"{self.base_url}/projects/0.1/projects"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_freelancer_jobs(data)
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Freelancer job search error: {str(e)}")
            return []
    
    def _parse_freelancer_jobs(self, data: Dict[str, Any]) -> List[ExternalJob]:
        """Parse Freelancer.com API response"""
        jobs = []
        
        for project in data.get("result", {}).get("projects", []):
            try:
                job = ExternalJob(
                    id=str(project.get("id", "")),
                    title=project.get("title", ""),
                    description=project.get("description", ""),
                    company=project.get("owner", {}).get("display_name", ""),
                    platform="Freelancer",
                    url=f"https://www.freelancer.com/projects/{project.get('seo_url', '')}",
                    budget=project.get("budget", {}).get("maximum"),
                    currency=project.get("currency", {}).get("code", "USD"),
                    job_type="project",
                    skills_required=[skill.get("name") for skill in project.get("jobs", [])],
                    location=project.get("owner", {}).get("location", {}).get("country", {}).get("name", ""),
                    posted_date=project.get("time_submitted"),
                    proposals_count=project.get("bid_stats", {}).get("bid_count", 0)
                )
                jobs.append(job)
            except Exception as e:
                logger.warning(f"Error parsing Freelancer project: {str(e)}")
                continue
        
        return jobs

class LinkedInIntegration(ExternalIntegration):
    """Integration with LinkedIn API for job search and research"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key, "https://api.linkedin.com/v2")
    
    async def test_connection(self) -> bool:
        """Test LinkedIn API connection"""
        try:
            await self._init_session()
            url = f"{self.base_url}/me"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with self.session.get(url, headers=headers) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"LinkedIn connection test failed: {str(e)}")
            return False
    
    async def search_jobs(self, query: str, filters: Dict[str, Any] = None) -> List[ExternalJob]:
        """Search for jobs on LinkedIn"""
        try:
            await self._rate_limit_check()
            await self._init_session()
            
            # LinkedIn job search would be implemented here
            # This is a placeholder as LinkedIn API has restrictions
            return []
        
        except Exception as e:
            logger.error(f"LinkedIn job search error: {str(e)}")
            return []

class GoogleScholarIntegration(ExternalIntegration):
    """Integration with Google Scholar for research"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key, "https://serpapi.com/search")
        self.engine = "google_scholar"
    
    async def test_connection(self) -> bool:
        """Test Google Scholar API connection"""
        try:
            await self._init_session()
            params = {
                "engine": self.engine,
                "q": "test",
                "api_key": self.api_key,
                "num": 1
            }
            
            async with self.session.get(self.base_url, params=params) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Google Scholar connection test failed: {str(e)}")
            return False
    
    async def search_research(self, query: str, filters: Dict[str, Any] = None) -> List[ResearchResult]:
        """Search for research papers and articles"""
        try:
            await self._rate_limit_check()
            await self._init_session()
            
            params = {
                "engine": self.engine,
                "q": query,
                "api_key": self.api_key,
                "num": filters.get("max_results", 10) if filters else 10
            }
            
            if filters:
                if filters.get("year_from"):
                    params["as_ylo"] = filters["year_from"]
                if filters.get("year_to"):
                    params["as_yhi"] = filters["year_to"]
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_scholar_results(data)
                else:
                    return []
        
        except Exception as e:
            logger.error(f"Google Scholar search error: {str(e)}")
            return []
    
    def _parse_scholar_results(self, data: Dict[str, Any]) -> List[ResearchResult]:
        """Parse Google Scholar search results"""
        results = []
        
        for result in data.get("organic_results", []):
            try:
                research_result = ResearchResult(
                    title=result.get("title", ""),
                    content=result.get("snippet", ""),
                    url=result.get("link", ""),
                    source="Google Scholar",
                    published_date=result.get("publication_info", {}).get("summary", ""),
                    relevance_score=float(result.get("cited_by", {}).get("value", 0)) / 1000,  # Normalize citations
                    metadata={
                        "authors": result.get("publication_info", {}).get("authors", []),
                        "cited_by": result.get("cited_by", {}),
                        "versions": result.get("versions", {})
                    }
                )
                results.append(research_result)
            except Exception as e:
                logger.warning(f"Error parsing Scholar result: {str(e)}")
                continue
        
        return results

class RedditIntegration(ExternalIntegration):
    """Integration with Reddit API for market research and trends"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        super().__init__(None, "https://www.reddit.com/api/v1")
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    async def test_connection(self) -> bool:
        """Test Reddit API connection"""
        try:
            await self._get_access_token()
            return self.access_token is not None
        except Exception as e:
            logger.error(f"Reddit connection test failed: {str(e)}")
            return False
    
    async def _get_access_token(self):
        """Get Reddit API access token"""
        try:
            await self._init_session()
            
            auth_data = {
                "grant_type": "client_credentials"
            }
            
            auth_string = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers = {
                "Authorization": f"Basic {auth_string}",
                "User-Agent": "FreelanceX.AI/1.0"
            }
            
            async with self.session.post(
                f"{self.base_url}/access_token",
                data=auth_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data.get("access_token")
        
        except Exception as e:
            logger.error(f"Reddit token error: {str(e)}")
    
    async def search_discussions(self, query: str, subreddits: List[str] = None) -> List[ResearchResult]:
        """Search Reddit discussions for market insights"""
        try:
            if not self.access_token:
                await self._get_access_token()
            
            await self._rate_limit_check()
            
            subreddit_list = subreddits or ["freelance", "entrepreneur", "digitalnomad", "programming"]
            results = []
            
            for subreddit in subreddit_list:
                search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {
                    "q": query,
                    "sort": "relevance",
                    "limit": 10,
                    "restrict_sr": "true"
                }
                
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "User-Agent": "FreelanceX.AI/1.0"
                }
                
                async with self.session.get(search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.extend(self._parse_reddit_results(data, subreddit))
            
            return results
        
        except Exception as e:
            logger.error(f"Reddit search error: {str(e)}")
            return []
    
    def _parse_reddit_results(self, data: Dict[str, Any], subreddit: str) -> List[ResearchResult]:
        """Parse Reddit search results"""
        results = []
        
        for post in data.get("data", {}).get("children", []):
            post_data = post.get("data", {})
            try:
                result = ResearchResult(
                    title=post_data.get("title", ""),
                    content=post_data.get("selftext", "")[:500],  # Limit content length
                    url=f"https://www.reddit.com{post_data.get('permalink', '')}",
                    source=f"Reddit - r/{subreddit}",
                    published_date=datetime.fromtimestamp(post_data.get("created_utc", 0)).isoformat(),
                    relevance_score=post_data.get("score", 0) / 100,  # Normalize score
                    metadata={
                        "author": post_data.get("author", ""),
                        "comments": post_data.get("num_comments", 0),
                        "upvote_ratio": post_data.get("upvote_ratio", 0)
                    }
                )
                results.append(result)
            except Exception as e:
                logger.warning(f"Error parsing Reddit post: {str(e)}")
                continue
        
        return results

class ExternalIntegrationsManager:
    """Manager for all external integrations"""
    
    def __init__(self, config: Dict[str, Dict[str, str]] = None):
        self.config = config or {}
        self.integrations = {}
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize all configured integrations"""
        try:
            # Initialize job board integrations
            if "upwork" in self.config:
                self.integrations["upwork"] = UpworkIntegration(
                    api_key=self.config["upwork"].get("api_key"),
                    api_secret=self.config["upwork"].get("api_secret")
                )
            
            if "freelancer" in self.config:
                self.integrations["freelancer"] = FreelancerIntegration(
                    api_key=self.config["freelancer"].get("api_key")
                )
            
            if "linkedin" in self.config:
                self.integrations["linkedin"] = LinkedInIntegration(
                    api_key=self.config["linkedin"].get("api_key")
                )
            
            # Initialize research integrations
            if "google_scholar" in self.config:
                self.integrations["google_scholar"] = GoogleScholarIntegration(
                    api_key=self.config["google_scholar"].get("api_key")
                )
            
            if "reddit" in self.config:
                self.integrations["reddit"] = RedditIntegration(
                    client_id=self.config["reddit"].get("client_id"),
                    client_secret=self.config["reddit"].get("client_secret")
                )
            
            logger.info(f"Initialized {len(self.integrations)} external integrations")
            
        except Exception as e:
            logger.error(f"Error initializing integrations: {str(e)}")
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test connections to all configured integrations"""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                async with integration:
                    results[name] = await integration.test_connection()
            except Exception as e:
                logger.error(f"Connection test failed for {name}: {str(e)}")
                results[name] = False
        
        return results
    
    async def search_all_job_boards(self, query: str, filters: Dict[str, Any] = None) -> List[ExternalJob]:
        """Search all configured job boards"""
        all_jobs = []
        
        job_board_integrations = ["upwork", "freelancer", "linkedin"]
        
        for board_name in job_board_integrations:
            if board_name in self.integrations:
                try:
                    async with self.integrations[board_name] as integration:
                        jobs = await integration.search_jobs(query, filters)
                        all_jobs.extend(jobs)
                        logger.info(f"Found {len(jobs)} jobs from {board_name}")
                except Exception as e:
                    logger.error(f"Error searching {board_name}: {str(e)}")
        
        # Remove duplicates and sort by relevance
        unique_jobs = self._deduplicate_jobs(all_jobs)
        return sorted(unique_jobs, key=lambda x: x.posted_date or "", reverse=True)
    
    async def search_all_research_sources(self, query: str, filters: Dict[str, Any] = None) -> List[ResearchResult]:
        """Search all configured research sources"""
        all_results = []
        
        research_integrations = ["google_scholar", "reddit"]
        
        for source_name in research_integrations:
            if source_name in self.integrations:
                try:
                    async with self.integrations[source_name] as integration:
                        if source_name == "google_scholar":
                            results = await integration.search_research(query, filters)
                        elif source_name == "reddit":
                            results = await integration.search_discussions(query, filters.get("subreddits") if filters else None)
                        
                        all_results.extend(results)
                        logger.info(f"Found {len(results)} results from {source_name}")
                except Exception as e:
                    logger.error(f"Error searching {source_name}: {str(e)}")
        
        # Sort by relevance score
        return sorted(all_results, key=lambda x: x.relevance_score, reverse=True)
    
    def _deduplicate_jobs(self, jobs: List[ExternalJob]) -> List[ExternalJob]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            job_signature = f"{job.title.lower()}-{job.company.lower()}"
            if job_signature not in seen:
                seen.add(job_signature)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def get_integration_status(self) -> Dict[str, str]:
        """Get status of all integrations"""
        status = {}
        for name, integration in self.integrations.items():
            if hasattr(integration, 'api_key') and integration.api_key:
                status[name] = "configured"
            else:
                status[name] = "not_configured"
        
        return status

# Global integrations manager
integrations_manager = None

def get_integrations_manager(config: Dict[str, Dict[str, str]] = None) -> ExternalIntegrationsManager:
    """Get or create the global integrations manager"""
    global integrations_manager
    if integrations_manager is None:
        integrations_manager = ExternalIntegrationsManager(config)
    return integrations_manager