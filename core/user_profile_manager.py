import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
import hashlib
from collections import defaultdict

class SkillLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ExperienceLevel(Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    LEAD = "lead"

class WorkPreference(Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"

@dataclass
class Skill:
    name: str
    level: SkillLevel
    years_experience: float
    last_used: datetime
    confidence_score: float
    certifications: List[str] = field(default_factory=list)
    projects_count: int = 0

@dataclass
class WorkHistory:
    project_id: str
    title: str
    description: str
    client: str
    platform: str
    start_date: datetime
    end_date: Optional[datetime]
    budget: float
    skills_used: List[str]
    rating: Optional[float]
    feedback: Optional[str]
    status: str  # completed, ongoing, cancelled

@dataclass
class LearningGoal:
    goal_id: str
    skill_name: str
    target_level: SkillLevel
    target_date: datetime
    current_progress: float
    learning_resources: List[str]
    status: str  # active, completed, paused

@dataclass
class UserBehavior:
    action_type: str
    timestamp: datetime
    context: Dict[str, Any]
    outcome: Optional[str]
    duration: Optional[float]
    satisfaction_score: Optional[float]

class UserProfileManager:
    """
    Comprehensive user profile management system that captures and continuously
    updates personal data points for extended personalization and learning.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.logger = logging.getLogger(f"UserProfileManager_{user_id}")
        self.profile_data = self._initialize_profile()
        self.behavior_history: List[UserBehavior] = []
        self.feedback_history: List[Dict[str, Any]] = []
        self.learning_progress: Dict[str, float] = {}
        
    def _initialize_profile(self) -> Dict[str, Any]:
        """Initialize a new user profile with default values"""
        return {
            "user_id": self.user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            
            # Basic Information
            "personal_info": {
                "name": "",
                "email": "",
                "location": "",
                "timezone": "",
                "bio": "",
                "avatar_url": ""
            },
            
            # Professional Information
            "professional_info": {
                "title": "",
                "experience_level": ExperienceLevel.ENTRY.value,
                "years_experience": 0,
                "specialization": "",
                "portfolio_url": "",
                "linkedin_url": "",
                "github_url": ""
            },
            
            # Skills and Expertise
            "skills": {},
            "skill_categories": {
                "technical": [],
                "soft_skills": [],
                "tools": [],
                "languages": []
            },
            
            # Work Preferences
            "work_preferences": {
                "work_type": WorkPreference.REMOTE.value,
                "min_hourly_rate": 0,
                "max_hourly_rate": 0,
                "preferred_job_types": ["fixed_price", "hourly"],
                "availability": {
                    "hours_per_week": 40,
                    "timezone_preference": "flexible",
                    "response_time": "24h"
                },
                "excluded_keywords": [],
                "preferred_industries": [],
                "deal_breakers": []
            },
            
            # Financial Information
            "financial_info": {
                "income_goals": {
                    "monthly": 0,
                    "annual": 0
                },
                "expense_categories": {},
                "tax_info": {
                    "country": "",
                    "tax_id": "",
                    "business_type": ""
                },
                "investment_preferences": {
                    "risk_tolerance": "medium",
                    "investment_goals": []
                }
            },
            
            # Learning and Development
            "learning_goals": {},
            "certifications": [],
            "education": [],
            
            # Work History
            "work_history": [],
            "client_feedback": [],
            
            # Performance Metrics
            "performance_metrics": {
                "total_earnings": 0,
                "projects_completed": 0,
                "average_rating": 0,
                "response_rate": 0,
                "on_time_delivery": 0
            },
            
            # Preferences and Settings
            "preferences": {
                "communication_style": "professional",
                "notification_preferences": {
                    "email": True,
                    "push": True,
                    "sms": False
                },
                "privacy_settings": {
                    "profile_visibility": "public",
                    "earnings_visibility": "private",
                    "skill_visibility": "public"
                },
                "ai_assistance_level": "high",
                "automation_preferences": {
                    "job_search": True,
                    "proposal_generation": True,
                    "client_communication": True,
                    "financial_tracking": True
                }
            },
            
            # Behavioral Patterns
            "behavioral_patterns": {
                "peak_working_hours": [],
                "preferred_project_size": "medium",
                "communication_preferences": [],
                "decision_making_style": "analytical"
            }
        }
    
    async def update_personal_info(self, personal_info: Dict[str, Any]) -> bool:
        """Update personal information"""
        try:
            self.profile_data["personal_info"].update(personal_info)
            self.profile_data["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"Updated personal info for user {self.user_id}")
            await self._log_behavior("profile_update", {"section": "personal_info"})
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating personal info: {str(e)}")
            return False
    
    async def add_skill(self, skill: Skill) -> bool:
        """Add or update a skill in the user profile"""
        try:
            self.profile_data["skills"][skill.name] = {
                "level": skill.level.value,
                "years_experience": skill.years_experience,
                "last_used": skill.last_used.isoformat(),
                "confidence_score": skill.confidence_score,
                "certifications": skill.certifications,
                "projects_count": skill.projects_count
            }
            
            # Update skill categories
            await self._categorize_skill(skill.name)
            
            self.profile_data["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"Added/updated skill: {skill.name} for user {self.user_id}")
            await self._log_behavior("skill_update", {"skill_name": skill.name, "level": skill.level.value})
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding skill: {str(e)}")
            return False
    
    async def _categorize_skill(self, skill_name: str) -> None:
        """Automatically categorize skills"""
        technical_keywords = ["python", "javascript", "java", "react", "node", "sql", "aws", "docker"]
        soft_skill_keywords = ["communication", "leadership", "project management", "teamwork"]
        tool_keywords = ["figma", "photoshop", "excel", "word", "powerpoint"]
        language_keywords = ["english", "spanish", "french", "german", "chinese"]
        
        skill_lower = skill_name.lower()
        
        if any(keyword in skill_lower for keyword in technical_keywords):
            if skill_name not in self.profile_data["skill_categories"]["technical"]:
                self.profile_data["skill_categories"]["technical"].append(skill_name)
        elif any(keyword in skill_lower for keyword in soft_skill_keywords):
            if skill_name not in self.profile_data["skill_categories"]["soft_skills"]:
                self.profile_data["skill_categories"]["soft_skills"].append(skill_name)
        elif any(keyword in skill_lower for keyword in tool_keywords):
            if skill_name not in self.profile_data["skill_categories"]["tools"]:
                self.profile_data["skill_categories"]["tools"].append(skill_name)
        elif any(keyword in skill_lower for keyword in language_keywords):
            if skill_name not in self.profile_data["skill_categories"]["languages"]:
                self.profile_data["skill_categories"]["languages"].append(skill_name)
    
    async def update_work_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update work preferences"""
        try:
            self.profile_data["work_preferences"].update(preferences)
            self.profile_data["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"Updated work preferences for user {self.user_id}")
            await self._log_behavior("preference_update", {"section": "work_preferences"})
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating work preferences: {str(e)}")
            return False
    
    async def add_work_history(self, work_history: WorkHistory) -> bool:
        """Add work history entry"""
        try:
            history_entry = {
                "project_id": work_history.project_id,
                "title": work_history.title,
                "description": work_history.description,
                "client": work_history.client,
                "platform": work_history.platform,
                "start_date": work_history.start_date.isoformat(),
                "end_date": work_history.end_date.isoformat() if work_history.end_date else None,
                "budget": work_history.budget,
                "skills_used": work_history.skills_used,
                "rating": work_history.rating,
                "feedback": work_history.feedback,
                "status": work_history.status
            }
            
            self.profile_data["work_history"].append(history_entry)
            
            # Update performance metrics
            await self._update_performance_metrics(work_history)
            
            self.profile_data["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"Added work history: {work_history.title} for user {self.user_id}")
            await self._log_behavior("work_history_added", {"project_title": work_history.title})
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding work history: {str(e)}")
            return False
    
    async def _update_performance_metrics(self, work_history: WorkHistory) -> None:
        """Update performance metrics based on work history"""
        metrics = self.profile_data["performance_metrics"]
        
        if work_history.status == "completed":
            metrics["projects_completed"] += 1
            metrics["total_earnings"] += work_history.budget
            
            if work_history.rating:
                # Update average rating
                current_avg = metrics["average_rating"]
                total_projects = metrics["projects_completed"]
                new_avg = ((current_avg * (total_projects - 1)) + work_history.rating) / total_projects
                metrics["average_rating"] = new_avg
    
    async def add_learning_goal(self, goal: LearningGoal) -> bool:
        """Add a learning goal"""
        try:
            goal_entry = {
                "goal_id": goal.goal_id,
                "skill_name": goal.skill_name,
                "target_level": goal.target_level.value,
                "target_date": goal.target_date.isoformat(),
                "current_progress": goal.current_progress,
                "learning_resources": goal.learning_resources,
                "status": goal.status,
                "created_at": datetime.now().isoformat()
            }
            
            self.profile_data["learning_goals"][goal.goal_id] = goal_entry
            self.profile_data["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"Added learning goal: {goal.skill_name} for user {self.user_id}")
            await self._log_behavior("learning_goal_added", {"skill_name": goal.skill_name})
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding learning goal: {str(e)}")
            return False
    
    async def update_learning_progress(self, goal_id: str, progress: float) -> bool:
        """Update learning progress for a goal"""
        try:
            if goal_id in self.profile_data["learning_goals"]:
                self.profile_data["learning_goals"][goal_id]["current_progress"] = progress
                self.profile_data["last_updated"] = datetime.now().isoformat()
                
                # Update learning progress tracking
                self.learning_progress[goal_id] = progress
                
                self.logger.info(f"Updated learning progress for goal {goal_id}: {progress}")
                await self._log_behavior("learning_progress_update", {"goal_id": goal_id, "progress": progress})
                
                return True
            else:
                self.logger.warning(f"Learning goal {goal_id} not found")
                return False
        except Exception as e:
            self.logger.error(f"Error updating learning progress: {str(e)}")
            return False
    
    async def log_behavior(self, action_type: str, context: Dict[str, Any], 
                          outcome: Optional[str] = None, duration: Optional[float] = None,
                          satisfaction_score: Optional[float] = None) -> None:
        """Log user behavior for learning and personalization"""
        behavior = UserBehavior(
            action_type=action_type,
            timestamp=datetime.now(),
            context=context,
            outcome=outcome,
            duration=duration,
            satisfaction_score=satisfaction_score
        )
        
        self.behavior_history.append(behavior)
        
        # Keep behavior history manageable
        if len(self.behavior_history) > 10000:
            self.behavior_history = self.behavior_history[-5000:]
        
        # Update behavioral patterns
        await self._update_behavioral_patterns(behavior)
    
    async def _log_behavior(self, action_type: str, context: Dict[str, Any]) -> None:
        """Internal method to log behavior"""
        await self.log_behavior(action_type, context)
    
    async def _update_behavioral_patterns(self, behavior: UserBehavior) -> None:
        """Update behavioral patterns based on user actions"""
        patterns = self.profile_data["behavioral_patterns"]
        
        # Update peak working hours
        hour = behavior.timestamp.hour
        if hour not in patterns["peak_working_hours"]:
            patterns["peak_working_hours"].append(hour)
            patterns["peak_working_hours"].sort()
        
        # Analyze decision making style based on actions
        if behavior.action_type in ["job_application", "proposal_submission"]:
            # Analyze response time and decision patterns
            if behavior.duration and behavior.duration < 300:  # Less than 5 minutes
                patterns["decision_making_style"] = "quick"
            elif behavior.duration and behavior.duration > 3600:  # More than 1 hour
                patterns["decision_making_style"] = "thorough"
    
    async def add_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Add user feedback"""
        try:
            feedback_entry = {
                "feedback_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "feedback_type": feedback_data.get("type", "general"),
                "content": feedback_data.get("content", ""),
                "rating": feedback_data.get("rating"),
                "category": feedback_data.get("category", "general"),
                "context": feedback_data.get("context", {})
            }
            
            self.feedback_history.append(feedback_entry)
            self.profile_data["last_updated"] = datetime.now().isoformat()
            
            self.logger.info(f"Added feedback for user {self.user_id}")
            await self._log_behavior("feedback_submitted", {"feedback_type": feedback_entry["feedback_type"]})
            
            return True
        except Exception as e:
            self.logger.error(f"Error adding feedback: {str(e)}")
            return False
    
    async def get_personalized_recommendations(self) -> Dict[str, Any]:
        """Generate personalized recommendations based on profile and behavior"""
        recommendations = {
            "skill_development": [],
            "job_opportunities": [],
            "financial_advice": [],
            "productivity_tips": [],
            "learning_resources": []
        }
        
        # Skill development recommendations
        skills = self.profile_data["skills"]
        for skill_name, skill_data in skills.items():
            if skill_data["confidence_score"] < 0.7:
                recommendations["skill_development"].append({
                    "skill": skill_name,
                    "current_level": skill_data["level"],
                    "suggestion": f"Consider taking advanced courses in {skill_name}",
                    "priority": "medium"
                })
        
        # Financial recommendations
        financial_info = self.profile_data["financial_info"]
        if financial_info["income_goals"]["monthly"] > 0:
            current_earnings = self.profile_data["performance_metrics"]["total_earnings"]
            if current_earnings < financial_info["income_goals"]["monthly"] * 12:
                recommendations["financial_advice"].append({
                    "type": "income_optimization",
                    "suggestion": "Consider raising your rates or diversifying income sources",
                    "priority": "high"
                })
        
        # Learning recommendations based on behavior
        if len(self.behavior_history) > 10:
            recent_actions = [b.action_type for b in self.behavior_history[-10:]]
            if "job_search" in recent_actions and "job_application" not in recent_actions:
                recommendations["job_opportunities"].append({
                    "type": "application_strategy",
                    "suggestion": "Consider applying to more jobs to increase your chances",
                    "priority": "medium"
                })
        
        return recommendations
    
    async def get_skill_gap_analysis(self) -> Dict[str, Any]:
        """Analyze skill gaps and provide recommendations"""
        current_skills = self.profile_data["skills"]
        work_history = self.profile_data["work_history"]
        
        # Analyze skills used in successful projects
        successful_skills = set()
        for project in work_history:
            if project["rating"] and project["rating"] >= 4.0:
                successful_skills.update(project["skills_used"])
        
        # Find skills that are in demand but not in profile
        in_demand_skills = ["python", "javascript", "react", "node.js", "aws", "docker", "kubernetes"]
        missing_skills = [skill for skill in in_demand_skills if skill not in current_skills]
        
        # Analyze skill levels
        skill_gaps = []
        for skill_name, skill_data in current_skills.items():
            if skill_data["confidence_score"] < 0.6:
                skill_gaps.append({
                    "skill": skill_name,
                    "current_level": skill_data["level"],
                    "recommended_level": "advanced",
                    "priority": "high" if skill_name in successful_skills else "medium"
                })
        
        return {
            "missing_skills": missing_skills,
            "skill_gaps": skill_gaps,
            "strong_skills": [skill for skill, data in current_skills.items() if data["confidence_score"] > 0.8],
            "recommendations": await self._generate_skill_recommendations(missing_skills, skill_gaps)
        }
    
    async def _generate_skill_recommendations(self, missing_skills: List[str], 
                                           skill_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific skill development recommendations"""
        recommendations = []
        
        for skill in missing_skills:
            recommendations.append({
                "skill": skill,
                "action": "learn",
                "priority": "high",
                "resources": [
                    f"Online courses for {skill}",
                    f"Practice projects using {skill}",
                    f"Join {skill} communities"
                ]
            })
        
        for gap in skill_gaps:
            recommendations.append({
                "skill": gap["skill"],
                "action": "improve",
                "priority": gap["priority"],
                "resources": [
                    f"Advanced {gap['skill']} courses",
                    f"Real-world projects",
                    f"Certification programs"
                ]
            })
        
        return recommendations
    
    async def get_profile_summary(self) -> Dict[str, Any]:
        """Get a comprehensive profile summary"""
        return {
            "user_id": self.user_id,
            "profile_completeness": await self._calculate_profile_completeness(),
            "key_metrics": {
                "total_skills": len(self.profile_data["skills"]),
                "projects_completed": self.profile_data["performance_metrics"]["projects_completed"],
                "total_earnings": self.profile_data["performance_metrics"]["total_earnings"],
                "average_rating": self.profile_data["performance_metrics"]["average_rating"],
                "active_learning_goals": len([g for g in self.profile_data["learning_goals"].values() if g["status"] == "active"])
            },
            "top_skills": await self._get_top_skills(),
            "recent_activity": await self._get_recent_activity(),
            "recommendations": await self.get_personalized_recommendations()
        }
    
    async def _calculate_profile_completeness(self) -> float:
        """Calculate profile completeness percentage"""
        sections = [
            "personal_info",
            "professional_info", 
            "skills",
            "work_preferences",
            "financial_info"
        ]
        
        completed_sections = 0
        for section in sections:
            if self.profile_data[section]:
                completed_sections += 1
        
        return (completed_sections / len(sections)) * 100
    
    async def _get_top_skills(self) -> List[Dict[str, Any]]:
        """Get top skills based on confidence and usage"""
        skills = self.profile_data["skills"]
        
        # Sort skills by confidence score and project count
        sorted_skills = sorted(
            skills.items(),
            key=lambda x: (x[1]["confidence_score"], x[1]["projects_count"]),
            reverse=True
        )
        
        return [
            {
                "name": skill_name,
                "level": skill_data["level"],
                "confidence": skill_data["confidence_score"],
                "projects": skill_data["projects_count"]
            }
            for skill_name, skill_data in sorted_skills[:5]
        ]
    
    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent user activity"""
        recent_behaviors = self.behavior_history[-10:] if self.behavior_history else []
        
        return [
            {
                "action": behavior.action_type,
                "timestamp": behavior.timestamp.isoformat(),
                "context": behavior.context
            }
            for behavior in recent_behaviors
        ]
    
    async def export_profile(self, format: str = "json") -> str:
        """Export user profile data"""
        if format == "json":
            export_data = {
                "profile": self.profile_data,
                "behavior_history": [
                    {
                        "action_type": b.action_type,
                        "timestamp": b.timestamp.isoformat(),
                        "context": b.context,
                        "outcome": b.outcome,
                        "duration": b.duration,
                        "satisfaction_score": b.satisfaction_score
                    }
                    for b in self.behavior_history
                ],
                "feedback_history": self.feedback_history,
                "learning_progress": self.learning_progress
            }
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    async def get_profile_data(self) -> Dict[str, Any]:
        """Get the complete profile data"""
        return self.profile_data.copy()