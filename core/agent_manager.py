import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import uuid
from enum import Enum

# Import the core agents
from agents.job_search_agent import JobSearchAgent, JobListing
from agents.web_search_agent import WebSearchAgent, SearchResult, ResearchTopic
from agents.math_agent import MathAgent, CalculationResult, StatisticalAnalysis, FinancialProjection

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AgentTask:
    """Data class for agent tasks"""
    id: str
    task_type: str
    agent_id: str
    priority: TaskPriority
    status: TaskStatus
    input_data: Dict[str, Any]
    result: Optional[Any] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class AgentNegotiation:
    """Data class for agent negotiations"""
    id: str
    initiating_agent: str
    target_agent: str
    negotiation_type: str
    proposal: Dict[str, Any]
    status: str  # pending, accepted, rejected, counter_proposal
    created_at: datetime
    resolved_at: Optional[datetime] = None
    final_agreement: Optional[Dict[str, Any]] = None

class AgentManager:
    """
    Enhanced Agent Manager for FreelanceX.AI
    
    Unified Framework: All agents work together via a centralized API layer, 
    facilitating task handoffs when needed.
    
    Negotiation Protocols: If two agents' recommendations clash, they will negotiate 
    to provide a solution that optimizes for the user's long-term goals.
    
    Transparency: The system logs all negotiations and decisions made by agents 
    for later review by users, ensuring accountability.
    """
    
    def __init__(self, user_profile: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.user_profile = user_profile or {}
        
        # Initialize core agents
        self.job_search_agent = JobSearchAgent(user_profile)
        self.web_search_agent = WebSearchAgent(user_profile)
        self.math_agent = MathAgent(user_profile)
        
        # Agent registry
        self.agents = {
            'job_search': self.job_search_agent,
            'web_search': self.web_search_agent,
            'math': self.math_agent
        }
        
        # Task management
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []
        
        # Negotiation system
        self.negotiations = []
        self.negotiation_history = []
        
        # System state
        self.system_status = {
            'agents_online': list(self.agents.keys()),
            'last_health_check': datetime.now(),
            'total_tasks_processed': 0,
            'success_rate': 1.0,
            'average_response_time': 0.0
        }
        
        # Memory and learning
        self.system_memory = {
            'user_interactions': [],
            'successful_patterns': [],
            'failed_patterns': [],
            'agent_collaborations': [],
            'optimization_suggestions': []
        }
        
        # Configuration
        self.config = {
            'max_concurrent_tasks': 10,
            'task_timeout': 300,  # 5 minutes
            'negotiation_timeout': 60,  # 1 minute
            'auto_negotiation': True,
            'learning_enabled': True,
            'transparency_logging': True
        }

    async def start(self):
        """Start the agent manager and all agents"""
        self.logger.info("Starting FreelanceX.AI Agent Manager...")
        
        # Initialize all agents
        for agent_id, agent in self.agents.items():
            try:
                if hasattr(agent, 'set_user_profile'):
                    agent.set_user_profile(self.user_profile)
                self.logger.info(f"Agent {agent_id} initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_id}: {e}")
        
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._task_processing_loop())
        asyncio.create_task(self._memory_cleanup_loop())
        
        self.logger.info("Agent Manager started successfully")

    async def stop(self):
        """Stop the agent manager and all agents"""
        self.logger.info("Stopping FreelanceX.AI Agent Manager...")
        
        # Cancel all active tasks
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)
        
        # Stop background loops
        # (In a real implementation, you'd have proper task cancellation)
        
        self.logger.info("Agent Manager stopped")

    async def submit_task(self, task_type: str, agent_id: str, input_data: Dict[str, Any], 
                         priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """
        Submit a task to a specific agent
        
        Args:
            task_type: Type of task to execute
            agent_id: ID of the agent to handle the task
            input_data: Input data for the task
            priority: Task priority level
            
        Returns:
            Task ID for tracking
        """
        if agent_id not in self.agents:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        task_id = str(uuid.uuid4())
        task = AgentTask(
            id=task_id,
            task_type=task_type,
            agent_id=agent_id,
            priority=priority,
            status=TaskStatus.PENDING,
            input_data=input_data,
            created_at=datetime.now(),
            metadata={'submitted_by': 'user'}
        )
        
        # Add to task queue
        self.task_queue.append(task)
        
        # Sort queue by priority
        self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
        
        self.logger.info(f"Task {task_id} submitted to {agent_id} with priority {priority.name}")
        return task_id

    async def get_task_status(self, task_id: str) -> Optional[AgentTask]:
        """Get the status of a specific task"""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check completed tasks
        for task in self.completed_tasks:
            if task.id == task_id:
                return task
        
        # Check failed tasks
        for task in self.failed_tasks:
            if task.id == task_id:
                return task
        
        return None

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or active task"""
        # Remove from queue
        self.task_queue = [t for t in self.task_queue if t.id != task_id]
        
        # Cancel active task
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.now()
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            return True
        
        return False

    async def _task_processing_loop(self):
        """Background loop for processing tasks"""
        while True:
            try:
                # Process tasks if we have capacity
                if len(self.active_tasks) < self.config['max_concurrent_tasks'] and self.task_queue:
                    task = self.task_queue.pop(0)
                    asyncio.create_task(self._execute_task(task))
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(5)

    async def _execute_task(self, task: AgentTask):
        """Execute a specific task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        self.active_tasks[task.id] = task
        
        try:
            agent = self.agents[task.agent_id]
            result = await self._call_agent_method(agent, task.task_type, task.input_data)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task.id]
            
            # Update system metrics
            self.system_status['total_tasks_processed'] += 1
            
            self.logger.info(f"Task {task.id} completed successfully")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            # Move to failed tasks
            self.failed_tasks.append(task)
            del self.active_tasks[task.id]
            
            self.logger.error(f"Task {task.id} failed: {e}")

    async def _call_agent_method(self, agent, method_name: str, input_data: Dict[str, Any]):
        """Call a method on an agent with proper error handling"""
        if not hasattr(agent, method_name):
            raise ValueError(f"Agent does not have method: {method_name}")
        
        method = getattr(agent, method_name)
        
        if asyncio.iscoroutinefunction(method):
            return await method(**input_data)
        else:
            return method(**input_data)

    async def coordinate_agents(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Coordinate multiple agents to fulfill a complex user request
        
        Args:
            user_request: Natural language request from user
            context: Additional context information
            
        Returns:
            Coordinated response from multiple agents
        """
        self.logger.info(f"Coordinating agents for request: {user_request}")
        
        # Analyze request to determine required agents
        required_agents = self._analyze_request(user_request)
        
        # Create tasks for each required agent
        tasks = []
        for agent_id, task_config in required_agents.items():
            task_id = await self.submit_task(
                task_config['task_type'],
                agent_id,
                task_config['input_data'],
                task_config['priority']
            )
            tasks.append(task_id)
        
        # Wait for all tasks to complete
        results = {}
        for task_id in tasks:
            while True:
                task = await self.get_task_status(task_id)
                if task and task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    if task.status == TaskStatus.COMPLETED:
                        results[task.agent_id] = task.result
                    break
                await asyncio.sleep(0.1)
        
        # Check for conflicts and negotiate if necessary
        if len(results) > 1:
            conflicts = self._identify_conflicts(results)
            if conflicts:
                resolved_results = await self._negotiate_conflicts(conflicts, results)
                results.update(resolved_results)
        
        # Synthesize final response
        final_response = await self._synthesize_response(user_request, results, context)
        
        # Log the coordination for transparency
        if self.config['transparency_logging']:
            self._log_coordination(user_request, required_agents, results, final_response)
        
        return final_response

    def _analyze_request(self, user_request: str) -> Dict[str, Dict[str, Any]]:
        """Analyze user request to determine required agents and tasks"""
        required_agents = {}
        
        # Simple keyword-based analysis (could be enhanced with NLP)
        request_lower = user_request.lower()
        
        # Job search related
        if any(keyword in request_lower for keyword in ['job', 'work', 'opportunity', 'position', 'hire']):
            required_agents['job_search'] = {
                'task_type': 'find_jobs',
                'input_data': {'platforms': None, 'use_ai_matching': True},
                'priority': TaskPriority.HIGH
            }
        
        # Research related
        if any(keyword in request_lower for keyword in ['research', 'find', 'search', 'information', 'trend']):
            required_agents['web_search'] = {
                'task_type': 'research_topic',
                'input_data': {'topic': user_request, 'depth': 'comprehensive'},
                'priority': TaskPriority.MEDIUM
            }
        
        # Math/Financial related
        if any(keyword in request_lower for keyword in ['calculate', 'math', 'financial', 'budget', 'rate', 'price']):
            required_agents['math'] = {
                'task_type': 'calculate_financial_metrics',
                'input_data': self._extract_financial_data(user_request),
                'priority': TaskPriority.MEDIUM
            }
        
        return required_agents

    def _extract_financial_data(self, user_request: str) -> Dict[str, Any]:
        """Extract financial data from user request"""
        # Simple extraction (could be enhanced with NLP)
        data = {}
        
        # Extract numbers that might be amounts
        import re
        amounts = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', user_request)
        if amounts:
            data['amount'] = float(amounts[0].replace(',', ''))
        
        return data

    def _identify_conflicts(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify conflicts between agent results"""
        conflicts = []
        
        # Example: Job search and math agent might have conflicting recommendations
        if 'job_search' in results and 'math' in results:
            jobs = results['job_search']
            financial_analysis = results['math']
            
            # Check if recommended jobs match financial goals
            if isinstance(jobs, list) and isinstance(financial_analysis, dict):
                for job in jobs:
                    if hasattr(job, 'budget') and 'hourly_rate' in financial_analysis:
                        if job.budget < financial_analysis['hourly_rate'] * 40:  # Assuming 40-hour project
                            conflicts.append({
                                'type': 'salary_mismatch',
                                'agents': ['job_search', 'math'],
                                'description': f"Job budget ${job.budget} is below recommended rate",
                                'data': {'job': job, 'recommended_rate': financial_analysis['hourly_rate']}
                            })
        
        return conflicts

    async def _negotiate_conflicts(self, conflicts: List[Dict[str, Any]], 
                                 results: Dict[str, Any]) -> Dict[str, Any]:
        """Negotiate conflicts between agents"""
        resolved_results = results.copy()
        
        for conflict in conflicts:
            negotiation = AgentNegotiation(
                id=str(uuid.uuid4()),
                initiating_agent=conflict['agents'][0],
                target_agent=conflict['agents'][1],
                negotiation_type=conflict['type'],
                proposal={'conflict': conflict, 'current_results': results},
                status='pending',
                created_at=datetime.now()
            )
            
            self.negotiations.append(negotiation)
            
            # Simulate negotiation process
            if conflict['type'] == 'salary_mismatch':
                # Math agent suggests filtering out low-paying jobs
                resolved_results['job_search'] = [
                    job for job in results['job_search']
                    if hasattr(job, 'budget') and job.budget >= results['math']['hourly_rate'] * 40
                ]
                
                negotiation.status = 'resolved'
                negotiation.final_agreement = {
                    'action': 'filtered_low_paying_jobs',
                    'filtered_count': len(results['job_search']) - len(resolved_results['job_search'])
                }
            
            negotiation.resolved_at = datetime.now()
            self.negotiation_history.append(negotiation)
        
        return resolved_results

    async def _synthesize_response(self, user_request: str, results: Dict[str, Any], 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Synthesize a coherent response from multiple agent results"""
        response = {
            'user_request': user_request,
            'agents_consulted': list(results.keys()),
            'timestamp': datetime.now(),
            'summary': '',
            'detailed_results': results,
            'recommendations': [],
            'next_actions': []
        }
        
        # Generate summary based on results
        if 'job_search' in results:
            jobs = results['job_search']
            if isinstance(jobs, list):
                response['summary'] += f"Found {len(jobs)} relevant job opportunities. "
                response['recommendations'].append("Review the job listings and apply to the most suitable ones.")
        
        if 'web_search' in results:
            research = results['web_search']
            if isinstance(research, dict) and 'insights' in research:
                response['summary'] += f"Research completed with {len(research.get('results', []))} sources. "
                response['recommendations'].extend(research.get('insights', {}).get('recommendations', []))
        
        if 'math' in results:
            calculations = results['math']
            if hasattr(calculations, 'result'):
                response['summary'] += f"Financial analysis completed. "
                response['recommendations'].append("Use the calculated rates for your pricing strategy.")
        
        # Generate next actions
        response['next_actions'] = [
            "Review all recommendations",
            "Take action on high-priority items",
            "Schedule follow-up analysis if needed"
        ]
        
        return response

    def _log_coordination(self, user_request: str, required_agents: Dict[str, Any], 
                         results: Dict[str, Any], final_response: Dict[str, Any]):
        """Log coordination details for transparency"""
        log_entry = {
            'timestamp': datetime.now(),
            'user_request': user_request,
            'agents_used': list(required_agents.keys()),
            'negotiations': len(self.negotiations),
            'conflicts_resolved': len([n for n in self.negotiations if n.status == 'resolved']),
            'final_recommendations': len(final_response.get('recommendations', [])),
            'user_profile_used': bool(self.user_profile)
        }
        
        self.system_memory['user_interactions'].append(log_entry)

    async def _health_check_loop(self):
        """Background loop for agent health checks"""
        while True:
            try:
                for agent_id, agent in self.agents.items():
                    # Simple health check - could be more sophisticated
                    if hasattr(agent, 'logger'):
                        # Agent is responsive
                        pass
                
                self.system_status['last_health_check'] = datetime.now()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)

    async def _memory_cleanup_loop(self):
        """Background loop for memory cleanup"""
        while True:
            try:
                # Clean up old completed tasks
                cutoff_date = datetime.now() - timedelta(days=7)
                self.completed_tasks = [
                    task for task in self.completed_tasks
                    if task.completed_at and task.completed_at > cutoff_date
                ]
                
                # Clean up old failed tasks
                self.failed_tasks = [
                    task for task in self.failed_tasks
                    if task.completed_at and task.completed_at > cutoff_date
                ]
                
                # Clean up old negotiations
                self.negotiation_history = [
                    neg for neg in self.negotiation_history
                    if neg.created_at and neg.created_at > cutoff_date
                ]
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                self.logger.error(f"Error in memory cleanup loop: {e}")
                await asyncio.sleep(3600)

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            **self.system_status,
            'queue_length': len(self.task_queue),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'negotiations': len(self.negotiations),
            'memory_usage': len(self.system_memory['user_interactions'])
        }

    def get_agent_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all agents"""
        performance = {}
        
        for agent_id, agent in self.agents.items():
            agent_tasks = [
                task for task in self.completed_tasks + self.failed_tasks
                if task.agent_id == agent_id
            ]
            
            if agent_tasks:
                completed = [t for t in agent_tasks if t.status == TaskStatus.COMPLETED]
                failed = [t for t in agent_tasks if t.status == TaskStatus.FAILED]
                
                performance[agent_id] = {
                    'total_tasks': len(agent_tasks),
                    'completed_tasks': len(completed),
                    'failed_tasks': len(failed),
                    'success_rate': len(completed) / len(agent_tasks) if agent_tasks else 0,
                    'average_response_time': self._calculate_average_response_time(agent_tasks)
                }
        
        return performance

    def _calculate_average_response_time(self, tasks: List[AgentTask]) -> float:
        """Calculate average response time for tasks"""
        response_times = []
        
        for task in tasks:
            if task.started_at and task.completed_at:
                response_time = (task.completed_at - task.started_at).total_seconds()
                response_times.append(response_time)
        
        return sum(response_times) / len(response_times) if response_times else 0.0

    def export_system_logs(self, filename: str = None) -> str:
        """Export system logs for transparency"""
        if not filename:
            filename = f"freelancex_system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        logs = {
            'system_status': self.get_system_status(),
            'agent_performance': self.get_agent_performance(),
            'user_interactions': self.system_memory['user_interactions'],
            'negotiation_history': [
                {
                    'id': neg.id,
                    'type': neg.negotiation_type,
                    'status': neg.status,
                    'created_at': neg.created_at.isoformat(),
                    'resolved_at': neg.resolved_at.isoformat() if neg.resolved_at else None
                }
                for neg in self.negotiation_history
            ],
            'recent_tasks': [
                {
                    'id': task.id,
                    'type': task.task_type,
                    'agent': task.agent_id,
                    'status': task.status.value,
                    'created_at': task.created_at.isoformat(),
                    'completed_at': task.completed_at.isoformat() if task.completed_at else None
                }
                for task in self.completed_tasks[-50:]  # Last 50 tasks
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(logs, f, indent=2, default=str)
        
        return filename
