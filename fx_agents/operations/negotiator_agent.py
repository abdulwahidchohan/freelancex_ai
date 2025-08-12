"""FreelanceX.AI Negotiator Agent - OpenAI Agents SDK Implementation
Specialized agent for contract and rate negotiations
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NegotiationStrategy(BaseModel):
    """Negotiation strategy for freelancers"""
    key_points: List[str] = Field(..., description="Key negotiation points")
    value_propositions: List[str] = Field(..., description="Value propositions to emphasize")
    concession_strategy: Dict[str, Any] = Field(..., description="Strategy for concessions")
    walkaway_conditions: List[str] = Field(..., description="Conditions to walk away from deal")
    communication_approach: str = Field(..., description="Recommended communication style")
    counter_arguments: Dict[str, List[str]] = Field(..., description="Counter-arguments for common objections")
    target_range: Dict[str, float] = Field(..., description="Target price/rate range")
    timeline: str = Field(..., description="Negotiation timeline")

class ContractReview(BaseModel):
    """Contract review analysis"""
    key_terms: Dict[str, Any] = Field(..., description="Key contract terms")
    favorable_clauses: List[str] = Field(..., description="Favorable contract clauses")
    concerning_clauses: List[Dict[str, Any]] = Field(..., description="Concerning contract clauses")
    suggested_modifications: List[Dict[str, str]] = Field(..., description="Suggested contract modifications")
    legal_considerations: Optional[List[str]] = Field(None, description="Legal considerations")
    overall_assessment: str = Field(..., description="Overall contract assessment")
    risk_level: str = Field(..., description="Risk level assessment")
    recommended_actions: List[str] = Field(..., description="Recommended actions")

class RateAnalysis(BaseModel):
    """Rate analysis and benchmarking"""
    market_rate: float = Field(..., description="Market rate for similar work")
    recommended_rate: float = Field(..., description="Recommended rate")
    rate_factors: List[str] = Field(..., description="Factors affecting rate")
    negotiation_leverage: List[str] = Field(..., description="Sources of negotiation leverage")
    rate_justification: List[str] = Field(..., description="Justifications for rate")

class NegotiationTactic(BaseModel):
    """Specific negotiation tactic"""
    tactic_name: str = Field(..., description="Name of the tactic")
    description: str = Field(..., description="Description of the tactic")
    when_to_use: str = Field(..., description="When to use this tactic")
    implementation: List[str] = Field(..., description="How to implement the tactic")
    risks: List[str] = Field(..., description="Potential risks of the tactic")

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
    try:
        logger.info("Creating negotiation strategy")
        
        # Extract project information
        project_type = project_details.get("type", "general")
        project_scope = project_details.get("scope", "medium")
        project_duration = project_details.get("duration", "short-term")
        
        # Dynamic key points based on project type
        key_points = []
        if project_type.lower() in ["web_development", "software"]:
            key_points.extend([
                "Technical expertise and experience",
                "Quality assurance and testing",
                "Post-launch support and maintenance",
                "Intellectual property rights"
            ])
        elif project_type.lower() in ["design", "creative"]:
            key_points.extend([
                "Creative vision and expertise",
                "Revision limits and scope",
                "Usage rights and licensing",
                "Portfolio quality and reputation"
            ])
        else:
            key_points.extend([
                "Value-based pricing",
                "Clear scope and deliverables",
                "Milestones and payment terms",
                "Quality and expertise"
            ])
        
        # Generate value propositions
        value_propositions = [
            "Specialized expertise in the field",
            "Proven track record and portfolio",
            "Flexible and responsive communication",
            "High-quality deliverables"
        ]
        
        # Dynamic concession strategy
        concession_strategy = {
            "max_discount_percent": 15,
            "non_monetary_concessions": [
                "Extended timeline for complex features",
                "Additional documentation",
                "Training or knowledge transfer",
                "Future project discounts"
            ],
            "concession_order": [
                "Timeline flexibility",
                "Additional deliverables",
                "Payment terms",
                "Rate adjustments"
            ]
        }
        
        # Walkaway conditions
        walkaway_conditions = [
            "Rate below market minimum",
            "Unclear or constantly changing scope",
            "Excessive unpaid work or trials",
            "Unreasonable payment terms",
            "Lack of respect for expertise"
        ]
        
        # Communication approach
        communication_approach = "Professional and collaborative"
        if client_info and client_info.get("communication_style") == "direct":
            communication_approach = "Direct and efficient"
        elif client_info and client_info.get("budget_constraints"):
            communication_approach = "Value-focused and flexible"
        
        # Counter-arguments for common objections
        counter_arguments = {
            "budget_constraints": [
                "Propose phased approach to align with budget",
                "Highlight long-term value and ROI",
                "Offer alternative pricing models",
                "Suggest scope adjustments"
            ],
            "timeline_pressure": [
                "Emphasize quality over speed",
                "Propose additional resources",
                "Suggest priority-based delivery",
                "Offer expedited options at premium"
            ],
            "experience_concerns": [
                "Share relevant portfolio examples",
                "Provide client testimonials",
                "Offer trial period or pilot project",
                "Demonstrate problem-solving approach"
            ]
        }
        
        # Target range based on project scope
        base_rate = 75.0  # Base hourly rate
        if project_scope == "large":
            base_rate = 100.0
        elif project_scope == "small":
            base_rate = 60.0
        
        target_range = {
            "minimum": base_rate * 0.9,
            "target": base_rate,
            "maximum": base_rate * 1.2
        }
        
        # Timeline
        timeline = "1-2 weeks"
        if project_duration == "long-term":
            timeline = "2-4 weeks"
        elif project_duration == "urgent":
            timeline = "3-5 days"
        
        return NegotiationStrategy(
            key_points=key_points,
            value_propositions=value_propositions,
            concession_strategy=concession_strategy,
            walkaway_conditions=walkaway_conditions,
            communication_approach=communication_approach,
            counter_arguments=counter_arguments,
            target_range=target_range,
            timeline=timeline
        )
        
    except Exception as e:
        logger.error(f"Error creating negotiation strategy: {e}")
        return NegotiationStrategy(
            key_points=["Review project details"],
            value_propositions=["Expertise and quality"],
            concession_strategy={"max_discount_percent": 10},
            walkaway_conditions=["Below market rates"],
            communication_approach="Professional",
            counter_arguments={"budget": ["Value-based pricing"]},
            target_range={"minimum": 50.0, "target": 75.0, "maximum": 100.0},
            timeline="1-2 weeks"
        )

@tool
def review_contract(contract_text: str, freelancer_priorities: Optional[List[str]] = None) -> ContractReview:
    """Review a contract and provide analysis and suggestions
    
    Args:
        contract_text: The text of the contract to review
        freelancer_priorities: Optional list of freelancer's priorities
    
    Returns:
        Contract review with analysis and suggested modifications
    """
    try:
        logger.info("Reviewing contract")
        
        # Analyze contract text for key terms
        contract_lower = contract_text.lower()
        
        # Extract key terms
        key_terms = {}
        if "payment" in contract_lower:
            key_terms["payment_terms"] = "net 30" if "net 30" in contract_lower else "net 14"
        if "intellectual property" in contract_lower or "ip" in contract_lower:
            key_terms["ip_rights"] = "client owns deliverables"
        if "termination" in contract_lower:
            key_terms["termination"] = "30 days notice"
        
        # Identify favorable clauses
        favorable_clauses = []
        if "milestone" in contract_lower:
            favorable_clauses.append("Milestone-based payments")
        if "acceptance criteria" in contract_lower:
            favorable_clauses.append("Clear acceptance criteria")
        if "scope" in contract_lower and "defined" in contract_lower:
            favorable_clauses.append("Well-defined project scope")
        
        # Identify concerning clauses
        concerning_clauses = []
        if "indemnify" in contract_lower and "unlimited" in contract_lower:
            concerning_clauses.append({
                "clause": "Unlimited indemnification",
                "reason": "Exposes freelancer to unlimited liability",
                "risk_level": "high"
            })
        if "work for hire" in contract_lower and "payment" not in contract_lower:
            concerning_clauses.append({
                "clause": "Work for hire without payment condition",
                "reason": "IP transfers before payment is received",
                "risk_level": "medium"
            })
        if "non-compete" in contract_lower and "broad" in contract_lower:
            concerning_clauses.append({
                "clause": "Broad non-compete clause",
                "reason": "May restrict future work opportunities",
                "risk_level": "medium"
            })
        
        # Generate suggested modifications
        suggested_modifications = []
        if concerning_clauses:
            for clause in concerning_clauses:
                if "indemnification" in clause["clause"]:
                    suggested_modifications.append({
                        "clause": "Indemnification",
                        "change": "Limit to direct damages and reasonable attorney fees",
                        "rationale": "Protect against unlimited liability exposure"
                    })
                if "work for hire" in clause["clause"]:
                    suggested_modifications.append({
                        "clause": "IP Transfer",
                        "change": "IP transfers only upon full payment",
                        "rationale": "Ensure payment before transferring rights"
                    })
        
        # Legal considerations
        legal_considerations = [
            "Jurisdiction and governing law",
            "Liability limitations",
            "Dispute resolution process",
            "Confidentiality obligations"
        ]
        
        # Overall assessment
        risk_level = "low"
        if len([c for c in concerning_clauses if c.get("risk_level") == "high"]) > 0:
            risk_level = "high"
        elif len(concerning_clauses) > 2:
            risk_level = "medium"
        
        overall_assessment = f"Contract has {len(favorable_clauses)} favorable and {len(concerning_clauses)} concerning clauses. Risk level: {risk_level}."
        
        # Recommended actions
        recommended_actions = []
        if risk_level == "high":
            recommended_actions.extend([
                "Consult with legal professional",
                "Request significant modifications",
                "Consider walking away if terms cannot be improved"
            ])
        elif risk_level == "medium":
            recommended_actions.extend([
                "Negotiate key modifications",
                "Clarify ambiguous terms",
                "Ensure payment terms are favorable"
            ])
        else:
            recommended_actions.extend([
                "Review for minor improvements",
                "Ensure scope is clearly defined",
                "Confirm payment terms are acceptable"
            ])
        
        return ContractReview(
            key_terms=key_terms,
            favorable_clauses=favorable_clauses,
            concerning_clauses=concerning_clauses,
            suggested_modifications=suggested_modifications,
            legal_considerations=legal_considerations,
            overall_assessment=overall_assessment,
            risk_level=risk_level,
            recommended_actions=recommended_actions
        )
        
    except Exception as e:
        logger.error(f"Error reviewing contract: {e}")
        return ContractReview(
            key_terms={},
            favorable_clauses=[],
            concerning_clauses=[{"clause": "Review error", "reason": str(e)}],
            suggested_modifications=[],
            legal_considerations=["Review contract format"],
            overall_assessment="Error in contract review",
            risk_level="unknown",
            recommended_actions=["Review contract text format"]
        )

@tool
def analyze_market_rates(skills: List[str], experience_level: str, location: Optional[str] = None) -> RateAnalysis:
    """Analyze market rates for freelancer skills and experience
    
    Args:
        skills: List of skills/expertise areas
        experience_level: Experience level (junior, mid, senior, expert)
        location: Optional location for regional rate analysis
    
    Returns:
        RateAnalysis with market rates and recommendations
    """
    try:
        logger.info("Analyzing market rates")
        
        # Base rates by experience level
        experience_multipliers = {
            "junior": 0.7,
            "mid": 1.0,
            "senior": 1.3,
            "expert": 1.6
        }
        
        # Skill-based rate adjustments
        skill_rates = {
            "web_development": 75.0,
            "mobile_development": 80.0,
            "ui_ux_design": 70.0,
            "content_writing": 50.0,
            "digital_marketing": 60.0,
            "data_analysis": 85.0,
            "machine_learning": 100.0,
            "project_management": 65.0
        }
        
        # Calculate base market rate
        base_rate = 60.0  # Default base rate
        for skill in skills:
            skill_lower = skill.lower()
            for skill_key, rate in skill_rates.items():
                if skill_key in skill_lower:
                    base_rate = max(base_rate, rate)
                    break
        
        # Apply experience multiplier
        multiplier = experience_multipliers.get(experience_level.lower(), 1.0)
        market_rate = base_rate * multiplier
        
        # Location adjustments
        if location:
            location_lower = location.lower()
            if "san francisco" in location_lower or "new york" in location_lower:
                market_rate *= 1.3
            elif "london" in location_lower or "toronto" in location_lower:
                market_rate *= 1.2
            elif "remote" in location_lower:
                market_rate *= 0.9
        
        # Recommended rate (slightly above market)
        recommended_rate = market_rate * 1.1
        
        # Rate factors
        rate_factors = [
            f"Experience level: {experience_level}",
            f"Skills: {', '.join(skills)}",
            f"Market demand for skills",
            f"Project complexity and scope"
        ]
        if location:
            rate_factors.append(f"Geographic location: {location}")
        
        # Negotiation leverage
        leverage_points = []
        if experience_level.lower() in ["senior", "expert"]:
            leverage_points.append("High level of expertise and experience")
        if len(skills) > 2:
            leverage_points.append("Diverse skill set and versatility")
        leverage_points.extend([
            "Proven track record and portfolio",
            "Specialized knowledge in high-demand areas",
            "Reliability and professional communication"
        ])
        
        # Rate justification
        justifications = [
            "Market-competitive pricing for expertise level",
            "Value delivered through quality and efficiency",
            "Specialized skills and experience",
            "Professional service and communication"
        ]
        
        return RateAnalysis(
            market_rate=round(market_rate, 2),
            recommended_rate=round(recommended_rate, 2),
            rate_factors=rate_factors,
            negotiation_leverage=leverage_points,
            rate_justification=justifications
        )
        
    except Exception as e:
        logger.error(f"Error analyzing market rates: {e}")
        return RateAnalysis(
            market_rate=75.0,
            recommended_rate=85.0,
            rate_factors=["Error in analysis"],
            negotiation_leverage=["Review input data"],
            rate_justification=["Standard market rate"]
        )

@tool
def generate_negotiation_tactics(negotiation_context: str, client_personality: Optional[str] = None) -> List[NegotiationTactic]:
    """Generate specific negotiation tactics for different situations
    
    Args:
        negotiation_context: Context of the negotiation
        client_personality: Optional client personality type
    
    Returns:
        List of NegotiationTactic with specific strategies
    """
    try:
        logger.info("Generating negotiation tactics")
        
        tactics = []
        context_lower = negotiation_context.lower()
        
        # Anchor pricing tactic
        if "rate" in context_lower or "price" in context_lower:
            tactics.append(NegotiationTactic(
                tactic_name="Anchoring",
                description="Set a high initial rate to establish the negotiation range",
                when_to_use="When client has budget flexibility and you want to maximize rate",
                implementation=[
                    "Start with rate 20-30% above target",
                    "Justify with specific value propositions",
                    "Be prepared to negotiate down to target range"
                ],
                risks=["May scare away budget-conscious clients", "Could damage relationship if too aggressive"]
            ))
        
        # Value-based pricing tactic
        if "value" in context_lower or "roi" in context_lower:
            tactics.append(NegotiationTactic(
                tactic_name="Value-Based Pricing",
                description="Focus on value delivered rather than time spent",
                when_to_use="When project has clear business impact or ROI",
                implementation=[
                    "Quantify project benefits and outcomes",
                    "Present ROI calculations",
                    "Emphasize long-term value over short-term cost"
                ],
                risks=["Requires clear value metrics", "May not work for all project types"]
            ))
        
        # Package deal tactic
        if "scope" in context_lower or "multiple" in context_lower:
            tactics.append(NegotiationTactic(
                tactic_name="Package Deal",
                description="Bundle services for better overall rate",
                when_to_use="When client needs multiple services or long-term work",
                implementation=[
                    "Offer discounted rate for larger scope",
                    "Include additional services at reduced rate",
                    "Propose retainer or ongoing relationship"
                ],
                risks=["May reduce per-project profitability", "Requires careful scope management"]
            ))
        
        # Walk-away power tactic
        if "deadlock" in context_lower or "stuck" in context_lower:
            tactics.append(NegotiationTactic(
                tactic_name="Walk-Away Power",
                description="Demonstrate willingness to walk away from bad deals",
                when_to_use="When client is being unreasonable or terms are unfavorable",
                implementation=[
                    "Clearly state your bottom line",
                    "Be prepared to end negotiations",
                    "Maintain professional demeanor throughout"
                ],
                risks=["Could lose the project entirely", "May damage future relationship"]
            ))
        
        # Default tactics if no specific context
        if not tactics:
            tactics.extend([
                NegotiationTactic(
                    tactic_name="Collaborative Problem Solving",
                    description="Work together to find mutually beneficial solutions",
                    when_to_use="Most negotiation situations",
                    implementation=[
                        "Identify shared interests and goals",
                        "Explore creative solutions",
                        "Focus on win-win outcomes"
                    ],
                    risks=["May require more time and effort"]
                ),
                NegotiationTactic(
                    tactic_name="Silence and Patience",
                    description="Use strategic silence to encourage client to make offers",
                    when_to_use="When client is hesitant or uncertain",
                    implementation=[
                        "Ask open-ended questions",
                        "Wait for client responses",
                        "Let client fill the silence"
                    ],
                    risks=["May create awkward moments", "Requires confidence"]
                )
            ])
        
        return tactics
        
    except Exception as e:
        logger.error(f"Error generating negotiation tactics: {e}")
        return [NegotiationTactic(
            tactic_name="Error in tactic generation",
            description=f"Error: {str(e)}",
            when_to_use="Review negotiation context",
            implementation=["Troubleshoot tactic generation"],
            risks=["Process error"]
        )]

# Create negotiator agent
negotiator_agent = Agent(
    name="Negotiator Agent",
    instructions="""You are the Negotiator Agent for FreelanceX.AI, specialized in helping freelancers negotiate contracts and rates effectively.

