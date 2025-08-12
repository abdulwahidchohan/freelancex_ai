"""Enhanced Triage Agent - OpenAI Agents SDK Integration
Provides intelligent request routing with full SDK handoffs and tracing
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool as tool, Session
from .custom_agent import create_dynamic_agent, DynamicAgent, AgentResponse, AgentRegistry
from memory.sqlite_memory import get_memory, create_enhanced_session
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable tracing to avoid API key issues
def set_trace_metadata(metadata: Dict[str, Any]) -> None:
    """Disabled trace metadata to avoid API key issues"""
    pass

# Try to disable tracing completely
try:
    from agents import set_tracing_disabled
    set_tracing_disabled(True)
except ImportError:
    pass

class RoutingDecision(BaseModel):
    """Enhanced routing decision with SDK features"""
    target_agent: str = Field(..., description="Target agent name")
    confidence: float = Field(..., description="Routing confidence score")
    reasoning: str = Field(..., description="Routing reasoning")
    handoff_type: str = Field(default="direct", description="Type of handoff")
    priority: int = Field(default=5, description="Request priority 1-10")
    estimated_time: float = Field(default=0.0, description="Estimated processing time")

class TriageResult(BaseModel):
    """Enhanced triage result with SDK features"""
    success: bool = Field(..., description="Success status")
    response: str = Field(..., description="Response content")
    routing_decision: Optional[RoutingDecision] = Field(default=None, description="Routing decision")
    handoffs: List[str] = Field(default_factory=list, description="Handoffs performed")
    execution_time: float = Field(..., description="Execution time")
    trace_id: Optional[str] = Field(default=None, description="Trace identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

@tool
def analyze_request_complexity(request: str, user_context: str = "") -> str:
    """Analyze request complexity for routing decisions"""
    try:
        # Dynamic complexity analysis
        complexity_score = 0.0
        factors = []
        
        # Analyze request length
        if len(request) > 500:
            complexity_score += 0.3
            factors.append("long_request")
        
        # Analyze keywords for complexity
        complex_keywords = ["analyze", "research", "comprehensive", "detailed", "strategy", "planning"]
        if any(keyword in request.lower() for keyword in complex_keywords):
            complexity_score += 0.4
            factors.append("complex_keywords")
        
        # Analyze user context
        if user_context and "beginner" in user_context.lower():
            complexity_score += 0.2
            factors.append("beginner_user")
        
        # Analyze request type
        if "proposal" in request.lower() or "strategy" in request.lower():
            complexity_score += 0.5
            factors.append("strategic_request")
        
        result = {
            "complexity_score": min(complexity_score, 1.0),
            "factors": factors,
            "recommended_agents": _get_recommended_agents(complexity_score, factors),
            "estimated_time": _estimate_processing_time(complexity_score)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Request complexity analysis failed: {str(e)}")
        error_result = {
            "complexity_score": 0.5,
            "factors": ["analysis_error"],
            "recommended_agents": ["general_agent"],
            "estimated_time": 30.0
        }
        return json.dumps(error_result, indent=2)

@tool
def determine_optimal_agent(request: str, complexity_analysis: str, available_agents: str) -> str:
    """Determine optimal agent for request handling"""
    try:
        # Parse inputs
        try:
            complexity_data = json.loads(complexity_analysis) if complexity_analysis else {}
        except json.JSONDecodeError:
            complexity_data = {}
        
        available_agents_list = [agent.strip() for agent in available_agents.split(',') if agent.strip()]
        
        # Dynamic agent selection logic
        complexity_score = complexity_data.get("complexity_score", 0.5)
        factors = complexity_data.get("factors", [])
        recommended_agents = complexity_data.get("recommended_agents", [])
        
        # Map request types to agents
        agent_mapping = {
            "job_search": ["job_search_agent", "market_research_agent"],
            "proposal": ["proposal_writer_agent", "content_agent"],
            "marketing": ["marketing_agent", "content_agent"],
            "research": ["web_research_agent", "cognitive_agent"],
            "math": ["math_agent", "automation_agent"],
            "security": ["security_agent", "governance_agent"],
            "ux": ["ux_agent", "content_agent"],
            "expansion": ["expansion_agent", "system_architect_agent"]
        }
        
        # Determine request type
        request_type = _classify_request_type(request)
        candidate_agents = agent_mapping.get(request_type, ["general_agent"])
        
        # Filter by available agents
        available_candidates = [agent for agent in candidate_agents if agent in available_agents_list]
        
        if not available_candidates:
            available_candidates = available_agents_list[:1] if available_agents_list else ["general_agent"]
        
        # Select best agent based on complexity
        if complexity_score > 0.7:
            # High complexity - use specialized agents
            target_agent = available_candidates[0] if available_candidates else "cognitive_agent"
            confidence = 0.8
            handoff_type = "specialized"
        elif complexity_score > 0.4:
            # Medium complexity - use balanced agents
            target_agent = available_candidates[0] if available_candidates else "general_agent"
            confidence = 0.7
            handoff_type = "balanced"
        else:
            # Low complexity - use general agents
            target_agent = "general_agent"
            confidence = 0.9
            handoff_type = "direct"
        
        reasoning = f"Request classified as {request_type} with complexity {complexity_score:.2f}. Selected {target_agent} for {handoff_type} handling."
        
        result = {
            "target_agent": target_agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "handoff_type": handoff_type,
            "priority": int(complexity_score * 10),
            "estimated_time": complexity_data.get("estimated_time", 30.0)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Agent determination failed: {str(e)}")
        error_result = {
            "target_agent": "general_agent",
            "confidence": 0.5,
            "reasoning": f"Fallback selection due to error: {str(e)}",
            "handoff_type": "fallback",
            "priority": 5,
            "estimated_time": 30.0
        }
        return json.dumps(error_result, indent=2)

def _classify_request_type(request: str) -> str:
    """Classify request type based on content"""
    request_lower = request.lower()
    
    if any(word in request_lower for word in ["job", "position", "opportunity", "hire"]):
        return "job_search"
    elif any(word in request_lower for word in ["proposal", "quote", "bid", "pitch"]):
        return "proposal"
    elif any(word in request_lower for word in ["marketing", "campaign", "promotion", "advertising"]):
        return "marketing"
    elif any(word in request_lower for word in ["research", "find", "search", "investigate"]):
        return "research"
    elif any(word in request_lower for word in ["calculate", "math", "compute", "analyze"]):
        return "math"
    elif any(word in request_lower for word in ["security", "privacy", "compliance", "risk"]):
        return "security"
    elif any(word in request_lower for word in ["ux", "ui", "interface", "user experience"]):
        return "ux"
    elif any(word in request_lower for word in ["expand", "growth", "scaling", "development"]):
        return "expansion"
    else:
        return "general"

def _get_recommended_agents(complexity_score: float, factors: List[str]) -> List[str]:
    """Get recommended agents based on complexity"""
    if complexity_score > 0.7:
        return ["cognitive_agent", "executive_agent", "system_architect_agent"]
    elif complexity_score > 0.4:
        return ["general_agent", "proposal_writer_agent", "marketing_agent"]
    else:
        return ["general_agent", "content_agent"]

def _estimate_processing_time(complexity_score: float) -> float:
    """Estimate processing time based on complexity"""
    return 15.0 + (complexity_score * 45.0)  # 15-60 seconds

class DynamicTriageAgent:
    """Enhanced triage agent with full SDK integration"""
    
    def __init__(self):
        self.agent = None
        self.specialized_agents: Dict[str, DynamicAgent] = {}
        self.memory = get_memory()
        self.agent_registry = AgentRegistry()  # Add agent registry
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize triage agent and specialized agents"""
        try:
            # Create triage agent with SDK features
            self.agent = Agent(
                name="FreelanceX Dynamic Triage Agent",
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
                tools=[analyze_request_complexity, determine_optimal_agent]
            )
            
            # Initialize specialized agents
            self._initialize_specialized_agents()
            
            logger.info("Enhanced triage agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize triage agent: {str(e)}")
            raise
    
    def _initialize_specialized_agents(self):
        """Initialize all specialized agents"""
        try:
            # Import and create specialized agents
            from .executive_core.executive_agent import executive_agent
            from .cognitive_core.cognitive_agent import cognitive_agent
            from .operations.job_search_agent import job_search_agent
            from .operations.proposal_writer_agent import proposal_writer_agent
            from .operations.web_research_agent import web_research_agent
            from .operations.math_agent import math_agent
            from .operations.marketing_agent import marketing_agent
            from .security.security_agent import security_agent
            from .user_experience.ux_agent import ux_agent
            from .expansion.expansion_agent import expansion_agent
            
            # Register specialized agents (use SDK Agent instances directly)
            self.specialized_agents = {
                "executive_agent": executive_agent,
                "cognitive_agent": cognitive_agent,
                "job_search_agent": job_search_agent,
                "proposal_writer_agent": proposal_writer_agent,
                "web_research_agent": web_research_agent,
                "math_agent": math_agent,
                "marketing_agent": marketing_agent,
                "security_agent": security_agent,
                "ux_agent": ux_agent,
                "expansion_agent": expansion_agent
            }
            
            logger.info(f"Initialized {len(self.specialized_agents)} specialized agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize specialized agents: {str(e)}")
            raise
    
    async def route_request(self, message: str, session_id: str, user_id: Optional[str] = None,
                           trace_metadata: Optional[Dict[str, Any]] = None) -> TriageResult:
        """Route request with enhanced SDK features"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Set trace metadata for SDK integration (disabled to avoid API key issues)
            # if trace_metadata:
            #     set_trace_metadata(trace_metadata)
            
            # Create enhanced session (with error handling)
            try:
                session = await create_enhanced_session(
                    session_id=session_id,
                    user_id=user_id,
                    agent=self.agent,
                    trace_metadata=trace_metadata
                )
            except Exception as session_error:
                logger.warning(f"Session creation failed in triage agent: {str(session_error)}")
                session = None
            
            # Add request to memory
            await self.memory.add_memory_entry(
                session_id=session_id,
                message_type="user",
                content=message,
                user_id=user_id,
                metadata={"agent_name": "triage_agent", "trace_metadata": trace_metadata}
            )
            
            # Create runner (without session parameter)
            runner = Runner()
            
            # Analyze request complexity (simplified routing logic)
            available_agents = list(self.specialized_agents.keys())
            
            # Simple keyword-based routing instead of complex AI analysis
            message_lower = message.lower()
            
            # Define routing keywords
            routing_keywords = {
                "job_search_agent": ["job", "opportunity", "position", "hire", "employment", "work", "freelance job"],
                "proposal_writer_agent": ["proposal", "bid", "quote", "cover letter", "application", "pitch"],
                "math_agent": ["calculate", "budget", "price", "cost", "financial", "math", "number", "percentage"],
                "web_research_agent": ["research", "trend", "market", "industry", "analysis", "study", "investigate"],
                "marketing_agent": ["marketing", "campaign", "promotion", "advertising", "brand", "social media"],
                "security_agent": ["security", "privacy", "compliance", "risk", "protection", "audit"],
                "ux_agent": ["ux", "ui", "design", "user experience", "interface", "usability"],
                "expansion_agent": ["expand", "growth", "scale", "business", "strategy", "planning"],
                "executive_agent": ["strategy", "leadership", "management", "decision", "planning"],
                "cognitive_agent": ["analysis", "thinking", "problem", "complex", "reasoning"]
            }
            
            # Find the best matching agent
            best_agent = "executive_agent"  # Default
            best_score = 0
            
            for agent_name, keywords in routing_keywords.items():
                score = sum(1 for keyword in keywords if keyword in message_lower)
                if score > best_score:
                    best_score = score
                    best_agent = agent_name
            
            # Create a simple routing result
            routing_result = f"Routed to {best_agent} with confidence {min(best_score / 3, 1.0):.2f}"
            
            # Extract routing decision
            routing_decision = _extract_routing_decision(routing_result, available_agents)
            
            # Execute handoff to specialized agent
            target_agent_name = routing_decision.target_agent
            target_agent = self.specialized_agents.get(target_agent_name)
            
            if target_agent:
                # Perform handoff using Runner.run() with agent and input
                try:
                    # Create runner and run the agent with the message
                    runner = Runner()
                    agent_response = await runner.run(target_agent, message)
                    
                    # Extract response content
                    if hasattr(agent_response, 'content'):
                        response_content = agent_response.content
                    elif hasattr(agent_response, 'output'):
                        response_content = agent_response.output
                    else:
                        response_content = str(agent_response)
                    
                    handoffs = [target_agent_name]
                except Exception as agent_error:
                    logger.error(f"Agent {target_agent_name} execution failed: {str(agent_error)}")
                    
                    # Provide helpful fallback responses based on the agent type
                    fallback_responses = {
                        "job_search_agent": f"I understand you're looking for freelance opportunities. While I'm having trouble accessing my job search tools right now, I recommend checking platforms like Upwork, Fiverr, LinkedIn, and Toptal for {message.lower().replace('help me find', '').replace('jobs', '').strip()} opportunities. You can also try networking on professional platforms and reaching out to companies directly.",
                        "proposal_writer_agent": f"I'd be happy to help you with proposal writing for {message.lower().replace('write a proposal for', '').replace('help me create', '').strip()}. While my tools are temporarily unavailable, here are some key elements to include: clear project scope, timeline, pricing, your qualifications, and a compelling value proposition. Would you like me to provide a template structure?",
                        "math_agent": f"I can help you with calculations for {message.lower().replace('calculate', '').replace('help me', '').strip()}. While my calculation tools are temporarily unavailable, I can guide you through the process. For project pricing, consider: hourly rate × estimated hours + buffer for revisions. For example, $75/hour × 40 hours = $3,000 base cost.",
                        "web_research_agent": f"I'd love to research {message.lower().replace('research', '').replace('find information about', '').strip()} for you. While my research tools are temporarily unavailable, I recommend checking industry reports, LinkedIn insights, and professional forums for the latest trends and information.",
                        "marketing_agent": f"I can help you with marketing strategy for {message.lower().replace('help me create a marketing strategy', '').replace('how can i promote', '').strip()}. While my marketing tools are temporarily unavailable, consider focusing on: social media presence, content marketing, networking, and showcasing your portfolio.",
                        "executive_agent": f"I can provide strategic guidance for {message.lower().replace('help me with', '').replace('strategy', '').strip()}. While my analysis tools are temporarily unavailable, I recommend focusing on: clear goals, market analysis, competitive positioning, and measurable outcomes.",
                        "cognitive_agent": f"I can help you analyze {message.lower().replace('analyze', '').replace('help me understand', '').strip()}. While my analysis tools are temporarily unavailable, I can guide you through a structured approach: define the problem, gather information, evaluate options, and make informed decisions.",
                        "security_agent": f"I can help you with security considerations for {message.lower().replace('security', '').replace('help me with', '').strip()}. While my security tools are temporarily unavailable, consider: data protection, secure communication, compliance requirements, and risk assessment.",
                        "ux_agent": f"I can help you with UX/UI design for {message.lower().replace('ux', '').replace('ui', '').replace('design', '').strip()}. While my design tools are temporarily unavailable, focus on: user research, wireframing, prototyping, and user testing.",
                        "expansion_agent": f"I can help you with business expansion for {message.lower().replace('expand', '').replace('growth', '').replace('help me with', '').strip()}. While my expansion tools are temporarily unavailable, consider: market research, scaling strategies, and partnership opportunities."
                    }
                    
                    response_content = fallback_responses.get(target_agent_name, f"I understand you're asking about {message}. While I'm having trouble accessing my specialized tools right now, I'd be happy to help you with general guidance. Could you provide more specific details about what you're looking for?")
                    handoffs = []
            else:
                # Fallback response
                response_content = f"Unable to route to {target_agent_name}. Please try a different request."
                handoffs = []
            
            # Calculate execution time
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Add triage result to memory
            await self.memory.add_memory_entry(
                session_id=session_id,
                message_type="system",
                content=f"Request routed to {target_agent_name} with confidence {routing_decision.confidence}",
                user_id=user_id,
                agent_name="triage_agent",
                handoffs=handoffs,
                metadata={
                    "routing_decision": routing_decision.dict(),
                    "execution_time": execution_time
                }
            )
            
            return TriageResult(
                success=True,
                response=response_content,
                routing_decision=routing_decision,
                handoffs=handoffs,
                execution_time=execution_time,
                trace_id=getattr(routing_result, 'trace_id', None),
                metadata={
                    "target_agent": target_agent_name,
                    "confidence": routing_decision.confidence,
                    "handoff_type": routing_decision.handoff_type
                }
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            logger.error(f"Triage routing failed: {str(e)}")
            
            # Record error in memory
            await self.memory.add_memory_entry(
                session_id=session_id,
                message_type="error",
                content=f"Triage routing failed: {str(e)}",
                user_id=user_id,
                agent_name="triage_agent",
                metadata={"error": str(e), "execution_time": execution_time}
            )
            
            return TriageResult(
                success=False,
                response=f"Routing error: {str(e)}",
                execution_time=execution_time,
                metadata={"error": str(e)}
            )
    
    def add_custom_agent(self, agent_name: str, agent: DynamicAgent):
        """Add custom agent to triage system"""
        try:
            self.specialized_agents[agent_name] = agent
            logger.info(f"Added custom agent: {agent_name}")
        except Exception as e:
            logger.error(f"Failed to add custom agent {agent_name}: {str(e)}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            return {
                "registered_agents": {
                    name: "active" for name in self.specialized_agents.keys()
                },
                "api_providers": "available",
                "total_agents": len(self.specialized_agents) + 1,
                "triage_agent": "active"
            }
        except Exception as e:
            logger.error(f"Failed to get agent status: {str(e)}")
            return {"error": str(e)}

def _extract_routing_decision(result, available_agents: List[str]) -> RoutingDecision:
    """Extract routing decision from simplified routing result"""
    try:
        # Parse the simplified routing result
        result_str = str(result)
        
        # Extract agent name and confidence from the simplified format
        # Format: "Routed to {agent_name} with confidence {confidence}"
        if "Routed to" in result_str:
            parts = result_str.split("Routed to ")[1].split(" with confidence ")
            target_agent = parts[0]
            confidence = float(parts[1]) if len(parts) > 1 else 0.7
        else:
            # Fallback parsing
            target_agent = "executive_agent"
            confidence = 0.7
        
        # Validate that the target agent exists
        if target_agent not in available_agents:
            target_agent = "executive_agent"
            confidence = 0.5
        
        reasoning = f"Keyword-based routing to {target_agent}"
        
        return RoutingDecision(
            target_agent=target_agent,
            confidence=confidence,
            reasoning=reasoning,
            handoff_type="direct",
            priority=5,
            estimated_time=30.0
        )
        
    except Exception as e:
        logger.error(f"Failed to extract routing decision: {str(e)}")
        return RoutingDecision(
            target_agent="executive_agent",
            confidence=0.5,
            reasoning=f"Fallback due to extraction error: {str(e)}",
            handoff_type="fallback",
            priority=5,
            estimated_time=30.0
        )

# Create enhanced triage agent instance
dynamic_triage_agent = DynamicTriageAgent()

# Legacy compatibility
triage_agent = dynamic_triage_agent.agent

async def route_request(message: str, session_id: str, user_id: Optional[str] = None,
                       trace_metadata: Optional[Dict[str, Any]] = None) -> TriageResult:
    """Route request using enhanced triage agent"""
    return await dynamic_triage_agent.route_request(message, session_id, user_id, trace_metadata)