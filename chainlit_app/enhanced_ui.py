#!/usr/bin/env python3
"""
FreelanceX.AI - Enhanced Chainlit UI
Modern, user-friendly interface that integrates with the multi-agent architecture.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import chainlit as cl
from chainlit import user_session, on_chat_start, on_message
import aiohttp
from dataclasses import asdict

# Import FreelanceX.AI components
from backend.memory_layer import MemoryLayer, UserProfile
from core.agent_coordinator import AgentCoordinator, Task, TaskPriority, TaskStatus
from backend.monitoring_system import FreelanceXMonitoringSystem
from backend.api_gateway import FreelanceXAPIGateway, RequestType

class FreelanceXUI:
    """Enhanced Chainlit UI for FreelanceX.AI"""
    
    def __init__(self):
        self.logger = logging.getLogger("FreelanceX.UI")
        
        # Initialize components
        self.memory_layer = MemoryLayer()
        self.agent_coordinator = None  # Will be initialized when agent manager is available
        self.monitoring_system = None  # Will be initialized when agent manager is available
        self.api_gateway = None  # Will be initialized when agent manager is available
        
        # UI state
        self.user_profiles: Dict[str, UserProfile] = {}
        self.active_tasks: Dict[str, Task] = {}
        self.chat_history: List[Dict[str, Any]] = []
        
        # UI configuration
        self.ui_config = {
            "theme": "modern",
            "show_dashboard": True,
            "show_agent_status": True,
            "show_task_progress": True,
            "enable_voice": False,
            "enable_images": True
        }
    
    async def initialize_components(self, agent_manager):
        """Initialize UI components with agent manager"""
        try:
            self.agent_coordinator = AgentCoordinator(agent_manager, self.memory_layer)
            self.monitoring_system = FreelanceXMonitoringSystem(agent_manager, self.memory_layer)
            self.api_gateway = FreelanceXAPIGateway(agent_manager)
            
            # Start monitoring system
            await self.monitoring_system.start()
            
            self.logger.info("FreelanceX.AI UI components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing UI components: {str(e)}")
    
    async def setup_user_session(self, user_id: str):
        """Setup user session and load profile"""
        try:
            # Load or create user profile
            profile = await self.memory_layer.get_user_profile(user_id)
            
            if not profile:
                # Create default profile
                profile = UserProfile(
                    user_id=user_id,
                    name="Freelancer",
                    email=f"{user_id}@freelancex.ai",
                    skills=[],
                    experience_years=0,
                    preferred_hourly_rate=50.0,
                    location="Unknown",
                    timezone="UTC",
                    work_schedule={},
                    goals=[],
                    preferences={},
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                await self.memory_layer.store_user_profile(profile)
            
            self.user_profiles[user_id] = profile
            
            # Store in user session
            user_session.set("user_profile", asdict(profile))
            user_session.set("user_id", user_id)
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error setting up user session: {str(e)}")
            return None
    
    async def create_welcome_message(self, user_profile: UserProfile):
        """Create personalized welcome message"""
        try:
            # Create welcome card
            welcome_card = cl.Card(
                title="🎉 Welcome to FreelanceX.AI!",
                content=f"""
                **Hello {user_profile.name}!** 👋
                
                I'm your AI-powered freelance assistant, designed to help you:
                
                🔍 **Find Opportunities**: Discover relevant job postings and projects
                📊 **Market Research**: Get insights on industry trends and rates
                💰 **Financial Planning**: Calculate rates, budgets, and projections
                📝 **Proposal Writing**: Create compelling proposals and pitches
                🎯 **Goal Tracking**: Monitor your progress and achievements
                
                **Quick Start:**
                - Ask me to find jobs in your field
                - Request market research for your skills
                - Get help with pricing calculations
                - Create professional proposals
                
                What would you like to work on today?
                """,
                size="large"
            )
            
            await cl.Message(
                content="",
                elements=[welcome_card]
            ).send()
            
            # Show user profile if incomplete
            if user_profile.profile_completeness < 0.7:
                await self.show_profile_completion_prompt(user_profile)
            
        except Exception as e:
            self.logger.error(f"Error creating welcome message: {str(e)}")
    
    async def show_profile_completion_prompt(self, user_profile: UserProfile):
        """Show profile completion prompt"""
        try:
            profile_card = cl.Card(
                title="📋 Complete Your Profile",
                content=f"""
                Your profile is {user_profile.profile_completeness:.1%} complete.
                
                To provide you with the best assistance, please share:
                
                **Skills & Expertise**: What are your main skills?
                **Experience**: How many years of experience do you have?
                **Rate**: What's your preferred hourly rate?
                **Location**: Where are you based?
                **Goals**: What are your freelance goals?
                
                You can update your profile anytime by saying "Update my profile"
                """,
                size="medium"
            )
            
            await cl.Message(
                content="",
                elements=[profile_card]
            ).send()
            
        except Exception as e:
            self.logger.error(f"Error showing profile completion prompt: {str(e)}")
    
    async def create_dashboard(self, user_profile: UserProfile):
        """Create user dashboard"""
        try:
            # Get user statistics
            job_history = await self.memory_layer.get_user_job_history(user_profile.user_id)
            interactions = await self.memory_layer.get_user_interactions(user_profile.user_id, limit=10)
            
            # Calculate statistics
            total_jobs = len(job_history)
            active_jobs = len([job for job in job_history if job.status in ["applied", "interviewed"]])
            completed_jobs = len([job for job in job_history if job.status == "completed"])
            
            # Create dashboard elements
            stats_card = cl.Card(
                title="📊 Your Statistics",
                content=f"""
                **Jobs Applied**: {total_jobs}
                **Active Applications**: {active_jobs}
                **Completed Projects**: {completed_jobs}
                **Success Rate**: {(completed_jobs/total_jobs*100):.1f}% if total_jobs > 0 else 0}%
                **Profile Completeness**: {user_profile.profile_completeness:.1f}%
                """,
                size="medium"
            )
            
            # Recent activity
            recent_activity = []
            for interaction in interactions[:5]:
                recent_activity.append(f"• {interaction.agent_name}: {interaction.request_type}")
            
            activity_card = cl.Card(
                title="🕒 Recent Activity",
                content="\n".join(recent_activity) if recent_activity else "No recent activity",
                size="medium"
            )
            
            # Quick actions
            actions_card = cl.Card(
                title="⚡ Quick Actions",
                content="""
                **Find Jobs**: "Find me Python development jobs"
                **Market Research**: "Research rates for web developers"
                **Calculate Rate**: "Help me calculate my hourly rate"
                **Write Proposal**: "Help me write a proposal for a project"
                **Update Profile**: "Update my profile information"
                """,
                size="medium"
            )
            
            await cl.Message(
                content="",
                elements=[stats_card, activity_card, actions_card]
            ).send()
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {str(e)}")
    
    async def process_user_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """Process user message and route to appropriate agents"""
        try:
            # Determine request type based on message content
            request_type = await self._classify_request(message)
            
            # Create task
            task = Task(
                task_id=f"task_{int(datetime.now().timestamp())}",
                user_id=user_id,
                task_type=request_type,
                description=message,
                priority=TaskPriority.NORMAL,
                required_agents=[],
                parameters={"message": message, "user_id": user_id}
            )
            
            # Submit task to coordinator
            if self.agent_coordinator:
                task_id = await self.agent_coordinator.submit_task(task)
                self.active_tasks[task_id] = task
                
                return {
                    "task_id": task_id,
                    "request_type": request_type,
                    "status": "submitted"
                }
            else:
                # Fallback to direct API gateway
                if self.api_gateway:
                    result = await self.api_gateway.router.route_request(
                        RequestType(request_type),
                        {"message": message, "user_id": user_id}
                    )
                    return result
                else:
                    return {"error": "System not fully initialized"}
            
        except Exception as e:
            self.logger.error(f"Error processing user message: {str(e)}")
            return {"error": str(e)}
    
    async def _classify_request(self, message: str) -> str:
        """Classify user request to determine appropriate agents"""
        message_lower = message.lower()
        
        # Job search patterns
        if any(keyword in message_lower for keyword in ["job", "work", "project", "opportunity", "position"]):
            return "job_search"
        
        # Research patterns
        if any(keyword in message_lower for keyword in ["research", "trend", "market", "rate", "industry"]):
            return "web_research"
        
        # Math/calculation patterns
        if any(keyword in message_lower for keyword in ["calculate", "math", "rate", "budget", "price", "cost"]):
            return "math_calculation"
        
        # Proposal patterns
        if any(keyword in message_lower for keyword in ["proposal", "pitch", "write", "draft"]):
            return "proposal_writing"
        
        # Profile patterns
        if any(keyword in message_lower for keyword in ["profile", "update", "skill", "experience"]):
            return "user_profile_analysis"
        
        # Wellness patterns
        if any(keyword in message_lower for keyword in ["wellness", "health", "balance", "stress"]):
            return "wellness_check"
        
        # Default to comprehensive research for complex queries
        return "comprehensive_research"
    
    async def show_task_progress(self, task_id: str):
        """Show task progress to user"""
        try:
            if not self.agent_coordinator:
                return
            
            task = await self.agent_coordinator.get_task_status(task_id)
            if not task:
                return
            
            # Create progress card
            status_emoji = {
                TaskStatus.PENDING: "⏳",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.COMPLETED: "✅",
                TaskStatus.FAILED: "❌",
                TaskStatus.CANCELLED: "🚫"
            }
            
            progress_card = cl.Card(
                title=f"{status_emoji.get(task.status, '❓')} Task Progress",
                content=f"""
                **Task**: {task.description}
                **Status**: {task.status.value}
                **Assigned Agents**: {', '.join(task.assigned_agents)}
                **Created**: {task.created_at.strftime('%H:%M:%S')}
                
                {f"**Error**: {task.error_message}" if task.error_message else ""}
                """,
                size="medium"
            )
            
            await cl.Message(
                content="",
                elements=[progress_card]
            ).send()
            
        except Exception as e:
            self.logger.error(f"Error showing task progress: {str(e)}")
    
    async def show_agent_status(self):
        """Show current agent status"""
        try:
            if not self.monitoring_system:
                return
            
            dashboard_data = await self.monitoring_system.get_dashboard_data()
            agent_health = dashboard_data.get("agent_health", {})
            
            # Create agent status cards
            agent_cards = []
            for agent_name, health in agent_health.items():
                status_emoji = "🟢" if health["is_healthy"] else "🔴"
                
                agent_card = cl.Card(
                    title=f"{status_emoji} {agent_name}",
                    content=f"""
                    **Status**: {health['status']}
                    **Response Time**: {health['response_time']:.2f}s
                    **Success Rate**: {health['success_rate']:.1%}
                    **Last Heartbeat**: {health['last_heartbeat']}
                    """,
                    size="small"
                )
                agent_cards.append(agent_card)
            
            if agent_cards:
                await cl.Message(
                    content="",
                    elements=agent_cards
                ).send()
            
        except Exception as e:
            self.logger.error(f"Error showing agent status: {str(e)}")
    
    async def handle_profile_update(self, message: str, user_id: str):
        """Handle profile update requests"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return
            
            # Simple keyword-based profile updates
            message_lower = message.lower()
            
            if "skill" in message_lower:
                # Extract skills from message
                skills = await self._extract_skills_from_message(message)
                if skills:
                    profile.skills.extend(skills)
                    profile.skills = list(set(profile.skills))  # Remove duplicates
            
            if "rate" in message_lower or "hourly" in message_lower:
                # Extract rate from message
                rate = await self._extract_rate_from_message(message)
                if rate:
                    profile.preferred_hourly_rate = rate
            
            if "experience" in message_lower or "year" in message_lower:
                # Extract experience from message
                experience = await self._extract_experience_from_message(message)
                if experience:
                    profile.experience_years = experience
            
            # Update profile
            profile.last_updated = datetime.now()
            await self.memory_layer.store_user_profile(profile)
            
            # Show updated profile
            await self.show_profile_summary(profile)
            
        except Exception as e:
            self.logger.error(f"Error handling profile update: {str(e)}")
    
    async def _extract_skills_from_message(self, message: str) -> List[str]:
        """Extract skills from user message"""
        # Simple keyword extraction - could be enhanced with NLP
        skills_keywords = [
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust",
            "react", "angular", "vue", "node.js", "django", "flask", "spring",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "machine learning", "ai", "data science", "sql", "mongodb", "redis",
            "design", "ui/ux", "graphic design", "illustration", "animation",
            "writing", "content", "marketing", "seo", "social media"
        ]
        
        found_skills = []
        message_lower = message.lower()
        
        for skill in skills_keywords:
            if skill in message_lower:
                found_skills.append(skill)
        
        return found_skills
    
    async def _extract_rate_from_message(self, message: str) -> Optional[float]:
        """Extract hourly rate from user message"""
        import re
        
        # Look for rate patterns like "$50/hour", "50 per hour", etc.
        rate_patterns = [
            r'\$(\d+(?:\.\d{2})?)\s*(?:per\s+)?hour',
            r'(\d+(?:\.\d{2})?)\s*(?:per\s+)?hour',
            r'rate\s+(?:of\s+)?\$?(\d+(?:\.\d{2})?)',
            r'\$(\d+(?:\.\d{2})?)\s*(?:an\s+)?hour'
        ]
        
        for pattern in rate_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    async def _extract_experience_from_message(self, message: str) -> Optional[int]:
        """Extract years of experience from user message"""
        import re
        
        # Look for experience patterns
        exp_patterns = [
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:in\s+)?(?:the\s+)?field'
        ]
        
        for pattern in exp_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    async def show_profile_summary(self, profile: UserProfile):
        """Show user profile summary"""
        try:
            profile_card = cl.Card(
                title="👤 Your Profile",
                content=f"""
                **Name**: {profile.name}
                **Skills**: {', '.join(profile.skills) if profile.skills else 'Not specified'}
                **Experience**: {profile.experience_years} years
                **Hourly Rate**: ${profile.preferred_hourly_rate}/hour
                **Location**: {profile.location}
                **Goals**: {', '.join(profile.goals) if profile.goals else 'Not specified'}
                **Profile Completeness**: {profile.profile_completeness:.1f}%
                """,
                size="medium"
            )
            
            await cl.Message(
                content="",
                elements=[profile_card]
            ).send()
            
        except Exception as e:
            self.logger.error(f"Error showing profile summary: {str(e)}")
    
    async def handle_special_commands(self, message: str, user_id: str) -> bool:
        """Handle special UI commands"""
        try:
            message_lower = message.lower().strip()
            
            if message_lower in ["dashboard", "show dashboard", "my dashboard"]:
                profile = self.user_profiles.get(user_id)
                if profile:
                    await self.create_dashboard(profile)
                return True
            
            elif message_lower in ["profile", "my profile", "show profile"]:
                profile = self.user_profiles.get(user_id)
                if profile:
                    await self.show_profile_summary(profile)
                return True
            
            elif message_lower in ["agents", "agent status", "show agents"]:
                await self.show_agent_status()
                return True
            
            elif message_lower in ["help", "commands", "what can you do"]:
                await self.show_help()
                return True
            
            elif "update profile" in message_lower:
                await self.handle_profile_update(message, user_id)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling special commands: {str(e)}")
            return False
    
    async def show_help(self):
        """Show help information"""
        try:
            help_card = cl.Card(
                title="❓ How Can I Help You?",
                content="""
                **Job Search**: "Find me Python development jobs"
                **Market Research**: "Research rates for web developers"
                **Calculations**: "Calculate my hourly rate for a project"
                **Proposals**: "Help me write a proposal for a web development project"
                **Profile**: "Update my profile" or "Show my profile"
                **Dashboard**: "Show my dashboard"
                **Agent Status**: "Show agent status"
                
                **Special Commands**:
                - "dashboard" - View your statistics and recent activity
                - "profile" - View or update your profile
                - "agents" - Check agent status
                - "help" - Show this help message
                """,
                size="large"
            )
            
            await cl.Message(
                content="",
                elements=[help_card]
            ).send()
            
        except Exception as e:
            self.logger.error(f"Error showing help: {str(e)}")

