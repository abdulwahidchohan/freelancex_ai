"""FreelanceX.AI Math Agent - OpenAI Agents SDK Implementation
Specialized agent for financial calculations, budgeting, and mathematical analysis
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
import logging
from typing import Dict, Any, List, Optional
import math
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class ProjectBudgetRequest(BaseModel):
    hourly_rate: float = Field(..., description="Your hourly rate in USD")
    estimated_hours: int = Field(..., description="Estimated hours for the project")
    expenses: float = Field(0, description="Additional expenses (materials, tools, etc.)")
    profit_margin: float = Field(0.2, description="Desired profit margin as decimal (default 0.2 = 20%)")
    project_type: Optional[str] = Field(None, description="Type of project (e.g., web development, design, writing)")
    complexity_level: Optional[str] = Field(None, description="Project complexity (low, medium, high)")

class ProjectBudgetResponse(BaseModel):
    base_cost: float = Field(..., description="Base cost calculation (hourly rate × estimated hours)")
    expenses: float = Field(..., description="Additional expenses")
    profit: float = Field(..., description="Profit amount based on margin")
    total_cost: float = Field(..., description="Total project cost")
    effective_rate: float = Field(..., description="Effective hourly rate")
    roi: float = Field(..., description="Return on investment percentage")
    recommendations: List[str] = Field(..., description="Budget recommendations")
    formatted_breakdown: str = Field(..., description="Formatted budget breakdown for display")

@tool
def calculate_project_budget(request: ProjectBudgetRequest) -> ProjectBudgetResponse:
    """Calculate project budget with various factors including complexity adjustments
    
    Args:
        request: Project budget calculation request with all necessary parameters
    
    Returns:
        Structured project budget response with detailed breakdown
    """
    try:
        # Extract values from request
        hourly_rate = request.hourly_rate
        estimated_hours = request.estimated_hours
        expenses = request.expenses
        profit_margin = request.profit_margin
        project_type = request.project_type
        complexity_level = request.complexity_level
        
        # Apply complexity adjustments if provided
        complexity_multiplier = 1.0
        if complexity_level:
            if complexity_level.lower() == "high":
                complexity_multiplier = 1.3
            elif complexity_level.lower() == "medium":
                complexity_multiplier = 1.15
            elif complexity_level.lower() == "low":
                complexity_multiplier = 1.0
        
        # Calculate base cost with complexity adjustment
        base_cost = hourly_rate * estimated_hours * complexity_multiplier
        
        # Calculate profit
        profit = base_cost * profit_margin
        
        # Calculate total project cost
        total_cost = base_cost + expenses + profit
        
        # Calculate effective hourly rate
        effective_rate = total_cost / estimated_hours
        
        # Calculate ROI if expenses are significant
        roi = ((total_cost - expenses) / expenses * 100) if expenses > 0 else float('inf')
        
        # Generate recommendations
        recommendations = []
        if effective_rate < hourly_rate * 1.5:
            recommendations.append("Consider increasing your hourly rate")
        if expenses > base_cost * 0.3:
            recommendations.append("High expenses - consider passing some costs to client")
        if estimated_hours > 100:
            recommendations.append("Large project - consider milestone payments")
        if complexity_level and complexity_level.lower() == "high":
            recommendations.append("High complexity - consider adding buffer time")
        if project_type and project_type.lower() in ["web development", "software development"]:
            recommendations.append("Tech project - consider adding maintenance plan")
        
        # Format budget breakdown for display
        budget_breakdown = f"💰 Project Budget Analysis:\n\n"
        budget_breakdown += f"**Base Calculations:**\n"
        budget_breakdown += f"• Hourly Rate: ${hourly_rate:.2f}\n"
        budget_breakdown += f"• Estimated Hours: {estimated_hours}\n"
        if complexity_level:
            budget_breakdown += f"• Complexity: {complexity_level} (multiplier: {complexity_multiplier:.2f})\n"
        if project_type:
            budget_breakdown += f"• Project Type: {project_type}\n"
        budget_breakdown += f"• Base Cost: ${base_cost:.2f}\n\n"
        
        budget_breakdown += f"**Additional Costs:**\n"
        budget_breakdown += f"• Expenses: ${expenses:.2f}\n"
        budget_breakdown += f"• Profit Margin ({profit_margin*100:.0f}%): ${profit:.2f}\n"
        budget_breakdown += f"• Total Project Cost: ${total_cost:.2f}\n\n"
        
        budget_breakdown += f"**Rate Analysis:**\n"
        budget_breakdown += f"• Effective Hourly Rate: ${effective_rate:.2f}\n"
        budget_breakdown += f"• Rate Increase: {((effective_rate - hourly_rate) / hourly_rate * 100):.1f}%\n"
        
        if expenses > 0:
            budget_breakdown += f"• ROI: {roi:.1f}%\n"
        
        budget_breakdown += f"\n💡 **Recommendations:**\n"
        for recommendation in recommendations:
            budget_breakdown += f"• {recommendation}\n"
        
        # Return structured response
        return ProjectBudgetResponse(
            base_cost=base_cost,
            expenses=expenses,
            profit=profit,
            total_cost=total_cost,
            effective_rate=effective_rate,
            roi=roi if expenses > 0 else 0,
            recommendations=recommendations,
            formatted_breakdown=budget_breakdown
        )
        
    except Exception as e:
        logger.error(f"Budget calculation error: {e}")
        # Return structured response with error information
        return ProjectBudgetResponse(
            base_cost=0,
            expenses=0,
            profit=0,
            total_cost=0,
            effective_rate=0,
            roi=0,
            recommendations=[f"Error: {str(e)}"],
            formatted_breakdown=f"Error calculating budget: {str(e)}"
        )

class TaxCalculationRequest(BaseModel):
    gross_income: float = Field(..., description="Total gross income for the year")
    business_expenses: float = Field(0, description="Total business expenses")
    tax_year: int = Field(2024, description="Tax year (default 2024)")
    state: Optional[str] = Field(None, description="US state for state tax calculation")
    filing_status: Optional[str] = Field("single", description="Filing status (single, married, head_of_household)")
    retirement_contributions: float = Field(0, description="Retirement contributions (e.g., 401k, IRA)")

class TaxCalculationResponse(BaseModel):
    net_income: float = Field(..., description="Net income after business expenses")
    federal_tax: float = Field(..., description="Federal income tax")
    self_employment_tax: float = Field(..., description="Self-employment tax (15.3% of net income)")
    state_tax: float = Field(..., description="Estimated state tax")
    total_taxes: float = Field(..., description="Total estimated taxes")
    effective_tax_rate: float = Field(..., description="Effective tax rate as percentage")
    take_home: float = Field(..., description="Take-home pay after taxes")
    monthly_take_home: float = Field(..., description="Monthly take-home pay")
    tax_tips: List[str] = Field(..., description="Tax planning tips")
    formatted_breakdown: str = Field(..., description="Formatted tax breakdown for display")

@tool
def calculate_freelance_taxes(request: TaxCalculationRequest) -> TaxCalculationResponse:
    """Calculate estimated taxes for freelancers with detailed breakdown
    
    Args:
        request: Tax calculation request with income, expenses, and tax preferences
    
    Returns:
        Structured tax calculation response with detailed breakdown
    """
    try:
        # Extract values from request
        gross_income = request.gross_income
        business_expenses = request.business_expenses
        tax_year = request.tax_year
        state = request.state
        filing_status = request.filing_status
        retirement_contributions = request.retirement_contributions
        
        # Calculate net income (adjusted for retirement contributions)
        taxable_income = gross_income - business_expenses - retirement_contributions
        net_income = gross_income - business_expenses
        
        # Adjust tax brackets based on filing status
        # 2024 US Federal Tax Brackets (simplified)
        if filing_status == "married":
            tax_brackets = [
                (0, 23200, 0.10),
                (23200, 94300, 0.12),
                (94300, 201050, 0.22),
                (201050, 383900, 0.24),
                (383900, 487450, 0.32),
                (487450, 731200, 0.35),
                (731200, float('inf'), 0.37)
            ]
        elif filing_status == "head_of_household":
            tax_brackets = [
                (0, 16550, 0.10),
                (16550, 63100, 0.12),
                (63100, 100500, 0.22),
                (100500, 191950, 0.24),
                (191950, 243700, 0.32),
                (243700, 609350, 0.35),
                (609350, float('inf'), 0.37)
            ]
        else:  # single
            tax_brackets = [
                (0, 11600, 0.10),
                (11600, 47150, 0.12),
                (47150, 100525, 0.22),
                (100525, 191950, 0.24),
                (191950, 243725, 0.32),
                (243725, 609350, 0.35),
                (609350, float('inf'), 0.37)
            ]
        
        # Calculate federal tax
        federal_tax = 0
        remaining_income = taxable_income
        
        for i, (min_income, max_income, rate) in enumerate(tax_brackets):
            if remaining_income <= 0:
                break
                
            if taxable_income > min_income:
                taxable_in_bracket = min(remaining_income, max_income - min_income)
                federal_tax += taxable_in_bracket * rate
                remaining_income -= taxable_in_bracket
        
        # Estimate self-employment tax (15.3% of net income)
        self_employment_tax = net_income * 0.153
        
        # Estimate state tax (varies by state)
        state_tax_rates = {
            "california": 0.093,
            "new york": 0.068,
            "texas": 0.0,
            "florida": 0.0,
            "washington": 0.0,
            "illinois": 0.0495,
            # Add more states as needed
        }
        
        # Default state tax rate if state not specified or not in our dictionary
        state_tax_rate = 0.05  # Average state tax rate
        if state and state.lower() in state_tax_rates:
            state_tax_rate = state_tax_rates[state.lower()]
        
        state_tax = taxable_income * state_tax_rate
        
        # Total estimated taxes
        total_taxes = federal_tax + self_employment_tax + state_tax
        
        # Calculate effective tax rate
        effective_tax_rate = (total_taxes / gross_income) * 100
        
        # Calculate take-home pay
        take_home = gross_income - business_expenses - total_taxes
        monthly_take_home = take_home / 12
        
        # Generate tax tips
        tax_tips = [
            f"Set aside {effective_tax_rate:.0f}% of income for taxes",
            "Consider quarterly estimated tax payments",
            "Track all business expenses for deductions"
        ]
        
        # Add conditional tax tips
        if retirement_contributions < 6000 and gross_income > 50000:
            tax_tips.append("Increase retirement contributions to reduce taxable income")
        if state_tax_rate > 0.06:
            tax_tips.append("Consider tax-advantaged investments for high-tax states")
        if business_expenses < gross_income * 0.2:
            tax_tips.append("Review potential business deductions you may be missing")
        if net_income > 150000:
            tax_tips.append("Consider setting up an S-Corp to potentially reduce self-employment taxes")
        
        # Format tax breakdown for display
        tax_breakdown = f"🧮 Tax Calculation for {tax_year}:\n\n"
        tax_breakdown += f"**Income Summary:**\n"
        tax_breakdown += f"• Gross Income: ${gross_income:,.2f}\n"
        tax_breakdown += f"• Business Expenses: ${business_expenses:,.2f}\n"
        if retirement_contributions > 0:
            tax_breakdown += f"• Retirement Contributions: ${retirement_contributions:,.2f}\n"
        tax_breakdown += f"• Net Income: ${net_income:,.2f}\n"
        tax_breakdown += f"• Taxable Income: ${taxable_income:,.2f}\n\n"
        
        tax_breakdown += f"**Tax Breakdown:**\n"
        tax_breakdown += f"• Filing Status: {filing_status.replace('_', ' ').title()}\n"
        tax_breakdown += f"• Federal Income Tax: ${federal_tax:,.2f}\n"
        tax_breakdown += f"• Self-Employment Tax: ${self_employment_tax:,.2f}\n"
        tax_breakdown += f"• Estimated State Tax"
        if state:
            tax_breakdown += f" ({state.title()})"
        tax_breakdown += f": ${state_tax:,.2f}\n"
        tax_breakdown += f"• Total Estimated Taxes: ${total_taxes:,.2f}\n\n"
        
        tax_breakdown += f"**Final Numbers:**\n"
        tax_breakdown += f"• Effective Tax Rate: {effective_tax_rate:.1f}%\n"
        tax_breakdown += f"• Take-Home Pay: ${take_home:,.2f}\n"
        tax_breakdown += f"• Monthly Take-Home: ${monthly_take_home:,.2f}\n\n"
        
        tax_breakdown += f"💡 **Tax Planning Tips:**\n"
        for tip in tax_tips:
            tax_breakdown += f"• {tip}\n"
        
        # Return structured response
        return TaxCalculationResponse(
            net_income=net_income,
            federal_tax=federal_tax,
            self_employment_tax=self_employment_tax,
            state_tax=state_tax,
            total_taxes=total_taxes,
            effective_tax_rate=effective_tax_rate,
            take_home=take_home,
            monthly_take_home=monthly_take_home,
            tax_tips=tax_tips,
            formatted_breakdown=tax_breakdown
        )
        
    except Exception as e:
        logger.error(f"Tax calculation error: {e}")
        # Return structured response with error information
        return TaxCalculationResponse(
            net_income=0,
            federal_tax=0,
            self_employment_tax=0,
            state_tax=0,
            total_taxes=0,
            effective_tax_rate=0,
            take_home=0,
            monthly_take_home=0,
            tax_tips=[f"Error: {str(e)}"],
            formatted_breakdown=f"Error calculating taxes: {str(e)}"
        )

class ROICalculationRequest(BaseModel):
    investment: float = Field(..., description="Initial investment amount")
    return_amount: float = Field(..., description="Total return amount")
    time_period: int = Field(1, description="Time period in years (default 1)")
    risk_level: Optional[str] = Field(None, description="Risk level (low, medium, high)")
    investment_type: Optional[str] = Field(None, description="Type of investment (e.g., equipment, marketing, training)")
    opportunity_cost: Optional[float] = Field(None, description="Opportunity cost of alternative investments")

class ROICalculationResponse(BaseModel):
    roi_percentage: float = Field(..., description="ROI as a percentage")
    annualized_roi: float = Field(..., description="Annualized ROI percentage")
    net_profit: float = Field(..., description="Net profit (return - investment)")
    payback_period: float = Field(..., description="Payback period in years")
    assessment: str = Field(..., description="Assessment of ROI quality")
    recommendations: List[str] = Field(..., description="Investment recommendations")
    formatted_analysis: str = Field(..., description="Formatted ROI analysis for display")

@tool
def calculate_roi(request: ROICalculationRequest) -> ROICalculationResponse:
    """Calculate Return on Investment (ROI) with detailed analysis
    
    Args:
        request: ROI calculation request with investment details
    
    Returns:
        Structured ROI calculation response with detailed analysis
    """
    try:
        # Extract values from request
        investment = request.investment
        return_amount = request.return_amount
        time_period = request.time_period
        risk_level = request.risk_level
        investment_type = request.investment_type
        opportunity_cost = request.opportunity_cost
        
        # Calculate basic ROI
        roi_percentage = ((return_amount - investment) / investment) * 100
        
        # Calculate annualized ROI
        annualized_roi = (((return_amount / investment) ** (1 / time_period)) - 1) * 100
        
        # Calculate net profit
        net_profit = return_amount - investment
        
        # Calculate payback period
        payback_period = investment / (net_profit / time_period) if net_profit > 0 else float('inf')
        
        # Determine ROI assessment
        if roi_percentage > 50:
            assessment = "Excellent ROI - Highly profitable investment"
        elif roi_percentage > 20:
            assessment = "Good ROI - Solid investment"
        elif roi_percentage > 0:
            assessment = "Positive but low ROI - Consider alternatives"
        else:
            assessment = "Negative ROI - Investment lost money"
        
        # Generate recommendations based on ROI and additional factors
        recommendations = []
        
        # Basic ROI-based recommendations
        if roi_percentage < 10:
            recommendations.append("Consider higher-return alternatives")
            recommendations.append("Review investment strategy")
        elif roi_percentage > 30:
            recommendations.append("Consider scaling this investment")
            recommendations.append("Look for similar opportunities")
        
        # Risk-adjusted recommendations
        if risk_level:
            if risk_level.lower() == "high" and roi_percentage < 30:
                recommendations.append("High risk with low return - reconsider this investment")
            elif risk_level.lower() == "low" and roi_percentage > 20:
                recommendations.append("Low risk with good return - excellent investment profile")
        
        # Investment type specific recommendations
        if investment_type:
            if investment_type.lower() == "equipment" and payback_period > 3:
                recommendations.append("Long payback for equipment - consider leasing options")
            elif investment_type.lower() == "marketing" and roi_percentage < 50:
                recommendations.append("Marketing ROI below target - review campaign effectiveness")
            elif investment_type.lower() == "training" and roi_percentage > 0:
                recommendations.append("Training shows positive ROI - consider additional skill development")
        
        # Opportunity cost analysis
        if opportunity_cost is not None:
            opp_cost_diff = roi_percentage - opportunity_cost
            if opp_cost_diff > 10:
                recommendations.append(f"Investment outperforms alternative by {opp_cost_diff:.1f}% - good choice")
            elif opp_cost_diff < -10:
                recommendations.append(f"Alternative would yield {-opp_cost_diff:.1f}% better return - reconsider")
        
        # Format ROI analysis for display
        roi_analysis = f"📈 ROI Analysis:\n\n"
        roi_analysis += f"**Investment Details:**\n"
        roi_analysis += f"• Initial Investment: ${investment:,.2f}\n"
        roi_analysis += f"• Total Return: ${return_amount:,.2f}\n"
        roi_analysis += f"• Time Period: {time_period} year{'s' if time_period != 1 else ''}\n"
        if risk_level:
            roi_analysis += f"• Risk Level: {risk_level.title()}\n"
        if investment_type:
            roi_analysis += f"• Investment Type: {investment_type.title()}\n"
        if opportunity_cost is not None:
            roi_analysis += f"• Opportunity Cost: {opportunity_cost:.2f}%\n"
        roi_analysis += "\n"
        
        roi_analysis += f"**ROI Calculations:**\n"
        roi_analysis += f"• Net Profit: ${net_profit:,.2f}\n"
        roi_analysis += f"• ROI: {roi_percentage:.2f}%\n"
        roi_analysis += f"• Annualized ROI: {annualized_roi:.2f}%\n"
        roi_analysis += f"• Payback Period: {payback_period:.1f} year{'s' if payback_period != 1 else ''}\n\n"
        
        roi_analysis += f"**Assessment:**\n"
        roi_analysis += f"{'✅' if roi_percentage > 20 else '⚠️' if roi_percentage > 0 else '❌'} {assessment}\n"
        
        roi_analysis += f"\n💡 **Recommendations:**\n"
        for recommendation in recommendations:
            roi_analysis += f"• {recommendation}\n"
        
        # Return structured response
        return ROICalculationResponse(
            roi_percentage=roi_percentage,
            annualized_roi=annualized_roi,
            net_profit=net_profit,
            payback_period=payback_period,
            assessment=assessment,
            recommendations=recommendations,
            formatted_analysis=roi_analysis
        )
        
    except Exception as e:
        logger.error(f"ROI calculation error: {e}")
        # Return structured response with error information
        return ROICalculationResponse(
            roi_percentage=0,
            annualized_roi=0,
            net_profit=0,
            payback_period=0,
            assessment=f"Error: {str(e)}",
            recommendations=["Review input values and try again"],
            formatted_analysis=f"Error calculating ROI: {str(e)}"
        )

class BreakEvenAnalysisRequest(BaseModel):
    fixed_costs: float = Field(..., description="Total fixed costs")
    price_per_unit: float = Field(..., description="Price per unit or hourly rate")
    variable_cost_per_unit: float = Field(..., description="Variable cost per unit or hour")
    time_period: Optional[str] = Field("monthly", description="Time period (daily, weekly, monthly, yearly)")
    business_type: Optional[str] = Field(None, description="Type of business (service, product, hybrid)")

class BreakEvenAnalysisResponse(BaseModel):
    break_even_units: float = Field(..., description="Break-even point in units or hours")
    break_even_revenue: float = Field(..., description="Break-even point in revenue")
    contribution_margin: float = Field(..., description="Contribution margin per unit")
    contribution_margin_ratio: float = Field(..., description="Contribution margin ratio")
    safety_margin: Optional[float] = Field(None, description="Safety margin if target units provided")
    recommendations: List[str] = Field(..., description="Business recommendations")
    formatted_analysis: str = Field(..., description="Formatted break-even analysis for display")

@tool
def calculate_break_even(request: BreakEvenAnalysisRequest) -> BreakEvenAnalysisResponse:
    """Calculate break-even point and perform break-even analysis
    
    Args:
        request: Break-even analysis request with cost and pricing information
    
    Returns:
        Structured break-even analysis response with detailed breakdown
    """
    try:
        # Extract values from request
        fixed_costs = request.fixed_costs
        price_per_unit = request.price_per_unit
        variable_cost_per_unit = request.variable_cost_per_unit
        time_period = request.time_period
        business_type = request.business_type
        
        # Calculate contribution margin
        contribution_margin = price_per_unit - variable_cost_per_unit
        
        # Calculate contribution margin ratio
        contribution_margin_ratio = contribution_margin / price_per_unit
        
        # Calculate break-even point in units
        if contribution_margin <= 0:
            raise ValueError("Contribution margin must be positive to calculate break-even point")
            
        break_even_units = fixed_costs / contribution_margin
        
        # Calculate break-even point in revenue
        break_even_revenue = break_even_units * price_per_unit
        
        # Generate recommendations
        recommendations = []
        
        # Basic recommendations
        if contribution_margin_ratio < 0.3:
            recommendations.append("Low contribution margin - consider raising prices")
        if variable_cost_per_unit > price_per_unit * 0.7:
            recommendations.append("High variable costs - look for cost-cutting opportunities")
        
        # Business type specific recommendations
        if business_type:
            if business_type.lower() == "service" and break_even_units > 120 and time_period.lower() == "monthly":
                recommendations.append("High monthly hour requirement - consider package pricing")
            elif business_type.lower() == "product" and contribution_margin_ratio < 0.4:
                recommendations.append("Low product margin - evaluate manufacturing/sourcing costs")
        
        # Time period specific recommendations
        period_multiplier = {
            "daily": 30,
            "weekly": 4.33,
            "monthly": 1,
            "yearly": 1/12
        }.get(time_period.lower(), 1)
        
        normalized_monthly_units = break_even_units * period_multiplier
        
        if normalized_monthly_units > 160 and (not business_type or business_type.lower() == "service"):
            recommendations.append("Break-even exceeds typical monthly capacity - review pricing strategy")
        
        # Add general recommendations if list is empty
        if not recommendations:
            recommendations.append("Consider ways to reduce fixed costs for a lower break-even point")
            recommendations.append("Monitor contribution margin to ensure profitability")
        
        # Format break-even analysis for display
        unit_label = "hours" if business_type and business_type.lower() == "service" else "units"
        
        analysis = f"📊 Break-Even Analysis ({time_period.title()}):\n\n"
        analysis += f"**Cost Structure:**\n"
        analysis += f"• Fixed Costs: ${fixed_costs:,.2f}\n"
        analysis += f"• Price per {unit_label.rstrip('s')}: ${price_per_unit:,.2f}\n"
        analysis += f"• Variable Cost per {unit_label.rstrip('s')}: ${variable_cost_per_unit:,.2f}\n"
        if business_type:
            analysis += f"• Business Type: {business_type.title()}\n"
        analysis += "\n"
        
        analysis += f"**Margin Analysis:**\n"
        analysis += f"• Contribution Margin: ${contribution_margin:,.2f} per {unit_label.rstrip('s')}\n"
        analysis += f"• Contribution Margin Ratio: {contribution_margin_ratio:.1%}\n\n"
        
        analysis += f"**Break-Even Points:**\n"
        analysis += f"• {break_even_units:.1f} {unit_label}\n"
        analysis += f"• ${break_even_revenue:,.2f} in revenue\n\n"
        
        analysis += f"💡 **Recommendations:**\n"
        for recommendation in recommendations:
            analysis += f"• {recommendation}\n"
        
        # Return structured response
        return BreakEvenAnalysisResponse(
            break_even_units=break_even_units,
            break_even_revenue=break_even_revenue,
            contribution_margin=contribution_margin,
            contribution_margin_ratio=contribution_margin_ratio,
            safety_margin=None,  # Not calculated in this version
            recommendations=recommendations,
            formatted_analysis=analysis
        )
        
    except Exception as e:
        logger.error(f"Break-even calculation error: {e}")
        # Return structured response with error information
        return BreakEvenAnalysisResponse(
            break_even_units=0,
            break_even_revenue=0,
            contribution_margin=0,
            contribution_margin_ratio=0,
            safety_margin=None,
            recommendations=[f"Error: {str(e)}"],
            formatted_analysis=f"Error calculating break-even point: {str(e)}"
        )

class FinancialHealthRequest(BaseModel):
    monthly_income: float = Field(..., description="Average monthly income")
    monthly_expenses: float = Field(..., description="Average monthly expenses")
    savings: float = Field(..., description="Current savings amount")
    debt: float = Field(0, description="Current debt amount")
    emergency_fund_target: Optional[float] = Field(None, description="Target emergency fund amount (defaults to 6x monthly expenses)")
    freelancer_experience: Optional[str] = Field(None, description="Experience level (beginner, intermediate, expert)")

class FinancialHealthResponse(BaseModel):
    income_expense_ratio: float = Field(..., description="Income to expense ratio")
    savings_rate: float = Field(..., description="Monthly savings rate as percentage")
    months_of_runway: float = Field(..., description="Number of months savings would last")
    debt_to_income_ratio: float = Field(..., description="Debt to income ratio")
    emergency_fund_status: str = Field(..., description="Status of emergency fund")
    financial_health_score: int = Field(..., description="Overall financial health score (0-100)")
    strengths: List[str] = Field(..., description="Financial strengths")
    areas_to_improve: List[str] = Field(..., description="Areas to improve")
    action_items: List[str] = Field(..., description="Recommended action items")
    formatted_analysis: str = Field(..., description="Formatted financial health analysis")

@tool
def analyze_financial_health(request: FinancialHealthRequest) -> FinancialHealthResponse:
    """Analyze freelancer's financial health and provide recommendations
    
    Args:
        request: Financial health analysis request with income, expenses, savings and debt information
    
    Returns:
        Structured financial health analysis with metrics and recommendations
    """
    try:
        # Extract values from request
        monthly_income = request.monthly_income
        monthly_expenses = request.monthly_expenses
        savings = request.savings
        debt = request.debt
        emergency_fund_target = request.emergency_fund_target or (monthly_expenses * 6)
        freelancer_experience = request.freelancer_experience
        
        # Calculate key financial metrics
        income_expense_ratio = monthly_income / monthly_expenses if monthly_expenses > 0 else float('inf')
        savings_rate = ((monthly_income - monthly_expenses) / monthly_income) * 100 if monthly_income > 0 else 0
        months_of_runway = savings / monthly_expenses if monthly_expenses > 0 else float('inf')
        debt_to_income_ratio = debt / (monthly_income * 12) if monthly_income > 0 else float('inf')
        emergency_fund_progress = (savings / emergency_fund_target) * 100 if emergency_fund_target > 0 else 0
        
        # Determine emergency fund status
        if emergency_fund_progress >= 100:
            emergency_fund_status = "Complete"
        elif emergency_fund_progress >= 75:
            emergency_fund_status = "Strong"
        elif emergency_fund_progress >= 50:
            emergency_fund_status = "Building"
        elif emergency_fund_progress >= 25:
            emergency_fund_status = "Started"
        else:
            emergency_fund_status = "Needs attention"
        
        # Calculate financial health score (0-100)
        score_components = [
            min(30, 30 * min(income_expense_ratio / 1.5, 1)),  # 30 points for income > 1.5x expenses
            min(20, 20 * min(savings_rate / 30, 1)),  # 20 points for 30% savings rate
            min(25, 25 * min(months_of_runway / 6, 1)),  # 25 points for 6 months runway
            min(15, 15 * (1 - min(debt_to_income_ratio / 0.5, 1))),  # 15 points for low debt-to-income
            min(10, 10 * min(emergency_fund_progress / 100, 1))  # 10 points for emergency fund
        ]
        financial_health_score = int(sum(score_components))
        
        # Identify strengths
        strengths = []
        if income_expense_ratio > 1.5:
            strengths.append("Strong income relative to expenses")
        if savings_rate > 20:
            strengths.append("Healthy savings rate")
        if months_of_runway > 6:
            strengths.append("Solid financial runway")
        if debt_to_income_ratio < 0.3:
            strengths.append("Low debt burden")
        if emergency_fund_progress > 75:
            strengths.append("Well-funded emergency fund")
        
        # Identify areas to improve
        areas_to_improve = []
        if income_expense_ratio < 1.2:
            areas_to_improve.append("Income-expense gap is narrow")
        if savings_rate < 15:
            areas_to_improve.append("Savings rate below recommended minimum")
        if months_of_runway < 3:
            areas_to_improve.append("Limited financial runway")
        if debt_to_income_ratio > 0.4:
            areas_to_improve.append("High debt-to-income ratio")
        if emergency_fund_progress < 50:
            areas_to_improve.append("Emergency fund needs building")
        
        # Generate action items based on experience level and financial metrics
        action_items = []
        
        # Income-related actions
        if income_expense_ratio < 1.3:
            if freelancer_experience and freelancer_experience.lower() == "beginner":
                action_items.append("Increase rates by 15-20% for new clients")
            elif freelancer_experience and freelancer_experience.lower() == "intermediate":
                action_items.append("Develop premium service offerings to increase average project value")
            else:
                action_items.append("Focus on high-value clients and consider value-based pricing")
        
        # Expense-related actions
        if savings_rate < 20:
            action_items.append("Review monthly expenses to identify potential savings")
            action_items.append("Separate business and personal expenses for better tracking")
        
        # Savings-related actions
        if months_of_runway < 6:
            action_items.append(f"Build emergency fund to target of ${emergency_fund_target:,.2f}")
            action_items.append("Set up automatic transfers to savings on client payment days")
        
        # Debt-related actions
        if debt_to_income_ratio > 0.3:
            action_items.append("Prioritize debt reduction, focusing on highest interest debt first")
            if debt_to_income_ratio > 0.5:
                action_items.append("Consider debt consolidation to reduce interest rates")
        
        # Business structure recommendations
        if monthly_income > 5000 and (not freelancer_experience or freelancer_experience.lower() != "beginner"):
            action_items.append("Evaluate business structure (LLC, S-Corp) for tax advantages")
        
        # Format financial health analysis
        analysis = f"💵 Freelancer Financial Health Analysis:\n\n"
        analysis += f"**Financial Overview:**\n"
        analysis += f"• Monthly Income: ${monthly_income:,.2f}\n"
        analysis += f"• Monthly Expenses: ${monthly_expenses:,.2f}\n"
        analysis += f"• Current Savings: ${savings:,.2f}\n"
        analysis += f"• Current Debt: ${debt:,.2f}\n"
        if freelancer_experience:
            analysis += f"• Experience Level: {freelancer_experience.title()}\n"
        analysis += "\n"
        
        analysis += f"**Key Financial Metrics:**\n"
        analysis += f"• Income/Expense Ratio: {income_expense_ratio:.2f}x\n"
        analysis += f"• Monthly Savings Rate: {savings_rate:.1f}%\n"
        analysis += f"• Months of Runway: {months_of_runway:.1f}\n"
        analysis += f"• Debt-to-Income Ratio: {debt_to_income_ratio:.2f}\n"
        analysis += f"• Emergency Fund: {emergency_fund_progress:.1f}% of target (${emergency_fund_target:,.2f})\n"
        analysis += f"• Financial Health Score: {financial_health_score}/100 ({get_health_rating(financial_health_score)})\n\n"
        
        analysis += f"**Financial Strengths:**\n"
        if strengths:
            for strength in strengths:
                analysis += f"• ✅ {strength}\n"
        else:
            analysis += "• No significant strengths identified\n"
        analysis += "\n"
        
        analysis += f"**Areas to Improve:**\n"
        if areas_to_improve:
            for area in areas_to_improve:
                analysis += f"• ⚠️ {area}\n"
        else:
            analysis += "• No significant areas of concern\n"
        analysis += "\n"
        
        analysis += f"💡 **Recommended Actions:**\n"
        for item in action_items:
            analysis += f"• {item}\n"
        
        # Return structured response
        return FinancialHealthResponse(
            income_expense_ratio=income_expense_ratio,
            savings_rate=savings_rate,
            months_of_runway=months_of_runway,
            debt_to_income_ratio=debt_to_income_ratio,
            emergency_fund_status=emergency_fund_status,
            financial_health_score=financial_health_score,
            strengths=strengths,
            areas_to_improve=areas_to_improve,
            action_items=action_items,
            formatted_analysis=analysis
        )
        
    except Exception as e:
        logger.error(f"Financial health analysis error: {e}")
        # Return structured response with error information
        return FinancialHealthResponse(
            income_expense_ratio=0,
            savings_rate=0,
            months_of_runway=0,
            debt_to_income_ratio=0,
            emergency_fund_status="Error",
            financial_health_score=0,
            strengths=[],
            areas_to_improve=[],
            action_items=[f"Error: {str(e)}"],
            formatted_analysis=f"Error analyzing financial health: {str(e)}"
        )

# Helper function for financial health rating
def get_health_rating(score: int) -> str:
    if score >= 90:
        return "Excellent"
    elif score >= 75:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Needs Attention"
    else:
        return "Critical"

# Create the math agent
math_agent = Agent(
    name="Math Agent",
    handoff_description="Specialist for financial calculations, budgeting, and mathematical analysis for freelancers",
    instructions="""You are a specialist in financial calculations and mathematical analysis for freelancers.

Your expertise includes:
- Project budgeting and cost analysis
- Tax calculations for freelancers
- ROI and investment analysis
- Break-even analysis and pricing strategy
- Financial planning and forecasting
- Rate calculations and profit margin analysis
- Financial health assessment

Always focus on:
- Providing accurate calculations with clear explanations
- Helping freelancers understand their financial position
- Offering practical financial advice tailored to freelance businesses
- Explaining complex financial concepts in simple terms
- Providing actionable recommendations with specific numbers
- Considering tax implications and business expenses

When analyzing financial data:
1. First understand the freelancer's specific situation and business type
2. Consider both short-term cash flow and long-term profitability
3. Provide context for your calculations (industry standards, benchmarks)
4. Highlight key metrics that the freelancer should monitor
5. Suggest specific actions to improve financial outcomes

Use your tools to perform financial calculations and provide insights that help freelancers make informed financial decisions.""",
    tools=[calculate_project_budget, calculate_freelance_taxes, calculate_roi, calculate_break_even, analyze_financial_health]
)