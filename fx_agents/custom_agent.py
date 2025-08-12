"""Enhanced Dynamic Agent System - OpenAI Agents SDK Integration
Provides dynamic agent creation and management with full SDK integration
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool as tool, Session, handoff
from memory.sqlite_memory import get_memory, create_enhanced_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import set_trace_metadata, use a dummy function if not available
try:
    from agents import set_trace_metadata
except ImportError:
    def set_trace_metadata(metadata: Dict[str, Any]) -> None:
        """Dummy function for trace metadata when not available"""
        logger.info(f"Trace metadata (not available): {metadata}")
        pass

class AgentConfig(BaseModel):
    """Enhanced agent configuration with SDK features"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    instructions: str = Field(..., description="Agent instructions")
    model: str = Field(default="gpt-4", description="Model to use")
    temperature: float = Field(default=0.7, description="Temperature setting")
    max_tokens: Optional[int] = Field(default=None, description="Maximum tokens")
    tools: List[Any] = Field(default_factory=list, description="Agent tools")
    handoffs: List[Any] = Field(default_factory=list, description="Handoff agents")
    guardrails: Optional[Dict[str, Any]] = Field(default=None, description="Guardrails configuration")
    enable_tracing: bool = Field(default=True, description="Enable tracing")
    enable_fallback: bool = Field(default=True, description="Enable fallback")
    session_config: Optional[Dict[str, Any]] = Field(default=None, description="Session configuration")
    
    class Config:
        arbitrary_types_allowed = True

