# Profile management
def update_profile(user_id, updates):
    """
    Updates a user's profile with the provided information.
    
    Args:
        user_id (str): The unique identifier of the user
        updates (dict): Dictionary containing the profile fields to update
        
    Returns:
        bool: True if update was successful, False otherwise
        
    Raises:
        ValueError: If user_id is empty or updates is not a dictionary
    """
    # Input validation
    if not user_id:
        raise ValueError("User ID cannot be empty")
    if not isinstance(updates, dict):
        raise ValueError("Updates must be a dictionary")
    
    try:
        print(f"Updating profile for user {user_id} with: {updates}")
        # TODO: Implement database connection and update logic
        # In a real scenario, this would update a user's profile in a database
        
        # Perform validation on update fields
        for field, value in updates.items():
            if value is None:
                raise ValueError(f"Field '{field}' cannot be None")
                
        # Mock successful update
        return True
        
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return False
