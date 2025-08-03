import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NegotiationStatus(Enum):
    PENDING = "pending"
    AGREED = "agreed"
    DISAGREED = "disagreed"
    COMPROMISE = "compromise"

@dataclass
class Task:
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentRequest:
    request_id: str
    from_agent: str
    to_agent: str
    request_type: str
    data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    response: Optional[Dict[str, Any]] = None
    status: str = "pending"

@dataclass
class NegotiationSession:
    session_id: str
    participants: List[str]
    topic: str
    initial_proposals: Dict[str, Any]
    status: NegotiationStatus = NegotiationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    final_agreement: Optional[Dict[str, Any]] = None
    negotiation_log: List[Dict[str, Any]] = field(default_factory=list)

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{agent_id}")
        self.capabilities = []
        self.current_tasks = []
        self.task_history = []
        
    @abstractmethod
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process a task and return results"""
        pass
    
    @abstractmethod
    async def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the given task"""
        pass
    
    async def get_capabilities(self) -> List[str]:
        """Get list of agent capabilities"""
        return self.capabilities

class AgentCollaborationManager:
    """
    Centralized agent collaboration system that manages task distribution,
    agent communication, and negotiation protocols.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self.requests: Dict[str, AgentRequest] = {}
        self.negotiations: Dict[str, NegotiationSession] = {}
        self.collaboration_log: List[Dict[str, Any]] = []
        self.task_queue = asyncio.Queue()
        self.request_queue = asyncio.Queue()
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the collaboration system"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_name} ({agent.agent_id})")
        
    async def submit_task(self, task_type: str, description: str, 
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit a task to the collaboration system
        
        Args:
            task_type: Type of task to be performed
            description: Detailed description of the task
            priority: Task priority level
            metadata: Additional task metadata
            
        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            description=description,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        
        self.logger.info(f"Submitted task: {task_id} - {task_type}")
        self._log_collaboration_event("task_submitted", {
            "task_id": task_id,
            "task_type": task_type,
            "priority": priority.value
        })
        
        return task_id
    
    async def assign_task(self, task_id: str, agent_id: str) -> bool:
        """
        Assign a task to a specific agent
        
        Args:
            task_id: ID of the task to assign
            agent_id: ID of the agent to assign the task to
            
        Returns:
            True if assignment successful, False otherwise
        """
        if task_id not in self.tasks:
            self.logger.error(f"Task {task_id} not found")
            return False
        
        if agent_id not in self.agents:
            self.logger.error(f"Agent {agent_id} not found")
            return False
        
        task = self.tasks[task_id]
        agent = self.agents[agent_id]
        
        if not await agent.can_handle_task(task):
            self.logger.warning(f"Agent {agent_id} cannot handle task {task_id}")
            return False
        
        task.assigned_agent = agent_id
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        self.logger.info(f"Assigned task {task_id} to agent {agent_id}")
        self._log_collaboration_event("task_assigned", {
            "task_id": task_id,
            "agent_id": agent_id
        })
        
        return True
    
    async def auto_assign_tasks(self) -> None:
        """Automatically assign pending tasks to available agents"""
        while not self.task_queue.empty():
            try:
                task = await self.task_queue.get()
                
                # Find best agent for the task
                best_agent = await self._find_best_agent_for_task(task)
                
                if best_agent:
                    await self.assign_task(task.task_id, best_agent.agent_id)
                else:
                    self.logger.warning(f"No suitable agent found for task {task.task_id}")
                    task.status = TaskStatus.FAILED
                    task.error = "No suitable agent available"
                    
            except Exception as e:
                self.logger.error(f"Error in auto assignment: {str(e)}")
    
    async def _find_best_agent_for_task(self, task: Task) -> Optional[BaseAgent]:
        """Find the best agent to handle a given task"""
        suitable_agents = []
        
        for agent in self.agents.values():
            if await agent.can_handle_task(task):
                # Calculate agent score based on capabilities, current load, etc.
                score = await self._calculate_agent_score(agent, task)
                suitable_agents.append((agent, score))
        
        if not suitable_agents:
            return None
        
        # Return agent with highest score
        return max(suitable_agents, key=lambda x: x[1])[0]
    
    async def _calculate_agent_score(self, agent: BaseAgent, task: Task) -> float:
        """Calculate how well an agent can handle a task"""
        score = 0.0
        
        # Base score from capabilities
        capabilities = await agent.get_capabilities()
        if task.task_type in capabilities:
            score += 10.0
        
        # Penalty for current workload
        current_tasks = len([t for t in self.tasks.values() 
                           if t.assigned_agent == agent.agent_id and 
                           t.status == TaskStatus.IN_PROGRESS])
        score -= current_tasks * 2.0
        
        # Bonus for priority matching
        if task.priority == TaskPriority.URGENT:
            score += 5.0
        
        return score
    
    async def send_request(self, from_agent_id: str, to_agent_id: str,
                          request_type: str, data: Dict[str, Any],
                          priority: TaskPriority = TaskPriority.MEDIUM) -> str:
        """
        Send a request from one agent to another
        
        Args:
            from_agent_id: ID of the requesting agent
            to_agent_id: ID of the target agent
            request_type: Type of request
            data: Request data
            priority: Request priority
            
        Returns:
            Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        request = AgentRequest(
            request_id=request_id,
            from_agent=from_agent_id,
            to_agent=to_agent_id,
            request_type=request_type,
            data=data,
            priority=priority
        )
        
        self.requests[request_id] = request
        await self.request_queue.put(request)
        
        self.logger.info(f"Request sent: {request_id} from {from_agent_id} to {to_agent_id}")
        self._log_collaboration_event("request_sent", {
            "request_id": request_id,
            "from_agent": from_agent_id,
            "to_agent": to_agent_id,
            "request_type": request_type
        })
        
        return request_id
    
    async def process_requests(self) -> None:
        """Process pending requests between agents"""
        while not self.request_queue.empty():
            try:
                request = await self.request_queue.get()
                
                if request.to_agent in self.agents:
                    agent = self.agents[request.to_agent]
                    response = await self._handle_agent_request(agent, request)
                    request.response = response
                    request.status = "completed"
                else:
                    request.status = "failed"
                    request.response = {"error": "Target agent not found"}
                    
            except Exception as e:
                self.logger.error(f"Error processing request: {str(e)}")
    
    async def _handle_agent_request(self, agent: BaseAgent, request: AgentRequest) -> Dict[str, Any]:
        """Handle a request sent to an agent"""
        try:
            # This would be implemented by each agent type
            # For now, return a generic response
            return {
                "status": "processed",
                "agent_id": agent.agent_id,
                "request_type": request.request_type,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent_id": agent.agent_id
            }
    
    async def initiate_negotiation(self, participants: List[str], topic: str,
                                 initial_proposals: Dict[str, Any]) -> str:
        """
        Initiate a negotiation session between agents
        
        Args:
            participants: List of agent IDs participating in negotiation
            topic: Topic of negotiation
            initial_proposals: Initial proposals from each participant
            
        Returns:
            Negotiation session ID
        """
        session_id = str(uuid.uuid4())
        session = NegotiationSession(
            session_id=session_id,
            participants=participants,
            topic=topic,
            initial_proposals=initial_proposals
        )
        
        self.negotiations[session_id] = session
        
        self.logger.info(f"Negotiation initiated: {session_id} - {topic}")
        self._log_collaboration_event("negotiation_initiated", {
            "session_id": session_id,
            "participants": participants,
            "topic": topic
        })
        
        return session_id
    
    async def negotiate(self, session_id: str, agent_id: str, 
                       proposal: Dict[str, Any], reasoning: str) -> Dict[str, Any]:
        """
        Submit a negotiation proposal
        
        Args:
            session_id: ID of the negotiation session
            agent_id: ID of the proposing agent
            proposal: New proposal
            reasoning: Reasoning behind the proposal
            
        Returns:
            Negotiation response
        """
        if session_id not in self.negotiations:
            return {"error": "Negotiation session not found"}
        
        session = self.negotiations[session_id]
        
        if agent_id not in session.participants:
            return {"error": "Agent not part of negotiation"}
        
        # Log the proposal
        session.negotiation_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "proposal": proposal,
            "reasoning": reasoning
        })
        
        # Check if agreement is reached
        agreement = await self._check_agreement(session, proposal)
        
        if agreement:
            session.status = NegotiationStatus.AGREED
            session.final_agreement = agreement
            session.resolved_at = datetime.now()
            
            self.logger.info(f"Negotiation {session_id} resolved with agreement")
            self._log_collaboration_event("negotiation_resolved", {
                "session_id": session_id,
                "agreement": agreement
            })
        
        return {
            "session_id": session_id,
            "status": session.status.value,
            "agreement": agreement
        }
    
    async def _check_agreement(self, session: NegotiationSession, 
                             current_proposal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check if all participants agree on a proposal"""
        # This is a simplified agreement checking mechanism
        # In practice, this would be more sophisticated
        
        if len(session.negotiation_log) < len(session.participants):
            return None  # Not all participants have proposed yet
        
        # Check if all recent proposals are similar
        recent_proposals = session.negotiation_log[-len(session.participants):]
        
        # Simple similarity check (in practice, this would be more nuanced)
        proposal_values = [p["proposal"] for p in recent_proposals]
        
        # If all proposals are the same, we have agreement
        if len(set(str(p) for p in proposal_values)) == 1:
            return proposal_values[0]
        
        return None
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific task"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        current_tasks = [t for t in self.tasks.values() 
                        if t.assigned_agent == agent_id and 
                        t.status == TaskStatus.IN_PROGRESS]
        
        return {
            "agent_id": agent.agent_id,
            "agent_name": agent.agent_name,
            "capabilities": await agent.get_capabilities(),
            "current_tasks": len(current_tasks),
            "total_tasks_completed": len([t for t in self.tasks.values() 
                                        if t.assigned_agent == agent_id and 
                                        t.status == TaskStatus.COMPLETED])
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_tasks = len(self.tasks)
        pending_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING])
        in_progress_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.FAILED])
        
        active_negotiations = len([n for n in self.negotiations.values() 
                                 if n.status == NegotiationStatus.PENDING])
        
        return {
            "total_agents": len(self.agents),
            "total_tasks": total_tasks,
            "task_status": {
                "pending": pending_tasks,
                "in_progress": in_progress_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks
            },
            "active_negotiations": active_negotiations,
            "total_requests": len(self.requests),
            "system_health": "healthy" if failed_tasks / total_tasks < 0.1 else "degraded"
        }
    
    def _log_collaboration_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log collaboration events for transparency"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.collaboration_log.append(event)
        
        # Keep log size manageable
        if len(self.collaboration_log) > 1000:
            self.collaboration_log = self.collaboration_log[-500:]
    
    async def get_collaboration_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent collaboration events"""
        return self.collaboration_log[-limit:]
    
    async def export_collaboration_data(self) -> Dict[str, Any]:
        """Export collaboration data for analysis"""
        return {
            "agents": {
                agent_id: {
                    "name": agent.agent_name,
                    "capabilities": await agent.get_capabilities()
                }
                for agent_id, agent in self.agents.items()
            },
            "tasks": {
                task_id: {
                    "type": task.task_type,
                    "status": task.status.value,
                    "assigned_agent": task.assigned_agent,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task_id, task in self.tasks.items()
            },
            "negotiations": {
                session_id: {
                    "topic": session.topic,
                    "participants": session.participants,
                    "status": session.status.value,
                    "final_agreement": session.final_agreement
                }
                for session_id, session in self.negotiations.items()
            },
            "collaboration_log": self.collaboration_log
        }