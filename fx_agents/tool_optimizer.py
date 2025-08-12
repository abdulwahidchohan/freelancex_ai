"""Enhanced Tool Optimizer - OpenAI Agents SDK Integration
Provides tool optimization with direct SDK integration and automatic schema generation
"""

import logging
import inspect
import json
from typing import Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel, Field, create_model
from agents import function_tool as tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolSchema(BaseModel):
    """Enhanced tool schema with SDK optimization"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    return_type: str = Field(..., description="Return type")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")
    validation_rules: Dict[str, Any] = Field(default_factory=dict, description="Validation rules")

class OptimizedTool(BaseModel):
    """Optimized tool with SDK features"""
    function: Callable = Field(..., description="Tool function")
    schema: ToolSchema = Field(..., description="Tool schema")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Tool metadata")
    
    class Config:
        arbitrary_types_allowed = True

class ToolOptimizer:
    """Enhanced tool optimizer with SDK integration"""
    
    def __init__(self):
        self.optimized_tools: Dict[str, OptimizedTool] = {}
        self.schema_cache: Dict[str, Dict[str, Any]] = {}
    
    def optimize_tool(self, func: Callable, name: Optional[str] = None, 
                     description: Optional[str] = None, examples: Optional[List[Dict[str, Any]]] = None,
                     validation_rules: Optional[Dict[str, Any]] = None) -> Callable:
        """Optimize tool with SDK integration and automatic schema generation"""
        try:
            # Get function metadata
            func_name = name or func.__name__
            func_description = description or func.__doc__ or f"Tool: {func_name}"
            
            # Generate schema automatically
            schema = self._generate_schema(func, func_name, func_description)
            
            # Add examples and validation rules
            if examples:
                schema.examples = examples
            if validation_rules:
                schema.validation_rules = validation_rules
            
            # Create optimized tool
            optimized_tool = OptimizedTool(
                function=func,
                schema=schema,
                metadata={
                    "original_function": func.__name__,
                    "module": func.__module__,
                    "optimized": True
                }
            )
            
            # Store optimized tool
            self.optimized_tools[func_name] = optimized_tool
            
            # Create SDK tool with optimized schema
            @tool(name=func_name, description=func_description)
            def optimized_function(*args, **kwargs):
                try:
                    # Apply validation rules
                    if schema.validation_rules:
                        self._validate_inputs(args, kwargs, schema.validation_rules)
                    
                    # Execute function
                    result = func(*args, **kwargs)
                    
                    # Validate output
                    if schema.validation_rules.get("output_validation"):
                        self._validate_output(result, schema.validation_rules["output_validation"])
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Tool execution failed: {str(e)}")
                    raise
            
            # Copy function signature
            optimized_function.__signature__ = func.__signature__
            optimized_function.__annotations__ = func.__annotations__
            
            logger.info(f"Optimized tool: {func_name}")
            return optimized_function
            
        except Exception as e:
            logger.error(f"Failed to optimize tool {func.__name__}: {str(e)}")
            return func
    
    def _generate_schema(self, func: Callable, name: str, description: str) -> ToolSchema:
        """Generate tool schema automatically from function signature"""
        try:
            # Get function signature
            sig = inspect.signature(func)
            
            # Extract parameters
            parameters = {}
            required_params = []
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_info = {
                    "type": self._get_type_string(param.annotation),
                    "description": f"Parameter: {param_name}"
                }
                
                # Check if parameter has default value
                if param.default != inspect.Parameter.empty:
                    param_info["default"] = param.default
                else:
                    required_params.append(param_name)
                
                # Add parameter description from docstring if available
                if func.__doc__:
                    doc_lines = func.__doc__.split('\n')
                    for line in doc_lines:
                        if line.strip().startswith(f":param {param_name}:"):
                            param_info["description"] = line.split(':', 2)[2].strip()
                            break
                
                parameters[param_name] = param_info
            
            # Get return type
            return_type = self._get_type_string(sig.return_annotation)
            
            # Create schema
            schema = ToolSchema(
                name=name,
                description=description,
                parameters={
                    "type": "object",
                    "properties": parameters,
                    "required": required_params
                },
                return_type=return_type,
                examples=[],
                validation_rules={}
            )
            
            return schema
            
        except Exception as e:
            logger.error(f"Failed to generate schema for {name}: {str(e)}")
            # Return basic schema
            return ToolSchema(
                name=name,
                description=description,
                parameters={"type": "object", "properties": {}},
                return_type="string",
                examples=[],
                validation_rules={}
            )
    
    def _get_type_string(self, annotation: Any) -> str:
        """Convert type annotation to string"""
        try:
            if annotation == inspect.Parameter.empty:
                return "string"
            
            if hasattr(annotation, '__name__'):
                return annotation.__name__
            
            if hasattr(annotation, '_name'):
                return annotation._name
            
            return str(annotation)
            
        except Exception:
            return "string"
    
    def _validate_inputs(self, args: tuple, kwargs: dict, validation_rules: Dict[str, Any]):
        """Validate tool inputs"""
        try:
            # Check required parameters
            if "required_params" in validation_rules:
                for param in validation_rules["required_params"]:
                    if param not in kwargs:
                        raise ValueError(f"Required parameter '{param}' is missing")
            
            # Check parameter types
            if "type_validation" in validation_rules:
                for param, expected_type in validation_rules["type_validation"].items():
                    if param in kwargs:
                        value = kwargs[param]
                        if not isinstance(value, expected_type):
                            raise TypeError(f"Parameter '{param}' must be of type {expected_type}")
            
            # Check parameter ranges
            if "range_validation" in validation_rules:
                for param, (min_val, max_val) in validation_rules["range_validation"].items():
                    if param in kwargs:
                        value = kwargs[param]
                        if isinstance(value, (int, float)) and (value < min_val or value > max_val):
                            raise ValueError(f"Parameter '{param}' must be between {min_val} and {max_val}")
            
            # Check string length
            if "length_validation" in validation_rules:
                for param, (min_len, max_len) in validation_rules["length_validation"].items():
                    if param in kwargs:
                        value = kwargs[param]
                        if isinstance(value, str):
                            if len(value) < min_len or len(value) > max_len:
                                raise ValueError(f"Parameter '{param}' length must be between {min_len} and {max_len}")
            
        except Exception as e:
            logger.error(f"Input validation failed: {str(e)}")
            raise
    
    def _validate_output(self, result: Any, validation_rules: Dict[str, Any]):
        """Validate tool output"""
        try:
            # Check output type
            if "type" in validation_rules:
                expected_type = validation_rules["type"]
                if not isinstance(result, expected_type):
                    raise TypeError(f"Output must be of type {expected_type}")
            
            # Check output length
            if "max_length" in validation_rules:
                if isinstance(result, str) and len(result) > validation_rules["max_length"]:
                    raise ValueError(f"Output length exceeds maximum of {validation_rules['max_length']}")
            
            # Check output content
            if "forbidden_content" in validation_rules:
                if isinstance(result, str):
                    for forbidden in validation_rules["forbidden_content"]:
                        if forbidden in result:
                            raise ValueError(f"Output contains forbidden content: {forbidden}")
            
        except Exception as e:
            logger.error(f"Output validation failed: {str(e)}")
            raise
    
    def create_validation_rules(self, required_params: Optional[List[str]] = None,
                               type_validation: Optional[Dict[str, type]] = None,
                               range_validation: Optional[Dict[str, tuple]] = None,
                               length_validation: Optional[Dict[str, tuple]] = None,
                               output_validation: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create validation rules for tools"""
        rules = {}
        
        if required_params:
            rules["required_params"] = required_params
        
        if type_validation:
            rules["type_validation"] = type_validation
        
        if range_validation:
            rules["range_validation"] = range_validation
        
        if length_validation:
            rules["length_validation"] = length_validation
        
        if output_validation:
            rules["output_validation"] = output_validation
        
        return rules
    
    def optimize_tool_suite(self, tools: List[Callable], 
                          descriptions: Optional[Dict[str, str]] = None,
                          examples: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                          validation_rules: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Callable]:
        """Optimize a suite of tools"""
        try:
            optimized_tools = []
            
            for tool_func in tools:
                tool_name = tool_func.__name__
                
                # Get tool-specific configurations
                description = descriptions.get(tool_name) if descriptions else None
                tool_examples = examples.get(tool_name) if examples else None
                tool_rules = validation_rules.get(tool_name) if validation_rules else None
                
                # Optimize tool
                optimized_tool = self.optimize_tool(
                    tool_func,
                    name=tool_name,
                    description=description,
                    examples=tool_examples,
                    validation_rules=tool_rules
                )
                
                optimized_tools.append(optimized_tool)
            
            logger.info(f"Optimized {len(optimized_tools)} tools")
            return optimized_tools
            
        except Exception as e:
            logger.error(f"Failed to optimize tool suite: {str(e)}")
            return tools
    
    def get_optimized_tool(self, name: str) -> Optional[OptimizedTool]:
        """Get optimized tool by name"""
        return self.optimized_tools.get(name)
    
    def list_optimized_tools(self) -> List[str]:
        """List all optimized tools"""
        return list(self.optimized_tools.keys())
    
    def get_tool_schema(self, name: str) -> Optional[ToolSchema]:
        """Get tool schema by name"""
        optimized_tool = self.get_optimized_tool(name)
        return optimized_tool.schema if optimized_tool else None