# Global UI instance
freelancex_ui = FreelanceXUI()

@on_chat_start
async def start_chat():
    """Initialize chat session"""
    try:
        # Get user ID (you might want to implement proper user authentication)
        user_id = user_session.get("user_id") or f"user_{int(datetime.now().timestamp())}"
        
        # Setup user session
        profile = await freelancex_ui.setup_user_session(user_id)
        
        if profile:
            # Create welcome message
            await freelancex_ui.create_welcome_message(profile)
            
            # Show dashboard
            await freelancex_ui.create_dashboard(profile)
        
    except Exception as e:
        logging.error(f"Error starting chat: {str(e)}")
        await cl.Message(content="Sorry, there was an error starting the chat. Please try again.").send()

@on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages"""
    try:
        user_id = user_session.get("user_id")
        if not user_id:
            await cl.Message(content="Error: User session not found. Please refresh the page.").send()
            return
        
        # Check for special commands first
        is_special_command = await freelancex_ui.handle_special_commands(message.content, user_id)
        if is_special_command:
            return
        
        # Show typing indicator
        await cl.Message(content="🤔 Thinking...").send()
        
        # Process the message
        result = await freelancex_ui.process_user_message(message.content, user_id)
        
        if "error" in result:
            await cl.Message(content=f"❌ Error: {result['error']}").send()
            return
        
        if "task_id" in result:
            # Show task progress
            await freelancex_ui.show_task_progress(result["task_id"])
            
            # Wait for task completion (in a real implementation, you'd use WebSockets or polling)
            await asyncio.sleep(2)
            
            # Show result (this would come from the actual task completion)
            await cl.Message(content="✅ Task completed! Here are the results...").send()
        
        # Store in chat history
        freelancex_ui.chat_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "message": message.content,
            "result": result
        })
        
    except Exception as e:
        logging.error(f"Error handling message: {str(e)}")
        await cl.Message(content="Sorry, there was an error processing your message. Please try again.").send()

# Configuration for Chainlit
cl.settings.ui.name = "FreelanceX.AI"
cl.settings.ui.description = "Your AI-powered freelance assistant"
cl.settings.ui.show_chain_of_thought = True
cl.settings.ui.show_readme_as_default = False

# Custom CSS for modern styling
cl.settings.ui.custom_css = """
.chat-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.message {
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card {
    border-radius: 12px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    border: none;
}

.card-title {
    font-weight: 600;
    color: #2d3748;
}

.card-content {
    color: #4a5568;
    line-height: 1.6;
}
"""

if __name__ == "__main__":
    # This would typically be run by Chainlit
    print("FreelanceX.AI Enhanced UI - Run with: chainlit run enhanced_ui.py")