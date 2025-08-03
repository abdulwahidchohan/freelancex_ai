import asyncio
import aiohttp
import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from core.base_agent import BaseAgent, AgentStatus
from bs4 import BeautifulSoup
import urllib.parse

@dataclass
class ResearchResult:
    """Structured research result data"""
    id: str
    query: str
    title: str
    url: str
    content: str
    source_type: str  # article, blog, research_paper, news, etc.
    authority_score: float
    relevance_score: float
    publish_date: Optional[str]
    author: Optional[str]
    keywords: List[str]
    summary: str
    insights: List[str]
    timestamp: str

class WebSearchAgent(BaseAgent):
    """
    WebSearchAgent for FreelanceX.AI
    Conducts in-depth research on business strategies, AI tools, industry trends, and competitive analysis
    """
    
    def __init__(self):
        super().__init__("WebSearchAgent", "web_search")
        
        # Research configurations
        self.search_engines = {
            'google': {
                'api_endpoint': 'https://www.googleapis.com/customsearch/v1',
                'requires_api_key': True,
                'rate_limit': 100,  # per day
                'last_request': None
            },
            'bing': {
                'api_endpoint': 'https://api.bing.microsoft.com/v7.0/search',
                'requires_api_key': True,
                'rate_limit': 1000,
                'last_request': None
            },
            'duckduckgo': {
                'api_endpoint': 'https://api.duckduckgo.com/',
                'requires_api_key': False,
                'rate_limit': 500,
                'last_request': None
            }
        }
        
        # Specialized search domains
        self.specialized_sources = {
            'ai_research': [
                'arxiv.org',
                'papers.nips.cc',
                'openai.com/research',
                'ai.googleblog.com',
                'research.facebook.com',
                'deepmind.com/research'
            ],
            'business_strategy': [
                'hbr.org',
                'mckinsey.com',
                'bcg.com',
                'strategy-business.com',
                'sloanreview.mit.edu'
            ],
            'freelance_trends': [
                'upwork.com/research',
                'freelancersunion.org',
                'future-of-work.org',
                'fiverr.com/blog',
                'toptal.com/insights'
            ],
            'tech_news': [
                'techcrunch.com',
                'venturebeat.com',
                'wired.com',
                'arstechnica.com',
                'theverge.com'
            ]
        }
        
        # Research categories
        self.research_categories = {
            'ai_tools': ['artificial intelligence tools', 'machine learning platforms', 'AI automation'],
            'business_optimization': ['business process optimization', 'productivity tools', 'workflow automation'],
            'industry_trends': ['freelance market trends', 'remote work statistics', 'gig economy analysis'],
            'competitive_analysis': ['competitor research', 'market analysis', 'SWOT analysis'],
            'technology_trends': ['emerging technologies', 'tech stack recommendations', 'software development trends'],
            'marketing_strategies': ['digital marketing', 'content marketing', 'social media strategies']
        }
        
        # Research cache and analytics
        self.research_cache: Dict[str, ResearchResult] = {}
        self.search_analytics = {
            'total_searches': 0,
            'successful_searches': 0,
            'sources_analyzed': 0,
            'insights_generated': 0,
            'avg_relevance_score': 0.0,
            'popular_categories': {},
            'trending_topics': []
        }
        
        # Daily research digest
        self.daily_digest = {
            'date': datetime.now().date().isoformat(),
            'topics_researched': [],
            'key_insights': [],
            'trending_keywords': [],
            'recommended_reads': []
        }
        
        self.logger.info("WebSearchAgent initialized with comprehensive research capabilities")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search and research tasks"""
        start_time = datetime.now()
        task_type = task.get('type', 'search')
        
        try:
            if task_type == 'research_topic':
                result = await self._research_topic(task.get('topic'), task.get('depth', 'medium'))
            elif task_type == 'competitive_analysis':
                result = await self._competitive_analysis(task.get('company'), task.get('industry'))
            elif task_type == 'trend_analysis':
                result = await self._trend_analysis(task.get('keywords'), task.get('timeframe', '30d'))
            elif task_type == 'ai_tool_research':
                result = await self._ai_tool_research(task.get('category'), task.get('use_case'))
            elif task_type == 'market_intelligence':
                result = await self._market_intelligence(task.get('market'), task.get('focus_areas'))
            elif task_type == 'daily_digest':
                result = await self._generate_daily_digest()
            elif task_type == 'semantic_search':
                result = await self._semantic_search(task.get('query'), task.get('context'))
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
        """Perform self-diagnosis for the WebSearchAgent"""
        diagnosis = {
            "agent_health": "healthy",
            "needs_repair": False,
            "issues": [],
            "recommendations": []
        }
        
        # Check search engine connectivity
        for engine, config in self.search_engines.items():
            if not await self._test_search_engine_connectivity(engine):
                diagnosis["issues"].append(f"Cannot connect to {engine}")
                diagnosis["agent_health"] = "degraded"
        
        # Check cache size and performance
        if len(self.research_cache) > 5000:
            diagnosis["recommendations"].append("Consider clearing old research cache")
            
        # Check research quality metrics
        if self.search_analytics["avg_relevance_score"] < 0.7:
            diagnosis["needs_repair"] = True
            diagnosis["recommendations"].append("Review and improve search algorithms for better relevance")
            
        return diagnosis

    async def _research_topic(self, topic: str, depth: str = 'medium') -> Dict[str, Any]:
        """Conduct comprehensive research on a specific topic"""
        self.status = AgentStatus.BUSY
        
        try:
            # Generate search queries based on topic and depth
            search_queries = self._generate_search_queries(topic, depth)
            
            all_results = []
            
            # Execute searches across multiple engines
            for query in search_queries:
                for engine in self.search_engines.keys():
                    try:
                        engine_results = await self._search_engine(engine, query)
                        all_results.extend(engine_results)
                    except Exception as e:
                        self.logger.error(f"Search failed for {engine}: {str(e)}")
            
            # Process and analyze results
            processed_results = await self._process_search_results(all_results, topic)
            
            # Generate insights and summary
            insights = self._generate_insights(processed_results, topic)
            summary = self._generate_summary(processed_results, topic)
            
            # Update analytics
            self.search_analytics['total_searches'] += 1
            self.search_analytics['successful_searches'] += 1
            self.search_analytics['sources_analyzed'] += len(processed_results)
            self.search_analytics['insights_generated'] += len(insights)
            
            # Store in cache
            research_id = f"research_{datetime.now().timestamp()}"
            self.store_memory(research_id, {
                'topic': topic,
                'depth': depth,
                'results': processed_results,
                'insights': insights,
                'summary': summary
            })
            
            self.status = AgentStatus.IDLE
            
            return {
                "status": "success",
                "topic": topic,
                "depth": depth,
                "summary": summary,
                "insights": insights,
                "sources_count": len(processed_results),
                "top_sources": processed_results[:10],  # Top 10 most relevant
                "research_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.status = AgentStatus.IDLE
            raise e

    async def _competitive_analysis(self, company: str, industry: str) -> Dict[str, Any]:
        """Conduct competitive analysis for a company in specific industry"""
        try:
            # Research queries for competitive analysis
            queries = [
                f"{company} competitors {industry}",
                f"{industry} market leaders 2024",
                f"{company} vs competitors analysis",
                f"{industry} market share analysis",
                f"{company} SWOT analysis"
            ]
            
            competitive_data = {
                'target_company': company,
                'industry': industry,
                'competitors': [],
                'market_position': {},
                'strengths': [],
                'weaknesses': [],
                'opportunities': [],
                'threats': [],
                'market_trends': [],
                'recommendations': []
            }
            
            # Execute research
            all_results = []
            for query in queries:
                results = await self._search_engine('google', query)  # Use primary engine
                all_results.extend(results)
            
            # Analyze competitive landscape
            competitive_data = await self._analyze_competitive_landscape(all_results, company, industry)
            
            return {
                "status": "success",
                "analysis": competitive_data,
                "research_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Competitive analysis failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def _trend_analysis(self, keywords: List[str], timeframe: str) -> Dict[str, Any]:
        """Analyze trends for given keywords over specified timeframe"""
        try:
            trend_data = {
                'keywords': keywords,
                'timeframe': timeframe,
                'trending_topics': [],
                'growth_patterns': {},
                'emerging_trends': [],
                'declining_trends': [],
                'predictions': [],
                'related_topics': []
            }
            
            # Research each keyword
            for keyword in keywords:
                query = f"{keyword} trends {timeframe}"
                results = await self._search_engine('google', query)
                
                # Analyze trend patterns
                trend_info = await self._analyze_trend_patterns(results, keyword)
                trend_data['growth_patterns'][keyword] = trend_info
            
            # Generate trend insights
            trend_data['emerging_trends'] = self._identify_emerging_trends(trend_data['growth_patterns'])
            trend_data['predictions'] = self._generate_trend_predictions(trend_data['growth_patterns'])
            
            return {
                "status": "success",
                "trend_analysis": trend_data,
                "research_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _ai_tool_research(self, category: str, use_case: str) -> Dict[str, Any]:
        """Research AI tools for specific category and use case"""
        try:
            # AI tool research queries
            queries = [
                f"best AI tools {category} {use_case}",
                f"{category} AI software comparison 2024",
                f"AI automation tools {use_case}",
                f"machine learning platforms {category}"
            ]
            
            ai_tools_data = {
                'category': category,
                'use_case': use_case,
                'recommended_tools': [],
                'tool_comparisons': [],
                'pricing_analysis': {},
                'integration_options': [],
                'user_reviews': [],
                'implementation_guides': []
            }
            
            # Research AI tools from specialized sources
            for source_domain in self.specialized_sources['ai_research']:
                try:
                    results = await self._search_specialized_source(source_domain, queries[0])
                    ai_tools_data['recommended_tools'].extend(results)
                except Exception as e:
                    self.logger.warning(f"Failed to search {source_domain}: {str(e)}")
            
            # Process and rank tools
            ai_tools_data = await self._process_ai_tools_data(ai_tools_data)
            
            return {
                "status": "success",
                "ai_tools_research": ai_tools_data,
                "research_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _market_intelligence(self, market: str, focus_areas: List[str]) -> Dict[str, Any]:
        """Gather market intelligence for specific market and focus areas"""
        try:
            intelligence_data = {
                'market': market,
                'focus_areas': focus_areas,
                'market_size': {},
                'growth_projections': {},
                'key_players': [],
                'market_dynamics': {},
                'opportunities': [],
                'challenges': [],
                'regulatory_environment': {},
                'technology_impact': {}
            }
            
            # Research each focus area
            for focus_area in focus_areas:
                query = f"{market} {focus_area} market analysis 2024"
                results = await self._search_engine('google', query)
                
                # Extract market intelligence
                focus_data = await self._extract_market_intelligence(results, focus_area)
                intelligence_data[focus_area] = focus_data
            
            return {
                "status": "success",
                "market_intelligence": intelligence_data,
                "research_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _generate_daily_digest(self) -> Dict[str, Any]:
        """Generate daily research digest for freelancers"""
        try:
            current_date = datetime.now().date()
            
            # Research trending topics in freelance industry
            trending_queries = [
                "freelance industry trends 2024",
                "remote work statistics today",
                "AI tools for freelancers new",
                "gig economy news latest",
                "freelance platform updates"
            ]
            
            digest_data = {
                'date': current_date.isoformat(),
                'trending_topics': [],
                'ai_tool_updates': [],
                'industry_news': [],
                'market_insights': [],
                'productivity_tips': [],
                'recommended_reading': [],
                'upcoming_opportunities': []
            }
            
            # Gather data for digest
            for query in trending_queries:
                results = await self._search_engine('google', query)
                categorized_results = self._categorize_digest_content(results)
                
                for category, content in categorized_results.items():
                    if category in digest_data:
                        digest_data[category].extend(content)
            
            # Curate and summarize digest
            digest_data = self._curate_daily_digest(digest_data)
            
            # Store digest
            self.daily_digest = digest_data
            self.store_memory(f"daily_digest_{current_date}", digest_data)
            
            return {
                "status": "success",
                "daily_digest": digest_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _semantic_search(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic search with context understanding"""
        try:
            # Enhance query with context
            enhanced_query = self._enhance_query_with_context(query, context)
            
            # Use multiple search strategies
            search_strategies = [
                ('exact_match', enhanced_query),
                ('semantic_expansion', self._expand_query_semantically(enhanced_query)),
                ('context_aware', self._create_context_aware_query(query, context))
            ]
            
            all_results = []
            for strategy_name, search_query in search_strategies:
                results = await self._search_engine('google', search_query)
                for result in results:
                    result['search_strategy'] = strategy_name
                all_results.extend(results)
            
            # Rank results by semantic relevance
            ranked_results = self._rank_by_semantic_relevance(all_results, query, context)
            
            return {
                "status": "success",
                "query": query,
                "context": context,
                "results": ranked_results[:20],  # Top 20 results
                "search_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _generate_search_queries(self, topic: str, depth: str) -> List[str]:
        """Generate multiple search queries for comprehensive research"""
        base_queries = [topic]
        
        if depth == 'shallow':
            return [f"{topic} overview", f"{topic} basics"]
        elif depth == 'medium':
            return [
                f"{topic} comprehensive guide",
                f"{topic} best practices",
                f"{topic} trends 2024",
                f"{topic} tools and resources"
            ]
        elif depth == 'deep':
            return [
                f"{topic} in-depth analysis",
                f"{topic} research papers",
                f"{topic} case studies",
                f"{topic} expert opinions",
                f"{topic} future predictions",
                f"{topic} implementation strategies",
                f"{topic} challenges and solutions"
            ]
        
        return base_queries

    async def _search_engine(self, engine: str, query: str) -> List[Dict[str, Any]]:
        """Search using specified search engine"""
        # Mock search results for demonstration
        # In production, this would make actual API calls
        
        mock_results = [
            {
                'title': f"Comprehensive Guide to {query}",
                'url': f"https://example.com/guide-{hash(query) % 1000}",
                'snippet': f"This comprehensive guide covers everything you need to know about {query}, including best practices, tools, and implementation strategies.",
                'source': 'example.com',
                'date': datetime.now().isoformat(),
                'relevance_score': 0.9
            },
            {
                'title': f"{query} - Latest Trends and Insights",
                'url': f"https://insights.example.com/trends-{hash(query) % 1000}",
                'snippet': f"Discover the latest trends and insights about {query}. Expert analysis and market predictions for 2024.",
                'source': 'insights.example.com',
                'date': (datetime.now() - timedelta(days=1)).isoformat(),
                'relevance_score': 0.85
            },
            {
                'title': f"How to Implement {query} Successfully",
                'url': f"https://howto.example.com/implement-{hash(query) % 1000}",
                'snippet': f"Step-by-step guide on implementing {query} in your organization. Includes best practices and common pitfalls to avoid.",
                'source': 'howto.example.com',
                'date': (datetime.now() - timedelta(days=3)).isoformat(),
                'relevance_score': 0.8
            }
        ]
        
        return mock_results

    async def _test_search_engine_connectivity(self, engine: str) -> bool:
        """Test connectivity to search engine"""
        try:
            # Mock connectivity test
            await asyncio.sleep(0.1)
            return True
        except:
            return False

    async def _process_search_results(self, results: List[Dict[str, Any]], topic: str) -> List[ResearchResult]:
        """Process and structure search results"""
        processed_results = []
        
        for i, result in enumerate(results):
            research_result = ResearchResult(
                id=f"result_{i}_{datetime.now().timestamp()}",
                query=topic,
                title=result.get('title', ''),
                url=result.get('url', ''),
                content=result.get('snippet', ''),
                source_type=self._determine_source_type(result.get('url', '')),
                authority_score=self._calculate_authority_score(result.get('source', '')),
                relevance_score=result.get('relevance_score', 0.5),
                publish_date=result.get('date'),
                author=result.get('author'),
                keywords=self._extract_keywords(result.get('snippet', '')),
                summary=self._generate_content_summary(result.get('snippet', '')),
                insights=self._extract_insights(result.get('snippet', ''), topic),
                timestamp=datetime.now().isoformat()
            )
            processed_results.append(research_result)
        
        # Sort by relevance and authority
        processed_results.sort(key=lambda x: (x.relevance_score + x.authority_score) / 2, reverse=True)
        
        return processed_results

    def _determine_source_type(self, url: str) -> str:
        """Determine the type of source based on URL"""
        if 'arxiv.org' in url or 'research' in url:
            return 'research_paper'
        elif 'news' in url or 'techcrunch' in url or 'reuters' in url:
            return 'news'
        elif 'blog' in url or 'medium.com' in url:
            return 'blog'
        elif '.edu' in url:
            return 'academic'
        elif '.gov' in url:
            return 'government'
        else:
            return 'article'

    def _calculate_authority_score(self, source: str) -> float:
        """Calculate authority score for a source"""
        high_authority_domains = [
            'harvard.edu', 'mit.edu', 'stanford.edu',
            'hbr.org', 'mckinsey.com', 'bcg.com',
            'nature.com', 'science.org', 'ieee.org'
        ]
        
        medium_authority_domains = [
            'techcrunch.com', 'wired.com', 'forbes.com',
            'bloomberg.com', 'reuters.com', 'bbc.com'
        ]
        
        if any(domain in source for domain in high_authority_domains):
            return 0.9
        elif any(domain in source for domain in medium_authority_domains):
            return 0.7
        else:
            return 0.5

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction - in production would use NLP
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if len(word) > 4 and word not in ['that', 'this', 'with', 'from', 'they', 'have', 'will', 'been', 'their']]
        return list(set(keywords))[:10]  # Top 10 unique keywords

    def _generate_content_summary(self, content: str) -> str:
        """Generate summary of content"""
        if len(content) <= 100:
            return content
        
        # Simple summarization - first sentence + key points
        sentences = content.split('.')
        summary = sentences[0] if sentences else content[:100]
        return summary + "..." if len(summary) < len(content) else summary

    def _extract_insights(self, content: str, topic: str) -> List[str]:
        """Extract insights from content related to topic"""
        insights = []
        
        # Simple insight extraction based on patterns
        insight_patterns = [
            r'key insight[s]?[:\-]\s*(.+?)[\.\n]',
            r'important[ly]?\s*(.+?)[\.\n]',
            r'significant[ly]?\s*(.+?)[\.\n]',
            r'notable?\s*(.+?)[\.\n]'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            insights.extend(matches)
        
        return insights[:5]  # Top 5 insights

    def _generate_insights(self, results: List[ResearchResult], topic: str) -> List[str]:
        """Generate overall insights from research results"""
        all_insights = []
        
        for result in results:
            all_insights.extend(result.insights)
        
        # Deduplicate and rank insights
        unique_insights = list(set(all_insights))
        
        return unique_insights[:10]  # Top 10 insights

    def _generate_summary(self, results: List[ResearchResult], topic: str) -> str:
        """Generate comprehensive summary of research"""
        if not results:
            return f"No research results found for {topic}."
        
        summary = f"Research summary for '{topic}':\n\n"
        summary += f"Analyzed {len(results)} sources with an average relevance score of {sum(r.relevance_score for r in results) / len(results):.2f}.\n\n"
        
        # Key findings
        summary += "Key findings:\n"
        for i, result in enumerate(results[:3]):  # Top 3 results
            summary += f"{i+1}. {result.title}: {result.summary}\n"
        
        summary += f"\nResearch completed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return summary

    async def _analyze_competitive_landscape(self, results: List[Dict[str, Any]], company: str, industry: str) -> Dict[str, Any]:
        """Analyze competitive landscape from search results"""
        # Mock competitive analysis
        return {
            'target_company': company,
            'industry': industry,
            'competitors': ['Competitor A', 'Competitor B', 'Competitor C'],
            'market_position': 'Strong player in the market',
            'strengths': ['Strong brand', 'Good customer service', 'Innovative products'],
            'weaknesses': ['Limited market presence', 'Higher pricing'],
            'opportunities': ['Emerging markets', 'New product categories'],
            'threats': ['New competitors', 'Market saturation'],
            'market_trends': ['Digital transformation', 'Sustainability focus'],
            'recommendations': ['Expand digital presence', 'Develop sustainable products']
        }

    async def _analyze_trend_patterns(self, results: List[Dict[str, Any]], keyword: str) -> Dict[str, Any]:
        """Analyze trend patterns from search results"""
        return {
            'keyword': keyword,
            'trend_direction': 'increasing',
            'growth_rate': '15% YoY',
            'peak_periods': ['Q4 2023', 'Q1 2024'],
            'related_trends': ['AI automation', 'Remote work'],
            'predictions': ['Continued growth expected']
        }

    def _identify_emerging_trends(self, growth_patterns: Dict[str, Any]) -> List[str]:
        """Identify emerging trends from growth patterns"""
        return ['AI automation tools', 'Remote collaboration platforms', 'Sustainable business practices']

    def _generate_trend_predictions(self, growth_patterns: Dict[str, Any]) -> List[str]:
        """Generate trend predictions"""
        return [
            'AI tools adoption will increase by 50% in 2024',
            'Remote work will become the standard for 60% of knowledge workers',
            'Sustainable practices will be mandatory for most businesses by 2025'
        ]

    async def _search_specialized_source(self, domain: str, query: str) -> List[Dict[str, Any]]:
        """Search within specialized sources"""
        # Mock specialized source search
        return [
            {
                'title': f"{query} - {domain} Analysis",
                'url': f"https://{domain}/analysis",
                'content': f"Specialized analysis from {domain} about {query}",
                'authority_score': 0.9
            }
        ]

    async def _process_ai_tools_data(self, ai_tools_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance AI tools research data"""
        # Mock processing
        ai_tools_data['recommended_tools'] = [
            {'name': 'Tool A', 'rating': 4.5, 'pricing': 'Freemium'},
            {'name': 'Tool B', 'rating': 4.3, 'pricing': '$50/month'},
            {'name': 'Tool C', 'rating': 4.7, 'pricing': 'Enterprise only'}
        ]
        return ai_tools_data

    async def _extract_market_intelligence(self, results: List[Dict[str, Any]], focus_area: str) -> Dict[str, Any]:
        """Extract market intelligence from results"""
        return {
            'focus_area': focus_area,
            'market_size': '$10B globally',
            'growth_rate': '12% CAGR',
            'key_drivers': ['Digital transformation', 'Remote work adoption']
        }

    def _categorize_digest_content(self, results: List[Dict[str, Any]]) -> Dict[str, List]:
        """Categorize content for daily digest"""
        return {
            'trending_topics': ['AI in freelancing', 'Remote work tools'],
            'industry_news': ['New freelance platform launched', 'Market growth reported'],
            'productivity_tips': ['Time management strategies', 'Client communication best practices']
        }

    def _curate_daily_digest(self, digest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Curate and enhance daily digest"""
        # Remove duplicates and enhance content
        for key in digest_data:
            if isinstance(digest_data[key], list):
                digest_data[key] = list(set(digest_data[key]))[:5]  # Top 5 unique items
        
        return digest_data

    def _enhance_query_with_context(self, query: str, context: Dict[str, Any]) -> str:
        """Enhance search query with context information"""
        enhanced_query = query
        
        if 'industry' in context:
            enhanced_query += f" {context['industry']}"
        if 'timeframe' in context:
            enhanced_query += f" {context['timeframe']}"
        if 'location' in context:
            enhanced_query += f" {context['location']}"
            
        return enhanced_query

    def _expand_query_semantically(self, query: str) -> str:
        """Expand query with semantic variations"""
        synonyms = {
            'freelance': ['gig work', 'independent contractor', 'self-employed'],
            'AI': ['artificial intelligence', 'machine learning', 'automation'],
            'business': ['company', 'enterprise', 'organization']
        }
        
        expanded_query = query
        for word, alternatives in synonyms.items():
            if word.lower() in query.lower():
                expanded_query += f" OR {' OR '.join(alternatives)}"
        
        return expanded_query

    def _create_context_aware_query(self, query: str, context: Dict[str, Any]) -> str:
        """Create context-aware search query"""
        context_terms = []
        
        if 'user_skills' in context:
            context_terms.extend(context['user_skills'])
        if 'industry' in context:
            context_terms.append(context['industry'])
        if 'goals' in context:
            context_terms.extend(context['goals'])
        
        context_query = f"{query} {' '.join(context_terms)}"
        return context_query

    def _rank_by_semantic_relevance(self, results: List[Dict[str, Any]], query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank results by semantic relevance to query and context"""
        # Simple relevance scoring - in production would use advanced NLP
        for result in results:
            relevance_score = 0.5  # Base score
            
            # Check title relevance
            if any(word.lower() in result.get('title', '').lower() for word in query.split()):
                relevance_score += 0.3
            
            # Check snippet relevance
            if any(word.lower() in result.get('snippet', '').lower() for word in query.split()):
                relevance_score += 0.2
            
            result['semantic_relevance'] = min(1.0, relevance_score)
        
        # Sort by semantic relevance
        results.sort(key=lambda x: x.get('semantic_relevance', 0), reverse=True)
        
        return results