import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
import uuid
from enum import Enum

# Import the core components
from core.agent_manager import AgentManager
from core.user_profile_manager import UserProfileManager
from agents.job_search_agent import JobSearchAgent
from agents.web_search_agent import WebSearchAgent
from agents.math_agent import MathAgent

class RoutineType(Enum):
    """Routine type enumeration"""
    MORNING = "morning"
    WORK_SESSION = "work_session"
    END_OF_DAY = "end_of_day"
    WEEKLY_REFLECTION = "weekly_reflection"

@dataclass
class RoutineTask:
    """Data class for routine tasks"""
    id: str
    routine_type: RoutineType
    task_name: str
    description: str
    agent_id: str
    status: str  # pending, in_progress, completed, failed
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error_message: Optional[str] = None
    priority: int = 1

@dataclass
class DailySummary:
    """Data class for daily summary"""
    date: datetime
    routine_type: RoutineType
    tasks_completed: int
    tasks_failed: int
    total_time_spent: int  # seconds
    key_insights: List[str]
    recommendations: List[str]
    next_actions: List[str]
    performance_metrics: Dict[str, Any]

class DailyRoutinesManager:
    """
    Daily Routines Manager for FreelanceX.AI
    
    Morning Routine:
    - Agents will review new job listings and market trends
    - WebSearchAgent will send a daily digest of new research, business growth tips, and competitive insights
    
    Work Session:
    - JobSearchAgent will ping alerts about new tasks based on the user's profile
    - MathAgent could assist in calculating hourly rates, taxes, and budget projections
    
    End of Day Summary:
    - A quick summary of the day's performance, including time spent on tasks, 
      the number of applications sent, and any new research insights provided
    """
    
    def __init__(self, agent_manager: AgentManager, user_profile_manager: UserProfileManager):
        self.logger = logging.getLogger(__name__)
        self.agent_manager = agent_manager
        self.user_profile_manager = user_profile_manager
        
        # Routine configurations
        self.routine_configs = {
            RoutineType.MORNING: {
                'enabled': True,
                'scheduled_time': '09:00',  # 9 AM
                'timezone': 'UTC',
                'tasks': [
                    {
                        'name': 'job_market_review',
                        'description': 'Review new job listings and market trends',
                        'agent': 'job_search',
                        'method': 'find_jobs',
                        'priority': 1
                    },
                    {
                        'name': 'research_digest',
                        'description': 'Generate daily research digest',
                        'agent': 'web_search',
                        'method': 'research_topic',
                        'priority': 2
                    },
                    {
                        'name': 'financial_check',
                        'description': 'Review financial metrics and projections',
                        'agent': 'math',
                        'method': 'calculate_financial_metrics',
                        'priority': 3
                    }
                ]
            },
            RoutineType.WORK_SESSION: {
                'enabled': True,
                'check_interval': 1800,  # 30 minutes
                'tasks': [
                    {
                        'name': 'job_alerts',
                        'description': 'Check for new job alerts',
                        'agent': 'job_search',
                        'method': 'find_jobs',
                        'priority': 1
                    },
                    {
                        'name': 'financial_calculations',
                        'description': 'Assist with financial calculations',
                        'agent': 'math',
                        'method': 'calculate_financial_metrics',
                        'priority': 2
                    }
                ]
            },
            RoutineType.END_OF_DAY: {
                'enabled': True,
                'scheduled_time': '18:00',  # 6 PM
                'timezone': 'UTC',
                'tasks': [
                    {
                        'name': 'performance_summary',
                        'description': 'Generate daily performance summary',
                        'agent': 'math',
                        'method': 'perform_statistical_analysis',
                        'priority': 1
                    },
                    {
                        'name': 'research_insights',
                        'description': 'Summarize research insights',
                        'agent': 'web_search',
                        'method': 'research_topic',
                        'priority': 2
                    }
                ]
            },
            RoutineType.WEEKLY_REFLECTION: {
                'enabled': True,
                'scheduled_day': 'sunday',
                'scheduled_time': '10:00',
                'timezone': 'UTC',
                'tasks': [
                    {
                        'name': 'weekly_analysis',
                        'description': 'Analyze weekly performance and trends',
                        'agent': 'math',
                        'method': 'perform_statistical_analysis',
                        'priority': 1
                    },
                    {
                        'name': 'skill_assessment',
                        'description': 'Assess skill development progress',
                        'agent': 'web_search',
                        'method': 'research_topic',
                        'priority': 2
                    }
                ]
            }
        }
        
        # Routine execution tracking
        self.routine_history: List[DailySummary] = []
        self.active_routines: Dict[str, List[RoutineTask]] = {}
        self.routine_schedules = {}
        
        # Performance tracking
        self.daily_metrics = {
            'tasks_completed': 0,
            'applications_sent': 0,
            'research_insights': 0,
            'financial_calculations': 0,
            'time_spent': 0
        }
        
        # Notification settings
        self.notification_settings = {
            'email_notifications': True,
            'push_notifications': True,
            'summary_frequency': 'daily',  # daily, weekly, monthly
            'preferred_time': '18:00'
        }

    async def start_routine_scheduler(self):
        """Start the routine scheduler"""
        self.logger.info("Starting Daily Routines Scheduler...")
        
        # Start background tasks for each routine type
        asyncio.create_task(self._morning_routine_scheduler())
        asyncio.create_task(self._work_session_monitor())
        asyncio.create_task(self._end_of_day_scheduler())
        asyncio.create_task(self._weekly_reflection_scheduler())
        
        self.logger.info("Daily Routines Scheduler started successfully")

    async def _morning_routine_scheduler(self):
        """Schedule and execute morning routines"""
        while True:
            try:
                now = datetime.now()
                scheduled_time = datetime.strptime(
                    self.routine_configs[RoutineType.MORNING]['scheduled_time'], 
                    '%H:%M'
                ).replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                # Check if it's time for morning routine
                if now.hour == scheduled_time.hour and now.minute == scheduled_time.minute:
                    await self.execute_morning_routine()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in morning routine scheduler: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _work_session_monitor(self):
        """Monitor work sessions throughout the day"""
        while True:
            try:
                # Check if work session routine is enabled
                if self.routine_configs[RoutineType.WORK_SESSION]['enabled']:
                    await self.execute_work_session_routine()
                
                # Wait for next check
                interval = self.routine_configs[RoutineType.WORK_SESSION]['check_interval']
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in work session monitor: {e}")
                await asyncio.sleep(300)

    async def _end_of_day_scheduler(self):
        """Schedule and execute end of day routines"""
        while True:
            try:
                now = datetime.now()
                scheduled_time = datetime.strptime(
                    self.routine_configs[RoutineType.END_OF_DAY]['scheduled_time'], 
                    '%H:%M'
                ).replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                # Check if it's time for end of day routine
                if now.hour == scheduled_time.hour and now.minute == scheduled_time.minute:
                    await self.execute_end_of_day_routine()
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in end of day scheduler: {e}")
                await asyncio.sleep(300)

    async def _weekly_reflection_scheduler(self):
        """Schedule and execute weekly reflection routines"""
        while True:
            try:
                now = datetime.now()
                scheduled_day = self.routine_configs[RoutineType.WEEKLY_REFLECTION]['scheduled_day']
                scheduled_time = datetime.strptime(
                    self.routine_configs[RoutineType.WEEKLY_REFLECTION]['scheduled_time'], 
                    '%H:%M'
                ).replace(
                    year=now.year, month=now.month, day=now.day
                )
                
                # Check if it's the scheduled day and time
                if (now.strftime('%A').lower() == scheduled_day.lower() and 
                    now.hour == scheduled_time.hour and now.minute == scheduled_time.minute):
                    await self.execute_weekly_reflection_routine()
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in weekly reflection scheduler: {e}")
                await asyncio.sleep(3600)

    async def execute_morning_routine(self) -> DailySummary:
        """Execute the morning routine"""
        self.logger.info("Executing morning routine...")
        
        routine_id = f"morning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tasks = []
        
        # Create tasks for morning routine
        for task_config in self.routine_configs[RoutineType.MORNING]['tasks']:
            task = RoutineTask(
                id=str(uuid.uuid4()),
                routine_type=RoutineType.MORNING,
                task_name=task_config['name'],
                description=task_config['description'],
                agent_id=task_config['agent'],
                status='pending',
                created_at=datetime.now(),
                priority=task_config['priority']
            )
            tasks.append(task)
        
        self.active_routines[routine_id] = tasks
        
        # Execute tasks
        results = await self._execute_routine_tasks(tasks)
        
        # Generate morning digest
        digest = await self._generate_morning_digest(results)
        
        # Create summary
        summary = DailySummary(
            date=datetime.now(),
            routine_type=RoutineType.MORNING,
            tasks_completed=len([t for t in tasks if t.status == 'completed']),
            tasks_failed=len([t for t in tasks if t.status == 'failed']),
            total_time_spent=sum(t.completed_at.timestamp() - t.started_at.timestamp() 
                               for t in tasks if t.completed_at and t.started_at),
            key_insights=digest['key_insights'],
            recommendations=digest['recommendations'],
            next_actions=digest['next_actions'],
            performance_metrics=self.daily_metrics
        )
        
        self.routine_history.append(summary)
        
        # Send notifications
        await self._send_morning_notifications(digest)
        
        self.logger.info("Morning routine completed successfully")
        return summary

    async def execute_work_session_routine(self) -> DailySummary:
        """Execute the work session routine"""
        self.logger.info("Executing work session routine...")
        
        routine_id = f"work_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tasks = []
        
        # Create tasks for work session
        for task_config in self.routine_configs[RoutineType.WORK_SESSION]['tasks']:
            task = RoutineTask(
                id=str(uuid.uuid4()),
                routine_type=RoutineType.WORK_SESSION,
                task_name=task_config['name'],
                description=task_config['description'],
                agent_id=task_config['agent'],
                status='pending',
                created_at=datetime.now(),
                priority=task_config['priority']
            )
            tasks.append(task)
        
        self.active_routines[routine_id] = tasks
        
        # Execute tasks
        results = await self._execute_routine_tasks(tasks)
        
        # Generate work session summary
        summary = await self._generate_work_session_summary(results)
        
        # Create summary
        daily_summary = DailySummary(
            date=datetime.now(),
            routine_type=RoutineType.WORK_SESSION,
            tasks_completed=len([t for t in tasks if t.status == 'completed']),
            tasks_failed=len([t for t in tasks if t.status == 'failed']),
            total_time_spent=sum(t.completed_at.timestamp() - t.started_at.timestamp() 
                               for t in tasks if t.completed_at and t.started_at),
            key_insights=summary['key_insights'],
            recommendations=summary['recommendations'],
            next_actions=summary['next_actions'],
            performance_metrics=self.daily_metrics
        )
        
        self.routine_history.append(daily_summary)
        
        self.logger.info("Work session routine completed successfully")
        return daily_summary

    async def execute_end_of_day_routine(self) -> DailySummary:
        """Execute the end of day routine"""
        self.logger.info("Executing end of day routine...")
        
        routine_id = f"end_of_day_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tasks = []
        
        # Create tasks for end of day routine
        for task_config in self.routine_configs[RoutineType.END_OF_DAY]['tasks']:
            task = RoutineTask(
                id=str(uuid.uuid4()),
                routine_type=RoutineType.END_OF_DAY,
                task_name=task_config['name'],
                description=task_config['description'],
                agent_id=task_config['agent'],
                status='pending',
                created_at=datetime.now(),
                priority=task_config['priority']
            )
            tasks.append(task)
        
        self.active_routines[routine_id] = tasks
        
        # Execute tasks
        results = await self._execute_routine_tasks(tasks)
        
        # Generate end of day summary
        summary = await self._generate_end_of_day_summary(results)
        
        # Create summary
        daily_summary = DailySummary(
            date=datetime.now(),
            routine_type=RoutineType.END_OF_DAY,
            tasks_completed=len([t for t in tasks if t.status == 'completed']),
            tasks_failed=len([t for t in tasks if t.status == 'failed']),
            total_time_spent=sum(t.completed_at.timestamp() - t.started_at.timestamp() 
                               for t in tasks if t.completed_at and t.started_at),
            key_insights=summary['key_insights'],
            recommendations=summary['recommendations'],
            next_actions=summary['next_actions'],
            performance_metrics=self.daily_metrics
        )
        
        self.routine_history.append(daily_summary)
        
        # Send end of day notifications
        await self._send_end_of_day_notifications(summary)
        
        # Reset daily metrics
        self._reset_daily_metrics()
        
        self.logger.info("End of day routine completed successfully")
        return daily_summary

    async def execute_weekly_reflection_routine(self) -> DailySummary:
        """Execute the weekly reflection routine"""
        self.logger.info("Executing weekly reflection routine...")
        
        routine_id = f"weekly_reflection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        tasks = []
        
        # Create tasks for weekly reflection
        for task_config in self.routine_configs[RoutineType.WEEKLY_REFLECTION]['tasks']:
            task = RoutineTask(
                id=str(uuid.uuid4()),
                routine_type=RoutineType.WEEKLY_REFLECTION,
                task_name=task_config['name'],
                description=task_config['description'],
                agent_id=task_config['agent'],
                status='pending',
                created_at=datetime.now(),
                priority=task_config['priority']
            )
            tasks.append(task)
        
        self.active_routines[routine_id] = tasks
        
        # Execute tasks
        results = await self._execute_routine_tasks(tasks)
        
        # Generate weekly reflection summary
        summary = await self._generate_weekly_reflection_summary(results)
        
        # Create summary
        weekly_summary = DailySummary(
            date=datetime.now(),
            routine_type=RoutineType.WEEKLY_REFLECTION,
            tasks_completed=len([t for t in tasks if t.status == 'completed']),
            tasks_failed=len([t for t in tasks if t.status == 'failed']),
            total_time_spent=sum(t.completed_at.timestamp() - t.started_at.timestamp() 
                               for t in tasks if t.completed_at and t.started_at),
            key_insights=summary['key_insights'],
            recommendations=summary['recommendations'],
            next_actions=summary['next_actions'],
            performance_metrics=self.daily_metrics
        )
        
        self.routine_history.append(weekly_summary)
        
        # Send weekly reflection notifications
        await self._send_weekly_reflection_notifications(summary)
        
        self.logger.info("Weekly reflection routine completed successfully")
        return weekly_summary

    async def _execute_routine_tasks(self, tasks: List[RoutineTask]) -> Dict[str, Any]:
        """Execute a list of routine tasks"""
        results = {}
        
        # Sort tasks by priority
        tasks.sort(key=lambda t: t.priority)
        
        for task in tasks:
            try:
                task.status = 'in_progress'
                task.started_at = datetime.now()
                
                # Execute task using agent manager
                result = await self.agent_manager.submit_task(
                    task_name=task.task_name,
                    agent_id=task.agent_id,
                    input_data=self._get_task_input_data(task),
                    priority='medium'
                )
                
                task.result = result
                task.status = 'completed'
                task.completed_at = datetime.now()
                
                results[task.task_name] = result
                
                # Update daily metrics
                self._update_daily_metrics(task)
                
            except Exception as e:
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = datetime.now()
                
                self.logger.error(f"Task {task.task_name} failed: {e}")
        
        return results

    def _get_task_input_data(self, task: RoutineTask) -> Dict[str, Any]:
        """Get input data for a specific task"""
        user_profile = self.user_profile_manager.get_profile_summary()
        
        if task.task_name == 'job_market_review':
            return {
                'platforms': user_profile.get('agent_preferences', {}).get('job_search', {}).get('preferred_platforms', []),
                'use_ai_matching': True
            }
        elif task.task_name == 'research_digest':
            return {
                'topic': 'freelancing trends and business growth',
                'depth': 'comprehensive'
            }
        elif task.task_name == 'financial_check':
            financial_data = self.user_profile_manager.get_financial_data_for_calculations()
            return {
                'financial_data': financial_data,
                'metric_type': 'hourly_rate'
            }
        elif task.task_name == 'job_alerts':
            return {
                'platforms': None,
                'use_ai_matching': True
            }
        elif task.task_name == 'financial_calculations':
            return {
                'financial_data': self.user_profile_manager.get_financial_data_for_calculations(),
                'metric_type': 'profit_margin'
            }
        elif task.task_name == 'performance_summary':
            return {
                'data': self._get_daily_performance_data(),
                'analysis_type': 'descriptive'
            }
        elif task.task_name == 'research_insights':
            return {
                'topic': 'freelancing insights and opportunities',
                'depth': 'standard'
            }
        else:
            return {}

    def _get_daily_performance_data(self) -> List[float]:
        """Get daily performance data for analysis"""
        # This would collect actual performance data
        # For now, return sample data
        return [85.5, 92.3, 78.9, 88.2, 95.1, 87.6, 91.4]

    def _update_daily_metrics(self, task: RoutineTask):
        """Update daily metrics based on completed task"""
        if task.status == 'completed':
            self.daily_metrics['tasks_completed'] += 1
            
            if 'job' in task.task_name.lower():
                self.daily_metrics['applications_sent'] += 1
            elif 'research' in task.task_name.lower():
                self.daily_metrics['research_insights'] += 1
            elif 'financial' in task.task_name.lower():
                self.daily_metrics['financial_calculations'] += 1
            
            if task.completed_at and task.started_at:
                time_spent = int((task.completed_at - task.started_at).total_seconds())
                self.daily_metrics['time_spent'] += time_spent

    def _reset_daily_metrics(self):
        """Reset daily metrics for the next day"""
        self.daily_metrics = {
            'tasks_completed': 0,
            'applications_sent': 0,
            'research_insights': 0,
            'financial_calculations': 0,
            'time_spent': 0
        }

    async def _generate_morning_digest(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate morning digest from routine results"""
        digest = {
            'key_insights': [],
            'recommendations': [],
            'next_actions': []
        }
        
        # Process job market review results
        if 'job_market_review' in results:
            jobs = results['job_market_review']
            if isinstance(jobs, list) and jobs:
                digest['key_insights'].append(f"Found {len(jobs)} new job opportunities")
                digest['recommendations'].append("Review and apply to high-priority positions")
                digest['next_actions'].append("Set aside time to craft personalized applications")
        
        # Process research digest results
        if 'research_digest' in results:
            research = results['research_digest']
            if isinstance(research, dict) and 'insights' in research:
                insights = research['insights']
                if 'trends' in insights:
                    digest['key_insights'].extend(insights['trends'])
                if 'recommendations' in insights:
                    digest['recommendations'].extend(insights['recommendations'])
        
        # Process financial check results
        if 'financial_check' in results:
            financial = results['financial_check']
            if hasattr(financial, 'result'):
                digest['key_insights'].append("Financial metrics reviewed and updated")
                digest['recommendations'].append("Consider adjusting rates based on market analysis")
        
        return digest

    async def _generate_work_session_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate work session summary"""
        summary = {
            'key_insights': [],
            'recommendations': [],
            'next_actions': []
        }
        
        # Process job alerts
        if 'job_alerts' in results:
            jobs = results['job_alerts']
            if isinstance(jobs, list) and jobs:
                summary['key_insights'].append(f"New job alerts: {len(jobs)} opportunities")
                summary['next_actions'].append("Review new job postings")
        
        # Process financial calculations
        if 'financial_calculations' in results:
            financial = results['financial_calculations']
            if hasattr(financial, 'result'):
                summary['key_insights'].append("Financial calculations completed")
                summary['recommendations'].append("Use calculated rates for project pricing")
        
        return summary

    async def _generate_end_of_day_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate end of day summary"""
        summary = {
            'key_insights': [],
            'recommendations': [],
            'next_actions': []
        }
        
        # Add daily performance insights
        summary['key_insights'].append(f"Completed {self.daily_metrics['tasks_completed']} tasks today")
        summary['key_insights'].append(f"Spent {self.daily_metrics['time_spent']} seconds on productive activities")
        
        if self.daily_metrics['applications_sent'] > 0:
            summary['key_insights'].append(f"Sent {self.daily_metrics['applications_sent']} job applications")
        
        # Process performance summary
        if 'performance_summary' in results:
            performance = results['performance_summary']
            if hasattr(performance, 'mean'):
                summary['key_insights'].append(f"Average performance score: {performance.mean:.1f}")
        
        # Process research insights
        if 'research_insights' in results:
            research = results['research_insights']
            if isinstance(research, dict) and 'insights' in research:
                insights = research['insights']
                if 'recommendations' in insights:
                    summary['recommendations'].extend(insights['recommendations'])
        
        # Generate next actions for tomorrow
        summary['next_actions'].extend([
            "Review today's insights and plan tomorrow's priorities",
            "Follow up on any pending applications or responses",
            "Update skill development progress"
        ])
        
        return summary

    async def _generate_weekly_reflection_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate weekly reflection summary"""
        summary = {
            'key_insights': [],
            'recommendations': [],
            'next_actions': []
        }
        
        # Analyze weekly performance
        weekly_routines = [r for r in self.routine_history 
                          if r.date > datetime.now() - timedelta(days=7)]
        
        if weekly_routines:
            total_tasks = sum(r.tasks_completed for r in weekly_routines)
            total_time = sum(r.total_time_spent for r in weekly_routines)
            
            summary['key_insights'].append(f"Weekly summary: {total_tasks} tasks completed")
            summary['key_insights'].append(f"Total productive time: {total_time/3600:.1f} hours")
        
        # Process weekly analysis
        if 'weekly_analysis' in results:
            analysis = results['weekly_analysis']
            if hasattr(analysis, 'trends'):
                summary['key_insights'].append("Weekly trends analyzed")
        
        # Process skill assessment
        if 'skill_assessment' in results:
            assessment = results['skill_assessment']
            if isinstance(assessment, dict) and 'insights' in assessment:
                insights = assessment['insights']
                if 'recommendations' in insights:
                    summary['recommendations'].extend(insights['recommendations'])
        
        # Generate weekly recommendations
        summary['recommendations'].extend([
            "Review and adjust goals for the upcoming week",
            "Focus on high-impact activities based on weekly analysis",
            "Plan skill development activities"
        ])
        
        return summary

    async def _send_morning_notifications(self, digest: Dict[str, Any]):
        """Send morning routine notifications"""
        if self.notification_settings['email_notifications']:
            # This would implement actual email sending
            self.logger.info("Morning digest email sent")
        
        if self.notification_settings['push_notifications']:
            # This would implement actual push notifications
            self.logger.info("Morning digest push notification sent")

    async def _send_end_of_day_notifications(self, summary: DailySummary):
        """Send end of day notifications"""
        if self.notification_settings['email_notifications']:
            # This would implement actual email sending
            self.logger.info("End of day summary email sent")
        
        if self.notification_settings['push_notifications']:
            # This would implement actual push notifications
            self.logger.info("End of day summary push notification sent")

    async def _send_weekly_reflection_notifications(self, summary: DailySummary):
        """Send weekly reflection notifications"""
        if self.notification_settings['email_notifications']:
            # This would implement actual email sending
            self.logger.info("Weekly reflection email sent")
        
        if self.notification_settings['push_notifications']:
            # This would implement actual push notifications
            self.logger.info("Weekly reflection push notification sent")

    def get_routine_history(self, days: int = 7) -> List[DailySummary]:
        """Get routine history for the specified number of days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [r for r in self.routine_history if r.date > cutoff_date]

    def get_routine_statistics(self) -> Dict[str, Any]:
        """Get routine execution statistics"""
        if not self.routine_history:
            return {}
        
        total_routines = len(self.routine_history)
        successful_routines = len([r for r in self.routine_history if r.tasks_failed == 0])
        
        return {
            'total_routines': total_routines,
            'successful_routines': successful_routines,
            'success_rate': successful_routines / total_routines if total_routines > 0 else 0,
            'average_tasks_per_routine': sum(r.tasks_completed for r in self.routine_history) / total_routines if total_routines > 0 else 0,
            'total_time_spent': sum(r.total_time_spent for r in self.routine_history),
            'last_routine': self.routine_history[-1].date if self.routine_history else None
        }

    def export_routine_data(self, filename: str = None) -> str:
        """Export routine data to JSON file"""
        if not filename:
            filename = f"routine_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'routine_history': [
                {
                    'date': summary.date.isoformat(),
                    'routine_type': summary.routine_type.value,
                    'tasks_completed': summary.tasks_completed,
                    'tasks_failed': summary.tasks_failed,
                    'total_time_spent': summary.total_time_spent,
                    'key_insights': summary.key_insights,
                    'recommendations': summary.recommendations,
                    'next_actions': summary.next_actions
                }
                for summary in self.routine_history
            ],
            'routine_statistics': self.get_routine_statistics(),
            'daily_metrics': self.daily_metrics,
            'notification_settings': self.notification_settings,
            'export_timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename