"""Enhanced Guardrails System - OpenAI Agents SDK Integration
Provides comprehensive guardrails for input validation, content filtering, and safety
"""

import logging
import re
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from agents import input_guardrail, output_guardrail

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GuardrailConfig(BaseModel):
    """Guardrail configuration"""
    input_validation: bool = Field(default=True, description="Enable input validation")
    content_filtering: bool = Field(default=True, description="Enable content filtering")
    rate_limiting: bool = Field(default=True, description="Enable rate limiting")
    safety_checks: bool = Field(default=True, description="Enable safety checks")
    max_input_length: int = Field(default=10000, description="Maximum input length")
    forbidden_keywords: List[str] = Field(default_factory=list, description="Forbidden keywords")
    allowed_domains: List[str] = Field(default_factory=list, description="Allowed domains")

class GuardrailResult(BaseModel):
    """Guardrail validation result"""
    passed: bool = Field(..., description="Validation passed")
    reason: Optional[str] = Field(default=None, description="Reason for failure")
    sanitized_input: Optional[str] = Field(default=None, description="Sanitized input")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Validation metadata")

# Global guardrail configuration
_guardrail_config = GuardrailConfig()

def set_guardrail_config(config: GuardrailConfig):
    """Set global guardrail configuration"""
    global _guardrail_config
    _guardrail_config = config
    logger.info("Updated guardrail configuration")

def get_guardrail_config() -> GuardrailConfig:
    """Get global guardrail configuration"""
    return _guardrail_config

@input_guardrail
def validate_input_safety(input_text: str) -> GuardrailResult:
    """Validate input for safety and appropriateness"""
    try:
        config = get_guardrail_config()
        
        # Check input length
        if len(input_text) > config.max_input_length:
            return GuardrailResult(
                passed=False,
                reason=f"Input too long ({len(input_text)} chars, max {config.max_input_length})",
                metadata={"input_length": len(input_text), "max_length": config.max_input_length}
            )
        
        # Check for forbidden keywords
        if config.forbidden_keywords:
            found_keywords = []
            for keyword in config.forbidden_keywords:
                if keyword.lower() in input_text.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                return GuardrailResult(
                    passed=False,
                    reason=f"Forbidden keywords detected: {', '.join(found_keywords)}",
                    metadata={"forbidden_keywords": found_keywords}
                )
        
        # Check for potentially harmful content
        harmful_patterns = [
            r'\b(hack|crack|exploit|vulnerability|backdoor)\b',
            r'\b(password|credential|token|key)\s*[=:]\s*\w+',
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'data:text/html'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    reason=f"Potentially harmful content detected: {pattern}",
                    metadata={"harmful_pattern": pattern}
                )
        
        # Sanitize input
        sanitized = sanitize_input(input_text)
        
        return GuardrailResult(
            passed=True,
            sanitized_input=sanitized,
            metadata={
                "input_length": len(input_text),
                "sanitized_length": len(sanitized),
                "validation_passed": True
            }
        )
        
    except Exception as e:
        logger.error(f"Input validation failed: {str(e)}")
        return GuardrailResult(
            passed=False,
            reason=f"Validation error: {str(e)}",
            metadata={"error": str(e)}
        )

@input_guardrail
def validate_content_appropriateness(input_text: str) -> GuardrailResult:
    """Validate content for appropriateness"""
    try:
        config = get_guardrail_config()
        
        if not config.content_filtering:
            return GuardrailResult(passed=True, sanitized_input=input_text)
        
        # Check for inappropriate content
        inappropriate_patterns = [
            r'\b(spam|scam|phishing|malware|virus)\b',
            r'\b(illegal|unlawful|criminal)\s+\w+',
            r'\b(hate|discrimination|racism|sexism)\b',
            r'\b(violence|threat|harm|kill)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    reason=f"Inappropriate content detected: {pattern}",
                    metadata={"inappropriate_pattern": pattern}
                )
        
        # Check for excessive repetition
        words = input_text.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
            
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > len(words) * 0.3:  # More than 30% repetition
                return GuardrailResult(
                    passed=False,
                    reason="Excessive word repetition detected",
                    metadata={"max_repetition": max_repetition, "total_words": len(words)}
                )
        
        return GuardrailResult(
            passed=True,
            sanitized_input=input_text,
            metadata={"content_appropriate": True}
        )
        
    except Exception as e:
        logger.error(f"Content validation failed: {str(e)}")
        return GuardrailResult(
            passed=False,
            reason=f"Content validation error: {str(e)}",
            metadata={"error": str(e)}
        )

