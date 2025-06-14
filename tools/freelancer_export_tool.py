# Data export
def export_all(format: str) -> str:
    """
    Export all data in the specified format.
    
    Args:
        format (str): The desired export format (e.g., 'csv', 'json', 'xlsx')
        
    Returns:
        str: Status message indicating export result
        
    Raises:
        ValueError: If format is not supported
    """
    supported_formats = ['csv', 'json', 'xlsx']
    format = format.lower()
    
    if format not in supported_formats:
        raise ValueError(f"Unsupported format: {format}. Supported formats are: {', '.join(supported_formats)}")
    
    print(f"Exporting all data in {format} format...")
    
    try:
        # In a real scenario, this would retrieve data from various sources and export it
        # Add export logic here based on format
        
        # Log the successful export
        print(f"Export completed successfully to {format}")
        return f"Data exported successfully in {format} format."
        
    except Exception as e:
        error_msg = f"Export failed: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg)
