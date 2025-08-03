"""
FreelanceX.AI Proposal Writer Agent
Specialized agent for creating compelling proposals and cover letters
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from core.base_agent import BaseAgent
from openai_agents import Agent, Session
from openai import OpenAI

logger = logging.getLogger(__name__)

class ProposalWriterAgent(BaseAgent):
    """
    Proposal Writer Agent - Creates compelling proposals and cover letters
    Analyzes job requirements and crafts personalized proposals
    Uses OpenAI Agent SDK for enhanced proposal generation
    """
    
    def __init__(self):
        super().__init__(
            agent_name="ProposalWriterAgent",
            agent_type="proposal_writer"
        )
        self.templates = self._load_templates()
        self.proposal_history = []
        
        # Initialize with agent-specific capabilities
        logger.info("🎯 ProposalWriterAgent initialized with OpenAI Agent SDK")
        
    def _get_agent_tools(self) -> List:
        """Get OpenAI Agent SDK tools for proposal writing"""
        return [
            self._get_proposal_generation_tool(),
            self._get_pricing_strategy_tool(),
            self._get_content_optimization_tool(),
            self._get_client_research_tool()
        ]
    
    def _get_proposal_generation_tool(self):
        """Tool for generating proposals"""
        def generate_proposal(job_description: str, user_profile: str) -> str:
            """Generate a compelling proposal based on job description and user profile"""
            return f"Generated proposal for: {job_description[:100]}..."
        
        return generate_proposal
    
    def _get_pricing_strategy_tool(self):
        """Tool for pricing strategy"""
        def suggest_pricing(project_scope: str, complexity: str) -> str:
            """Suggest pricing strategy based on project scope and complexity"""
            return f"Pricing strategy for {complexity} project: {project_scope[:50]}..."
        
        return suggest_pricing
    
    def _get_content_optimization_tool(self):
        """Tool for content optimization"""
        def optimize_content(content: str) -> str:
            """Optimize proposal content for better engagement"""
            return f"Optimized content: {content[:100]}..."
        
        return optimize_content
    
    def _get_client_research_tool(self):
        """Tool for client research"""
        def research_client(client_info: str) -> str:
            """Research client background and preferences"""
            return f"Client research results for: {client_info[:50]}..."
        
        return research_client
    
    def get_capabilities(self) -> List[str]:
        """Return proposal writer agent capabilities"""
        return [
            'proposal_generation',
            'content_optimization',
            'client_research',
            'pricing_strategy',
            'persuasive_writing',
            'template_customization'
        ]
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute proposal writing tasks using OpenAI Agent SDK"""
        try:
            user_id = task.get('user_id', 'default')
            content = task.get('content', '')
            
            # Use OpenAI Agent SDK session if available
            if self.openai_agent:
                session = self.get_or_create_session(user_id)
                if session:
                    response = session.run(content)
                    return {
                        'success': True,
                        'result': str(response),
                        'agent': self.agent_name,
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Fallback to custom processing
            return await self.process_task(task)
            
        except Exception as e:
            logger.error(f"❌ Proposal writer agent task execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            }
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process proposal writing related tasks (fallback method)"""
        try:
            content = task_data.get('content', '').lower()
            task_type = task_data.get('task_type', 'general')
            
            if 'proposal' in content or 'cover letter' in content or 'application' in content:
                return await self._generate_proposal(task_data)
            elif 'pricing' in content or 'rate' in content or 'cost' in content:
                return await self._suggest_pricing(task_data)
            elif 'research' in content or 'client' in content:
                return await self._research_client(task_data)
            elif 'optimize' in content or 'improve' in content:
                return await self._optimize_proposal(task_data)
            else:
                return await self._general_proposal_assistance(task_data)
                
        except Exception as e:
            logger.error(f"❌ Proposal writer agent task processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_proposal(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a proposal for a job"""
        try:
            content = task_data.get('content', '')
            
            # Extract proposal parameters
            proposal_params = self._extract_proposal_params(content)
            
            # Research client and job requirements
            client_info = await self._research_client_info(proposal_params)
            
            # Generate proposal content
            proposal = await self._create_proposal(proposal_params, client_info)
            
            # Optimize proposal
            optimized_proposal = await self._optimize_content(proposal)
            
            return {
                'success': True,
                'task_type': 'proposal_generation',
                'proposal': optimized_proposal,
                'client_info': client_info,
                'pricing_suggestions': await self._suggest_pricing_strategy(proposal_params),
                'tips': self._get_proposal_tips()
            }
            
        except Exception as e:
            logger.error(f"❌ Proposal generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _suggest_pricing(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest pricing strategy"""
        try:
            content = task_data.get('content', '')
            
            # Extract pricing parameters
            pricing_params = self._extract_pricing_params(content)
            
            # Generate pricing strategy
            pricing_strategy = await self._create_pricing_strategy(pricing_params)
            
            return {
                'success': True,
                'task_type': 'pricing_strategy',
                'pricing_strategy': pricing_strategy,
                'market_analysis': await self._analyze_market_rates(pricing_params),
                'recommendations': self._get_pricing_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Pricing suggestion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _research_client(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research client information"""
        try:
            content = task_data.get('content', '')
            
            # Extract client research parameters
            client_params = self._extract_client_params(content)
            
            # Research client
            client_info = await self._research_client_info(client_params)
            
            return {
                'success': True,
                'task_type': 'client_research',
                'client_info': client_info,
                'research_insights': self._generate_client_insights(client_info),
                'recommendations': self._get_client_research_recommendations()
            }
            
        except Exception as e:
            logger.error(f"❌ Client research failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _optimize_proposal(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize existing proposal"""
        try:
            content = task_data.get('content', '')
            
            # Extract optimization parameters
            optimization_params = self._extract_optimization_params(content)
            
            # Optimize proposal
            optimized_proposal = await self._optimize_content(optimization_params)
            
            return {
                'success': True,
                'task_type': 'proposal_optimization',
                'optimized_proposal': optimized_proposal,
                'improvements': self._identify_improvements(optimization_params),
                'optimization_tips': self._get_optimization_tips()
            }
            
        except Exception as e:
            logger.error(f"❌ Proposal optimization failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _general_proposal_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide general proposal assistance"""
        try:
            content = task_data.get('content', '')
            
            # Provide general guidance
            guidance = self._generate_proposal_guidance(content)
            
            return {
                'success': True,
                'task_type': 'proposal_assistance',
                'guidance': guidance,
                'best_practices': self._get_proposal_best_practices(),
                'common_mistakes': self._get_common_mistakes(),
                'templates': self._get_proposal_templates()
            }
            
        except Exception as e:
            logger.error(f"❌ Proposal assistance failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_templates(self) -> Dict[str, str]:
        """Load proposal templates"""
        return {
            'standard': """
Dear {client_name},

I'm excited to submit my proposal for your {project_title} project. With {years_experience} years of experience in {skills}, I'm confident I can deliver exceptional results.

**Why I'm the right fit:**
- {key_achievement_1}
- {key_achievement_2}
- {key_achievement_3}

**My approach:**
{approach_description}

**Timeline:** {timeline}
**Budget:** ${budget}

I'd love to discuss this project in detail. When would be a good time to connect?

Best regards,
{your_name}
            """,
            'detailed': """
Dear {client_name},

Thank you for posting the {project_title} opportunity. After carefully reviewing your requirements, I'm confident I can exceed your expectations.

**About Me:**
{personal_introduction}

**Relevant Experience:**
{experience_details}

**Project Understanding:**
{project_understanding}

**Proposed Solution:**
{solution_details}

**Timeline & Milestones:**
{timeline_details}

**Investment:**
{budget_breakdown}

**Next Steps:**
{next_steps}

I'm available for a call to discuss this further. Looking forward to working together!

Best regards,
{your_name}
            """
        }
    
    def _extract_proposal_params(self, content: str) -> Dict[str, Any]:
        """Extract proposal parameters from content"""
        params = {
            'project_title': 'Freelance Project',
            'client_name': 'Client',
            'skills': ['development', 'design'],
            'years_experience': 3,
            'budget': 5000,
            'timeline': '2-3 weeks',
            'template_type': 'standard'
        }
        
        # Extract project type
        if 'web' in content and 'development' in content:
            params['project_title'] = 'Web Development Project'
            params['skills'] = ['web development', 'javascript', 'react']
        elif 'mobile' in content and 'app' in content:
            params['project_title'] = 'Mobile App Development'
            params['skills'] = ['mobile development', 'react native', 'ios']
        elif 'design' in content:
            params['project_title'] = 'Design Project'
            params['skills'] = ['ui/ux design', 'figma', 'prototyping']
        
        # Extract budget information
        if 'budget' in content:
            if 'high' in content or 'expensive' in content:
                params['budget'] = 10000
            elif 'low' in content or 'cheap' in content:
                params['budget'] = 1000
        
        return params
    
    def _extract_pricing_params(self, content: str) -> Dict[str, Any]:
        """Extract pricing parameters"""
        return {
            'project_type': 'development',
            'complexity': 'medium',
            'timeline': '2-3 weeks',
            'skills_required': ['python', 'web development'],
            'market_rate': 75
        }
    
    def _extract_client_params(self, content: str) -> Dict[str, Any]:
        """Extract client research parameters"""
        return {
            'client_name': 'Unknown Client',
            'research_focus': ['reputation', 'payment_history', 'project_quality']
        }
    
    def _extract_optimization_params(self, content: str) -> Dict[str, Any]:
        """Extract optimization parameters"""
        return {
            'current_proposal': content,
            'optimization_focus': ['clarity', 'persuasion', 'structure']
        }
    
    async def _research_client_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Research client information"""
        # Simulate client research
        return {
            'name': params.get('client_name', 'Client'),
            'total_spent': 25000,
            'projects_completed': 15,
            'average_rating': 4.7,
            'payment_history': 'excellent',
            'communication_style': 'professional',
            'preferred_skills': ['python', 'react', 'ui/ux'],
            'company_size': 'startup',
            'industry': 'technology'
        }
    
    async def _create_proposal(self, params: Dict[str, Any], client_info: Dict[str, Any]) -> str:
        """Create proposal content"""
        template = self.templates.get(params.get('template_type', 'standard'), self.templates['standard'])
        
        # Fill template with parameters
        proposal = template.format(
            client_name=client_info['name'],
            project_title=params['project_title'],
            skills=', '.join(params['skills']),
            years_experience=params['years_experience'],
            budget=params['budget'],
            timeline=params['timeline'],
            your_name='Abdul Wahid Chohan',
            key_achievement_1=f"Delivered {params['years_experience']}+ successful projects",
            key_achievement_2=f"Expert in {', '.join(params['skills'])}",
            key_achievement_3="100% client satisfaction rate",
            approach_description="I follow an iterative approach with regular check-ins and transparent communication.",
            personal_introduction="I'm a passionate freelancer with expertise in modern technologies and a track record of delivering high-quality solutions.",
            experience_details=f"I have {params['years_experience']} years of experience in {', '.join(params['skills'])} with a focus on scalable, maintainable solutions.",
            project_understanding="I understand you need a robust, user-friendly solution that meets your specific requirements and timeline.",
            solution_details="I'll provide a comprehensive solution including planning, development, testing, and deployment with ongoing support.",
            timeline_details="Week 1: Planning and setup\nWeek 2: Core development\nWeek 3: Testing and refinement",
            budget_breakdown="Development: ${params['budget']}\nRevisions: Included\nSupport: 30 days included",
            next_steps="1. Initial consultation call\n2. Detailed project planning\n3. Development kickoff"
        )
        
        return proposal
    
    async def _optimize_content(self, content: str) -> str:
        """Optimize proposal content"""
        # Simple optimization - in real implementation, this would use NLP
        optimized = content.replace('I am', 'I\'m')
        optimized = optimized.replace('I will', 'I\'ll')
        optimized = optimized.replace('cannot', 'can\'t')
        
        # Add more engaging language
        optimized = optimized.replace('good', 'exceptional')
        optimized = optimized.replace('help', 'assist')
        
        return optimized
    
    async def _suggest_pricing_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest pricing strategy"""
        base_rate = 75
        complexity_multiplier = 1.2 if params.get('complexity') == 'high' else 1.0
        
        return {
            'hourly_rate': base_rate * complexity_multiplier,
            'project_rate': params.get('budget', 5000),
            'pricing_model': 'project-based',
            'justification': 'Based on project complexity and market rates',
            'negotiation_range': {
                'min': params.get('budget', 5000) * 0.9,
                'max': params.get('budget', 5000) * 1.1
            }
        }
    
    async def _analyze_market_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market rates"""
        return {
            'average_rate': 75,
            'market_position': 'competitive',
            'rate_factors': ['experience', 'skills', 'project_complexity'],
            'recommendation': 'Your rate is competitive for the market'
        }
    
    def _generate_client_insights(self, client_info: Dict[str, Any]) -> List[str]:
        """Generate client insights"""
        insights = []
        
        if client_info['payment_history'] == 'excellent':
            insights.append("Client has excellent payment history - low risk")
        
        if client_info['average_rating'] > 4.5:
            insights.append("High client rating indicates good working relationship")
        
        if client_info['total_spent'] > 20000:
            insights.append("Client has significant budget for quality work")
        
        return insights
    
    def _identify_improvements(self, params: Dict[str, Any]) -> List[str]:
        """Identify proposal improvements"""
        return [
            "Make the opening more compelling",
            "Add specific examples of past work",
            "Include a clear call-to-action",
            "Highlight unique value proposition",
            "Add social proof or testimonials"
        ]
    
    def _generate_proposal_guidance(self, content: str) -> str:
        """Generate proposal guidance"""
        if 'start' in content:
            return "Start with a compelling hook that addresses the client's specific needs. Show you understand their project."
        elif 'structure' in content:
            return "Structure your proposal with: Introduction, Understanding, Solution, Timeline, Budget, and Call-to-Action."
        elif 'pricing' in content:
            return "Justify your pricing with value, not just time. Focus on results and benefits to the client."
        else:
            return "Focus on the client's needs, provide clear value proposition, and make it easy for them to say yes."
    
    def _get_proposal_tips(self) -> List[str]:
        """Get proposal writing tips"""
        return [
            "Start with a compelling hook that grabs attention",
            "Show you understand the client's specific needs",
            "Provide concrete examples of similar work",
            "Include a clear timeline and deliverables",
            "Justify your pricing with value, not just time",
            "End with a strong call-to-action"
        ]
    
    def _get_pricing_recommendations(self) -> List[str]:
        """Get pricing recommendations"""
        return [
            "Research market rates for similar projects",
            "Consider project complexity and timeline",
            "Factor in your experience and expertise",
            "Include value-added services in your pricing",
            "Be prepared to negotiate but know your minimum"
        ]
    
    def _get_client_research_recommendations(self) -> List[str]:
        """Get client research recommendations"""
        return [
            "Check client's payment history and ratings",
            "Review their previous projects and feedback",
            "Understand their communication style",
            "Research their company and industry",
            "Look for red flags in their project descriptions"
        ]
    
    def _get_optimization_tips(self) -> List[str]:
        """Get optimization tips"""
        return [
            "Use active voice and strong action verbs",
            "Keep sentences concise and clear",
            "Add specific numbers and metrics",
            "Include social proof and testimonials",
            "Make it scannable with bullet points and headers"
        ]
    
    def _get_proposal_best_practices(self) -> List[str]:
        """Get proposal best practices"""
        return [
            "Personalize each proposal for the specific client",
            "Address the client's pain points directly",
            "Show understanding of their business context",
            "Provide clear deliverables and timeline",
            "Include relevant portfolio examples"
        ]
    
    def _get_common_mistakes(self) -> List[str]:
        """Get common proposal mistakes"""
        return [
            "Using generic templates without customization",
            "Focusing too much on yourself instead of client needs",
            "Not providing clear pricing or timeline",
            "Making promises you can't keep",
            "Using jargon the client won't understand"
        ]
    
    def _get_proposal_templates(self) -> Dict[str, str]:
        """Get proposal templates"""
        return {
            'quick_proposal': "Brief, focused proposal for simple projects",
            'detailed_proposal': "Comprehensive proposal for complex projects",
            'follow_up_proposal': "Proposal for existing clients",
            'referral_proposal': "Proposal for referred clients"
        }
