"""Advanced Agent Implementations - OpenAI Agent SDK Advanced Patterns
Implements advanced agent types and patterns from the SDK documentation
"""

import logging
import datetime
import asyncio
import json
from agents import Agent, function_tool as tool, Session, Runner
from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced Pydantic models for advanced functionality
class AgentMetrics(BaseModel):
    """Comprehensive agent performance metrics"""
    total_requests: int = Field(default=0, description="Total number of requests processed")
    successful_requests: int = Field(default=0, description="Number of successful requests")
    failed_requests: int = Field(default=0, description="Number of failed requests")
    average_response_time: float = Field(default=0.0, description="Average response time in seconds")
    last_request_time: Optional[datetime.datetime] = Field(default=None, description="Timestamp of last request")
    success_rate: float = Field(default=1.0, description="Success rate percentage")
    total_execution_time: float = Field(default=0.0, description="Total execution time")

class ExecutionContext(BaseModel):
    """Context for agent execution"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    request_type: str = Field(..., description="Type of request being processed")
    priority: int = Field(default=5, description="Request priority 1-10")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")

class ToolExecutionResult(BaseModel):
    """Result of tool execution"""
    tool_name: str = Field(..., description="Name of the executed tool")
    success: bool = Field(..., description="Whether execution was successful")
    result: Any = Field(..., description="Tool execution result")
    execution_time: float = Field(..., description="Execution time in seconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")

# Advanced agent base class with enhanced functionality
class AdvancedAgent(Agent):
    """Advanced agent with enhanced capabilities and monitoring"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = AgentMetrics()
        self.context_history = []
        self.tool_execution_history = []
        self.performance_monitors = {}
        
    def update_metrics(self, success: bool, response_time: float):
        """Update agent metrics"""
        self.metrics.total_requests += 1
        self.metrics.last_request_time = datetime.datetime.now()
        self.metrics.total_execution_time += response_time
        
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            
        self.metrics.average_response_time = (
            self.metrics.total_execution_time / self.metrics.total_requests
        )
        self.metrics.success_rate = (
            self.metrics.successful_requests / self.metrics.total_requests
        )
    
    async def process_with_metrics(self, message: str, session: Session = None, context: ExecutionContext = None) -> Dict[str, Any]:
        """Process message with enhanced metrics collection"""
        start_time = datetime.datetime.now()
        logger.info(f"Processing request for agent {self.name}: {message[:100]}...")
        
        try:
            # Create session if not provided
            if not session:
                session = Session(agent=self)
            
            # Add context to session if provided
            if context:
                session.context.update(context.dict())
            
            # Process the message
            runner = Runner(session)
            result = await runner.run(message)
            
            # Calculate response time and update metrics
            response_time = (datetime.datetime.now() - start_time).total_seconds()
            self.update_metrics(True, response_time)
            
            # Log successful execution
            logger.info(f"Agent {self.name} processed request successfully in {response_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "response_time": response_time,
                "metrics": self.metrics.dict(),
                "context": context.dict() if context else {}
            }
            
        except Exception as e:
            response_time = (datetime.datetime.now() - start_time).total_seconds()
            self.update_metrics(False, response_time)
            logger.error(f"Agent {self.name} processing failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "metrics": self.metrics.dict(),
                "context": context.dict() if context else {}
            }
    
    def add_tool_execution_record(self, tool_name: str, success: bool, execution_time: float, result: Any = None, error: str = None):
        """Record tool execution for monitoring"""
        record = ToolExecutionResult(
            tool_name=tool_name,
            success=success,
            result=result,
            execution_time=execution_time,
            error_message=error
        )
        self.tool_execution_history.append(record)
        
        # Keep only last 100 records to prevent memory issues
        if len(self.tool_execution_history) > 100:
            self.tool_execution_history = self.tool_execution_history[-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "agent_name": self.name,
            "metrics": self.metrics.dict(),
            "tool_executions": len(self.tool_execution_history),
            "recent_tool_success_rate": self._calculate_recent_tool_success_rate(),
            "average_tool_execution_time": self._calculate_average_tool_time()
        }
    
    def _calculate_recent_tool_success_rate(self) -> float:
        """Calculate success rate of recent tool executions"""
        if not self.tool_execution_history:
            return 1.0
        
        recent_executions = self.tool_execution_history[-20:]  # Last 20 executions
        successful = sum(1 for exec_record in recent_executions if exec_record.success)
        return successful / len(recent_executions)
    
    def _calculate_average_tool_time(self) -> float:
        """Calculate average tool execution time"""
        if not self.tool_execution_history:
            return 0.0
        
        total_time = sum(exec_record.execution_time for exec_record in self.tool_execution_history)
        return total_time / len(self.tool_execution_history)

