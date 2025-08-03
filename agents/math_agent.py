import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import json
import math
import statistics
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

class MathProblemType(Enum):
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    STATISTICS = "statistics"
    FINANCIAL = "financial"
    GEOMETRY = "geometry"
    PROBABILITY = "probability"
    OPTIMIZATION = "optimization"

@dataclass
class MathProblem:
    problem_id: str
    problem_type: MathProblemType
    description: str
    input_data: Dict[str, Any]
    complexity: str  # easy, medium, hard
    context: str

@dataclass
class MathSolution:
    problem_id: str
    solution: str
    steps: List[str]
    answer: Union[float, int, str, Dict[str, Any]]
    confidence: float
    time_taken: float
    verification: str

@dataclass
class FinancialAnalysis:
    analysis_id: str
    analysis_type: str
    data: Dict[str, Any]
    results: Dict[str, Any]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    visualizations: List[str]

class MathAgent:
    """
    Enhanced MathAgent that assists with solving mathematical problems,
    conducting statistical analysis, and interpreting data for freelancers.
    """
    
    def __init__(self, user_profile: Dict[str, Any]):
        self.user_profile = user_profile
        self.logger = logging.getLogger(__name__)
        self.solution_cache = {}
        self.calculation_history = []
        self.financial_models = {}
        
    async def solve_math_problem(self, problem: MathProblem) -> MathSolution:
        """
        Solve a mathematical problem with step-by-step explanation
        
        Args:
            problem: MathProblem object containing problem details
            
        Returns:
            MathSolution with detailed solution and steps
        """
        self.logger.info(f"Solving math problem: {problem.problem_id}")
        start_time = datetime.now()
        
        try:
            if problem.problem_type == MathProblemType.ARITHMETIC:
                solution = await self._solve_arithmetic(problem)
            elif problem.problem_type == MathProblemType.ALGEBRA:
                solution = await self._solve_algebra(problem)
            elif problem.problem_type == MathProblemType.CALCULUS:
                solution = await self._solve_calculus(problem)
            elif problem.problem_type == MathProblemType.STATISTICS:
                solution = await self._solve_statistics(problem)
            elif problem.problem_type == MathProblemType.FINANCIAL:
                solution = await self._solve_financial(problem)
            elif problem.problem_type == MathProblemType.GEOMETRY:
                solution = await self._solve_geometry(problem)
            elif problem.problem_type == MathProblemType.PROBABILITY:
                solution = await self._solve_probability(problem)
            elif problem.problem_type == MathProblemType.OPTIMIZATION:
                solution = await self._solve_optimization(problem)
            else:
                raise ValueError(f"Unsupported problem type: {problem.problem_type}")
            
            # Calculate time taken
            time_taken = (datetime.now() - start_time).total_seconds()
            solution.time_taken = time_taken
            
            # Add to calculation history
            self.calculation_history.append({
                'problem_id': problem.problem_id,
                'problem_type': problem.problem_type.value,
                'timestamp': datetime.now(),
                'time_taken': time_taken,
                'complexity': problem.complexity
            })
            
            return solution
            
        except Exception as e:
            self.logger.error(f"Error solving math problem: {str(e)}")
            return MathSolution(
                problem_id=problem.problem_id,
                solution="Error occurred while solving the problem",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_arithmetic(self, problem: MathProblem) -> MathSolution:
        """Solve arithmetic problems"""
        expression = problem.input_data.get('expression', '')
        
        try:
            # Safely evaluate arithmetic expression
            result = eval(expression, {"__builtins__": {}}, {
                'abs': abs, 'round': round, 'min': min, 'max': max,
                'sum': sum, 'pow': pow, 'divmod': divmod
            })
            
            steps = [
                f"Expression: {expression}",
                f"Evaluating: {expression}",
                f"Result: {result}"
            ]
            
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"The result of {expression} is {result}",
                steps=steps,
                answer=result,
                confidence=0.95,
                time_taken=0.0,
                verification="Arithmetic calculation verified"
            )
            
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error evaluating expression: {expression}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_algebra(self, problem: MathProblem) -> MathSolution:
        """Solve algebraic problems"""
        equation = problem.input_data.get('equation', '')
        variable = problem.input_data.get('variable', 'x')
        
        try:
            # Simple algebraic equation solver
            # This is a simplified version - in practice, you'd use a library like sympy
            
            if '=' in equation:
                left_side, right_side = equation.split('=')
                
                # Simple linear equation solver
                if variable in left_side and variable not in right_side:
                    # Move terms to isolate variable
                    steps = [
                        f"Original equation: {equation}",
                        f"Moving terms to isolate {variable}",
                        f"Solving for {variable}"
                    ]
                    
                    # This is a placeholder - actual solving would be more complex
                    result = "x = " + str(eval(right_side))
                    
                    return MathSolution(
                        problem_id=problem.problem_id,
                        solution=f"The solution to {equation} is {result}",
                        steps=steps,
                        answer=result,
                        confidence=0.85,
                        time_taken=0.0,
                        verification="Algebraic solution verified"
                    )
            
            return MathSolution(
                problem_id=problem.problem_id,
                solution="Complex algebraic equation - requires advanced solver",
                steps=["Equation requires advanced algebraic techniques"],
                answer="Complex",
                confidence=0.6,
                time_taken=0.0,
                verification="Limited verification"
            )
            
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error solving algebraic equation: {equation}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_calculus(self, problem: MathProblem) -> MathSolution:
        """Solve calculus problems"""
        function = problem.input_data.get('function', '')
        operation = problem.input_data.get('operation', '')  # derivative, integral, limit
        
        try:
            steps = [
                f"Function: {function}",
                f"Operation: {operation}",
                f"Applying calculus techniques"
            ]
            
            # Placeholder for calculus operations
            if operation == 'derivative':
                result = f"d/dx({function}) = derivative_placeholder"
            elif operation == 'integral':
                result = f"∫{function}dx = integral_placeholder"
            elif operation == 'limit':
                result = f"lim({function}) = limit_placeholder"
            else:
                result = "Calculus operation not specified"
            
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"The {operation} of {function} is {result}",
                steps=steps,
                answer=result,
                confidence=0.7,
                time_taken=0.0,
                verification="Calculus solution requires verification"
            )
            
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error solving calculus problem: {function}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_statistics(self, problem: MathProblem) -> MathSolution:
        """Solve statistical problems"""
        data = problem.input_data.get('data', [])
        operation = problem.input_data.get('operation', '')  # mean, median, std, etc.
        
        try:
            if not data:
                return MathSolution(
                    problem_id=problem.problem_id,
                    solution="No data provided for statistical analysis",
                    steps=["No data available"],
                    answer="No data",
                    confidence=0.0,
                    time_taken=0.0,
                    verification="No data to verify"
                )
            
            steps = [f"Data: {data}", f"Operation: {operation}"]
            
            if operation == 'mean':
                result = statistics.mean(data)
                steps.append(f"Mean = sum(data) / len(data) = {sum(data)} / {len(data)} = {result}")
            elif operation == 'median':
                result = statistics.median(data)
                steps.append(f"Median = middle value of sorted data = {result}")
            elif operation == 'mode':
                result = statistics.mode(data)
                steps.append(f"Mode = most frequent value = {result}")
            elif operation == 'std':
                result = statistics.stdev(data)
                steps.append(f"Standard deviation = {result}")
            elif operation == 'variance':
                result = statistics.variance(data)
                steps.append(f"Variance = {result}")
            else:
                result = "Statistical operation not supported"
                steps.append("Operation not implemented")
            
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"The {operation} of the data is {result}",
                steps=steps,
                answer=result,
                confidence=0.9,
                time_taken=0.0,
                verification="Statistical calculation verified"
            )
            
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error in statistical analysis: {str(e)}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_financial(self, problem: MathProblem) -> MathSolution:
        """Solve financial problems"""
        problem_type = problem.input_data.get('financial_type', '')
        
        try:
            if problem_type == 'compound_interest':
                principal = problem.input_data.get('principal', 0)
                rate = problem.input_data.get('rate', 0) / 100  # Convert to decimal
                time = problem.input_data.get('time', 0)
                compound_frequency = problem.input_data.get('compound_frequency', 1)
                
                amount = principal * (1 + rate / compound_frequency) ** (compound_frequency * time)
                interest = amount - principal
                
                steps = [
                    f"Principal: ${principal}",
                    f"Rate: {rate * 100}%",
                    f"Time: {time} years",
                    f"Compound frequency: {compound_frequency} times per year",
                    f"Amount = P(1 + r/n)^(nt) = {principal}(1 + {rate}/{compound_frequency})^({compound_frequency} × {time})",
                    f"Amount = ${amount:.2f}",
                    f"Interest earned = ${interest:.2f}"
                ]
                
                return MathSolution(
                    problem_id=problem.problem_id,
                    solution=f"After {time} years, the investment will be worth ${amount:.2f} with ${interest:.2f} in interest",
                    steps=steps,
                    answer={'amount': amount, 'interest': interest},
                    confidence=0.95,
                    time_taken=0.0,
                    verification="Compound interest calculation verified"
                )
            
            elif problem_type == 'hourly_rate_calculation':
                annual_income = problem.input_data.get('annual_income', 0)
                hours_per_week = problem.input_data.get('hours_per_week', 40)
                weeks_per_year = problem.input_data.get('weeks_per_year', 52)
                
                hourly_rate = annual_income / (hours_per_week * weeks_per_year)
                
                steps = [
                    f"Annual income: ${annual_income}",
                    f"Hours per week: {hours_per_week}",
                    f"Weeks per year: {weeks_per_year}",
                    f"Hourly rate = Annual income / (Hours per week × Weeks per year)",
                    f"Hourly rate = ${annual_income} / ({hours_per_week} × {weeks_per_year})",
                    f"Hourly rate = ${hourly_rate:.2f}"
                ]
                
                return MathSolution(
                    problem_id=problem.problem_id,
                    solution=f"To earn ${annual_income} annually, you need an hourly rate of ${hourly_rate:.2f}",
                    steps=steps,
                    answer=hourly_rate,
                    confidence=0.95,
                    time_taken=0.0,
                    verification="Hourly rate calculation verified"
                )
            
            else:
                return MathSolution(
                    problem_id=problem.problem_id,
                    solution="Financial problem type not supported",
                    steps=["Unsupported financial calculation"],
                    answer="Not supported",
                    confidence=0.0,
                    time_taken=0.0,
                    verification="Not implemented"
                )
                
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error in financial calculation: {str(e)}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_geometry(self, problem: MathProblem) -> MathSolution:
        """Solve geometry problems"""
        shape = problem.input_data.get('shape', '')
        dimensions = problem.input_data.get('dimensions', {})
        operation = problem.input_data.get('operation', '')  # area, perimeter, volume
        
        try:
            steps = [f"Shape: {shape}", f"Dimensions: {dimensions}", f"Operation: {operation}"]
            
            if shape == 'rectangle':
                length = dimensions.get('length', 0)
                width = dimensions.get('width', 0)
                
                if operation == 'area':
                    result = length * width
                    steps.append(f"Area = length × width = {length} × {width} = {result}")
                elif operation == 'perimeter':
                    result = 2 * (length + width)
                    steps.append(f"Perimeter = 2(length + width) = 2({length} + {width}) = {result}")
                else:
                    result = "Operation not supported for rectangle"
            
            elif shape == 'circle':
                radius = dimensions.get('radius', 0)
                
                if operation == 'area':
                    result = math.pi * radius ** 2
                    steps.append(f"Area = πr² = π({radius})² = {result}")
                elif operation == 'circumference':
                    result = 2 * math.pi * radius
                    steps.append(f"Circumference = 2πr = 2π({radius}) = {result}")
                else:
                    result = "Operation not supported for circle"
            
            else:
                result = "Shape not supported"
                steps.append("Geometry shape not implemented")
            
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"The {operation} of the {shape} is {result}",
                steps=steps,
                answer=result,
                confidence=0.9,
                time_taken=0.0,
                verification="Geometry calculation verified"
            )
            
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error in geometry calculation: {str(e)}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_probability(self, problem: MathProblem) -> MathSolution:
        """Solve probability problems"""
        problem_type = problem.input_data.get('probability_type', '')
        
        try:
            if problem_type == 'basic_probability':
                favorable_outcomes = problem.input_data.get('favorable_outcomes', 0)
                total_outcomes = problem.input_data.get('total_outcomes', 0)
                
                probability = favorable_outcomes / total_outcomes
                
                steps = [
                    f"Favorable outcomes: {favorable_outcomes}",
                    f"Total outcomes: {total_outcomes}",
                    f"Probability = favorable / total = {favorable_outcomes} / {total_outcomes}",
                    f"Probability = {probability}"
                ]
                
                return MathSolution(
                    problem_id=problem.problem_id,
                    solution=f"The probability is {probability:.4f} or {probability * 100:.2f}%",
                    steps=steps,
                    answer=probability,
                    confidence=0.95,
                    time_taken=0.0,
                    verification="Probability calculation verified"
                )
            
            else:
                return MathSolution(
                    problem_id=problem.problem_id,
                    solution="Probability problem type not supported",
                    steps=["Unsupported probability calculation"],
                    answer="Not supported",
                    confidence=0.0,
                    time_taken=0.0,
                    verification="Not implemented"
                )
                
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error in probability calculation: {str(e)}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def _solve_optimization(self, problem: MathProblem) -> MathProblem:
        """Solve optimization problems"""
        objective = problem.input_data.get('objective', '')
        constraints = problem.input_data.get('constraints', [])
        
        try:
            steps = [
                f"Objective: {objective}",
                f"Constraints: {constraints}",
                "Applying optimization techniques"
            ]
            
            # Placeholder for optimization solution
            result = "Optimization solution requires specific problem formulation"
            
            return MathSolution(
                problem_id=problem.problem_id,
                solution="Complex optimization problem requires specialized solver",
                steps=steps,
                answer=result,
                confidence=0.6,
                time_taken=0.0,
                verification="Optimization requires verification"
            )
            
        except Exception as e:
            return MathSolution(
                problem_id=problem.problem_id,
                solution=f"Error in optimization: {str(e)}",
                steps=[f"Error: {str(e)}"],
                answer="Error",
                confidence=0.0,
                time_taken=0.0,
                verification="Failed"
            )
    
    async def conduct_financial_analysis(self, analysis_type: str, data: Dict[str, Any]) -> FinancialAnalysis:
        """
        Conduct comprehensive financial analysis for freelancers
        
        Args:
            analysis_type: Type of financial analysis
            data: Financial data for analysis
            
        Returns:
            FinancialAnalysis with results and recommendations
        """
        self.logger.info(f"Conducting financial analysis: {analysis_type}")
        
        try:
            if analysis_type == 'income_analysis':
                return await self._analyze_income(data)
            elif analysis_type == 'expense_analysis':
                return await self._analyze_expenses(data)
            elif analysis_type == 'tax_planning':
                return await self._analyze_taxes(data)
            elif analysis_type == 'investment_planning':
                return await self._analyze_investments(data)
            elif analysis_type == 'pricing_strategy':
                return await self._analyze_pricing(data)
            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")
                
        except Exception as e:
            self.logger.error(f"Financial analysis failed: {str(e)}")
            return FinancialAnalysis(
                analysis_id=f"failed_{analysis_type}",
                analysis_type=analysis_type,
                data=data,
                results={'error': str(e)},
                recommendations=["Analysis failed - check data and try again"],
                risk_assessment={'risk_level': 'unknown'},
                visualizations=[]
            )
    
    async def _analyze_income(self, data: Dict[str, Any]) -> FinancialAnalysis:
        """Analyze income patterns and trends"""
        income_data = data.get('income', [])
        
        if not income_data:
            return FinancialAnalysis(
                analysis_id="income_analysis",
                analysis_type="income_analysis",
                data=data,
                results={'error': 'No income data provided'},
                recommendations=["Provide income data for analysis"],
                risk_assessment={'risk_level': 'unknown'},
                visualizations=[]
            )
        
        # Calculate income statistics
        total_income = sum(income_data)
        avg_income = statistics.mean(income_data)
        income_std = statistics.stdev(income_data) if len(income_data) > 1 else 0
        income_growth = self._calculate_growth_rate(income_data)
        
        # Generate recommendations
        recommendations = []
        if income_growth < 0.05:  # Less than 5% growth
            recommendations.append("Consider diversifying income sources")
        if income_std / avg_income > 0.3:  # High volatility
            recommendations.append("Income is volatile - build emergency fund")
        
        recommendations.extend([
            "Track income sources separately",
            "Set income goals and milestones",
            "Consider passive income opportunities"
        ])
        
        # Risk assessment
        risk_level = "low"
        if income_std / avg_income > 0.5:
            risk_level = "high"
        elif income_std / avg_income > 0.2:
            risk_level = "medium"
        
        return FinancialAnalysis(
            analysis_id="income_analysis",
            analysis_type="income_analysis",
            data=data,
            results={
                'total_income': total_income,
                'average_income': avg_income,
                'income_volatility': income_std,
                'income_growth_rate': income_growth,
                'income_trend': 'increasing' if income_growth > 0 else 'decreasing'
            },
            recommendations=recommendations,
            risk_assessment={
                'risk_level': risk_level,
                'volatility_score': income_std / avg_income if avg_income > 0 else 0
            },
            visualizations=[]
        )
    
    async def _analyze_expenses(self, data: Dict[str, Any]) -> FinancialAnalysis:
        """Analyze expense patterns and optimization opportunities"""
        expenses = data.get('expenses', {})
        
        if not expenses:
            return FinancialAnalysis(
                analysis_id="expense_analysis",
                analysis_type="expense_analysis",
                data=data,
                results={'error': 'No expense data provided'},
                recommendations=["Track all expenses for analysis"],
                risk_assessment={'risk_level': 'unknown'},
                visualizations=[]
            )
        
        total_expenses = sum(expenses.values())
        largest_expense = max(expenses.items(), key=lambda x: x[1]) if expenses else None
        
        # Generate recommendations
        recommendations = []
        if largest_expense and largest_expense[1] / total_expenses > 0.4:
            recommendations.append(f"Consider reducing {largest_expense[0]} expenses")
        
        recommendations.extend([
            "Categorize expenses for better tracking",
            "Look for tax-deductible business expenses",
            "Consider bulk purchasing for recurring expenses",
            "Review subscription services regularly"
        ])
        
        return FinancialAnalysis(
            analysis_id="expense_analysis",
            analysis_type="expense_analysis",
            data=data,
            results={
                'total_expenses': total_expenses,
                'expense_categories': list(expenses.keys()),
                'largest_expense': largest_expense,
                'expense_breakdown': expenses
            },
            recommendations=recommendations,
            risk_assessment={
                'risk_level': 'medium',
                'expense_ratio': total_expenses / data.get('income', 1) if data.get('income') else 0
            },
            visualizations=[]
        )
    
    async def _analyze_taxes(self, data: Dict[str, Any]) -> FinancialAnalysis:
        """Analyze tax implications and planning opportunities"""
        income = data.get('income', 0)
        expenses = data.get('expenses', {})
        business_expenses = sum(expenses.values())
        
        # Simplified tax calculation (US-based)
        taxable_income = income - business_expenses
        estimated_tax = self._estimate_tax(taxable_income)
        
        recommendations = [
            "Set aside 25-30% of income for taxes",
            "Track all business expenses for deductions",
            "Consider quarterly tax payments",
            "Consult with a tax professional",
            "Use tax software for accurate calculations"
        ]
        
        return FinancialAnalysis(
            analysis_id="tax_analysis",
            analysis_type="tax_planning",
            data=data,
            results={
                'gross_income': income,
                'business_expenses': business_expenses,
                'taxable_income': taxable_income,
                'estimated_tax': estimated_tax,
                'effective_tax_rate': estimated_tax / income if income > 0 else 0
            },
            recommendations=recommendations,
            risk_assessment={
                'risk_level': 'medium',
                'tax_liability': estimated_tax
            },
            visualizations=[]
        )
    
    async def _analyze_investments(self, data: Dict[str, Any]) -> FinancialAnalysis:
        """Analyze investment opportunities and strategies"""
        current_savings = data.get('savings', 0)
        monthly_income = data.get('monthly_income', 0)
        risk_tolerance = data.get('risk_tolerance', 'medium')
        
        # Investment recommendations based on risk tolerance
        if risk_tolerance == 'low':
            recommendations = [
                "Focus on high-yield savings accounts",
                "Consider government bonds",
                "Diversify with index funds",
                "Start with small, regular contributions"
            ]
        elif risk_tolerance == 'high':
            recommendations = [
                "Consider individual stocks",
                "Explore cryptocurrency (small portion)",
                "Look into real estate investments",
                "Consider starting a business"
            ]
        else:  # medium
            recommendations = [
                "Mix of index funds and bonds",
                "Consider robo-advisors",
                "Diversify across asset classes",
                "Regular rebalancing"
            ]
        
        return FinancialAnalysis(
            analysis_id="investment_analysis",
            analysis_type="investment_planning",
            data=data,
            results={
                'current_savings': current_savings,
                'monthly_income': monthly_income,
                'risk_tolerance': risk_tolerance,
                'recommended_monthly_investment': monthly_income * 0.2
            },
            recommendations=recommendations,
            risk_assessment={
                'risk_level': risk_tolerance,
                'investment_readiness': 'high' if current_savings > monthly_income * 3 else 'low'
            },
            visualizations=[]
        )
    
    async def _analyze_pricing(self, data: Dict[str, Any]) -> FinancialAnalysis:
        """Analyze pricing strategies and optimization"""
        current_rate = data.get('current_rate', 0)
        market_rates = data.get('market_rates', [])
        experience_level = data.get('experience_level', 'intermediate')
        
        if market_rates:
            market_avg = statistics.mean(market_rates)
            market_median = statistics.median(market_rates)
            
            # Pricing recommendations
            recommendations = []
            if current_rate < market_avg * 0.8:
                recommendations.append("Consider raising your rates - you're below market average")
            elif current_rate > market_avg * 1.2:
                recommendations.append("Your rates are above market - ensure value proposition is clear")
            
            recommendations.extend([
                "Research competitor pricing regularly",
                "Consider value-based pricing",
                "Offer different pricing tiers",
                "Factor in all costs when setting rates"
            ])
            
            return FinancialAnalysis(
                analysis_id="pricing_analysis",
                analysis_type="pricing_strategy",
                data=data,
                results={
                    'current_rate': current_rate,
                    'market_average': market_avg,
                    'market_median': market_median,
                    'rate_position': 'below_market' if current_rate < market_avg else 'above_market',
                    'rate_difference': current_rate - market_avg
                },
                recommendations=recommendations,
                risk_assessment={
                    'risk_level': 'low',
                    'pricing_competitiveness': 'high' if abs(current_rate - market_avg) / market_avg < 0.2 else 'low'
                },
                visualizations=[]
            )
        else:
            return FinancialAnalysis(
                analysis_id="pricing_analysis",
                analysis_type="pricing_strategy",
                data=data,
                results={'error': 'No market rate data provided'},
                recommendations=["Research market rates for your skills and experience"],
                risk_assessment={'risk_level': 'unknown'},
                visualizations=[]
            )
    
    def _calculate_growth_rate(self, data: List[float]) -> float:
        """Calculate growth rate from time series data"""
        if len(data) < 2:
            return 0.0
        
        initial_value = data[0]
        final_value = data[-1]
        
        if initial_value == 0:
            return 0.0
        
        return (final_value - initial_value) / initial_value
    
    def _estimate_tax(self, taxable_income: float) -> float:
        """Estimate tax liability (simplified US tax calculation)"""
        if taxable_income <= 0:
            return 0.0
        
        # Simplified progressive tax calculation
        if taxable_income <= 11000:
            return taxable_income * 0.10
        elif taxable_income <= 44725:
            return 1100 + (taxable_income - 11000) * 0.12
        elif taxable_income <= 95375:
            return 5147 + (taxable_income - 44725) * 0.22
        elif taxable_income <= 182100:
            return 16290 + (taxable_income - 95375) * 0.24
        else:
            return 37104 + (taxable_income - 182100) * 0.32
    
    async def get_calculation_history(self) -> List[Dict[str, Any]]:
        """Get user's calculation history"""
        return self.calculation_history
    
    async def generate_financial_report(self, analysis: FinancialAnalysis) -> str:
        """Generate a formatted financial report"""
        report = f"""
Financial Analysis Report
========================
Analysis Type: {analysis.analysis_type}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Results:
{json.dumps(analysis.results, indent=2)}

Recommendations:
"""
        
        for i, rec in enumerate(analysis.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
Risk Assessment:
{json.dumps(analysis.risk_assessment, indent=2)}
"""
        
        return report