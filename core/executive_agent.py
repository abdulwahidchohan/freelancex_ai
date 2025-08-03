#!/usr/bin/env python3
"""
FreelanceX.AI Executive Agent - OpenAI Agent SDK Implementation
Central coordinator using OpenAI Agent SDK for task delegation and management
"""

import os
import yaml
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from openai_agents import Agent, Session
from openai import OpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class TaskRequest(BaseModel):
    """Model for task requests"""
    task_type: str
    description: str
    priority: int = 1
    metadata: Dict[str, Any] = {}

class ExecutiveAgent:
    """
    OpenAI Agent SDK-based Executive Agent
    Manages task delegation and coordination using the OpenAI Agent SDK
    """
    
    def __init__(self, config_path: str = 'config/system_prompts.yaml'):
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load system prompt from configuration
        self.system_prompt = self._load_config(config_path)
        self.logger.info('ExecutiveAgent initializing with OpenAI Agent SDK...')
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        self.client = OpenAI(api_key=api_key)
        
        # Initialize the OpenAI Agent SDK agent
        self.agent = Agent(
            name="FreelanceX Executive Agent",
            instructions=self.system_prompt,
            model="gpt-4o",
            tools=[self._get_task_delegation_tool(), self._get_status_check_tool()]
        )
        
        # Session management
        self.sessions: Dict[str, Session] = {}
        
        self.logger.info('✅ ExecutiveAgent initialized with OpenAI Agent SDK')
    
    def _load_config(self, config_path: str) -> str:
        """Load and validate configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if not config.get('system_prompt'):
                    raise ValueError("system_prompt not found in config file")
                return config['system_prompt']
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            # Fallback system prompt
            return """
            You are the Executive Agent for FreelanceX.AI, a comprehensive AI-powered freelancing assistant.
            Your role is to coordinate tasks, delegate to specialized agents, and ensure optimal user experience.
            
            Mission: Enhance productivity, decision-making, and market adaptability for freelancers.
            Values: Innovation, autonomy, collaboration, growth, and impact.
            
            Always prioritize user privacy, ethical AI usage, and bias mitigation.
            """
    
    def _get_task_delegation_tool(self):
        """Define task delegation tool for the agent"""
        def delegate_task(task_type: str, description: str, priority: int = 1) -> str:
            """
            Delegate a task to the appropriate specialized agent.
            
            Args:
                task_type: Type of task (job_search, web_search, math, etc.)
                description: Detailed description of the task
                priority: Task priority (1-5, where 5 is highest)
            
            Returns:
                str: Task delegation result
            """
            try:
                # Task delegation logic would integrate with existing agent manager
                self.logger.info(f"Delegating {task_type} task: {description}")
                
                # This would integrate with the existing AgentManager
                result = f"Task '{task_type}' delegated successfully. Description: {description}"
                return result
                
            except Exception as e:
                self.logger.error(f"Task delegation failed: {str(e)}")
                return f"Task delegation failed: {str(e)}"
        
        return delegate_task
    
    def _get_status_check_tool(self):
        """Define status checking tool for the agent"""
        def check_agent_status(agent_name: str = None) -> str:
            """
            Check the status of agents in the system.
            
            Args:
                agent_name: Specific agent to check, or None for all agents
            
            Returns:
                str: Agent status information
            """
            try:
                # This would integrate with the existing AgentManager
                if agent_name:
                    return f"Agent '{agent_name}' status: Active"
                else:
                    return "All agents status: Active and ready"
                    
            except Exception as e:
                self.logger.error(f"Status check failed: {str(e)}")
                return f"Status check failed: {str(e)}"
        
        return check_agent_status
    
    def get_or_create_session(self, user_id: str) -> Session:
        """Get or create a session for a user"""
        if user_id not in self.sessions:
            self.sessions[user_id] = Session(agent=self.agent)
            self.logger.info(f"Created new session for user: {user_id}")
        return self.sessions[user_id]
    
    async def handle_message(self, message_content: str, user_id: str = "default") -> str:
        """
        Handle incoming messages using OpenAI Agent SDK.
        
        Args:
            message_content: The input message to process
            user_id: User identifier for session management
            
        Returns:
            str: The generated response
        """
        self.logger.info(f"Processing message for user {user_id}: {message_content[:100]}...")
        
        try:
            # Get or create session for the user
            session = self.get_or_create_session(user_id)
            
            # Process message through the agent
            response = session.run(message_content)
            
            # Extract text from response
            if hasattr(response, 'content'):
                return response.content
            elif isinstance(response, str):
                return response
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    async def execute_task(self, task: Dict[str, Any], user_id: str = "default") -> Dict[str, Any]:
        """
        Execute a task using OpenAI Agent SDK.
        
        Args:
            task: Dictionary containing task details
            user_id: User identifier for session management
            
        Returns:
            Dict containing task results and status
        """
        self.logger.info(f"Executing task for user {user_id}: {task}")
        
        try:
            # Validate task format
            if not isinstance(task, dict) or 'type' not in task:
                raise ValueError("Invalid task format")
            
            # Get or create session for the user
            session = self.get_or_create_session(user_id)
            
            # Format task as a message for the agent
            task_message = f"Execute task: {task['type']} - {task.get('description', 'No description provided')}"
            
            # Process through the agent
            response = session.run(task_message)
            
            result = {
                'status': 'completed',
                'task_id': task.get('id'),
                'result': str(response),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"Task completed successfully: {task.get('id')}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            return {
                'status': 'failed',
                'task_id': task.get('id'),
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def close_session(self, user_id: str):
        """Close a user session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            self.logger.info(f"Closed session for user: {user_id}")
    
    def get_session_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get session history for a user"""
        session = self.sessions.get(user_id)
        if session and hasattr(session, 'messages'):
            return [{'role': msg.role, 'content': msg.content} for msg in session.messages]
        return []
