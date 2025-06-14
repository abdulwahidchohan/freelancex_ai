# User interface
def render_controls(agents):
    """
    Renders the control panel UI for managing agents.
    
    Args:
        agents (list): List of agent objects to display in the control panel
        
    Returns:
        dict: Status of UI rendering with components information
    """
    try:
        print(f"Initializing control panel UI for {len(agents)} agents...")
        
        # Validate input
        if not agents:
            return {
                "status": "error",
                "message": "No agents provided to render",
                "components": []
            }
            
        # Process each agent for UI rendering
        ui_components = []
        for agent in agents:
            component = {
                "id": id(agent),
                "name": getattr(agent, "name", "Unnamed Agent"),
                "status": getattr(agent, "status", "unknown"),
                "controls": ["start", "stop", "pause", "resume"]
            }
            ui_components.append(component)
            
        print(f"Successfully generated UI components for agents: {agents}")
        
        return {
            "status": "success",
            "message": "UI rendered successfully",
            "components": ui_components
        }
        
    except Exception as e:
        print(f"Error rendering control panel UI: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to render UI: {str(e)}",
            "components": []
        }
