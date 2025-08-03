import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, asdict
import hashlib
import uuid
from enum import Enum

class ExperienceLevel(Enum):
    """Experience level enumeration"""
    ENTRY = "entry"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"

class WorkPreference(Enum):
    """Work preference enumeration"""
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"

@dataclass
class Skill:
    """Data class for user skills"""
    name: str
    level: ExperienceLevel
    years_experience: float
    proficiency_score: float  # 0-1
    last_used: datetime
    certifications: List[str] = None
    projects_count: int = 0
    is_preferred: bool = False

@dataclass
class WorkHistory:
    """Data class for work history"""
    id: str
    company: str
    position: str
    start_date: datetime
    end_date: Optional[datetime] = None
    description: str
    skills_used: List[str]
    achievements: List[str]
    salary: Optional[float] = None
    is_current: bool = False

@dataclass
class FinancialProfile:
    """Data class for financial profile"""
    desired_annual_income: float
    current_hourly_rate: float
    preferred_rate_range: Dict[str, float]  # min, max
    tax_rate: float
    currency: str
    business_expenses: float
    savings_goals: Dict[str, float]
    investment_preferences: List[str]

@dataclass
class WorkPreferences:
    """Data class for work preferences"""
    preferred_work_type: WorkPreference
    preferred_hours: Dict[str, int]  # start_hour, end_hour
    timezone: str
    availability: Dict[str, bool]  # day_of_week -> available
    communication_preferences: List[str]
    project_duration_preferences: List[str]  # short_term, long_term, ongoing
    industry_preferences: List[str]

@dataclass
class LearningGoals:
    """Data class for learning goals"""
    skill_name: str
    target_level: ExperienceLevel
    deadline: datetime
    learning_resources: List[str]
    progress: float  # 0-1
    status: str  # active, completed, paused

@dataclass
class UserBehavior:
    """Data class for user behavior tracking"""
    timestamp: datetime
    action_type: str
    action_data: Dict[str, Any]
    success_rate: float
    time_spent: int  # seconds
    satisfaction_score: Optional[float] = None

