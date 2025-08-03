#!/usr/bin/env python3
"""
FreelanceX.AI - Agent Coordination System
Manages inter-agent communication, task routing, and collaboration protocols.
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid
from concurrent.futures import ThreadPoolExecutor
import queue

# Import FreelanceX.AI components
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent, AgentStatus
from backend.memory_layer import MemoryLayer, InteractionRecord

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class CoordinationProtocol(Enum):
    """Inter-agent coordination protocols"""
    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"      # Agents work simultaneously
    PIPELINE = "pipeline"      # Agents work in a chain
    NEGOTIATION = "negotiation"  # Agents negotiate for resources
    CONSENSUS = "consensus"    # Agents reach consensus

@dataclass
class Task:
    """Represents a task to be executed by agents"""
    task_id: str
    user_id: str
    task_type: str
    description: str
    priority: TaskPriority
    required_agents: List[str]
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

@dataclass
class AgentCapability:
    """Represents an agent's capabilities"""
    agent_name: str
    capabilities: List[str]
    performance_metrics: Dict[str, float]
    availability: bool
    current_load: int
    max_concurrent_tasks: int
    specializations: List[str] = field(default_factory=list)

@dataclass
class NegotiationRequest:
    """Represents a negotiation request between agents"""
    negotiation_id: str
    initiator_agent: str
    target_agents: List[str]
    request_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    responses: Dict[str, Any] = field(default_factory=dict)

class TaskRouter:
    """Routes tasks to appropriate agents based on capabilities and availability"""
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.logger = logging.getLogger("FreelanceX.Coordinator.Router")
        
        # Task routing rules
        self.routing_rules = {
            "job_search": ["job_search_agent"],
            "web_research": ["web_search_agent"],
            "math_calculation": ["math_agent"],
            "proposal_writing": ["proposal_writer_agent"],
            "market_analysis": ["web_search_agent", "math_agent"],
            "comprehensive_research": ["web_search_agent", "job_search_agent", "math_agent"],
            "user_profile_analysis": ["user_clone_agent"],
            "wellness_check": ["wellness_monitor_agent"],
            "feedback_analysis": ["feedback_loop_agent"]
        }
    
    async def route_task(self, task: Task) -> List[str]:
        """Route task to appropriate agents"""
        try:
            # Get required agents from routing rules
            required_agents = self.routing_rules.get(task.task_type, [])
            
            if not required_agents:
                self.logger.warning(f"No routing rule found for task type: {task.task_type}")
                return []
            
            # Filter available agents
            available_agents = []
            for agent_name in required_agents:
                agent = self.agent_manager.get_agent(agent_name)
                if agent and agent.status == AgentStatus.ACTIVE:
                    available_agents.append(agent_name)
            
            if not available_agents:
                self.logger.error(f"No available agents for task type: {task.task_type}")
                return []
            
            return available_agents
            
        except Exception as e:
            self.logger.error(f"Error routing task: {str(e)}")
            return []

