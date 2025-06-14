# Logs agent outcomes
def log_feedback(agent_name: str, outcome: str, log_file: str = "agent_feedback.log", log_level: str = "INFO") -> bool:
    """
    Logs feedback for an agent's outcome.
    
    Args:
        agent_name (str): Name of the agent
        outcome (str): Outcome/feedback to be logged
        log_file (str): Path to the log file (default: agent_feedback.log)
        log_level (str): Logging level (default: INFO)
        
    Returns:
        bool: True if logging was successful, False otherwise
    """
    try:
        # Add timestamp to log entry
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{log_level}] Agent: {agent_name} - Outcome: {outcome}"
        
        # Print to console
        print(log_entry)
        
        # Write to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
            
        # Could extend with additional logging methods:
        # - Database logging
        # - Cloud logging service
        # - Metrics collection
        
        return True
    except Exception as e:
        error_msg = f"Error logging feedback: {str(e)}"
        print(error_msg)
        
        # Log the error itself
        try:
            with open(log_file + '.error', 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.datetime.now().isoformat()}] {error_msg}\n")
        except:
            pass  # Suppress secondary errors
            
        return False
