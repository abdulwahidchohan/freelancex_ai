"""
FreelanceX.AI Invoice Agent
Specialized agent for invoicing, payment tracking, and financial management
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from core.agent_manager import BaseAgent

logger = logging.getLogger(__name__)

class InvoiceAgent(BaseAgent):
    """
    Invoice Agent - Handles invoicing, payment tracking, and financial management
    Generates invoices, tracks payments, and provides financial insights
    """
    
    def __init__(self):
        super().__init__(
            agent_id="invoice_agent",
            name="InvoiceAgent",
            description="Handles invoicing, payment tracking, and financial management"
        )
        self.invoice_templates = self._load_invoice_templates()
        
    def get_capabilities(self) -> List[str]:
        """Return invoice agent capabilities"""
        return [
            'invoice_generation',
            'payment_tracking',
            'tax_calculations',
            'financial_reporting',
            'expense_management',
            'cash_flow_analysis'
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process invoice and financial related tasks"""
        try:
            content = task_data.get('content', '').lower()
            task_type = task_data.get('task_type', 'general')
            
            if 'invoice' in content or 'bill' in content:
                return await self._generate_invoice(task_data)
            elif 'payment' in content or 'track' in content:
                return await self._track_payments(task_data)
            elif 'tax' in content or 'financial' in content:
                return await self._handle_financial_analysis(task_data)
            elif 'expense' in content or 'cost' in content:
                return await self._manage_expenses(task_data)
            else:
                return await self._general_financial_assistance(task_data)
                
        except Exception as e:
            logger.error(f"❌ Invoice agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_invoice(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an invoice"""
        try:
            content = task_data.get('content', '')
            
            # Extract invoice parameters
            invoice_params = self._extract_invoice_params(content)
            
            # Generate invoice
            invoice = await self._create_invoice(invoice_params)
            
            # Calculate taxes
            tax_calculations = await self._calculate_taxes(invoice_params)
            
            return {
                'success': True,
                'task_type': 'invoice_generation',
                'invoice': invoice,
                'tax_calculations': tax_calculations,
                'payment_terms': self._get_payment_terms(),
                'invoice_tips': self._get_invoice_tips()
            }
            
        except Exception as e:
            logger.error(f"❌ Invoice generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _track_payments(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track payments and outstanding invoices"""
        try:
            content = task_data.get('content', '')
            
            # Extract payment tracking parameters
            tracking_params = self._extract_tracking_params(content)
            
            # Get payment status
            payment_status = await self._get_payment_status(tracking_params)
            
            return {
                'success': True,
                'task_type': 'payment_tracking',
                'payment_status': payment_status,
                'outstanding_invoices': await self._get_outstanding_invoices(),
                'payment_recommendations': self._get_payment_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Payment tracking failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _handle_financial_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle financial analysis and reporting"""
        try:
            content = task_data.get('content', '')
            
            # Extract financial analysis parameters
            analysis_params = self._extract_analysis_params(content)
            
            # Perform financial analysis
            financial_analysis = await self._perform_financial_analysis(analysis_params)
            
            return {
                'success': True,
                'task_type': 'financial_analysis',
                'financial_analysis': financial_analysis,
                'cash_flow_analysis': await self._analyze_cash_flow(),
                'financial_recommendations': self._get_financial_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Financial analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _manage_expenses(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage expenses and cost tracking"""
        try:
            content = task_data.get('content', '')
            
            # Extract expense parameters
            expense_params = self._extract_expense_params(content)
            
            # Manage expenses
            expense_management = await self._track_expenses(expense_params)
            
            return {
                'success': True,
                'task_type': 'expense_management',
                'expense_management': expense_management,
                'expense_categories': self._get_expense_categories(),
                'expense_tips': self._get_expense_tips()
            }
            
        except Exception as e:
            logger.error(f"❌ Expense management failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _general_financial_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general financial assistance"""
        try:
            content = task_data.get('content', '')
            
            # Provide general guidance
            guidance = self._generate_financial_guidance(content)
            
            return {
                'success': True,
                'task_type': 'financial_assistance',
                'guidance': guidance,
                'financial_tools': self._get_financial_tools(),
                'best_practices': self._get_financial_best_practices()
            }
            
        except Exception as e:
            logger.error(f"❌ Financial assistance failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_invoice_templates(self) -> Dict[str, str]:
        """Load invoice templates"""
        return {
            'standard': """
INVOICE

From: Abdul Wahid Chohan
Email: abdul@freelancex.ai
Date: {invoice_date}

To: {client_name}
Email: {client_email}

Description: {description}
Amount: ${amount}
Tax: ${tax_amount}
Total: ${total_amount}

Payment Terms: {payment_terms}
Due Date: {due_date}

Thank you for your business!
            """,
            'detailed': """
DETAILED INVOICE

From: Abdul Wahid Chohan
Email: abdul@freelancex.ai
Phone: +1-555-0123
Date: {invoice_date}

To: {client_name}
Email: {client_email}

SERVICES RENDERED:
{services_rendered}

Subtotal: ${subtotal}
Tax ({tax_rate}%): ${tax_amount}
Total: ${total_amount}

Payment Terms: {payment_terms}
Due Date: {due_date}

Payment Methods:
- Bank Transfer
- PayPal
- Credit Card

Thank you for choosing my services!
            """
        }
    
    def _extract_invoice_params(self, content: str) -> Dict[str, Any]:
        """Extract invoice parameters from content"""
        params = {
            'client_name': 'Client',
            'client_email': 'client@example.com',
            'description': 'Freelance Services',
            'amount': 1000,
            'tax_rate': 0.1,
            'payment_terms': 'Net 30',
            'template_type': 'standard'
        }
        
        # Extract amount
        if 'amount' in content or 'rate' in content:
            # Simple extraction - in real implementation, use NLP
            if '500' in content:
                params['amount'] = 500
            elif '1000' in content:
                params['amount'] = 1000
            elif '2000' in content:
                params['amount'] = 2000
        
        # Extract client information
        if 'client' in content:
            params['client_name'] = 'Client Name'
            params['client_email'] = 'client@company.com'
        
        return params
    
    def _extract_tracking_params(self, content: str) -> Dict[str, Any]:
        """Extract payment tracking parameters"""
        return {
            'timeframe': '30 days',
            'include_overdue': True,
            'sort_by': 'due_date'
        }
    
    def _extract_analysis_params(self, content: str) -> Dict[str, Any]:
        """Extract financial analysis parameters"""
        return {
            'period': 'monthly',
            'include_expenses': True,
            'include_taxes': True
        }
    
    def _extract_expense_params(self, content: str) -> Dict[str, Any]:
        """Extract expense parameters"""
        return {
            'category': 'general',
            'amount': 0,
            'date': datetime.now().isoformat()
        }
    
    async def _create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create invoice content"""
        template = self.invoice_templates.get(params.get('template_type', 'standard'))
        
        # Calculate amounts
        amount = params['amount']
        tax_amount = amount * params['tax_rate']
        total_amount = amount + tax_amount
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{hash(str(datetime.now())) % 1000:03d}"
        
        # Fill template
        invoice_content = template.format(
            invoice_date=datetime.now().strftime('%Y-%m-%d'),
            client_name=params['client_name'],
            client_email=params['client_email'],
            description=params['description'],
            amount=f"{amount:.2f}",
            tax_amount=f"{tax_amount:.2f}",
            total_amount=f"{total_amount:.2f}",
            payment_terms=params['payment_terms'],
            due_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            tax_rate=f"{params['tax_rate'] * 100:.1f}",
            services_rendered="Professional freelance services as agreed",
            subtotal=f"{amount:.2f}"
        )
        
        return {
            'invoice_number': invoice_number,
            'content': invoice_content,
            'amount': amount,
            'tax_amount': tax_amount,
            'total_amount': total_amount,
            'due_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            'status': 'pending'
        }
    
    async def _calculate_taxes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate taxes for invoice"""
        amount = params['amount']
        tax_rate = params['tax_rate']
        
        return {
            'taxable_amount': amount,
            'tax_rate': tax_rate,
            'tax_amount': amount * tax_rate,
            'total_with_tax': amount * (1 + tax_rate),
            'tax_breakdown': {
                'federal_tax': amount * 0.15,
                'state_tax': amount * 0.05,
                'local_tax': amount * 0.02
            }
        }
    
    async def _get_payment_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment status for invoices"""
        # Simulate payment status
        return {
            'total_invoices': 15,
            'paid_invoices': 12,
            'pending_invoices': 2,
            'overdue_invoices': 1,
            'total_amount': 15000,
            'paid_amount': 12000,
            'pending_amount': 2000,
            'overdue_amount': 1000,
            'payment_rate': 0.8
        }
    
    async def _get_outstanding_invoices(self) -> List[Dict[str, Any]]:
        """Get outstanding invoices"""
        return [
            {
                'invoice_number': 'INV-20240115-001',
                'client_name': 'Tech Startup Inc',
                'amount': 2000,
                'due_date': '2024-02-15',
                'days_overdue': 5,
                'status': 'overdue'
            },
            {
                'invoice_number': 'INV-20240120-002',
                'client_name': 'Design Agency LLC',
                'amount': 1500,
                'due_date': '2024-02-20',
                'days_overdue': 0,
                'status': 'pending'
            }
        ]
    
    async def _perform_financial_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform financial analysis"""
        return {
            'revenue': {
                'total': 25000,
                'monthly_average': 5000,
                'growth_rate': 0.15
            },
            'expenses': {
                'total': 8000,
                'monthly_average': 1600,
                'categories': {
                    'software': 2000,
                    'marketing': 1500,
                    'office': 1000,
                    'other': 3500
                }
            },
            'profitability': {
                'gross_profit': 17000,
                'net_profit': 12000,
                'profit_margin': 0.48
            }
        }
    
    async def _analyze_cash_flow(self) -> Dict[str, Any]:
        """Analyze cash flow"""
        return {
            'cash_in': 25000,
            'cash_out': 8000,
            'net_cash_flow': 17000,
            'cash_flow_trend': 'positive',
            'recommendations': [
                'Maintain current payment terms',
                'Consider offering early payment discounts',
                'Diversify income sources'
            ]
        }
    
    async def _track_expenses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Track expenses"""
        return {
            'total_expenses': 8000,
            'expense_categories': {
                'software_subscriptions': 2000,
                'marketing': 1500,
                'office_supplies': 500,
                'professional_development': 1000,
                'travel': 500,
                'other': 2500
            },
            'monthly_trend': 'stable',
            'budget_vs_actual': 'under_budget'
        }
    
    def _get_payment_terms(self) -> List[str]:
        """Get payment terms options"""
        return [
            'Net 30 - Payment due within 30 days',
            'Net 15 - Payment due within 15 days',
            'Due on receipt - Payment due immediately',
            '50% upfront, 50% on completion'
        ]
    
    def _get_invoice_tips(self) -> List[str]:
        """Get invoice tips"""
        return [
            'Send invoices promptly after work completion',
            'Use clear, professional invoice templates',
            'Include detailed descriptions of services',
            'Set clear payment terms and due dates',
            'Follow up on overdue payments politely',
            'Keep detailed records of all transactions'
        ]
    
    def _get_payment_recommendations(self) -> List[str]:
        """Get payment recommendations"""
        return [
            'Send payment reminders 3 days before due date',
            'Offer early payment discounts for large invoices',
            'Use multiple payment methods for convenience',
            'Automate recurring invoices where possible',
            'Maintain professional communication about payments'
        ]
    
    def _get_financial_recommendations(self) -> List[str]:
        """Get financial recommendations"""
        return [
            'Set aside 30% of income for taxes',
            'Track all expenses for tax deductions',
            'Maintain separate business and personal accounts',
            'Regularly review and adjust pricing',
            'Build emergency fund for slow periods',
            'Consider business insurance for protection'
        ]
    
    def _get_expense_categories(self) -> List[str]:
        """Get expense categories"""
        return [
            'Software Subscriptions',
            'Marketing and Advertising',
            'Office Supplies',
            'Professional Development',
            'Travel and Transportation',
            'Insurance',
            'Legal and Accounting',
            'Other'
        ]
    
    def _get_expense_tips(self) -> List[str]:
        """Get expense tracking tips"""
        return [
            'Track expenses immediately when they occur',
            'Use expense tracking apps for convenience',
            'Keep receipts and documentation',
            'Categorize expenses for better organization',
            'Review expenses monthly for optimization',
            'Separate business and personal expenses'
        ]
    
    def _generate_financial_guidance(self, content: str) -> str:
        """Generate financial guidance"""
        if 'tax' in content:
            return "Set aside 30% of your income for taxes. Track all business expenses for deductions."
        elif 'pricing' in content:
            return "Regularly review your pricing based on market rates and your experience level."
        elif 'cash' in content:
            return "Maintain positive cash flow by managing payment terms and following up on overdue invoices."
        else:
            return "Good financial management involves tracking income, expenses, and maintaining proper records."
    
    def _get_financial_tools(self) -> List[str]:
        """Get recommended financial tools"""
        return [
            'QuickBooks - Accounting and invoicing',
            'FreshBooks - Invoicing and expense tracking',
            'Wave - Free accounting software',
            'PayPal - Payment processing',
            'Stripe - Payment processing for businesses',
            'Mint - Personal finance tracking'
        ]
    
    def _get_financial_best_practices(self) -> List[str]:
        """Get financial best practices"""
        return [
            'Separate business and personal finances',
            'Track all income and expenses',
            'Set aside money for taxes',
            'Maintain emergency fund',
            'Regular financial reviews',
            'Professional invoicing and payment terms',
            'Keep detailed records for tax purposes'
        ] 