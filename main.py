#!/usr/bin/env python3
"""
FreelanceX.AI - Main Application

A powerful AI-driven platform for freelancers that leverages cutting-edge technologies
to streamline and enhance your freelancing career.

This is the main entry point for the FreelanceX.AI application.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core components
from core.agent_manager import AgentManager
from core.user_profile_manager import UserProfileManager
from core.daily_routines import DailyRoutinesManager
from core.executive_agent import ExecutiveAgent

# Import agents
from agents.job_search_agent import JobSearchAgent
from agents.web_search_agent import WebSearchAgent
from agents.math_agent import MathAgent

class FreelanceXAI:
    """
    Main FreelanceX.AI Application Class
    
    This class orchestrates all the components of the FreelanceX.AI platform:
    - Agent Manager for coordinating AI agents
    - User Profile Manager for personalized experiences
    - Daily Routines Manager for automated workflows
    - Executive Agent for high-level decision making
    """
    
    def __init__(self, config_path: str = 'config/system_prompts.yaml'):
        # Set up logging
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config_path = config_path
        self.is_running = False
        
        # Core components
        self.user_profile_manager: Optional[UserProfileManager] = None
        self.agent_manager: Optional[AgentManager] = None
        self.daily_routines_manager: Optional[DailyRoutinesManager] = None
        self.executive_agent: Optional[ExecutiveAgent] = None
        
        # Application state
        self.startup_time = None
        self.total_requests_processed = 0
        self.active_sessions = {}
        
        self.logger.info("FreelanceX.AI application initialized")

    def _setup_logging(self):
        """Set up logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('freelancex_ai.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

    async def initialize(self, user_profile_data: Optional[Dict[str, Any]] = None):
        """
        Initialize the FreelanceX.AI application
        
        Args:
            user_profile_data: Optional user profile data for initialization
        """
        self.logger.info("Initializing FreelanceX.AI...")
        
        try:
            # Initialize user profile manager
            self.user_profile_manager = UserProfileManager()
            
            # Create default user profile if data provided
            if user_profile_data:
                self.user_profile_manager.create_profile(user_profile_data)
                self.logger.info(f"Created user profile for: {user_profile_data.get('name', 'Unknown')}")
            else:
                # Create a default profile for demonstration
                default_profile = {
                    'name': 'Demo User',
                    'email': 'demo@freelancex.ai',
                    'location': 'Remote',
                    'timezone': 'UTC',
                    'bio': 'Freelance professional using FreelanceX.AI'
                }
                self.user_profile_manager.create_profile(default_profile)
                self.logger.info("Created default user profile")
            
            # Initialize agent manager with user profile
            user_profile = self.user_profile_manager.get_profile_summary()
            self.agent_manager = AgentManager(user_profile)
            
            # Initialize daily routines manager
            self.daily_routines_manager = DailyRoutinesManager(
                self.agent_manager, 
                self.user_profile_manager
            )
            
            # Initialize executive agent
            self.executive_agent = ExecutiveAgent(self.config_path)
            
            # Start the agent manager
            await self.agent_manager.start()
            
            # Start daily routines scheduler
            await self.daily_routines_manager.start_routine_scheduler()
            
            self.startup_time = datetime.now()
            self.is_running = True
            
            self.logger.info("FreelanceX.AI initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FreelanceX.AI: {e}")
            raise

    async def shutdown(self):
        """Shutdown the FreelanceX.AI application gracefully"""
        self.logger.info("Shutting down FreelanceX.AI...")
        
        try:
            # Stop the agent manager
            if self.agent_manager:
                await self.agent_manager.stop()
            
            # Stop daily routines
            if self.daily_routines_manager:
                # Note: In a real implementation, you'd have proper shutdown for routines
                pass
            
            self.is_running = False
            
            # Calculate uptime
            if self.startup_time:
                uptime = datetime.now() - self.startup_time
                self.logger.info(f"FreelanceX.AI was running for: {uptime}")
            
            self.logger.info("FreelanceX.AI shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def process_user_request(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a user request through the coordinated agent system
        
        Args:
            request: User's natural language request
            context: Additional context information
            
        Returns:
            Coordinated response from the agent system
        """
        if not self.is_running:
            raise RuntimeError("FreelanceX.AI is not running")
        
        self.logger.info(f"Processing user request: {request[:100]}...")
        
        try:
            # Track the request
            self.total_requests_processed += 1
            
            # Use the agent manager to coordinate the response
            response = await self.agent_manager.coordinate_agents(request, context)
            
            # Track user behavior
            if self.user_profile_manager:
                self.user_profile_manager.track_behavior(
                    action_type='user_request',
                    action_data={'request': request, 'response_summary': response.get('summary', '')},
                    success_rate=1.0,
                    time_spent=0,  # Would calculate actual time
                    satisfaction_score=None  # Would be provided by user
                )
            
            self.logger.info(f"Request processed successfully. Response summary: {response.get('summary', '')[:100]}...")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing user request: {e}")
            
            # Track failed request
            if self.user_profile_manager:
                self.user_profile_manager.track_behavior(
                    action_type='user_request',
                    action_data={'request': request, 'error': str(e)},
                    success_rate=0.0,
                    time_spent=0,
                    satisfaction_score=0.0
                )
            
            raise

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'is_running': self.is_running,
            'startup_time': self.startup_time.isoformat() if self.startup_time else None,
            'total_requests_processed': self.total_requests_processed,
            'active_sessions': len(self.active_sessions),
            'uptime': str(datetime.now() - self.startup_time) if self.startup_time else None
        }
        
        # Add agent manager status
        if self.agent_manager:
            status['agent_manager'] = self.agent_manager.get_system_status()
        
        # Add user profile status
        if self.user_profile_manager:
            status['user_profile'] = self.user_profile_manager.get_profile_summary()
        
        # Add daily routines status
        if self.daily_routines_manager:
            status['daily_routines'] = self.daily_routines_manager.get_routine_statistics()
        
        return status

    async def update_user_profile(self, profile_updates: Dict[str, Any]):
        """Update user profile with new information"""
        if not self.user_profile_manager:
            raise RuntimeError("User profile manager not initialized")
        
        self.logger.info("Updating user profile...")
        
        # Update basic info
        if 'basic_info' in profile_updates:
            self.user_profile_manager.update_basic_info(profile_updates['basic_info'])
        
        # Add skills
        if 'skills' in profile_updates:
            for skill_data in profile_updates['skills']:
                self.user_profile_manager.add_skill(skill_data)
        
        # Add work history
        if 'work_history' in profile_updates:
            for work_data in profile_updates['work_history']:
                self.user_profile_manager.add_work_history(work_data)
        
        # Update financial profile
        if 'financial_profile' in profile_updates:
            self.user_profile_manager.set_financial_profile(profile_updates['financial_profile'])
        
        # Update work preferences
        if 'work_preferences' in profile_updates:
            self.user_profile_manager.set_work_preferences(profile_updates['work_preferences'])
        
        # Add learning goals
        if 'learning_goals' in profile_updates:
            for goal_data in profile_updates['learning_goals']:
                self.user_profile_manager.add_learning_goal(goal_data)
        
        # Update agent preferences
        if 'agent_preferences' in profile_updates:
            for agent_id, preferences in profile_updates['agent_preferences'].items():
                self.user_profile_manager.update_agent_preferences(agent_id, preferences)
        
        # Update agent manager with new profile
        if self.agent_manager:
            user_profile = self.user_profile_manager.get_profile_summary()
            # Note: In a real implementation, you'd update the agent manager's user profile
            
        self.logger.info("User profile updated successfully")

    async def get_personalized_recommendations(self) -> Dict[str, Any]:
        """Get personalized recommendations for the user"""
        if not self.user_profile_manager:
            raise RuntimeError("User profile manager not initialized")
        
        recommendations = {}
        
        # Get recommendations for each agent
        for agent_id in ['job_search', 'web_search', 'math']:
            agent_recs = self.user_profile_manager.get_agent_recommendations(agent_id)
            recommendations[agent_id] = agent_recs
        
        # Get behavior insights
        behavior_insights = self.user_profile_manager.learn_from_behavior()
        recommendations['behavior_insights'] = behavior_insights
        
        return recommendations

    async def export_system_data(self, export_path: str = None) -> Dict[str, str]:
        """Export all system data for backup or analysis"""
        if not export_path:
            export_path = f"freelancex_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        exported_files = {}
        
        try:
            # Export user profile
            if self.user_profile_manager:
                profile_file = self.user_profile_manager.export_profile(
                    f"{export_path}_user_profile.json"
                )
                exported_files['user_profile'] = profile_file
            
            # Export agent manager logs
            if self.agent_manager:
                agent_logs_file = self.agent_manager.export_system_logs(
                    f"{export_path}_agent_logs.json"
                )
                exported_files['agent_logs'] = agent_logs_file
            
            # Export daily routines data
            if self.daily_routines_manager:
                routines_file = self.daily_routines_manager.export_routine_data(
                    f"{export_path}_routines.json"
                )
                exported_files['daily_routines'] = routines_file
            
            # Export system status
            system_status = await self.get_system_status()
            import json
            status_file = f"{export_path}_system_status.json"
            with open(status_file, 'w') as f:
                json.dump(system_status, f, indent=2, default=str)
            exported_files['system_status'] = status_file
            
            self.logger.info(f"System data exported to: {export_path}")
            return exported_files
            
        except Exception as e:
            self.logger.error(f"Error exporting system data: {e}")
            raise

    async def run_demo(self):
        """Run a demonstration of FreelanceX.AI capabilities"""
        self.logger.info("Starting FreelanceX.AI demonstration...")
        
        # Demo user profile
        demo_profile = {
            'name': 'Alex Chen',
            'email': 'alex.chen@example.com',
            'location': 'San Francisco, CA',
            'timezone': 'America/Los_Angeles',
            'bio': 'Full-stack developer with 5+ years of experience in web development and AI/ML'
        }
        
        # Demo skills
        demo_skills = [
            {
                'name': 'Python',
                'level': 'expert',
                'years_experience': 5.0,
                'proficiency_score': 0.9,
                'is_preferred': True
            },
            {
                'name': 'JavaScript',
                'level': 'expert',
                'years_experience': 4.0,
                'proficiency_score': 0.85,
                'is_preferred': True
            },
            {
                'name': 'Machine Learning',
                'level': 'intermediate',
                'years_experience': 2.0,
                'proficiency_score': 0.7,
                'is_preferred': False
            }
        ]
        
        # Demo financial profile
        demo_financial = {
            'desired_annual_income': 120000,
            'current_hourly_rate': 75,
            'preferred_rate_range': {'min': 60, 'max': 100},
            'tax_rate': 0.25,
            'currency': 'USD',
            'business_expenses': 15000
        }
        
        # Demo work preferences
        demo_work_prefs = {
            'preferred_work_type': 'remote',
            'preferred_hours': {'start_hour': 9, 'end_hour': 17},
            'timezone': 'America/Los_Angeles',
            'availability': {
                'monday': True, 'tuesday': True, 'wednesday': True,
                'thursday': True, 'friday': True, 'saturday': False, 'sunday': False
            },
            'communication_preferences': ['email', 'slack', 'zoom'],
            'project_duration_preferences': ['short_term', 'long_term'],
            'industry_preferences': ['technology', 'healthcare', 'finance']
        }
        
        # Initialize with demo data
        await self.initialize(demo_profile)
        
        # Update profile with demo data
        await self.update_user_profile({
            'skills': demo_skills,
            'financial_profile': demo_financial,
            'work_preferences': demo_work_prefs
        })
        
        # Demo requests
        demo_requests = [
            "Find me high-paying Python development jobs on Upwork",
            "Research the latest trends in AI and machine learning for freelancers",
            "Calculate my optimal hourly rate based on my expenses and income goals",
            "What are the best strategies for increasing my freelance income?"
        ]
        
        print("\n" + "="*60)
        print("FREELANCEX.AI DEMONSTRATION")
        print("="*60)
        
        for i, request in enumerate(demo_requests, 1):
            print(f"\n--- Demo Request {i} ---")
            print(f"User: {request}")
            
            try:
                response = await self.process_user_request(request)
                print(f"FreelanceX.AI: {response.get('summary', 'Response generated')}")
                print(f"Agents consulted: {', '.join(response.get('agents_consulted', []))}")
                
            except Exception as e:
                print(f"Error: {e}")
        
        # Show system status
        print(f"\n--- System Status ---")
        status = await self.get_system_status()
        print(f"Total requests processed: {status['total_requests_processed']}")
        print(f"Agent manager tasks: {status.get('agent_manager', {}).get('total_tasks_processed', 0)}")
        print(f"User profile skills: {status.get('user_profile', {}).get('skills_count', 0)}")
        
        # Show personalized recommendations
        print(f"\n--- Personalized Recommendations ---")
        recommendations = await self.get_personalized_recommendations()
        for agent_id, recs in recommendations.items():
            if recs.get('learning_suggestions'):
                print(f"{agent_id}: {recs['learning_suggestions'][0] if recs['learning_suggestions'] else 'No suggestions'}")
        
        print(f"\n--- Demo Complete ---")
        print("="*60)

async def main():
    """Main entry point for the FreelanceX.AI application"""
    app = FreelanceXAI()
    
    try:
        # Check if demo mode is requested
        if len(sys.argv) > 1 and sys.argv[1] == '--demo':
            await app.run_demo()
        else:
            # Initialize with default profile
            await app.initialize()
            
            # Keep the application running
            print("FreelanceX.AI is running. Press Ctrl+C to stop.")
            while True:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\nShutting down FreelanceX.AI...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await app.shutdown()

if __name__ == "__main__":
    # Run the application
    asyncio.run(main())