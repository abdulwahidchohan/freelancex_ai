# Financial management
class InvoiceTaxAgent:
    def __init__(self):
        self.tax_rate = 0.20  # Default tax rate of 20%
        
    def generate_invoice(self, job):
        """
        Generate a detailed invoice for a given job
        
        Args:
            job (dict): Dictionary containing job details including title, amount, etc.
            
        Returns:
            dict: Invoice details including subtotal, tax, and total amount
        """
        if not isinstance(job, dict):
            raise ValueError("Job must be a dictionary")
            
        if 'amount' not in job or 'title' not in job:
            raise ValueError("Job must contain 'amount' and 'title' fields")
            
        subtotal = float(job['amount'])
        tax = subtotal * self.tax_rate
        total = subtotal + tax
        
        invoice = {
            'job_title': job['title'],
            'date': datetime.now().strftime("%Y-%m-%d"),
            'subtotal': subtotal,
            'tax_rate': f"{self.tax_rate:.0%}",
            'tax_amount': tax,
            'total': total,
            'status': 'generated'
        }
        
        print(f"InvoiceTaxAgent: Generated invoice for job: {job['title']}")
        return invoice
        
    def set_tax_rate(self, rate):
        """
        Set custom tax rate
        
        Args:
            rate (float): Tax rate as decimal (e.g., 0.20 for 20%)
        """
        if not 0 <= rate <= 1:
            raise ValueError("Tax rate must be between 0 and 1")
        self.tax_rate = rate
