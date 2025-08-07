"""FreelanceX.AI Triage Agent - OpenAI Agents SDK Implementation
Main coordinator that routes user requests to specialized agents
Implements proper OpenAI Agent SDK features including tracing and session management
"""

from agents import Agent, Runner, tool
from pydantic import BaseModel
from typing import List, Dict, Any

# Import agents from all layers
# Executive Core Layer
from .executive_core import executive_agent

# Cognitive Core Layer
from .cognitive_core import cognitive_agent

# Operations Layer
from .operations import job_search_agent, proposal_writer_agent, web_research_agent, math_agent
from .operations import marketing_agent, client_liaison_agent, negotiator_agent, automation_agent

# User Experience Layer
from .user_experience import ux_agent

# Security & Reliability Layer
from .security import security_agent

# Expansion Layer
from .expansion import expansion_agent

class RequestAnalysis(BaseModel):
    """Analysis of user request for routing"""
    primary_intent: str
    confidence: float
    required_agents: List[str]
    complexity: str
    reasoning: str

@tool
def analyze_request(user_input: str) -> RequestAnalysis:
    """Analyze the user request to determine routing strategy
    
    Args:
        user_input: The user's request message
    
    Returns:
        Analysis of the request including intent, confidence, and required agents
    """
    # Simple deterministic routing heuristic to bootstrap triage behavior
    text = (user_input or "").lower()

    # Keyword-based mapping to agent names (matching Agent.name values)
    routes = [
        ("job", "Job Search Agent"),
        ("search", "Job Search Agent"),
        ("proposal", "Proposal Writer Agent"),
        ("cover letter", "Proposal Writer Agent"),
        ("market", "Web Research Agent"),
        ("research", "Web Research Agent"),
        ("trend", "Web Research Agent"),
        ("price", "Web Research Agent"),
        ("rate", "Math Agent"),
        ("budget", "Math Agent"),
        ("tax", "Math Agent"),
        ("roi", "Math Agent"),
        ("marketing", "Marketing Agent"),
        ("brand", "Marketing Agent"),
        ("client", "Client Liaison Agent"),
        ("communication", "Client Liaison Agent"),
        ("negotia", "Negotiator Agent"),
        ("contract", "Negotiator Agent"),
        ("automation", "Automation Agent"),
        ("workflow", "Automation Agent"),
        ("ux", "User Experience Agent"),
        ("experience", "User Experience Agent"),
        ("security", "Security Agent"),
        ("threat", "Security Agent"),
        ("expand", "Expansion Agent"),
        ("feature", "Expansion Agent"),
        ("strategy", "Executive Core Agent"),
        ("govern", "Executive Core Agent"),
        ("decision", "Cognitive Core Agent"),
        ("reason", "Cognitive Core Agent"),
    ]

    matched_agents: List[str] = []
    for keyword, agent_name in routes:
        if keyword in text and agent_name not in matched_agents:
            matched_agents.append(agent_name)

    if not matched_agents:
        matched_agents = ["Cognitive Core Agent"]
        primary_intent = "reasoning"
        confidence = 0.5
        reasoning = "No specific domain keywords found; defaulting to Cognitive Core Agent."
    else:
        primary_intent = matched_agents[0]
        confidence = 0.7 if len(matched_agents) == 1 else 0.6
        reasoning = f"Matched keywords to agents: {', '.join(matched_agents)}"

    # Rough complexity heuristic
    complexity = "high" if (" and " in text or len(text.split()) > 30) else "medium" if len(text.split()) > 12 else "low"

    return RequestAnalysis(
        primary_intent=primary_intent,
        confidence=confidence,
        required_agents=matched_agents,
        complexity=complexity,
        reasoning=reasoning,
    )

# Create triage agent with handoffs to specialized agents
triage_agent = Agent(
    name="FreelanceX Triage Agent",
    instructions="""You are the main coordinator for FreelanceX.AI, a comprehensive AI assistant for freelancers.

Your role is to analyze user requests and route them to the most appropriate specialized agent within our hierarchical structure:

**Available Specialized Agents:**

**Executive Core Layer:**
- **Executive Agent** - For high-level strategic decisions and business planning

**Cognitive Core Layer:**
- **Cognitive Agent** - For complex reasoning, decision-making, and problem-solving

**Operations Layer:**
- **Job Search Agent** - For finding freelance jobs, analyzing market demand, career guidance
- **Proposal Writer Agent** - For creating compelling proposals, cover letters, pricing strategies
- **Web Research Agent** - For market research, industry trends, competitor analysis
- **Math Agent** - For financial calculations, budgeting, ROI analysis, tax calculations
- **Marketing Agent** - For marketing strategy, content creation, personal branding
- **Client Liaison Agent** - For client relationship management and communication
- **Negotiator Agent** - For contract and rate negotiations, terms review
- **Automation Agent** - For workflow automation and efficiency improvements

**User Experience Layer:**
- **UX Agent** - For optimizing user interface and experience

**Security & Reliability Layer:**
- **Security Agent** - For security assessments and data protection

**Expansion Layer:**
- **Expansion Agent** - For platform growth and new capability development

**Routing Guidelines:**
- Strategic business decisions → Executive Agent
- Complex reasoning tasks → Cognitive Agent
- Job-related queries → Job Search Agent
- Proposal/application requests → Proposal Writer Agent  
- Research/market analysis → Web Research Agent
- Financial/mathematical calculations → Math Agent
- Marketing and branding → Marketing Agent
- Client communication → Client Liaison Agent
- Contract and rate negotiations → Negotiator Agent
- Workflow optimization → Automation Agent
- User experience feedback → UX Agent
- Security concerns → Security Agent
- Platform growth ideas → Expansion Agent
- Complex requests may require multiple agents

Before routing, use the analyze_request tool to determine the best agent(s) for the job.
Always provide a brief explanation of why you're routing to a specific agent.

When handling complex requests that might require multiple agents, consider:
1. Which agent should handle the primary task
2. What information needs to be gathered first
3. How to synthesize information from multiple sources

Ensure all responses are helpful, accurate, and tailored to freelancers' needs.""",
    handoffs=[
        # Executive Core Layer
        executive_agent,
        
        # Cognitive Core Layer
        cognitive_agent,
        
        # Operations Layer
        job_search_agent,
        proposal_writer_agent, 
        web_research_agent,
        math_agent,
        marketing_agent,
        client_liaison_agent,
        negotiator_agent,
        automation_agent,
        
        # User Experience Layer
        ux_agent,
        
        # Security & Reliability Layer
        security_agent,
        
        # Expansion Layer
        expansion_agent
    ],
    tools=[analyze_request]
)

async def route_request(user_input: str) -> Dict[str, Any]:
    """Route user request to appropriate agent"""
    try:
        result = await Runner.run(triage_agent, user_input)
        return {
            "success": True,
            "agent_used": result.last_agent.name if result.last_agent else "Triage Agent",
            "response": result.final_output,
            "handoffs": len(result.handoffs) if result.handoffs else 0,
            "trace_id": result.trace_id if hasattr(result, 'trace_id') else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "I apologize, but I encountered an error processing your request. Please try again."
        }