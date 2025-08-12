"""Enhanced Agent Configuration - Latest OpenAI Agent SDK Patterns
Demonstrates best practices for agent configuration and tool integration
"""

from agents import Agent, function_tool as tool
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Enhanced tool configuration with better error handling and validation
class EnhancedToolConfig:
    """Configuration for enhanced tool usage"""
    
    @staticmethod
    def create_tool_with_validation(func, description: str = None, **kwargs):
        """Create a tool with enhanced validation and error handling"""
        return tool(
            func,
            description=description,
            strict_mode=False,  # Allow flexible parameter handling
            **kwargs
        )

# Enhanced agent configuration patterns
class AgentConfig(BaseModel):
    """Configuration for agent behavior"""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    instructions: str = Field(..., description="Agent instructions")
    model: str = Field(default="gpt-4o-mini", description="Model to use")
    temperature: float = Field(default=0.7, description="Creativity level")
    max_tokens: int = Field(default=4000, description="Maximum response length")
    tools_enabled: List[str] = Field(default_factory=list, description="Enabled tools")
    
    class Config:
        extra = "allow"  # Allow additional fields

# Enhanced agent creation with configuration
def create_enhanced_agent(config: AgentConfig, tools: List = None) -> Agent:
    """Create an agent with enhanced configuration"""
    
    # Validate configuration
    if not config.name or not config.description:
        raise ValueError("Agent name and description are required")
    
    # Create agent with enhanced configuration
    agent = Agent(
        name=config.name,
        description=config.description,
        instructions=config.instructions,
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        tools=tools or []
    )
    
    logger.info(f"Created enhanced agent: {config.name}")
    return agent

# Enhanced tool patterns with better error handling
class ToolResult(BaseModel):
    """Standardized tool result format"""
    success: bool = Field(..., description="Whether the tool execution was successful")
    data: Any = Field(default=None, description="Tool execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

def enhanced_tool_execution(func):
    """Decorator for enhanced tool execution with error handling"""
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return ToolResult(
                success=True,
                data=result,
                metadata={"tool": func.__name__}
            )
        except Exception as e:
            logger.error(f"Tool execution failed: {str(e)}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"tool": func.__name__}
            )
    return wrapper

# Example enhanced tool with better patterns
@tool
def enhanced_search_example(query: str, filters: Dict[str, Any] = None) -> ToolResult:
    """Enhanced search tool with better error handling and validation"""
    try:
        # Validate input
        if not query or len(query.strip()) < 2:
            return ToolResult(
                success=False,
                error="Query must be at least 2 characters long"
            )
        
        # Process search
        results = {
            "query": query,
            "filters": filters or {},
            "results": ["Sample result 1", "Sample result 2"]
        }
        
        return ToolResult(
            success=True,
            data=results,
            metadata={"query_length": len(query)}
        )
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return ToolResult(
            success=False,
            error=f"Search execution failed: {str(e)}"
        )

# Enhanced agent session management
class AgentSession:
    """Enhanced session management for agents"""
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.session_id = None
        self.context = {}
        
    async def start_session(self, initial_context: Dict[str, Any] = None):
        """Start a new agent session"""
        from agents import Session
        
        self.context = initial_context or {}
        self.session_id = f"session_{id(self)}"
        
        # Create session with enhanced context
        session = Session(
            agent=self.agent,
            context=self.context
        )
        
        logger.info(f"Started session {self.session_id} for agent {self.agent.name}")
        return session
    
    def update_context(self, key: str, value: Any):
        """Update session context"""
        self.context[key] = value
        logger.debug(f"Updated context for session {self.session_id}: {key}")

# Enhanced agent monitoring and metrics
class AgentMetrics:
    """Enhanced metrics collection for agents"""
    
    def __init__(self):
        self.metrics = {
            "tool_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_response_time": 0.0
        }
    
    def record_tool_execution(self, success: bool, response_time: float):
        """Record tool execution metrics"""
        self.metrics["tool_executions"] += 1
        if success:
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1
            
        # Update average response time
        current_avg = self.metrics["average_response_time"]
        total_executions = self.metrics["tool_executions"]
        self.metrics["average_response_time"] = (
            (current_avg * (total_executions - 1) + response_time) / total_executions
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
