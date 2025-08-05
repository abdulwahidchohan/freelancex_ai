"""
FreelanceX.AI Math Agent - OpenAI Agents SDK Implementation
Specialized agent for financial calculations, budgeting, and mathematical analysis
"""

from agents import Agent, tool
import math
import logging

logger = logging.getLogger(__name__)

@tool
def calculate_project_budget(hourly_rate: float, estimated_hours: int, expenses: float = 0, profit_margin: float = 0.2) -> str:
    """Calculate comprehensive project budget with profit margins
    
    Args:
        hourly_rate: Your hourly rate in dollars
        estimated_hours: Estimated hours to complete project
        expenses: Additional project expenses (tools, services, etc.)
        profit_margin: Desired profit margin as decimal (0.2 = 20%)
    
    Returns:
        Detailed budget breakdown
    """
    try:
        base_cost = hourly_rate * estimated_hours
        total_expenses = expenses
        subtotal = base_cost + total_expenses
        profit_amount = subtotal * profit_margin
        total_budget = subtotal + profit_amount
        
        # Risk and contingency
        contingency = total_budget * 0.15  # 15% contingency
        final_budget = total_budget + contingency
        
        budget = f"Project Budget Calculation\n"
        budget += f"{'='*40}\n\n"
        budget += f"💼 Base Calculation:\n"
        budget += f"• Hourly Rate: ${hourly_rate:,.2f}\n"
        budget += f"• Estimated Hours: {estimated_hours}\n"
        budget += f"• Base Labor Cost: ${base_cost:,.2f}\n\n"
        
        budget += f"💰 Additional Costs:\n"
        budget += f"• Project Expenses: ${total_expenses:,.2f}\n"
        budget += f"• Subtotal: ${subtotal:,.2f}\n\n"
        
        budget += f"📈 Profit & Risk:\n"
        budget += f"• Profit Margin ({profit_margin*100:.0f}%): ${profit_amount:,.2f}\n"
        budget += f"• Contingency (15%): ${contingency:,.2f}\n\n"
        
        budget += f"🎯 Final Budget: ${final_budget:,.2f}\n\n"
        
        budget += f"📊 Budget Breakdown:\n"
        budget += f"• Labor: {(base_cost/final_budget)*100:.1f}%\n"
        budget += f"• Expenses: {(total_expenses/final_budget)*100:.1f}%\n"
        budget += f"• Profit: {(profit_amount/final_budget)*100:.1f}%\n"
        budget += f"• Contingency: {(contingency/final_budget)*100:.1f}%\n\n"
        
        budget += f"💡 Pricing Strategy:\n"
        budget += f"• Minimum Quote: ${total_budget:,.2f}\n"
        budget += f"• Recommended Quote: ${final_budget:,.2f}\n"
        budget += f"• Premium Quote: ${final_budget*1.2:,.2f}\n"
        
        return budget
        
    except Exception as e:
        logger.error(f"Budget calculation error: {e}")
        return f"Error calculating project budget: {str(e)}"

@tool
def calculate_freelance_taxes(gross_income: float, business_expenses: float = 0, tax_year: int = 2024) -> str:
    """Calculate estimated taxes for freelance income
    
    Args:
        gross_income: Total freelance income for the year
        business_expenses: Deductible business expenses
        tax_year: Tax year (default: 2024)
    
    Returns:
        Tax calculation breakdown
    """
    try:
        # Simplified US tax calculation (consult tax professional for accuracy)
        net_income = gross_income - business_expenses
        
        # Self-employment tax (15.3% on first $160,200 in 2024)
        se_tax_rate = 0.153
        se_tax_limit = 160200
        se_taxable = min(net_income, se_tax_limit)
        se_tax = se_taxable * se_tax_rate
        
        # Federal income tax (simplified brackets)
        adjusted_income = net_income - (se_tax * 0.5)  # Deduct employer portion
        
        # Simplified tax brackets (single filer)
        federal_tax = 0
        if adjusted_income > 11000:
            federal_tax += min(adjusted_income - 11000, 33550) * 0.12
        if adjusted_income > 44550:
            federal_tax += min(adjusted_income - 44550, 50000) * 0.22
        if adjusted_income > 94550:
            federal_tax += (adjusted_income - 94550) * 0.24
        
        total_tax = se_tax + federal_tax
        quarterly_payment = total_tax / 4
        net_after_tax = net_income - total_tax
        
        tax_report = f"Freelance Tax Calculation ({tax_year})\n"
        tax_report += f"{'='*45}\n\n"
        tax_report += f"💰 Income Summary:\n"
        tax_report += f"• Gross Income: ${gross_income:,.2f}\n"
        tax_report += f"• Business Expenses: ${business_expenses:,.2f}\n"
        tax_report += f"• Net Business Income: ${net_income:,.2f}\n\n"
        
        tax_report += f"🏛️ Tax Breakdown:\n"
        tax_report += f"• Self-Employment Tax: ${se_tax:,.2f}\n"
        tax_report += f"• Federal Income Tax: ${federal_tax:,.2f}\n"
        tax_report += f"• Total Tax Liability: ${total_tax:,.2f}\n\n"
        
        tax_report += f"📅 Payment Schedule:\n"
        tax_report += f"• Quarterly Payment: ${quarterly_payment:,.2f}\n"
        tax_report += f"• Monthly Savings Goal: ${total_tax/12:,.2f}\n\n"
        
        tax_report += f"💵 Take-Home Summary:\n"
        tax_report += f"• Net After Tax: ${net_after_tax:,.2f}\n"
        tax_report += f"• Effective Tax Rate: {(total_tax/net_income)*100:.1f}%\n\n"
        
        tax_report += f"💡 Tax Tips:\n"
        tax_report += f"• Set aside {((total_tax/net_income)*100)+5:.0f}% of income for taxes\n"
        tax_report += f"• Track all business expenses for deductions\n"
        tax_report += f"• Consider quarterly estimated payments\n"
        tax_report += f"• Consult a tax professional for accuracy\n"
        
        return tax_report
        
    except Exception as e:
        logger.error(f"Tax calculation error: {e}")
        return f"Error calculating taxes: {str(e)}"

@tool
def calculate_roi(investment: float, return_amount: float, time_period: int = 1) -> str:
    """Calculate return on investment for business decisions
    
    Args:
        investment: Initial investment amount
        return_amount: Expected return amount
        time_period: Time period in years (default: 1)
    
    Returns:
        ROI analysis report
    """
    try:
        if investment <= 0:
            return "Investment amount must be greater than 0"
        
        profit = return_amount - investment
        roi_percentage = (profit / investment) * 100
        annualized_roi = roi_percentage / time_period
        
        # Break-even calculation
        break_even_time = investment / (return_amount / time_period) if return_amount > investment else float('inf')
        
        roi_report = f"Return on Investment Analysis\n"
        roi_report += f"{'='*35}\n\n"
        roi_report += f"💰 Investment Details:\n"
        roi_report += f"• Initial Investment: ${investment:,.2f}\n"
        roi_report += f"• Expected Return: ${return_amount:,.2f}\n"
        roi_report += f"• Time Period: {time_period} year(s)\n"
        roi_report += f"• Net Profit: ${profit:,.2f}\n\n"
        
        roi_report += f"📈 ROI Metrics:\n"
        roi_report += f"• Total ROI: {roi_percentage:.1f}%\n"
        roi_report += f"• Annualized ROI: {annualized_roi:.1f}%\n"
        
        if break_even_time != float('inf'):
            roi_report += f"• Break-even Time: {break_even_time:.1f} years\n\n"
        else:
            roi_report += f"• Break-even: Never (negative ROI)\n\n"
        
        roi_report += f"🎯 Investment Grade:\n"
        if annualized_roi >= 20:
            roi_report += f"• Grade: Excellent (>20% annual return)\n"
            roi_report += f"• Recommendation: Strong investment opportunity\n"
        elif annualized_roi >= 10:
            roi_report += f"• Grade: Good (10-20% annual return)\n"
            roi_report += f"• Recommendation: Solid investment choice\n"
        elif annualized_roi >= 5:
            roi_report += f"• Grade: Fair (5-10% annual return)\n"
            roi_report += f"• Recommendation: Consider other options\n"
        else:
            roi_report += f"• Grade: Poor (<5% annual return)\n"
            roi_report += f"• Recommendation: Look for better opportunities\n"
        
        roi_report += f"\n💡 Investment Insights:\n"
        if roi_percentage > 0:
            roi_report += f"• Positive ROI indicates profitable investment\n"
            roi_report += f"• Consider reinvesting profits for compound growth\n"
        else:
            roi_report += f"• Negative ROI indicates potential loss\n"
            roi_report += f"• Reassess investment strategy\n"
        
        return roi_report
        
    except Exception as e:
        logger.error(f"ROI calculation error: {e}")
        return f"Error calculating ROI: {str(e)}"

math_agent = Agent(
    name="Math Agent",
    handoff_description="Specialist for financial calculations, budgeting, and mathematical analysis",
    instructions="""You are a financial and mathematical analysis specialist for freelancers.

    Your expertise includes:
    - Project budget calculations and pricing
    - Tax calculations and planning
    - ROI analysis for business investments
    - Financial planning and cash flow analysis
    - Mathematical problem solving

    Always provide:
    - Accurate calculations with clear breakdowns
    - Practical financial advice for freelancers
    - Risk assessment and contingency planning
    - Strategic insights for business decisions
    - Easy-to-understand explanations

    Use your tools to calculate budgets, taxes, and ROI when users need financial analysis.""",
    
    tools=[calculate_project_budget, calculate_freelance_taxes, calculate_roi]
)