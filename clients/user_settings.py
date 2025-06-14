# User preferences
class UserSettings:
    def __init__(self):
        self.preferences = {}

    def save_preferences(self, preferences=None):
        """
        Save user preferences to storage
        Args:
            preferences (dict, optional): Dictionary of preferences to save. 
                                        Uses instance preferences if not provided.
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            if preferences:
                self.preferences.update(preferences)
            print("Saving user preferences...")
            # In a real scenario, this would persist user settings to a file or database
            return True
        except Exception as e:
            print(f"Error saving preferences: {str(e)}")
            return False

    def get_preferences(self):
        """
        Get current user preferences
        Returns:
            dict: Dictionary containing user preferences
        """
        return self.preferences

    def update_preference(self, key, value):
        """
        Update a single preference
        Args:
            key (str): Preference key to update
            value: New value for the preference
        """
        self.preferences[key] = value
        self.save_preferences()
