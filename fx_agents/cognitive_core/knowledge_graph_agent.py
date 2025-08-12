"""FreelanceX.AI Knowledge Graph Agent
Dynamic skill linking & inference
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


class SkillRelation(BaseModel):
    source: str = Field(..., description="Source skill or concept")
    target: str = Field(..., description="Target skill or concept")
    relation: str = Field(..., description="Type of relationship")
    confidence: float = Field(..., description="Confidence score (0-1)")
    context: str = Field(..., description="Context of the relationship")


class KnowledgeNode(BaseModel):
    id: str = Field(..., description="Node identifier")
    name: str = Field(..., description="Node name")
    type: str = Field(..., description="Node type (skill, tool, concept, etc.)")
    description: str = Field(..., description="Node description")
    attributes: Dict[str, Any] = Field(..., description="Node attributes")
    connections: List[str] = Field(..., description="Connected node IDs")


class KnowledgeGraph(BaseModel):
    nodes: List[KnowledgeNode] = Field(..., description="Graph nodes")
    relationships: List[SkillRelation] = Field(..., description="Graph relationships")
    metadata: Dict[str, Any] = Field(..., description="Graph metadata")
    last_updated: str = Field(..., description="Last update timestamp")


class SkillRecommendation(BaseModel):
    skill: str = Field(..., description="Recommended skill")
    reason: str = Field(..., description="Reason for recommendation")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    learning_path: List[str] = Field(..., description="Suggested learning path")


@tool
def infer_related_skills(skills: List[str], context: Optional[str] = None) -> List[SkillRelation]:
    """
    Infer related skills and concepts based on input skills.
    
    Args:
        skills: List of skills to analyze
        context: Optional context for relationship inference
        
    Returns:
        List of SkillRelation with inferred relationships
    """
    try:
        logger.info(f"Inferring related skills for: {skills}")
        
        relationships = []
        
        # Dynamic skill relationship mapping
        skill_relationships = {
            "python": [
                ("pydantic", "uses", 0.9, "Data validation and serialization"),
                ("fastapi", "popular_with", 0.8, "Web framework development"),
                ("sqlalchemy", "uses", 0.7, "Database ORM"),
                ("pytest", "testing", 0.8, "Unit testing framework"),
                ("pandas", "data_analysis", 0.7, "Data manipulation and analysis")
            ],
            "javascript": [
                ("react", "frontend", 0.9, "User interface development"),
                ("node.js", "backend", 0.8, "Server-side development"),
                ("typescript", "enhances", 0.9, "Type safety and development experience"),
                ("express", "web_framework", 0.8, "Web application framework"),
                ("jest", "testing", 0.8, "Testing framework")
            ],
            "react": [
                ("next.js", "framework", 0.9, "Full-stack React framework"),
                ("typescript", "enhances", 0.8, "Type safety"),
                ("redux", "state_management", 0.7, "Application state management"),
                ("tailwind", "styling", 0.7, "Utility-first CSS framework"),
                ("jest", "testing", 0.8, "Testing framework")
            ],
            "machine_learning": [
                ("python", "primary_language", 0.9, "Primary language for ML"),
                ("tensorflow", "framework", 0.8, "Deep learning framework"),
                ("pandas", "data_processing", 0.8, "Data manipulation"),
                ("scikit-learn", "library", 0.8, "Machine learning library"),
                ("jupyter", "development", 0.7, "Interactive development environment")
            ],
            "data_science": [
                ("python", "primary_language", 0.9, "Primary language for data science"),
                ("pandas", "data_manipulation", 0.9, "Data manipulation and analysis"),
                ("numpy", "numerical_computing", 0.8, "Numerical computing"),
                ("matplotlib", "visualization", 0.8, "Data visualization"),
                ("sql", "data_querying", 0.7, "Database querying")
            ]
        }
        
        # Generate relationships for each skill
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check predefined relationships
            if skill_lower in skill_relationships:
                for target, relation, confidence, context_desc in skill_relationships[skill_lower]:
                    relationships.append(SkillRelation(
                        source=skill,
                        target=target,
                        relation=relation,
                        confidence=confidence,
                        context=context_desc
                    ))
            
            # Generate dynamic relationships based on skill patterns
            if "api" in skill_lower or "rest" in skill_lower:
                relationships.append(SkillRelation(
                    source=skill,
                    target="authentication",
                    relation="requires",
                    confidence=0.7,
                    context="API development typically requires authentication"
                ))
            
            if "database" in skill_lower or "sql" in skill_lower:
                relationships.append(SkillRelation(
                    source=skill,
                    target="data_modeling",
                    relation="requires",
                    confidence=0.8,
                    context="Database work requires data modeling skills"
                ))
            
            if "frontend" in skill_lower or "ui" in skill_lower:
                relationships.append(SkillRelation(
                    source=skill,
                    target="responsive_design",
                    relation="includes",
                    confidence=0.8,
                    context="Frontend development includes responsive design"
                ))
        
        # Remove duplicates based on source-target pairs
        unique_relationships = []
        seen_pairs = set()
        for rel in relationships:
            pair = (rel.source.lower(), rel.target.lower())
            if pair not in seen_pairs:
                unique_relationships.append(rel)
                seen_pairs.add(pair)
        
        return unique_relationships
        
    except Exception as e:
        logger.error(f"Error inferring related skills: {e}")
        return [SkillRelation(
            source=skills[0] if skills else "unknown",
            target="error",
            relation="error",
            confidence=0.0,
            context=f"Error in inference: {str(e)}"
        )]


@tool
def build_knowledge_graph(nodes: List[Dict[str, Any]], relationships: List[Dict[str, Any]]) -> KnowledgeGraph:
    """
    Build a comprehensive knowledge graph from nodes and relationships.
    
    Args:
        nodes: List of node data
        relationships: List of relationship data
        
    Returns:
        KnowledgeGraph with structured knowledge representation
    """
    try:
        logger.info("Building knowledge graph")
        
        # Convert nodes to KnowledgeNode objects
        knowledge_nodes = []
        for node_data in nodes:
            node = KnowledgeNode(
                id=node_data.get("id", str(len(knowledge_nodes))),
                name=node_data.get("name", "Unknown"),
                type=node_data.get("type", "concept"),
                description=node_data.get("description", ""),
                attributes=node_data.get("attributes", {}),
                connections=[]
            )
            knowledge_nodes.append(node)
        
        # Convert relationships to SkillRelation objects
        skill_relations = []
        for rel_data in relationships:
            relation = SkillRelation(
                source=rel_data.get("source", ""),
                target=rel_data.get("target", ""),
                relation=rel_data.get("relation", "related"),
                confidence=rel_data.get("confidence", 0.5),
                context=rel_data.get("context", "")
            )
            skill_relations.append(relation)
        
        # Build metadata
        metadata = {
            "total_nodes": len(knowledge_nodes),
            "total_relationships": len(skill_relations),
            "node_types": list(set(node.type for node in knowledge_nodes)),
            "relationship_types": list(set(rel.relation for rel in skill_relations)),
            "average_confidence": sum(rel.confidence for rel in skill_relations) / max(len(skill_relations), 1)
        }
        
        return KnowledgeGraph(
            nodes=knowledge_nodes,
            relationships=skill_relations,
            metadata=metadata,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error building knowledge graph: {e}")
        return KnowledgeGraph(
            nodes=[],
            relationships=[],
            metadata={"error": str(e)},
            last_updated=datetime.now().isoformat()
        )


@tool
def recommend_skills(current_skills: List[str], target_role: Optional[str] = None) -> List[SkillRecommendation]:
    """
    Recommend skills based on current skills and target role.
    
    Args:
        current_skills: List of current skills
        target_role: Optional target role or position
        
    Returns:
        List of SkillRecommendation with skill suggestions
    """
    try:
        logger.info(f"Recommending skills for role: {target_role}")
        
        recommendations = []
        
        # Role-based skill mappings
        role_skill_mappings = {
            "frontend_developer": [
                ("TypeScript", "Enhances JavaScript development with type safety", 0.9, ["JavaScript", "TypeScript", "Advanced TypeScript"]),
                ("React", "Popular frontend framework for building user interfaces", 0.8, ["JavaScript", "React", "Advanced React Patterns"]),
                ("CSS Frameworks", "Essential for modern UI development", 0.7, ["CSS", "Tailwind CSS", "Styled Components"])
            ],
            "backend_developer": [
                ("Python", "Versatile language for backend development", 0.9, ["Programming Basics", "Python", "FastAPI/Django"]),
                ("Database Design", "Essential for data persistence", 0.8, ["SQL", "Database Design", "ORM Usage"]),
                ("API Design", "Core skill for backend development", 0.8, ["HTTP", "REST APIs", "GraphQL"])
            ],
            "data_scientist": [
                ("Python", "Primary language for data science", 0.9, ["Python", "Pandas", "NumPy"]),
                ("Machine Learning", "Core skill for data analysis", 0.8, ["Statistics", "ML Basics", "Advanced ML"]),
                ("Data Visualization", "Essential for communicating insights", 0.7, ["Matplotlib", "Seaborn", "Plotly"])
            ],
            "devops_engineer": [
                ("Docker", "Containerization technology", 0.9, ["Linux", "Docker", "Kubernetes"]),
                ("CI/CD", "Continuous integration and deployment", 0.8, ["Git", "CI/CD Basics", "Advanced CI/CD"]),
                ("Cloud Platforms", "Essential for modern infrastructure", 0.8, ["AWS/Azure", "Cloud Services", "Infrastructure as Code"])
            ]
        }
        
        # Generate recommendations based on target role
        if target_role and target_role.lower() in role_skill_mappings:
            for skill, reason, relevance, learning_path in role_skill_mappings[target_role.lower()]:
                if skill.lower() not in [s.lower() for s in current_skills]:
                    recommendations.append(SkillRecommendation(
                        skill=skill,
                        reason=reason,
                        relevance_score=relevance,
                        learning_path=learning_path
                    ))
        
        # Generate recommendations based on current skills
        if not recommendations:
            skill_gaps = {
                "python": ("FastAPI", "Modern web framework for Python", 0.8, ["Python", "FastAPI", "Advanced FastAPI"]),
                "javascript": ("TypeScript", "Type-safe JavaScript", 0.9, ["JavaScript", "TypeScript", "Advanced TypeScript"]),
                "react": ("Next.js", "Full-stack React framework", 0.8, ["React", "Next.js", "Advanced Next.js"]),
                "sql": ("Database Design", "Advanced database concepts", 0.7, ["SQL", "Database Design", "Performance Optimization"])
            }
            
            for current_skill in current_skills:
                skill_lower = current_skill.lower()
                if skill_lower in skill_gaps:
                    gap_skill, reason, relevance, learning_path = skill_gaps[skill_lower]
                    recommendations.append(SkillRecommendation(
                        skill=gap_skill,
                        reason=reason,
                        relevance_score=relevance,
                        learning_path=learning_path
                    ))
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
        
    except Exception as e:
        logger.error(f"Error recommending skills: {e}")
        return [SkillRecommendation(
            skill="Error in recommendation",
            reason=f"Error: {str(e)}",
            relevance_score=0.0,
            learning_path=[]
        )]


@tool
def analyze_skill_gaps(current_skills: List[str], required_skills: List[str]) -> Dict[str, Any]:
    """
    Analyze gaps between current skills and required skills.
    
    Args:
        current_skills: List of current skills
        required_skills: List of required skills
        
    Returns:
        Dictionary with gap analysis results
    """
    try:
        logger.info("Analyzing skill gaps")
        
        current_lower = [skill.lower() for skill in current_skills]
        required_lower = [skill.lower() for skill in required_skills]
        
        # Find missing skills
        missing_skills = [skill for skill in required_skills if skill.lower() not in current_lower]
        
        # Find matching skills
        matching_skills = [skill for skill in required_skills if skill.lower() in current_lower]
        
        # Calculate coverage percentage
        coverage = len(matching_skills) / len(required_skills) if required_skills else 0
        
        # Categorize gaps
        gap_categories = {
            "critical": [],
            "important": [],
            "nice_to_have": []
        }
        
        for skill in missing_skills:
            # Simple categorization based on skill importance
            if any(keyword in skill.lower() for keyword in ["python", "javascript", "sql", "api"]):
                gap_categories["critical"].append(skill)
            elif any(keyword in skill.lower() for keyword in ["testing", "git", "docker"]):
                gap_categories["important"].append(skill)
            else:
                gap_categories["nice_to_have"].append(skill)
        
        return {
            "missing_skills": missing_skills,
            "matching_skills": matching_skills,
            "coverage_percentage": round(coverage * 100, 2),
            "gap_categories": gap_categories,
            "total_gaps": len(missing_skills),
            "priority_order": gap_categories["critical"] + gap_categories["important"] + gap_categories["nice_to_have"]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing skill gaps: {e}")
        return {
            "error": str(e),
            "missing_skills": [],
            "matching_skills": [],
            "coverage_percentage": 0.0,
            "gap_categories": {},
            "total_gaps": 0,
            "priority_order": []
        }


knowledge_graph_agent = Agent(
    name="Knowledge Graph Agent",
    instructions="""You relate skills and concepts to help routing and recommendations in FreelanceX.AI.

Your responsibilities include:
- Inferring related skills and concepts
- Building and maintaining knowledge graphs
- Recommending skills based on current capabilities and goals
- Analyzing skill gaps and learning paths
- Providing insights for career development and skill enhancement

Always consider the context and relevance of skill relationships.""",
    tools=[infer_related_skills, build_knowledge_graph, recommend_skills, analyze_skill_gaps],
)