class UserProfileManager:
    """
    Comprehensive User Profile Manager for FreelanceX.AI
    
    Extended Personalization: A rich profile system that captures and continuously 
    updates personal data points such as skills, experience, and preferred work conditions.
    
    Learning from User Behavior: FreelanceX.AI agents will track interactions and 
    adjust responses based on user behavior patterns, providing a tailored experience.
    
    Feedback Loops: Users can rate agent suggestions, refining the AI's responses 
    for future interactions.
    """
    
    def __init__(self, user_id: str = None):
        self.logger = logging.getLogger(__name__)
        self.user_id = user_id or str(uuid.uuid4())
        
        # Core profile data
        self.basic_info = {
            'name': '',
            'email': '',
            'location': '',
            'timezone': 'UTC',
            'bio': '',
            'profile_picture': None,
            'date_joined': datetime.now(),
            'last_updated': datetime.now()
        }
        
        # Skills and expertise
        self.skills: List[Skill] = []
        
        # Work history
        self.work_history: List[WorkHistory] = []
        
        # Financial profile
        self.financial_profile: Optional[FinancialProfile] = None
        
        # Work preferences
        self.work_preferences: Optional[WorkPreferences] = None
        
        # Learning goals
        self.learning_goals: List[LearningGoals] = []
        
        # Behavior tracking
        self.behavior_history: List[UserBehavior] = []
        
        # Feedback and ratings
        self.feedback_history: List[Dict[str, Any]] = []
        
        # Agent interaction preferences
        self.agent_preferences = {
            'job_search': {
                'preferred_platforms': ['upwork', 'fiverr', 'freelancer'],
                'alert_frequency': 'daily',
                'salary_threshold': 0.0,
                'skill_filters': []
            },
            'web_search': {
                'research_depth': 'comprehensive',
                'preferred_sources': ['medium.com', 'github.com', 'stackoverflow.com'],
                'notification_frequency': 'weekly'
            },
            'math': {
                'calculation_precision': 2,
                'preferred_currency': 'USD',
                'financial_goals': ['income_optimization', 'tax_planning']
            }
        }
        
        # Learning patterns
        self.learning_patterns = {
            'successful_actions': [],
            'failed_actions': [],
            'preference_changes': [],
            'skill_improvements': []
        }
        
        # Privacy settings
        self.privacy_settings = {
            'data_retention_days': 365,
            'share_behavior_data': True,
            'share_financial_data': False,
            'auto_learning': True
        }

    def create_profile(self, basic_info: Dict[str, Any]) -> str:
        """
        Create a new user profile
        
        Args:
            basic_info: Basic user information
            
        Returns:
            User ID
        """
        self.basic_info.update(basic_info)
        self.basic_info['date_joined'] = datetime.now()
        self.basic_info['last_updated'] = datetime.now()
        
        self.logger.info(f"Created profile for user: {basic_info.get('name', 'Unknown')}")
        return self.user_id

    def update_basic_info(self, updates: Dict[str, Any]):
        """Update basic user information"""
        self.basic_info.update(updates)
        self.basic_info['last_updated'] = datetime.now()
        self.logger.info(f"Updated basic info for user: {self.user_id}")

    def add_skill(self, skill_data: Dict[str, Any]) -> str:
        """
        Add or update a skill
        
        Args:
            skill_data: Skill information
            
        Returns:
            Skill ID
        """
        skill_id = str(uuid.uuid4())
        
        skill = Skill(
            name=skill_data['name'],
            level=ExperienceLevel(skill_data.get('level', 'intermediate')),
            years_experience=skill_data.get('years_experience', 0.0),
            proficiency_score=skill_data.get('proficiency_score', 0.5),
            last_used=skill_data.get('last_used', datetime.now()),
            certifications=skill_data.get('certifications', []),
            projects_count=skill_data.get('projects_count', 0),
            is_preferred=skill_data.get('is_preferred', False)
        )
        
        # Check if skill already exists
        existing_skill = next((s for s in self.skills if s.name.lower() == skill.name.lower()), None)
        if existing_skill:
            # Update existing skill
            existing_skill.level = skill.level
            existing_skill.years_experience = skill.years_experience
            existing_skill.proficiency_score = skill.proficiency_score
            existing_skill.last_used = skill.last_used
            existing_skill.certifications = skill.certifications
            existing_skill.projects_count = skill.projects_count
            existing_skill.is_preferred = skill.is_preferred
            skill_id = existing_skill.name  # Use skill name as ID for existing skills
        else:
            # Add new skill
            self.skills.append(skill)
        
        self.basic_info['last_updated'] = datetime.now()
        self.logger.info(f"Added/updated skill: {skill.name} for user: {self.user_id}")
        return skill_id

    def remove_skill(self, skill_name: str) -> bool:
        """Remove a skill from the profile"""
        initial_count = len(self.skills)
        self.skills = [s for s in self.skills if s.name.lower() != skill_name.lower()]
        
        if len(self.skills) < initial_count:
            self.basic_info['last_updated'] = datetime.now()
            self.logger.info(f"Removed skill: {skill_name} for user: {self.user_id}")
            return True
        return False

    def add_work_history(self, work_data: Dict[str, Any]) -> str:
        """
        Add work history entry
        
        Args:
            work_data: Work history information
            
        Returns:
            Work history ID
        """
        work_id = str(uuid.uuid4())
        
        work_history = WorkHistory(
            id=work_id,
            company=work_data['company'],
            position=work_data['position'],
            start_date=work_data['start_date'],
            end_date=work_data.get('end_date'),
            description=work_data.get('description', ''),
            skills_used=work_data.get('skills_used', []),
            achievements=work_data.get('achievements', []),
            salary=work_data.get('salary'),
            is_current=work_data.get('is_current', False)
        )
        
        self.work_history.append(work_history)
        self.basic_info['last_updated'] = datetime.now()
        
        self.logger.info(f"Added work history: {work_data['position']} at {work_data['company']}")
        return work_id

    def set_financial_profile(self, financial_data: Dict[str, Any]):
        """Set or update financial profile"""
        self.financial_profile = FinancialProfile(
            desired_annual_income=financial_data['desired_annual_income'],
            current_hourly_rate=financial_data.get('current_hourly_rate', 0.0),
            preferred_rate_range=financial_data.get('preferred_rate_range', {'min': 0, 'max': 0}),
            tax_rate=financial_data.get('tax_rate', 0.25),
            currency=financial_data.get('currency', 'USD'),
            business_expenses=financial_data.get('business_expenses', 0.0),
            savings_goals=financial_data.get('savings_goals', {}),
            investment_preferences=financial_data.get('investment_preferences', [])
        )
        
        self.basic_info['last_updated'] = datetime.now()
        self.logger.info(f"Updated financial profile for user: {self.user_id}")

    def set_work_preferences(self, preferences_data: Dict[str, Any]):
        """Set or update work preferences"""
        self.work_preferences = WorkPreferences(
            preferred_work_type=WorkPreference(preferences_data.get('preferred_work_type', 'remote')),
            preferred_hours=preferences_data.get('preferred_hours', {'start_hour': 9, 'end_hour': 17}),
            timezone=preferences_data.get('timezone', 'UTC'),
            availability=preferences_data.get('availability', {
                'monday': True, 'tuesday': True, 'wednesday': True,
                'thursday': True, 'friday': True, 'saturday': False, 'sunday': False
            }),
            communication_preferences=preferences_data.get('communication_preferences', ['email', 'chat']),
            project_duration_preferences=preferences_data.get('project_duration_preferences', ['short_term', 'long_term']),
            industry_preferences=preferences_data.get('industry_preferences', [])
        )
        
        self.basic_info['last_updated'] = datetime.now()
        self.logger.info(f"Updated work preferences for user: {self.user_id}")

    def add_learning_goal(self, goal_data: Dict[str, Any]) -> str:
        """
        Add a learning goal
        
        Args:
            goal_data: Learning goal information
            
        Returns:
            Goal ID
        """
        goal_id = str(uuid.uuid4())
        
        learning_goal = LearningGoals(
            skill_name=goal_data['skill_name'],
            target_level=ExperienceLevel(goal_data['target_level']),
            deadline=goal_data['deadline'],
            learning_resources=goal_data.get('learning_resources', []),
            progress=goal_data.get('progress', 0.0),
            status=goal_data.get('status', 'active')
        )
        
        self.learning_goals.append(learning_goal)
        self.basic_info['last_updated'] = datetime.now()
        
        self.logger.info(f"Added learning goal: {goal_data['skill_name']} for user: {self.user_id}")
        return goal_id

    def track_behavior(self, action_type: str, action_data: Dict[str, Any], 
                      success_rate: float = 1.0, time_spent: int = 0, 
                      satisfaction_score: Optional[float] = None):
        """
        Track user behavior for learning patterns
        
        Args:
            action_type: Type of action performed
            action_data: Data related to the action
            success_rate: Success rate of the action (0-1)
            time_spent: Time spent on the action in seconds
            satisfaction_score: User satisfaction score (0-1)
        """
        behavior = UserBehavior(
            timestamp=datetime.now(),
            action_type=action_type,
            action_data=action_data,
            success_rate=success_rate,
            time_spent=time_spent,
            satisfaction_score=satisfaction_score
        )
        
        self.behavior_history.append(behavior)
        
        # Update learning patterns
        if success_rate > 0.7:
            self.learning_patterns['successful_actions'].append({
                'action_type': action_type,
                'timestamp': datetime.now(),
                'data': action_data
            })
        else:
            self.learning_patterns['failed_actions'].append({
                'action_type': action_type,
                'timestamp': datetime.now(),
                'data': action_data,
                'failure_reason': action_data.get('failure_reason', 'unknown')
            })
        
        # Clean up old behavior data based on privacy settings
        self._cleanup_old_data()
        
        self.logger.debug(f"Tracked behavior: {action_type} for user: {self.user_id}")

    def add_feedback(self, agent_id: str, suggestion_id: str, rating: float, 
                    feedback_text: str = None):
        """
        Add user feedback for agent suggestions
        
        Args:
            agent_id: ID of the agent that made the suggestion
            suggestion_id: ID of the suggestion
            rating: Rating (0-1)
            feedback_text: Optional feedback text
        """
        feedback = {
            'id': str(uuid.uuid4()),
            'agent_id': agent_id,
            'suggestion_id': suggestion_id,
            'rating': rating,
            'feedback_text': feedback_text,
            'timestamp': datetime.now()
        }
        
        self.feedback_history.append(feedback)
        self.basic_info['last_updated'] = datetime.now()
        
        self.logger.info(f"Added feedback for agent {agent_id}: rating {rating}")

    def update_agent_preferences(self, agent_id: str, preferences: Dict[str, Any]):
        """Update preferences for a specific agent"""
        if agent_id in self.agent_preferences:
            self.agent_preferences[agent_id].update(preferences)
            self.basic_info['last_updated'] = datetime.now()
            self.logger.info(f"Updated preferences for agent: {agent_id}")

    def get_profile_summary(self) -> Dict[str, Any]:
        """Get a summary of the user profile"""
        return {
            'user_id': self.user_id,
            'basic_info': self.basic_info,
            'skills_count': len(self.skills),
            'preferred_skills': [s.name for s in self.skills if s.is_preferred],
            'work_history_count': len(self.work_history),
            'current_position': next((w.position for w in self.work_history if w.is_current), None),
            'learning_goals_count': len(self.learning_goals),
            'active_learning_goals': len([g for g in self.learning_goals if g.status == 'active']),
            'behavior_tracking_enabled': self.privacy_settings['share_behavior_data'],
            'last_activity': self.basic_info['last_updated']
        }

    def get_skills_for_job_matching(self) -> List[Dict[str, Any]]:
        """Get skills formatted for job matching"""
        return [
            {
                'name': skill.name,
                'level': skill.level.value,
                'years_experience': skill.years_experience,
                'proficiency_score': skill.proficiency_score,
                'is_preferred': skill.is_preferred,
                'last_used': skill.last_used.isoformat()
            }
            for skill in self.skills
        ]

    def get_financial_data_for_calculations(self) -> Dict[str, Any]:
        """Get financial data formatted for calculations"""
        if not self.financial_profile:
            return {}
        
        return {
            'desired_annual_income': self.financial_profile.desired_annual_income,
            'current_hourly_rate': self.financial_profile.current_hourly_rate,
            'preferred_rate_range': self.financial_profile.preferred_rate_range,
            'tax_rate': self.financial_profile.tax_rate,
            'currency': self.financial_profile.currency,
            'business_expenses': self.financial_profile.business_expenses
        }

    def get_work_preferences_for_search(self) -> Dict[str, Any]:
        """Get work preferences formatted for job search"""
        if not self.work_preferences:
            return {}
        
        return {
            'preferred_work_type': self.work_preferences.preferred_work_type.value,
            'timezone': self.work_preferences.timezone,
            'availability': self.work_preferences.availability,
            'communication_preferences': self.work_preferences.communication_preferences,
            'industry_preferences': self.work_preferences.industry_preferences
        }

    def learn_from_behavior(self) -> Dict[str, Any]:
        """
        Analyze behavior patterns and generate insights
        
        Returns:
            Dictionary of learned insights
        """
        insights = {
            'preferred_actions': [],
            'successful_patterns': [],
            'improvement_areas': [],
            'recommendations': []
        }
        
        if not self.behavior_history:
            return insights
        
        # Analyze successful actions
        successful_actions = [b for b in self.behavior_history if b.success_rate > 0.7]
        if successful_actions:
            action_types = [b.action_type for b in successful_actions]
            insights['preferred_actions'] = list(set(action_types))
        
        # Analyze time patterns
        recent_behavior = [b for b in self.behavior_history 
                          if b.timestamp > datetime.now() - timedelta(days=30)]
        
        if recent_behavior:
            avg_time_spent = sum(b.time_spent for b in recent_behavior) / len(recent_behavior)
            insights['recommendations'].append(f"Average time per action: {avg_time_spent:.1f} seconds")
        
        # Analyze satisfaction trends
        satisfaction_scores = [b.satisfaction_score for b in self.behavior_history 
                             if b.satisfaction_score is not None]
        if satisfaction_scores:
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            insights['recommendations'].append(f"Average satisfaction: {avg_satisfaction:.2f}")
        
        return insights

    def get_agent_recommendations(self, agent_id: str) -> Dict[str, Any]:
        """
        Get personalized recommendations for a specific agent
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary of recommendations
        """
        recommendations = {
            'preferences': self.agent_preferences.get(agent_id, {}),
            'behavior_insights': self.learn_from_behavior(),
            'skill_gaps': self._identify_skill_gaps(),
            'learning_suggestions': self._generate_learning_suggestions()
        }
        
        return recommendations

    def _identify_skill_gaps(self) -> List[Dict[str, Any]]:
        """Identify skill gaps based on learning goals and market demands"""
        skill_gaps = []
        
        for goal in self.learning_goals:
            if goal.status == 'active':
                current_skill = next((s for s in self.skills if s.name.lower() == goal.skill_name.lower()), None)
                
                if not current_skill or current_skill.level.value != goal.target_level.value:
                    skill_gaps.append({
                        'skill_name': goal.skill_name,
                        'current_level': current_skill.level.value if current_skill else 'none',
                        'target_level': goal.target_level.value,
                        'progress': goal.progress,
                        'deadline': goal.deadline.isoformat()
                    })
        
        return skill_gaps

    def _generate_learning_suggestions(self) -> List[str]:
        """Generate learning suggestions based on profile data"""
        suggestions = []
        
        # Suggest based on learning goals
        active_goals = [g for g in self.learning_goals if g.status == 'active']
        if active_goals:
            suggestions.append(f"Focus on {len(active_goals)} active learning goals")
        
        # Suggest based on skill levels
        entry_level_skills = [s for s in self.skills if s.level == ExperienceLevel.ENTRY]
        if entry_level_skills:
            suggestions.append(f"Consider advancing {len(entry_level_skills)} entry-level skills")
        
        # Suggest based on financial goals
        if self.financial_profile and self.financial_profile.desired_annual_income > 0:
            current_rate = self.financial_profile.current_hourly_rate
            if current_rate > 0:
                target_rate = self.financial_profile.desired_annual_income / 2080  # Assuming 2080 hours/year
                if target_rate > current_rate * 1.2:  # 20% increase
                    suggestions.append("Consider upskilling to achieve desired income goals")
        
        return suggestions

    def _cleanup_old_data(self):
        """Clean up old data based on privacy settings"""
        retention_days = self.privacy_settings['data_retention_days']
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Clean up old behavior data
        self.behavior_history = [
            b for b in self.behavior_history
            if b.timestamp > cutoff_date
        ]
        
        # Clean up old feedback
        self.feedback_history = [
            f for f in self.feedback_history
            if f['timestamp'] > cutoff_date
        ]

    def export_profile(self, filename: str = None) -> str:
        """Export user profile to JSON file"""
        if not filename:
            filename = f"user_profile_{self.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        profile_data = {
            'user_id': self.user_id,
            'basic_info': self.basic_info,
            'skills': [asdict(skill) for skill in self.skills],
            'work_history': [asdict(work) for work in self.work_history],
            'financial_profile': asdict(self.financial_profile) if self.financial_profile else None,
            'work_preferences': asdict(self.work_preferences) if self.work_preferences else None,
            'learning_goals': [asdict(goal) for goal in self.learning_goals],
            'agent_preferences': self.agent_preferences,
            'privacy_settings': self.privacy_settings,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(profile_data, f, indent=2, default=str)
        
        return filename

    def import_profile(self, filename: str) -> bool:
        """Import user profile from JSON file"""
        try:
            with open(filename, 'r') as f:
                profile_data = json.load(f)
            
            # Import basic info
            self.basic_info = profile_data.get('basic_info', self.basic_info)
            
            # Import skills
            self.skills = []
            for skill_data in profile_data.get('skills', []):
                skill = Skill(**skill_data)
                self.skills.append(skill)
            
            # Import work history
            self.work_history = []
            for work_data in profile_data.get('work_history', []):
                work = WorkHistory(**work_data)
                self.work_history.append(work)
            
            # Import other data
            if profile_data.get('financial_profile'):
                self.financial_profile = FinancialProfile(**profile_data['financial_profile'])
            
            if profile_data.get('work_preferences'):
                self.work_preferences = WorkPreferences(**profile_data['work_preferences'])
            
            self.learning_goals = []
            for goal_data in profile_data.get('learning_goals', []):
                goal = LearningGoals(**goal_data)
                self.learning_goals.append(goal)
            
            self.agent_preferences = profile_data.get('agent_preferences', self.agent_preferences)
            self.privacy_settings = profile_data.get('privacy_settings', self.privacy_settings)
            
            self.logger.info(f"Successfully imported profile from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to import profile from {filename}: {e}")
            return False