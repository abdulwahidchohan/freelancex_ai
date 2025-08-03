import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import aiohttp
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import hashlib
import time

@dataclass
class SearchResult:
    """Data class for search result information"""
    title: str
    url: str
    snippet: str
    source: str
    published_date: Optional[datetime] = None
    relevance_score: float = 0.0
    content_type: str = "webpage"  # webpage, pdf, video, etc.
    language: str = "en"
    word_count: int = 0

@dataclass
class ResearchTopic:
    """Data class for research topic information"""
    id: str
    title: str
    description: str
    keywords: List[str]
    search_engines: List[str]
    filters: Dict[str, Any]
    created_date: datetime
    last_updated: datetime
    status: str = "active"  # active, paused, completed

class WebSearchAgent:
    """
    Enhanced WebSearchAgent for FreelanceX.AI
    
    Primary Role: Conducts in-depth research for users on business strategies, AI tools, 
    industry trends, and competitive analysis.
    
    Features: Search for trending technologies, business optimization tips, and knowledge 
    on AI/ML tools for freelancers.
    Mode of Action: Uses semantic understanding to tailor research outputs to each user's needs.
    """
    
    def __init__(self, user_profile: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.user_profile = user_profile or {}
        
        # Search engine configurations
        self.search_engines = {
            'google': {
                'enabled': True,
                'api_key': None,  # Would be set from environment
                'cx': None,  # Custom search engine ID
                'rate_limit': 100,
                'last_request': None
            },
            'bing': {
                'enabled': True,
                'api_key': None,
                'rate_limit': 50,
                'last_request': None
            },
            'duckduckgo': {
                'enabled': True,
                'rate_limit': 200,
                'last_request': None
            },
            'arxiv': {
                'enabled': True,
                'rate_limit': 50,
                'last_request': None
            },
            'github': {
                'enabled': True,
                'rate_limit': 30,
                'last_request': None
            }
        }
        
        # Research categories and their associated keywords
        self.research_categories = {
            'ai_tools': {
                'keywords': ['AI tools', 'machine learning', 'automation', 'GPT', 'Claude', 'AI assistants'],
                'sources': ['techcrunch.com', 'venturebeat.com', 'arxiv.org', 'github.com'],
                'priority': 'high'
            },
            'business_strategy': {
                'keywords': ['business strategy', 'freelancing', 'entrepreneurship', 'marketing', 'growth'],
                'sources': ['forbes.com', 'entrepreneur.com', 'hbr.org', 'inc.com'],
                'priority': 'high'
            },
            'industry_trends': {
                'keywords': ['industry trends', 'market analysis', 'future of work', 'remote work'],
                'sources': ['linkedin.com', 'medium.com', 'substack.com'],
                'priority': 'medium'
            },
            'competitive_analysis': {
                'keywords': ['competitor analysis', 'market research', 'competitive intelligence'],
                'sources': ['crunchbase.com', 'linkedin.com', 'company websites'],
                'priority': 'high'
            },
            'freelance_platforms': {
                'keywords': ['Upwork', 'Fiverr', 'Freelancer', 'Toptal', 'freelance platforms'],
                'sources': ['upwork.com', 'fiverr.com', 'freelancer.com'],
                'priority': 'medium'
            }
        }
        
        # Search filters and preferences
        self.search_filters = {
            'date_range': 'any',  # any, day, week, month, year
            'language': 'en',
            'region': 'global',
            'content_type': 'all',  # all, news, academic, blogs, videos
            'exclude_domains': [],
            'include_domains': [],
            'max_results': 20,
            'min_relevance_score': 0.3
        }
        
        # Research memory and learning
        self.research_memory = {
            'searched_topics': {},
            'user_preferences': {},
            'successful_searches': [],
            'failed_searches': [],
            'content_cache': {},
            'last_cleanup': datetime.now()
        }
        
        # Content analysis settings
        self.content_analysis = {
            'extract_key_insights': True,
            'summarize_content': True,
            'identify_trends': True,
            'extract_quotes': True,
            'sentiment_analysis': True
        }

    def set_user_profile(self, profile: Dict[str, Any]):
        """Update user profile for personalized research"""
        self.user_profile = profile
        self.logger.info(f"Updated user profile for {profile.get('name', 'Unknown')}")
        
        # Update search preferences based on profile
        if 'interests' in profile:
            self._update_research_interests(profile['interests'])
        if 'industry' in profile:
            self._update_industry_focus(profile['industry'])

    def _update_research_interests(self, interests: List[str]):
        """Update research interests based on user profile"""
        for interest in interests:
            if interest.lower() in ['ai', 'artificial intelligence', 'machine learning']:
                self.research_categories['ai_tools']['priority'] = 'high'
            elif interest.lower() in ['business', 'entrepreneurship', 'marketing']:
                self.research_categories['business_strategy']['priority'] = 'high'

    def _update_industry_focus(self, industry: str):
        """Update industry focus for research"""
        self.search_filters['include_domains'].extend([
            f"{industry.lower()}.com",
            f"{industry.lower()}news.com"
        ])

    async def research_topic(self, topic: str, category: str = None, 
                           depth: str = 'comprehensive') -> Dict[str, Any]:
        """
        Conduct comprehensive research on a specific topic
        
        Args:
            topic: The research topic
            category: Research category (optional)
            depth: Research depth ('quick', 'standard', 'comprehensive')
            
        Returns:
            Dictionary containing research results and insights
        """
        self.logger.info(f"Starting research on topic: {topic}")
        
        # Create research topic object
        research_topic = ResearchTopic(
            id=self._generate_topic_id(topic),
            title=topic,
            description=f"Research on {topic}",
            keywords=self._extract_keywords(topic),
            search_engines=list(self.search_engines.keys()),
            filters=self.search_filters.copy(),
            created_date=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Determine search strategy based on depth
        search_strategy = self._get_search_strategy(depth, category)
        
        # Execute searches across multiple engines
        all_results = []
        for engine, queries in search_strategy.items():
            if not self.search_engines[engine]['enabled']:
                continue
                
            for query in queries:
                try:
                    results = await self._search_engine(engine, query, research_topic)
                    all_results.extend(results)
                except Exception as e:
                    self.logger.error(f"Error searching {engine} with query '{query}': {e}")
        
        # Remove duplicates and rank results
        unique_results = self._deduplicate_results(all_results)
        ranked_results = await self._rank_results(unique_results, research_topic)
        
        # Analyze content and extract insights
        insights = await self._analyze_content(ranked_results, research_topic)
        
        # Update research memory
        self._update_research_memory(research_topic, ranked_results, insights)
        
        return {
            'topic': research_topic,
            'results': ranked_results,
            'insights': insights,
            'summary': self._generate_research_summary(ranked_results, insights),
            'recommendations': self._generate_recommendations(insights),
            'metadata': {
                'total_results': len(ranked_results),
                'search_engines_used': list(search_strategy.keys()),
                'research_duration': None,  # Would calculate actual duration
                'timestamp': datetime.now()
            }
        }

    def _generate_topic_id(self, topic: str) -> str:
        """Generate unique ID for research topic"""
        return hashlib.md5(topic.encode()).hexdigest()[:8]

    def _extract_keywords(self, topic: str) -> List[str]:
        """Extract keywords from research topic"""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r'\b\w+\b', topic.lower())
        return [word for word in words if len(word) > 3]

    def _get_search_strategy(self, depth: str, category: str = None) -> Dict[str, List[str]]:
        """Get search strategy based on depth and category"""
        strategy = {}
        
        if depth == 'quick':
            # Use only primary search engines with basic queries
            strategy = {
                'google': [f'"{category}" {topic}' if category else topic],
                'bing': [f'"{category}" {topic}' if category else topic]
            }
        elif depth == 'standard':
            # Use multiple engines with varied queries
            strategy = {
                'google': [topic, f'"{topic}" latest', f'"{topic}" 2024'],
                'bing': [topic, f'"{topic}" news'],
                'duckduckgo': [topic]
            }
        else:  # comprehensive
            # Use all engines with extensive query variations
            strategy = {
                'google': [
                    topic, f'"{topic}" latest', f'"{topic}" 2024', 
                    f'"{topic}" trends', f'"{topic}" analysis'
                ],
                'bing': [topic, f'"{topic}" news', f'"{topic}" research'],
                'duckduckgo': [topic, f'"{topic}" recent'],
                'arxiv': [topic] if self._is_academic_topic(topic) else [],
                'github': [topic] if self._is_technical_topic(topic) else []
            }
        
        return strategy

    def _is_academic_topic(self, topic: str) -> bool:
        """Check if topic is academic/research-oriented"""
        academic_keywords = ['research', 'study', 'analysis', 'methodology', 'framework']
        return any(keyword in topic.lower() for keyword in academic_keywords)

    def _is_technical_topic(self, topic: str) -> bool:
        """Check if topic is technical/development-oriented"""
        technical_keywords = ['code', 'api', 'framework', 'library', 'tool', 'software']
        return any(keyword in topic.lower() for keyword in technical_keywords)

    async def _search_engine(self, engine: str, query: str, 
                           research_topic: ResearchTopic) -> List[SearchResult]:
        """Search a specific engine with rate limiting"""
        # Check rate limiting
        if not self._check_rate_limit(engine):
            self.logger.warning(f"Rate limit reached for {engine}")
            return []
        
        try:
            if engine == 'google':
                return await self._search_google(query, research_topic)
            elif engine == 'bing':
                return await self._search_bing(query, research_topic)
            elif engine == 'duckduckgo':
                return await self._search_duckduckgo(query, research_topic)
            elif engine == 'arxiv':
                return await self._search_arxiv(query, research_topic)
            elif engine == 'github':
                return await self._search_github(query, research_topic)
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Error searching {engine}: {e}")
            return []

    async def _search_google(self, query: str, research_topic: ResearchTopic) -> List[SearchResult]:
        """Search Google (would implement actual API call)"""
        # This would implement actual Google Custom Search API
        # For now, return sample results
        return [
            SearchResult(
                title=f"Sample Google Result for {query}",
                url=f"https://example.com/google-result-1",
                snippet=f"This is a sample search result for the query: {query}",
                source="google",
                published_date=datetime.now() - timedelta(days=1),
                relevance_score=0.8
            )
        ]

    async def _search_bing(self, query: str, research_topic: ResearchTopic) -> List[SearchResult]:
        """Search Bing (would implement actual API call)"""
        return [
            SearchResult(
                title=f"Sample Bing Result for {query}",
                url=f"https://example.com/bing-result-1",
                snippet=f"This is a sample Bing search result for: {query}",
                source="bing",
                published_date=datetime.now() - timedelta(days=2),
                relevance_score=0.7
            )
        ]

    async def _search_duckduckgo(self, query: str, research_topic: ResearchTopic) -> List[SearchResult]:
        """Search DuckDuckGo (would implement actual API call)"""
        return [
            SearchResult(
                title=f"Sample DuckDuckGo Result for {query}",
                url=f"https://example.com/ddg-result-1",
                snippet=f"This is a sample DuckDuckGo search result for: {query}",
                source="duckduckgo",
                published_date=datetime.now() - timedelta(days=3),
                relevance_score=0.6
            )
        ]

    async def _search_arxiv(self, query: str, research_topic: ResearchTopic) -> List[SearchResult]:
        """Search arXiv for academic papers"""
        return [
            SearchResult(
                title=f"Sample ArXiv Paper: {query}",
                url=f"https://arxiv.org/abs/sample-paper",
                snippet=f"Academic paper related to: {query}",
                source="arxiv",
                published_date=datetime.now() - timedelta(days=30),
                relevance_score=0.9,
                content_type="academic"
            )
        ]

    async def _search_github(self, query: str, research_topic: ResearchTopic) -> List[SearchResult]:
        """Search GitHub for repositories and code"""
        return [
            SearchResult(
                title=f"Sample GitHub Repository: {query}",
                url=f"https://github.com/sample/repo",
                snippet=f"GitHub repository related to: {query}",
                source="github",
                published_date=datetime.now() - timedelta(days=10),
                relevance_score=0.8,
                content_type="code"
            )
        ]

    def _deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Remove duplicate search results"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            if result.url not in seen_urls:
                seen_urls.add(result.url)
                unique_results.append(result)
        
        return unique_results

    async def _rank_results(self, results: List[SearchResult], 
                          research_topic: ResearchTopic) -> List[SearchResult]:
        """Rank search results by relevance"""
        for result in results:
            # Calculate relevance score based on multiple factors
            score = 0.0
            
            # Keyword matching
            for keyword in research_topic.keywords:
                if keyword.lower() in result.title.lower():
                    score += 0.3
                if keyword.lower() in result.snippet.lower():
                    score += 0.2
            
            # Recency bonus
            if result.published_date:
                days_old = (datetime.now() - result.published_date).days
                if days_old <= 7:
                    score += 0.2
                elif days_old <= 30:
                    score += 0.1
            
            # Source credibility
            credible_sources = ['arxiv.org', 'github.com', 'stackoverflow.com', 'medium.com']
            if any(source in result.url for source in credible_sources):
                score += 0.1
            
            # Content type bonus
            if result.content_type in ['academic', 'code']:
                score += 0.1
            
            result.relevance_score = min(score, 1.0)
        
        # Sort by relevance score
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)

    async def _analyze_content(self, results: List[SearchResult], 
                             research_topic: ResearchTopic) -> Dict[str, Any]:
        """Analyze content and extract insights"""
        insights = {
            'key_themes': [],
            'trends': [],
            'quotes': [],
            'sentiment': 'neutral',
            'recommendations': [],
            'gaps': []
        }
        
        # Extract key themes
        all_text = ' '.join([result.title + ' ' + result.snippet for result in results])
        insights['key_themes'] = self._extract_key_themes(all_text)
        
        # Identify trends
        insights['trends'] = self._identify_trends(results)
        
        # Extract notable quotes
        insights['quotes'] = self._extract_quotes(results)
        
        # Analyze sentiment
        insights['sentiment'] = self._analyze_sentiment(all_text)
        
        # Identify research gaps
        insights['gaps'] = self._identify_research_gaps(results, research_topic)
        
        return insights

    def _extract_key_themes(self, text: str) -> List[str]:
        """Extract key themes from text"""
        # Simple theme extraction - could be enhanced with NLP
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Filter out short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top themes
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]

    def _identify_trends(self, results: List[SearchResult]) -> List[str]:
        """Identify trends from search results"""
        trends = []
        
        # Analyze publication dates for trends
        recent_results = [r for r in results if r.published_date and 
                         (datetime.now() - r.published_date).days <= 30]
        
        if len(recent_results) > len(results) * 0.5:
            trends.append("Growing interest in this topic")
        
        # Analyze sources for trends
        sources = [r.source for r in results]
        if 'arxiv' in sources:
            trends.append("Active academic research in this area")
        if 'github' in sources:
            trends.append("Active development and open-source projects")
        
        return trends

    def _extract_quotes(self, results: List[SearchResult]) -> List[str]:
        """Extract notable quotes from search results"""
        quotes = []
        
        for result in results:
            # Look for quoted text in snippets
            quoted_text = re.findall(r'"([^"]*)"', result.snippet)
            quotes.extend(quoted_text)
        
        return quotes[:5]  # Return top 5 quotes

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text"""
        # Simple sentiment analysis - could be enhanced with NLP
        positive_words = ['good', 'great', 'excellent', 'amazing', 'innovative', 'successful']
        negative_words = ['bad', 'poor', 'terrible', 'failed', 'problem', 'issue']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _identify_research_gaps(self, results: List[SearchResult], 
                               research_topic: ResearchTopic) -> List[str]:
        """Identify gaps in current research"""
        gaps = []
        
        # Check for recent publications
        recent_results = [r for r in results if r.published_date and 
                         (datetime.now() - r.published_date).days <= 90]
        
        if len(recent_results) < 5:
            gaps.append("Limited recent research on this topic")
        
        # Check for diverse sources
        sources = set(r.source for r in results)
        if len(sources) < 3:
            gaps.append("Limited diversity in information sources")
        
        return gaps

    def _generate_research_summary(self, results: List[SearchResult], 
                                 insights: Dict[str, Any]) -> str:
        """Generate a summary of research findings"""
        summary = f"Research Summary:\n\n"
        summary += f"Found {len(results)} relevant sources across multiple search engines.\n"
        
        if insights['key_themes']:
            summary += f"Key themes identified: {', '.join(insights['key_themes'][:5])}\n"
        
        if insights['trends']:
            summary += f"Trends observed: {', '.join(insights['trends'])}\n"
        
        if insights['sentiment'] != 'neutral':
            summary += f"Overall sentiment: {insights['sentiment']}\n"
        
        return summary

    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on research insights"""
        recommendations = []
        
        if insights['gaps']:
            recommendations.append("Consider exploring the identified research gaps")
        
        if insights['trends']:
            recommendations.append("Stay updated on the identified trends")
        
        if insights['sentiment'] == 'positive':
            recommendations.append("The positive sentiment suggests good opportunities in this area")
        
        return recommendations

    def _update_research_memory(self, research_topic: ResearchTopic, 
                              results: List[SearchResult], insights: Dict[str, Any]):
        """Update research memory with new findings"""
        self.research_memory['searched_topics'][research_topic.id] = {
            'topic': research_topic,
            'results_count': len(results),
            'insights': insights,
            'timestamp': datetime.now()
        }
        
        # Clean up old entries periodically
        if (datetime.now() - self.research_memory['last_cleanup']).days >= 7:
            self._cleanup_research_memory()

    def _cleanup_research_memory(self):
        """Clean up old research memory entries"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        # Remove old topic entries
        old_topics = [
            topic_id for topic_id, data in self.research_memory['searched_topics'].items()
            if data['timestamp'] < cutoff_date
        ]
        
        for topic_id in old_topics:
            del self.research_memory['searched_topics'][topic_id]
        
        self.research_memory['last_cleanup'] = datetime.now()

    def _check_rate_limit(self, engine: str) -> bool:
        """Check if we're within rate limits for a search engine"""
        config = self.search_engines[engine]
        if config['last_request'] is None:
            return True
        
        time_since_last = datetime.now() - config['last_request']
        return time_since_last.total_seconds() >= (3600 / config['rate_limit'])

    async def get_trending_topics(self, category: str = None) -> List[str]:
        """Get trending topics in a specific category"""
        trending_queries = [
            "AI tools 2024",
            "freelancing trends",
            "remote work opportunities",
            "passive income strategies",
            "business automation"
        ]
        
        if category:
            trending_queries = [query for query in trending_queries if category.lower() in query.lower()]
        
        return trending_queries

    def export_research_to_json(self, research_data: Dict[str, Any], filename: str = None) -> str:
        """Export research data to JSON format"""
        if not filename:
            filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(filename, 'w') as f:
            json.dump(research_data, f, default=datetime_converter, indent=2)
        
        return filename

    def get_research_history(self) -> Dict[str, Any]:
        """Get research history and statistics"""
        return {
            'total_searches': len(self.research_memory['searched_topics']),
            'recent_searches': [
                {
                    'topic': data['topic'].title,
                    'results_count': data['results_count'],
                    'timestamp': data['timestamp']
                }
                for data in self.research_memory['searched_topics'].values()
            ],
            'user_preferences': self.research_memory['user_preferences'],
            'last_cleanup': self.research_memory['last_cleanup']
        }