Your primary responsibilities include:
1. Creating comprehensive negotiation strategies for specific projects and clients
2. Reviewing contracts and identifying potential issues and opportunities
3. Analyzing market rates and providing rate recommendations
4. Generating specific negotiation tactics for different situations
5. Providing language for counter-offers and rate discussions
6. Helping freelancers understand their market value and leverage

When creating negotiation strategies:
- Focus on value-based negotiation rather than just price
- Consider the specific client and project context
- Provide clear walkaway conditions to avoid bad deals
- Suggest effective communication approaches
- Include target ranges and timelines

When reviewing contracts:
- Identify potentially problematic clauses and their risks
- Suggest specific modifications to protect freelancer interests
- Highlight important terms that may need clarification
- Provide overall risk assessment and recommended actions
- Consider legal implications and jurisdiction

When analyzing rates:
- Consider skills, experience, location, and market demand
- Provide market benchmarks and recommended rates
- Identify sources of negotiation leverage
- Justify rates with value propositions

When generating tactics:
- Provide specific, actionable negotiation strategies
- Consider client personality and negotiation context
- Explain when and how to use each tactic
- Highlight potential risks and mitigation strategies

You should provide practical, actionable negotiation advice that helps freelancers secure fair compensation while building positive client relationships.
""",
    tools=[create_negotiation_strategy, review_contract, analyze_market_rates, generate_negotiation_tactics]
)