@output_guardrail
def validate_output_safety(output_text: str) -> GuardrailResult:
    """Validate output for safety and appropriateness"""
    try:
        config = get_guardrail_config()
        
        # Check for sensitive information in output
        sensitive_patterns = [
            r'\b(password|passwd|pwd)\s*[=:]\s*\w+',
            r'\b(api_key|token|secret)\s*[=:]\s*\w+',
            r'\b(email|phone|ssn|credit_card)\s*[=:]\s*\w+',
            r'\b(admin|root|sudo)\s+password',
            r'<script[^>]*>.*?</script>',
            r'javascript:'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, output_text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    reason=f"Sensitive information detected in output: {pattern}",
                    metadata={"sensitive_pattern": pattern}
                )
        
        # Check for potentially harmful code
        harmful_code_patterns = [
            r'rm\s+-rf',
            r'del\s+/s\s+/q',
            r'format\s+c:',
            r'shutdown\s+/s',
            r'kill\s+-9'
        ]
        
        for pattern in harmful_code_patterns:
            if re.search(pattern, output_text, re.IGNORECASE):
                return GuardrailResult(
                    passed=False,
                    reason=f"Potentially harmful code detected: {pattern}",
                    metadata={"harmful_code": pattern}
                )
        
        # Sanitize output
        sanitized = sanitize_output(output_text)
        
        return GuardrailResult(
            passed=True,
            sanitized_input=sanitized,
            metadata={"output_safe": True, "sanitized": True}
        )
        
    except Exception as e:
        logger.error(f"Output validation failed: {str(e)}")
        return GuardrailResult(
            passed=False,
            reason=f"Output validation error: {str(e)}",
            metadata={"error": str(e)}
        )

def sanitize_input(input_text: str) -> str:
    """Sanitize input text"""
    try:
        # Remove HTML tags
        sanitized = re.sub(r'<[^>]+>', '', input_text)
        
        # Remove script tags and content
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove javascript: URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        
        # Remove data: URLs
        sanitized = re.sub(r'data:text/html', '', sanitized, flags=re.IGNORECASE)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Input sanitization failed: {str(e)}")
        return input_text

def sanitize_output(output_text: str) -> str:
    """Sanitize output text"""
    try:
        # Remove any sensitive information patterns
        sensitive_patterns = [
            r'password\s*[=:]\s*\w+',
            r'api_key\s*[=:]\s*\w+',
            r'token\s*[=:]\s*\w+',
            r'secret\s*[=:]\s*\w+'
        ]
        
        sanitized = output_text
        for pattern in sensitive_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        
        # Remove potentially harmful code
        harmful_patterns = [
            r'rm\s+-rf\s+\w+',
            r'del\s+/s\s+/q\s+\w+',
            r'format\s+c:\s*',
            r'shutdown\s+/s\s*',
            r'kill\s+-9\s+\d+'
        ]
        
        for pattern in harmful_patterns:
            sanitized = re.sub(pattern, '[BLOCKED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Output sanitization failed: {str(e)}")
        return output_text

def create_guardrail_suite() -> Dict[str, Any]:
    """Create a comprehensive guardrail suite"""
    return {
        "input_guardrails": [
            validate_input_safety,
            validate_content_appropriateness
        ],
        "output_guardrails": [
            validate_output_safety
        ],
        "config": get_guardrail_config()
    }

def apply_guardrails_to_agent(agent: Any, guardrail_suite: Dict[str, Any]):
    """Apply guardrails to an agent"""
    try:
        # Apply input guardrails
        for guardrail in guardrail_suite.get("input_guardrails", []):
            agent.input_guardrails.append(guardrail)
        
        # Apply output guardrails
        for guardrail in guardrail_suite.get("output_guardrails", []):
            agent.output_guardrails.append(guardrail)
        
        logger.info(f"Applied guardrails to agent: {getattr(agent, 'name', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Failed to apply guardrails to agent: {str(e)}")

# Initialize default guardrail configuration
def initialize_default_guardrails():
    """Initialize default guardrail configuration"""
    default_config = GuardrailConfig(
        input_validation=True,
        content_filtering=True,
        rate_limiting=True,
        safety_checks=True,
        max_input_length=10000,
        forbidden_keywords=[
            "hack", "crack", "exploit", "vulnerability", "backdoor",
            "password", "credential", "token", "key"
        ],
        allowed_domains=[]
    )
    
    set_guardrail_config(default_config)
    logger.info("Initialized default guardrail configuration")

# Initialize guardrails on module import
initialize_default_guardrails()
