import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import math
import statistics
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import re
import sympy
from sympy import symbols, solve, integrate, diff, limit, simplify
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

@dataclass
class CalculationResult:
    """Data class for calculation results"""
    operation: str
    input_data: Dict[str, Any]
    result: Any
    formula_used: str
    steps: List[str]
    confidence: float
    timestamp: datetime
    metadata: Dict[str, Any] = None

@dataclass
class FinancialProjection:
    """Data class for financial projections"""
    period: str
    revenue: float
    expenses: float
    profit: float
    profit_margin: float
    cumulative_profit: float
    assumptions: Dict[str, Any]

@dataclass
class StatisticalAnalysis:
    """Data class for statistical analysis results"""
    dataset_name: str
    sample_size: int
    mean: float
    median: float
    std_deviation: float
    variance: float
    min_value: float
    max_value: float
    quartiles: Dict[str, float]
    outliers: List[float]
    distribution_type: str
    confidence_intervals: Dict[str, List[float]]

class MathAgent:
    """
    Enhanced MathAgent for FreelanceX.AI
    
    Primary Role: Assists with solving mathematical problems, conducting statistical analysis, 
    and interpreting data.
    
    Features: Real-time formula solving, statistical models, financial predictions.
    Mode of Action: Helps freelancers with financial planning, project budgeting, and more.
    """
    
    def __init__(self, user_profile: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.user_profile = user_profile or {}
        
        # Mathematical operation capabilities
        self.capabilities = {
            'basic_math': True,
            'algebra': True,
            'calculus': True,
            'statistics': True,
            'financial_calculations': True,
            'data_analysis': True,
            'visualization': True,
            'optimization': True
        }
        
        # Financial calculation settings
        self.financial_settings = {
            'tax_rate': 0.25,  # Default 25% tax rate
            'currency': 'USD',
            'decimal_places': 2,
            'inflation_rate': 0.02,  # 2% annual inflation
            'discount_rate': 0.05,  # 5% discount rate for NPV calculations
            'working_hours_per_year': 2080,  # 40 hours/week * 52 weeks
            'business_expenses_rate': 0.15  # 15% of revenue for business expenses
        }
        
        # Statistical analysis settings
        self.statistical_settings = {
            'confidence_level': 0.95,  # 95% confidence interval
            'outlier_threshold': 1.5,  # IQR multiplier for outlier detection
            'min_sample_size': 5,
            'max_sample_size': 10000,
            'default_distribution': 'normal'
        }
        
        # Calculation history and memory
        self.calculation_history = {
            'recent_calculations': [],
            'frequent_operations': {},
            'user_preferences': {},
            'error_log': [],
            'performance_metrics': {}
        }
        
        # Financial templates and models
        self.financial_templates = {
            'freelancer_budget': {
                'income_sources': ['client_projects', 'passive_income', 'consulting'],
                'expense_categories': ['software_tools', 'marketing', 'office_supplies', 'insurance'],
                'tax_categories': ['income_tax', 'self_employment_tax', 'state_tax']
            },
            'project_roi': {
                'metrics': ['roi', 'payback_period', 'npv', 'irr'],
                'timeframes': ['monthly', 'quarterly', 'yearly']
            },
            'pricing_model': {
                'strategies': ['hourly_rate', 'project_based', 'value_based', 'retainer'],
                'factors': ['experience_level', 'market_demand', 'project_complexity']
            }
        }

    def set_user_profile(self, profile: Dict[str, Any]):
        """Update user profile for personalized calculations"""
        self.user_profile = profile
        self.logger.info(f"Updated user profile for {profile.get('name', 'Unknown')}")
        
        # Update financial settings based on profile
        if 'tax_rate' in profile:
            self.financial_settings['tax_rate'] = profile['tax_rate']
        if 'currency' in profile:
            self.financial_settings['currency'] = profile['currency']
        if 'working_hours_per_year' in profile:
            self.financial_settings['working_hours_per_year'] = profile['working_hours_per_year']

    async def solve_equation(self, equation: str, variables: Dict[str, float] = None) -> CalculationResult:
        """
        Solve mathematical equations using symbolic computation
        
        Args:
            equation: Mathematical equation as string
            variables: Dictionary of variable values (optional)
            
        Returns:
            CalculationResult with solution and steps
        """
        self.logger.info(f"Solving equation: {equation}")
        
        try:
            # Parse equation and extract variables
            parsed_eq = self._parse_equation(equation)
            
            if variables:
                # Substitute known values
                for var, value in variables.items():
                    parsed_eq = parsed_eq.subs(symbols(var), value)
            
            # Solve the equation
            solution = solve(parsed_eq)
            
            # Generate steps
            steps = [
                f"Original equation: {equation}",
                f"Parsed equation: {parsed_eq}",
                f"Solution: {solution}"
            ]
            
            result = CalculationResult(
                operation="equation_solving",
                input_data={'equation': equation, 'variables': variables},
                result=solution,
                formula_used=str(parsed_eq),
                steps=steps,
                confidence=0.95,
                timestamp=datetime.now()
            )
            
            self._update_calculation_history(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error solving equation: {e}")
            raise ValueError(f"Could not solve equation: {e}")

    def _parse_equation(self, equation: str) -> sympy.Expr:
        """Parse mathematical equation string to SymPy expression"""
        # Clean up the equation
        equation = equation.replace('^', '**')
        equation = equation.replace('×', '*')
        equation = equation.replace('÷', '/')
        
        # Extract variables
        variables = re.findall(r'\b[a-zA-Z]\b', equation)
        sym_vars = symbols(' '.join(variables))
        
        # Parse the expression
        return sympy.sympify(equation)

    async def calculate_financial_metrics(self, financial_data: Dict[str, Any], 
                                        metric_type: str) -> CalculationResult:
        """
        Calculate financial metrics for freelancers
        
        Args:
            financial_data: Dictionary containing financial data
            metric_type: Type of financial calculation
            
        Returns:
            CalculationResult with financial analysis
        """
        self.logger.info(f"Calculating financial metrics: {metric_type}")
        
        try:
            if metric_type == 'hourly_rate':
                result = self._calculate_hourly_rate(financial_data)
            elif metric_type == 'project_pricing':
                result = self._calculate_project_pricing(financial_data)
            elif metric_type == 'roi_analysis':
                result = self._calculate_roi_analysis(financial_data)
            elif metric_type == 'tax_estimation':
                result = self._calculate_tax_estimation(financial_data)
            elif metric_type == 'profit_margin':
                result = self._calculate_profit_margin(financial_data)
            elif metric_type == 'break_even':
                result = self._calculate_break_even(financial_data)
            else:
                raise ValueError(f"Unsupported financial metric: {metric_type}")
            
            self._update_calculation_history(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating financial metrics: {e}")
            raise ValueError(f"Could not calculate {metric_type}: {e}")

    def _calculate_hourly_rate(self, data: Dict[str, Any]) -> CalculationResult:
        """Calculate optimal hourly rate based on expenses and desired income"""
        desired_annual_income = data.get('desired_annual_income', 100000)
        annual_expenses = data.get('annual_expenses', 20000)
        billable_hours = data.get('billable_hours', 1600)  # 80% of working hours
        tax_rate = data.get('tax_rate', self.financial_settings['tax_rate'])
        
        # Calculate required gross income
        required_gross = (desired_annual_income + annual_expenses) / (1 - tax_rate)
        
        # Calculate hourly rate
        hourly_rate = required_gross / billable_hours
        
        steps = [
            f"Desired annual income: ${desired_annual_income:,.2f}",
            f"Annual expenses: ${annual_expenses:,.2f}",
            f"Tax rate: {tax_rate:.1%}",
            f"Required gross income: ${required_gross:,.2f}",
            f"Billable hours per year: {billable_hours}",
            f"Recommended hourly rate: ${hourly_rate:.2f}"
        ]
        
        return CalculationResult(
            operation="hourly_rate_calculation",
            input_data=data,
            result={'hourly_rate': hourly_rate, 'required_gross': required_gross},
            formula_used="hourly_rate = (desired_income + expenses) / ((1 - tax_rate) * billable_hours)",
            steps=steps,
            confidence=0.9,
            timestamp=datetime.now()
        )

    def _calculate_project_pricing(self, data: Dict[str, Any]) -> CalculationResult:
        """Calculate project pricing based on various factors"""
        estimated_hours = data.get('estimated_hours', 40)
        hourly_rate = data.get('hourly_rate', 100)
        complexity_multiplier = data.get('complexity_multiplier', 1.2)
        risk_factor = data.get('risk_factor', 1.1)
        market_demand = data.get('market_demand', 1.0)
        
        # Calculate base price
        base_price = estimated_hours * hourly_rate
        
        # Apply adjustments
        adjusted_price = base_price * complexity_multiplier * risk_factor * market_demand
        
        # Calculate profit margin
        profit_margin = (adjusted_price - base_price) / adjusted_price
        
        steps = [
            f"Estimated hours: {estimated_hours}",
            f"Hourly rate: ${hourly_rate}",
            f"Base price: ${base_price:,.2f}",
            f"Complexity multiplier: {complexity_multiplier}",
            f"Risk factor: {risk_factor}",
            f"Market demand factor: {market_demand}",
            f"Adjusted price: ${adjusted_price:,.2f}",
            f"Profit margin: {profit_margin:.1%}"
        ]
        
        return CalculationResult(
            operation="project_pricing",
            input_data=data,
            result={'adjusted_price': adjusted_price, 'profit_margin': profit_margin},
            formula_used="adjusted_price = base_price * complexity * risk * demand",
            steps=steps,
            confidence=0.85,
            timestamp=datetime.now()
        )

    def _calculate_roi_analysis(self, data: Dict[str, Any]) -> CalculationResult:
        """Calculate ROI for investments and projects"""
        initial_investment = data.get('initial_investment', 10000)
        returns = data.get('returns', [])
        time_period = data.get('time_period', 12)  # months
        
        if not returns:
            # Generate sample returns if not provided
            returns = [initial_investment * 0.1] * time_period
        
        # Calculate total return
        total_return = sum(returns)
        
        # Calculate ROI
        roi = (total_return - initial_investment) / initial_investment
        
        # Calculate annualized ROI
        annualized_roi = ((1 + roi) ** (12 / time_period)) - 1
        
        # Calculate payback period
        cumulative_return = 0
        payback_period = None
        for i, ret in enumerate(returns):
            cumulative_return += ret
            if cumulative_return >= initial_investment:
                payback_period = i + 1
                break
        
        steps = [
            f"Initial investment: ${initial_investment:,.2f}",
            f"Total returns: ${total_return:,.2f}",
            f"ROI: {roi:.1%}",
            f"Annualized ROI: {annualized_roi:.1%}",
            f"Payback period: {payback_period} months" if payback_period else "Payback period: Not reached"
        ]
        
        return CalculationResult(
            operation="roi_analysis",
            input_data=data,
            result={
                'roi': roi,
                'annualized_roi': annualized_roi,
                'payback_period': payback_period,
                'total_return': total_return
            },
            formula_used="ROI = (total_return - initial_investment) / initial_investment",
            steps=steps,
            confidence=0.9,
            timestamp=datetime.now()
        )

    def _calculate_tax_estimation(self, data: Dict[str, Any]) -> CalculationResult:
        """Estimate taxes for freelancers"""
        gross_income = data.get('gross_income', 100000)
        business_expenses = data.get('business_expenses', 15000)
        tax_rate = data.get('tax_rate', self.financial_settings['tax_rate'])
        self_employment_tax_rate = data.get('self_employment_tax_rate', 0.153)  # 15.3%
        
        # Calculate net business income
        net_business_income = gross_income - business_expenses
        
        # Calculate income tax
        income_tax = net_business_income * tax_rate
        
        # Calculate self-employment tax
        self_employment_tax = net_business_income * self_employment_tax_rate
        
        # Calculate total tax
        total_tax = income_tax + self_employment_tax
        
        # Calculate effective tax rate
        effective_tax_rate = total_tax / gross_income
        
        steps = [
            f"Gross income: ${gross_income:,.2f}",
            f"Business expenses: ${business_expenses:,.2f}",
            f"Net business income: ${net_business_income:,.2f}",
            f"Income tax: ${income_tax:,.2f}",
            f"Self-employment tax: ${self_employment_tax:,.2f}",
            f"Total tax: ${total_tax:,.2f}",
            f"Effective tax rate: {effective_tax_rate:.1%}"
        ]
        
        return CalculationResult(
            operation="tax_estimation",
            input_data=data,
            result={
                'total_tax': total_tax,
                'effective_tax_rate': effective_tax_rate,
                'income_tax': income_tax,
                'self_employment_tax': self_employment_tax
            },
            formula_used="total_tax = income_tax + self_employment_tax",
            steps=steps,
            confidence=0.8,
            timestamp=datetime.now()
        )

    def _calculate_profit_margin(self, data: Dict[str, Any]) -> CalculationResult:
        """Calculate profit margin for projects or business"""
        revenue = data.get('revenue', 10000)
        costs = data.get('costs', 7000)
        
        # Calculate profit
        profit = revenue - costs
        
        # Calculate profit margin
        profit_margin = profit / revenue
        
        # Calculate markup
        markup = profit / costs
        
        steps = [
            f"Revenue: ${revenue:,.2f}",
            f"Costs: ${costs:,.2f}",
            f"Profit: ${profit:,.2f}",
            f"Profit margin: {profit_margin:.1%}",
            f"Markup: {markup:.1%}"
        ]
        
        return CalculationResult(
            operation="profit_margin",
            input_data=data,
            result={'profit_margin': profit_margin, 'markup': markup, 'profit': profit},
            formula_used="profit_margin = (revenue - costs) / revenue",
            steps=steps,
            confidence=0.95,
            timestamp=datetime.now()
        )

    def _calculate_break_even(self, data: Dict[str, Any]) -> CalculationResult:
        """Calculate break-even point"""
        fixed_costs = data.get('fixed_costs', 5000)
        variable_cost_per_unit = data.get('variable_cost_per_unit', 50)
        price_per_unit = data.get('price_per_unit', 100)
        
        # Calculate contribution margin
        contribution_margin = price_per_unit - variable_cost_per_unit
        
        # Calculate break-even quantity
        break_even_quantity = fixed_costs / contribution_margin
        
        # Calculate break-even revenue
        break_even_revenue = break_even_quantity * price_per_unit
        
        steps = [
            f"Fixed costs: ${fixed_costs:,.2f}",
            f"Variable cost per unit: ${variable_cost_per_unit}",
            f"Price per unit: ${price_per_unit}",
            f"Contribution margin: ${contribution_margin}",
            f"Break-even quantity: {break_even_quantity:.0f} units",
            f"Break-even revenue: ${break_even_revenue:,.2f}"
        ]
        
        return CalculationResult(
            operation="break_even_analysis",
            input_data=data,
            result={
                'break_even_quantity': break_even_quantity,
                'break_even_revenue': break_even_revenue,
                'contribution_margin': contribution_margin
            },
            formula_used="break_even_quantity = fixed_costs / (price_per_unit - variable_cost_per_unit)",
            steps=steps,
            confidence=0.95,
            timestamp=datetime.now()
        )

    async def perform_statistical_analysis(self, data: List[float], 
                                         analysis_type: str = 'descriptive') -> StatisticalAnalysis:
        """
        Perform statistical analysis on dataset
        
        Args:
            data: List of numerical data
            analysis_type: Type of statistical analysis
            
        Returns:
            StatisticalAnalysis object with results
        """
        self.logger.info(f"Performing {analysis_type} statistical analysis on {len(data)} data points")
        
        try:
            if len(data) < self.statistical_settings['min_sample_size']:
                raise ValueError(f"Sample size too small. Minimum required: {self.statistical_settings['min_sample_size']}")
            
            # Convert to numpy array for calculations
            data_array = np.array(data)
            
            # Calculate basic statistics
            mean = np.mean(data_array)
            median = np.median(data_array)
            std_dev = np.std(data_array, ddof=1)
            variance = np.var(data_array, ddof=1)
            min_val = np.min(data_array)
            max_val = np.max(data_array)
            
            # Calculate quartiles
            q1, q2, q3 = np.percentile(data_array, [25, 50, 75])
            quartiles = {'Q1': q1, 'Q2': q2, 'Q3': q3}
            
            # Detect outliers using IQR method
            iqr = q3 - q1
            lower_bound = q1 - (self.statistical_settings['outlier_threshold'] * iqr)
            upper_bound = q3 + (self.statistical_settings['outlier_threshold'] * iqr)
            outliers = data_array[(data_array < lower_bound) | (data_array > upper_bound)].tolist()
            
            # Determine distribution type
            distribution_type = self._determine_distribution(data_array)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(data_array)
            
            result = StatisticalAnalysis(
                dataset_name=f"Dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sample_size=len(data_array),
                mean=mean,
                median=median,
                std_deviation=std_dev,
                variance=variance,
                min_value=min_val,
                max_value=max_val,
                quartiles=quartiles,
                outliers=outliers,
                distribution_type=distribution_type,
                confidence_intervals=confidence_intervals
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error performing statistical analysis: {e}")
            raise ValueError(f"Could not perform statistical analysis: {e}")

    def _determine_distribution(self, data: np.ndarray) -> str:
        """Determine the type of distribution for the data"""
        # Simple distribution detection based on skewness and kurtosis
        skewness = self._calculate_skewness(data)
        kurtosis = self._calculate_kurtosis(data)
        
        if abs(skewness) < 0.5 and abs(kurtosis - 3) < 1:
            return 'normal'
        elif skewness > 1:
            return 'right_skewed'
        elif skewness < -1:
            return 'left_skewed'
        else:
            return 'unknown'

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of the data"""
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        
        skewness = (n / ((n-1) * (n-2))) * np.sum(((data - mean) / std) ** 3)
        return skewness

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of the data"""
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        
        kurtosis = (n * (n+1) / ((n-1) * (n-2) * (n-3))) * np.sum(((data - mean) / std) ** 4) - (3 * (n-1)**2 / ((n-2) * (n-3)))
        return kurtosis

    def _calculate_confidence_intervals(self, data: np.ndarray) -> Dict[str, List[float]]:
        """Calculate confidence intervals for the mean"""
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        n = len(data)
        
        # Z-scores for different confidence levels
        z_scores = {
            '90%': 1.645,
            '95%': 1.96,
            '99%': 2.576
        }
        
        confidence_intervals = {}
        for level, z_score in z_scores.items():
            margin_of_error = z_score * (std / np.sqrt(n))
            confidence_intervals[level] = [mean - margin_of_error, mean + margin_of_error]
        
        return confidence_intervals

    async def create_financial_projection(self, current_data: Dict[str, Any], 
                                        projection_periods: int = 12) -> List[FinancialProjection]:
        """
        Create financial projections for freelancers
        
        Args:
            current_data: Current financial data
            projection_periods: Number of periods to project
            
        Returns:
            List of FinancialProjection objects
        """
        self.logger.info(f"Creating financial projections for {projection_periods} periods")
        
        projections = []
        current_revenue = current_data.get('current_revenue', 10000)
        current_expenses = current_data.get('current_expenses', 7000)
        growth_rate = current_data.get('growth_rate', 0.05)  # 5% monthly growth
        inflation_rate = current_data.get('inflation_rate', self.financial_settings['inflation_rate'])
        
        cumulative_profit = 0
        
        for period in range(1, projection_periods + 1):
            # Project revenue with growth
            revenue = current_revenue * ((1 + growth_rate) ** period)
            
            # Project expenses with inflation
            expenses = current_expenses * ((1 + inflation_rate/12) ** period)
            
            # Calculate profit
            profit = revenue - expenses
            cumulative_profit += profit
            
            # Calculate profit margin
            profit_margin = profit / revenue if revenue > 0 else 0
            
            projection = FinancialProjection(
                period=f"Month {period}",
                revenue=revenue,
                expenses=expenses,
                profit=profit,
                profit_margin=profit_margin,
                cumulative_profit=cumulative_profit,
                assumptions={
                    'growth_rate': growth_rate,
                    'inflation_rate': inflation_rate,
                    'base_revenue': current_revenue,
                    'base_expenses': current_expenses
                }
            )
            
            projections.append(projection)
        
        return projections

    def generate_visualization(self, data: Union[List[float], Dict[str, Any]], 
                             chart_type: str = 'histogram') -> str:
        """
        Generate data visualizations
        
        Args:
            data: Data to visualize
            chart_type: Type of chart to generate
            
        Returns:
            Base64 encoded image string
        """
        try:
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'histogram' and isinstance(data, list):
                plt.hist(data, bins=20, alpha=0.7, edgecolor='black')
                plt.title('Data Distribution')
                plt.xlabel('Values')
                plt.ylabel('Frequency')
                
            elif chart_type == 'line' and isinstance(data, dict):
                periods = list(data.keys())
                values = list(data.values())
                plt.plot(periods, values, marker='o')
                plt.title('Time Series Data')
                plt.xlabel('Period')
                plt.ylabel('Value')
                plt.xticks(rotation=45)
                
            elif chart_type == 'bar' and isinstance(data, dict):
                categories = list(data.keys())
                values = list(data.values())
                plt.bar(categories, values)
                plt.title('Categorical Data')
                plt.xlabel('Categories')
                plt.ylabel('Values')
                plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Save to bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return image_base64
            
        except Exception as e:
            self.logger.error(f"Error generating visualization: {e}")
            raise ValueError(f"Could not generate {chart_type} chart: {e}")

    def _update_calculation_history(self, result: CalculationResult):
        """Update calculation history with new result"""
        self.calculation_history['recent_calculations'].append(result)
        
        # Keep only last 100 calculations
        if len(self.calculation_history['recent_calculations']) > 100:
            self.calculation_history['recent_calculations'] = \
                self.calculation_history['recent_calculations'][-100:]
        
        # Update frequent operations
        operation = result.operation
        if operation not in self.calculation_history['frequent_operations']:
            self.calculation_history['frequent_operations'][operation] = 0
        self.calculation_history['frequent_operations'][operation] += 1

    def get_calculation_history(self) -> Dict[str, Any]:
        """Get calculation history and statistics"""
        return {
            'total_calculations': len(self.calculation_history['recent_calculations']),
            'frequent_operations': self.calculation_history['frequent_operations'],
            'recent_calculations': [
                {
                    'operation': calc.operation,
                    'timestamp': calc.timestamp,
                    'confidence': calc.confidence
                }
                for calc in self.calculation_history['recent_calculations'][-10:]
            ],
            'error_count': len(self.calculation_history['error_log'])
        }

    def export_calculations_to_csv(self, calculations: List[CalculationResult], 
                                  filename: str = None) -> str:
        """Export calculations to CSV format"""
        import csv
        from io import StringIO
        
        if not filename:
            filename = f"calculations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Operation', 'Result', 'Formula Used', 'Confidence', 'Timestamp'
        ])
        
        # Write data
        for calc in calculations:
            writer.writerow([
                calc.operation,
                str(calc.result),
                calc.formula_used,
                calc.confidence,
                calc.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Save to file
        with open(filename, 'w', newline='') as f:
            f.write(output.getvalue())
        
        return filename