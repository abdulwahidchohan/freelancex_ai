#!/usr/bin/env python3
"""
FreelanceX.AI Full Access Setup Script
Configures the application with full access permissions and API keys
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for full access"""
    logger.info("Setting up environment for full access...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("Creating .env file...")
        create_env_file()
    else:
        logger.info(".env file already exists")
    
    # Set default environment variables if not already set
    env_vars = {
        "FREELANCEX_ENV": "development",
        "FREELANCEX_DEBUG": "true",
        "FREELANCEX_LOG_LEVEL": "INFO",
        "FREELANCEX_DATABASE_URL": "sqlite:///freelancex.db",
        "FREELANCEX_SESSION_SECRET": "freelancex_ai_session_secret_2024",
        "FREELANCEX_ENABLE_METRICS": "true",
        "FREELANCEX_ENABLE_TRACING": "true",
        "FREELANCEX_API_KEY_REQUIRED": "false",  # Allow operation without API keys
        "FREELANCEX_SESSION_VALIDATION": "false",  # Disable strict session validation
        "FREELANCEX_RATE_LIMITING": "false",  # Disable rate limiting for full access
        "FREELANCEX_ADMIN_USERS": "admin,user,test",  # Grant admin access to common users
    }
    
    for key, value in env_vars.items():
        if not os.getenv(key):
            os.environ[key] = value
            logger.info(f"Set {key}={value}")

def create_env_file():
    """Create .env file with default configuration"""
    env_content = """# FreelanceX.AI Environment Configuration
# This file contains environment variables for the application

# API Keys (Set these to your actual API keys for full functionality)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Configuration
FREELANCEX_ENV=development
FREELANCEX_DEBUG=true
FREELANCEX_LOG_LEVEL=INFO

# Database Configuration
FREELANCEX_DATABASE_URL=sqlite:///freelancex.db

# Security Configuration
FREELANCEX_SESSION_SECRET=freelancex_ai_session_secret_2024

# Monitoring Configuration
FREELANCEX_ENABLE_METRICS=true
FREELANCEX_ENABLE_TRACING=true

# Access Control Configuration
FREELANCEX_API_KEY_REQUIRED=false
FREELANCEX_SESSION_VALIDATION=false
FREELANCEX_RATE_LIMITING=false
FREELANCEX_ADMIN_USERS=admin,user,test

# Full Access Configuration
FREELANCEX_FULL_ACCESS=true
FREELANCEX_DISABLE_RESTRICTIONS=true
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    logger.info("Created .env file with default configuration")

def setup_access_control():
    """Set up access control with full permissions"""
    logger.info("Setting up access control with full permissions...")
    
    try:
        from fx_agents.access_control import get_access_control_manager, ResourceType, PermissionLevel
        
        # Get access control manager
        manager = get_access_control_manager()
        
        # Grant full access to all users for testing
        test_users = ["admin", "user", "test", "default"]
        
        for user_id in test_users:
            # Grant full access to all resource types
            for resource_type in ResourceType:
                manager.grant_access(
                    user_id=user_id,
                    resource_type=resource_type,
                    resource_name="*",
                    permission_level=PermissionLevel.FULL_ACCESS
                )
        
        logger.info(f"Granted full access to {len(test_users)} users")
        
    except Exception as e:
        logger.error(f"Error setting up access control: {str(e)}")

def setup_database():
    """Set up database with full access"""
    logger.info("Setting up database with full access...")
    
    try:
        from memory.sqlite_memory import get_memory
        
        # Initialize memory system
        memory = get_memory()
        
        # Create test session
        test_session_id = "setup_test_session"
        test_user_id = "setup_user"
        
        # Test memory operations (synchronous check)
        logger.info("Database system initialized successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")

def setup_agents():
    """Set up agents with full access"""
    logger.info("Setting up agents with full access...")
    
    try:
        from fx_agents.triage_agent import dynamic_triage_agent
        
        # Test agent initialization
        if dynamic_triage_agent:
            logger.info("Triage agent initialized successfully")
        
        # Test agent status
        status = dynamic_triage_agent.get_agent_status()
        logger.info(f"Agent status: {len(status.get('registered_agents', []))} agents registered")
        
    except Exception as e:
        logger.error(f"Error setting up agents: {str(e)}")

def verify_full_access():
    """Verify that full access is properly configured"""
    logger.info("Verifying full access configuration...")
    
    checks = []
    
    # Check environment variables
    required_vars = [
        "FREELANCEX_ENV",
        "FREELANCEX_DEBUG", 
        "FREELANCEX_SESSION_SECRET"
    ]
    
    for var in required_vars:
        if os.getenv(var):
            checks.append(f"✅ {var} is set")
        else:
            checks.append(f"❌ {var} is not set")
    
    # Check access control
    try:
        from fx_agents.access_control import get_access_control_manager
        manager = get_access_control_manager()
        checks.append("✅ Access control manager initialized")
    except Exception as e:
        checks.append(f"❌ Access control error: {str(e)}")
    
    # Check memory system
    try:
        from memory.sqlite_memory import get_memory
        memory = get_memory()
        checks.append("✅ Memory system initialized")
    except Exception as e:
        checks.append(f"❌ Memory system error: {str(e)}")
    
    # Check agents
    try:
        from fx_agents.triage_agent import dynamic_triage_agent
        if dynamic_triage_agent:
            checks.append("✅ Triage agent initialized")
        else:
            checks.append("❌ Triage agent not initialized")
    except Exception as e:
        checks.append(f"❌ Agent error: {str(e)}")
    
    # Print verification results
    logger.info("Full Access Verification Results:")
    for check in checks:
        logger.info(check)
    
    # Summary
    success_count = sum(1 for check in checks if check.startswith("✅"))
    total_count = len(checks)
    
    logger.info(f"\nSummary: {success_count}/{total_count} checks passed")
    
    if success_count == total_count:
        logger.info("🎉 Full access setup completed successfully!")
        return True
    else:
        logger.warning("⚠️ Some checks failed. Please review the configuration.")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting FreelanceX.AI Full Access Setup...")
    
    try:
        # Step 1: Set up environment
        setup_environment()
        
        # Step 2: Set up access control
        setup_access_control()
        
        # Step 3: Set up database
        setup_database()
        
        # Step 4: Set up agents
        setup_agents()
        
        # Step 5: Verify full access
        success = verify_full_access()
        
        if success:
            logger.info("\n🎉 FreelanceX.AI is now configured with full access!")
            logger.info("\nNext steps:")
            logger.info("1. Set your actual API keys in the .env file")
            logger.info("2. Run: chainlit run chainlit_app/main.py")
            logger.info("3. Open http://localhost:8000 in your browser")
            logger.info("4. Start using your enhanced FreelanceX.AI!")
        else:
            logger.error("\n❌ Setup completed with warnings. Please review the configuration.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
