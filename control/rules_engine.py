# Business rules
def enforce_rules(context):
    """
    Enforces business rules on the given context and returns validation results.
    
    Args:
        context (dict): Dictionary containing the context data to validate
        
    Returns:
        tuple: (bool, list) - (passed_all_rules, list of rule violations)
    """
    print(f"RulesEngine: Enforcing rules for context: {context}")
    
    violations = []
    rules_passed = True
    
    # Example rule validations
    if not context:
        violations.append("Context cannot be empty")
        rules_passed = False
        
    try:
        # Validate required fields
        required_fields = ['user_id', 'action_type', 'timestamp']
        for field in required_fields:
            if field not in context:
                violations.append(f"Missing required field: {field}")
                rules_passed = False
                
        # Validate data types
        if 'user_id' in context and not isinstance(context['user_id'], (int, str)):
            violations.append("user_id must be integer or string")
            rules_passed = False
            
        # Add more complex business rule validations here
        
    except Exception as e:
        violations.append(f"Error during rule validation: {str(e)}")
        rules_passed = False
        
    return rules_passed, violations
