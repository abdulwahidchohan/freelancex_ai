import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from core.base_agent import BaseAgent, AgentStatus
import statistics
import math
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

@dataclass
class FinancialData:
    """Structured financial data for analysis"""
    income: List[float]
    expenses: List[float]
    projects: List[Dict[str, Any]]
    tax_rate: float
    currency: str
    period: str  # monthly, quarterly, yearly
    timestamp: str

@dataclass
class StatisticalResult:
    """Structured statistical analysis result"""
    analysis_type: str
    dataset: str
    metrics: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    confidence_level: float
    timestamp: str

class MathAgent(BaseAgent):
    """
    MathAgent for FreelanceX.AI
    Assists with mathematical problems, statistical analysis, financial predictions, and project budgeting
    """
    
    def __init__(self):
        super().__init__("MathAgent", "mathematics")
        
        # Mathematical capabilities
        self.supported_operations = {
            'basic_math': ['addition', 'subtraction', 'multiplication', 'division', 'exponentiation'],
            'statistics': ['mean', 'median', 'mode', 'std_dev', 'variance', 'correlation', 'regression'],
            'financial': ['roi', 'npv', 'irr', 'payback_period', 'compound_interest', 'tax_calculations'],
            'probability': ['distributions', 'hypothesis_testing', 'confidence_intervals', 'bayesian'],
            'optimization': ['linear_programming', 'portfolio_optimization', 'resource_allocation'],
            'forecasting': ['time_series', 'trend_analysis', 'seasonal_decomposition', 'arima']
        }
        
        # Financial analysis configurations
        self.financial_metrics = {
            'freelancer_kpis': [
                'hourly_rate_optimization',
                'project_profitability',
                'income_stability',
                'tax_efficiency',
                'cash_flow_analysis',
                'client_value_analysis'
            ],
            'risk_assessments': [
                'income_volatility',
                'client_concentration_risk',
                'market_dependency',
                'skill_obsolescence_risk'
            ]
        }
        
        # Budgeting templates
        self.budget_templates = {
            'project_budget': {
                'development_hours': 0,
                'hourly_rate': 0,
                'expenses': {
                    'tools': 0,
                    'services': 0,
                    'marketing': 0,
                    'education': 0
                },
                'contingency_percentage': 15,
                'tax_percentage': 25
            },
            'monthly_budget': {
                'fixed_expenses': {
                    'rent': 0,
                    'utilities': 0,
                    'insurance': 0,
                    'subscriptions': 0
                },
                'variable_expenses': {
                    'food': 0,
                    'transportation': 0,
                    'entertainment': 0,
                    'equipment': 0
                },
                'emergency_fund_target': 0.2  # 20% of income
            }
        }
        
        # Analysis cache and metrics
        self.analysis_cache: Dict[str, Any] = {}
        self.calculation_history: List[Dict[str, Any]] = []
        self.performance_analytics = {
            'calculations_performed': 0,
            'financial_analyses': 0,
            'predictions_made': 0,
            'accuracy_scores': [],
            'most_used_functions': {},
            'user_satisfaction_ratings': []
        }
        
        self.logger.info("MathAgent initialized with comprehensive mathematical and financial capabilities")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mathematical and financial analysis tasks"""
        start_time = datetime.now()
        task_type = task.get('type', 'calculate')
        
        try:
            if task_type == 'basic_calculation':
                result = await self._basic_calculation(task.get('expression'), task.get('variables', {}))
            elif task_type == 'statistical_analysis':
                result = await self._statistical_analysis(task.get('data'), task.get('analysis_type'))
            elif task_type == 'financial_analysis':
                result = await self._financial_analysis(task.get('financial_data'), task.get('analysis_goals'))
            elif task_type == 'project_budgeting':
                result = await self._project_budgeting(task.get('project_details'), task.get('constraints'))
            elif task_type == 'income_forecasting':
                result = await self._income_forecasting(task.get('historical_data'), task.get('forecast_period'))
            elif task_type == 'tax_calculations':
                result = await self._tax_calculations(task.get('income_data'), task.get('tax_jurisdiction'))
            elif task_type == 'roi_analysis':
                result = await self._roi_analysis(task.get('investment_data'))
            elif task_type == 'risk_assessment':
                result = await self._risk_assessment(task.get('portfolio_data'), task.get('risk_factors'))
            elif task_type == 'optimization':
                result = await self._optimization_analysis(task.get('optimization_problem'))
            elif task_type == 'market_analysis':
                result = await self._market_analysis(task.get('market_data'), task.get('metrics'))
            else:
                result = {"status": "error", "message": f"Unknown task type: {task_type}"}
                
            # Update performance metrics
            response_time = (datetime.now() - start_time).total_seconds()
            success = result.get('status') == 'success'
            self.update_performance_metrics(success, response_time)
            
            # Store calculation in history
            self._store_calculation_history(task, result, response_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Mathematical task execution failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def self_diagnose(self) -> Dict[str, Any]:
        """Perform self-diagnosis for the MathAgent"""
        diagnosis = {
            "agent_health": "healthy",
            "needs_repair": False,
            "issues": [],
            "recommendations": []
        }
        
        # Check calculation accuracy
        if self.performance_analytics['accuracy_scores']:
            avg_accuracy = sum(self.performance_analytics['accuracy_scores']) / len(self.performance_analytics['accuracy_scores'])
            if avg_accuracy < 0.9:
                diagnosis["needs_repair"] = True
                diagnosis["issues"].append("Mathematical accuracy below threshold")
        
        # Check memory usage
        if len(self.calculation_history) > 1000:
            diagnosis["recommendations"].append("Consider archiving old calculation history")
            
        # Check mathematical libraries
        try:
            import numpy, pandas, scipy, sklearn
            diagnosis["dependencies"] = "all_available"
        except ImportError as e:
            diagnosis["issues"].append(f"Missing mathematical library: {str(e)}")
            diagnosis["agent_health"] = "degraded"
            
        return diagnosis

    async def _basic_calculation(self, expression: str, variables: Dict[str, float] = None) -> Dict[str, Any]:
        """Perform basic mathematical calculations"""
        try:
            # Sanitize expression for security
            allowed_chars = set('0123456789+-*/().x** ')
            if not all(c in allowed_chars or c.isalpha() for c in expression):
                return {"status": "error", "message": "Invalid characters in expression"}
            
            # Replace variables in expression
            if variables:
                for var, value in variables.items():
                    expression = expression.replace(var, str(value))
            
            # Evaluate expression safely
            result = eval(expression)
            
            calculation_data = {
                "expression": expression,
                "result": result,
                "variables": variables or {},
                "calculation_type": "basic_math"
            }
            
            self.performance_analytics['calculations_performed'] += 1
            
            return {
                "status": "success",
                "calculation": calculation_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Calculation error: {str(e)}"}

    async def _statistical_analysis(self, data: List[float], analysis_type: str) -> Dict[str, Any]:
        """Perform statistical analysis on provided data"""
        try:
            if not data or len(data) < 2:
                return {"status": "error", "message": "Insufficient data for statistical analysis"}
            
            np_data = np.array(data)
            analysis_results = {}
            
            if analysis_type == 'descriptive':
                analysis_results = {
                    'count': len(data),
                    'mean': float(np.mean(np_data)),
                    'median': float(np.median(np_data)),
                    'mode': float(statistics.mode(data)) if len(set(data)) < len(data) else None,
                    'std_dev': float(np.std(np_data)),
                    'variance': float(np.var(np_data)),
                    'min': float(np.min(np_data)),
                    'max': float(np.max(np_data)),
                    'range': float(np.max(np_data) - np.min(np_data)),
                    'quartiles': {
                        'q1': float(np.percentile(np_data, 25)),
                        'q2': float(np.percentile(np_data, 50)),
                        'q3': float(np.percentile(np_data, 75))
                    },
                    'skewness': float(stats.skew(np_data)),
                    'kurtosis': float(stats.kurtosis(np_data))
                }
                
            elif analysis_type == 'normality_test':
                shapiro_stat, shapiro_p = stats.shapiro(np_data)
                analysis_results = {
                    'shapiro_statistic': float(shapiro_stat),
                    'shapiro_p_value': float(shapiro_p),
                    'is_normal': shapiro_p > 0.05,
                    'recommendation': 'Use parametric tests' if shapiro_p > 0.05 else 'Use non-parametric tests'
                }
                
            elif analysis_type == 'outlier_detection':
                q1 = np.percentile(np_data, 25)
                q3 = np.percentile(np_data, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = np_data[(np_data < lower_bound) | (np_data > upper_bound)]
                
                analysis_results = {
                    'outliers': outliers.tolist(),
                    'outlier_count': len(outliers),
                    'outlier_percentage': (len(outliers) / len(data)) * 100,
                    'bounds': {'lower': float(lower_bound), 'upper': float(upper_bound)},
                    'clean_data': np_data[(np_data >= lower_bound) & (np_data <= upper_bound)].tolist()
                }
            
            # Generate insights
            insights = self._generate_statistical_insights(analysis_results, analysis_type)
            
            statistical_result = StatisticalResult(
                analysis_type=analysis_type,
                dataset="user_provided",
                metrics=analysis_results,
                insights=insights,
                recommendations=self._generate_statistical_recommendations(analysis_results, analysis_type),
                confidence_level=0.95,
                timestamp=datetime.now().isoformat()
            )
            
            return {
                "status": "success",
                "statistical_analysis": statistical_result.__dict__,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Statistical analysis error: {str(e)}"}

    async def _financial_analysis(self, financial_data: Dict[str, Any], analysis_goals: List[str]) -> Dict[str, Any]:
        """Perform comprehensive financial analysis for freelancers"""
        try:
            results = {}
            
            # Extract financial data
            income = financial_data.get('income', [])
            expenses = financial_data.get('expenses', [])
            projects = financial_data.get('projects', [])
            
            if not income:
                return {"status": "error", "message": "Income data required for financial analysis"}
            
            # Basic financial metrics
            total_income = sum(income)
            total_expenses = sum(expenses) if expenses else 0
            net_income = total_income - total_expenses
            profit_margin = (net_income / total_income) * 100 if total_income > 0 else 0
            
            results['basic_metrics'] = {
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_income': net_income,
                'profit_margin': profit_margin,
                'average_monthly_income': total_income / 12 if len(income) >= 12 else total_income / len(income)
            }
            
            # Income stability analysis
            if len(income) > 1:
                income_std = np.std(income)
                income_cv = (income_std / np.mean(income)) * 100
                results['income_stability'] = {
                    'coefficient_of_variation': income_cv,
                    'stability_rating': self._rate_income_stability(income_cv),
                    'monthly_variance': income_std ** 2
                }
            
            # Project profitability analysis
            if projects:
                project_analysis = self._analyze_project_profitability(projects)
                results['project_analysis'] = project_analysis
            
            # Cash flow analysis
            if income and expenses and len(income) == len(expenses):
                cash_flow = [inc - exp for inc, exp in zip(income, expenses)]
                results['cash_flow'] = {
                    'monthly_cash_flow': cash_flow,
                    'positive_months': sum(1 for cf in cash_flow if cf > 0),
                    'negative_months': sum(1 for cf in cash_flow if cf < 0),
                    'average_monthly_cash_flow': sum(cash_flow) / len(cash_flow)
                }
            
            # Financial health score
            health_score = self._calculate_financial_health_score(results)
            results['financial_health'] = {
                'score': health_score,
                'rating': self._get_health_rating(health_score),
                'improvement_areas': self._identify_improvement_areas(results)
            }
            
            # Generate recommendations
            recommendations = self._generate_financial_recommendations(results, analysis_goals)
            
            self.performance_analytics['financial_analyses'] += 1
            
            return {
                "status": "success",
                "financial_analysis": results,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Financial analysis error: {str(e)}"}

    async def _project_budgeting(self, project_details: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed project budget with risk analysis"""
        try:
            # Extract project parameters
            hours_estimate = project_details.get('estimated_hours', 0)
            hourly_rate = project_details.get('hourly_rate', 0)
            fixed_price = project_details.get('fixed_price', 0)
            complexity = project_details.get('complexity', 'medium')
            
            # Calculate base budget
            if fixed_price:
                base_revenue = fixed_price
                implied_hourly_rate = fixed_price / hours_estimate if hours_estimate > 0 else 0
            else:
                base_revenue = hours_estimate * hourly_rate
                implied_hourly_rate = hourly_rate
            
            # Apply complexity multipliers
            complexity_multipliers = {'low': 0.8, 'medium': 1.0, 'high': 1.3, 'very_high': 1.6}
            complexity_factor = complexity_multipliers.get(complexity, 1.0)
            adjusted_hours = hours_estimate * complexity_factor
            
            # Calculate expenses
            expenses = {
                'tools_and_software': project_details.get('tools_cost', 0),
                'third_party_services': project_details.get('services_cost', 0),
                'marketing_and_communication': base_revenue * 0.05,  # 5% of revenue
                'professional_development': base_revenue * 0.03,  # 3% of revenue
                'equipment_depreciation': project_details.get('equipment_cost', 0) * 0.1
            }
            
            total_expenses = sum(expenses.values())
            
            # Risk and contingency analysis
            risk_factors = {
                'scope_creep': 0.15,  # 15% additional time
                'technical_challenges': 0.10,  # 10% additional time
                'client_delays': 0.08,  # 8% additional time
                'external_dependencies': 0.12  # 12% additional time
            }
            
            contingency_hours = adjusted_hours * sum(risk_factors.values())
            total_estimated_hours = adjusted_hours + contingency_hours
            
            # Budget breakdown
            budget = {
                'revenue': {
                    'base_revenue': base_revenue,
                    'potential_additional_revenue': contingency_hours * implied_hourly_rate
                },
                'expenses': expenses,
                'time_analysis': {
                    'initial_estimate_hours': hours_estimate,
                    'complexity_adjusted_hours': adjusted_hours,
                    'contingency_hours': contingency_hours,
                    'total_estimated_hours': total_estimated_hours,
                    'hourly_rate': implied_hourly_rate
                },
                'profitability': {
                    'gross_profit': base_revenue - total_expenses,
                    'net_profit_margin': ((base_revenue - total_expenses) / base_revenue) * 100 if base_revenue > 0 else 0,
                    'profit_per_hour': (base_revenue - total_expenses) / total_estimated_hours if total_estimated_hours > 0 else 0
                },
                'risk_analysis': {
                    'risk_factors': risk_factors,
                    'probability_on_budget': 0.7,  # 70% chance of staying on budget
                    'worst_case_scenario': {
                        'additional_hours': contingency_hours * 1.5,
                        'additional_costs': total_expenses * 0.2
                    }
                }
            }
            
            # Generate budget recommendations
            recommendations = self._generate_budget_recommendations(budget, constraints)
            
            return {
                "status": "success",
                "project_budget": budget,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Project budgeting error: {str(e)}"}

    async def _income_forecasting(self, historical_data: List[float], forecast_period: int) -> Dict[str, Any]:
        """Forecast future income based on historical data"""
        try:
            if len(historical_data) < 3:
                return {"status": "error", "message": "Insufficient historical data for forecasting"}
            
            # Prepare data for forecasting
            X = np.array(range(len(historical_data))).reshape(-1, 1)
            y = np.array(historical_data)
            
            # Linear regression for trend
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate forecast
            future_X = np.array(range(len(historical_data), len(historical_data) + forecast_period)).reshape(-1, 1)
            forecast = model.predict(future_X)
            
            # Calculate confidence intervals (simplified)
            mse = mean_squared_error(y, model.predict(X))
            std_error = np.sqrt(mse)
            
            forecast_with_confidence = []
            for i, pred in enumerate(forecast):
                confidence_interval = 1.96 * std_error  # 95% CI
                forecast_with_confidence.append({
                    'period': len(historical_data) + i + 1,
                    'predicted_income': float(pred),
                    'lower_bound': float(pred - confidence_interval),
                    'upper_bound': float(pred + confidence_interval)
                })
            
            # Trend analysis
            trend_slope = model.coef_[0]
            trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
            
            # Seasonal analysis (simplified)
            if len(historical_data) >= 12:
                seasonal_factors = self._analyze_seasonality(historical_data)
            else:
                seasonal_factors = None
            
            forecast_results = {
                'forecast_data': forecast_with_confidence,
                'model_performance': {
                    'r_squared': float(r2_score(y, model.predict(X))),
                    'mean_squared_error': float(mse),
                    'trend_slope': float(trend_slope),
                    'trend_direction': trend_direction
                },
                'seasonal_analysis': seasonal_factors,
                'summary_statistics': {
                    'total_forecast_income': float(sum(forecast)),
                    'average_monthly_forecast': float(np.mean(forecast)),
                    'forecast_growth_rate': float((forecast[-1] - historical_data[-1]) / historical_data[-1] * 100) if historical_data[-1] != 0 else 0
                }
            }
            
            self.performance_analytics['predictions_made'] += 1
            
            return {
                "status": "success",
                "income_forecast": forecast_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Income forecasting error: {str(e)}"}

    async def _tax_calculations(self, income_data: Dict[str, Any], tax_jurisdiction: str) -> Dict[str, Any]:
        """Calculate tax obligations for freelancers"""
        try:
            gross_income = income_data.get('gross_income', 0)
            business_expenses = income_data.get('business_expenses', 0)
            deductions = income_data.get('deductions', 0)
            
            # Simplified tax calculation (US-based example)
            taxable_income = max(0, gross_income - business_expenses - deductions)
            
            # Progressive tax brackets (simplified US federal rates)
            tax_brackets = [
                (0, 10275, 0.10),
                (10275, 41775, 0.12),
                (41775, 89450, 0.22),
                (89450, 190750, 0.24),
                (190750, 364200, 0.32),
                (364200, 462550, 0.35),
                (462550, float('inf'), 0.37)
            ]
            
            federal_tax = self._calculate_progressive_tax(taxable_income, tax_brackets)
            
            # Self-employment tax (Social Security + Medicare)
            se_tax_rate = 0.1413  # 14.13% for 2024
            self_employment_tax = gross_income * se_tax_rate
            
            # State tax (estimated average)
            state_tax_rate = income_data.get('state_tax_rate', 0.05)  # 5% default
            state_tax = taxable_income * state_tax_rate
            
            total_tax = federal_tax + self_employment_tax + state_tax
            
            # Tax planning recommendations
            quarterly_payment = total_tax / 4
            effective_tax_rate = (total_tax / gross_income) * 100 if gross_income > 0 else 0
            
            tax_results = {
                'income_breakdown': {
                    'gross_income': gross_income,
                    'business_expenses': business_expenses,
                    'deductions': deductions,
                    'taxable_income': taxable_income
                },
                'tax_calculations': {
                    'federal_income_tax': federal_tax,
                    'self_employment_tax': self_employment_tax,
                    'state_tax': state_tax,
                    'total_tax_owed': total_tax
                },
                'tax_metrics': {
                    'effective_tax_rate': effective_tax_rate,
                    'marginal_tax_rate': self._get_marginal_rate(taxable_income, tax_brackets),
                    'quarterly_payment_estimate': quarterly_payment
                },
                'planning_recommendations': [
                    'Make quarterly estimated tax payments',
                    'Track all business expenses for deductions',
                    'Consider retirement contributions for tax savings',
                    'Maintain separate business and personal accounts'
                ]
            }
            
            return {
                "status": "success",
                "tax_calculations": tax_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Tax calculation error: {str(e)}"}

    async def _roi_analysis(self, investment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze return on investment for various freelancer investments"""
        try:
            investment_type = investment_data.get('type', 'general')
            initial_cost = investment_data.get('initial_cost', 0)
            ongoing_costs = investment_data.get('ongoing_costs', 0)
            benefits = investment_data.get('benefits', [])
            time_period = investment_data.get('time_period_months', 12)
            
            # Calculate total costs and benefits
            total_costs = initial_cost + (ongoing_costs * time_period)
            total_benefits = sum(benefits)
            
            # ROI calculations
            roi_percentage = ((total_benefits - total_costs) / total_costs) * 100 if total_costs > 0 else 0
            payback_period = initial_cost / (total_benefits / time_period) if total_benefits > 0 else float('inf')
            
            # Net Present Value (simplified)
            discount_rate = 0.05  # 5% annual discount rate
            monthly_discount_rate = discount_rate / 12
            
            npv = -initial_cost
            for i, benefit in enumerate(benefits):
                npv += benefit / ((1 + monthly_discount_rate) ** (i + 1))
            
            # Profitability Index
            pi = (npv + initial_cost) / initial_cost if initial_cost > 0 else 0
            
            roi_results = {
                'investment_summary': {
                    'type': investment_type,
                    'initial_cost': initial_cost,
                    'ongoing_monthly_costs': ongoing_costs,
                    'time_period_months': time_period,
                    'total_investment': total_costs
                },
                'returns_analysis': {
                    'total_benefits': total_benefits,
                    'net_profit': total_benefits - total_costs,
                    'roi_percentage': roi_percentage,
                    'payback_period_months': payback_period,
                    'net_present_value': npv,
                    'profitability_index': pi
                },
                'decision_metrics': {
                    'investment_grade': self._grade_investment(roi_percentage, payback_period),
                    'risk_level': investment_data.get('risk_level', 'medium'),
                    'recommendation': self._get_investment_recommendation(roi_percentage, payback_period, npv)
                }
            }
            
            return {
                "status": "success",
                "roi_analysis": roi_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"ROI analysis error: {str(e)}"}

    async def _risk_assessment(self, portfolio_data: Dict[str, Any], risk_factors: List[str]) -> Dict[str, Any]:
        """Assess various risks for freelancer portfolio"""
        try:
            # Income sources analysis
            income_sources = portfolio_data.get('income_sources', [])
            if not income_sources:
                return {"status": "error", "message": "Income sources data required for risk assessment"}
            
            # Client concentration risk
            total_income = sum(source.get('income', 0) for source in income_sources)
            client_concentrations = {}
            for source in income_sources:
                client = source.get('client', 'unknown')
                if client not in client_concentrations:
                    client_concentrations[client] = 0
                client_concentrations[client] += source.get('income', 0)
            
            max_client_percentage = max(client_concentrations.values()) / total_income * 100 if total_income > 0 else 0
            
            # Skill diversification analysis
            skills_used = portfolio_data.get('skills_utilized', [])
            skill_diversity_score = len(set(skills_used)) / len(skills_used) if skills_used else 0
            
            # Market dependency risk
            industries = [source.get('industry', 'general') for source in income_sources]
            industry_diversity = len(set(industries)) / len(industries) if industries else 0
            
            # Income volatility
            income_history = portfolio_data.get('monthly_income_history', [])
            if len(income_history) > 1:
                income_volatility = np.std(income_history) / np.mean(income_history) if np.mean(income_history) > 0 else 0
            else:
                income_volatility = 0
            
            # Risk scores (0-100, where 100 is highest risk)
            risk_scores = {
                'client_concentration_risk': min(100, max_client_percentage),
                'skill_diversification_risk': (1 - skill_diversity_score) * 100,
                'market_dependency_risk': (1 - industry_diversity) * 100,
                'income_volatility_risk': min(100, income_volatility * 100),
                'technology_obsolescence_risk': self._assess_tech_risk(skills_used),
                'competitive_pressure_risk': portfolio_data.get('competitive_pressure', 50)
            }
            
            # Overall risk score
            overall_risk = sum(risk_scores.values()) / len(risk_scores)
            risk_level = self._categorize_risk_level(overall_risk)
            
            # Generate mitigation strategies
            mitigation_strategies = self._generate_risk_mitigation_strategies(risk_scores)
            
            risk_assessment = {
                'risk_scores': risk_scores,
                'overall_risk_score': overall_risk,
                'risk_level': risk_level,
                'detailed_analysis': {
                    'top_client_percentage': max_client_percentage,
                    'number_of_clients': len(client_concentrations),
                    'skill_diversity_index': skill_diversity_score,
                    'industry_diversity_index': industry_diversity,
                    'income_coefficient_of_variation': income_volatility
                },
                'mitigation_strategies': mitigation_strategies,
                'monitoring_recommendations': [
                    'Review client concentration monthly',
                    'Track skill market demand quarterly',
                    'Monitor industry trends continuously',
                    'Maintain 3-6 months emergency fund'
                ]
            }
            
            return {
                "status": "success",
                "risk_assessment": risk_assessment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Risk assessment error: {str(e)}"}

    async def _optimization_analysis(self, optimization_problem: Dict[str, Any]) -> Dict[str, Any]:
        """Solve optimization problems for freelancers"""
        try:
            problem_type = optimization_problem.get('type', 'resource_allocation')
            
            if problem_type == 'hourly_rate_optimization':
                return await self._optimize_hourly_rate(optimization_problem)
            elif problem_type == 'project_selection':
                return await self._optimize_project_selection(optimization_problem)
            elif problem_type == 'time_allocation':
                return await self._optimize_time_allocation(optimization_problem)
            elif problem_type == 'skill_investment':
                return await self._optimize_skill_investment(optimization_problem)
            else:
                return {"status": "error", "message": f"Unsupported optimization type: {problem_type}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Optimization error: {str(e)}"}

    async def _market_analysis(self, market_data: Dict[str, Any], metrics: List[str]) -> Dict[str, Any]:
        """Analyze market conditions and freelancer positioning"""
        try:
            skill_category = market_data.get('skill_category', 'general')
            location = market_data.get('location', 'global')
            experience_level = market_data.get('experience_level', 'intermediate')
            
            # Mock market analysis - in production would use real market data
            market_analysis = {
                'skill_category': skill_category,
                'market_conditions': {
                    'demand_level': 'high',  # high, medium, low
                    'supply_level': 'medium',
                    'market_saturation': 0.6,  # 60% saturated
                    'growth_rate': 0.12,  # 12% annual growth
                    'seasonality_factor': 1.0  # neutral seasonality
                },
                'pricing_analysis': {
                    'average_hourly_rate': 75.0,
                    'rate_range': {'min': 45.0, 'max': 120.0},
                    'rate_percentiles': {
                        '25th': 55.0,
                        '50th': 75.0,
                        '75th': 95.0,
                        '90th': 110.0
                    },
                    'rate_trends': {
                        'yearly_change': 0.08,  # 8% increase year-over-year
                        'seasonal_multiplier': 1.1  # 10% higher in peak season
                    }
                },
                'competitive_landscape': {
                    'total_freelancers': 50000,
                    'active_freelancers': 35000,
                    'top_tier_percentage': 0.15,  # 15% are top performers
                    'average_rating': 4.3,
                    'success_rate': 0.82  # 82% project success rate
                },
                'opportunity_analysis': {
                    'emerging_technologies': ['AI/ML', 'Blockchain', 'IoT'],
                    'declining_skills': ['Legacy systems', 'Outdated frameworks'],
                    'high_demand_niches': ['AI automation', 'Data science', 'Cybersecurity'],
                    'market_gaps': ['AI ethics consulting', 'Quantum computing']
                }
            }
            
            # Generate market insights
            insights = self._generate_market_insights(market_analysis, experience_level)
            
            return {
                "status": "success",
                "market_analysis": market_analysis,
                "insights": insights,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Market analysis error: {str(e)}"}

    # Helper methods
    def _store_calculation_history(self, task: Dict[str, Any], result: Dict[str, Any], response_time: float):
        """Store calculation in history for analysis"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task.get('type'),
            'success': result.get('status') == 'success',
            'response_time': response_time,
            'complexity': len(str(task))  # Simple complexity measure
        }
        
        self.calculation_history.append(history_entry)
        
        # Keep only last 100 calculations to manage memory
        if len(self.calculation_history) > 100:
            self.calculation_history = self.calculation_history[-100:]

    def _generate_statistical_insights(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
        """Generate insights from statistical analysis"""
        insights = []
        
        if analysis_type == 'descriptive':
            mean_val = results.get('mean', 0)
            std_val = results.get('std_dev', 0)
            cv = (std_val / mean_val * 100) if mean_val > 0 else 0
            
            if cv < 15:
                insights.append("Data shows low variability - very consistent performance")
            elif cv > 30:
                insights.append("Data shows high variability - consider investigating causes")
                
            if results.get('skewness', 0) > 1:
                insights.append("Data is positively skewed - most values below average")
            elif results.get('skewness', 0) < -1:
                insights.append("Data is negatively skewed - most values above average")
                
        elif analysis_type == 'outlier_detection':
            outlier_percentage = results.get('outlier_percentage', 0)
            if outlier_percentage > 10:
                insights.append(f"High outlier percentage ({outlier_percentage:.1f}%) - investigate data quality")
            elif outlier_percentage < 2:
                insights.append("Very clean dataset with minimal outliers")
                
        return insights

    def _generate_statistical_recommendations(self, results: Dict[str, Any], analysis_type: str) -> List[str]:
        """Generate recommendations based on statistical analysis"""
        recommendations = []
        
        if analysis_type == 'descriptive':
            cv = (results.get('std_dev', 0) / results.get('mean', 1)) * 100
            if cv > 25:
                recommendations.append("Consider strategies to reduce variability")
                recommendations.append("Investigate factors causing high variance")
                
        elif analysis_type == 'normality_test':
            if not results.get('is_normal', True):
                recommendations.append("Use non-parametric statistical tests")
                recommendations.append("Consider data transformation techniques")
                
        return recommendations

    def _rate_income_stability(self, cv: float) -> str:
        """Rate income stability based on coefficient of variation"""
        if cv < 15:
            return "Very Stable"
        elif cv < 25:
            return "Stable"
        elif cv < 40:
            return "Moderate"
        elif cv < 60:
            return "Unstable"
        else:
            return "Very Unstable"

    def _analyze_project_profitability(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze profitability of individual projects"""
        if not projects:
            return {}
            
        total_revenue = sum(p.get('revenue', 0) for p in projects)
        total_costs = sum(p.get('costs', 0) for p in projects)
        
        project_margins = []
        for project in projects:
            revenue = project.get('revenue', 0)
            costs = project.get('costs', 0)
            margin = ((revenue - costs) / revenue * 100) if revenue > 0 else 0
            project_margins.append(margin)
        
        return {
            'total_projects': len(projects),
            'total_revenue': total_revenue,
            'total_costs': total_costs,
            'overall_margin': ((total_revenue - total_costs) / total_revenue * 100) if total_revenue > 0 else 0,
            'average_project_margin': sum(project_margins) / len(project_margins) if project_margins else 0,
            'best_project_margin': max(project_margins) if project_margins else 0,
            'worst_project_margin': min(project_margins) if project_margins else 0
        }

    def _calculate_financial_health_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall financial health score (0-100)"""
        score = 0
        
        # Profit margin (30 points)
        profit_margin = results.get('basic_metrics', {}).get('profit_margin', 0)
        score += min(30, profit_margin * 1.5)  # Max 30 points for 20% margin
        
        # Income stability (25 points)
        stability = results.get('income_stability', {})
        cv = stability.get('coefficient_of_variation', 100)
        score += max(0, 25 - cv / 2)  # Better score for lower CV
        
        # Cash flow (25 points)
        cash_flow = results.get('cash_flow', {})
        positive_months = cash_flow.get('positive_months', 0)
        total_months = len(cash_flow.get('monthly_cash_flow', [1]))
        if total_months > 0:
            score += (positive_months / total_months) * 25
        
        # Project profitability (20 points)
        project_analysis = results.get('project_analysis', {})
        avg_margin = project_analysis.get('average_project_margin', 0)
        score += min(20, avg_margin / 2)  # Max 20 points for 40% margin
        
        return min(100, score)

    def _get_health_rating(self, score: float) -> str:
        """Convert financial health score to rating"""
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        elif score >= 20:
            return "Poor"
        else:
            return "Critical"

    def _identify_improvement_areas(self, results: Dict[str, Any]) -> List[str]:
        """Identify areas for financial improvement"""
        areas = []
        
        profit_margin = results.get('basic_metrics', {}).get('profit_margin', 0)
        if profit_margin < 10:
            areas.append("Increase profit margins by optimizing pricing or reducing costs")
            
        income_stability = results.get('income_stability', {})
        cv = income_stability.get('coefficient_of_variation', 0)
        if cv > 30:
            areas.append("Improve income stability through diversified client base")
            
        cash_flow = results.get('cash_flow', {})
        negative_months = cash_flow.get('negative_months', 0)
        if negative_months > 2:
            areas.append("Improve cash flow management and build emergency reserves")
            
        return areas

    def _generate_financial_recommendations(self, results: Dict[str, Any], goals: List[str]) -> List[str]:
        """Generate personalized financial recommendations"""
        recommendations = []
        
        # Add standard recommendations based on analysis
        recommendations.extend(self._identify_improvement_areas(results))
        
        # Add goal-specific recommendations
        for goal in goals:
            if goal == 'increase_income':
                recommendations.append("Consider raising rates for new clients")
                recommendations.append("Explore higher-value service offerings")
            elif goal == 'reduce_risk':
                recommendations.append("Diversify client portfolio")
                recommendations.append("Build 6-month emergency fund")
            elif goal == 'optimize_taxes':
                recommendations.append("Maximize business expense deductions")
                recommendations.append("Consider retirement account contributions")
                
        return list(set(recommendations))  # Remove duplicates

    def _generate_budget_recommendations(self, budget: Dict[str, Any], constraints: Dict[str, Any]) -> List[str]:
        """Generate project budget recommendations"""
        recommendations = []
        
        profit_margin = budget.get('profitability', {}).get('net_profit_margin', 0)
        if profit_margin < 20:
            recommendations.append("Consider increasing project rate - profit margin is below 20%")
            
        total_hours = budget.get('time_analysis', {}).get('total_estimated_hours', 0)
        if total_hours > constraints.get('max_hours', float('inf')):
            recommendations.append("Project may exceed available time - consider scope reduction")
            
        recommendations.append("Include detailed scope documentation to prevent scope creep")
        recommendations.append("Request 50% upfront payment to improve cash flow")
        
        return recommendations

    def _analyze_seasonality(self, data: List[float]) -> Dict[str, Any]:
        """Analyze seasonal patterns in income data"""
        if len(data) < 12:
            return None
            
        # Simple seasonal analysis
        monthly_averages = {}
        for i, value in enumerate(data):
            month = (i % 12) + 1
            if month not in monthly_averages:
                monthly_averages[month] = []
            monthly_averages[month].append(value)
        
        seasonal_factors = {}
        overall_mean = np.mean(data)
        
        for month, values in monthly_averages.items():
            month_mean = np.mean(values)
            seasonal_factors[month] = month_mean / overall_mean if overall_mean > 0 else 1
            
        return {
            'seasonal_factors': seasonal_factors,
            'peak_months': [month for month, factor in seasonal_factors.items() if factor > 1.1],
            'low_months': [month for month, factor in seasonal_factors.items() if factor < 0.9]
        }

    def _calculate_progressive_tax(self, income: float, brackets: List[Tuple[float, float, float]]) -> float:
        """Calculate tax using progressive tax brackets"""
        total_tax = 0
        remaining_income = income
        
        for min_income, max_income, rate in brackets:
            if remaining_income <= 0:
                break
                
            taxable_in_bracket = min(remaining_income, max_income - min_income)
            total_tax += taxable_in_bracket * rate
            remaining_income -= taxable_in_bracket
            
        return total_tax

    def _get_marginal_rate(self, income: float, brackets: List[Tuple[float, float, float]]) -> float:
        """Get marginal tax rate for given income"""
        for min_income, max_income, rate in brackets:
            if min_income <= income <= max_income:
                return rate * 100
        return 0

    def _grade_investment(self, roi: float, payback_period: float) -> str:
        """Grade investment based on ROI and payback period"""
        if roi > 50 and payback_period < 6:
            return "A+ (Excellent)"
        elif roi > 25 and payback_period < 12:
            return "A (Very Good)"
        elif roi > 15 and payback_period < 18:
            return "B (Good)"
        elif roi > 5 and payback_period < 24:
            return "C (Fair)"
        else:
            return "D (Poor)"

    def _get_investment_recommendation(self, roi: float, payback_period: float, npv: float) -> str:
        """Get investment recommendation"""
        if roi > 20 and npv > 0 and payback_period < 12:
            return "Strongly Recommended"
        elif roi > 10 and npv > 0:
            return "Recommended"
        elif roi > 0 and npv > 0:
            return "Consider"
        else:
            return "Not Recommended"

    def _assess_tech_risk(self, skills: List[str]) -> float:
        """Assess technology obsolescence risk for skills"""
        # Mock assessment - in production would use real tech trend data
        high_risk_skills = ['flash', 'silverlight', 'perl', 'cobol']
        medium_risk_skills = ['jquery', 'angular.js', 'php']
        
        total_skills = len(skills)
        if total_skills == 0:
            return 50  # Medium risk if no skills data
            
        high_risk_count = sum(1 for skill in skills if skill.lower() in high_risk_skills)
        medium_risk_count = sum(1 for skill in skills if skill.lower() in medium_risk_skills)
        
        risk_score = (high_risk_count * 80 + medium_risk_count * 40) / total_skills
        return min(100, risk_score)

    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize overall risk level"""
        if risk_score < 20:
            return "Low"
        elif risk_score < 40:
            return "Medium-Low"
        elif risk_score < 60:
            return "Medium"
        elif risk_score < 80:
            return "Medium-High"
        else:
            return "High"

    def _generate_risk_mitigation_strategies(self, risk_scores: Dict[str, float]) -> List[str]:
        """Generate risk mitigation strategies"""
        strategies = []
        
        if risk_scores.get('client_concentration_risk', 0) > 50:
            strategies.append("Diversify client base - aim for no single client >30% of income")
            
        if risk_scores.get('skill_diversification_risk', 0) > 60:
            strategies.append("Develop complementary skills to reduce dependency")
            
        if risk_scores.get('technology_obsolescence_risk', 0) > 40:
            strategies.append("Invest in learning emerging technologies")
            
        if risk_scores.get('income_volatility_risk', 0) > 50:
            strategies.append("Establish retainer agreements for stable income")
            
        return strategies

    async def _optimize_hourly_rate(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize hourly rate based on market conditions and goals"""
        current_rate = problem.get('current_rate', 50)
        target_income = problem.get('target_monthly_income', 5000)
        available_hours = problem.get('available_hours_per_month', 160)
        market_rate_range = problem.get('market_rate_range', [40, 80])
        
        # Calculate required rate for target income
        required_rate = target_income / available_hours if available_hours > 0 else 0
        
        # Optimize within market constraints
        min_market_rate, max_market_rate = market_rate_range
        optimal_rate = max(min_market_rate, min(required_rate, max_market_rate))
        
        optimization_result = {
            'current_rate': current_rate,
            'optimal_rate': optimal_rate,
            'rate_change': optimal_rate - current_rate,
            'projected_monthly_income': optimal_rate * available_hours,
            'income_increase': (optimal_rate - current_rate) * available_hours,
            'market_position': self._get_market_position(optimal_rate, market_rate_range),
            'implementation_strategy': [
                'Gradually increase rates for new clients',
                'Demonstrate value through case studies',
                'Offer premium services to justify higher rates'
            ]
        }
        
        return {
            "status": "success",
            "optimization_result": optimization_result,
            "timestamp": datetime.now().isoformat()
        }

    async def _optimize_project_selection(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize project selection based on multiple criteria"""
        projects = problem.get('projects', [])
        constraints = problem.get('constraints', {})
        
        # Score each project
        scored_projects = []
        for project in projects:
            score = self._calculate_project_score(project, constraints)
            scored_projects.append({**project, 'score': score})
        
        # Sort by score
        scored_projects.sort(key=lambda x: x['score'], reverse=True)
        
        # Select projects within constraints
        selected_projects = []
        total_hours = 0
        total_revenue = 0
        max_hours = constraints.get('max_hours', float('inf'))
        
        for project in scored_projects:
            project_hours = project.get('estimated_hours', 0)
            if total_hours + project_hours <= max_hours:
                selected_projects.append(project)
                total_hours += project_hours
                total_revenue += project.get('revenue', 0)
        
        optimization_result = {
            'selected_projects': selected_projects,
            'total_projects': len(selected_projects),
            'total_hours': total_hours,
            'total_revenue': total_revenue,
            'average_hourly_rate': total_revenue / total_hours if total_hours > 0 else 0,
            'utilization_rate': (total_hours / max_hours) * 100 if max_hours != float('inf') else 0
        }
        
        return {
            "status": "success",
            "optimization_result": optimization_result,
            "timestamp": datetime.now().isoformat()
        }

    async def _optimize_time_allocation(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize time allocation across different activities"""
        activities = problem.get('activities', [])
        total_hours = problem.get('total_hours_per_week', 40)
        
        # Simple optimization - allocate time based on value per hour
        for activity in activities:
            value_per_hour = activity.get('value_per_hour', 0)
            min_hours = activity.get('min_hours', 0)
            max_hours = activity.get('max_hours', total_hours)
            activity['efficiency'] = value_per_hour
        
        # Sort by efficiency
        activities.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Allocate time
        remaining_hours = total_hours
        allocation = []
        
        for activity in activities:
            min_hours = activity.get('min_hours', 0)
            max_hours = min(activity.get('max_hours', remaining_hours), remaining_hours)
            allocated_hours = max(min_hours, min(max_hours, remaining_hours))
            
            allocation.append({
                'activity': activity.get('name', 'Unknown'),
                'allocated_hours': allocated_hours,
                'value_per_hour': activity.get('value_per_hour', 0),
                'total_value': allocated_hours * activity.get('value_per_hour', 0)
            })
            
            remaining_hours -= allocated_hours
        
        total_value = sum(item['total_value'] for item in allocation)
        
        optimization_result = {
            'time_allocation': allocation,
            'total_weekly_value': total_value,
            'average_value_per_hour': total_value / total_hours if total_hours > 0 else 0,
            'unallocated_hours': remaining_hours
        }
        
        return {
            "status": "success",
            "optimization_result": optimization_result,
            "timestamp": datetime.now().isoformat()
        }

    async def _optimize_skill_investment(self, problem: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize investment in skill development"""
        skills = problem.get('skills_to_learn', [])
        budget = problem.get('budget', 1000)
        time_budget = problem.get('time_budget_hours', 100)
        
        # Score skills based on multiple factors
        scored_skills = []
        for skill in skills:
            market_demand = skill.get('market_demand_score', 5)  # 1-10
            learning_difficulty = skill.get('difficulty_score', 5)  # 1-10
            cost = skill.get('learning_cost', 100)
            time_required = skill.get('time_required_hours', 20)
            potential_rate_increase = skill.get('potential_rate_increase', 5)
            
            # Calculate ROI score
            roi_score = (market_demand * potential_rate_increase) / (learning_difficulty * 0.1 + cost * 0.001 + time_required * 0.01)
            
            scored_skills.append({
                **skill,
                'roi_score': roi_score
            })
        
        # Sort by ROI score
        scored_skills.sort(key=lambda x: x['roi_score'], reverse=True)
        
        # Select skills within budget constraints
        selected_skills = []
        total_cost = 0
        total_time = 0
        
        for skill in scored_skills:
            cost = skill.get('learning_cost', 0)
            time = skill.get('time_required_hours', 0)
            
            if total_cost + cost <= budget and total_time + time <= time_budget:
                selected_skills.append(skill)
                total_cost += cost
                total_time += time
        
        optimization_result = {
            'recommended_skills': selected_skills,
            'total_investment_cost': total_cost,
            'total_time_investment': total_time,
            'budget_utilization': (total_cost / budget) * 100 if budget > 0 else 0,
            'time_utilization': (total_time / time_budget) * 100 if time_budget > 0 else 0,
            'expected_roi': sum(skill.get('roi_score', 0) for skill in selected_skills)
        }
        
        return {
            "status": "success",
            "optimization_result": optimization_result,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_project_score(self, project: Dict[str, Any], constraints: Dict[str, Any]) -> float:
        """Calculate project score for selection optimization"""
        revenue = project.get('revenue', 0)
        hours = project.get('estimated_hours', 1)
        complexity = project.get('complexity_score', 5)  # 1-10
        client_rating = project.get('client_rating', 3)  # 1-5
        strategic_value = project.get('strategic_value', 3)  # 1-5
        
        hourly_rate = revenue / hours if hours > 0 else 0
        
        # Weighted scoring
        score = (
            hourly_rate * 0.4 +  # 40% weight on hourly rate
            (11 - complexity) * 10 * 0.2 +  # 20% weight on simplicity
            client_rating * 20 * 0.2 +  # 20% weight on client quality
            strategic_value * 20 * 0.2  # 20% weight on strategic value
        )
        
        return score

    def _get_market_position(self, rate: float, market_range: List[float]) -> str:
        """Determine market position based on rate"""
        min_rate, max_rate = market_range
        position = (rate - min_rate) / (max_rate - min_rate) if max_rate > min_rate else 0.5
        
        if position < 0.25:
            return "Budget/Entry Level"
        elif position < 0.5:
            return "Below Market Average"
        elif position < 0.75:
            return "Above Market Average"
        else:
            return "Premium/Expert Level"

    def _generate_market_insights(self, analysis: Dict[str, Any], experience_level: str) -> List[str]:
        """Generate market insights based on analysis"""
        insights = []
        
        demand = analysis.get('market_conditions', {}).get('demand_level', 'medium')
        supply = analysis.get('market_conditions', {}).get('supply_level', 'medium')
        
        if demand == 'high' and supply == 'low':
            insights.append("Excellent market conditions - high demand with low supply")
        elif demand == 'low' and supply == 'high':
            insights.append("Challenging market - consider specialization or skill diversification")
            
        growth_rate = analysis.get('market_conditions', {}).get('growth_rate', 0)
        if growth_rate > 0.1:
            insights.append(f"Strong market growth at {growth_rate*100:.1f}% annually")
            
        avg_rate = analysis.get('pricing_analysis', {}).get('average_hourly_rate', 0)
        if experience_level == 'expert' and avg_rate > 100:
            insights.append("Consider premium positioning - market supports high-value services")
            
        return insights