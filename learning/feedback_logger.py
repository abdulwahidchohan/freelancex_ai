import json
import os
import datetime

# Logs all outcomes
def log_feedback(agent_name, feedback):
    log_file = f"logs/{agent_name}.log"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Append feedback to log file
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] {feedback}\n")

        # Analyze feedback for continuous improvement
        analyze_feedback(agent_name, feedback)

        print(f"Feedback logged for {agent_name}.")
    except Exception as e:
        print(f"Error logging feedback for {agent_name}: {e}")

def analyze_feedback(agent_name, feedback):
    # Implement feedback analysis logic here
    # This could involve sentiment analysis, keyword extraction, etc.
    pass