# Custom agent with specialized behavior
class CustomFreelancerAgent(AdvancedAgent):
    """Custom agent specialized for freelancer needs"""
    
    def __init__(self, specialization: str, custom_tools: List[Callable] = None, expertise_level: str = "expert"):
        instructions = f"""
        You are a specialized {specialization} agent for freelancers with {expertise_level} level expertise.
        Focus on providing expert advice and tools for {specialization} tasks.
        Always consider the freelancer's perspective and business needs.
        
        Your expertise areas include:
        - {specialization} best practices and industry standards
        - Market analysis and competitive positioning
        - Client relationship management
        - Project planning and execution
        - Financial planning and pricing strategies
        
        Provide actionable, practical advice that freelancers can implement immediately.
        """
        
        super().__init__(
            name=f"{specialization.title()} Specialist",
            description=f"Specialized agent for {specialization} tasks with {expertise_level} expertise",
            instructions=instructions,
            tools=custom_tools or []
        )
        
        self.specialization = specialization
        self.expertise_level = expertise_level
        self.custom_tools = custom_tools or []
        self.specialization_metrics = {
            "specialization_requests": 0,
            "successful_specialization_advice": 0,
            "average_advice_quality_score": 0.0
        }

# Tool agent for specialized tool operations
class ToolAgent(AdvancedAgent):
    """Agent specialized for tool operations and integrations"""
    
    def __init__(self, tool_category: str, tools: List[Callable], optimization_level: str = "standard"):
        instructions = f"""
        You are a {tool_category} tool agent with {optimization_level} optimization capabilities.
        Your primary role is to execute {tool_category} related tools efficiently and accurately.
        
        Responsibilities:
        - Validate all inputs before tool execution
        - Provide clear explanations of tool results
        - Optimize tool usage for best performance
        - Handle errors gracefully with helpful feedback
        - Monitor tool performance and suggest improvements
        
        Always ensure tool outputs are properly formatted and actionable.
        """
        
        super().__init__(
            name=f"{tool_category.title()} Tool Agent",
            description=f"Specialized agent for {tool_category} tools with {optimization_level} optimization",
            instructions=instructions,
            tools=tools
        )
        
        self.tool_category = tool_category
        self.optimization_level = optimization_level
        self.tool_performance_metrics = {}
        
        # Initialize performance tracking for each tool
        for tool in tools:
            tool_name = getattr(tool, '__name__', str(tool))
            self.tool_performance_metrics[tool_name] = {
                "executions": 0,
                "successes": 0,
                "average_time": 0.0,
                "last_used": None
            }

