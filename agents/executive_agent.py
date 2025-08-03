"""
FreelanceX.AI Executive Agent
Central coordinator that analyzes tasks and manages agent interactions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from core.agent_manager import BaseAgent
from memory.sqlite_memory import MemoryManager

logger = logging.getLogger(__name__)

class ExecutiveAgent(BaseAgent):
    """
    Executive Agent - The brain of FreelanceX.AI
    Analyzes user input, determines task types, and coordinates other agents
    """
    
    def __init__(self, agent_manager, memory_manager: MemoryManager, config):
        super().__init__(
            agent_id="executive_agent",
            name="ExecutiveAgent",
            description="Central coordinator for FreelanceX.AI system"
        )
        self.agent_manager = agent_manager
        self.memory_manager = memory_manager
        self.config = config
        self.task_patterns = self._initialize_task_patterns()
        self.context_window = []
        
    def _initialize_task_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for task type detection"""
        return {
            'job_search': {
                'keywords': ['job', 'work', 'opportunity', 'gig', 'project', 'hire', 'position', 'freelance'],
                'priority': 8,
                'capabilities': ['job_discovery', 'skill_matching', 'market_analysis']
            },
            'proposal_writing': {
                'keywords': ['proposal', 'cover letter', 'application', 'bid', 'quote', 'pitch'],
                'priority': 7,
                'capabilities': ['proposal_generation', 'content_optimization', 'client_research']
            },
            'project_planning': {
                'keywords': ['plan', 'schedule', 'timeline', 'milestone', 'deadline', 'project'],
                'priority': 6,
                'capabilities': ['project_planning', 'task_scheduling', 'time_management']
            },
            'invoicing': {
                'keywords': ['invoice', 'payment', 'bill', 'money', 'rate', 'price', 'cost'],
                'priority': 5,
                'capabilities': ['invoice_generation', 'payment_tracking', 'financial_analysis']
            },
            'client_communication': {
                'keywords': ['client', 'email', 'message', 'communication', 'follow up', 'contact'],
                'priority': 4,
                'capabilities': ['client_communication', 'relationship_management', 'feedback_processing']
            },
            'market_research': {
                'keywords': ['research', 'market', 'trend', 'industry', 'competition', 'analysis'],
                'priority': 6,
                'capabilities': ['market_analysis', 'research', 'data_collection']
            },
            'financial_analysis': {
                'keywords': ['budget', 'financial', 'profit', 'revenue', 'expense', 'tax'],
                'priority': 5,
                'capabilities': ['financial_analysis', 'budget_planning', 'tax_calculations']
            },
            'content_creation': {
                'keywords': ['write', 'content', 'article', 'blog', 'copy', 'text'],
                'priority': 6,
                'capabilities': ['content_creation', 'writing', 'editing']
            },
            'scheduling': {
                'keywords': ['schedule', 'calendar', 'appointment', 'meeting', 'time'],
                'priority': 4,
                'capabilities': ['scheduling', 'calendar_management', 'time_tracking']
            }
        }
    
    def get_capabilities(self) -> List[str]:
        """Return executive agent capabilities"""
        return [
            'task_analysis',
            'agent_coordination',
            'priority_management',
            'context_understanding',
            'decision_making',
            'workflow_orchestration'
        ]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process task - this is the main entry point for task analysis"""
        try:
            # Analyze the task
            analysis = await self.analyze_task(task_data)
            
            # Add context from memory
            context = await self._get_relevant_context(task_data)
            analysis['context'] = context
            
            # Determine if this is a multi-step task
            if self._is_multi_step_task(analysis):
                return await self._handle_multi_step_task(analysis)
            
            return {
                'success': True,
                'analysis': analysis,
                'recommendations': await self._generate_recommendations(analysis),
                'next_steps': await self._suggest_next_steps(analysis)
            }
            
        except Exception as e:
            logger.error(f"❌ Executive agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user input to determine task type, priority, and requirements
        
        Args:
            input_data: Dict containing input type and content
                - type: 'text', 'voice', 'image'
                - content: The actual input data
                - user_id: User identifier
                - context: Additional context
        """
        try:
            content = input_data.get('content', '').lower()
            user_id = input_data.get('user_id', 'default')
            
            # Detect task type using pattern matching
            task_type, confidence = self._detect_task_type(content)
            
            # Determine priority
            priority = self._determine_priority(content, task_type)
            
            # Extract required capabilities
            required_capabilities = self._extract_required_capabilities(content, task_type)
            
            # Analyze urgency
            urgency = self._analyze_urgency(content)
            
            # Get user context
            user_context = await self._get_user_context(user_id)
            
            analysis = {
                'task_type': task_type,
                'confidence': confidence,
                'priority': priority,
                'urgency': urgency,
                'required_capabilities': required_capabilities,
                'content': input_data.get('content', ''),
                'user_id': user_id,
                'user_context': user_context,
                'timestamp': datetime.now().isoformat(),
                'input_type': input_data.get('type', 'text')
            }
            
            # Store analysis in memory
            await self.memory_manager.log_interaction(
                user_id=user_id,
                input_type='task_analysis',
                content=json.dumps(analysis),
                timestamp=datetime.now().isoformat()
            )
            
            logger.info(f"🔍 Task analysis: {task_type} (confidence: {confidence:.2f}, priority: {priority})")
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Task analysis failed: {str(e)}")
            return {
                'task_type': 'general',
                'confidence': 0.0,
                'priority': 5,
                'urgency': 'normal',
                'required_capabilities': [],
                'content': input_data.get('content', ''),
                'user_id': input_data.get('user_id', 'default'),
                'error': str(e)
            }
    
    def _detect_task_type(self, content: str) -> tuple[str, float]:
        """Detect task type using keyword patterns"""
        best_match = 'general'
        best_confidence = 0.0
        
        for task_type, pattern in self.task_patterns.items():
            keywords = pattern['keywords']
            matches = sum(1 for keyword in keywords if keyword in content)
            
            if matches > 0:
                confidence = matches / len(keywords)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = task_type
        
        return best_match, best_confidence
    
    def _determine_priority(self, content: str, task_type: str) -> int:
        """Determine task priority based on content and type"""
        base_priority = self.task_patterns.get(task_type, {}).get('priority', 5)
        
        # Adjust based on urgency indicators
        urgency_words = ['urgent', 'asap', 'immediately', 'now', 'quick', 'fast']
        if any(word in content for word in urgency_words):
            base_priority += 2
        
        # Adjust based on user importance indicators
        importance_words = ['important', 'critical', 'essential', 'must', 'need']
        if any(word in content for word in importance_words):
            base_priority += 1
        
        return min(base_priority, 10)  # Cap at 10
    
    def _extract_required_capabilities(self, content: str, task_type: str) -> List[str]:
        """Extract required capabilities for the task"""
        base_capabilities = self.task_patterns.get(task_type, {}).get('capabilities', [])
        
        # Add specific capabilities based on content analysis
        additional_capabilities = []
        
        if 'research' in content or 'analysis' in content:
            additional_capabilities.append('research')
        
        if 'writing' in content or 'content' in content:
            additional_capabilities.append('content_creation')
        
        if 'money' in content or 'financial' in content:
            additional_capabilities.append('financial_analysis')
        
        return list(set(base_capabilities + additional_capabilities))
    
    def _analyze_urgency(self, content: str) -> str:
        """Analyze urgency level of the task"""
        urgent_words = ['urgent', 'asap', 'immediately', 'now', 'emergency']
        high_words = ['important', 'critical', 'priority', 'deadline']
        
        if any(word in content for word in urgent_words):
            return 'urgent'
        elif any(word in content for word in high_words):
            return 'high'
        else:
            return 'normal'
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context from memory"""
        try:
            # Get recent interactions
            recent_interactions = await self.memory_manager.get_recent_interactions(
                user_id=user_id,
                limit=10
            )
            
            # Get user preferences
            user_profile = self.config.get_user_setting('name', 'Unknown')
            
            return {
                'recent_interactions': recent_interactions,
                'user_profile': user_profile,
                'preferences': self.config.get_user_setting('preferences', {})
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user context: {str(e)}")
            return {}
    
    async def _get_relevant_context(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get relevant context for the task"""
        try:
            content = task_data.get('content', '')
            user_id = task_data.get('user_id', 'default')
            
            # Get related past tasks
            related_tasks = await self.memory_manager.search_interactions(
                user_id=user_id,
                query=content,
                limit=5
            )
            
            # Get current system status
            system_status = await self.agent_manager.health_check()
            
            return {
                'related_tasks': related_tasks,
                'system_status': system_status,
                'current_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get relevant context: {str(e)}")
            return {}
    
    def _is_multi_step_task(self, analysis: Dict[str, Any]) -> bool:
        """Determine if this is a multi-step task requiring coordination"""
        task_type = analysis.get('task_type', '')
        content = analysis.get('content', '')
        
        # Check for multi-step indicators
        multi_step_indicators = [
            'and then', 'after that', 'next', 'also', 'additionally',
            'first', 'second', 'finally', 'step', 'phase'
        ]
        
        has_multi_step_indicators = any(indicator in content.lower() for indicator in multi_step_indicators)
        
        # Certain task types are inherently multi-step
        multi_step_types = ['project_planning', 'market_research', 'financial_analysis']
        
        return has_multi_step_indicators or task_type in multi_step_types
    
    async def _handle_multi_step_task(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle multi-step tasks by breaking them down"""
        try:
            steps = await self._break_down_task(analysis)
            
            return {
                'success': True,
                'analysis': analysis,
                'task_type': 'multi_step',
                'steps': steps,
                'estimated_duration': self._estimate_duration(steps),
                'coordination_required': True
            }
            
        except Exception as e:
            logger.error(f"❌ Multi-step task handling failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _break_down_task(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Break down a complex task into steps"""
        content = analysis.get('content', '')
        task_type = analysis.get('task_type', '')
        
        # Simple step extraction based on common patterns
        steps = []
        
        if 'first' in content.lower() or 'step 1' in content.lower():
            steps.append({
                'step': 1,
                'description': 'Initial analysis and planning',
                'agent_type': 'planning_agent',
                'estimated_time': 5
            })
        
        if 'research' in content.lower() or 'find' in content.lower():
            steps.append({
                'step': len(steps) + 1,
                'description': 'Research and data collection',
                'agent_type': 'job_search_agent',
                'estimated_time': 10
            })
        
        if 'write' in content.lower() or 'create' in content.lower():
            steps.append({
                'step': len(steps) + 1,
                'description': 'Content creation and writing',
                'agent_type': 'proposal_writer_agent',
                'estimated_time': 15
            })
        
        if 'review' in content.lower() or 'check' in content.lower():
            steps.append({
                'step': len(steps) + 1,
                'description': 'Review and quality check',
                'agent_type': 'executive_agent',
                'estimated_time': 3
            })
        
        # Default steps if none detected
        if not steps:
            steps = [
                {
                    'step': 1,
                    'description': 'Task analysis and planning',
                    'agent_type': 'executive_agent',
                    'estimated_time': 5
                },
                {
                    'step': 2,
                    'description': 'Task execution',
                    'agent_type': task_type.replace('_', '_agent'),
                    'estimated_time': 10
                }
            ]
        
        return steps
    
    def _estimate_duration(self, steps: List[Dict[str, Any]]) -> int:
        """Estimate total duration for multi-step task"""
        return sum(step.get('estimated_time', 5) for step in steps)
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on task analysis"""
        recommendations = []
        task_type = analysis.get('task_type', '')
        
        if task_type == 'job_search':
            recommendations.extend([
                "Consider setting up job alerts for similar opportunities",
                "Review and update your skills profile",
                "Prepare a portfolio of recent work"
            ])
        
        elif task_type == 'proposal_writing':
            recommendations.extend([
                "Research the client's previous projects",
                "Customize the proposal to their specific needs",
                "Include relevant case studies and testimonials"
            ])
        
        elif task_type == 'financial_analysis':
            recommendations.extend([
                "Track all income and expenses regularly",
                "Set aside funds for taxes",
                "Consider diversifying income sources"
            ])
        
        return recommendations
    
    async def _suggest_next_steps(self, analysis: Dict[str, Any]) -> List[str]:
        """Suggest next steps for the user"""
        next_steps = []
        task_type = analysis.get('task_type', '')
        
        if task_type == 'job_search':
            next_steps.extend([
                "Review job opportunities and apply to relevant ones",
                "Follow up on applications after 3-5 days",
                "Network with potential clients on LinkedIn"
            ])
        
        elif task_type == 'proposal_writing':
            next_steps.extend([
                "Submit the proposal within 24 hours",
                "Follow up with the client after 2-3 days",
                "Prepare for potential interview questions"
            ])
        
        return next_steps 