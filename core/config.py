"""
FreelanceX.AI Configuration Management
Handles loading and managing system configuration from YAML files
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    description: str
    model: str
    temperature: float
    max_tokens: int
    capabilities: list
    tools: list
    enabled: bool
    priority: int

@dataclass
class ToolConfig:
    """Configuration for tools"""
    name: str
    description: str
    type: str
    config: Dict[str, Any]
    required_keys: list

@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str
    max_concurrent_tasks: int
    task_timeout: int
    retry_attempts: int
    health_check_interval: int
    memory_cleanup_interval: int

class Config:
    """
    Central configuration manager for FreelanceX.AI
    Loads and manages all system settings, agent configs, and tool definitions
    """
    
    def __init__(self):
        self.config_path = Path("agent.yaml")
        self.env_path = Path(".env")
        self.config_data = {}
        self.agents = {}
        self.tools = {}
        self.system_config = None
        self.user_profile = {}
        
    async def load(self):
        """Load configuration from YAML file and environment variables"""
        try:
            # Load YAML configuration
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)
                logger.info("✅ Configuration loaded from agent.yaml")
            else:
                logger.warning("⚠️ agent.yaml not found, using default configuration")
                self.config_data = self._get_default_config()
            
            # Load environment variables
            self._load_env_vars()
            
            # Parse configurations
            self._parse_agent_configs()
            self._parse_tool_configs()
            self._parse_system_config()
            self._parse_user_profile()
            
            # Validate configuration
            self._validate_config()
            
            logger.info("✅ Configuration initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration loading failed: {str(e)}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if YAML file is missing"""
        return {
            "name": "FreelanceX.AI",
            "description": "World-class AI assistant platform for freelancers",
            "version": "1.0.0",
            "system": {
                "log_level": "INFO",
                "max_concurrent_tasks": 10,
                "task_timeout": 300,
                "retry_attempts": 3,
                "health_check_interval": 300,
                "memory_cleanup_interval": 86400
            }
        }
    
    def _load_env_vars(self):
        """Load environment variables for API keys and secrets"""
        env_vars = [
            "OPENAI_API_KEY",
            "UPWORK_API_KEY",
            "UPWORK_API_SECRET",
            "FIVERR_API_KEY",
            "LINKEDIN_CLIENT_ID",
            "LINKEDIN_CLIENT_SECRET",
            "GOOGLE_SEARCH_API_KEY",
            "GMAIL_CLIENT_ID",
            "GMAIL_CLIENT_SECRET"
        ]
        
        for var in env_vars:
            if os.getenv(var):
                logger.info(f"✅ Environment variable {var} loaded")
            else:
                logger.warning(f"⚠️ Environment variable {var} not set")
    
    def _parse_agent_configs(self):
        """Parse agent configurations from YAML"""
        agents_data = self.config_data.get('agents', {})
        
        for agent_id, agent_data in agents_data.items():
            try:
                agent_config = AgentConfig(
                    name=agent_data.get('name', agent_id),
                    description=agent_data.get('description', ''),
                    model=agent_data.get('model', 'gpt-4'),
                    temperature=agent_data.get('temperature', 0.5),
                    max_tokens=agent_data.get('max_tokens', 1000),
                    capabilities=agent_data.get('capabilities', []),
                    tools=agent_data.get('tools', []),
                    enabled=agent_data.get('enabled', True),
                    priority=agent_data.get('priority', 999)
                )
                self.agents[agent_id] = agent_config
                logger.info(f"📋 Parsed agent config: {agent_config.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to parse agent config {agent_id}: {str(e)}")
    
    def _parse_tool_configs(self):
        """Parse tool configurations from YAML"""
        tools_data = self.config_data.get('tools', {})
        
        for tool_id, tool_data in tools_data.items():
            try:
                tool_config = ToolConfig(
                    name=tool_data.get('name', tool_id),
                    description=tool_data.get('description', ''),
                    type=tool_data.get('type', 'tool'),
                    config=tool_data.get('config', {}),
                    required_keys=tool_data.get('required_keys', [])
                )
                self.tools[tool_id] = tool_config
                logger.info(f"🔧 Parsed tool config: {tool_config.name}")
                
            except Exception as e:
                logger.error(f"❌ Failed to parse tool config {tool_id}: {str(e)}")
    
    def _parse_system_config(self):
        """Parse system configuration"""
        system_data = self.config_data.get('system', {})
        
        try:
            self.system_config = SystemConfig(
                log_level=system_data.get('log_level', 'INFO'),
                max_concurrent_tasks=system_data.get('max_concurrent_tasks', 10),
                task_timeout=system_data.get('task_timeout', 300),
                retry_attempts=system_data.get('retry_attempts', 3),
                health_check_interval=system_data.get('health_check_interval', 300),
                memory_cleanup_interval=system_data.get('memory_cleanup_interval', 86400)
            )
            logger.info("⚙️ System configuration parsed")
            
        except Exception as e:
            logger.error(f"❌ Failed to parse system config: {str(e)}")
    
    def _parse_user_profile(self):
        """Parse user profile configuration"""
        self.user_profile = self.config_data.get('user_profile', {})
        logger.info(f"👤 User profile loaded: {self.user_profile.get('name', 'Unknown')}")
    
    def _validate_config(self):
        """Validate configuration integrity"""
        # Check required environment variables for enabled tools
        for tool_id, tool_config in self.tools.items():
            for key in tool_config.required_keys:
                if not os.getenv(key):
                    logger.warning(f"⚠️ Required environment variable {key} not set for tool {tool_id}")
        
        # Validate agent configurations
        for agent_id, agent_config in self.agents.items():
            if agent_config.enabled:
                # Check if agent's tools are available
                for tool_name in agent_config.tools:
                    if tool_name not in self.tools:
                        logger.warning(f"⚠️ Tool {tool_name} not found for agent {agent_id}")
        
        logger.info("✅ Configuration validation complete")
    
    def get_agent_config(self, agent_id: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent"""
        return self.agents.get(agent_id)
    
    def get_tool_config(self, tool_id: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool"""
        return self.tools.get(tool_id)
    
    def get_enabled_agents(self) -> Dict[str, AgentConfig]:
        """Get all enabled agents"""
        return {k: v for k, v in self.agents.items() if v.enabled}
    
    def get_agent_by_capability(self, capability: str) -> Optional[AgentConfig]:
        """Find agent with specific capability"""
        for agent_config in self.agents.values():
            if agent_config.enabled and capability in agent_config.capabilities:
                return agent_config
        return None
    
    def get_system_setting(self, key: str, default=None):
        """Get system configuration setting"""
        if self.system_config:
            return getattr(self.system_config, key, default)
        return default
    
    def get_user_setting(self, key: str, default=None):
        """Get user profile setting"""
        return self.user_profile.get(key, default)
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration dynamically"""
        try:
            # Update config data
            for key, value in updates.items():
                keys = key.split('.')
                current = self.config_data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            
            # Reload configurations
            self._parse_agent_configs()
            self._parse_tool_configs()
            self._parse_system_config()
            
            logger.info("✅ Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Configuration update failed: {str(e)}")
            return False 