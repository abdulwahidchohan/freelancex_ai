# Analyzes performance
def analyze_logs(logs):
    print(f"Analyzing logs for reflection: {logs}")
    
    # Initialize metrics
    total_tasks = len(logs)
    successful_tasks = 0
    failed_tasks = 0
    avg_completion_time = 0
    
    # Analyze each log entry
    completion_times = []
    for log in logs:
        try:
            if isinstance(log, dict):
                # Track success/failure
                if log.get('status') == 'success':
                    successful_tasks += 1
                else:
                    failed_tasks += 1
                    
                # Track completion time if available
                if 'completion_time' in log:
                    completion_times.append(log['completion_time'])
                    
                # Additional metrics could be analyzed here
        except Exception as e:
            print(f"Error analyzing log entry: {e}")
            
    # Calculate statistics
    success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    # Generate detailed reflection
    reflection = (
        f"Performance Analysis:\n"
        f"- Total tasks: {total_tasks}\n"
        f"- Successful tasks: {successful_tasks} ({success_rate:.1f}%)\n"
        f"- Failed tasks: {failed_tasks}\n"
        f"- Average completion time: {avg_completion_time:.2f} seconds\n"
        f"Recommendations:\n"
        f"- {'Maintain current performance' if success_rate > 90 else 'Investigate failure patterns'}\n"
        f"- {'Review completion times for optimization' if avg_completion_time > 5 else 'Time efficiency is good'}"
    )
    
    return reflection
