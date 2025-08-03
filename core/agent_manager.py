"""
FreelanceX.AI Agent Manager
Manages agent registration, lifecycle, and coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

@dataclass
class AgentStatus:
    """Status information for an agent"""
    agent_id: str
    name: str
    status: str  # 'idle', 'busy', 'error', 'disabled'
    last_activity: datetime
    task_count: int
    error_count: int
    avg_response_time: float

class BaseAgent(ABC):
    """
    Base class for all FreelanceX.AI agents
    Provides common functionality and interface
    """
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.status = 'idle'
        self.task_count = 0
        self.error_count = 0
        self.response_times = []
        self.last_activity = datetime.now()
        self.tools = {}
        self.memory = {}
        
    @abstractmethod
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass
    
    async def initialize(self):
        """Initialize agent resources"""
        try:
            logger.info(f"🚀 Initializing agent: {self.name}")
            self.status = 'idle'
            logger.info(f"✅ Agent {self.name} initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent {self.name}: {str(e)}")
            self.status = 'error'
            raise
    
    async def shutdown(self):
        """Cleanup agent resources"""
        try:
            logger.info(f"🛑 Shutting down agent: {self.name}")
            self.status = 'disabled'
            logger.info(f"✅ Agent {self.name} shut down")
        except Exception as e:
            logger.error(f"❌ Error shutting down agent {self.name}: {str(e)}")
    
    def get_status(self) -> AgentStatus:
        """Get current agent status"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return AgentStatus(
            agent_id=self.agent_id,
            name=self.name,
            status=self.status,
            last_activity=self.last_activity,
            task_count=self.task_count,
            error_count=self.error_count,
            avg_response_time=avg_response_time
        )
    
    def add_tool(self, tool_name: str, tool_func):
        """Add a tool to the agent"""
        self.tools[tool_name] = tool_func
        logger.info(f"🔧 Added tool {tool_name} to agent {self.name}")
    
    def has_capability(self, capability: str) -> bool:
        """Check if agent has specific capability"""
        return capability in self.get_capabilities()

