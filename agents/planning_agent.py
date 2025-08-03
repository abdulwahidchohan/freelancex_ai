"""
FreelanceX.AI Planning Agent
Specialized agent for project planning, scheduling, and task organization
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from core.agent_manager import BaseAgent

logger = logging.getLogger(__name__)

class PlanningAgent(BaseAgent):
    """
    Planning Agent - Manages project planning, scheduling, and task organization
    Creates timelines, milestones, and project roadmaps
    """
    
    def __init__(self):
        super().__init__(
            agent_id="planning_agent",
            name="PlanningAgent",
            description="Manages project planning, scheduling, and task organization"
        )
        self.project_templates = self._load_project_templates()
        
    def get_capabilities(self) -> List[str]:
        """Return planning agent capabilities"""
        return [
            'project_planning',
            'task_scheduling',
            'time_management',
            'milestone_tracking',
            'resource_allocation',
            'risk_assessment'
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process planning related tasks"""
        try:
            content = task_data.get('content', '').lower()
            task_type = task_data.get('task_type', 'general')
            
            if 'plan' in content or 'schedule' in content or 'timeline' in content:
                return await self._create_project_plan(task_data)
            elif 'task' in content or 'milestone' in content:
                return await self._manage_tasks(task_data)
            elif 'time' in content or 'deadline' in content:
                return await self._manage_time(task_data)
            elif 'risk' in content or 'assessment' in content:
                return await self._assess_risks(task_data)
            else:
                return await self._general_planning_assistance(task_data)
                
        except Exception as e:
            logger.error(f"❌ Planning agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_project_plan(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive project plan"""
        try:
            content = task_data.get('content', '')
            
            # Extract project parameters
            project_params = self._extract_project_params(content)
            
            # Create project plan
            project_plan = await self._generate_project_plan(project_params)
            
            # Create timeline
            timeline = await self._create_timeline(project_params)
            
            # Identify milestones
            milestones = await self._identify_milestones(project_params)
            
            return {
                'success': True,
                'task_type': 'project_planning',
                'project_plan': project_plan,
                'timeline': timeline,
                'milestones': milestones,
                'risk_assessment': await self._assess_project_risks(project_params),
                'recommendations': self._get_planning_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Project planning failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _manage_tasks(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage tasks and milestones"""
        try:
            content = task_data.get('content', '')
            
            # Extract task parameters
            task_params = self._extract_task_params(content)
            
            # Create task breakdown
            tasks = await self._break_down_tasks(task_params)
            
            # Prioritize tasks
            prioritized_tasks = await self._prioritize_tasks(tasks)
            
            return {
                'success': True,
                'task_type': 'task_management',
                'tasks': prioritized_tasks,
                'task_dependencies': self._identify_dependencies(tasks),
                'estimated_effort': self._estimate_effort(tasks)
            }
            
        except Exception as e:
            logger.error(f"❌ Task management failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _manage_time(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage time and deadlines"""
        try:
            content = task_data.get('content', '')
            
            # Extract time parameters
            time_params = self._extract_time_params(content)
            
            # Create time management plan
            time_plan = await self._create_time_plan(time_params)
            
            return {
                'success': True,
                'task_type': 'time_management',
                'time_plan': time_plan,
                'deadlines': self._identify_deadlines(time_params),
                'time_optimization_tips': self._get_time_optimization_tips()
            }
            
        except Exception as e:
            logger.error(f"❌ Time management failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _assess_risks(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess project risks"""
        try:
            content = task_data.get('content', '')
            
            # Extract risk parameters
            risk_params = self._extract_risk_params(content)
            
            # Assess risks
            risk_assessment = await self._perform_risk_assessment(risk_params)
            
            return {
                'success': True,
                'task_type': 'risk_assessment',
                'risk_assessment': risk_assessment,
                'mitigation_strategies': self._generate_mitigation_strategies(risk_assessment),
                'risk_monitoring_plan': self._create_risk_monitoring_plan()
            }
            
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _general_planning_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general planning assistance"""
        try:
            content = task_data.get('content', '')
            
            # Provide general guidance
            guidance = self._generate_planning_guidance(content)
            
            return {
                'success': True,
                'task_type': 'planning_assistance',
                'guidance': guidance,
                'planning_tools': self._get_planning_tools(),
                'best_practices': self._get_planning_best_practices()
            }
            
        except Exception as e:
            logger.error(f"❌ Planning assistance failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_project_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load project planning templates"""
        return {
            'web_development': {
                'phases': ['Planning', 'Design', 'Development', 'Testing', 'Deployment'],
                'duration_weeks': 8,
                'milestones': ['Requirements Finalized', 'Design Approved', 'MVP Complete', 'Testing Complete', 'Live Deployment']
            },
            'mobile_app': {
                'phases': ['Research', 'Design', 'Development', 'Testing', 'App Store Submission'],
                'duration_weeks': 12,
                'milestones': ['Requirements Document', 'UI/UX Design', 'Core Features', 'Beta Testing', 'App Store Approval']
            },
            'content_creation': {
                'phases': ['Research', 'Outline', 'Writing', 'Review', 'Publication'],
                'duration_weeks': 4,
                'milestones': ['Research Complete', 'Outline Approved', 'First Draft', 'Final Review', 'Published']
            }
        }
    
    def _extract_project_params(self, content: str) -> Dict[str, Any]:
        """Extract project parameters from content"""
        params = {
            'project_type': 'general',
            'duration_weeks': 4,
            'complexity': 'medium',
            'team_size': 1,
            'budget': 5000
        }
        
        # Determine project type
        if 'web' in content and 'development' in content:
            params['project_type'] = 'web_development'
            params['duration_weeks'] = 8
        elif 'mobile' in content and 'app' in content:
            params['project_type'] = 'mobile_app'
            params['duration_weeks'] = 12
        elif 'content' in content or 'writing' in content:
            params['project_type'] = 'content_creation'
            params['duration_weeks'] = 4
        
        # Extract complexity
        if 'complex' in content or 'advanced' in content:
            params['complexity'] = 'high'
            params['duration_weeks'] += 2
        elif 'simple' in content or 'basic' in content:
            params['complexity'] = 'low'
            params['duration_weeks'] = max(2, params['duration_weeks'] - 2)
        
        return params
    
    def _extract_task_params(self, content: str) -> Dict[str, Any]:
        """Extract task parameters"""
        return {
            'project_type': 'general',
            'total_tasks': 10,
            'priority_levels': ['high', 'medium', 'low']
        }
    
    def _extract_time_params(self, content: str) -> Dict[str, Any]:
        """Extract time parameters"""
        return {
            'total_hours': 160,
            'deadline': datetime.now() + timedelta(weeks=4),
            'work_hours_per_day': 8
        }
    
    def _extract_risk_params(self, content: str) -> Dict[str, Any]:
        """Extract risk parameters"""
        return {
            'project_type': 'general',
            'complexity': 'medium',
            'team_size': 1,
            'timeline': 'standard'
        }
    
    async def _generate_project_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive project plan"""
        template = self.project_templates.get(params['project_type'], self.project_templates['web_development'])
        
        plan = {
            'project_type': params['project_type'],
            'duration_weeks': params['duration_weeks'],
            'phases': template['phases'],
            'milestones': template['milestones'],
            'deliverables': self._generate_deliverables(params),
            'success_criteria': self._define_success_criteria(params)
        }
        
        return plan
    
    async def _create_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create project timeline"""
        start_date = datetime.now()
        duration_weeks = params['duration_weeks']
        
        timeline = {
            'start_date': start_date.isoformat(),
            'end_date': (start_date + timedelta(weeks=duration_weeks)).isoformat(),
            'phases': []
        }
        
        template = self.project_templates.get(params['project_type'], self.project_templates['web_development'])
        phases = template['phases']
        
        phase_duration = duration_weeks / len(phases)
        current_date = start_date
        
        for i, phase in enumerate(phases):
            phase_end = current_date + timedelta(weeks=phase_duration)
            timeline['phases'].append({
                'phase': phase,
                'start_date': current_date.isoformat(),
                'end_date': phase_end.isoformat(),
                'duration_weeks': phase_duration
            })
            current_date = phase_end
        
        return timeline
    
    async def _identify_milestones(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify project milestones"""
        template = self.project_templates.get(params['project_type'], self.project_templates['web_development'])
        milestones = template['milestones']
        
        milestone_list = []
        start_date = datetime.now()
        duration_weeks = params['duration_weeks']
        
        for i, milestone in enumerate(milestones):
            milestone_date = start_date + timedelta(weeks=(duration_weeks * (i + 1) / len(milestones)))
            milestone_list.append({
                'milestone': milestone,
                'target_date': milestone_date.isoformat(),
                'status': 'pending',
                'dependencies': self._get_milestone_dependencies(milestone)
            })
        
        return milestone_list
    
    async def _break_down_tasks(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down project into tasks"""
        tasks = [
            {
                'id': 'task_001',
                'name': 'Project Setup',
                'description': 'Initialize project environment and tools',
                'estimated_hours': 8,
                'priority': 'high',
                'dependencies': []
            },
            {
                'id': 'task_002',
                'name': 'Requirements Analysis',
                'description': 'Gather and document project requirements',
                'estimated_hours': 16,
                'priority': 'high',
                'dependencies': ['task_001']
            },
            {
                'id': 'task_003',
                'name': 'Design Phase',
                'description': 'Create project design and architecture',
                'estimated_hours': 24,
                'priority': 'high',
                'dependencies': ['task_002']
            },
            {
                'id': 'task_004',
                'name': 'Development',
                'description': 'Implement core functionality',
                'estimated_hours': 80,
                'priority': 'medium',
                'dependencies': ['task_003']
            },
            {
                'id': 'task_005',
                'name': 'Testing',
                'description': 'Test and validate functionality',
                'estimated_hours': 20,
                'priority': 'medium',
                'dependencies': ['task_004']
            },
            {
                'id': 'task_006',
                'name': 'Deployment',
                'description': 'Deploy to production environment',
                'estimated_hours': 8,
                'priority': 'high',
                'dependencies': ['task_005']
            }
        ]
        
        return tasks
    
    async def _prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize tasks based on dependencies and importance"""
        # Simple prioritization - in real implementation, this would be more sophisticated
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        
        for task in tasks:
            task['priority_score'] = priority_order.get(task['priority'], 1)
        
        return sorted(tasks, key=lambda x: x['priority_score'], reverse=True)
    
    async def _create_time_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create time management plan"""
        total_hours = params['total_hours']
        work_hours_per_day = params['work_hours_per_day']
        
        return {
            'total_hours': total_hours,
            'work_hours_per_day': work_hours_per_day,
            'work_days_needed': total_hours / work_hours_per_day,
            'daily_schedule': self._create_daily_schedule(work_hours_per_day),
            'time_allocation': {
                'planning': 0.1,
                'development': 0.6,
                'testing': 0.2,
                'documentation': 0.1
            }
        }
    
    async def _perform_risk_assessment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        risks = [
            {
                'risk': 'Scope Creep',
                'probability': 'medium',
                'impact': 'high',
                'mitigation': 'Regular scope reviews and change control process'
            },
            {
                'risk': 'Technical Challenges',
                'probability': 'high',
                'impact': 'medium',
                'mitigation': 'Proof of concept and technical research upfront'
            },
            {
                'risk': 'Timeline Delays',
                'probability': 'medium',
                'impact': 'high',
                'mitigation': 'Buffer time and regular progress tracking'
            },
            {
                'risk': 'Client Communication Issues',
                'probability': 'low',
                'impact': 'medium',
                'mitigation': 'Regular check-ins and clear communication channels'
            }
        ]
        
        return {
            'risks': risks,
            'overall_risk_level': 'medium',
            'risk_score': 6.5
        }
    
    def _generate_deliverables(self, params: Dict[str, Any]) -> List[str]:
        """Generate project deliverables"""
        if params['project_type'] == 'web_development':
            return [
                'Requirements Document',
                'Design Mockups',
                'Working Application',
                'User Documentation',
                'Deployment Guide'
            ]
        elif params['project_type'] == 'mobile_app':
            return [
                'App Requirements',
                'UI/UX Designs',
                'Mobile Application',
                'User Guide',
                'App Store Assets'
            ]
        else:
            return [
                'Project Documentation',
                'Final Deliverable',
                'User Guide',
                'Maintenance Plan'
            ]
    
    def _define_success_criteria(self, params: Dict[str, Any]) -> List[str]:
        """Define project success criteria"""
        return [
            'All requirements are met',
            'Project is delivered on time',
            'Project is within budget',
            'Client is satisfied with the result',
            'Code/documentation is maintainable'
        ]
    
    def _get_milestone_dependencies(self, milestone: str) -> List[str]:
        """Get dependencies for a milestone"""
        dependencies = {
            'Requirements Finalized': [],
            'Design Approved': ['Requirements Finalized'],
            'MVP Complete': ['Design Approved'],
            'Testing Complete': ['MVP Complete'],
            'Live Deployment': ['Testing Complete']
        }
        return dependencies.get(milestone, [])
    
    def _identify_dependencies(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify task dependencies"""
        dependencies = {}
        for task in tasks:
            dependencies[task['id']] = task.get('dependencies', [])
        return dependencies
    
    def _estimate_effort(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate total effort for tasks"""
        total_hours = sum(task.get('estimated_hours', 0) for task in tasks)
        return {
            'total_hours': total_hours,
            'total_days': total_hours / 8,
            'total_weeks': total_hours / 40
        }
    
    def _identify_deadlines(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify important deadlines"""
        deadline = params['deadline']
        return [
            {
                'milestone': 'Project Start',
                'date': datetime.now().isoformat(),
                'type': 'start'
            },
            {
                'milestone': 'Mid-Project Review',
                'date': (deadline - timedelta(weeks=2)).isoformat(),
                'type': 'checkpoint'
            },
            {
                'milestone': 'Project Completion',
                'date': deadline.isoformat(),
                'type': 'deadline'
            }
        ]
    
    def _create_daily_schedule(self, work_hours: int) -> Dict[str, Any]:
        """Create daily work schedule"""
        return {
            'morning': f"{work_hours * 0.4} hours - Planning and focused work",
            'afternoon': f"{work_hours * 0.4} hours - Development and implementation",
            'evening': f"{work_hours * 0.2} hours - Review and planning for next day"
        }
    
    def _generate_mitigation_strategies(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate risk mitigation strategies"""
        return [
            "Regular project status meetings",
            "Clear communication channels",
            "Documentation of all decisions",
            "Regular client check-ins",
            "Buffer time in schedule",
            "Technical proof of concepts"
        ]
    
    def _create_risk_monitoring_plan(self) -> Dict[str, Any]:
        """Create risk monitoring plan"""
        return {
            'monitoring_frequency': 'weekly',
            'key_metrics': ['progress', 'quality', 'timeline', 'budget'],
            'escalation_process': 'Immediate notification for high-impact risks',
            'review_schedule': 'Bi-weekly risk assessment meetings'
        }
    
    def _generate_planning_guidance(self, content: str) -> str:
        """Generate planning guidance"""
        if 'start' in content:
            return "Start with clear requirements and scope definition. Break down the project into manageable phases."
        elif 'timeline' in content:
            return "Create realistic timelines with buffer time for unexpected challenges. Regular check-ins help stay on track."
        elif 'risk' in content:
            return "Identify potential risks early and create mitigation strategies. Regular monitoring helps catch issues early."
        else:
            return "Good planning involves clear goals, realistic timelines, and regular progress tracking."
    
    def _get_planning_recommendations(self) -> List[str]:
        """Get planning recommendations"""
        return [
            "Start with clear project requirements",
            "Break down work into manageable tasks",
            "Set realistic timelines with buffer time",
            "Identify and plan for potential risks",
            "Regular progress tracking and updates",
            "Clear communication with stakeholders"
        ]
    
    def _get_time_optimization_tips(self) -> List[str]:
        """Get time optimization tips"""
        return [
            "Use time blocking for focused work",
            "Prioritize tasks by importance and urgency",
            "Eliminate or delegate low-value activities",
            "Take regular breaks to maintain productivity",
            "Use productivity tools and automation",
            "Review and optimize your schedule regularly"
        ]
    
    def _get_planning_tools(self) -> List[str]:
        """Get recommended planning tools"""
        return [
            "Trello - Task management and collaboration",
            "Asana - Project planning and tracking",
            "Notion - Documentation and planning",
            "Monday.com - Project management",
            "Jira - Agile project management",
            "Microsoft Project - Complex project planning"
        ]
    
    def _get_planning_best_practices(self) -> List[str]:
        """Get planning best practices"""
        return [
            "Define clear project objectives and success criteria",
            "Break down work into small, manageable tasks",
            "Set realistic deadlines with buffer time",
            "Regular progress tracking and status updates",
            "Clear communication with all stakeholders",
            "Document all decisions and changes",
            "Plan for risks and have mitigation strategies"
        ] 