# Enhanced session management
class EnhancedSession(Session):
    """Enhanced session with additional context and history management"""
    
    def __init__(self, agent: Agent, context: Dict[str, Any] = None):
        super().__init__(agent=agent, context=context or {})
        self.conversation_history = []
        self.user_preferences = {}
        self.system_state = {}
        self.created_at = datetime.datetime.now()
        self.session_metrics = {
            "message_count": 0,
            "average_message_length": 0.0,
            "user_satisfaction_score": 0.0,
            "session_duration": 0.0
        }
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add message to conversation history with enhanced tracking"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now(),
            "metadata": metadata or {},
            "message_length": len(content),
            "message_id": f"msg_{len(self.conversation_history) + 1}"
        }
        self.conversation_history.append(message)
        self.session_metrics["message_count"] += 1
        
        # Update average message length
        total_length = sum(msg["message_length"] for msg in self.conversation_history)
        self.session_metrics["average_message_length"] = total_length / self.session_metrics["message_count"]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of session context"""
        current_time = datetime.datetime.now()
        session_duration = (current_time - self.created_at).total_seconds()
        
        return {
            "session_id": id(self),
            "agent_name": self.agent.name,
            "created_at": self.created_at.isoformat(),
            "session_duration": session_duration,
            "message_count": self.session_metrics["message_count"],
            "average_message_length": self.session_metrics["average_message_length"],
            "user_preferences": self.user_preferences,
            "system_state": self.system_state,
            "recent_messages": self.conversation_history[-5:] if self.conversation_history else []
        }
    
    def update_user_preferences(self, preferences: Dict[str, Any]):
        """Update user preferences for personalization"""
        self.user_preferences.update(preferences)
        logger.info(f"Updated user preferences: {preferences}")
    
    def update_system_state(self, state_updates: Dict[str, Any]):
        """Update system state for context management"""
        self.system_state.update(state_updates)
        logger.info(f"Updated system state: {state_updates}")

# Advanced runner with enhanced capabilities
class EnhancedRunner(Runner):
    """Enhanced runner with additional monitoring and control"""
    
    def __init__(self, session: Session):
        super().__init__(session)
        self.execution_history = []
        self.performance_metrics = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time": 0.0,
            "success_rate": 1.0,
            "total_execution_time": 0.0
        }
        self.execution_config = {
            "max_retries": 3,
            "timeout_seconds": 30,
            "enable_tracing": True,
            "enable_metrics": True
        }
    
    async def run_with_monitoring(self, message: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run with enhanced monitoring and metrics"""
        start_time = datetime.datetime.now()
        
        # Update config if provided
        if config:
            self.execution_config.update(config)
        
        try:
            # Add message to session history
            if hasattr(self.session, 'add_message'):
                self.session.add_message("user", message)
            
            # Execute the run with timeout
            if self.execution_config["timeout_seconds"]:
                result = await asyncio.wait_for(
                    self.run(message), 
                    timeout=self.execution_config["timeout_seconds"]
                )
            else:
                result = await self.run(message)
            
            # Calculate metrics
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            self.performance_metrics["total_executions"] += 1
            self.performance_metrics["successful_executions"] += 1
            self.performance_metrics["total_execution_time"] += execution_time
            self.performance_metrics["average_execution_time"] = (
                self.performance_metrics["total_execution_time"] / 
                self.performance_metrics["total_executions"]
            )
            self.performance_metrics["success_rate"] = (
                self.performance_metrics["successful_executions"] / 
                self.performance_metrics["total_executions"]
            )
            
            # Record execution
            execution_record = {
                "timestamp": start_time.isoformat(),
                "message": message,
                "result": result,
                "execution_time": execution_time,
                "success": True,
                "config_used": self.execution_config.copy()
            }
            self.execution_history.append(execution_record)
            
            logger.info(f"Enhanced runner executed successfully in {execution_time:.2f}s")
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time,
                "metrics": self.performance_metrics.copy(),
                "config": self.execution_config.copy()
            }
            
        except asyncio.TimeoutError:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            self._record_failed_execution(start_time, message, "Timeout", execution_time)
            logger.error(f"Runner execution timed out after {execution_time:.2f}s")
            return {
                "success": False,
                "error": "Execution timed out",
                "execution_time": execution_time,
                "metrics": self.performance_metrics.copy()
            }
        except Exception as e:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            self._record_failed_execution(start_time, message, str(e), execution_time)
            logger.error(f"Runner execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "metrics": self.performance_metrics.copy()
            }
    
    def _record_failed_execution(self, start_time: datetime.datetime, message: str, error: str, execution_time: float):
        """Record failed execution for monitoring"""
        self.performance_metrics["total_executions"] += 1
        self.performance_metrics["failed_executions"] += 1
        self.performance_metrics["total_execution_time"] += execution_time
        self.performance_metrics["average_execution_time"] = (
            self.performance_metrics["total_execution_time"] / 
            self.performance_metrics["total_executions"]
        )
        self.performance_metrics["success_rate"] = (
            self.performance_metrics["successful_executions"] / 
            self.performance_metrics["total_executions"]
        )
        
        execution_record = {
            "timestamp": start_time.isoformat(),
            "message": message,
            "error": error,
            "execution_time": execution_time,
            "success": False,
            "config_used": self.execution_config.copy()
        }
        self.execution_history.append(execution_record)

