# Admin controls
class AdminPanel:
    def __init__(self):
        self.metrics = {
            'total_users': 0,
            'active_projects': 0,
            'revenue': 0.0,
            'pending_tasks': 0
        }
    
    def show_dashboard(self):
        """Display the admin dashboard with key metrics and controls"""
        print("AdminPanel: Displaying admin dashboard...")
        self._update_metrics()
        self._display_metrics()
        self._show_controls()
        return "Admin dashboard displayed with latest metrics."
    
    def _update_metrics(self):
        """Update dashboard metrics from database"""
        # In a real implementation, this would fetch actual data
        print("Fetching latest metrics from database...")
        
    def _display_metrics(self):
        """Display current dashboard metrics"""
        print("\nDashboard Metrics:")
        print("-----------------")
        for metric, value in self.metrics.items():
            print(f"{metric.replace('_', ' ').title()}: {value}")
            
    def _show_controls(self):
        """Display admin control options"""
        print("\nAvailable Controls:")
        print("-----------------")
        print("1. User Management")
        print("2. Project Overview")
        print("3. Financial Reports")
        print("4. System Settings")
