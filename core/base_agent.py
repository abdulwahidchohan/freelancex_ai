import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum

from openai import OpenAI
from pydantic import BaseModel

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    NEGOTIATING = "negotiating"

class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NEGOTIATION = "negotiation"
    BROADCAST = "broadcast"

class BaseAgent(ABC):
    def __init__(self, agent_name: str, agent_type: str):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.status = AgentStatus.IDLE
        self.system_prompt = self._load_system_prompt()
        self.logger = logging.getLogger(f"FreelanceX.{agent_name}")
        
        # Initialize OpenAI Agent SDK
        self._init_openai_agent()
        
        # Core FreelanceX.AI attributes
        self.ethical_guidelines = self._load_ethical_guidelines()
        self.memory_store = {}
        self.negotiation_history = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "user_satisfaction": 0.0
        }
        
        # Cross-agent communication
        self.message_queue = asyncio.Queue()
        self.agent_registry = None  # Will be set by AgentManager
        
        # Session management for OpenAI Agent SDK
        self.sessions: Dict[str, Session] = {}
        
        self.logger.info(f"FreelanceX.AI Agent '{agent_name}' initialized with OpenAI Agent SDK")

    def _init_openai_agent(self):
        """Initialize OpenAI Agent SDK agent"""
        try:
            import os
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.logger.warning("OPENAI_API_KEY not set, using fallback mode")
                self.openai_agent = None
                return
                
            self.openai_agent = Agent(
                name=f"FreelanceX {self.agent_name}",
                instructions=self.system_prompt,
                model="gpt-4o-mini",
                tools=self._get_agent_tools()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI Agent SDK: {str(e)}")
            self.openai_agent = None
    
    def _load_system_prompt(self) -> str:
        """Load system prompt with FreelanceX.AI context"""
        try:
            with open('config/system_prompt.json', 'r') as f:
                config = json.load(f)
                base_prompt = config.get('SYSTEM_PROMPT', '')
                
            # Add FreelanceX.AI specific context
            freelancex_context = f"""
            You are the {self.agent_name} agent in FreelanceX.AI, empowering freelancers with cutting-edge AI tools.
            Mission: Enhance productivity, decision-making, and market adaptability.
            Values: Innovation, autonomy, collaboration, growth, and impact.
            
            Always prioritize user privacy, ethical AI usage, and bias mitigation.
            Collaborate with other agents through the centralized API layer.
            """
            
            return f"{base_prompt}\n\n{freelancex_context}"
            
        except FileNotFoundError:
            self.logger.error("system_prompt.json not found in config directory")
            return f"You are the {self.agent_name} agent in FreelanceX.AI."
        except json.JSONDecodeError:
            self.logger.error("Could not decode system_prompt.json. Check JSON format")
            return f"You are the {self.agent_name} agent in FreelanceX.AI."

    def _get_agent_tools(self) -> List:
        """Get tools for this agent - to be overridden by subclasses"""
        return []
    
    def _load_ethical_guidelines(self) -> Dict[str, Any]:
        """Load FreelanceX.AI ethical guidelines"""
        return {
            "transparency": True,
            "fairness": True,
            "privacy_protection": True,
            "bias_mitigation": True,
            "user_consent_required": True,
            "data_encryption": True,
            "anonymization": True
        }
    
    def get_or_create_session(self, user_id: str) -> Optional[Session]:
        """Get or create a session for a user"""
        if not self.openai_agent:
            return None
            
        if user_id not in self.sessions:
            self.sessions[user_id] = Session(agent=self.openai_agent)
            self.logger.info(f"Created new session for user: {user_id}")
        return self.sessions[user_id]

    async def send_message(self, target_agent: str, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to another agent through centralized API"""
        if not self.agent_registry:
            self.logger.error("Agent registry not available for communication")
            return None
            
        message_payload = {
            "from": self.agent_name,
            "to": target_agent,
            "type": MessageType.REQUEST.value,
            "timestamp": datetime.now().isoformat(),
            "data": message
        }
        
        try:
            response = await self.agent_registry.route_message(message_payload)
            self.logger.info(f"Message sent to {target_agent}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to send message to {target_agent}: {str(e)}")
            return None

    async def negotiate_with_agent(self, target_agent: str, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate negotiation with another agent"""
        self.status = AgentStatus.NEGOTIATING
        
        negotiation_request = {
            "type": "negotiation",
            "proposal": proposal,
            "negotiation_id": f"{self.agent_name}_{target_agent}_{datetime.now().timestamp()}"
        }
        
        response = await self.send_message(target_agent, negotiation_request)
        
        # Store negotiation history for transparency
        self.negotiation_history.append({
            "timestamp": datetime.now().isoformat(),
            "target_agent": target_agent,
            "proposal": proposal,
            "response": response
        })
        
        self.status = AgentStatus.IDLE
        return response or {"status": "failed", "reason": "Communication error"}

    def update_performance_metrics(self, task_success: bool, response_time: float, user_rating: Optional[float] = None):
        """Update agent performance metrics"""
        self.performance_metrics["tasks_completed"] += 1
        
        # Update success rate
        total_tasks = self.performance_metrics["tasks_completed"]
        current_successes = self.performance_metrics["success_rate"] * (total_tasks - 1)
        if task_success:
            current_successes += 1
        self.performance_metrics["success_rate"] = current_successes / total_tasks
        
        # Update average response time
        current_avg = self.performance_metrics["avg_response_time"]
        self.performance_metrics["avg_response_time"] = (
            (current_avg * (total_tasks - 1) + response_time) / total_tasks
        )
        
        # Update user satisfaction if provided
        if user_rating is not None:
            current_satisfaction = self.performance_metrics["user_satisfaction"]
            self.performance_metrics["user_satisfaction"] = (
                (current_satisfaction * (total_tasks - 1) + user_rating) / total_tasks
            )

    def store_memory(self, key: str, value: Any, user_consent: bool = True):
        """Store information in agent memory with privacy controls"""
        if not user_consent:
            self.logger.warning("Memory storage declined due to lack of user consent")
            return
            
        if self.ethical_guidelines["privacy_protection"]:
            # In real implementation, this would include encryption
            self.memory_store[key] = {
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "encrypted": True
            }
        else:
            self.memory_store[key] = value

    def retrieve_memory(self, key: str) -> Any:
        """Retrieve information from agent memory"""
        if key in self.memory_store:
            memory_item = self.memory_store[key]
            if isinstance(memory_item, dict) and "value" in memory_item:
                return memory_item["value"]
            return memory_item
        return None

    def clear_memory(self, user_request: bool = False):
        """Clear agent memory (user-controlled)"""
        if user_request:
            self.memory_store.clear()
            self.logger.info("Agent memory cleared by user request")
        else:
            self.logger.warning("Memory clear attempted without user authorization")

    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific task - must be implemented by subclasses"""
        pass

    @abstractmethod
    async def self_diagnose(self) -> Dict[str, Any]:
        """Perform self-diagnosis for self-repair capability"""
        pass

    def get_agent_info(self) -> Dict[str, Any]:
        """Return comprehensive agent information"""
        return {
            "name": self.agent_name,
            "type": self.agent_type,
            "status": self.status.value,
            "performance_metrics": self.performance_metrics,
            "ethical_guidelines": self.ethical_guidelines,
            "memory_items": len(self.memory_store),
            "negotiations_count": len(self.negotiation_history)
        }

    async def run(self):
        """Main agent execution loop"""
        self.logger.info(f"Agent {self.agent_name} starting execution loop")
        while True:
            try:
                # Process incoming messages
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._process_message(message)
                
                # Perform self-diagnosis periodically
                if self.performance_metrics["tasks_completed"] % 10 == 0:
                    diagnosis = await self.self_diagnose()
                    if diagnosis.get("needs_repair", False):
                        await self._initiate_self_repair(diagnosis)
                
                await asyncio.sleep(1)  # Prevent busy waiting
                
            except Exception as e:
                self.logger.error(f"Error in agent execution loop: {str(e)}")
                self.status = AgentStatus.ERROR
                await asyncio.sleep(5)  # Wait before retrying

    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        message_type = message.get("type")
        
        if message_type == MessageType.NEGOTIATION.value:
            await self._handle_negotiation(message)
        elif message_type == MessageType.REQUEST.value:
            await self._handle_request(message)
        else:
            self.logger.warning(f"Unknown message type: {message_type}")

    async def _handle_negotiation(self, message: Dict[str, Any]):
        """Handle negotiation message from another agent"""
        # This would contain the negotiation logic
        # For now, return a simple acceptance
        response = {
            "status": "accepted",
            "counter_proposal": None,
            "agent": self.agent_name
        }
        
        # Send response back
        sender = message.get("from")
        if sender:
            await self.send_message(sender, response)

    async def _handle_request(self, message: Dict[str, Any]):
        """Handle regular request from another agent"""
        task = message.get("data", {})
        result = await self.execute_task(task)
        
        # Send response back
        sender = message.get("from")
        if sender:
            await self.send_message(sender, result)

    async def _initiate_self_repair(self, diagnosis: Dict[str, Any]):
        """Initiate self-repair based on diagnosis"""
        self.logger.info(f"Initiating self-repair: {diagnosis}")
        # Self-repair logic would go here
        # For now, just reset status
        self.status = AgentStatus.IDLE