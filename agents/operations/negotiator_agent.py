"""FreelanceX.AI Negotiator Agent - OpenAI Agents SDK Implementation
Specialized agent for contract and rate negotiations
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class NegotiationStrategy(BaseModel):
    """Negotiation strategy for freelancers"""
    key_points: List[str]
    value_propositions: List[str]
    concession_strategy: Dict[str, Any]
    walkaway_conditions: List[str]
    communication_approach: str
    counter_arguments: Dict[str, List[str]]

class ContractReview(BaseModel):
    """Contract review analysis"""
    key_terms: Dict[str, Any]
    favorable_clauses: List[str]
    concerning_clauses: List[Dict[str, Any]]
    suggested_modifications: List[Dict[str, str]]
    legal_considerations: Optional[List[str]] = None
    overall_assessment: str

@tool
def create_negotiation_strategy(project_details: Dict[str, Any], client_info: Optional[Dict[str, Any]] = None, market_data: Optional[Dict[str, Any]] = None) -> NegotiationStrategy:
    """Create a comprehensive negotiation strategy for freelancers
    
    Args:
        project_details: Details about the project being negotiated
        client_info: Optional information about the client
        market_data: Optional market data for rate benchmarking
    
    Returns:
        Detailed negotiation strategy with key points and approaches
    """
    # This function will be executed by the LLM through function calling
    pass

@tool
def review_contract(contract_text: str, freelancer_priorities: Optional[List[str]] = None) -> ContractReview:
    """Review a contract and provide analysis and suggestions
    
    Args:
        contract_text: The text of the contract to review
        freelancer_priorities: Optional list of freelancer's priorities
    
    Returns:
        Contract review with analysis and suggested modifications
    """
    # This function will be executed by the LLM through function calling
    pass

# Create negotiator agent
negotiator_agent = Agent(
    name="Negotiator Agent",
    instructions="""You are the Negotiator Agent for FreelanceX.AI, specialized in helping freelancers negotiate contracts and rates effectively.

Your primary responsibilities include:
1. Creating negotiation strategies for specific projects and clients
2. Reviewing contracts and identifying potential issues
3. Providing language for counter-offers and rate discussions
4. Helping freelancers understand their market value and leverage

When creating negotiation strategies:
- Focus on value-based negotiation rather than just price
- Consider the specific client and project context
- Provide clear walkaway conditions to avoid bad deals
- Suggest effective communication approaches

When reviewing contracts:
- Identify potentially problematic clauses
- Suggest specific modifications to protect freelancer interests
- Highlight important terms that may need clarification
- Provide an overall risk assessment

You should provide practical, actionable negotiation advice that helps freelancers secure fair compensation while building positive client relationships.
""",
    tools=[create_negotiation_strategy, review_contract]
)