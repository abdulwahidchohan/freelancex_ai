# Personality modeling
class ProfileBuilder:
    def __init__(self):
        self.profiles = {}  # In-memory storage for profiles
        self.update_history = []  # Track profile update history
        
    def update_profile(self, agent_name: str, new_data: dict) -> bool:
        """
        Updates an agent's profile with new behavioral/personality data
        
        Args:
            agent_name: Name/ID of the agent to update
            new_data: Dictionary containing new profile data
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Validate inputs
            if not isinstance(agent_name, str) or not isinstance(new_data, dict):
                raise ValueError("Invalid input types")
                
            # Create profile if it doesn't exist
            if agent_name not in self.profiles:
                self.profiles[agent_name] = {}
                
            # Update profile with new data
            self.profiles[agent_name].update(new_data)
            
            # Log the update
            self.update_history.append({
                'timestamp': datetime.now(),
                'agent': agent_name,
                'updates': new_data
            })
            
            print(f"Successfully updated profile for {agent_name} with new data: {new_data}")
            return True
            
        except Exception as e:
            print(f"Error updating profile: {str(e)}")
            return False
            
    def get_profile(self, agent_name: str) -> dict:
        """
        Retrieves an agent's complete profile
        
        Args:
            agent_name: Name/ID of the agent
            
        Returns:
            dict: The agent's profile data
        """
        return self.profiles.get(agent_name, {})
        
    def get_update_history(self, agent_name: str = None) -> list:
        """
        Gets profile update history, optionally filtered by agent
        
        Args:
            agent_name: Optional name/ID to filter updates for specific agent
            
        Returns:
            list: Update history entries
        """
        if agent_name:
            return [update for update in self.update_history if update['agent'] == agent_name]
        return self.update_history