class NegotiationManager:
    """Manages negotiations between agents"""
    
    def __init__(self):
        self.logger = logging.getLogger("FreelanceX.Coordinator.Negotiation")
        self.active_negotiations: Dict[str, NegotiationRequest] = {}
        self.negotiation_timeout = 30  # seconds
    
    async def initiate_negotiation(self, 
                                 initiator_agent: str,
                                 target_agents: List[str],
                                 request_type: str,
                                 parameters: Dict[str, Any],
                                 priority: TaskPriority) -> str:
        """Initiate a negotiation between agents"""
        try:
            negotiation_id = str(uuid.uuid4())
            
            negotiation = NegotiationRequest(
                negotiation_id=negotiation_id,
                initiator_agent=initiator_agent,
                target_agents=target_agents,
                request_type=request_type,
                parameters=parameters,
                priority=priority
            )
            
            self.active_negotiations[negotiation_id] = negotiation
            
            # Notify target agents
            await self._notify_target_agents(negotiation)
            
            # Set timeout
            asyncio.create_task(self._handle_negotiation_timeout(negotiation_id))
            
            self.logger.info(f"Negotiation initiated: {negotiation_id}")
            return negotiation_id
            
        except Exception as e:
            self.logger.error(f"Error initiating negotiation: {str(e)}")
            return ""
    
    async def respond_to_negotiation(self, 
                                   negotiation_id: str,
                                   responding_agent: str,
                                   response: Dict[str, Any]) -> bool:
        """Respond to a negotiation request"""
        try:
            if negotiation_id not in self.active_negotiations:
                return False
            
            negotiation = self.active_negotiations[negotiation_id]
            negotiation.responses[responding_agent] = response
            
            # Check if all agents have responded
            if len(negotiation.responses) == len(negotiation.target_agents):
                await self._finalize_negotiation(negotiation_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error responding to negotiation: {str(e)}")
            return False
    
    async def _notify_target_agents(self, negotiation: NegotiationRequest):
        """Notify target agents about the negotiation"""
        # This would typically send messages to the agents
        # For now, we'll just log the notification
        for agent_name in negotiation.target_agents:
            self.logger.info(f"Notifying agent {agent_name} about negotiation {negotiation.negotiation_id}")
    
    async def _finalize_negotiation(self, negotiation_id: str):
        """Finalize a negotiation with all responses"""
        try:
            negotiation = self.active_negotiations[negotiation_id]
            
            # Analyze responses and make decision
            decision = await self._analyze_responses(negotiation)
            
            # Notify all agents of the decision
            await self._notify_negotiation_decision(negotiation, decision)
            
            # Remove from active negotiations
            del self.active_negotiations[negotiation_id]
            
            self.logger.info(f"Negotiation {negotiation_id} finalized with decision: {decision}")
            
        except Exception as e:
            self.logger.error(f"Error finalizing negotiation: {str(e)}")
    
    async def _analyze_responses(self, negotiation: NegotiationRequest) -> Dict[str, Any]:
        """Analyze negotiation responses and make decision"""
        # Simple decision logic - can be enhanced with more sophisticated algorithms
        if len(negotiation.responses) == 0:
            return {"decision": "rejected", "reason": "no responses"}
        
        # Count acceptances
        acceptances = sum(1 for response in negotiation.responses.values() 
                         if response.get("decision") == "accept")
        
        if acceptances >= len(negotiation.target_agents) * 0.5:  # Majority rule
            return {"decision": "accepted", "responses": negotiation.responses}
        else:
            return {"decision": "rejected", "responses": negotiation.responses}
    
    async def _notify_negotiation_decision(self, negotiation: NegotiationRequest, decision: Dict[str, Any]):
        """Notify all agents of the negotiation decision"""
        # This would typically send messages to all involved agents
        self.logger.info(f"Negotiation decision for {negotiation.negotiation_id}: {decision}")
    
    async def _handle_negotiation_timeout(self, negotiation_id: str):
        """Handle negotiation timeout"""
        await asyncio.sleep(self.negotiation_timeout)
        
        if negotiation_id in self.active_negotiations:
            negotiation = self.active_negotiations[negotiation_id]
            negotiation.status = "timeout"
            
            # Finalize with timeout decision
            await self._finalize_negotiation(negotiation_id)

class AgentCoordinator:
    """Main agent coordination system"""
    
    def __init__(self, 
                 agent_manager: AgentManager,
                 memory_layer: MemoryLayer,
                 max_concurrent_tasks: int = 10):
        
        self.agent_manager = agent_manager
        self.memory_layer = memory_layer
        self.max_concurrent_tasks = max_concurrent_tasks
        self.logger = logging.getLogger("FreelanceX.Coordinator")
        
        # Initialize components
        self.task_router = TaskRouter(agent_manager)
        self.negotiation_manager = NegotiationManager()
        
        # Task management
        self.active_tasks: Dict[str, Task] = {}
        self.task_queue = asyncio.Queue()
        self.completed_tasks: Dict[str, Task] = {}
        
        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, float]] = {}
        self.coordination_metrics = {
            "tasks_processed": 0,
            "successful_coordinations": 0,
            "failed_coordinations": 0,
            "average_task_duration": 0.0
        }
        
        # Start coordination loop
        self.coordination_task = None
        self.is_running = False
    
    async def start(self):
        """Start the agent coordination system"""
        self.is_running = True
        self.coordination_task = asyncio.create_task(self._coordination_loop())
        self.logger.info("Agent coordination system started")
    
    async def stop(self):
        """Stop the agent coordination system"""
        self.is_running = False
        if self.coordination_task:
            self.coordination_task.cancel()
            try:
                await self.coordination_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Agent coordination system stopped")
    
    async def submit_task(self, task: Task) -> str:
        """Submit a task for coordination"""
        try:
            # Validate task
            if not task.task_id or not task.user_id or not task.task_type:
                raise ValueError("Invalid task: missing required fields")
            
            # Add to queue
            await self.task_queue.put(task)
            
            self.logger.info(f"Task submitted: {task.task_id} ({task.task_type})")
            return task.task_id
            
        except Exception as e:
            self.logger.error(f"Error submitting task: {str(e)}")
            return ""
    
    async def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get the status of a task"""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        
        return None
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        try:
            if task_id in self.active_tasks:
                task = self.active_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                
                # Notify assigned agents
                await self._notify_agents_of_cancellation(task)
                
                # Move to completed tasks
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
                
                self.logger.info(f"Task cancelled: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling task: {str(e)}")
            return False
    
    async def _coordination_loop(self):
        """Main coordination loop"""
        while self.is_running:
            try:
                # Process tasks from queue
                if not self.task_queue.empty() and len(self.active_tasks) < self.max_concurrent_tasks:
                    task = await self.task_queue.get()
                    await self._process_task(task)
                
                # Monitor active tasks
                await self._monitor_active_tasks()
                
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {str(e)}")
                await asyncio.sleep(1)
    
    async def _process_task(self, task: Task):
        """Process a single task"""
        try:
            self.logger.info(f"Processing task: {task.task_id}")
            
            # Route task to appropriate agents
            assigned_agents = await self.task_router.route_task(task)
            
            if not assigned_agents:
                task.status = TaskStatus.FAILED
                task.error_message = "No available agents for task"
                self.completed_tasks[task.task_id] = task
                return
            
            # Assign agents to task
            task.assigned_agents = assigned_agents
            task.status = TaskStatus.IN_PROGRESS
            
            # Add to active tasks
            self.active_tasks[task.task_id] = task
            
            # Execute task based on coordination protocol
            await self._execute_task(task)
            
        except Exception as e:
            self.logger.error(f"Error processing task {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.completed_tasks[task.task_id] = task
    
    async def _execute_task(self, task: Task):
        """Execute a task with the assigned agents"""
        try:
            start_time = time.time()
            
            # Determine coordination protocol based on task type
            protocol = self._determine_coordination_protocol(task)
            
            if protocol == CoordinationProtocol.SEQUENTIAL:
                result = await self._execute_sequential(task)
            elif protocol == CoordinationProtocol.PARALLEL:
                result = await self._execute_parallel(task)
            elif protocol == CoordinationProtocol.PIPELINE:
                result = await self._execute_pipeline(task)
            else:
                result = await self._execute_parallel(task)  # Default to parallel
            
            # Store results
            task.results = result
            task.status = TaskStatus.COMPLETED
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Store interaction record
            await self._store_interaction_record(task, duration)
            
            # Move to completed tasks
            self.completed_tasks[task.task_id] = task
            del self.active_tasks[task.task_id]
            
            self.logger.info(f"Task completed: {task.task_id} in {duration:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.completed_tasks[task.task_id] = task
            del self.active_tasks[task.task_id]
    
    def _determine_coordination_protocol(self, task: Task) -> CoordinationProtocol:
        """Determine the coordination protocol for a task"""
        if len(task.assigned_agents) == 1:
            return CoordinationProtocol.SEQUENTIAL
        
        # Multi-agent tasks
        if task.task_type in ["market_analysis", "comprehensive_research"]:
            return CoordinationProtocol.PARALLEL
        elif task.task_type in ["proposal_writing"]:
            return CoordinationProtocol.PIPELINE
        else:
            return CoordinationProtocol.PARALLEL
    
    async def _execute_sequential(self, task: Task) -> Dict[str, Any]:
        """Execute task sequentially with agents"""
        results = {}
        
        for agent_name in task.assigned_agents:
            agent = self.agent_manager.get_agent(agent_name)
            if agent:
                try:
                    result = await agent.process_request(task.parameters)
                    results[agent_name] = result
                except Exception as e:
                    self.logger.error(f"Error with agent {agent_name}: {str(e)}")
                    results[agent_name] = {"error": str(e)}
        
        return results
    
    async def _execute_parallel(self, task: Task) -> Dict[str, Any]:
        """Execute task in parallel with agents"""
        async def execute_agent(agent_name: str):
            agent = self.agent_manager.get_agent(agent_name)
            if agent:
                try:
                    result = await agent.process_request(task.parameters)
                    return agent_name, result
                except Exception as e:
                    self.logger.error(f"Error with agent {agent_name}: {str(e)}")
                    return agent_name, {"error": str(e)}
            return agent_name, {"error": "Agent not found"}
        
        # Execute all agents in parallel
        tasks = [execute_agent(agent_name) for agent_name in task.assigned_agents]
        results_list = await asyncio.gather(*tasks)
        
        # Convert to dictionary
        results = {agent_name: result for agent_name, result in results_list}
        return results
    
    async def _execute_pipeline(self, task: Task) -> Dict[str, Any]:
        """Execute task in pipeline with agents"""
        results = {}
        current_data = task.parameters
        
        for agent_name in task.assigned_agents:
            agent = self.agent_manager.get_agent(agent_name)
            if agent:
                try:
                    # Pass current data to agent
                    agent_params = {**current_data, "pipeline_data": results}
                    result = await agent.process_request(agent_params)
                    results[agent_name] = result
                    
                    # Update current data for next agent
                    if isinstance(result, dict) and "output" in result:
                        current_data = result["output"]
                    
                except Exception as e:
                    self.logger.error(f"Error with agent {agent_name}: {str(e)}")
                    results[agent_name] = {"error": str(e)}
        
        return results
    
    async def _monitor_active_tasks(self):
        """Monitor active tasks for timeouts and issues"""
        current_time = datetime.now()
        
        for task_id, task in list(self.active_tasks.items()):
            # Check for deadline
            if task.deadline and current_time > task.deadline:
                self.logger.warning(f"Task {task_id} exceeded deadline")
                task.status = TaskStatus.FAILED
                task.error_message = "Task exceeded deadline"
                self.completed_tasks[task_id] = task
                del self.active_tasks[task_id]
    
    async def _notify_agents_of_cancellation(self, task: Task):
        """Notify agents that a task has been cancelled"""
        for agent_name in task.assigned_agents:
            agent = self.agent_manager.get_agent(agent_name)
            if agent:
                # This would typically send a cancellation message to the agent
                self.logger.info(f"Notified agent {agent_name} of task cancellation: {task.task_id}")
    
    async def _store_interaction_record(self, task: Task, duration: float):
        """Store interaction record in memory layer"""
        try:
            interaction = InteractionRecord(
                interaction_id=str(uuid.uuid4()),
                user_id=task.user_id,
                agent_name=",".join(task.assigned_agents),
                request_type=task.task_type,
                request_content=task.parameters,
                response_content=task.results,
                timestamp=datetime.now(),
                duration_ms=int(duration * 1000),
                success=task.status == TaskStatus.COMPLETED,
                tags=[task.task_type] + task.assigned_agents
            )
            
            await self.memory_layer.store_interaction(interaction)
            
        except Exception as e:
            self.logger.error(f"Error storing interaction record: {str(e)}")
    
    async def _update_performance_metrics(self):
        """Update coordination performance metrics"""
        try:
            total_tasks = len(self.completed_tasks)
            if total_tasks > 0:
                successful_tasks = sum(1 for task in self.completed_tasks.values() 
                                     if task.status == TaskStatus.COMPLETED)
                
                self.coordination_metrics["tasks_processed"] = total_tasks
                self.coordination_metrics["successful_coordinations"] = successful_tasks
                self.coordination_metrics["failed_coordinations"] = total_tasks - successful_tasks
                
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {str(e)}")
    
    async def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get current coordination metrics"""
        return {
            **self.coordination_metrics,
            "active_tasks": len(self.active_tasks),
            "queued_tasks": self.task_queue.qsize(),
            "completed_tasks": len(self.completed_tasks)
        }

if __name__ == "__main__":
    import asyncio
    
    async def test_coordinator():
        """Test the agent coordinator"""
        # This would require actual agent manager and memory layer instances
        # For now, we'll just create a basic test structure
        print("Agent Coordinator test - requires AgentManager and MemoryLayer instances")
    
    asyncio.run(test_coordinator())