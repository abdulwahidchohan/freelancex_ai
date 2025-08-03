#!/usr/bin/env python3
"""
FreelanceX.AI Configuration Management
Comprehensive configuration system with environment-specific settings and security
Features: Environment management, API keys, database settings, monitoring configuration
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
import secrets
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "freelancex"
    username: str = ""
    password: str = ""
    ssl_mode: str = "prefer"
    connection_pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class APIGatewayConfig:
    """API Gateway configuration settings"""
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    enable_cors: bool = True
    enable_https_redirect: bool = False
    trusted_hosts: List[str] = field(default_factory=list)
    enable_docs: bool = True

@dataclass
class MonitoringConfig:
    """Monitoring system configuration"""
    enabled: bool = True
    metrics_retention_days: int = 30
    health_check_interval: int = 60
    alert_email_enabled: bool = False
    alert_email_smtp_server: str = ""
    alert_email_smtp_port: int = 587
    alert_email_username: str = ""
    alert_email_password: str = ""
    alert_email_recipients: List[str] = field(default_factory=list)
    prometheus_enabled: bool = False
    prometheus_port: int = 9090

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    encryption_key: str = field(default_factory=lambda: Fernet.generate_key().decode())
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = False
    session_timeout_minutes: int = 60
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

@dataclass
class ExternalIntegrationsConfig:
    """External integrations configuration"""
    upwork_api_key: str = ""
    upwork_api_secret: str = ""
    freelancer_api_key: str = ""
    linkedin_api_key: str = ""
    google_scholar_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

@dataclass
class UIConfig:
    """User interface configuration"""
    title: str = "FreelanceX.AI"
    theme: str = "default"
    enable_voice_input: bool = True
    enable_image_upload: bool = True
    max_file_size_mb: int = 10
    supported_file_types: List[str] = field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".txt"
    ])
    dashboard_refresh_interval: int = 30
    notification_sound_enabled: bool = True

@dataclass
class AgentConfig:
    """Agent system configuration"""
    max_concurrent_tasks: int = 10
    task_timeout_minutes: int = 30
    memory_retention_days: int = 90
    enable_learning: bool = True
    enable_cross_agent_communication: bool = True
    default_model: str = "gpt-4"
    fallback_model: str = "gpt-3.5-turbo"
    max_tokens: int = 4000
    temperature: float = 0.7

class FreelanceXConfig:
    """Main configuration class for FreelanceX.AI"""
    
    def __init__(self, config_file: str = None, environment: str = None):
        self.environment = environment or os.getenv("FREELANCEX_ENV", "development")
        self.config_file = config_file or self._get_default_config_file()
        
        # Initialize configuration sections
        self.database = DatabaseConfig()
        self.api_gateway = APIGatewayConfig()
        self.monitoring = MonitoringConfig()
        self.security = SecurityConfig()
        self.external_integrations = ExternalIntegrationsConfig()
        self.ui = UIConfig()
        self.agents = AgentConfig()
        
        # Load configuration
        self._load_configuration()
        
        logger.info(f"FreelanceX.AI configuration loaded for environment: {self.environment}")
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file path"""
        config_dir = Path(__file__).parent
        return str(config_dir / f"settings_{self.environment}.json")
    
    def _load_configuration(self):
        """Load configuration from various sources"""
        try:
            # Load from file if exists
            if os.path.exists(self.config_file):
                self._load_from_file()
            
            # Override with environment variables
            self._load_from_environment()
            
            # Validate configuration
            self._validate_configuration()
            
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    def _load_from_file(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            # Update configuration sections
            if "database" in config_data:
                self._update_dataclass(self.database, config_data["database"])
            
            if "api_gateway" in config_data:
                self._update_dataclass(self.api_gateway, config_data["api_gateway"])
            
            if "monitoring" in config_data:
                self._update_dataclass(self.monitoring, config_data["monitoring"])
            
            if "security" in config_data:
                self._update_dataclass(self.security, config_data["security"])
            
            if "external_integrations" in config_data:
                self._update_dataclass(self.external_integrations, config_data["external_integrations"])
            
            if "ui" in config_data:
                self._update_dataclass(self.ui, config_data["ui"])
            
            if "agents" in config_data:
                self._update_dataclass(self.agents, config_data["agents"])
            
            logger.info(f"Configuration loaded from file: {self.config_file}")
            
        except Exception as e:
            logger.warning(f"Could not load configuration file {self.config_file}: {str(e)}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            # Database
            "FREELANCEX_DB_TYPE": ("database", "type"),
            "FREELANCEX_DB_HOST": ("database", "host"),
            "FREELANCEX_DB_PORT": ("database", "port"),
            "FREELANCEX_DB_NAME": ("database", "name"),
            "FREELANCEX_DB_USERNAME": ("database", "username"),
            "FREELANCEX_DB_PASSWORD": ("database", "password"),
            
            # API Gateway
            "FREELANCEX_API_HOST": ("api_gateway", "host"),
            "FREELANCEX_API_PORT": ("api_gateway", "port"),
            "FREELANCEX_API_SECRET_KEY": ("api_gateway", "secret_key"),
            
            # Security
            "FREELANCEX_ENCRYPTION_KEY": ("security", "encryption_key"),
            
            # External Integrations
            "UPWORK_API_KEY": ("external_integrations", "upwork_api_key"),
            "UPWORK_API_SECRET": ("external_integrations", "upwork_api_secret"),
            "FREELANCER_API_KEY": ("external_integrations", "freelancer_api_key"),
            "LINKEDIN_API_KEY": ("external_integrations", "linkedin_api_key"),
            "GOOGLE_SCHOLAR_API_KEY": ("external_integrations", "google_scholar_api_key"),
            "REDDIT_CLIENT_ID": ("external_integrations", "reddit_client_id"),
            "REDDIT_CLIENT_SECRET": ("external_integrations", "reddit_client_secret"),
            "OPENAI_API_KEY": ("external_integrations", "openai_api_key"),
            "ANTHROPIC_API_KEY": ("external_integrations", "anthropic_api_key"),
            
            # Monitoring
            "FREELANCEX_MONITORING_ENABLED": ("monitoring", "enabled"),
            "FREELANCEX_ALERT_EMAIL": ("monitoring", "alert_email_enabled"),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                section_obj = getattr(self, section)
                
                # Type conversion
                if hasattr(section_obj, key):
                    current_value = getattr(section_obj, key)
                    if isinstance(current_value, bool):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    elif isinstance(current_value, int):
                        value = int(value)
                    elif isinstance(current_value, float):
                        value = float(value)
                    elif isinstance(current_value, list):
                        value = value.split(',') if value else []
                
                setattr(section_obj, key, value)
    
    def _update_dataclass(self, dataclass_obj, config_dict: Dict[str, Any]):
        """Update dataclass with configuration dictionary"""
        for key, value in config_dict.items():
            if hasattr(dataclass_obj, key):
                setattr(dataclass_obj, key, value)
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        errors = []
        
        # Validate database configuration
        if self.database.type not in ["sqlite", "postgresql", "mysql"]:
            errors.append(f"Invalid database type: {self.database.type}")
        
        # Validate API Gateway configuration
        if not (1024 <= self.api_gateway.port <= 65535):
            errors.append(f"Invalid API port: {self.api_gateway.port}")
        
        if len(self.api_gateway.secret_key) < 32:
            errors.append("API secret key must be at least 32 characters")
        
        # Validate security configuration
        if self.security.password_min_length < 6:
            errors.append("Minimum password length must be at least 6")
        
        # Validate monitoring configuration
        if self.monitoring.health_check_interval < 10:
            errors.append("Health check interval must be at least 10 seconds")
        
        if errors:
            raise ValueError(f"Configuration validation errors: {'; '.join(errors)}")
    
    def save_to_file(self, file_path: str = None):
        """Save current configuration to file"""
        try:
            file_path = file_path or self.config_file
            
            config_data = {
                "database": self._dataclass_to_dict(self.database),
                "api_gateway": self._dataclass_to_dict(self.api_gateway),
                "monitoring": self._dataclass_to_dict(self.monitoring),
                "security": self._dataclass_to_dict(self.security),
                "external_integrations": self._dataclass_to_dict(self.external_integrations),
                "ui": self._dataclass_to_dict(self.ui),
                "agents": self._dataclass_to_dict(self.agents)
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            raise
    
    def _dataclass_to_dict(self, dataclass_obj) -> Dict[str, Any]:
        """Convert dataclass to dictionary"""
        return {
            field.name: getattr(dataclass_obj, field.name)
            for field in dataclass_obj.__dataclass_fields__.values()
        }
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database.type == "sqlite":
            return f"sqlite:///{self.database.name}.db"
        elif self.database.type == "postgresql":
            return (f"postgresql://{self.database.username}:{self.database.password}"
                   f"@{self.database.host}:{self.database.port}/{self.database.name}")
        elif self.database.type == "mysql":
            return (f"mysql://{self.database.username}:{self.database.password}"
                   f"@{self.database.host}:{self.database.port}/{self.database.name}")
        else:
            raise ValueError(f"Unsupported database type: {self.database.type}")
    
    def get_external_integrations_config(self) -> Dict[str, Dict[str, str]]:
        """Get external integrations configuration"""
        return {
            "upwork": {
                "api_key": self.external_integrations.upwork_api_key,
                "api_secret": self.external_integrations.upwork_api_secret
            },
            "freelancer": {
                "api_key": self.external_integrations.freelancer_api_key
            },
            "linkedin": {
                "api_key": self.external_integrations.linkedin_api_key
            },
            "google_scholar": {
                "api_key": self.external_integrations.google_scholar_api_key
            },
            "reddit": {
                "client_id": self.external_integrations.reddit_client_id,
                "client_secret": self.external_integrations.reddit_client_secret
            }
        }
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == "development"
    
    def is_testing(self) -> bool:
        """Check if running in testing environment"""
        return self.environment == "testing"
    
    def get_log_level(self) -> str:
        """Get appropriate log level for environment"""
        if self.is_production():
            return "WARNING"
        elif self.is_testing():
            return "ERROR"
        else:
            return "INFO"

# Global configuration instance
_config = None

def get_config(config_file: str = None, environment: str = None) -> FreelanceXConfig:
    """Get or create the global configuration instance"""
    global _config
    if _config is None:
        _config = FreelanceXConfig(config_file, environment)
    return _config

def reload_config(config_file: str = None, environment: str = None) -> FreelanceXConfig:
    """Reload the global configuration"""
    global _config
    _config = FreelanceXConfig(config_file, environment)
    return _config

# Environment-specific defaults
DEVELOPMENT_DEFAULTS = {
    "database": {
        "type": "sqlite",
        "name": "freelancex_dev",
        "echo": True
    },
    "api_gateway": {
        "enable_docs": True,
        "enable_cors": True
    },
    "monitoring": {
        "enabled": True,
        "prometheus_enabled": False
    },
    "security": {
        "session_timeout_minutes": 120
    },
    "agents": {
        "enable_learning": True,
        "temperature": 0.8
    }
}

PRODUCTION_DEFAULTS = {
    "database": {
        "type": "postgresql",
        "connection_pool_size": 20,
        "echo": False
    },
    "api_gateway": {
        "enable_docs": False,
        "enable_https_redirect": True,
        "max_requests_per_minute": 100
    },
    "monitoring": {
        "enabled": True,
        "prometheus_enabled": True,
        "alert_email_enabled": True
    },
    "security": {
        "session_timeout_minutes": 30,
        "password_require_symbols": True
    },
    "agents": {
        "enable_learning": True,
        "temperature": 0.7
    }
}

TESTING_DEFAULTS = {
    "database": {
        "type": "sqlite",
        "name": ":memory:",
        "echo": False
    },
    "api_gateway": {
        "enable_docs": False,
        "enable_cors": True
    },
    "monitoring": {
        "enabled": False
    },
    "agents": {
        "enable_learning": False,
        "task_timeout_minutes": 5
    }
}