class AgentManager:
    """
    Central manager for all FreelanceX.AI agents
    Handles registration, lifecycle management, and coordination
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_status: Dict[str, AgentStatus] = {}
        self.task_queue = asyncio.Queue()
        self.running = False
        self.max_concurrent_tasks = 10
        self.active_tasks = 0
        
    async def register_agent(self, agent: BaseAgent) -> bool:
        """Register a new agent"""
        try:
            if agent.agent_id in self.agents:
                logger.warning(f"⚠️ Agent {agent.name} already registered")
                return False
            
            # Initialize the agent
            await agent.initialize()
            
            # Register the agent
            self.agents[agent.agent_id] = agent
            self.agent_status[agent.agent_id] = agent.get_status()
            
            logger.info(f"📋 Registered agent: {agent.name} (ID: {agent.agent_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register agent {agent.name}: {str(e)}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        try:
            if agent_id not in self.agents:
                logger.warning(f"⚠️ Agent {agent_id} not found")
                return False
            
            agent = self.agents[agent_id]
            await agent.shutdown()
            
            del self.agents[agent_id]
            del self.agent_status[agent_id]
            
            logger.info(f"🗑️ Unregistered agent: {agent.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unregister agent {agent_id}: {str(e)}")
            return False
    
    async def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    async def get_agent_by_capability(self, capability: str) -> Optional[BaseAgent]:
        """Find agent with specific capability"""
        for agent in self.agents.values():
            if agent.has_capability(capability) and agent.status != 'disabled':
                return agent
        return None
    
    async def get_agent_by_name(self, name: str) -> Optional[BaseAgent]:
        """Find agent by name"""
        for agent in self.agents.values():
            if agent.name == name:
                return agent
        return None
    
    async def execute_task(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with a specific agent"""
        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not found'
                }
            
            if agent.status == 'disabled':
                return {
                    'success': False,
                    'error': f'Agent {agent.name} is disabled'
                }
            
            # Update agent status
            agent.status = 'busy'
            agent.last_activity = datetime.now()
            start_time = datetime.now()
            
            # Execute task
            result = await agent.process_task(task_data)
            
            # Update metrics
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            agent.response_times.append(response_time)
            agent.task_count += 1
            agent.status = 'idle'
            
            # Keep only last 100 response times for average calculation
            if len(agent.response_times) > 100:
                agent.response_times = agent.response_times[-100:]
            
            # Update status
            self.agent_status[agent_id] = agent.get_status()
            
            logger.info(f"✅ Task completed by {agent.name} in {response_time:.2f}s")
            return {
                'success': True,
                'result': result,
                'agent_id': agent_id,
                'response_time': response_time
            }
            
        except Exception as e:
            logger.error(f"❌ Task execution failed for agent {agent_id}: {str(e)}")
            
            # Update error metrics
            if agent:
                agent.error_count += 1
                agent.status = 'error'
                self.agent_status[agent_id] = agent.get_status()
            
            return {
                'success': False,
                'error': str(e),
                'agent_id': agent_id
            }
    
    async def get_all_status(self) -> Dict[str, AgentStatus]:
        """Get status of all agents"""
        for agent_id, agent in self.agents.items():
            self.agent_status[agent_id] = agent.get_status()
        return self.agent_status.copy()
    
    async def get_enabled_agents(self) -> List[BaseAgent]:
        """Get all enabled agents"""
        return [agent for agent in self.agents.values() if agent.status != 'disabled']
    
    async def enable_agent(self, agent_id: str) -> bool:
        """Enable a disabled agent"""
        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                return False
            
            await agent.initialize()
            logger.info(f"✅ Enabled agent: {agent.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enable agent {agent_id}: {str(e)}")
            return False
    
    async def disable_agent(self, agent_id: str) -> bool:
        """Disable an agent"""
        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                return False
            
            agent.status = 'disabled'
            logger.info(f"⏸️ Disabled agent: {agent.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to disable agent {agent_id}: {str(e)}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents"""
        health_status = {
            'overall': 'healthy',
            'agents': {},
            'total_agents': len(self.agents),
            'enabled_agents': len(await self.get_enabled_agents()),
            'errors': []
        }
        
        for agent_id, agent in self.agents.items():
            agent_health = {
                'status': agent.status,
                'task_count': agent.task_count,
                'error_count': agent.error_count,
                'last_activity': agent.last_activity.isoformat()
            }
            
            if agent.status == 'error':
                health_status['overall'] = 'degraded'
                health_status['errors'].append(f"Agent {agent.name} is in error state")
            
            health_status['agents'][agent_id] = agent_health
        
        return health_status
    
    async def start(self):
        """Start the agent manager"""
        self.running = True
        logger.info("🚀 Agent Manager started")
        
        # Start background task processor
        asyncio.create_task(self._process_task_queue())
    
    async def stop(self):
        """Stop the agent manager"""
        self.running = False
        logger.info("🛑 Agent Manager stopping...")
        
        # Shutdown all agents
        for agent in self.agents.values():
            await agent.shutdown()
        
        logger.info("✅ Agent Manager stopped")
    
    async def _process_task_queue(self):
        """Background task processor"""
        while self.running:
            try:
                # Process tasks from queue
                if not self.task_queue.empty() and self.active_tasks < self.max_concurrent_tasks:
                    task = await self.task_queue.get()
                    self.active_tasks += 1
                    
                    # Execute task in background
                    asyncio.create_task(self._execute_queued_task(task))
                
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"❌ Task queue processing error: {str(e)}")
                await asyncio.sleep(1)
    
    async def _execute_queued_task(self, task):
        """Execute a queued task"""
        try:
            await self.execute_task(task['agent_id'], task['task_data'])
        finally:
            self.active_tasks -= 1
    
    async def queue_task(self, agent_id: str, task_data: Dict[str, Any]):
        """Queue a task for execution"""
        await self.task_queue.put({
            'agent_id': agent_id,
            'task_data': task_data
        })
