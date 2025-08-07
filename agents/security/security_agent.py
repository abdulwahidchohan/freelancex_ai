"""FreelanceX.AI Security Agent - OpenAI Agents SDK Implementation
Specialized agent for security and data protection
"""

from agents import Agent, tool
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SecurityAssessment(BaseModel):
    """Security assessment report"""
    risk_level: str
    vulnerabilities: List[Dict[str, Any]]
    compliance_issues: Optional[List[Dict[str, Any]]] = None
    recommendations: List[Dict[str, Any]]
    priority_actions: List[str]

class DataProtectionPlan(BaseModel):
    """Data protection plan"""
    data_types: List[Dict[str, Any]]
    protection_measures: Dict[str, List[str]]
    access_controls: List[Dict[str, Any]]
    incident_response: Dict[str, Any]
    compliance_considerations: Optional[List[str]] = None

@tool
def perform_security_assessment(system_description: str, current_measures: Optional[Dict[str, Any]] = None) -> SecurityAssessment:
    """Perform a security assessment and identify vulnerabilities
    
    Args:
        system_description: Description of the system to assess
        current_measures: Optional description of current security measures
    
    Returns:
        Security assessment with vulnerabilities and recommendations
    """
    measures = current_measures or {}
    vulns = []
    if not measures.get("rate_limiting"):
        vulns.append({"area": "API", "issue": "No rate limiting"})
    if not measures.get("encryption_at_rest"):
        vulns.append({"area": "Data", "issue": "No encryption at rest"})
    compliance = [{"framework": "GDPR", "status": "partial"}]
    recs = [
        {"action": "Enable rate limiting"},
        {"action": "Encrypt sensitive data at rest"},
    ]
    priority = ["Rate limiting", "Backups & encryption"]
    return SecurityAssessment(
        risk_level="medium" if vulns else "low",
        vulnerabilities=vulns,
        compliance_issues=compliance,
        recommendations=recs,
        priority_actions=priority,
    )

@tool
def create_data_protection_plan(data_types: List[str], regulatory_requirements: Optional[List[str]] = None) -> DataProtectionPlan:
    """Create a comprehensive data protection plan
    
    Args:
        data_types: Types of data that need protection
        regulatory_requirements: Optional list of regulatory requirements
    
    Returns:
        Data protection plan with measures and controls
    """
    protections = {
        "PII": ["encryption", "access controls", "data minimization"],
        "financial": ["encryption", "auditing"],
    }
    measures = {dt: protections.get(dt.lower(), ["backups", "access logging"]) for dt in data_types}
    access_controls = [{"role": "admin", "scope": "all"}, {"role": "agent", "scope": "limited"}]
    ir = {"detect": "monitoring", "respond": "isolate & notify", "recover": "restore from backup"}
    return DataProtectionPlan(
        data_types=[{"type": dt} for dt in data_types],
        protection_measures=measures,
        access_controls=access_controls,
        incident_response=ir,
        compliance_considerations=regulatory_requirements or [],
    )

# Create security agent
security_agent = Agent(
    name="Security Agent",
    instructions="""You are the Security Agent for FreelanceX.AI, specialized in ensuring system security and data protection.

Your primary responsibilities include:
1. Performing security assessments to identify vulnerabilities
2. Creating data protection plans for sensitive information
3. Providing guidance on security best practices
4. Ensuring compliance with relevant regulations

When performing security assessments:
- Consider various attack vectors and threat models
- Prioritize vulnerabilities by risk level and potential impact
- Provide specific, actionable recommendations
- Balance security needs with usability considerations

When creating data protection plans:
- Consider the specific types of data and their sensitivity
- Recommend appropriate technical and procedural controls
- Address relevant regulatory requirements
- Include incident response procedures

You should focus on practical security measures that protect both the system and user data without creating unnecessary friction.
""",
    tools=[perform_security_assessment, create_data_protection_plan]
)