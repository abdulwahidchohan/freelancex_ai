#!/usr/bin/env python3
"""
FreelanceX.AI Enhanced Math Agent - OpenAI Agents SDK Implementation
Dynamic math agent for calculations, analysis, and mathematical problem solving
"""

from agents import Agent, function_tool as tool
from functools import partial
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import math
import statistics

# Use non-strict schema to allow Dict/Any parameters
tool = partial(tool, strict_mode=False)

logger = logging.getLogger(__name__)

class CalculationRequest(BaseModel):
    """Calculation request model"""
    expression: str = Field(..., description="Mathematical expression to evaluate")
    variables: Optional[Dict[str, float]] = Field(default_factory=dict, description="Variable values")
    precision: int = Field(4, description="Decimal precision for results")
    calculation_type: str = Field("basic", description="Type of calculation (basic, advanced, statistical)")

class CalculationResult(BaseModel):
    """Calculation result model"""
    expression: str = Field(..., description="Original expression")
    result: float = Field(..., description="Calculation result")
    steps: List[str] = Field(default_factory=list, description="Calculation steps")
    units: Optional[str] = Field(None, description="Units of measurement")
    confidence: float = Field(..., description="Confidence in result (0-1)")
    warnings: List[str] = Field(default_factory=list, description="Any warnings or notes")

class StatisticalAnalysis(BaseModel):
    """Statistical analysis model"""
    dataset: List[float] = Field(..., description="Input dataset")
    mean: float = Field(..., description="Arithmetic mean")
    median: float = Field(..., description="Median value")
    mode: Optional[float] = Field(None, description="Mode value")
    std_deviation: float = Field(..., description="Standard deviation")
    variance: float = Field(..., description="Variance")
    min_value: float = Field(..., description="Minimum value")
    max_value: float = Field(..., description="Maximum value")
    range_value: float = Field(..., description="Range (max - min)")
    quartiles: Dict[str, float] = Field(default_factory=dict, description="Quartile values")
    outliers: List[float] = Field(default_factory=list, description="Outlier values")

class FinancialCalculation(BaseModel):
    """Financial calculation model"""
    calculation_type: str = Field(..., description="Type of financial calculation")
    principal: float = Field(..., description="Principal amount")
    rate: float = Field(..., description="Interest rate (as decimal)")
    time: float = Field(..., description="Time period")
    result: float = Field(..., description="Calculation result")
    formula_used: str = Field(..., description="Formula applied")
    breakdown: Dict[str, float] = Field(default_factory=dict, description="Calculation breakdown")

@tool
def calculate_expression(request: CalculationRequest) -> CalculationResult:
    """Calculate mathematical expressions with support for variables and different types
    
    Args:
        request: Calculation request with expression and parameters
    
    Returns:
        Calculation result with steps and confidence
    """
    try:
        # Validate input
        if not request.expression:
            return CalculationResult(
                expression="",
                result=0.0,
                steps=["No expression provided"],
                confidence=0.0,
                warnings=["Empty expression provided"]
            )
        
        # Dynamic calculation based on expression type
        expression = request.expression.lower().strip()
        steps = []
        warnings = []
        
        # Handle different calculation types
        if request.calculation_type == "basic":
            result = _evaluate_basic_expression(expression, request.variables, steps, warnings)
        elif request.calculation_type == "advanced":
            result = _evaluate_advanced_expression(expression, request.variables, steps, warnings)
        elif request.calculation_type == "statistical":
            result = _evaluate_statistical_expression(expression, request.variables, steps, warnings)
        else:
            result = _evaluate_basic_expression(expression, request.variables, steps, warnings)
        
        # Apply precision
        result = round(result, request.precision)
        
        # Determine confidence based on calculation complexity
        confidence = 0.95 if len(warnings) == 0 else 0.8 - len(warnings) * 0.1
        confidence = max(0.5, confidence)
        
        return CalculationResult(
            expression=request.expression,
            result=result,
            steps=steps,
            confidence=confidence,
            warnings=warnings
        )
        
    except Exception as e:
        logger.error(f"Error in calculation: {str(e)}")
        return CalculationResult(
            expression=request.expression,
            result=0.0,
            steps=["Calculation failed"],
            confidence=0.0,
            warnings=[f"Calculation error: {str(e)}"]
        )

def _evaluate_basic_expression(expression: str, variables: Dict[str, float], steps: List[str], warnings: List[str]) -> float:
    """Evaluate basic mathematical expressions"""
    try:
        # Replace variables with values
        for var, value in variables.items():
            expression = expression.replace(var, str(value))
            steps.append(f"Substituted {var} = {value}")
        
        # Handle common mathematical functions
        if "sqrt" in expression:
            expression = expression.replace("sqrt", "math.sqrt")
            steps.append("Applied square root function")
        
        if "pow" in expression:
            expression = expression.replace("pow", "math.pow")
            steps.append("Applied power function")
        
        if "log" in expression:
            expression = expression.replace("log", "math.log10")
            steps.append("Applied logarithm function")
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        steps.append(f"Evaluated: {expression} = {result}")
        
        return float(result)
        
    except Exception as e:
        warnings.append(f"Basic evaluation failed: {str(e)}")
        return 0.0

def _evaluate_advanced_expression(expression: str, variables: Dict[str, float], steps: List[str], warnings: List[str]) -> float:
    """Evaluate advanced mathematical expressions"""
    try:
        # Handle trigonometric functions
        if any(func in expression for func in ["sin", "cos", "tan"]):
            expression = expression.replace("sin", "math.sin")
            expression = expression.replace("cos", "math.cos")
            expression = expression.replace("tan", "math.tan")
            steps.append("Applied trigonometric functions")
        
        # Handle exponential and logarithmic functions
        if "exp" in expression:
            expression = expression.replace("exp", "math.exp")
            steps.append("Applied exponential function")
        
        if "ln" in expression:
            expression = expression.replace("ln", "math.log")
            steps.append("Applied natural logarithm")
        
        # Replace variables
        for var, value in variables.items():
            expression = expression.replace(var, str(value))
            steps.append(f"Substituted {var} = {value}")
        
        # Evaluate
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        steps.append(f"Evaluated: {expression} = {result}")
        
        return float(result)
        
    except Exception as e:
        warnings.append(f"Advanced evaluation failed: {str(e)}")
        return 0.0

def _evaluate_statistical_expression(expression: str, variables: Dict[str, float], steps: List[str], warnings: List[str]) -> float:
    """Evaluate statistical expressions"""
    try:
        # Handle statistical functions
        if "mean" in expression:
            # Extract numbers from expression
            numbers = [float(v) for v in variables.values() if isinstance(v, (int, float))]
            if numbers:
                result = statistics.mean(numbers)
                steps.append(f"Calculated mean of {numbers} = {result}")
                return result
        
        if "median" in expression:
            numbers = [float(v) for v in variables.values() if isinstance(v, (int, float))]
            if numbers:
                result = statistics.median(numbers)
                steps.append(f"Calculated median of {numbers} = {result}")
                return result
        
        # Default to basic evaluation
        return _evaluate_basic_expression(expression, variables, steps, warnings)
        
    except Exception as e:
        warnings.append(f"Statistical evaluation failed: {str(e)}")
        return 0.0

@tool
def analyze_statistics(dataset: List[float]) -> StatisticalAnalysis:
    """Perform comprehensive statistical analysis on a dataset
    
    Args:
        dataset: List of numerical values to analyze
    
    Returns:
        Comprehensive statistical analysis
    """
    try:
        # Validate input
        if not dataset or len(dataset) < 2:
            return StatisticalAnalysis(
                dataset=dataset,
                mean=0.0,
                median=0.0,
                std_deviation=0.0,
                variance=0.0,
                min_value=0.0,
                max_value=0.0,
                range_value=0.0,
                quartiles={},
                outliers=[]
            )
        
        # Calculate basic statistics
        mean = statistics.mean(dataset)
        median = statistics.median(dataset)
        std_deviation = statistics.stdev(dataset) if len(dataset) > 1 else 0.0
        variance = statistics.variance(dataset) if len(dataset) > 1 else 0.0
        min_value = min(dataset)
        max_value = max(dataset)
        range_value = max_value - min_value
        
        # Calculate mode
        try:
            mode = statistics.mode(dataset)
        except statistics.StatisticsError:
            mode = None
        
        # Calculate quartiles
        sorted_data = sorted(dataset)
        n = len(sorted_data)
        q1 = sorted_data[n // 4] if n >= 4 else sorted_data[0]
        q2 = median
        q3 = sorted_data[3 * n // 4] if n >= 4 else sorted_data[-1]
        
        quartiles = {
            "Q1": q1,
            "Q2": q2,
            "Q3": q3
        }
        
        # Identify outliers using IQR method
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = [x for x in dataset if x < lower_bound or x > upper_bound]
        
        return StatisticalAnalysis(
            dataset=dataset,
            mean=mean,
            median=median,
            mode=mode,
            std_deviation=std_deviation,
            variance=variance,
            min_value=min_value,
            max_value=max_value,
            range_value=range_value,
            quartiles=quartiles,
            outliers=outliers
        )
        
    except Exception as e:
        logger.error(f"Error in statistical analysis: {str(e)}")
        return StatisticalAnalysis(
            dataset=dataset,
            mean=0.0,
            median=0.0,
            std_deviation=0.0,
            variance=0.0,
            min_value=0.0,
            max_value=0.0,
            range_value=0.0,
            quartiles={},
            outliers=[]
        )

@tool
def calculate_financial(calculation_type: str, principal: float, rate: float, time: float) -> FinancialCalculation:
    """Perform financial calculations (interest, compound interest, etc.)
    
    Args:
        calculation_type: Type of financial calculation
        principal: Principal amount
        rate: Interest rate (as decimal)
        time: Time period
    
    Returns:
        Financial calculation result
    """
    try:
        # Validate input
        if principal <= 0 or rate < 0 or time <= 0:
            return FinancialCalculation(
                calculation_type=calculation_type,
                principal=principal,
                rate=rate,
                time=time,
                result=0.0,
                formula_used="Invalid input parameters",
                breakdown={}
            )
        
        # Dynamic financial calculations
        if calculation_type.lower() == "simple_interest":
            result = principal * rate * time
            formula_used = "A = P * r * t"
            breakdown = {
                "principal": principal,
                "interest": result,
                "total": principal + result
            }
        
        elif calculation_type.lower() == "compound_interest":
            result = principal * (1 + rate) ** time - principal
            formula_used = "A = P(1 + r)^t - P"
            breakdown = {
                "principal": principal,
                "interest": result,
                "total": principal + result
            }
        
        elif calculation_type.lower() == "future_value":
            result = principal * (1 + rate) ** time
            formula_used = "FV = P(1 + r)^t"
            breakdown = {
                "principal": principal,
                "interest": result - principal,
                "future_value": result
            }
        
        elif calculation_type.lower() == "present_value":
            result = principal / (1 + rate) ** time
            formula_used = "PV = FV / (1 + r)^t"
            breakdown = {
                "future_value": principal,
                "discount": principal - result,
                "present_value": result
            }
        
        else:
            # Default to simple interest
            result = principal * rate * time
            formula_used = "A = P * r * t (default)"
            breakdown = {
                "principal": principal,
                "interest": result,
                "total": principal + result
            }
        
        return FinancialCalculation(
            calculation_type=calculation_type,
            principal=principal,
            rate=rate,
            time=time,
            result=result,
            formula_used=formula_used,
            breakdown=breakdown
        )
        
    except Exception as e:
        logger.error(f"Error in financial calculation: {str(e)}")
        return FinancialCalculation(
            calculation_type=calculation_type,
            principal=principal,
            rate=rate,
            time=time,
            result=0.0,
            formula_used="Calculation failed",
            breakdown={}
        )

# Create dynamic math agent
math_agent = Agent(
    name="Math Agent",
    instructions="""You are the Math Agent for FreelanceX.AI, specialized in mathematical calculations and analysis.

Your role is to:
1. Perform mathematical calculations with high precision
2. Conduct statistical analysis on datasets
3. Perform financial calculations and analysis
4. Provide step-by-step solutions and explanations

Use the available tools to:
- calculate_expression: Evaluate mathematical expressions with variables and different types
- analyze_statistics: Perform comprehensive statistical analysis on datasets
- calculate_financial: Perform financial calculations (interest, compound interest, etc.)

Always provide clear explanations, show your work, and ensure accuracy in all calculations.
""",
    tools=[calculate_expression, analyze_statistics, calculate_financial]
)
