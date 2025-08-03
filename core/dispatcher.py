"""
FreelanceX.AI Task Dispatcher
Routes tasks to appropriate agents based on capabilities and availability
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class TaskDispatcher:
    """
    Intelligent task dispatcher that routes tasks to the most appropriate agent
    Uses capability matching, load balancing, and priority management
    """
    
    def __init__(self):
        self.agent_manager = None
        self.task_history = []
        self.routing_rules = self._initialize_routing_rules()
        self.priority_queue = asyncio.PriorityQueue()
        
    def set_agent_manager(self, agent_manager):
        """Set the agent manager reference"""
        self.agent_manager = agent_manager
    
    def _initialize_routing_rules(self) -> Dict[str, List[str]]:
        """Initialize routing rules for different task types"""
        return {
            'job_search': ['job_search_agent'],
            'proposal_writing': ['proposal_writer_agent'],
            'project_planning': ['planning_agent'],
            'invoicing': ['invoice_agent'],
            'client_communication': ['client_agent'],
            'market_research': ['job_search_agent', 'web_search'],
            'financial_analysis': ['invoice_agent', 'math_agent'],
            'content_creation': ['proposal_writer_agent'],
            'scheduling': ['planning_agent'],
            'follow_up': ['client_agent']
        }
    
    async def dispatch_task(self, task_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatch a task to the most appropriate agent
        
        Args:
            task_analysis: Analysis result from executive agent containing:
                - task_type: Type of task
                - priority: Task priority (1-10)
                - required_capabilities: List of required capabilities
                - content: Task content
                - user_id: User identifier
        """
        try:
            task_type = task_analysis.get('task_type', 'general')
            priority = task_analysis.get('priority', 5)
            required_capabilities = task_analysis.get('required_capabilities', [])
            content = task_analysis.get('content', '')
            user_id = task_analysis.get('user_id', 'default')
            
            # Find suitable agents
            suitable_agents = await self._find_suitable_agents(task_type, required_capabilities)
            
            if not suitable_agents:
                return {
                    'success': False,
                    'error': f'No suitable agents found for task type: {task_type}',
                    'task_type': task_type
                }
            
            # Select best agent based on load balancing and priority
            selected_agent = await self._select_best_agent(suitable_agents, priority)
            
            if not selected_agent:
                return {
                    'success': False,
                    'error': 'No available agents to handle the task',
                    'task_type': task_type
                }
            
            # Prepare task data
            task_data = {
                'task_type': task_type,
                'content': content,
                'user_id': user_id,
                'priority': priority,
                'timestamp': datetime.now().isoformat(),
                'required_capabilities': required_capabilities
            }
            
            # Execute task
            result = await self.agent_manager.execute_task(selected_agent.agent_id, task_data)
            
            # Log task execution
            self._log_task_execution(task_analysis, selected_agent, result)
            
            return {
                'success': True,
                'result': result,
                'agent_used': selected_agent.name,
                'agent_id': selected_agent.agent_id,
                'task_type': task_type
            }
            
        except Exception as e:
            logger.error(f"❌ Task dispatch failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'task_type': task_analysis.get('task_type', 'unknown')
            }
    
    async def _find_suitable_agents(self, task_type: str, required_capabilities: List[str]) -> List[Any]:
        """Find agents suitable for the task"""
        suitable_agents = []
        
        # Get routing rules for task type
        preferred_agents = self.routing_rules.get(task_type, [])
        
        # Get all enabled agents
        enabled_agents = await self.agent_manager.get_enabled_agents()
        
        for agent in enabled_agents:
            # Check if agent has required capabilities
            has_capabilities = all(
                agent.has_capability(cap) for cap in required_capabilities
            )
            
            # Check if agent is in preferred list or has matching capabilities
            is_preferred = any(
                preferred_agent in agent.name.lower() 
                for preferred_agent in preferred_agents
            )
            
            if has_capabilities or is_preferred:
                suitable_agents.append(agent)
        
        # If no agents found by capabilities, try fuzzy matching
        if not suitable_agents:
            suitable_agents = await self._fuzzy_match_agents(task_type, enabled_agents)
        
        return suitable_agents
    
    async def _fuzzy_match_agents(self, task_type: str, agents: List[Any]) -> List[Any]:
        """Fuzzy match agents based on task type keywords"""
        task_keywords = self._extract_keywords(task_type)
        matched_agents = []
        
        for agent in agents:
            agent_capabilities = agent.get_capabilities()
            agent_name = agent.name.lower()
            
            # Check for keyword matches in capabilities and name
            for keyword in task_keywords:
                if (keyword in agent_name or 
                    any(keyword in cap.lower() for cap in agent_capabilities)):
                    matched_agents.append(agent)
                    break
        
        return matched_agents
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for fuzzy matching"""
        # Remove common words and extract meaningful keywords
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in common_words and len(word) > 2]
        return keywords
    
    async def _select_best_agent(self, suitable_agents: List[Any], priority: int) -> Optional[Any]:
        """Select the best agent based on load balancing and priority"""
        if not suitable_agents:
            return None
        
        # Get agent statuses
        agent_statuses = await self.agent_manager.get_all_status()
        
        # Score agents based on multiple factors
        agent_scores = []
        
        for agent in suitable_agents:
            status = agent_statuses.get(agent.agent_id)
            if not status:
                continue
            
            # Calculate score based on multiple factors
            score = self._calculate_agent_score(agent, status, priority)
            agent_scores.append((score, agent))
        
        # Sort by score (higher is better) and return the best
        agent_scores.sort(key=lambda x: x[0], reverse=True)
        
        if agent_scores:
            return agent_scores[0][1]
        
        return None
    
    def _calculate_agent_score(self, agent: Any, status: Any, priority: int) -> float:
        """Calculate agent score for selection"""
        score = 0.0
        
        # Base score from priority
        score += priority * 10
        
        # Availability bonus (idle agents get higher score)
        if status.status == 'idle':
            score += 50
        elif status.status == 'busy':
            score += 20
        elif status.status == 'error':
            score -= 100
        
        # Performance bonus (lower error rate, higher task count)
        if status.task_count > 0:
            error_rate = status.error_count / status.task_count
            score += (1 - error_rate) * 30
        
        # Response time bonus (faster agents get higher score)
        if status.avg_response_time > 0:
            response_bonus = max(0, 10 - status.avg_response_time)
            score += response_bonus
        
        # Recent activity bonus
        time_since_activity = (datetime.now() - status.last_activity).total_seconds()
        if time_since_activity < 300:  # 5 minutes
            score += 10
        
        return score
    
    def _log_task_execution(self, task_analysis: Dict[str, Any], agent: Any, result: Dict[str, Any]):
        """Log task execution for analytics"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_analysis.get('task_type'),
            'agent_name': agent.name,
            'agent_id': agent.agent_id,
            'success': result.get('success', False),
            'response_time': result.get('response_time', 0),
            'user_id': task_analysis.get('user_id', 'default')
        }
        
        self.task_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]
    
    async def get_task_statistics(self) -> Dict[str, Any]:
        """Get task execution statistics"""
        if not self.task_history:
            return {
                'total_tasks': 0,
                'success_rate': 0,
                'avg_response_time': 0,
                'task_types': {},
                'agent_performance': {}
            }
        
        total_tasks = len(self.task_history)
        successful_tasks = sum(1 for task in self.task_history if task['success'])
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        response_times = [task['response_time'] for task in self.task_history if task['response_time'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Task type distribution
        task_types = {}
        for task in self.task_history:
            task_type = task['task_type']
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        # Agent performance
        agent_performance = {}
        for task in self.task_history:
            agent_name = task['agent_name']
            if agent_name not in agent_performance:
                agent_performance[agent_name] = {
                    'total_tasks': 0,
                    'successful_tasks': 0,
                    'total_response_time': 0
                }
            
            agent_performance[agent_name]['total_tasks'] += 1
            if task['success']:
                agent_performance[agent_name]['successful_tasks'] += 1
            agent_performance[agent_name]['total_response_time'] += task['response_time']
        
        # Calculate success rates and avg response times for agents
        for agent_name, stats in agent_performance.items():
            stats['success_rate'] = stats['successful_tasks'] / stats['total_tasks']
            stats['avg_response_time'] = stats['total_response_time'] / stats['total_tasks']
        
        return {
            'total_tasks': total_tasks,
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'task_types': task_types,
            'agent_performance': agent_performance
        }
    
    async def add_routing_rule(self, task_type: str, agent_names: List[str]):
        """Add a new routing rule"""
        self.routing_rules[task_type] = agent_names
        logger.info(f"📋 Added routing rule: {task_type} -> {agent_names}")
    
    async def remove_routing_rule(self, task_type: str):
        """Remove a routing rule"""
        if task_type in self.routing_rules:
            del self.routing_rules[task_type]
            logger.info(f"🗑️ Removed routing rule: {task_type}")
    
    async def get_routing_rules(self) -> Dict[str, List[str]]:
        """Get all routing rules"""
        return self.routing_rules.copy() 