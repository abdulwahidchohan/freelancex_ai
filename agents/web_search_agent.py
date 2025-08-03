import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import aiohttp
import json
from dataclasses import dataclass
from enum import Enum
import re
from urllib.parse import urlparse, urljoin
import hashlib
import os

class SearchType(Enum):
    BUSINESS_STRATEGY = "business_strategy"
    AI_TOOLS = "ai_tools"
    INDUSTRY_TRENDS = "industry_trends"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    TECHNOLOGY_RESEARCH = "technology_research"
    MARKET_ANALYSIS = "market_analysis"
    SKILL_DEVELOPMENT = "skill_development"
    FREELANCE_TIPS = "freelance_tips"

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    relevance_score: float
    content_type: str
    published_date: Optional[datetime]
    author: Optional[str]
    tags: List[str]
    summary: str

@dataclass
class ResearchReport:
    topic: str
    search_type: SearchType
    created_at: datetime
    summary: str
    key_findings: List[str]
    recommendations: List[str]
    sources: List[SearchResult]
    market_insights: Dict[str, Any]
    trend_analysis: Dict[str, Any]

class WebSearchAgent:
    """
    Enhanced WebSearchAgent that conducts in-depth research for business strategies,
    AI tools, industry trends, and competitive analysis with semantic understanding.
    """
    
    def __init__(self, user_profile: Dict[str, Any]):
        self.user_profile = user_profile
        self.logger = logging.getLogger(__name__)
        self.search_cache = {}
        self.research_history = []
        self.trend_data = {}
        self.api_keys = self._load_api_keys()
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys for various search services"""
        return {
            'google_search': os.getenv('GOOGLE_SEARCH_API_KEY', ''),
            'serpapi': os.getenv('SERPAPI_KEY', ''),
            'newsapi': os.getenv('NEWS_API_KEY', ''),
            'openai': os.getenv('OPENAI_API_KEY', '')
        }
    
    async def conduct_research(self, topic: str, search_type: SearchType, 
                             depth: str = "comprehensive") -> ResearchReport:
        """
        Conduct comprehensive research on a specific topic
        
        Args:
            topic: Research topic
            search_type: Type of research to conduct
            depth: Research depth (basic, comprehensive, expert)
            
        Returns:
            ResearchReport with findings and recommendations
        """
        self.logger.info(f"Starting research on '{topic}' with type '{search_type.value}'")
        
        # Check cache first
        cache_key = self._generate_cache_key(topic, search_type, depth)
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            if self._is_cache_valid(cached_result['timestamp']):
                self.logger.info("Returning cached research result")
                return cached_result['report']
        
        # Generate search queries based on topic and type
        search_queries = self._generate_search_queries(topic, search_type)
        
        # Conduct searches across multiple sources
        all_results = []
        for query in search_queries:
            results = await self._search_multiple_sources(query, search_type)
            all_results.extend(results)
        
        # Remove duplicates and rank by relevance
        unique_results = self._deduplicate_results(all_results)
        ranked_results = self._rank_results_by_relevance(unique_results, topic, search_type)
        
        # Analyze trends and generate insights
        trend_analysis = await self._analyze_trends(topic, search_type)
        market_insights = await self._extract_market_insights(ranked_results, search_type)
        
        # Generate comprehensive report
        report = ResearchReport(
            topic=topic,
            search_type=search_type,
            created_at=datetime.now(),
            summary=self._generate_summary(ranked_results, topic),
            key_findings=self._extract_key_findings(ranked_results),
            recommendations=self._generate_recommendations(ranked_results, search_type),
            sources=ranked_results[:10],  # Top 10 sources
            market_insights=market_insights,
            trend_analysis=trend_analysis
        )
        
        # Cache the result
        self.search_cache[cache_key] = {
            'report': report,
            'timestamp': datetime.now()
        }
        
        # Add to research history
        self.research_history.append({
            'topic': topic,
            'type': search_type.value,
            'timestamp': datetime.now(),
            'sources_count': len(ranked_results)
        })
        
        self.logger.info(f"Research completed. Found {len(ranked_results)} relevant sources")
        return report
    
    def _generate_search_queries(self, topic: str, search_type: SearchType) -> List[str]:
        """Generate optimized search queries based on topic and search type"""
        base_queries = [topic]
        
        if search_type == SearchType.BUSINESS_STRATEGY:
            base_queries.extend([
                f"{topic} business strategy 2024",
                f"{topic} freelance business model",
                f"{topic} market opportunities",
                f"{topic} competitive advantage"
            ])
        elif search_type == SearchType.AI_TOOLS:
            base_queries.extend([
                f"{topic} AI tools 2024",
                f"{topic} automation tools",
                f"{topic} productivity AI",
                f"{topic} best AI software"
            ])
        elif search_type == SearchType.INDUSTRY_TRENDS:
            base_queries.extend([
                f"{topic} industry trends 2024",
                f"{topic} market forecast",
                f"{topic} emerging technologies",
                f"{topic} future outlook"
            ])
        elif search_type == SearchType.COMPETITIVE_ANALYSIS:
            base_queries.extend([
                f"{topic} competitors analysis",
                f"{topic} market leaders",
                f"{topic} competitive landscape",
                f"{topic} industry players"
            ])
        elif search_type == SearchType.TECHNOLOGY_RESEARCH:
            base_queries.extend([
                f"{topic} technology stack",
                f"{topic} latest developments",
                f"{topic} technical requirements",
                f"{topic} implementation guide"
            ])
        elif search_type == SearchType.MARKET_ANALYSIS:
            base_queries.extend([
                f"{topic} market size",
                f"{topic} growth rate",
                f"{topic} market segmentation",
                f"{topic} customer demand"
            ])
        elif search_type == SearchType.SKILL_DEVELOPMENT:
            base_queries.extend([
                f"{topic} learning resources",
                f"{topic} online courses",
                f"{topic} skill development",
                f"{topic} certification programs"
            ])
        elif search_type == SearchType.FREELANCE_TIPS:
            base_queries.extend([
                f"{topic} freelance tips",
                f"{topic} freelancer success",
                f"{topic} client management",
                f"{topic} freelance business"
            ])
        
        # Add user-specific context
        user_skills = self.user_profile.get('skills', [])
        if user_skills:
            for skill in user_skills[:3]:  # Top 3 skills
                base_queries.append(f"{topic} {skill}")
        
        return base_queries
    
    async def _search_multiple_sources(self, query: str, search_type: SearchType) -> List[SearchResult]:
        """Search across multiple sources for comprehensive results"""
        all_results = []
        
        # Search tasks for different sources
        search_tasks = [
            self._search_google(query),
            self._search_news(query),
            self._search_blog_posts(query),
            self._search_academic_sources(query),
            self._search_social_media(query)
        ]
        
        # Execute searches concurrently
        results = await asyncio.gather(*search_tasks, return_exceptions=True)
        
        # Combine results
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            else:
                self.logger.error(f"Search failed: {result}")
        
        return all_results
    
    async def _search_google(self, query: str) -> List[SearchResult]:
        """Search Google for web results"""
        try:
            # Simulate Google search API call
            await asyncio.sleep(0.2)
            
            # Mock results for demonstration
            mock_results = [
                SearchResult(
                    title=f"Top Result for: {query}",
                    url=f"https://example.com/{query.replace(' ', '-')}",
                    snippet=f"This is a comprehensive article about {query} with detailed insights...",
                    source="example.com",
                    relevance_score=0.95,
                    content_type="article",
                    published_date=datetime.now() - timedelta(days=2),
                    author="Expert Author",
                    tags=[query, "research", "analysis"],
                    summary=f"Comprehensive analysis of {query} with practical insights and recommendations."
                ),
                SearchResult(
                    title=f"Latest News: {query}",
                    url=f"https://news.example.com/{query.replace(' ', '-')}",
                    snippet=f"Breaking news and latest developments in {query}...",
                    source="news.example.com",
                    relevance_score=0.88,
                    content_type="news",
                    published_date=datetime.now() - timedelta(hours=6),
                    author="News Reporter",
                    tags=[query, "news", "latest"],
                    summary=f"Recent developments and news about {query}."
                )
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Google search failed: {str(e)}")
            return []
    
    async def _search_news(self, query: str) -> List[SearchResult]:
        """Search news sources for current information"""
        try:
            await asyncio.sleep(0.1)
            
            mock_results = [
                SearchResult(
                    title=f"Industry News: {query}",
                    url=f"https://industry-news.com/{query.replace(' ', '-')}",
                    snippet=f"Industry experts discuss the latest trends in {query}...",
                    source="industry-news.com",
                    relevance_score=0.92,
                    content_type="news",
                    published_date=datetime.now() - timedelta(hours=12),
                    author="Industry Expert",
                    tags=[query, "industry", "trends"],
                    summary=f"Industry perspective on {query} with expert insights."
                )
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"News search failed: {str(e)}")
            return []
    
    async def _search_blog_posts(self, query: str) -> List[SearchResult]:
        """Search blog posts and articles"""
        try:
            await asyncio.sleep(0.1)
            
            mock_results = [
                SearchResult(
                    title=f"Blog Post: {query} Guide",
                    url=f"https://blog.example.com/{query.replace(' ', '-')}-guide",
                    snippet=f"A detailed guide covering everything you need to know about {query}...",
                    source="blog.example.com",
                    relevance_score=0.85,
                    content_type="blog",
                    published_date=datetime.now() - timedelta(days=5),
                    author="Blog Author",
                    tags=[query, "guide", "tutorial"],
                    summary=f"Comprehensive guide and tutorial on {query}."
                )
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Blog search failed: {str(e)}")
            return []
    
    async def _search_academic_sources(self, query: str) -> List[SearchResult]:
        """Search academic and research sources"""
        try:
            await asyncio.sleep(0.1)
            
            mock_results = [
                SearchResult(
                    title=f"Research Paper: {query} Analysis",
                    url=f"https://research.example.com/{query.replace(' ', '-')}-analysis",
                    snippet=f"Academic research and analysis of {query} with data-driven insights...",
                    source="research.example.com",
                    relevance_score=0.90,
                    content_type="academic",
                    published_date=datetime.now() - timedelta(days=30),
                    author="Research Team",
                    tags=[query, "research", "academic"],
                    summary=f"Academic research and data analysis on {query}."
                )
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Academic search failed: {str(e)}")
            return []
    
    async def _search_social_media(self, query: str) -> List[SearchResult]:
        """Search social media for trending discussions"""
        try:
            await asyncio.sleep(0.1)
            
            mock_results = [
                SearchResult(
                    title=f"Social Discussion: {query}",
                    url=f"https://social.example.com/discussion/{query.replace(' ', '-')}",
                    snippet=f"Community discussion and insights about {query}...",
                    source="social.example.com",
                    relevance_score=0.75,
                    content_type="social",
                    published_date=datetime.now() - timedelta(hours=3),
                    author="Community Member",
                    tags=[query, "community", "discussion"],
                    summary=f"Community insights and discussions about {query}."
                )
            ]
            
            return mock_results
            
        except Exception as e:
            self.logger.error(f"Social media search failed: {str(e)}")
            return []
    
    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate results based on URL and content similarity"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            # Normalize URL
            normalized_url = self._normalize_url(result.url)
            
            if normalized_url not in seen_urls:
                seen_urls.add(normalized_url)
                unique_results.append(result)
        
        return unique_results
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for deduplication"""
        parsed = urlparse(url)
        return f"{parsed.netloc}{parsed.path}".lower()
    
    def _rank_results_by_relevance(self, results: List[SearchResult], topic: str, 
                                  search_type: SearchType) -> List[SearchResult]:
        """Rank search results by relevance to topic and search type"""
        def calculate_relevance_score(result: SearchResult) -> float:
            score = result.relevance_score
            
            # Boost score based on content type match
            if search_type == SearchType.NEWS and result.content_type == "news":
                score *= 1.2
            elif search_type == SearchType.ACADEMIC and result.content_type == "academic":
                score *= 1.3
            elif search_type == SearchType.BUSINESS_STRATEGY and "business" in result.tags:
                score *= 1.1
            
            # Boost recent content
            if result.published_date:
                days_old = (datetime.now() - result.published_date).days
                if days_old < 7:
                    score *= 1.1
                elif days_old < 30:
                    score *= 1.05
            
            # Boost authoritative sources
            authoritative_domains = ['github.com', 'stackoverflow.com', 'medium.com', 'dev.to']
            if any(domain in result.url for domain in authoritative_domains):
                score *= 1.15
            
            return score
        
        # Sort by relevance score
        ranked_results = sorted(results, key=calculate_relevance_score, reverse=True)
        return ranked_results
    
    async def _analyze_trends(self, topic: str, search_type: SearchType) -> Dict[str, Any]:
        """Analyze trends related to the research topic"""
        try:
            # Simulate trend analysis
            await asyncio.sleep(0.1)
            
            trends = {
                'topic': topic,
                'trend_direction': 'increasing',
                'growth_rate': '15%',
                'peak_season': 'Q4 2024',
                'related_topics': [f"{topic} tools", f"{topic} best practices", f"{topic} tutorial"],
                'market_sentiment': 'positive',
                'forecast': f"Expected growth in {topic} market by 25% in 2024"
            }
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return {}
    
    async def _extract_market_insights(self, results: List[SearchResult], 
                                     search_type: SearchType) -> Dict[str, Any]:
        """Extract market insights from search results"""
        insights = {
            'market_size': 'Est. $50B globally',
            'key_players': ['Company A', 'Company B', 'Company C'],
            'growth_drivers': ['AI adoption', 'Remote work', 'Digital transformation'],
            'challenges': ['Skill shortage', 'Market saturation', 'Regulatory changes'],
            'opportunities': ['Emerging markets', 'New technologies', 'Partnerships']
        }
        
        return insights
    
    def _generate_summary(self, results: List[SearchResult], topic: str) -> str:
        """Generate a comprehensive summary of research findings"""
        if not results:
            return f"No relevant information found for {topic}."
        
        top_results = results[:5]
        summary_parts = [
            f"Research on '{topic}' revealed {len(results)} relevant sources.",
            f"Key findings include:",
        ]
        
        for i, result in enumerate(top_results, 1):
            summary_parts.append(f"{i}. {result.title} - {result.summary}")
        
        summary_parts.append(f"Overall, the research indicates strong market interest and growth potential in {topic}.")
        
        return " ".join(summary_parts)
    
    def _extract_key_findings(self, results: List[SearchResult]) -> List[str]:
        """Extract key findings from search results"""
        findings = []
        
        for result in results[:5]:
            findings.append(f"{result.title}: {result.summary}")
        
        return findings
    
    def _generate_recommendations(self, results: List[SearchResult], 
                                search_type: SearchType) -> List[str]:
        """Generate actionable recommendations based on research"""
        recommendations = []
        
        if search_type == SearchType.BUSINESS_STRATEGY:
            recommendations.extend([
                "Focus on niche markets with high demand",
                "Develop unique value propositions",
                "Build strong client relationships",
                "Invest in continuous skill development"
            ])
        elif search_type == SearchType.AI_TOOLS:
            recommendations.extend([
                "Evaluate AI tools for workflow automation",
                "Stay updated with latest AI developments",
                "Consider AI certification programs",
                "Experiment with AI-powered productivity tools"
            ])
        elif search_type == SearchType.INDUSTRY_TRENDS:
            recommendations.extend([
                "Monitor emerging trends regularly",
                "Adapt services to market demands",
                "Network with industry professionals",
                "Attend relevant conferences and events"
            ])
        
        return recommendations
    
    def _generate_cache_key(self, topic: str, search_type: SearchType, depth: str) -> str:
        """Generate cache key for research results"""
        key_string = f"{topic}_{search_type.value}_{depth}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached result is still valid (24 hours)"""
        return (datetime.now() - timestamp).total_seconds() < 86400  # 24 hours
    
    async def get_trending_topics(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get trending topics in a specific category"""
        try:
            # Simulate trending topics API call
            await asyncio.sleep(0.1)
            
            trending_topics = [
                {
                    'topic': 'AI-Powered Freelancing Tools',
                    'category': 'technology',
                    'trend_score': 95,
                    'growth_rate': '+25%',
                    'description': 'AI tools that enhance freelancer productivity'
                },
                {
                    'topic': 'Remote Work Optimization',
                    'category': 'business',
                    'trend_score': 88,
                    'growth_rate': '+18%',
                    'description': 'Strategies for maximizing remote work efficiency'
                },
                {
                    'topic': 'Blockchain Freelancing Platforms',
                    'category': 'emerging',
                    'trend_score': 75,
                    'growth_rate': '+40%',
                    'description': 'Decentralized freelancing platforms'
                }
            ]
            
            if category:
                trending_topics = [t for t in trending_topics if t['category'] == category]
            
            return trending_topics
            
        except Exception as e:
            self.logger.error(f"Failed to get trending topics: {str(e)}")
            return []
    
    async def get_research_history(self) -> List[Dict[str, Any]]:
        """Get user's research history"""
        return self.research_history
    
    async def export_research_report(self, report: ResearchReport, format: str = "json") -> str:
        """Export research report in specified format"""
        if format == "json":
            return json.dumps({
                'topic': report.topic,
                'search_type': report.search_type.value,
                'created_at': report.created_at.isoformat(),
                'summary': report.summary,
                'key_findings': report.key_findings,
                'recommendations': report.recommendations,
                'sources_count': len(report.sources),
                'market_insights': report.market_insights,
                'trend_analysis': report.trend_analysis
            }, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")