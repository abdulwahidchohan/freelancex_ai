#!/usr/bin/env python3
"""
FreelanceX.AI Enhanced Cognitive Agent - OpenAI Agents SDK Implementation
Dynamic cognitive agent for deep reasoning and decision-making capabilities
"""

from agents import Agent, function_tool as tool
from functools import partial
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime

# Use non-strict schema to allow Dict/Any parameters
tool = partial(tool, strict_mode=False)

logger = logging.getLogger(__name__)

class ReasoningRequest(BaseModel):
    """Reasoning request model"""
    problem: str = Field(..., description="Problem to analyze")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    constraints: List[str] = Field(default_factory=list, description="Problem constraints")
    objectives: List[str] = Field(default_factory=list, description="Objectives to achieve")

class ReasoningResponse(BaseModel):
    """Reasoning response model"""
    conclusion: str = Field(..., description="Main conclusion")
    confidence: float = Field(..., description="Confidence level (0-1)")
    reasoning_path: List[str] = Field(default_factory=list, description="Reasoning steps")
    alternatives: List[str] = Field(default_factory=list, description="Alternative approaches")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")

class DecisionRequest(BaseModel):
    """Decision request model"""
    options: List[str] = Field(..., description="Available options")
    criteria: List[str] = Field(..., description="Decision criteria")
    weights: Dict[str, float] = Field(default_factory=dict, description="Criteria weights")
    context: Dict[str, Any] = Field(default_factory=dict, description="Decision context")

class DecisionResponse(BaseModel):
    """Decision response model"""
    selected_option: str = Field(..., description="Selected option")
    confidence: float = Field(..., description="Confidence level (0-1)")
    reasoning: str = Field(..., description="Reasoning for selection")
    alternatives_analysis: Dict[str, float] = Field(default_factory=dict, description="Analysis of alternatives")
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation strategies")

@tool
def analyze_reasoning(request: ReasoningRequest) -> ReasoningResponse:
    """Perform deep reasoning analysis on a complex problem
    
    Args:
        request: Reasoning request with problem and context
    
    Returns:
        Detailed reasoning analysis with conclusion and steps
    """
    try:
        # Validate input
        if not request.problem:
            return ReasoningResponse(
                conclusion="No problem specified for analysis",
                confidence=0.0,
                reasoning_path=["Input validation failed"],
                alternatives=["Provide a specific problem to analyze"],
                next_steps=["Define the problem clearly", "Provide relevant context"]
            )
        
        # Dynamic reasoning based on problem type
        problem_lower = request.problem.lower()
        
        # Analyze problem complexity
        complexity = "high" if len(request.problem.split()) > 50 else "medium" if len(request.problem.split()) > 20 else "low"
        
        # Generate reasoning path based on problem type
        if "business" in problem_lower or "strategy" in problem_lower:
            reasoning_path = [
                "Market analysis and competitive landscape",
                "Resource assessment and capabilities",
                "Risk evaluation and mitigation",
                "Strategic alignment and objectives"
            ]
            conclusion = "Business strategy requires comprehensive market analysis and resource planning"
        elif "technical" in problem_lower or "development" in problem_lower:
            reasoning_path = [
                "Technical requirements analysis",
                "Architecture and design considerations",
                "Implementation approach and timeline",
                "Quality assurance and testing strategy"
            ]
            conclusion = "Technical solution requires careful planning and iterative development"
        elif "financial" in problem_lower or "budget" in problem_lower:
            reasoning_path = [
                "Financial impact assessment",
                "Cost-benefit analysis",
                "Resource allocation optimization",
                "Risk management and contingency planning"
            ]
            conclusion = "Financial decision requires thorough analysis and risk management"
        else:
            reasoning_path = [
                "Problem decomposition and analysis",
                "Solution exploration and evaluation",
                "Implementation planning and execution",
                "Monitoring and optimization"
            ]
            conclusion = "General problem-solving approach with systematic analysis"
        
        # Generate alternatives based on context
        alternatives = []
        if request.context.get("multiple_approaches"):
            alternatives = ["Conservative approach", "Aggressive approach", "Balanced approach"]
        else:
            alternatives = ["Direct solution", "Iterative improvement", "Alternative methodology"]
        
        # Generate next steps
        next_steps = [
            "Validate the analysis with stakeholders",
            "Develop detailed implementation plan",
            "Set up monitoring and feedback mechanisms"
        ]
        
        # Calculate confidence based on available information
        confidence = min(0.9, 0.3 + len(request.context) * 0.1 + len(request.constraints) * 0.05)
        
        return ReasoningResponse(
            conclusion=conclusion,
            confidence=confidence,
            reasoning_path=reasoning_path,
            alternatives=alternatives,
            next_steps=next_steps
        )
        
    except Exception as e:
        logger.error(f"Error in reasoning analysis: {str(e)}")
        return ReasoningResponse(
            conclusion="Analysis failed due to technical error",
            confidence=0.0,
            reasoning_path=["Error occurred during analysis"],
            alternatives=["Retry analysis", "Simplify problem statement"],
            next_steps=["Check input data", "Retry with simplified problem"]
        )

@tool
def make_decision(request: DecisionRequest) -> DecisionResponse:
    """Make structured decision based on options and criteria
    
    Args:
        request: Decision request with options and criteria
    
    Returns:
        Decision analysis with selected option and reasoning
    """
    try:
        # Validate input
        if not request.options or not request.criteria:
            return DecisionResponse(
                selected_option="",
                confidence=0.0,
                reasoning="Insufficient information for decision making",
                alternatives_analysis={},
                risks=["Incomplete information"],
                mitigation_strategies=["Gather more data", "Define clear criteria"]
            )
        
        # Dynamic decision analysis
        alternatives_analysis = {}
        
        # Analyze each option against criteria
        for option in request.options:
            score = 0.0
            for criterion in request.criteria:
                weight = request.weights.get(criterion, 1.0)
                # Simple scoring heuristic
                if criterion.lower() in option.lower():
                    score += weight * 0.8
                else:
                    score += weight * 0.3
            alternatives_analysis[option] = min(1.0, score / len(request.criteria))
        
        # Select best option
        if alternatives_analysis:
            selected_option = max(alternatives_analysis.keys(), key=lambda x: alternatives_analysis[x])
            confidence = alternatives_analysis[selected_option]
        else:
            selected_option = request.options[0] if request.options else ""
            confidence = 0.5
        
        # Generate reasoning
        reasoning = f"Selected '{selected_option}' based on analysis of {len(request.criteria)} criteria"
        if request.weights:
            reasoning += f" with weighted evaluation"
        
        # Identify risks
        risks = []
        if confidence < 0.7:
            risks.append("Low confidence in decision")
        if len(request.options) < 2:
            risks.append("Limited options available")
        if not request.weights:
            risks.append("No criteria weighting provided")
        
        # Generate mitigation strategies
        mitigation_strategies = []
        if confidence < 0.7:
            mitigation_strategies.append("Gather additional information")
        if len(request.options) < 2:
            mitigation_strategies.append("Explore additional options")
        mitigation_strategies.append("Monitor decision outcomes")
        mitigation_strategies.append("Prepare contingency plans")
        
        return DecisionResponse(
            selected_option=selected_option,
            confidence=confidence,
            reasoning=reasoning,
            alternatives_analysis=alternatives_analysis,
            risks=risks,
            mitigation_strategies=mitigation_strategies
        )
        
    except Exception as e:
        logger.error(f"Error in decision making: {str(e)}")
        return DecisionResponse(
            selected_option="",
            confidence=0.0,
            reasoning=f"Decision making failed: {str(e)}",
            alternatives_analysis={},
            risks=["Decision process error"],
            mitigation_strategies=["Review input data", "Retry decision process"]
        )

# Create dynamic cognitive agent
cognitive_agent = Agent(
    name="Cognitive Core Agent",
    instructions="""You are the Cognitive Core Agent for FreelanceX.AI, responsible for deep reasoning and decision-making capabilities.

Your role is to:
1. Perform complex reasoning analysis on problems
2. Make structured decisions based on multiple criteria
3. Provide logical conclusions and recommendations
4. Identify risks and mitigation strategies

Use the available tools to:
- analyze_reasoning: Perform deep reasoning analysis on complex problems
- make_decision: Make structured decisions based on options and criteria

Always provide clear reasoning, consider multiple perspectives, and ensure logical consistency in your analysis.
""",
    tools=[analyze_reasoning, make_decision]
)