# Implements improvements
class AdaptationEngine:
    def __init__(self):
        self.change_history = []
        self.active_configurations = {}

    def apply_changes(self, agent_name: str, changes: dict) -> bool:
        """
        Apply configuration changes to an agent and track the modifications.
        
        Args:
            agent_name: Name of the agent to modify
            changes: Dictionary containing configuration changes
            
        Returns:
            bool: True if changes were applied successfully, False otherwise
        """
        try:
            # Validate inputs
            if not isinstance(agent_name, str) or not isinstance(changes, dict):
                raise ValueError("Invalid input types")
            
            if not changes:
                return False
                
            # Store current configuration
            current_config = self.active_configurations.get(agent_name, {})
            
            # Apply and track changes
            self.active_configurations[agent_name] = {
                **current_config,
                **changes
            }
            
            # Record change in history
            self.change_history.append({
                'timestamp': datetime.now(),
                'agent': agent_name,
                'changes': changes,
                'status': 'success'
            })
            
            print(f"Successfully applied changes to {agent_name}: {changes}")
            return True
            
        except Exception as e:
            # Log error and record failed change attempt
            self.change_history.append({
                'timestamp': datetime.now(),
                'agent': agent_name,
                'changes': changes,
                'status': 'failed',
                'error': str(e)
            })
            print(f"Error applying changes to {agent_name}: {str(e)}")
            return False
    
    def get_agent_configuration(self, agent_name: str) -> dict:
        """Get current configuration for an agent"""
        return self.active_configurations.get(agent_name, {})
    
    def get_change_history(self, agent_name: str = None) -> list:
        """Get change history, optionally filtered by agent name"""
        if agent_name:
            return [change for change in self.change_history if change['agent'] == agent_name]
        return self.change_history