# Global tool optimizer
_tool_optimizer = ToolOptimizer()

def get_tool_optimizer() -> ToolOptimizer:
    """Get global tool optimizer"""
    return _tool_optimizer

def optimize_tool(func: Callable, **kwargs) -> Callable:
    """Optimize a single tool"""
    optimizer = get_tool_optimizer()
    return optimizer.optimize_tool(func, **kwargs)

def optimize_tools(tools: List[Callable], **kwargs) -> List[Callable]:
    """Optimize multiple tools"""
    optimizer = get_tool_optimizer()
    return optimizer.optimize_tool_suite(tools, **kwargs)

def create_validation_rules(**kwargs) -> Dict[str, Any]:
    """Create validation rules for tools"""
    optimizer = get_tool_optimizer()
    return optimizer.create_validation_rules(**kwargs)

# Example usage and optimization patterns
def create_optimized_tool_patterns():
    """Create common optimized tool patterns"""
    
    # Pattern 1: Simple tool with basic validation
    @optimize_tool
    def simple_tool(input_text: str) -> str:
        """Simple tool with automatic optimization"""
        return f"Processed: {input_text}"
    
    # Pattern 2: Tool with custom validation
    @optimize_tool(
        description="Advanced tool with validation",
        validation_rules=create_validation_rules(
            required_params=["input_text"],
            type_validation={"input_text": str},
            length_validation={"input_text": (1, 1000)},
            output_validation={"max_length": 2000}
        )
    )
    def advanced_tool(input_text: str, max_length: int = 100) -> str:
        """Advanced tool with custom validation"""
        if len(input_text) > max_length:
            input_text = input_text[:max_length]
        return f"Advanced processing: {input_text}"
    
    # Pattern 3: Tool with examples
    @optimize_tool(
        description="Example tool with usage examples",
        examples=[
            {"input_text": "Hello world", "result": "Processed: Hello world"},
            {"input_text": "Test input", "result": "Processed: Test input"}
        ]
    )
    def example_tool(input_text: str) -> str:
        """Tool with usage examples"""
        return f"Processed: {input_text}"
    
    return [simple_tool, advanced_tool, example_tool]

# Initialize tool optimization patterns
def initialize_tool_patterns():
    """Initialize common tool optimization patterns"""
    try:
        patterns = create_optimized_tool_patterns()
        logger.info(f"Initialized {len(patterns)} tool optimization patterns")
        return patterns
    except Exception as e:
        logger.error(f"Failed to initialize tool patterns: {str(e)}")
        return []

# Initialize on module import
initialize_tool_patterns()
