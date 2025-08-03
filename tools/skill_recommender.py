"""
FreelanceX.AI Skill Recommender Tool
Intelligent skill recommendations based on profile and market trends
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SkillRecommender:
    """
    Skill Recommender - Provides intelligent skill recommendations
    Analyzes profiles, market trends, and job requirements to suggest relevant skills
    """
    
    def __init__(self):
        self.skill_database = {
            'technical_skills': {
                'programming_languages': [
                    'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin', 'TypeScript'
                ],
                'web_development': [
                    'React', 'Vue.js', 'Angular', 'Node.js', 'Django', 'Flask', 'Express.js', 'Laravel', 'Spring Boot'
                ],
                'data_science': [
                    'Pandas', 'NumPy', 'Scikit-learn', 'TensorFlow', 'PyTorch', 'R', 'SQL', 'MongoDB', 'Apache Spark'
                ],
                'cloud_platforms': [
                    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins', 'GitLab CI'
                ],
                'mobile_development': [
                    'React Native', 'Flutter', 'Xamarin', 'Swift', 'Kotlin', 'Android Studio', 'Xcode'
                ]
            },
            'business_skills': {
                'project_management': [
                    'Agile', 'Scrum', 'Kanban', 'JIRA', 'Trello', 'Asana', 'Microsoft Project', 'PMP'
                ],
                'marketing': [
                    'Digital Marketing', 'SEO', 'SEM', 'Social Media Marketing', 'Content Marketing', 'Email Marketing'
                ],
                'analytics': [
                    'Google Analytics', 'Tableau', 'Power BI', 'Mixpanel', 'Amplitude', 'Hotjar'
                ],
                'sales': [
                    'CRM Systems', 'Salesforce', 'HubSpot', 'Lead Generation', 'Negotiation', 'Client Relations'
                ]
            },
            'soft_skills': {
                'communication': [
                    'Public Speaking', 'Technical Writing', 'Presentation Skills', 'Active Listening', 'Conflict Resolution'
                ],
                'leadership': [
                    'Team Management', 'Strategic Planning', 'Decision Making', 'Mentoring', 'Change Management'
                ],
                'problem_solving': [
                    'Critical Thinking', 'Analytical Skills', 'Creative Problem Solving', 'Root Cause Analysis'
                ],
                'time_management': [
                    'Prioritization', 'Goal Setting', 'Delegation', 'Stress Management', 'Work-Life Balance'
                ]
            }
        }
        self.recommendation_history = []
        self.market_trends = {}
        
    async def recommend_skills(self, profile: Dict[str, Any], context: str = "general") -> Dict[str, Any]:
        """
        Recommend skills based on user profile and context.
        
        Args:
            profile (dict): User profile with experience, interests, etc.
            context (str): Context for recommendations (job_search, career_growth, etc.)
            
        Returns:
            dict: Skill recommendations with explanations
        """
        try:
            logger.info(f"🎯 Generating skill recommendations for profile: {profile.get('name', 'Unknown')}")
            
            # Analyze profile
            profile_analysis = await self._analyze_profile(profile)
            
            # Get market trends
            market_analysis = await self._analyze_market_trends()
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(profile_analysis, market_analysis, context)
            
            # Log recommendation
            self._log_recommendation(profile, context, recommendations)
            
            return {
                'success': True,
                'recommendations': recommendations,
                'profile_analysis': profile_analysis,
                'market_analysis': market_analysis,
                'context': context
            }
            
        except Exception as e:
            logger.error(f"❌ Skill recommendation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user profile for skill recommendations"""
        analysis = {
            'experience_level': 'beginner',
            'current_skills': [],
            'skill_gaps': [],
            'career_goals': [],
            'industry_focus': 'general'
        }
        
        # Determine experience level
        experience_years = profile.get('experience_years', 0)
        if experience_years < 2:
            analysis['experience_level'] = 'beginner'
        elif experience_years < 5:
            analysis['experience_level'] = 'intermediate'
        elif experience_years < 10:
            analysis['experience_level'] = 'advanced'
        else:
            analysis['experience_level'] = 'expert'
        
        # Extract current skills
        current_skills = profile.get('skills', [])
        analysis['current_skills'] = current_skills
        
        # Determine industry focus
        interests = profile.get('interests', [])
        if any('tech' in interest.lower() for interest in interests):
            analysis['industry_focus'] = 'technology'
        elif any('business' in interest.lower() for interest in interests):
            analysis['industry_focus'] = 'business'
        elif any('design' in interest.lower() for interest in interests):
            analysis['industry_focus'] = 'design'
        
        # Extract career goals
        goals = profile.get('career_goals', [])
        analysis['career_goals'] = goals
        
        return analysis
    
    async def _analyze_market_trends(self) -> Dict[str, Any]:
        """Analyze current market trends for skills"""
        # Simulate market analysis
        await asyncio.sleep(0.2)
        
        return {
            'hot_skills': [
                'Python', 'React', 'AWS', 'Machine Learning', 'Data Analysis',
                'Agile', 'Digital Marketing', 'Cloud Computing'
            ],
            'emerging_skills': [
                'AI/ML', 'Blockchain', 'Cybersecurity', 'DevOps', 'No-Code/Low-Code'
            ],
            'declining_skills': [
                'Flash', 'Perl', 'COBOL', 'Traditional Marketing'
            ],
            'salary_impact': {
                'high_demand': ['AI/ML', 'Cybersecurity', 'Cloud Architecture'],
                'medium_demand': ['Web Development', 'Data Analysis', 'Project Management'],
                'stable': ['Communication', 'Problem Solving', 'Team Leadership']
            }
        }
    
    async def _generate_recommendations(self, profile_analysis: Dict[str, Any], 
                                      market_analysis: Dict[str, Any], 
                                      context: str) -> Dict[str, Any]:
        """Generate skill recommendations"""
        recommendations = {
            'priority_skills': [],
            'growth_skills': [],
            'complementary_skills': [],
            'explanations': {},
            'learning_path': []
        }
        
        experience_level = profile_analysis['experience_level']
        current_skills = profile_analysis['current_skills']
        industry_focus = profile_analysis['industry_focus']
        
        # Generate priority skills based on experience level
        if experience_level == 'beginner':
            recommendations['priority_skills'] = self._get_beginner_skills(industry_focus)
        elif experience_level == 'intermediate':
            recommendations['priority_skills'] = self._get_intermediate_skills(industry_focus)
        elif experience_level == 'advanced':
            recommendations['priority_skills'] = self._get_advanced_skills(industry_focus)
        else:
            recommendations['priority_skills'] = self._get_expert_skills(industry_focus)
        
        # Add market-driven recommendations
        hot_skills = market_analysis.get('hot_skills', [])
        recommendations['growth_skills'] = [skill for skill in hot_skills 
                                          if skill not in current_skills][:5]
        
        # Generate complementary skills
        recommendations['complementary_skills'] = self._get_complementary_skills(
            current_skills, industry_focus
        )
        
        # Add explanations
        recommendations['explanations'] = self._generate_explanations(
            recommendations, profile_analysis, market_analysis
        )
        
        # Create learning path
        recommendations['learning_path'] = self._create_learning_path(
            recommendations, experience_level
        )
        
        return recommendations
    
    def _get_beginner_skills(self, industry_focus: str) -> List[str]:
        """Get skills for beginners"""
        if industry_focus == 'technology':
            return ['Python', 'HTML/CSS', 'JavaScript', 'Git', 'Problem Solving']
        elif industry_focus == 'business':
            return ['Microsoft Office', 'Communication', 'Time Management', 'Customer Service']
        elif industry_focus == 'design':
            return ['Adobe Photoshop', 'Adobe Illustrator', 'Design Principles', 'Creativity']
        else:
            return ['Communication', 'Problem Solving', 'Time Management', 'Microsoft Office']
    
    def _get_intermediate_skills(self, industry_focus: str) -> List[str]:
        """Get skills for intermediate level"""
        if industry_focus == 'technology':
            return ['React', 'Node.js', 'SQL', 'AWS', 'Agile']
        elif industry_focus == 'business':
            return ['Project Management', 'Data Analysis', 'Digital Marketing', 'Sales']
        elif industry_focus == 'design':
            return ['UI/UX Design', 'Figma', 'Prototyping', 'User Research']
        else:
            return ['Project Management', 'Data Analysis', 'Leadership', 'Strategic Thinking']
    
    def _get_advanced_skills(self, industry_focus: str) -> List[str]:
        """Get skills for advanced level"""
        if industry_focus == 'technology':
            return ['Machine Learning', 'System Architecture', 'DevOps', 'Team Leadership']
        elif industry_focus == 'business':
            return ['Strategic Planning', 'Business Development', 'Change Management', 'Executive Leadership']
        elif industry_focus == 'design':
            return ['Design Systems', 'Design Leadership', 'User Experience Strategy']
        else:
            return ['Strategic Planning', 'Executive Leadership', 'Change Management', 'Innovation']
    
    def _get_expert_skills(self, industry_focus: str) -> List[str]:
        """Get skills for expert level"""
        if industry_focus == 'technology':
            return ['AI/ML Strategy', 'Technology Leadership', 'Innovation Management', 'Mentoring']
        elif industry_focus == 'business':
            return ['Executive Leadership', 'Strategic Innovation', 'Board Management', 'Mentoring']
        elif industry_focus == 'design':
            return ['Design Strategy', 'Creative Leadership', 'Design Innovation', 'Mentoring']
        else:
            return ['Executive Leadership', 'Strategic Innovation', 'Mentoring', 'Thought Leadership']
    
    def _get_complementary_skills(self, current_skills: List[str], industry_focus: str) -> List[str]:
        """Get complementary skills"""
        complementary = []
        
        # Add soft skills if missing
        soft_skills = ['Communication', 'Problem Solving', 'Time Management', 'Teamwork']
        for skill in soft_skills:
            if skill not in current_skills:
                complementary.append(skill)
        
        # Add industry-specific complementary skills
        if industry_focus == 'technology':
            tech_complementary = ['Agile', 'DevOps', 'Cloud Computing']
            for skill in tech_complementary:
                if skill not in current_skills:
                    complementary.append(skill)
        
        return complementary[:5]
    
    def _generate_explanations(self, recommendations: Dict[str, Any], 
                             profile_analysis: Dict[str, Any], 
                             market_analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate explanations for recommendations"""
        explanations = {}
        
        # Priority skills explanation
        experience_level = profile_analysis['experience_level']
        explanations['priority_skills'] = f"These skills are essential for {experience_level} level professionals in your field."
        
        # Growth skills explanation
        hot_skills = market_analysis.get('hot_skills', [])
        explanations['growth_skills'] = f"These are high-demand skills in the current market that can boost your career prospects."
        
        # Complementary skills explanation
        explanations['complementary_skills'] = "These skills complement your current skill set and enhance your overall profile."
        
        return explanations
    
    def _create_learning_path(self, recommendations: Dict[str, Any], experience_level: str) -> List[Dict[str, Any]]:
        """Create a learning path for skill development"""
        learning_path = []
        
        # Add priority skills to learning path
        for i, skill in enumerate(recommendations['priority_skills'][:3]):
            learning_path.append({
                'skill': skill,
                'priority': 'high',
                'estimated_time': '2-4 weeks',
                'resources': self._get_learning_resources(skill),
                'order': i + 1
            })
        
        # Add growth skills to learning path
        for i, skill in enumerate(recommendations['growth_skills'][:2]):
            learning_path.append({
                'skill': skill,
                'priority': 'medium',
                'estimated_time': '4-8 weeks',
                'resources': self._get_learning_resources(skill),
                'order': len(learning_path) + 1
            })
        
        return learning_path
    
    def _get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resources for a skill"""
        resources = {
            'Python': ['Coursera', 'edX', 'Codecademy', 'Real Python'],
            'React': ['React Documentation', 'Udemy', 'Frontend Masters', 'YouTube'],
            'AWS': ['AWS Training', 'A Cloud Guru', 'Linux Academy', 'AWS Documentation'],
            'Machine Learning': ['Coursera ML Course', 'Fast.ai', 'Kaggle', 'MIT OpenCourseWare'],
            'Agile': ['Scrum Alliance', 'Atlassian', 'Agile Alliance', 'LinkedIn Learning']
        }
        
        return resources.get(skill, ['Online Courses', 'Documentation', 'Practice Projects', 'Community Forums'])
    
    def _log_recommendation(self, profile: Dict[str, Any], context: str, recommendations: Dict[str, Any]):
        """Log skill recommendation activity"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'profile_id': profile.get('id', 'unknown'),
            'context': context,
            'recommendations_count': len(recommendations.get('priority_skills', [])),
            'experience_level': profile.get('experience_level', 'unknown')
        }
        
        self.recommendation_history.append(log_entry)
        
        # Keep only last 100 recommendations
        if len(self.recommendation_history) > 100:
            self.recommendation_history = self.recommendation_history[-100:]
    
    async def get_recommendation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent recommendation history"""
        return self.recommendation_history[-limit:]
    
    async def get_skill_statistics(self) -> Dict[str, Any]:
        """Get skill recommendation statistics"""
        if not self.recommendation_history:
            return {'message': 'No recommendation history available'}
        
        total_recommendations = len(self.recommendation_history)
        
        # Count by experience level
        experience_counts = {}
        for entry in self.recommendation_history:
            level = entry.get('experience_level', 'unknown')
            experience_counts[level] = experience_counts.get(level, 0) + 1
        
        return {
            'total_recommendations': total_recommendations,
            'experience_level_distribution': experience_counts,
            'average_recommendations_per_request': 5.0
        }

# Global instance for easy access
skill_recommender = SkillRecommender()

# Backward compatibility function
async def recommend_skills(profile: Dict[str, Any]) -> List[str]:
    """
    Recommend skills for a given profile.
    
    Args:
        profile (dict): User profile with experience, interests, etc.
        
    Returns:
        list: Recommended skills
    """
    result = await skill_recommender.recommend_skills(profile)
    
    if result.get('success'):
        return result.get('recommendations', {}).get('priority_skills', [])
    else:
        return ["Python Programming", "Data Analysis", "Machine Learning"]  # Default fallback
