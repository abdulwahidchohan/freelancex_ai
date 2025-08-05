"""
FreelanceX.AI Weekly Reflection Agent
Specialized agent for weekly performance review and reflection
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from core.agent_manager import BaseAgent

logger = logging.getLogger(__name__)

class WeeklyReflectionAgent(BaseAgent):
    """
    Weekly Reflection Agent - Conducts weekly performance reviews and reflections
    Analyzes productivity, achievements, and areas for improvement
    """
    
    def __init__(self):
        super().__init__(
            agent_id="weekly_reflection_agent",
            name="WeeklyReflectionAgent",
            description="Conducts weekly performance reviews and reflections"
        )
        self.activities = []
        self.achievements = []
        self.improvements = []
        self.goals = []
        self.metrics = {}
        self.reflection_history = []
        
    def get_capabilities(self) -> List[str]:
        """Return weekly reflection agent capabilities"""
        return [
            'performance_review',
            'goal_tracking',
            'productivity_analysis',
            'achievement_recognition',
            'improvement_planning',
            'trend_analysis'
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process weekly reflection related tasks"""
        try:
            content = task_data.get('content', '').lower()
            task_type = task_data.get('task_type', 'general')
            
            if 'review' in content or 'reflection' in content or 'weekly' in content:
                return await self._conduct_weekly_review(task_data)
            elif 'goal' in content or 'target' in content:
                return await self._manage_goals(task_data)
            elif 'achievement' in content or 'accomplishment' in content:
                return await self._track_achievements(task_data)
            elif 'improvement' in content or 'better' in content:
                return await self._plan_improvements(task_data)
            elif 'activity' in content or 'task' in content:
                return await self._track_activities(task_data)
            else:
                return await self._general_reflection_assistance(task_data)
                
        except Exception as e:
            logger.error(f"❌ Weekly reflection agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _conduct_weekly_review(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive weekly review"""
        try:
            content = task_data.get('content', '')
            
            # Generate weekly report
            report = await self._generate_weekly_report()
            
            # Analyze performance trends
            trends = await self._analyze_performance_trends()
            
            # Generate insights
            insights = await self._generate_insights(report, trends)
            
            return {
                'success': True,
                'task_type': 'weekly_review',
                'report': report,
                'trends': trends,
                'insights': insights,
                'recommendations': self._generate_recommendations(report, trends)
            }
            
        except Exception as e:
            logger.error(f"❌ Weekly review failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _manage_goals(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage weekly goals and targets"""
        try:
            content = task_data.get('content', '')
            
            # Extract goal information
            goal_info = self._extract_goal_info(content)
            
            # Update goals
            if goal_info:
                self._update_goals(goal_info)
            
            # Track goal progress
            progress = await self._track_goal_progress()
            
            return {
                'success': True,
                'task_type': 'goal_management',
                'current_goals': self.goals,
                'goal_progress': progress,
                'goal_recommendations': self._get_goal_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Goal management failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _track_achievements(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and analyze achievements"""
        try:
            content = task_data.get('content', '')
            
            # Extract achievement information
            achievement_info = self._extract_achievement_info(content)
            
            # Add achievement
            if achievement_info:
                self._add_achievement(achievement_info)
            
            # Analyze achievements
            analysis = await self._analyze_achievements()
            
            return {
                'success': True,
                'task_type': 'achievement_tracking',
                'achievements': self.achievements,
                'analysis': analysis,
                'achievement_stats': self._get_achievement_stats()
            }
            
        except Exception as e:
            logger.error(f"❌ Achievement tracking failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _plan_improvements(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan improvements and next steps"""
        try:
            content = task_data.get('content', '')
            
            # Extract improvement areas
            improvement_areas = self._extract_improvement_areas(content)
            
            # Add improvement areas
            if improvement_areas:
                self._add_improvement_areas(improvement_areas)
            
            # Generate improvement plan
            plan = await self._generate_improvement_plan()
            
            return {
                'success': True,
                'task_type': 'improvement_planning',
                'improvement_areas': self.improvements,
                'improvement_plan': plan,
                'action_items': self._generate_action_items()
            }
            
        except Exception as e:
            logger.error(f"❌ Improvement planning failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _track_activities(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track daily activities and tasks"""
        try:
            content = task_data.get('content', '')
            
            # Extract activity information
            activity_info = self._extract_activity_info(content)
            
            # Add activity
            if activity_info:
                self._add_activity(activity_info)
            
            # Analyze activities
            analysis = await self._analyze_activities()
            
            return {
                'success': True,
                'task_type': 'activity_tracking',
                'activities': self.activities,
                'analysis': analysis,
                'activity_summary': self._get_activity_summary()
            }
            
        except Exception as e:
            logger.error(f"❌ Activity tracking failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _general_reflection_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general reflection assistance"""
        try:
            content = task_data.get('content', '')
            
            # Provide guidance
            guidance = self._generate_reflection_guidance(content)
            
            return {
                'success': True,
                'task_type': 'reflection_assistance',
                'guidance': guidance,
                'reflection_tips': self._get_reflection_tips(),
                'reflection_questions': self._get_reflection_questions()
            }
            
        except Exception as e:
            logger.error(f"❌ Reflection assistance failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_weekly_report(self) -> Dict[str, Any]:
        """Generate comprehensive weekly report"""
        report = {
            'week_ending': datetime.now().strftime('%Y-%m-%d'),
            'activities_completed': len(self.activities),
            'achievements': len(self.achievements),
            'goals_met': self._count_goals_met(),
            'improvement_areas': len(self.improvements),
            'productivity_score': self._calculate_productivity_score(),
            'summary': self._generate_summary()
        }
        
        return report
    
    def _generate_summary(self) -> str:
        """Generate weekly summary"""
        summary = f"Weekly Reflection Report - {datetime.now().strftime('%Y-%m-%d')}\n"
        summary += "=" * 50 + "\n\n"
        
        summary += f"Activities Completed: {len(self.activities)}\n"
        summary += f"Achievements: {len(self.achievements)}\n"
        summary += f"Goals Met: {self._count_goals_met()}\n"
        summary += f"Improvement Areas: {len(self.improvements)}\n"
        summary += f"Productivity Score: {self._calculate_productivity_score()}/100\n\n"
        
        if self.activities:
            summary += "Key Activities:\n"
            for i, activity in enumerate(self.activities[-5:], 1):
                summary += f"{i}. {activity.get('description', 'Unknown activity')}\n"
            summary += "\n"
        
        if self.achievements:
            summary += "Achievements:\n"
            for i, achievement in enumerate(self.achievements[-5:], 1):
                summary += f"{i}. {achievement.get('description', 'Unknown achievement')}\n"
            summary += "\n"
        
        if self.improvements:
            summary += "Areas for Improvement:\n"
            for i, improvement in enumerate(self.improvements[-5:], 1):
                summary += f"{i}. {improvement.get('description', 'Unknown improvement area')}\n"
        
        return summary
    
    async def _analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends over time"""
        if len(self.reflection_history) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        trends = {
            'productivity_trend': self._analyze_productivity_trend(),
            'achievement_trend': self._analyze_achievement_trend(),
            'goal_completion_trend': self._analyze_goal_completion_trend(),
            'improvement_areas_trend': self._analyze_improvement_trend()
        }
        
        return trends
    
    def _analyze_productivity_trend(self) -> str:
        """Analyze productivity trend"""
        if len(self.reflection_history) < 2:
            return 'stable'
        
        recent_scores = [entry.get('productivity_score', 0) for entry in self.reflection_history[-3:]]
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0]:
                return 'improving'
            elif recent_scores[-1] < recent_scores[0]:
                return 'declining'
        
        return 'stable'
    
    def _analyze_achievement_trend(self) -> str:
        """Analyze achievement trend"""
        if len(self.reflection_history) < 2:
            return 'stable'
        
        recent_achievements = [entry.get('achievements_count', 0) for entry in self.reflection_history[-3:]]
        if len(recent_achievements) >= 2:
            if recent_achievements[-1] > recent_achievements[0]:
                return 'increasing'
            elif recent_achievements[-1] < recent_achievements[0]:
                return 'decreasing'
        
        return 'stable'
    
    def _analyze_goal_completion_trend(self) -> str:
        """Analyze goal completion trend"""
        if len(self.reflection_history) < 2:
            return 'stable'
        
        recent_goals = [entry.get('goals_met', 0) for entry in self.reflection_history[-3:]]
        if len(recent_goals) >= 2:
            if recent_goals[-1] > recent_goals[0]:
                return 'improving'
            elif recent_goals[-1] < recent_goals[0]:
                return 'declining'
        
        return 'stable'
    
    def _analyze_improvement_trend(self) -> str:
        """Analyze improvement areas trend"""
        if len(self.reflection_history) < 2:
            return 'stable'
        
        recent_improvements = [entry.get('improvement_areas_count', 0) for entry in self.reflection_history[-3:]]
        if len(recent_improvements) >= 2:
            if recent_improvements[-1] < recent_improvements[0]:
                return 'improving'
            elif recent_improvements[-1] > recent_improvements[0]:
                return 'increasing'
        
        return 'stable'
    
    async def _generate_insights(self, report: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """Generate insights from report and trends"""
        insights = []
        
        # Productivity insights
        productivity_score = report.get('productivity_score', 0)
        if productivity_score >= 80:
            insights.append("Excellent productivity this week! Keep up the great work.")
        elif productivity_score >= 60:
            insights.append("Good productivity level. Small improvements can lead to even better results.")
        else:
            insights.append("Productivity could be improved. Consider focusing on time management and prioritization.")
        
        # Achievement insights
        achievements_count = report.get('achievements', 0)
        if achievements_count >= 5:
            insights.append("Impressive number of achievements this week!")
        elif achievements_count >= 3:
            insights.append("Good progress with achievements. Celebrate your wins!")
        else:
            insights.append("Consider setting smaller, achievable goals to build momentum.")
        
        # Trend insights
        productivity_trend = trends.get('productivity_trend', 'stable')
        if productivity_trend == 'improving':
            insights.append("Your productivity is trending upward - great job!")
        elif productivity_trend == 'declining':
            insights.append("Productivity has been declining. Consider what might be causing this.")
        
        return insights
    
    def _generate_recommendations(self, report: Dict[str, Any], trends: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on report and trends"""
        recommendations = []
        
        # Productivity recommendations
        productivity_score = report.get('productivity_score', 0)
        if productivity_score < 70:
            recommendations.append("Implement time blocking to improve focus and productivity")
            recommendations.append("Use the Pomodoro technique for better task management")
        
        # Goal recommendations
        goals_met = report.get('goals_met', 0)
        if goals_met < 3:
            recommendations.append("Break down larger goals into smaller, manageable tasks")
            recommendations.append("Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)")
        
        # Improvement recommendations
        improvement_areas = report.get('improvement_areas', 0)
        if improvement_areas > 5:
            recommendations.append("Focus on 2-3 key improvement areas rather than trying to improve everything at once")
        
        return recommendations
    
    def _extract_goal_info(self, content: str) -> Dict[str, Any]:
        """Extract goal information from content"""
        # Simple extraction - in a real implementation, this would use NLP
        return {
            'description': content,
            'target_date': datetime.now() + timedelta(days=7),
            'priority': 'medium',
            'status': 'active'
        }
    
    def _update_goals(self, goal_info: Dict[str, Any]):
        """Update goals list"""
        self.goals.append({
            'id': len(self.goals) + 1,
            'description': goal_info.get('description', ''),
            'target_date': goal_info.get('target_date'),
            'priority': goal_info.get('priority', 'medium'),
            'status': goal_info.get('status', 'active'),
            'created_at': datetime.now().isoformat()
        })
        logger.info(f"📋 Added new goal: {goal_info.get('description', '')}")
    
    async def _track_goal_progress(self) -> Dict[str, Any]:
        """Track progress towards goals"""
        active_goals = [goal for goal in self.goals if goal.get('status') == 'active']
        completed_goals = [goal for goal in self.goals if goal.get('status') == 'completed']
        
        return {
            'total_goals': len(self.goals),
            'active_goals': len(active_goals),
            'completed_goals': len(completed_goals),
            'completion_rate': len(completed_goals) / max(1, len(self.goals)) * 100
        }
    
    def _get_goal_recommendations(self) -> List[str]:
        """Get goal setting recommendations"""
        return [
            "Set specific, measurable goals",
            "Break down large goals into smaller tasks",
            "Set realistic deadlines",
            "Track progress regularly",
            "Celebrate small wins"
        ]
    
    def _extract_achievement_info(self, content: str) -> Dict[str, Any]:
        """Extract achievement information from content"""
        return {
            'description': content,
            'impact': 'medium',
            'category': 'general'
        }
    
    def _add_achievement(self, achievement_info: Dict[str, Any]):
        """Add achievement to list"""
        self.achievements.append({
            'id': len(self.achievements) + 1,
            'description': achievement_info.get('description', ''),
            'impact': achievement_info.get('impact', 'medium'),
            'category': achievement_info.get('category', 'general'),
            'date': datetime.now().isoformat()
        })
        logger.info(f"🏆 Added achievement: {achievement_info.get('description', '')}")
    
    async def _analyze_achievements(self) -> Dict[str, Any]:
        """Analyze achievements"""
        if not self.achievements:
            return {'message': 'No achievements recorded yet'}
        
        categories = [achievement.get('category', 'general') for achievement in self.achievements]
        impacts = [achievement.get('impact', 'medium') for achievement in self.achievements]
        
        return {
            'total_achievements': len(self.achievements),
            'category_distribution': {cat: categories.count(cat) for cat in set(categories)},
            'impact_distribution': {impact: impacts.count(impact) for impact in set(impacts)},
            'recent_achievements': self.achievements[-5:]
        }
    
    def _get_achievement_stats(self) -> Dict[str, Any]:
        """Get achievement statistics"""
        if not self.achievements:
            return {'message': 'No achievements recorded yet'}
        
        return {
            'total_achievements': len(self.achievements),
            'this_week': len([a for a in self.achievements if self._is_this_week(a.get('date'))]),
            'this_month': len([a for a in self.achievements if self._is_this_month(a.get('date'))])
        }
    
    def _extract_improvement_areas(self, content: str) -> List[Dict[str, Any]]:
        """Extract improvement areas from content"""
        return [{'description': content, 'priority': 'medium'}]
    
    def _add_improvement_areas(self, improvement_areas: List[Dict[str, Any]]):
        """Add improvement areas to list"""
        for area in improvement_areas:
            self.improvements.append({
                'id': len(self.improvements) + 1,
                'description': area.get('description', ''),
                'priority': area.get('priority', 'medium'),
                'date': datetime.now().isoformat()
            })
            logger.info(f"📈 Added improvement area: {area.get('description', '')}")
    
    async def _generate_improvement_plan(self) -> Dict[str, Any]:
        """Generate improvement plan"""
        if not self.improvements:
            return {'message': 'No improvement areas identified'}
        
        high_priority = [imp for imp in self.improvements if imp.get('priority') == 'high']
        medium_priority = [imp for imp in self.improvements if imp.get('priority') == 'medium']
        
        return {
            'high_priority_improvements': high_priority[:3],
            'medium_priority_improvements': medium_priority[:3],
            'action_plan': self._create_action_plan(),
            'timeline': 'next_week'
        }
    
    def _create_action_plan(self) -> List[str]:
        """Create action plan for improvements"""
        return [
            "Focus on one improvement area at a time",
            "Set specific, measurable targets",
            "Track progress daily",
            "Seek feedback and support",
            "Celebrate small improvements"
        ]
    
    def _generate_action_items(self) -> List[Dict[str, Any]]:
        """Generate specific action items"""
        action_items = []
        
        for improvement in self.improvements[-3:]:
            action_items.append({
                'improvement': improvement.get('description', ''),
                'action': f"Work on {improvement.get('description', '')}",
                'timeline': 'this_week',
                'priority': improvement.get('priority', 'medium')
            })
        
        return action_items
    
    def _extract_activity_info(self, content: str) -> Dict[str, Any]:
        """Extract activity information from content"""
        return {
            'description': content,
            'duration': 'unknown',
            'category': 'general'
        }
    
    def _add_activity(self, activity_info: Dict[str, Any]):
        """Add activity to list"""
        self.activities.append({
            'id': len(self.activities) + 1,
            'description': activity_info.get('description', ''),
            'duration': activity_info.get('duration', 'unknown'),
            'category': activity_info.get('category', 'general'),
            'date': datetime.now().isoformat()
        })
        logger.info(f"📝 Added activity: {activity_info.get('description', '')}")
    
    async def _analyze_activities(self) -> Dict[str, Any]:
        """Analyze activities"""
        if not self.activities:
            return {'message': 'No activities recorded yet'}
        
        categories = [activity.get('category', 'general') for activity in self.activities]
        
        return {
            'total_activities': len(self.activities),
            'category_distribution': {cat: categories.count(cat) for cat in set(categories)},
            'recent_activities': self.activities[-10:],
            'activity_trend': 'stable'
        }
    
    def _get_activity_summary(self) -> Dict[str, Any]:
        """Get activity summary"""
        if not self.activities:
            return {'message': 'No activities recorded yet'}
        
        return {
            'total_activities': len(self.activities),
            'this_week': len([a for a in self.activities if self._is_this_week(a.get('date'))]),
            'this_month': len([a for a in self.activities if self._is_this_month(a.get('date'))])
        }
    
    def _generate_reflection_guidance(self, content: str) -> str:
        """Generate reflection guidance"""
        if 'productivity' in content:
            return "Reflect on what helped or hindered your productivity this week. Identify patterns and plan improvements."
        elif 'goal' in content:
            return "Review your goals and assess progress. What worked well? What needs adjustment?"
        elif 'achievement' in content:
            return "Celebrate your achievements and identify what contributed to your success."
        else:
            return "Take time to reflect on your week. Consider what went well, what could be improved, and what you learned."
    
    def _get_reflection_tips(self) -> List[str]:
        """Get reflection tips"""
        return [
            "Set aside dedicated time for reflection",
            "Be honest with yourself about your performance",
            "Focus on both successes and areas for improvement",
            "Look for patterns in your behavior and results",
            "Use reflection to plan for the next week"
        ]
    
    def _get_reflection_questions(self) -> List[str]:
        """Get reflection questions"""
        return [
            "What were my biggest achievements this week?",
            "What challenges did I face and how did I handle them?",
            "What could I have done better?",
            "What am I grateful for this week?",
            "What are my priorities for next week?",
            "What habits or behaviors served me well?",
            "What do I want to improve or change?"
        ]
    
    def _count_goals_met(self) -> int:
        """Count goals that were met"""
        return len([goal for goal in self.goals if goal.get('status') == 'completed'])
    
    def _calculate_productivity_score(self) -> int:
        """Calculate productivity score"""
        if not self.activities and not self.achievements:
            return 0
        
        # Simple scoring based on activities and achievements
        activity_score = min(50, len(self.activities) * 5)
        achievement_score = min(50, len(self.achievements) * 10)
        
        return min(100, activity_score + achievement_score)
    
    def _is_this_week(self, date_str: str) -> bool:
        """Check if date is within this week"""
        try:
            date = datetime.fromisoformat(date_str)
            now = datetime.now()
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            return week_start <= date <= week_end
        except:
            return False
    
    def _is_this_month(self, date_str: str) -> bool:
        """Check if date is within this month"""
        try:
            date = datetime.fromisoformat(date_str)
            now = datetime.now()
            return date.year == now.year and date.month == now.month
        except:
            return False
