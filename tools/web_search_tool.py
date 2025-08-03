"""
FreelanceX.AI Web Search Tool
Enhanced web search functionality for research and information gathering
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

class WebSearchTool:
    """
    Web Search Tool - Enhanced web search functionality
    Provides intelligent search capabilities with result filtering and analysis
    """
    
    def __init__(self):
        self.search_history = []
        self.search_cache = {}
        self.max_results = 10
        self.timeout = 30
        
    async def search(self, query: str, search_type: str = "general", filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform a web search for the given query.
        
        Args:
            query (str): The search query string
            search_type (str): Type of search (general, news, academic, etc.)
            filters (dict): Search filters (date, language, etc.)
            
        Returns:
            dict: Search results containing title, snippet, url, and metadata
        """
        try:
            logger.info(f"🔍 Performing web search for: {query}")
            
            # Check cache first
            cache_key = f"{query}_{search_type}_{hash(str(filters))}"
            if cache_key in self.search_cache:
                logger.info("📋 Returning cached search results")
                return self.search_cache[cache_key]
            
            # Perform search based on type
            if search_type == "news":
                results = await self._search_news(query, filters)
            elif search_type == "academic":
                results = await self._search_academic(query, filters)
            elif search_type == "jobs":
                results = await self._search_jobs(query, filters)
            else:
                results = await self._search_general(query, filters)
            
            # Process and filter results
            processed_results = await self._process_results(results, query)
            
            # Store in cache
            self.search_cache[cache_key] = processed_results
            
            # Log search
            self._log_search(query, search_type, len(processed_results.get('results', [])))
            
            return processed_results
            
        except Exception as e:
            logger.error(f"❌ Web search failed: {str(e)}")
            return {
                'error': str(e),
                'results': [],
                'total_results': 0,
                'search_time': 0
            }
    
    async def _search_general(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform general web search"""
        # Simulate search delay
        await asyncio.sleep(0.5)
        
        # Generate mock results based on query
        results = []
        
        # Extract key terms from query
        terms = query.lower().split()
        
        for i in range(self.max_results):
            result = {
                'title': f'Result {i+1} for "{query}"',
                'snippet': f'This is a simulated search result for {query}. It contains relevant information about {", ".join(terms[:3])}.',
                'url': f'https://example.com/result{i+1}',
                'domain': 'example.com',
                'date': datetime.now().isoformat(),
                'relevance_score': max(0.1, 1.0 - (i * 0.1)),
                'type': 'webpage'
            }
            results.append(result)
        
        return {
            'results': results,
            'total_results': len(results),
            'search_time': 0.5,
            'query': query
        }
    
    async def _search_news(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform news search"""
        await asyncio.sleep(0.3)
        
        results = []
        for i in range(min(5, self.max_results)):
            result = {
                'title': f'News: {query} - Latest Updates',
                'snippet': f'Breaking news about {query}. Recent developments and analysis.',
                'url': f'https://news.example.com/article{i+1}',
                'domain': 'news.example.com',
                'date': datetime.now().isoformat(),
                'relevance_score': max(0.1, 1.0 - (i * 0.2)),
                'type': 'news'
            }
            results.append(result)
        
        return {
            'results': results,
            'total_results': len(results),
            'search_time': 0.3,
            'query': query
        }
    
    async def _search_academic(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform academic search"""
        await asyncio.sleep(0.7)
        
        results = []
        for i in range(min(8, self.max_results)):
            result = {
                'title': f'Research Paper: {query} - Academic Study',
                'snippet': f'Academic research and scholarly analysis of {query}. Peer-reviewed study with comprehensive findings.',
                'url': f'https://scholar.example.com/paper{i+1}',
                'domain': 'scholar.example.com',
                'date': datetime.now().isoformat(),
                'relevance_score': max(0.1, 1.0 - (i * 0.15)),
                'type': 'academic'
            }
            results.append(result)
        
        return {
            'results': results,
            'total_results': len(results),
            'search_time': 0.7,
            'query': query
        }
    
    async def _search_jobs(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform job search"""
        await asyncio.sleep(0.4)
        
        results = []
        job_titles = [
            f'Remote {query} Developer',
            f'Freelance {query} Specialist',
            f'{query} Consultant Position',
            f'Part-time {query} Role',
            f'Contract {query} Work'
        ]
        
        for i, title in enumerate(job_titles[:self.max_results]):
            result = {
                'title': title,
                'snippet': f'Job opportunity for {query} professionals. Competitive salary and remote work options available.',
                'url': f'https://jobs.example.com/position{i+1}',
                'domain': 'jobs.example.com',
                'date': datetime.now().isoformat(),
                'relevance_score': max(0.1, 1.0 - (i * 0.1)),
                'type': 'job'
            }
            results.append(result)
        
        return {
            'results': results,
            'total_results': len(results),
            'search_time': 0.4,
            'query': query
        }
    
    async def _process_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Process and enhance search results"""
        processed_results = results.copy()
        
        # Add query analysis
        processed_results['query_analysis'] = self._analyze_query(query)
        
        # Add result summary
        processed_results['summary'] = self._generate_summary(results.get('results', []))
        
        # Add search suggestions
        processed_results['suggestions'] = self._generate_search_suggestions(query)
        
        return processed_results
    
    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze search query for insights"""
        terms = query.lower().split()
        
        return {
            'word_count': len(terms),
            'key_terms': terms[:5],
            'query_type': self._classify_query(query),
            'complexity': 'simple' if len(terms) <= 3 else 'complex',
            'language': 'english'  # Default assumption
        }
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['job', 'career', 'position', 'hire']):
            return 'job_search'
        elif any(word in query_lower for word in ['news', 'latest', 'update']):
            return 'news'
        elif any(word in query_lower for word in ['research', 'study', 'paper', 'academic']):
            return 'academic'
        elif any(word in query_lower for word in ['how to', 'tutorial', 'guide']):
            return 'how_to'
        elif any(word in query_lower for word in ['price', 'cost', 'rate']):
            return 'pricing'
        else:
            return 'general'
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of search results"""
        if not results:
            return {'message': 'No results found'}
        
        domains = [result.get('domain', 'unknown') for result in results]
        types = [result.get('type', 'unknown') for result in results]
        
        return {
            'total_results': len(results),
            'top_domains': list(set(domains))[:3],
            'result_types': list(set(types)),
            'average_relevance': sum(r.get('relevance_score', 0) for r in results) / len(results),
            'date_range': {
                'earliest': min(r.get('date', '') for r in results),
                'latest': max(r.get('date', '') for r in results)
            }
        }
    
    def _generate_search_suggestions(self, query: str) -> List[str]:
        """Generate related search suggestions"""
        suggestions = []
        
        # Add common variations
        if 'freelance' in query.lower():
            suggestions.extend([
                f"{query} rates",
                f"{query} jobs",
                f"{query} portfolio",
                f"{query} skills"
            ])
        elif 'job' in query.lower():
            suggestions.extend([
                f"{query} remote",
                f"{query} salary",
                f"{query} requirements",
                f"{query} interview"
            ])
        else:
            suggestions.extend([
                f"{query} tutorial",
                f"{query} examples",
                f"{query} best practices",
                f"{query} tools"
            ])
        
        return suggestions[:5]
    
    def _log_search(self, query: str, search_type: str, result_count: int):
        """Log search activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'search_type': search_type,
            'result_count': result_count
        }
        
        self.search_history.append(log_entry)
        
        # Keep only last 100 searches
        if len(self.search_history) > 100:
            self.search_history = self.search_history[-100:]
    
    async def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history"""
        return self.search_history[-limit:]
    
    async def clear_cache(self):
        """Clear search cache"""
        self.search_cache.clear()
        logger.info("🗑️ Search cache cleared")
    
    async def get_search_statistics(self) -> Dict[str, Any]:
        """Get search statistics"""
        if not self.search_history:
            return {'message': 'No search history available'}
        
        total_searches = len(self.search_history)
        search_types = {}
        popular_queries = {}
        
        for entry in self.search_history:
            # Count search types
            search_type = entry.get('search_type', 'unknown')
            search_types[search_type] = search_types.get(search_type, 0) + 1
            
            # Count popular queries
            query = entry.get('query', '')
            popular_queries[query] = popular_queries.get(query, 0) + 1
        
        return {
            'total_searches': total_searches,
            'search_types': search_types,
            'popular_queries': dict(sorted(popular_queries.items(), key=lambda x: x[1], reverse=True)[:5]),
            'cache_size': len(self.search_cache)
        }

# Global instance for easy access
web_search_tool = WebSearchTool()

# Backward compatibility function
async def search(query: str) -> dict:
    """
    Perform a web search for the given query.
    
    Args:
        query (str): The search query string
        
    Returns:
        dict: Search results containing title, snippet and url
    """
    return await web_search_tool.search(query)
