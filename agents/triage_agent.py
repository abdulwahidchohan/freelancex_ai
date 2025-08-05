"""
FreelanceX.AI Triage Agent - OpenAI Agents SDK Implementation
Central coordinator that routes requests to specialized agents
"""

from agents import Agent, InputGuardrail, GuardrailFunctionOutput
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class TaskValidation(BaseModel):
    is_valid_task: bool
    task_category: str
    reasoning: str
    confidence: float

# Guardrail agent for input validation
guardrail_agent = Agent(
    name="Task Validation Guardrail",
    instructions="""You validate if user requests are legitimate freelancer tasks.
    
    Valid tasks include:
    - Job searching and career advice
    - Proposal writing and client communication
    - Research and market analysis  
    - Financial calculations and budgeting
    - Project planning and time management
    
    Invalid tasks include:
    - Unethical requests
    - Personal information requests
    - Off-topic conversations
    
    Respond with validation details.""",
    output_type=TaskValidation
)

async def task_validation_guardrail(ctx, agent, input_data: str) -> GuardrailFunctionOutput:
    """Validate incoming tasks"""
    try:
        from agents import Runner
        
        result = await Runner.run(
            agent=guardrail_agent,
            message=f"Validate this freelancer task: {input_data}",
            context=ctx.context
        )
        
        validation = result.final_output_as(TaskValidation)
        
        # Trigger tripwire if task is invalid or confidence too low
        tripwire_triggered = not validation.is_valid_task or validation.confidence < 0.3
        
        return GuardrailFunctionOutput(
            output_info=validation,
            tripwire_triggered=tripwire_triggered
        )
        
    except Exception as e:
        logger.error(f"Task validation error: {e}")
        return GuardrailFunctionOutput(
            output_info=TaskValidation(
                is_valid_task=False,
                task_category="error", 
                reasoning=f"Validation error: {str(e)}",
                confidence=0.0
            ),
            tripwire_triggered=True
        )

# Main triage agent
triage_agent = Agent(
    name="FreelanceX Triage Agent",
    instructions="""You are the central coordinator for FreelanceX.AI, a freelancer assistance platform.

    Your role is to:
    1. Understand user requests related to freelancing
    2. Route requests to the appropriate specialized agent
    3. Coordinate between agents when needed
    4. Provide helpful responses to users

    Available specialized agents:
    - JobSearchAgent: Finding jobs, career advice, skill matching
    - ProposalWriterAgent: Writing proposals, cover letters, client communication
    - WebResearchAgent: Market research, industry trends, competitive analysis
    - MathAgent: Financial calculations, budgeting, ROI analysis

    Always be professional, helpful, and focused on freelancer success.""",
    
    handoffs=[],  # Will be populated when other agents are imported
    
    input_guardrails=[
        InputGuardrail(guardrail_function=task_validation_guardrail)
    ]
)