import asyncio
import logging
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from core.base_agent import BaseAgent, MessageType, AgentStatus

class AgentManager:
    """
    Centralized API layer for FreelanceX.AI agent communication and coordination
    Implements cross-agent negotiation protocols and unified task management
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_history: List[Dict[str, Any]] = []
        self.negotiation_sessions: Dict[str, Dict[str, Any]] = {}
        self.task_queue = asyncio.Queue()
        self.logger = logging.getLogger("FreelanceX.AgentManager")
        
        # Performance monitoring
        self.system_metrics = {
            "total_messages": 0,
            "successful_negotiations": 0,
            "failed_negotiations": 0,
            "active_agents": 0,
            "system_uptime": datetime.now()
        }
        
        self.logger.info("FreelanceX.AI Agent Manager initialized")

    def register_agent(self, agent: BaseAgent) -> bool:
        """Register an agent with the manager"""
        try:
            if agent.agent_name in self.agents:
                self.logger.warning(f"Agent {agent.agent_name} already registered")
                return False
                
            self.agents[agent.agent_name] = agent
            agent.agent_registry = self  # Set reference for communication
            self.system_metrics["active_agents"] += 1
            
            self.logger.info(f"Agent {agent.agent_name} registered successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_name}: {str(e)}")
            return False

    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent from the manager"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.system_metrics["active_agents"] -= 1
            self.logger.info(f"Agent {agent_name} unregistered")
            return True
        return False

    async def route_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Route message between agents through centralized API"""
        try:
            target_agent = message.get("to")
            source_agent = message.get("from")
            
            if target_agent not in self.agents:
                self.logger.error(f"Target agent {target_agent} not found")
                return {"status": "error", "reason": "Agent not found"}
                
            # Log message for transparency
            self.message_history.append({
                **message,
                "processed_at": datetime.now().isoformat()
            })
            self.system_metrics["total_messages"] += 1
            
            # Route message to target agent
            target = self.agents[target_agent]
            await target.message_queue.put(message)
            
            self.logger.info(f"Message routed from {source_agent} to {target_agent}")
            return {"status": "delivered", "timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            self.logger.error(f"Failed to route message: {str(e)}")
            return {"status": "error", "reason": str(e)}

    async def initiate_negotiation(self, agent_a: str, agent_b: str, context: Dict[str, Any]) -> str:
        """Initiate negotiation session between two agents"""
        negotiation_id = f"neg_{agent_a}_{agent_b}_{datetime.now().timestamp()}"
        
        if agent_a not in self.agents or agent_b not in self.agents:
            self.logger.error(f"One or both agents not found: {agent_a}, {agent_b}")
            return ""
            
        negotiation_session = {
            "id": negotiation_id,
            "participants": [agent_a, agent_b],
            "context": context,
            "status": "active",
            "rounds": [],
            "start_time": datetime.now().isoformat(),
            "resolution": None
        }
        
        self.negotiation_sessions[negotiation_id] = negotiation_session
        
        # Notify both agents about negotiation
        negotiation_message = {
            "type": MessageType.NEGOTIATION.value,
            "negotiation_id": negotiation_id,
            "context": context,
            "other_party": agent_b if agent_a else agent_a
        }
        
        await self.route_message({
            "from": "AgentManager",
            "to": agent_a,
            "type": MessageType.NEGOTIATION.value,
            "data": negotiation_message
        })
        
        await self.route_message({
            "from": "AgentManager", 
            "to": agent_b,
            "type": MessageType.NEGOTIATION.value,
            "data": negotiation_message
        })
        
        self.logger.info(f"Negotiation {negotiation_id} initiated between {agent_a} and {agent_b}")
        return negotiation_id

    async def resolve_conflict(self, agent_a: str, agent_b: str, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve conflicts between agents using negotiation protocols"""
        try:
            # Get agent preferences and constraints
            agent_a_obj = self.agents.get(agent_a)
            agent_b_obj = self.agents.get(agent_b)
            
            if not agent_a_obj or not agent_b_obj:
                return {"status": "error", "reason": "Agent not found"}
                
            # Simple conflict resolution algorithm
            # In practice, this would be more sophisticated
            resolution = {
                "status": "resolved",
                "solution": "compromise",
                "agent_a_concessions": conflict_data.get("agent_a_demands", []),
                "agent_b_concessions": conflict_data.get("agent_b_demands", []),
                "final_agreement": self._generate_compromise(conflict_data),
                "timestamp": datetime.now().isoformat()
            }
            
            # Notify agents of resolution
            await self.broadcast_to_agents([agent_a, agent_b], {
                "type": "conflict_resolution",
                "resolution": resolution
            })
            
            self.system_metrics["successful_negotiations"] += 1
            return resolution
            
        except Exception as e:
            self.logger.error(f"Failed to resolve conflict: {str(e)}")
            self.system_metrics["failed_negotiations"] += 1
            return {"status": "error", "reason": str(e)}

    def _generate_compromise(self, conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate compromise solution for conflict resolution"""
        # Simple compromise algorithm - split the difference
        return {
            "priority_adjustment": "balanced",
            "resource_allocation": "equal_split",
            "execution_order": "parallel_where_possible"
        }

    async def broadcast_to_agents(self, agent_names: List[str], message: Dict[str, Any]):
        """Broadcast message to multiple agents"""
        for agent_name in agent_names:
            if agent_name in self.agents:
                broadcast_message = {
                    "from": "AgentManager",
                    "to": agent_name,
                    "type": MessageType.BROADCAST.value,
                    "data": message,
                    "timestamp": datetime.now().isoformat()
                }
                await self.route_message(broadcast_message)

    async def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Intelligently distribute task to most suitable agent"""
        try:
            task_type = task.get("type", "general")
            required_skills = task.get("required_skills", [])
            priority = task.get("priority", "medium")
            
            # Find best agent for the task
            best_agent = self._select_best_agent(task_type, required_skills)
            
            if not best_agent:
                return {"status": "error", "reason": "No suitable agent found"}
                
            # Check if agent is available
            agent = self.agents[best_agent]
            if agent.status == AgentStatus.BUSY:
                # Try to negotiate with agent or find alternative
                alternative = self._find_alternative_agent(task_type, [best_agent])
                if alternative:
                    best_agent = alternative
                else:
                    # Queue task for later
                    await self.task_queue.put({**task, "assigned_agent": best_agent})
                    return {"status": "queued", "assigned_agent": best_agent}
            
            # Assign task to agent
            result = await agent.execute_task(task)
            
            self.logger.info(f"Task {task.get('id', 'unknown')} assigned to {best_agent}")
            return {"status": "assigned", "agent": best_agent, "result": result}
            
        except Exception as e:
            self.logger.error(f"Failed to distribute task: {str(e)}")
            return {"status": "error", "reason": str(e)}

    def _select_best_agent(self, task_type: str, required_skills: List[str]) -> Optional[str]:
        """Select the best agent for a given task"""
        best_agent = None
        best_score = 0
        
        for agent_name, agent in self.agents.items():
            score = 0
            
            # Agent type matching
            if agent.agent_type.lower() in task_type.lower():
                score += 50
                
            # Performance metrics
            score += agent.performance_metrics["success_rate"] * 30
            score += (5 - agent.performance_metrics["avg_response_time"]) * 10
            score += agent.performance_metrics["user_satisfaction"] * 10
            
            # Availability
            if agent.status == AgentStatus.IDLE:
                score += 20
            elif agent.status == AgentStatus.BUSY:
                score -= 30
                
            if score > best_score:
                best_score = score
                best_agent = agent_name
                
        return best_agent

    def _find_alternative_agent(self, task_type: str, exclude_agents: List[str]) -> Optional[str]:
        """Find alternative agent excluding specified agents"""
        for agent_name, agent in self.agents.items():
            if agent_name not in exclude_agents and agent.status == AgentStatus.IDLE:
                if agent.agent_type.lower() in task_type.lower():
                    return agent_name
        return None

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agent_statuses = {
            name: agent.get_agent_info() 
            for name, agent in self.agents.items()
        }
        
        return {
            "system_metrics": self.system_metrics,
            "agent_statuses": agent_statuses,
            "active_negotiations": len(self.negotiation_sessions),
            "message_history_size": len(self.message_history),
            "queued_tasks": self.task_queue.qsize()
        }

    async def shutdown(self):
        """Gracefully shutdown the agent manager"""
        self.logger.info("Shutting down FreelanceX.AI Agent Manager")
        
        # Notify all agents of shutdown
        await self.broadcast_to_agents(
            list(self.agents.keys()),
            {"type": "system_shutdown", "timestamp": datetime.now().isoformat()}
        )
        
        # Clear all data
        self.agents.clear()
        self.message_history.clear()
        self.negotiation_sessions.clear()
        
        self.logger.info("Agent Manager shutdown complete")
