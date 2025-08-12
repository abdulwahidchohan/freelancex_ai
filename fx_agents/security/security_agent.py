"""FreelanceX.AI Security Agent - OpenAI Agents SDK Implementation
Specialized agent for security and data protection
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityAssessment(BaseModel):
    """Security assessment report"""
    risk_level: str = Field(..., description="Overall risk level")
    vulnerabilities: List[Dict[str, Any]] = Field(..., description="Identified vulnerabilities")
    compliance_issues: Optional[List[Dict[str, Any]]] = Field(None, description="Compliance issues")
    recommendations: List[Dict[str, Any]] = Field(..., description="Security recommendations")
    priority_actions: List[str] = Field(..., description="Priority actions to take")
    threat_analysis: Dict[str, Any] = Field(..., description="Threat analysis")
    security_score: float = Field(..., description="Security score (0-100)")

class DataProtectionPlan(BaseModel):
    """Data protection plan"""
    data_types: List[Dict[str, Any]] = Field(..., description="Types of data to protect")
    protection_measures: Dict[str, List[str]] = Field(..., description="Protection measures by data type")
    access_controls: List[Dict[str, Any]] = Field(..., description="Access control policies")
    incident_response: Dict[str, Any] = Field(..., description="Incident response procedures")
    compliance_considerations: Optional[List[str]] = Field(None, description="Compliance considerations")
    encryption_strategy: Dict[str, Any] = Field(..., description="Encryption strategy")
    monitoring_plan: List[str] = Field(..., description="Monitoring and detection plan")

class SecurityPolicy(BaseModel):
    """Security policy framework"""
    policy_name: str = Field(..., description="Policy name")
    scope: str = Field(..., description="Policy scope")
    objectives: List[str] = Field(..., description="Policy objectives")
    requirements: List[str] = Field(..., description="Security requirements")
    procedures: List[Dict[str, Any]] = Field(..., description="Security procedures")
    enforcement: Dict[str, Any] = Field(..., description="Enforcement mechanisms")

class ThreatModel(BaseModel):
    """Threat model analysis"""
    threat_actors: List[Dict[str, Any]] = Field(..., description="Potential threat actors")
    attack_vectors: List[Dict[str, Any]] = Field(..., description="Attack vectors")
    vulnerabilities: List[Dict[str, Any]] = Field(..., description="System vulnerabilities")
    mitigations: List[Dict[str, Any]] = Field(..., description="Mitigation strategies")
    risk_matrix: Dict[str, Any] = Field(..., description="Risk assessment matrix")

@tool
def perform_security_assessment(system_description: str, current_measures: Optional[Dict[str, Any]] = None) -> SecurityAssessment:
    """Perform a security assessment and identify vulnerabilities
    
    Args:
        system_description: Description of the system to assess
        current_measures: Optional description of current security measures
    
    Returns:
        Security assessment with vulnerabilities and recommendations
    """
    try:
        logger.info("Performing security assessment")
        
        # Analyze system description for security concerns
        system_lower = system_description.lower()
        vulnerabilities = []
        compliance_issues = []
        recommendations = []
        
        # Check for common security issues
        if "api" in system_lower and "authentication" not in system_lower:
            vulnerabilities.append({
                "area": "API Security",
                "issue": "Missing authentication mechanism",
                "severity": "high",
                "impact": "Unauthorized access to API endpoints"
            })
            recommendations.append({
                "action": "Implement API authentication",
                "priority": "high",
                "effort": "medium",
                "description": "Add JWT tokens or API keys for authentication"
            })
        
        if "database" in system_lower and "encryption" not in system_lower:
            vulnerabilities.append({
                "area": "Data Security",
                "issue": "No database encryption",
                "severity": "high",
                "impact": "Data exposure in case of breach"
            })
            recommendations.append({
                "action": "Enable database encryption",
                "priority": "high",
                "effort": "medium",
                "description": "Implement encryption at rest for sensitive data"
            })
        
        if "user" in system_lower and "password" in system_lower:
            if "rate limiting" not in system_lower:
                vulnerabilities.append({
                    "area": "Authentication",
                    "issue": "No rate limiting on login attempts",
                    "severity": "medium",
                    "impact": "Brute force attack vulnerability"
                })
                recommendations.append({
                    "action": "Implement rate limiting",
                    "priority": "medium",
                    "effort": "low",
                    "description": "Add rate limiting to prevent brute force attacks"
                })
        
        if "file upload" in system_lower or "upload" in system_lower:
            vulnerabilities.append({
                "area": "File Security",
                "issue": "Potential file upload vulnerabilities",
                "severity": "medium",
                "impact": "Malicious file uploads and code execution"
            })
            recommendations.append({
                "action": "Implement file upload security",
                "priority": "medium",
                "effort": "medium",
                "description": "Add file type validation, size limits, and scanning"
            })
        
        # Check for compliance issues
        if "personal" in system_lower or "user data" in system_lower:
            compliance_issues.append({
                "framework": "GDPR",
                "status": "partial",
                "issues": ["Data minimization", "User consent", "Right to deletion"]
            })
            compliance_issues.append({
                "framework": "CCPA",
                "status": "partial",
                "issues": ["Privacy notice", "Opt-out mechanisms"]
            })
        
        # Determine risk level
        high_severity_count = len([v for v in vulnerabilities if v.get("severity") == "high"])
        medium_severity_count = len([v for v in vulnerabilities if v.get("severity") == "medium"])
        
        if high_severity_count > 0:
            risk_level = "high"
        elif medium_severity_count > 2:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Priority actions
        priority_actions = []
        high_priority_recs = [r for r in recommendations if r.get("priority") == "high"]
        medium_priority_recs = [r for r in recommendations if r.get("priority") == "medium"]
        
        priority_actions.extend([r["action"] for r in high_priority_recs])
        priority_actions.extend([r["action"] for r in medium_priority_recs[:3]])
        
        # Threat analysis
        threat_analysis = {
            "external_threats": ["Malicious actors", "Automated attacks", "Data breaches"],
            "internal_threats": ["Insider threats", "Accidental exposure", "Privilege abuse"],
            "attack_surface": len(vulnerabilities),
            "risk_factors": ["Data sensitivity", "System exposure", "User base size"]
        }
        
        # Calculate security score
        base_score = 100
        score_deductions = high_severity_count * 25 + medium_severity_count * 10
        security_score = max(0, base_score - score_deductions)
        
        return SecurityAssessment(
            risk_level=risk_level,
            vulnerabilities=vulnerabilities,
            compliance_issues=compliance_issues,
            recommendations=recommendations,
            priority_actions=priority_actions,
            threat_analysis=threat_analysis,
            security_score=security_score
        )
        
    except Exception as e:
        logger.error(f"Error performing security assessment: {e}")
        return SecurityAssessment(
            risk_level="unknown",
            vulnerabilities=[{"area": "Assessment", "issue": f"Error: {str(e)}"}],
            recommendations=[{"action": "Review system description"}],
            priority_actions=["Troubleshoot assessment process"],
            threat_analysis={"error": str(e)},
            security_score=0.0
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
    try:
        logger.info("Creating data protection plan")
        
        # Define protection measures by data type
        protection_templates = {
            "pii": ["encryption_at_rest", "encryption_in_transit", "access_controls", "data_minimization", "consent_management"],
            "financial": ["encryption_at_rest", "encryption_in_transit", "audit_logging", "access_controls", "pci_compliance"],
            "health": ["encryption_at_rest", "encryption_in_transit", "hipaa_compliance", "access_controls", "audit_logging"],
            "intellectual_property": ["encryption_at_rest", "access_controls", "watermarking", "audit_logging"],
            "credentials": ["hashing", "salt", "rate_limiting", "multi_factor_auth", "session_management"]
        }
        
        # Generate protection measures for each data type
        protection_measures = {}
        for data_type in data_types:
            data_type_lower = data_type.lower()
            if data_type_lower in protection_templates:
                protection_measures[data_type] = protection_templates[data_type_lower]
            else:
                protection_measures[data_type] = ["encryption_at_rest", "access_controls", "audit_logging", "backup_encryption"]
        
        # Define access controls
        access_controls = [
            {
                "role": "admin",
                "scope": "all_data",
                "permissions": ["read", "write", "delete", "manage_users"],
                "restrictions": ["audit_logging", "approval_required"]
            },
            {
                "role": "user",
                "scope": "own_data",
                "permissions": ["read", "write"],
                "restrictions": ["no_delete", "data_retention"]
            },
            {
                "role": "analyst",
                "scope": "anonymized_data",
                "permissions": ["read"],
                "restrictions": ["no_pii", "aggregated_only"]
            }
        ]
        
        # Incident response procedures
        incident_response = {
            "detection": {
                "methods": ["automated_monitoring", "user_reports", "security_alerts"],
                "escalation": ["immediate_notification", "incident_team_activation"]
            },
            "response": {
                "containment": ["isolate_affected_systems", "disable_compromised_accounts"],
                "investigation": ["forensic_analysis", "root_cause_analysis"],
                "notification": ["internal_stakeholders", "regulatory_bodies", "affected_users"]
            },
            "recovery": {
                "system_restoration": ["backup_verification", "system_restoration", "security_patching"],
                "post_incident": ["lessons_learned", "policy_updates", "training"]
            }
        }
        
        # Compliance considerations
        compliance_considerations = regulatory_requirements or []
        if not compliance_considerations:
            compliance_considerations = [
                "GDPR compliance for EU data",
                "CCPA compliance for California residents",
                "Industry-specific regulations",
                "Data retention policies"
            ]
        
        # Encryption strategy
        encryption_strategy = {
            "at_rest": {
                "algorithm": "AES-256",
                "key_management": "hardware_security_module",
                "scope": "all_sensitive_data"
            },
            "in_transit": {
                "protocol": "TLS_1_3",
                "certificate_management": "automated_renewal",
                "scope": "all_communications"
            },
            "key_rotation": {
                "frequency": "90_days",
                "automation": "enabled",
                "backup_keys": "secure_storage"
            }
        }
        
        # Monitoring plan
        monitoring_plan = [
            "Real-time security event monitoring",
            "Anomaly detection for data access patterns",
            "Regular security log analysis",
            "Automated threat detection and alerting",
            "Periodic security assessments and penetration testing"
        ]
        
        return DataProtectionPlan(
            data_types=[{"type": dt, "sensitivity": "high" if dt.lower() in ["pii", "financial", "health"] else "medium"} for dt in data_types],
            protection_measures=protection_measures,
            access_controls=access_controls,
            incident_response=incident_response,
            compliance_considerations=compliance_considerations,
            encryption_strategy=encryption_strategy,
            monitoring_plan=monitoring_plan
        )
        
    except Exception as e:
        logger.error(f"Error creating data protection plan: {e}")
        return DataProtectionPlan(
            data_types=[{"type": "error", "sensitivity": "unknown"}],
            protection_measures={"error": ["Review data types"]},
            access_controls=[],
            incident_response={"error": str(e)},
            compliance_considerations=["Review requirements"],
            encryption_strategy={"error": "Review encryption needs"},
            monitoring_plan=["Troubleshoot plan creation"]
        )

@tool
def develop_security_policy(organization_type: str, data_sensitivity: str, compliance_requirements: List[str]) -> SecurityPolicy:
    """Develop a comprehensive security policy
    
    Args:
        organization_type: Type of organization
        data_sensitivity: Level of data sensitivity
        compliance_requirements: List of compliance requirements
    
    Returns:
        SecurityPolicy with comprehensive security framework
    """
    try:
        logger.info("Developing security policy")
        
        # Generate policy name
        policy_name = f"{organization_type.title()} Security Policy"
        
        # Define scope based on organization type
        scope = "Organization-wide security policy"
        if organization_type.lower() in ["startup", "small_business"]:
            scope = "Small business security framework"
        elif organization_type.lower() in ["enterprise", "large_corporation"]:
            scope = "Enterprise security governance"
        
        # Define objectives
        objectives = [
            "Protect sensitive data and information assets",
            "Ensure compliance with regulatory requirements",
            "Maintain system availability and integrity",
            "Prevent unauthorized access and data breaches",
            "Establish security awareness and training programs"
        ]
        
        # Generate requirements based on data sensitivity and compliance
        requirements = []
        
        # Base requirements
        requirements.extend([
            "Implement strong authentication mechanisms",
            "Encrypt sensitive data at rest and in transit",
            "Establish access control policies",
            "Maintain security logs and monitoring",
            "Conduct regular security assessments"
        ])
        
        # Data sensitivity requirements
        if data_sensitivity.lower() == "high":
            requirements.extend([
                "Implement multi-factor authentication",
                "Use hardware security modules for key management",
                "Conduct background checks for personnel",
                "Implement data loss prevention measures",
                "Establish incident response procedures"
            ])
        
        # Compliance-specific requirements
        for compliance in compliance_requirements:
            if "gdpr" in compliance.lower():
                requirements.extend([
                    "Implement data minimization principles",
                    "Establish user consent management",
                    "Provide data portability mechanisms",
                    "Implement right to deletion procedures"
                ])
            elif "hipaa" in compliance.lower():
                requirements.extend([
                    "Implement administrative safeguards",
                    "Establish physical security measures",
                    "Implement technical safeguards",
                    "Conduct regular risk assessments"
                ])
            elif "pci" in compliance.lower():
                requirements.extend([
                    "Implement cardholder data protection",
                    "Establish vulnerability management",
                    "Implement access control measures",
                    "Conduct regular security testing"
                ])
        
        # Security procedures
        procedures = [
            {
                "name": "Access Management",
                "description": "Procedures for granting and revoking access",
                "steps": ["Request submission", "Approval process", "Access provisioning", "Regular review"]
            },
            {
                "name": "Incident Response",
                "description": "Procedures for handling security incidents",
                "steps": ["Detection", "Containment", "Investigation", "Recovery", "Lessons learned"]
            },
            {
                "name": "Data Classification",
                "description": "Procedures for classifying data sensitivity",
                "steps": ["Data inventory", "Risk assessment", "Classification labeling", "Protection measures"]
            },
            {
                "name": "Security Training",
                "description": "Procedures for security awareness training",
                "steps": ["Initial training", "Regular updates", "Phishing simulations", "Compliance verification"]
            }
        ]
        
        # Enforcement mechanisms
        enforcement = {
            "monitoring": ["Automated compliance checking", "Regular audits", "Security metrics tracking"],
            "consequences": ["Progressive disciplinary actions", "Access revocation", "Legal consequences"],
            "reporting": ["Security incident reporting", "Compliance reporting", "Executive dashboards"]
        }
        
        return SecurityPolicy(
            policy_name=policy_name,
            scope=scope,
            objectives=objectives,
            requirements=requirements,
            procedures=procedures,
            enforcement=enforcement
        )
        
    except Exception as e:
        logger.error(f"Error developing security policy: {e}")
        return SecurityPolicy(
            policy_name="Error in policy development",
            scope="Review organization type",
            objectives=["Review policy requirements"],
            requirements=["Troubleshoot policy creation"],
            procedures=[],
            enforcement={"error": str(e)}
        )

@tool
def create_threat_model(system_architecture: str, data_assets: List[str], user_types: List[str]) -> ThreatModel:
    """Create a comprehensive threat model
    
    Args:
        system_architecture: Description of system architecture
        data_assets: List of data assets to protect
        user_types: List of user types accessing the system
    
    Returns:
        ThreatModel with threat analysis and mitigations
    """
    try:
        logger.info("Creating threat model")
        
        # Define threat actors
        threat_actors = [
            {
                "type": "External Attacker",
                "motivation": "Financial gain, data theft, disruption",
                "capabilities": "High technical skills, automated tools",
                "targets": ["User credentials", "Sensitive data", "System availability"]
            },
            {
                "type": "Insider Threat",
                "motivation": "Financial gain, revenge, accidental",
                "capabilities": "Legitimate access, knowledge of systems",
                "targets": ["Confidential data", "System access", "Intellectual property"]
            },
            {
                "type": "State Actor",
                "motivation": "Intelligence gathering, economic espionage",
                "capabilities": "Advanced persistent threats, significant resources",
                "targets": ["Trade secrets", "User data", "Infrastructure"]
            }
        ]
        
        # Define attack vectors
        attack_vectors = [
            {
                "vector": "Phishing",
                "description": "Social engineering attacks via email",
                "likelihood": "high",
                "impact": "medium",
                "mitigation": "User training, email filtering"
            },
            {
                "vector": "SQL Injection",
                "description": "Database attacks through input validation",
                "likelihood": "medium",
                "impact": "high",
                "mitigation": "Input validation, prepared statements"
            },
            {
                "vector": "Cross-Site Scripting",
                "description": "Client-side code injection attacks",
                "likelihood": "medium",
                "impact": "medium",
                "mitigation": "Output encoding, CSP headers"
            },
            {
                "vector": "Privilege Escalation",
                "description": "Gaining elevated system access",
                "likelihood": "low",
                "impact": "high",
                "mitigation": "Principle of least privilege, access controls"
            }
        ]
        
        # Identify vulnerabilities based on architecture
        vulnerabilities = []
        arch_lower = system_architecture.lower()
        
        if "web" in arch_lower:
            vulnerabilities.append({
                "type": "Web Application",
                "description": "Common web application vulnerabilities",
                "severity": "medium",
                "mitigation": "Security testing, code review"
            })
        
        if "api" in arch_lower:
            vulnerabilities.append({
                "type": "API Security",
                "description": "API authentication and authorization",
                "severity": "high",
                "mitigation": "API security testing, rate limiting"
            })
        
        if "database" in arch_lower:
            vulnerabilities.append({
                "type": "Database Security",
                "description": "Database access and encryption",
                "severity": "high",
                "mitigation": "Database security, encryption"
            })
        
        # Generate mitigations
        mitigations = [
            {
                "threat": "Data Breach",
                "strategy": "Defense in depth",
                "measures": ["Encryption", "Access controls", "Monitoring", "Incident response"]
            },
            {
                "threat": "Unauthorized Access",
                "strategy": "Multi-layered authentication",
                "measures": ["MFA", "Role-based access", "Session management", "Audit logging"]
            },
            {
                "threat": "System Compromise",
                "strategy": "Security hardening",
                "measures": ["Regular patching", "Security testing", "Vulnerability management", "Backup strategies"]
            }
        ]
        
        # Risk matrix
        risk_matrix = {
            "high_impact_high_likelihood": ["Immediate action required"],
            "high_impact_low_likelihood": ["Monitor and mitigate"],
            "low_impact_high_likelihood": ["Implement controls"],
            "low_impact_low_likelihood": ["Accept and monitor"]
        }
        
        return ThreatModel(
            threat_actors=threat_actors,
            attack_vectors=attack_vectors,
            vulnerabilities=vulnerabilities,
            mitigations=mitigations,
            risk_matrix=risk_matrix
        )
        
    except Exception as e:
        logger.error(f"Error creating threat model: {e}")
        return ThreatModel(
            threat_actors=[{"type": "Error", "motivation": str(e)}],
            attack_vectors=[],
            vulnerabilities=[{"type": "Error", "description": str(e)}],
            mitigations=[],
            risk_matrix={"error": "Review system architecture"}
        )

# Create security agent
security_agent = Agent(
    name="Security Agent",
    instructions="""You are the Security Agent for FreelanceX.AI, specialized in ensuring system security and data protection.

Your primary responsibilities include:
1. Performing comprehensive security assessments to identify vulnerabilities
2. Creating data protection plans for sensitive information
3. Developing security policies and frameworks
4. Creating threat models and risk assessments
5. Providing guidance on security best practices
6. Ensuring compliance with relevant regulations

When performing security assessments:
- Consider various attack vectors and threat models
- Prioritize vulnerabilities by risk level and potential impact
- Provide specific, actionable recommendations
- Balance security needs with usability considerations
- Include compliance and regulatory considerations

When creating data protection plans:
- Consider the specific types of data and their sensitivity
- Recommend appropriate technical and procedural controls
- Address relevant regulatory requirements
- Include incident response procedures
- Plan for monitoring and detection

When developing security policies:
- Align with organizational goals and culture
- Consider industry standards and best practices
- Include clear procedures and enforcement mechanisms
- Address training and awareness requirements

When creating threat models:
- Identify potential threat actors and their motivations
- Analyze attack vectors and system vulnerabilities
- Develop appropriate mitigation strategies
- Assess risks and prioritize responses

You should focus on practical security measures that protect both the system and user data while maintaining usability and compliance with relevant regulations.
""",
    tools=[perform_security_assessment, create_data_protection_plan, develop_security_policy, create_threat_model]
)