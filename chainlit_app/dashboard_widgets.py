# Dashboard components
def render_dashboard():
    """Renders the main dashboard components and layout"""
    # Create the main dashboard container
    with cl.Row():
        # Left column for key metrics
        with cl.Column(width="1/3"):
            cl.Metric(
                "Total Projects",
                "42",
                description="Active projects this month"
            )
            cl.Metric(
                "Success Rate",
                "87%",
                description="Project completion rate"
            )

        # Middle column for charts/graphs
        with cl.Column(width="1/3"):
            cl.Plot(
                figure={
                    "data": [{"x": [1,2,3], "y": [4,2,6], "type": "bar"}],
                    "layout": {"title": "Project Statistics"}
                }
            )

        # Right column for recent activity
        with cl.Column(width="1/3"):
            cl.Message(
                content="Recent Activity Feed",
                author="System"
            )
            cl.Message(
                content="Project X completed",
                author="Updates"
            )
            cl.Message(
                content="New task assigned",
                author="Updates"
            )