# Advanced tool patterns with enhanced functionality
class AdvancedTool:
    """Advanced tool with enhanced validation and error handling"""
    
    def __init__(self, func: Callable, name: str = None, description: str = None, 
                 validation_rules: Dict[str, Any] = None, retry_config: Dict[str, Any] = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__
        self.validation_rules = validation_rules or {}
        self.retry_config = retry_config or {"max_retries": 3, "retry_delay": 1.0}
        self.execution_count = 0
        self.success_count = 0
        self.total_execution_time = 0.0
        self.last_execution_time = None
    
    def __call__(self, *args, **kwargs):
        """Execute tool with enhanced metrics collection and retry logic"""
        start_time = datetime.datetime.now()
        self.execution_count += 1
        
        # Validate inputs if rules are provided
        if self.validation_rules:
            self._validate_inputs(*args, **kwargs)
        
        # Execute with retry logic
        for attempt in range(self.retry_config["max_retries"] + 1):
            try:
                result = self.func(*args, **kwargs)
                execution_time = (datetime.datetime.now() - start_time).total_seconds()
                
                self.success_count += 1
                self.total_execution_time += execution_time
                self.last_execution_time = execution_time
                
                logger.info(f"Tool {self.name} executed successfully in {execution_time:.2f}s")
                return result
                
            except Exception as e:
                if attempt < self.retry_config["max_retries"]:
                    logger.warning(f"Tool {self.name} attempt {attempt + 1} failed: {str(e)}, retrying...")
                    asyncio.sleep(self.retry_config["retry_delay"])
                else:
                    logger.error(f"Tool {self.name} failed after {self.retry_config['max_retries']} retries: {str(e)}")
                    raise
    
    def _validate_inputs(self, *args, **kwargs):
        """Validate tool inputs based on rules"""
        # Basic validation implementation
        if "required_args" in self.validation_rules:
            required_count = self.validation_rules["required_args"]
            if len(args) < required_count:
                raise ValueError(f"Tool {self.name} requires at least {required_count} arguments")
    
    @property
    def success_rate(self) -> float:
        """Get tool success rate"""
        return self.success_count / self.execution_count if self.execution_count > 0 else 0.0
    
    @property
    def average_execution_time(self) -> float:
        """Get average tool execution time"""
        return self.total_execution_time / self.execution_count if self.execution_count > 0 else 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive tool performance summary"""
        return {
            "tool_name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "average_execution_time": self.average_execution_time,
            "last_execution_time": self.last_execution_time,
            "total_execution_time": self.total_execution_time
        }

# Enhanced tool decorator for advanced functionality
def advanced_tool(name: str = None, description: str = None, 
                  validation_rules: Dict[str, Any] = None, 
                  retry_config: Dict[str, Any] = None):
    """Decorator for creating advanced tools with enhanced functionality"""
    def decorator(func):
        advanced_tool_instance = AdvancedTool(
            func=func,
            name=name,
            description=description,
            validation_rules=validation_rules,
            retry_config=retry_config
        )
        
        # Create a wrapper that maintains the original function signature
        @wraps(func)
        def wrapper(*args, **kwargs):
            return advanced_tool_instance(*args, **kwargs)
        
        # Add advanced tool attributes to the wrapper
        wrapper.advanced_tool = advanced_tool_instance
        wrapper.get_performance_summary = advanced_tool_instance.get_performance_summary
        
        return wrapper
    return decorator

# Example enhanced tools with advanced functionality
@advanced_tool(
    name="Advanced Market Analysis",
    description="Comprehensive market analysis with multiple depth levels and dynamic insights",
    validation_rules={"required_args": 1},
    retry_config={"max_retries": 2, "retry_delay": 0.5}
)
def advanced_market_analysis(keywords: str, depth: str = "basic", market_focus: str = "global") -> Dict[str, Any]:
    """Advanced market analysis tool with multiple depth levels and market focus"""
    try:
        logger.info(f"Performing {depth} market analysis for '{keywords}' in {market_focus} market")
        
        # Dynamic analysis based on depth and market focus
        base_analysis = {
            "demand_level": "high",
            "competition": "medium",
            "average_rate": "$50-75/hour",
            "trend": "growing",
            "keywords": keywords,
            "market_focus": market_focus,
            "analysis_timestamp": datetime.datetime.now().isoformat()
        }
        
        if depth == "basic":
            analysis = base_analysis
        elif depth == "detailed":
            analysis = {
                **base_analysis,
                "market_size": "$2.5B",
                "growth_rate": "15% annually",
                "key_players": ["Company A", "Company B", "Company C"],
                "geographic_hotspots": ["US", "Europe", "Asia"],
                "technology_adoption": "High",
                "regulatory_environment": "Stable"
            }
        else:  # comprehensive
            analysis = {
                **base_analysis,
                "market_size": "$2.5B",
                "growth_rate": "15% annually",
                "key_players": ["Company A", "Company B", "Company C"],
                "geographic_hotspots": ["US", "Europe", "Asia"],
                "technology_trends": ["AI integration", "Remote work", "Automation"],
                "regulatory_environment": "Favorable",
                "investment_landscape": "Active",
                "skill_requirements": ["Technical expertise", "Communication", "Project management"],
                "pricing_trends": ["Increasing", "Value-based pricing"],
                "future_outlook": "Positive with 20% growth expected"
            }
        
        # Add market-specific insights
        if market_focus == "enterprise":
            analysis["enterprise_features"] = ["Security compliance", "Integration capabilities", "Scalability"]
        elif market_focus == "startup":
            analysis["startup_features"] = ["Cost-effectiveness", "Flexibility", "Quick deployment"]
        
        return {
            "analysis": analysis,
            "confidence_score": 0.85,
            "data_sources": ["Market research", "Industry reports", "Trend analysis"],
            "recommendations": [
                "Focus on differentiated value proposition",
                "Target high-growth market segments",
                "Invest in technology capabilities"
            ]
        }
        
    except Exception as e:
        logger.error(f"Advanced market analysis failed: {str(e)}")
        return {
            "error": str(e),
            "analysis": {"keywords": keywords, "status": "failed"},
            "confidence_score": 0.0
        }

@advanced_tool(
    name="Advanced Proposal Generator",
    description="Intelligent proposal generator with customization and optimization",
    validation_rules={"required_args": 3},
    retry_config={"max_retries": 1, "retry_delay": 0.2}
)
def advanced_proposal_generator(
    project_type: str,
    client_budget: str,
    experience_level: str,
    custom_requirements: str = "",
    proposal_style: str = "professional"
) -> Dict[str, Any]:
    """Advanced proposal generator with multiple customization options and style variations"""
    try:
        logger.info(f"Generating {proposal_style} proposal for {project_type} project")
        
        # Dynamic proposal generation based on parameters
        base_proposal = {
            "project_type": project_type,
            "client_budget": client_budget,
            "experience_level": experience_level,
            "proposal_style": proposal_style,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
        # Generate style-specific content
        if proposal_style == "professional":
            proposal_text = f"""
            Dear Client,
            
            Thank you for considering our services for your {project_type} project. Based on your requirements and budget of {client_budget}, I'm confident we can deliver exceptional results.
            
            With {experience_level} experience in {project_type}, I bring:
            • Proven track record of successful project delivery
            • Deep understanding of industry best practices
            • Commitment to quality and timely delivery
            • Transparent communication throughout the project
            
            {f"Custom Requirements: {custom_requirements}" if custom_requirements else ""}
            
            I look forward to discussing how we can bring your vision to life.
            
            Best regards,
            [Your Name]
            """
        elif proposal_style == "creative":
            proposal_text = f"""
            🚀 Ready to Transform Your {project_type} Vision!
            
            Hey there! I'm excited about your {project_type} project and the {client_budget} budget you've set aside. This is exactly the kind of challenge I love!
            
            What makes me the perfect fit:
            ✨ {experience_level} expertise in {project_type}
            ✨ Creative problem-solving approach
            ✨ Collaborative partnership mindset
            ✨ Results-driven methodology
            
            {f"🎯 Your Custom Requirements: {custom_requirements}" if custom_requirements else ""}
            
            Let's create something amazing together!
            
            Cheers,
            [Your Name]
            """
        else:  # concise
            proposal_text = f"""
            {project_type} Project Proposal
            
            Budget: {client_budget}
            Experience: {experience_level}
            
            Key Benefits:
            - Proven expertise in {project_type}
            - Quality-focused delivery
            - Competitive pricing
            
            {f"Custom Requirements: {custom_requirements}" if custom_requirements else ""}
            
            Ready to start when you are.
            """
        
        # Generate pricing structure based on experience level
        if experience_level == "expert":
            pricing = "Premium hourly rate with milestone payments"
            timeline = "3-4 weeks"
        elif experience_level == "intermediate":
            pricing = "Competitive hourly rate with project milestones"
            timeline = "4-6 weeks"
        else:
            pricing = "Value-based pricing with flexible payment terms"
            timeline = "5-8 weeks"
        
        proposal = {
            **base_proposal,
            "proposal_text": proposal_text,
            "pricing_structure": pricing,
            "timeline": timeline,
            "deliverables": [
                "Phase 1: Project Planning and Requirements Analysis",
                "Phase 2: Development and Implementation",
                "Phase 3: Testing and Quality Assurance",
                "Phase 4: Deployment and Documentation"
            ],
            "terms": "50% upfront, 50% upon completion",
            "next_steps": [
                "Schedule consultation call",
                "Review detailed project plan",
                "Sign agreement and begin work"
            ]
        }
        
        return {
            "proposal": proposal,
            "confidence_score": 0.90,
            "optimization_suggestions": [
                "Consider adding portfolio examples",
                "Include client testimonials if available",
                "Specify communication preferences"
            ]
        }
        
    except Exception as e:
        logger.error(f"Advanced proposal generation failed: {str(e)}")
        return {
            "error": str(e),
            "proposal": {"project_type": project_type, "status": "failed"},
            "confidence_score": 0.0
        }

# Agent factory for creating specialized agents
class AgentFactory:
    """Factory for creating specialized agents with enhanced capabilities"""
    
    @staticmethod
    def create_market_research_agent(expertise_level: str = "expert") -> CustomFreelancerAgent:
        """Create a market research specialized agent"""
        tools = [advanced_market_analysis]
        return CustomFreelancerAgent("market research", tools, expertise_level)
    
    @staticmethod
    def create_proposal_specialist_agent(expertise_level: str = "expert") -> CustomFreelancerAgent:
        """Create a proposal writing specialized agent"""
        tools = [advanced_proposal_generator]
        return CustomFreelancerAgent("proposal writing", tools, expertise_level)
    
    @staticmethod
    def create_tool_agent(tool_category: str, tools: List[Callable], optimization_level: str = "standard") -> ToolAgent:
        """Create a tool-specific agent with optimization"""
        return ToolAgent(tool_category, tools, optimization_level)
    
    @staticmethod
    def create_enhanced_session(agent: Agent, context: Dict[str, Any] = None) -> EnhancedSession:
        """Create an enhanced session for advanced agents"""
        return EnhancedSession(agent, context)
    
    @staticmethod
    def create_enhanced_runner(session: Session) -> EnhancedRunner:
        """Create an enhanced runner for advanced execution"""
        return EnhancedRunner(session)
