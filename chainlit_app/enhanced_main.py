#!/usr/bin/env python3
"""
FreelanceX.AI Enhanced Chainlit UI
Integrates with all architectural components for a comprehensive user experience
"""

import chainlit as cl
import sys
import os
import asyncio
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import FreelanceX.AI components
from core.api_gateway import APIGateway
from core.memory_layer import MemoryLayer, UserProfile
from core.external_integrations import ExternalIntegrations
from core.monitoring_dashboard import MonitoringDashboard
from core.data_privacy import DataPrivacyGovernance, PrivacyLevel, DataCategory
from core.executive_agent import ExecutiveAgent
from core.agent_manager import AgentManager

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FreelanceXEnhancedUI:
    """
    Enhanced FreelanceX.AI UI with full architectural integration
    """
    
    def __init__(self):
        # Initialize all core components
        self.api_gateway = APIGateway()
        self.memory_layer = MemoryLayer()
        self.external_integrations = ExternalIntegrations()
        self.monitoring_dashboard = MonitoringDashboard()
        self.data_privacy = DataPrivacyGovernance()
        self.executive_agent = ExecutiveAgent()
        self.agent_manager = AgentManager()
        
        # User session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize components
        asyncio.create_task(self._initialize_components())
        
        logger.info("FreelanceX.AI Enhanced UI initialized")
    
    async def _initialize_components(self):
        """Initialize all system components"""
        try:
            # Initialize external integrations
            await self.external_integrations.initialize()
            
            # Start monitoring dashboard
            await self.monitoring_dashboard._initialize_database()
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Component initialization failed: {str(e)}")
    
    async def create_user_session(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Create a new user session with privacy settings"""
        try:
            # Create or get user profile
            user_profile = await self.memory_layer.get_user_profile(user_id)
            if not user_profile:
                # Create default profile
                user_profile = UserProfile(
                    user_id=user_id,
                    name="User",
                    email="",
                    skills=[],
                    experience_years=0,
                    preferred_hourly_rate=0.0,
                    location="",
                    timezone="UTC",
                    work_schedule={},
                    goals=[],
                    preferences={},
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                await self.memory_layer.store_user_profile(user_profile)
            
            # Get or create privacy settings
            privacy_settings = await self.data_privacy.get_user_privacy_settings(user_id)
            if not privacy_settings:
                await self.data_privacy.update_user_privacy_settings(user_id, {
                    'data_retention_days': 365,
                    'allow_analytics': True,
                    'allow_research': True,
                    'allow_marketing': False,
                    'data_export_enabled': True,
                    'auto_delete_enabled': True,
                    'encryption_level': PrivacyLevel.CONFIDENTIAL.value
                })
            
            # Create session
            session = {
                'user_id': user_id,
                'session_id': session_id,
                'created_at': datetime.now(),
                'last_activity': datetime.now(),
                'interaction_count': 0,
                'current_agent': None,
                'context': {}
            }
            
            self.active_sessions[session_id] = session
            
            # Log session creation
            await self.data_privacy.log_audit_event(
                user_id, "session_created", "user_session", session_id,
                success=True
            )
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create user session: {str(e)}")
            raise
    
    async def process_user_message(self, message: str, user_id: str, session_id: str) -> str:
        """Process user message through the complete system"""
        try:
            # Update session activity
            if session_id in self.active_sessions:
                self.active_sessions[session_id]['last_activity'] = datetime.now()
                self.active_sessions[session_id]['interaction_count'] += 1
            
            # Create API request
            request = {
                'type': 'agent_coordination',
                'user_id': user_id,
                'session_id': session_id,
                'data': {
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'session_context': self.active_sessions.get(session_id, {}).get('context', {})
                }
            }
            
            # Process through API Gateway
            api_response = await self.api_gateway.process_request(request)
            
            if api_response.get('status') == 'error':
                return f"I apologize, but I encountered an error: {api_response.get('message', 'Unknown error')}"
            
            # Get user profile for context
            user_profile = await self.memory_layer.get_user_profile(user_id)
            
            # Route to appropriate agent based on message content
            agent_response = await self._route_to_agent(message, user_profile, user_id, session_id)
            
            # Store interaction
            await self._store_interaction(user_id, session_id, message, agent_response)
            
            # Update monitoring
            await self._update_monitoring(user_id, session_id, message, agent_response)
            
            return agent_response
            
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    async def _route_to_agent(self, message: str, user_profile: Optional[UserProfile], 
                            user_id: str, session_id: str) -> str:
        """Route message to appropriate agent"""
        message_lower = message.lower()
        
        # Job search requests
        if any(keyword in message_lower for keyword in ['job', 'work', 'freelance', 'upwork', 'fiverr']):
            return await self._handle_job_search(message, user_profile, user_id, session_id)
        
        # Research requests
        elif any(keyword in message_lower for keyword in ['research', 'trend', 'market', 'industry']):
            return await self._handle_research(message, user_profile, user_id, session_id)
        
        # Math/calculation requests
        elif any(keyword in message_lower for keyword in ['calculate', 'math', 'budget', 'rate', 'price']):
            return await self._handle_calculation(message, user_profile, user_id, session_id)
        
        # Profile management
        elif any(keyword in message_lower for keyword in ['profile', 'settings', 'preferences']):
            return await self._handle_profile_management(message, user_profile, user_id, session_id)
        
        # System status
        elif any(keyword in message_lower for keyword in ['status', 'health', 'performance']):
            return await self._handle_system_status(message, user_id, session_id)
        
        # Privacy/GDPR requests
        elif any(keyword in message_lower for keyword in ['privacy', 'gdpr', 'data', 'export', 'delete']):
            return await self._handle_privacy_request(message, user_id, session_id)
        
        # Default to executive agent
        else:
            return await self.executive_agent.handle_message(message)
    
    async def _handle_job_search(self, message: str, user_profile: Optional[UserProfile], 
                               user_id: str, session_id: str) -> str:
        """Handle job search requests"""
        try:
            # Extract search parameters from message
            search_params = self._extract_job_search_params(message, user_profile)
            
            # Search across platforms
            all_jobs = []
            platforms = ['upwork', 'fiverr', 'freelancer']
            
            for platform in platforms:
                jobs = await self.external_integrations.search_jobs(
                    platform, search_params.get('query', ''), search_params
                )
                all_jobs.extend(jobs[:5])  # Limit to 5 jobs per platform
            
            # Sort by relevance
            all_jobs.sort(key=lambda x: x.budget or 0, reverse=True)
            
            # Format response
            if all_jobs:
                response = "Here are some relevant job opportunities:\n\n"
                for i, job in enumerate(all_jobs[:10], 1):
                    response += f"{i}. **{job.title}**\n"
                    response += f"   Platform: {job.platform.title()}\n"
                    response += f"   Budget: ${job.budget or 'Not specified'}\n"
                    response += f"   Skills: {', '.join(job.skills_required[:3])}\n"
                    response += f"   Location: {job.location}\n"
                    response += f"   [View Job]({job.url})\n\n"
                
                # Store job search results
                await self.memory_layer.store_job_history({
                    'job_id': f"search_{int(datetime.now().timestamp())}",
                    'user_id': user_id,
                    'job_title': f"Job Search: {search_params.get('query', 'General')}",
                    'platform': 'multiple',
                    'budget': None,
                    'status': 'searched',
                    'applied_at': datetime.now().isoformat(),
                    'result': f"Found {len(all_jobs)} jobs",
                    'notes': json.dumps(search_params)
                })
                
                return response
            else:
                return "I couldn't find any relevant job opportunities at the moment. Try adjusting your search criteria or check back later."
                
        except Exception as e:
            logger.error(f"Job search failed: {str(e)}")
            return "I encountered an error while searching for jobs. Please try again."
    
    async def _handle_research(self, message: str, user_profile: Optional[UserProfile], 
                             user_id: str, session_id: str) -> str:
        """Handle research requests"""
        try:
            # Extract research topic
            research_topic = self._extract_research_topic(message)
            
            # Search for research content
            research_results = await self.external_integrations.search_research(research_topic)
            
            if research_results:
                response = f"Here's what I found about **{research_topic}**:\n\n"
                
                for i, result in enumerate(research_results[:5], 1):
                    response += f"{i}. **{result.title}**\n"
                    response += f"   Source: {result.source}\n"
                    response += f"   Relevance: {result.relevance_score:.2f}\n"
                    response += f"   {result.content[:200]}...\n"
                    response += f"   [Read More]({result.url})\n\n"
                
                # Store research data
                await self.memory_layer.store_research_data({
                    'research_id': f"research_{int(datetime.now().timestamp())}",
                    'user_id': user_id,
                    'topic': research_topic,
                    'sources': [r.source for r in research_results],
                    'findings': {'summary': response[:500]},
                    'created_at': datetime.now().isoformat(),
                    'last_updated': datetime.now().isoformat(),
                    'relevance_score': sum(r.relevance_score for r in research_results) / len(research_results)
                })
                
                return response
            else:
                return f"I couldn't find any recent research about '{research_topic}'. Try a different search term or check back later."
                
        except Exception as e:
            logger.error(f"Research failed: {str(e)}")
            return "I encountered an error while researching. Please try again."
    
    async def _handle_calculation(self, message: str, user_profile: Optional[UserProfile], 
                                user_id: str, session_id: str) -> str:
        """Handle calculation requests"""
        try:
            # Use the existing math agent
            from agents.math_agent import MathAgent
            math_agent = MathAgent()
            
            # Process the calculation
            result = await math_agent.process_message(message)
            
            return result
            
        except Exception as e:
            logger.error(f"Calculation failed: {str(e)}")
            return "I encountered an error while performing the calculation. Please try again."
    
    async def _handle_profile_management(self, message: str, user_profile: Optional[UserProfile], 
                                       user_id: str, session_id: str) -> str:
        """Handle profile management requests"""
        try:
            if 'update' in message.lower() or 'change' in message.lower():
                # Extract profile updates from message
                updates = self._extract_profile_updates(message)
                
                if user_profile:
                    # Update profile
                    for key, value in updates.items():
                        if hasattr(user_profile, key):
                            setattr(user_profile, key, value)
                    
                    user_profile.last_updated = datetime.now()
                    await self.memory_layer.store_user_profile(user_profile)
                    
                    return f"Profile updated successfully! Changes: {', '.join(updates.keys())}"
                else:
                    return "I couldn't find your profile. Please try again."
            else:
                # Show current profile
                if user_profile:
                    response = "**Your Current Profile:**\n\n"
                    response += f"Name: {user_profile.name}\n"
                    response += f"Skills: {', '.join(user_profile.skills)}\n"
                    response += f"Experience: {user_profile.experience_years} years\n"
                    response += f"Preferred Rate: ${user_profile.preferred_hourly_rate}/hour\n"
                    response += f"Location: {user_profile.location}\n"
                    response += f"Goals: {', '.join(user_profile.goals)}\n"
                    
                    return response
                else:
                    return "You don't have a profile yet. Say 'update profile' to create one."
                    
        except Exception as e:
            logger.error(f"Profile management failed: {str(e)}")
            return "I encountered an error while managing your profile. Please try again."
    
    async def _handle_system_status(self, message: str, user_id: str, session_id: str) -> str:
        """Handle system status requests"""
        try:
            # Get system status
            system_status = await self.monitoring_dashboard.get_system_status()
            
            response = "**FreelanceX.AI System Status:**\n\n"
            response += f"Overall Status: {system_status['status'].title()}\n"
            response += f"Last Updated: {system_status['timestamp']}\n\n"
            
            # Health metrics
            health = system_status['metrics'].get('health_summary', {})
            response += "**System Health:**\n"
            response += f"CPU Usage: {health.get('cpu_usage', 0):.1f}%\n"
            response += f"Memory Usage: {health.get('memory_usage', 0):.1f}%\n"
            response += f"Disk Usage: {health.get('disk_usage', 0):.1f}%\n"
            response += f"Network: {'Online' if health.get('network_status', False) else 'Offline'}\n\n"
            
            # Agent status
            agents = system_status['metrics'].get('agent_summary', [])
            response += "**Agent Status:**\n"
            for agent in agents[:5]:  # Show first 5 agents
                status_emoji = "🟢" if agent['status'] == 'active' else "🔴"
                response += f"{status_emoji} {agent['agent_name']}: {agent['status']}\n"
            
            return response
            
        except Exception as e:
            logger.error(f"System status failed: {str(e)}")
            return "I encountered an error while checking system status. Please try again."
    
    async def _handle_privacy_request(self, message: str, user_id: str, session_id: str) -> str:
        """Handle privacy and GDPR requests"""
        try:
            message_lower = message.lower()
            
            if 'export' in message_lower or 'download' in message_lower:
                # Create GDPR export request
                request_id = await self.data_privacy.create_gdpr_request(user_id, 'export')
                
                # Export user data
                export_data = await self.data_privacy.export_user_data(user_id)
                
                return f"Your data export request has been created (ID: {request_id}). Here's a summary of your data:\n\n" + \
                       f"- Profile Settings: {'Yes' if export_data.get('privacy_settings') else 'No'}\n" + \
                       f"- Encrypted Data Records: {len(export_data.get('encrypted_data', []))}\n" + \
                       f"- Audit Logs: {len(export_data.get('audit_logs', []))}\n" + \
                       f"- Data Access Logs: {len(export_data.get('data_access_logs', []))}\n\n" + \
                       "Your complete data export will be processed and made available for download."
            
            elif 'delete' in message_lower or 'remove' in message_lower:
                # Create GDPR deletion request
                request_id = await self.data_privacy.create_gdpr_request(user_id, 'deletion')
                
                return f"Your data deletion request has been created (ID: {request_id}). " + \
                       "This will permanently delete all your data from the system. " + \
                       "This action cannot be undone."
            
            elif 'privacy' in message_lower or 'settings' in message_lower:
                # Show privacy settings
                privacy_settings = await self.data_privacy.get_user_privacy_settings(user_id)
                
                if privacy_settings:
                    response = "**Your Privacy Settings:**\n\n"
                    response += f"Data Retention: {privacy_settings.data_retention_days} days\n"
                    response += f"Allow Analytics: {'Yes' if privacy_settings.allow_analytics else 'No'}\n"
                    response += f"Allow Research: {'Yes' if privacy_settings.allow_research else 'No'}\n"
                    response += f"Allow Marketing: {'Yes' if privacy_settings.allow_marketing else 'No'}\n"
                    response += f"Data Export Enabled: {'Yes' if privacy_settings.data_export_enabled else 'No'}\n"
                    response += f"Auto Delete Enabled: {'Yes' if privacy_settings.auto_delete_enabled else 'No'}\n"
                    response += f"Encryption Level: {privacy_settings.encryption_level.value}\n"
                    
                    return response
                else:
                    return "You don't have privacy settings configured yet. Default settings are being used."
            
            else:
                return "I can help you with privacy-related requests. You can:\n" + \
                       "- Export your data\n" + \
                       "- Delete your data\n" + \
                       "- View privacy settings\n" + \
                       "Just let me know what you'd like to do!"
                
        except Exception as e:
            logger.error(f"Privacy request failed: {str(e)}")
            return "I encountered an error while processing your privacy request. Please try again."
    
    def _extract_job_search_params(self, message: str, user_profile: Optional[UserProfile]) -> Dict[str, Any]:
        """Extract job search parameters from message"""
        params = {'query': message}
        
        if user_profile:
            params['skills'] = user_profile.skills
            params['budget_min'] = user_profile.preferred_hourly_rate * 0.8
            params['budget_max'] = user_profile.preferred_hourly_rate * 1.2
        
        return params
    
    def _extract_research_topic(self, message: str) -> str:
        """Extract research topic from message"""
        # Simple extraction - in production, use NLP
        keywords = ['research', 'about', 'trends', 'market', 'industry']
        words = message.lower().split()
        
        for i, word in enumerate(words):
            if word in keywords and i + 1 < len(words):
                return ' '.join(words[i+1:])
        
        return message
    
    def _extract_profile_updates(self, message: str) -> Dict[str, Any]:
        """Extract profile updates from message"""
        updates = {}
        
        # Simple extraction - in production, use NLP
        if 'rate' in message.lower() or 'hourly' in message.lower():
            # Extract rate
            import re
            rate_match = re.search(r'\$?(\d+(?:\.\d+)?)', message)
            if rate_match:
                updates['preferred_hourly_rate'] = float(rate_match.group(1))
        
        if 'experience' in message.lower() or 'years' in message.lower():
            # Extract years of experience
            import re
            exp_match = re.search(r'(\d+)\s*years?', message)
            if exp_match:
                updates['experience_years'] = int(exp_match.group(1))
        
        return updates
    
    async def _store_interaction(self, user_id: str, session_id: str, input_message: str, output_message: str):
        """Store user interaction"""
        try:
            from core.memory_layer import InteractionRecord
            
            interaction = InteractionRecord(
                interaction_id=f"interaction_{int(datetime.now().timestamp())}",
                user_id=user_id,
                agent_name=self.active_sessions.get(session_id, {}).get('current_agent', 'executive'),
                interaction_type='chat',
                input_data={'message': input_message},
                output_data={'response': output_message},
                timestamp=datetime.now(),
                duration=0.0,  # Would calculate actual duration
                success=True
            )
            
            await self.memory_layer.store_interaction(interaction)
            
        except Exception as e:
            logger.error(f"Failed to store interaction: {str(e)}")
    
    async def _update_monitoring(self, user_id: str, session_id: str, input_message: str, output_message: str):
        """Update monitoring metrics"""
        try:
            # Record user interaction
            await self.monitoring_dashboard.record_user_interaction(
                user_id, session_id, {
                    'interaction_count': self.active_sessions.get(session_id, {}).get('interaction_count', 0),
                    'total_duration': 0.0,  # Would calculate actual duration
                    'average_session_length': 0.0,
                    'most_used_agent': 'executive',
                    'last_activity': datetime.now().isoformat(),
                    'satisfaction_score': None
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to update monitoring: {str(e)}")

# Initialize the enhanced UI
enhanced_ui = FreelanceXEnhancedUI()

@cl.on_chat_start
async def start_chat():
    """Initialize chat session with enhanced features"""
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        user_id = "user_" + str(uuid.uuid4())[:8]  # In production, get from auth
        
        # Create user session
        await enhanced_ui.create_user_session(user_id, session_id)
        
        # Store session info
        cl.user_session.set("user_id", user_id)
        cl.user_session.set("session_id", session_id)
        
        # Send welcome message
        welcome_message = """
        # 🚀 Welcome to FreelanceX.AI!
        
        I'm your comprehensive AI assistant for freelancing success. Here's what I can help you with:
        
        **🎯 Job Search & Opportunities**
        - Find relevant freelance jobs across platforms
        - Match your skills to job requirements
        - Track application history
        
        **📊 Market Research & Trends**
        - Industry research and analysis
        - Competitive intelligence
        - Market rate insights
        
        **💰 Financial Planning**
        - Rate calculations and pricing
        - Budget planning and projections
        - Tax and invoice management
        
        **⚙️ System Features**
        - Profile management
        - Privacy controls
        - System status monitoring
        
        **🔒 Privacy & Security**
        - GDPR compliance
        - Data export/deletion
        - Encrypted data storage
        
        How can I assist you today?
        """
        
        await cl.Message(content=welcome_message).send()
        
    except Exception as e:
        logger.error(f"Error in chat initialization: {str(e)}")
        await cl.Message(content="Sorry, there was an error starting the chat. Please try again.").send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages with enhanced processing"""
    try:
        # Get session info
        user_id = cl.user_session.get("user_id")
        session_id = cl.user_session.get("session_id")
        
        if not user_id or not session_id:
            await cl.Message(content="Session error. Please refresh and try again.").send()
            return
        
        # Show typing indicator
        async with cl.Step("Processing your request...") as step:
            # Process message through enhanced system
            response = await enhanced_ui.process_user_message(
                message.content, user_id, session_id
            )
            
            # Send response
            if response:
                await cl.Message(content=response).send()
            else:
                step.error("Empty response received")
                await cl.Message(content="I apologize, but I couldn't generate a response. Please try again.").send()
                
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await cl.Message(content="I apologize, but I encountered an error processing your request. Please try again.").send()

@cl.on_chat_end
async def end_chat():
    """Handle chat session end"""
    try:
        session_id = cl.user_session.get("session_id")
        if session_id and session_id in enhanced_ui.active_sessions:
            # Log session end
            user_id = enhanced_ui.active_sessions[session_id]['user_id']
            await enhanced_ui.data_privacy.log_audit_event(
                user_id, "session_ended", "user_session", session_id,
                success=True
            )
            
            # Clean up session
            del enhanced_ui.active_sessions[session_id]
            
    except Exception as e:
        logger.error(f"Error ending chat: {str(e)}")