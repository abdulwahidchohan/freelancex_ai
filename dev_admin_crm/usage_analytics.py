# Analytics
def generate_report(timeframe, report_type="summary", include_metrics=True):
    """
    Generate a usage analytics report for the specified timeframe.
    
    Args:
        timeframe (str): Time period for the report (e.g. 'daily', 'weekly', 'monthly')
        report_type (str): Type of report to generate ('summary' or 'detailed')
        include_metrics (bool): Whether to include performance metrics
        
    Returns:
        dict: Report data containing usage statistics and metrics
    """
    print(f"UsageAnalytics: Generating {report_type} report for timeframe: {timeframe}")
    
    # Mock report data structure
    report_data = {
        "timeframe": timeframe,
        "type": report_type,
        "timestamp": datetime.now().isoformat(),
        "metrics": {}
    }
    
    if include_metrics:
        # In a real scenario, these would be actual metrics from the system
        report_data["metrics"] = {
            "total_users": 0,
            "active_users": 0,
            "total_transactions": 0,
            "average_response_time": 0
        }
    
    # In a real scenario, this would query usage data and compile it into a report.
    return report_data
