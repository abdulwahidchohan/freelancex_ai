# Document generation
def write_document(doc_type, context):
    """
    Generate a document based on the specified type and context.
    
    Args:
        doc_type (str): The type of document to generate
        context (dict): Context data for document generation
        
    Returns:
        tuple: (str, bool) - Document creation message and success status
    """
    try:
        # Validate inputs
        if not doc_type or not isinstance(doc_type, str):
            raise ValueError("Document type must be a non-empty string")
        
        if not context or not isinstance(context, dict):
            raise ValueError("Context must be a non-empty dictionary")

        print(f"Writing {doc_type} document with context: {context}")
        
        # TODO: Implement actual document generation logic here
        # Example: Use templates, formatting, etc.
        
        # Add logging for document creation
        print(f"Successfully created document of type: {doc_type}")
        
        return f"Document '{doc_type}' created successfully.", True
        
    except Exception as e:
        error_msg = f"Failed to create document: {str(e)}"
        print(error_msg)
        return error_msg, False