class AgentResponse(BaseModel):
    """Enhanced agent response with SDK features"""
    success: bool = Field(..., description="Success status")
    content: str = Field(..., description="Response content")
    agent_name: str = Field(..., description="Agent name")
    session_id: str = Field(..., description="Session identifier")
    execution_time: float = Field(..., description="Execution time")
    tool_calls: int = Field(default=0, description="Number of tool calls")
    handoffs: int = Field(default=0, description="Number of handoffs")
    trace_id: Optional[str] = Field(default=None, description="Trace identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class DynamicAgent:
    """Enhanced dynamic agent with full SDK integration"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent = None
        self.session = None
        self.memory = get_memory()
        self._create_agent()
    
    def _create_agent(self):
        """Create agent with SDK integration"""
        try:
            # Create agent with SDK features
            self.agent = Agent(
                name=self.config.name,
                instructions=self.config.instructions,
                tools=self.config.tools
            )
            
            logger.info(f"Created enhanced agent: {self.config.name}")
            
        except Exception as e:
            logger.error(f"Failed to create agent {self.config.name}: {str(e)}")
            raise
    
    async def run(self, message: str, session_id: str, user_id: Optional[str] = None,
                 trace_metadata: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Run agent with enhanced SDK features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Set trace metadata for SDK integration
            if trace_metadata and self.config.enable_tracing:
                set_trace_metadata(trace_metadata)
            
            # Create enhanced session with memory integration
            self.session = await create_enhanced_session(
                session_id=session_id,
                agent=self.agent,
                user_id=user_id,
                trace_metadata=trace_metadata
            )
            
            # Add user message to memory
            await self.memory.add_memory_entry(
                session_id=session_id,
                message_type="user",
                content=message,
                user_id=user_id,
                metadata={"agent_name": self.config.name, "trace_metadata": trace_metadata}
            )
            
            # Create runner with enhanced session
            runner = Runner(self.session)
            
            # Execute with SDK features
            result = await runner.run(message)
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Extract SDK-specific information
            tool_calls = len(result.tool_calls) if hasattr(result, 'tool_calls') else 0
            handoffs = len(result.handoffs) if hasattr(result, 'handoffs') else 0
            trace_id = getattr(result, 'trace_id', None)
            
            # Add agent response to memory
            await self.memory.add_memory_entry(
                session_id=session_id,
                message_type="agent",
                content=str(result),
                user_id=user_id,
                agent_name=self.config.name,
                tool_calls=getattr(result, 'tool_calls', []),
                handoffs=getattr(result, 'handoffs', []),
                metadata={
                    "execution_time": execution_time,
                    "tool_calls_count": tool_calls,
                    "handoffs_count": handoffs,
                    "trace_id": trace_id
                }
            )
            
            # Record performance metrics
            await self.memory.record_agent_performance(
                agent_name=self.config.name,
                session_id=session_id,
                execution_time=execution_time,
                success_rate=1.0,
                tool_calls_count=tool_calls,
                handoffs_count=handoffs
            )
            
            # Update session context
            await self.memory.update_session_context(
                session_id=session_id,
                agent_history=[self.config.name],
                system_state={"last_agent": self.config.name, "last_execution_time": execution_time}
            )
            
            return AgentResponse(
                success=True,
                content=str(result),
                agent_name=self.config.name,
                session_id=session_id,
                execution_time=execution_time,
                tool_calls=tool_calls,
                handoffs=handoffs,
                trace_id=trace_id,
                metadata={
                    "model": self.config.model,
                    "temperature": self.config.temperature,
                    "session_config": self.config.session_config
                }
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Agent {self.config.name} execution failed: {str(e)}")
            
            # Record failure in memory
            await self.memory.add_memory_entry(
                session_id=session_id,
                message_type="error",
                content=f"Agent execution failed: {str(e)}",
                user_id=user_id,
                agent_name=self.config.name,
                metadata={"error": str(e), "execution_time": execution_time}
            )
            
            return AgentResponse(
                success=False,
                content=f"Error: {str(e)}",
                agent_name=self.config.name,
                session_id=session_id,
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
    
    def add_tool(self, tool_func):
        """Add tool to agent dynamically"""
        try:
            self.agent.tools.append(tool_func)
            logger.info(f"Added tool to {self.config.name}")
        except Exception as e:
            logger.error(f"Failed to add tool to {self.config.name}: {str(e)}")
    
    def add_handoff(self, target_agent: 'DynamicAgent'):
        """Add handoff to another agent"""
        try:
            # Create handoff using SDK handoff decorator
            @handoff(target_agent.agent)
            def handoff_to_target(message: str):
                return f"Handing off to {target_agent.config.name}: {message}"
            
            self.agent.tools.append(handoff_to_target)
            logger.info(f"Added handoff from {self.config.name} to {target_agent.config.name}")
        except Exception as e:
            logger.error(f"Failed to add handoff: {str(e)}")
    
    def set_guardrails(self, guardrails_config: Dict[str, Any]):
        """Set guardrails for agent"""
        try:
            self.config.guardrails = guardrails_config
            logger.info(f"Set guardrails for {self.config.name}")
        except Exception as e:
            logger.error(f"Failed to set guardrails for {self.config.name}: {str(e)}")

class AgentRegistry:
    """Centralized agent registry with SDK features"""
    
    def __init__(self):
        self.agents: Dict[str, DynamicAgent] = {}
        self.memory = get_memory()
    
    def register(self, agent: DynamicAgent):
        """Register agent in registry"""
        try:
            self.agents[agent.config.name] = agent
            logger.info(f"Registered enhanced agent: {agent.config.name}")
        except Exception as e:
            logger.error(f"Failed to register agent {agent.config.name}: {str(e)}")
    
    def get(self, name: str) -> Optional[DynamicAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def list(self) -> List[str]:
        """List all registered agents"""
        return list(self.agents.keys())
    
    def remove(self, name: str):
        """Remove agent from registry"""
        if name in self.agents:
            del self.agents[name]
            logger.info(f"Removed agent: {name}")
    
    async def get_agent_performance(self, agent_name: str) -> Dict[str, Any]:
        """Get agent performance metrics"""
        try:
            # This would query the memory system for performance data
            return {
                "agent_name": agent_name,
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0
            }
        except Exception as e:
            logger.error(f"Failed to get performance for {agent_name}: {str(e)}")
            return {}

# Global agent registry
_agent_registry = AgentRegistry()

def get_agent_registry() -> AgentRegistry:
    """Get global agent registry"""
    return _agent_registry

def create_dynamic_agent(name: str, description: str, instructions: str, 
                        tools: List[Any] = None, model: str = "gpt-4") -> DynamicAgent:
    """Create dynamic agent with SDK integration"""
    try:
        config = AgentConfig(
            name=name,
            description=description,
            instructions=instructions,
            tools=tools or [],
            model=model
        )
        
        agent = DynamicAgent(config)
        _agent_registry.register(agent)
        return agent
        
    except Exception as e:
        logger.error(f"Failed to create dynamic agent {name}: {str(e)}")
        raise

def create_agent_from_config(config: AgentConfig) -> DynamicAgent:
    """Create agent from configuration"""
    try:
        agent = DynamicAgent(config)
        _agent_registry.register(agent)
        return agent
    except Exception as e:
        logger.error(f"Failed to create agent from config: {str(e)}")
        raise

def create_enhanced_triage_agent() -> DynamicAgent:
    """Create enhanced triage agent with SDK features"""
    try:
        config = AgentConfig(
            name="Enhanced Triage Agent",
            description="Intelligent request routing with SDK handoffs",
            instructions="""
            You are the enhanced FreelanceX.AI Triage Agent with full OpenAI Agents SDK integration.
            
            Your enhanced capabilities include:
            - Dynamic handoffs to specialized agents
            - Guardrails for input validation
            - Tracing for debugging and monitoring
            - Memory integration for context persistence
            - Performance monitoring and metrics
            
            Route user requests to the most appropriate specialized agents based on:
            1. Request type and complexity
            2. User context and preferences
            3. Agent availability and performance
            4. Handoff optimization
            
            Always consider:
            - User experience and response time
            - Agent specialization and expertise
            - System performance and resource usage
            - Error handling and fallback strategies
            """,
            tools=[],
            enable_tracing=True,
            enable_fallback=True,
            guardrails={
                "input_validation": True,
                "content_filtering": True,
                "rate_limiting": True
            }
        )
        
        return create_agent_from_config(config)
        
    except Exception as e:
        logger.error(f"Failed to create enhanced triage agent: {str(e)}")
        raise
