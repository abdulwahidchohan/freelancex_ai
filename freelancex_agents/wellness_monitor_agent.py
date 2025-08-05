"""
FreelanceX.AI Wellness Monitor Agent
Specialized agent for health and wellness tracking
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from core.agent_manager import BaseAgent

logger = logging.getLogger(__name__)

class WellnessMonitorAgent(BaseAgent):
    """
    Wellness Monitor Agent - Tracks health metrics and provides wellness insights
    Monitors sleep, activity, stress levels, and provides personalized recommendations
    """
    
    def __init__(self):
        super().__init__(
            agent_id="wellness_monitor_agent",
            name="WellnessMonitorAgent",
            description="Tracks health metrics and provides wellness insights"
        )
        self.health_metrics = {
            "heart_rate": None,
            "sleep_hours": None,
            "steps": None,
            "stress_level": None,
            "water_intake": None,
            "exercise_minutes": None,
            "screen_time": None,
            "mood": None
        }
        self.wellness_history = []
        
    def get_capabilities(self) -> List[str]:
        """Return wellness monitor agent capabilities"""
        return [
            'health_tracking',
            'wellness_analysis',
            'recommendation_generation',
            'trend_analysis',
            'goal_setting',
            'progress_monitoring'
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process wellness related tasks"""
        try:
            content = task_data.get('content', '').lower()
            task_type = task_data.get('task_type', 'general')
            
            if 'track' in content or 'update' in content or 'metrics' in content:
                return await self._update_metrics(task_data)
            elif 'analyze' in content or 'insights' in content or 'health' in content:
                return await self._analyze_wellness(task_data)
            elif 'recommend' in content or 'suggest' in content:
                return await self._generate_recommendations(task_data)
            elif 'goal' in content or 'target' in content:
                return await self._manage_goals(task_data)
            else:
                return await self._general_wellness_assistance(task_data)
                
        except Exception as e:
            logger.error(f"❌ Wellness monitor agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _update_metrics(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update health metrics"""
        try:
            content = task_data.get('content', '')
            
            # Extract metrics from content
            metrics = self._extract_metrics_from_content(content)
            
            # Update metrics
            self._update_health_metrics(metrics)
            
            # Store in history
            self._store_metrics_history(metrics)
            
            return {
                'success': True,
                'task_type': 'metrics_update',
                'updated_metrics': metrics,
                'current_status': await self._get_current_status(),
                'trends': await self._analyze_trends()
            }
            
        except Exception as e:
            logger.error(f"❌ Metrics update failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _analyze_wellness(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze wellness data and generate insights"""
        try:
            content = task_data.get('content', '')
            
            # Analyze current metrics
            analysis = await self._perform_wellness_analysis()
            
            # Generate insights
            insights = await self._generate_insights(analysis)
            
            return {
                'success': True,
                'task_type': 'wellness_analysis',
                'analysis': analysis,
                'insights': insights,
                'wellness_score': self._calculate_wellness_score(),
                'recommendations': self._get_wellness_recommendations(analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ Wellness analysis failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_recommendations(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized wellness recommendations"""
        try:
            content = task_data.get('content', '')
            
            # Analyze current state
            current_analysis = await self._perform_wellness_analysis()
            
            # Generate recommendations
            recommendations = await self._create_personalized_recommendations(current_analysis)
            
            return {
                'success': True,
                'task_type': 'recommendation_generation',
                'recommendations': recommendations,
                'priority_levels': self._prioritize_recommendations(recommendations),
                'implementation_tips': self._get_implementation_tips()
            }
            
        except Exception as e:
            logger.error(f"❌ Recommendation generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _manage_goals(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage wellness goals and targets"""
        try:
            content = task_data.get('content', '')
            
            # Extract goal parameters
            goal_params = self._extract_goal_params(content)
            
            # Manage goals
            goal_management = await self._handle_goal_management(goal_params)
            
            return {
                'success': True,
                'task_type': 'goal_management',
                'goal_management': goal_management,
                'progress_tracking': await self._track_goal_progress(),
                'goal_recommendations': self._get_goal_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Goal management failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _general_wellness_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general wellness assistance"""
        try:
            content = task_data.get('content', '')
            
            # Provide general guidance
            guidance = self._generate_wellness_guidance(content)
            
            return {
                'success': True,
                'task_type': 'wellness_assistance',
                'guidance': guidance,
                'wellness_tips': self._get_wellness_tips(),
                'health_resources': self._get_health_resources()
            }
            
        except Exception as e:
            logger.error(f"❌ Wellness assistance failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_metrics_from_content(self, content: str) -> Dict[str, Any]:
        """Extract health metrics from content"""
        metrics = {}
        
        # Extract sleep hours
        if 'sleep' in content:
            if '8' in content or 'eight' in content:
                metrics['sleep_hours'] = 8
            elif '7' in content or 'seven' in content:
                metrics['sleep_hours'] = 7
            elif '6' in content or 'six' in content:
                metrics['sleep_hours'] = 6
        
        # Extract steps
        if 'steps' in content or 'walk' in content:
            if '10000' in content or '10k' in content:
                metrics['steps'] = 10000
            elif '8000' in content or '8k' in content:
                metrics['steps'] = 8000
            elif '5000' in content or '5k' in content:
                metrics['steps'] = 5000
        
        # Extract exercise
        if 'exercise' in content or 'workout' in content:
            if '30' in content:
                metrics['exercise_minutes'] = 30
            elif '60' in content or 'hour' in content:
                metrics['exercise_minutes'] = 60
        
        # Extract water intake
        if 'water' in content or 'drink' in content:
            if '8' in content:
                metrics['water_intake'] = 8  # glasses
            elif '2' in content and 'liter' in content:
                metrics['water_intake'] = 2  # liters
        
        return metrics
    
    def _update_health_metrics(self, new_metrics: Dict[str, Any]):
        """Update health metrics with new data"""
        for metric, value in new_metrics.items():
            if metric in self.health_metrics:
                self.health_metrics[metric] = value
                logger.info(f"📊 Updated {metric}: {value}")
    
    def _store_metrics_history(self, metrics: Dict[str, Any]):
        """Store metrics in history for trend analysis"""
        if metrics:
            history_entry = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics.copy()
            }
            self.wellness_history.append(history_entry)
            
            # Keep only last 30 days of history
            if len(self.wellness_history) > 30:
                self.wellness_history = self.wellness_history[-30:]
    
    async def _get_current_status(self) -> Dict[str, Any]:
        """Get current wellness status"""
        return {
            'overall_status': self._get_overall_status(),
            'metrics_summary': self._get_metrics_summary(),
            'last_updated': datetime.now().isoformat(),
            'data_completeness': self._calculate_data_completeness()
        }
    
    async def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze wellness trends over time"""
        if len(self.wellness_history) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        trends = {}
        
        # Analyze sleep trends
        sleep_data = [entry['metrics'].get('sleep_hours') for entry in self.wellness_history if entry['metrics'].get('sleep_hours')]
        if sleep_data:
            trends['sleep'] = {
                'average': sum(sleep_data) / len(sleep_data),
                'trend': 'improving' if len(sleep_data) > 1 and sleep_data[-1] > sleep_data[0] else 'stable'
            }
        
        # Analyze steps trends
        steps_data = [entry['metrics'].get('steps') for entry in self.wellness_history if entry['metrics'].get('steps')]
        if steps_data:
            trends['steps'] = {
                'average': sum(steps_data) / len(steps_data),
                'trend': 'improving' if len(steps_data) > 1 and steps_data[-1] > steps_data[0] else 'stable'
            }
        
        return trends
    
    async def _perform_wellness_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive wellness analysis"""
        analysis = {
            'sleep_analysis': self._analyze_sleep(),
            'activity_analysis': self._analyze_activity(),
            'stress_analysis': self._analyze_stress(),
            'nutrition_analysis': self._analyze_nutrition(),
            'overall_health_score': self._calculate_wellness_score()
        }
        
        return analysis
    
    def _analyze_sleep(self) -> Dict[str, Any]:
        """Analyze sleep patterns"""
        sleep_hours = self.health_metrics.get('sleep_hours')
        
        if sleep_hours is None:
            return {'status': 'no_data', 'recommendation': 'Track your sleep hours'}
        
        if sleep_hours < 6:
            return {'status': 'poor', 'recommendation': 'Aim for 7-9 hours of sleep'}
        elif sleep_hours < 7:
            return {'status': 'fair', 'recommendation': 'Try to get 7-8 hours of sleep'}
        elif sleep_hours <= 9:
            return {'status': 'good', 'recommendation': 'Maintain this sleep pattern'}
        else:
            return {'status': 'excessive', 'recommendation': 'Consider reducing sleep to 7-9 hours'}
    
    def _analyze_activity(self) -> Dict[str, Any]:
        """Analyze physical activity"""
        steps = self.health_metrics.get('steps')
        exercise_minutes = self.health_metrics.get('exercise_minutes')
        
        if steps is None and exercise_minutes is None:
            return {'status': 'no_data', 'recommendation': 'Track your daily activity'}
        
        activity_score = 0
        if steps and steps >= 10000:
            activity_score += 50
        elif steps and steps >= 8000:
            activity_score += 40
        elif steps and steps >= 5000:
            activity_score += 30
        
        if exercise_minutes and exercise_minutes >= 30:
            activity_score += 50
        
        if activity_score >= 80:
            return {'status': 'excellent', 'recommendation': 'Keep up the great work!'}
        elif activity_score >= 60:
            return {'status': 'good', 'recommendation': 'Consider increasing activity slightly'}
        else:
            return {'status': 'needs_improvement', 'recommendation': 'Aim for 10,000 steps or 30 minutes of exercise'}
    
    def _analyze_stress(self) -> Dict[str, Any]:
        """Analyze stress levels"""
        stress_level = self.health_metrics.get('stress_level')
        
        if stress_level is None:
            return {'status': 'no_data', 'recommendation': 'Track your stress levels'}
        
        if stress_level <= 3:
            return {'status': 'low', 'recommendation': 'Maintain good stress management'}
        elif stress_level <= 6:
            return {'status': 'moderate', 'recommendation': 'Consider stress reduction techniques'}
        else:
            return {'status': 'high', 'recommendation': 'Prioritize stress management and relaxation'}
    
    def _analyze_nutrition(self) -> Dict[str, Any]:
        """Analyze nutrition and hydration"""
        water_intake = self.health_metrics.get('water_intake')
        
        if water_intake is None:
            return {'status': 'no_data', 'recommendation': 'Track your water intake'}
        
        if water_intake >= 8:
            return {'status': 'good', 'recommendation': 'Maintain good hydration'}
        else:
            return {'status': 'needs_improvement', 'recommendation': 'Aim for 8 glasses of water daily'}
    
    def _calculate_wellness_score(self) -> int:
        """Calculate overall wellness score"""
        score = 0
        metrics_count = 0
        
        # Sleep score (0-25 points)
        sleep_hours = self.health_metrics.get('sleep_hours')
        if sleep_hours:
            if 7 <= sleep_hours <= 9:
                score += 25
            elif 6 <= sleep_hours <= 10:
                score += 20
            elif 5 <= sleep_hours <= 11:
                score += 15
            else:
                score += 5
            metrics_count += 1
        
        # Activity score (0-25 points)
        steps = self.health_metrics.get('steps')
        exercise_minutes = self.health_metrics.get('exercise_minutes')
        if steps or exercise_minutes:
            activity_score = 0
            if steps and steps >= 10000:
                activity_score += 15
            elif steps and steps >= 8000:
                activity_score += 12
            elif steps and steps >= 5000:
                activity_score += 8
            
            if exercise_minutes and exercise_minutes >= 30:
                activity_score += 10
            elif exercise_minutes and exercise_minutes >= 15:
                activity_score += 5
            
            score += min(25, activity_score)
            metrics_count += 1
        
        # Stress score (0-25 points)
        stress_level = self.health_metrics.get('stress_level')
        if stress_level is not None:
            if stress_level <= 3:
                score += 25
            elif stress_level <= 6:
                score += 15
            else:
                score += 5
            metrics_count += 1
        
        # Hydration score (0-25 points)
        water_intake = self.health_metrics.get('water_intake')
        if water_intake:
            if water_intake >= 8:
                score += 25
            elif water_intake >= 6:
                score += 20
            elif water_intake >= 4:
                score += 15
            else:
                score += 5
            metrics_count += 1
        
        return round(score / max(1, metrics_count))
    
    async def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate wellness insights"""
        insights = []
        
        # Sleep insights
        sleep_analysis = analysis.get('sleep_analysis', {})
        if sleep_analysis.get('status') == 'poor':
            insights.append("Your sleep quality needs improvement. Consider establishing a consistent bedtime routine.")
        
        # Activity insights
        activity_analysis = analysis.get('activity_analysis', {})
        if activity_analysis.get('status') == 'needs_improvement':
            insights.append("Increasing your daily activity can significantly improve your overall health.")
        
        # Stress insights
        stress_analysis = analysis.get('stress_analysis', {})
        if stress_analysis.get('status') == 'high':
            insights.append("High stress levels detected. Consider meditation, exercise, or other stress management techniques.")
        
        # Overall insights
        overall_score = analysis.get('overall_health_score', 0)
        if overall_score >= 80:
            insights.append("Excellent overall wellness! Keep maintaining these healthy habits.")
        elif overall_score >= 60:
            insights.append("Good wellness foundation. Small improvements can lead to significant benefits.")
        else:
            insights.append("Focus on building healthy habits gradually. Start with one area and expand.")
        
        return insights
    
    def _get_wellness_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Get wellness recommendations based on analysis"""
        recommendations = []
        
        # Sleep recommendations
        sleep_analysis = analysis.get('sleep_analysis', {})
        if sleep_analysis.get('status') in ['poor', 'fair']:
            recommendations.append("Establish a consistent sleep schedule and create a relaxing bedtime routine")
        
        # Activity recommendations
        activity_analysis = analysis.get('activity_analysis', {})
        if activity_analysis.get('status') == 'needs_improvement':
            recommendations.append("Start with 30 minutes of daily exercise and gradually increase to 60 minutes")
        
        # Stress recommendations
        stress_analysis = analysis.get('stress_analysis', {})
        if stress_analysis.get('status') == 'high':
            recommendations.append("Practice daily meditation or deep breathing exercises for 10-15 minutes")
        
        # General recommendations
        recommendations.extend([
            "Stay hydrated by drinking 8 glasses of water daily",
            "Take regular breaks from screen time",
            "Maintain a balanced diet with plenty of fruits and vegetables"
        ])
        
        return recommendations
    
    async def _create_personalized_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create personalized wellness recommendations"""
        recommendations = []
        
        overall_score = analysis.get('overall_health_score', 0)
        
        if overall_score < 60:
            recommendations.append({
                'category': 'sleep',
                'priority': 'high',
                'recommendation': 'Focus on getting 7-9 hours of quality sleep',
                'action_steps': ['Set a consistent bedtime', 'Create a relaxing routine', 'Avoid screens before bed']
            })
            
            recommendations.append({
                'category': 'activity',
                'priority': 'high',
                'recommendation': 'Start with 30 minutes of daily physical activity',
                'action_steps': ['Take daily walks', 'Try home workouts', 'Use stairs instead of elevator']
            })
        
        elif overall_score < 80:
            recommendations.append({
                'category': 'optimization',
                'priority': 'medium',
                'recommendation': 'Optimize your current habits for better results',
                'action_steps': ['Track your progress', 'Set specific goals', 'Find an accountability partner']
            })
        
        else:
            recommendations.append({
                'category': 'maintenance',
                'priority': 'low',
                'recommendation': 'Maintain your excellent wellness habits',
                'action_steps': ['Continue current routine', 'Share your success with others', 'Set new challenges']
            })
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Prioritize recommendations by importance"""
        prioritized = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        for rec in recommendations:
            priority = rec.get('priority', 'medium')
            prioritized[priority].append(rec)
        
        return prioritized
    
    def _get_implementation_tips(self) -> List[str]:
        """Get tips for implementing wellness recommendations"""
        return [
            "Start with one change at a time",
            "Set specific, measurable goals",
            "Track your progress regularly",
            "Find activities you enjoy",
            "Build a support system",
            "Be patient with yourself"
        ]
    
    def _extract_goal_params(self, content: str) -> Dict[str, Any]:
        """Extract goal parameters from content"""
        return {
            'goal_type': 'general',
            'target_value': None,
            'timeframe': 'weekly'
        }
    
    async def _handle_goal_management(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle goal management"""
        return {
            'current_goals': [],
            'goal_progress': {},
            'goal_recommendations': self._get_goal_recommendations()
        }
    
    async def _track_goal_progress(self) -> Dict[str, Any]:
        """Track progress towards wellness goals"""
        return {
            'goals_completed': 0,
            'goals_in_progress': 0,
            'overall_progress': 0.0
        }
    
    def _get_goal_recommendations(self) -> List[str]:
        """Get goal setting recommendations"""
        return [
            "Set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)",
            "Start with small, achievable goals",
            "Track your progress regularly",
            "Celebrate small wins",
            "Adjust goals as needed"
        ]
    
    def _generate_wellness_guidance(self, content: str) -> str:
        """Generate wellness guidance"""
        if 'sleep' in content:
            return "Quality sleep is fundamental to wellness. Aim for 7-9 hours and maintain a consistent schedule."
        elif 'exercise' in content or 'activity' in content:
            return "Regular physical activity improves both physical and mental health. Start with 30 minutes daily."
        elif 'stress' in content:
            return "Managing stress is crucial for overall wellness. Try meditation, exercise, or other relaxation techniques."
        else:
            return "Wellness is about balance. Focus on sleep, nutrition, activity, and stress management for optimal health."
    
    def _get_wellness_tips(self) -> List[str]:
        """Get general wellness tips"""
        return [
            "Get 7-9 hours of quality sleep each night",
            "Exercise for at least 30 minutes daily",
            "Stay hydrated by drinking 8 glasses of water",
            "Practice stress management techniques",
            "Maintain a balanced diet",
            "Take regular breaks from screens",
            "Connect with others regularly"
        ]
    
    def _get_health_resources(self) -> List[str]:
        """Get health and wellness resources"""
        return [
            "Sleep tracking apps (Sleep Cycle, Fitbit)",
            "Fitness apps (MyFitnessPal, Strava)",
            "Meditation apps (Headspace, Calm)",
            "Health monitoring devices (Fitbit, Apple Watch)",
            "Online fitness programs",
            "Wellness blogs and podcasts"
        ]
    
    def _get_overall_status(self) -> str:
        """Get overall wellness status"""
        score = self._calculate_wellness_score()
        
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of current metrics"""
        return {
            'sleep_hours': self.health_metrics.get('sleep_hours'),
            'steps': self.health_metrics.get('steps'),
            'exercise_minutes': self.health_metrics.get('exercise_minutes'),
            'water_intake': self.health_metrics.get('water_intake'),
            'stress_level': self.health_metrics.get('stress_level')
        }
    
    def _calculate_data_completeness(self) -> float:
        """Calculate completeness of health data"""
        total_metrics = len(self.health_metrics)
        filled_metrics = sum(1 for value in self.health_metrics.values() if value is not None)
        return (filled_metrics / total_metrics) * 100
