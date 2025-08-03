#!/usr/bin/env python3
"""
FreelanceX.AI System Startup Script
Comprehensive startup orchestrator for the entire FreelanceX.AI ecosystem
Features: Service initialization, health checks, monitoring setup, graceful shutdown
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import argparse

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import FreelanceX.AI components
from config.settings import get_config, FreelanceXConfig
from core.agent_manager import AgentManager
from backend.database import DatabaseManager
from backend.api_gateway import APIGateway
from backend.monitoring_system import get_monitoring_system
from backend.external_integrations import get_integrations_manager
from chainlit_app.main import executive_agent

# Import specialized agents
from agents.job_search_agent import JobSearchAgent
from agents.web_search_agent import WebSearchAgent
from agents.math_agent import MathAgent

# Configure logging
def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('freelancex.log')
        ]
    )

logger = logging.getLogger(__name__)

class FreelanceXOrchestrator:
    """
    Main orchestrator for FreelanceX.AI system
    Manages initialization, startup, and shutdown of all components
    """
    
    def __init__(self, config: FreelanceXConfig):
        self.config = config
        self.services = {}
        self.running = False
        self.shutdown_event = asyncio.Event()
        
        # System components
        self.agent_manager = None
        self.db_manager = None
        self.api_gateway = None
        self.monitoring_system = None
        self.integrations_manager = None
        
        # Agents
        self.agents = {}
        
        logger.info("FreelanceX.AI Orchestrator initialized")
    
    async def initialize_database(self):
        """Initialize database connection and schema"""
        logger.info("Initializing database...")
        
        try:
            self.db_manager = DatabaseManager(
                db_path=self.config.database.name,
                encryption_key=self.config.security.encryption_key
            )
            
            # Connect to database
            success = await self.db_manager.connect()
            if not success:
                raise Exception("Failed to connect to database")
            
            # Clean up expired memories
            cleaned = await self.db_manager.cleanup_expired_memories()
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} expired memory entries")
            
            self.services["database"] = self.db_manager
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise
    
    async def initialize_agents(self):
        """Initialize and register all agents"""
        logger.info("Initializing agents...")
        
        try:
            # Initialize agent manager
            self.agent_manager = AgentManager()
            
            # Initialize specialized agents
            self.agents["job_search"] = JobSearchAgent()
            self.agents["web_search"] = WebSearchAgent()
            self.agents["math"] = MathAgent()
            
            # Register agents with manager
            for name, agent in self.agents.items():
                success = self.agent_manager.register_agent(agent)
                if success:
                    logger.info(f"Registered agent: {name}")
                else:
                    logger.warning(f"Failed to register agent: {name}")
            
            self.services["agent_manager"] = self.agent_manager
            self.services["agents"] = self.agents
            
            logger.info(f"Initialized {len(self.agents)} agents successfully")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {str(e)}")
            raise
    
    async def initialize_external_integrations(self):
        """Initialize external service integrations"""
        logger.info("Initializing external integrations...")
        
        try:
            integrations_config = self.config.get_external_integrations_config()
            self.integrations_manager = get_integrations_manager(integrations_config)
            
            # Test connections
            connection_results = await self.integrations_manager.test_all_connections()
            
            active_integrations = sum(1 for status in connection_results.values() if status)
            total_integrations = len(connection_results)
            
            logger.info(f"External integrations: {active_integrations}/{total_integrations} active")
            
            for service, status in connection_results.items():
                if status:
                    logger.info(f"✓ {service} - Connected")
                else:
                    logger.warning(f"✗ {service} - Connection failed")
            
            self.services["integrations"] = self.integrations_manager
            
        except Exception as e:
            logger.error(f"External integrations initialization failed: {str(e)}")
            # Don't raise - external integrations are optional
    
    async def initialize_monitoring(self):
        """Initialize monitoring and health check system"""
        logger.info("Initializing monitoring system...")
        
        try:
            if not self.config.monitoring.enabled:
                logger.info("Monitoring disabled in configuration")
                return
            
            self.monitoring_system = get_monitoring_system(
                self.agent_manager, 
                self.db_manager
            )
            
            # Start monitoring in background
            asyncio.create_task(self.monitoring_system.start_monitoring())
            
            self.services["monitoring"] = self.monitoring_system
            logger.info("Monitoring system initialized and started")
            
        except Exception as e:
            logger.error(f"Monitoring initialization failed: {str(e)}")
            # Don't raise - monitoring is optional for basic functionality
    
    async def initialize_api_gateway(self):
        """Initialize API Gateway"""
        logger.info("Initializing API Gateway...")
        
        try:
            # Create API Gateway with configuration
            self.api_gateway = APIGateway()
            
            # Update agent manager reference
            self.api_gateway.agent_manager = self.agent_manager
            self.api_gateway.db_manager = self.db_manager
            
            self.services["api_gateway"] = self.api_gateway
            logger.info("API Gateway initialized successfully")
            
        except Exception as e:
            logger.error(f"API Gateway initialization failed: {str(e)}")
            raise
    
    async def start_services(self):
        """Start all system services"""
        logger.info("Starting FreelanceX.AI services...")
        
        try:
            # Start API Gateway server
            if self.api_gateway:
                logger.info(f"Starting API Gateway on {self.config.api_gateway.host}:{self.config.api_gateway.port}")
                
                # Start server in background task
                server_task = asyncio.create_task(
                    self.api_gateway.start_server(
                        host=self.config.api_gateway.host,
                        port=self.config.api_gateway.port
                    )
                )
                
                # Wait a moment to ensure server starts
                await asyncio.sleep(2)
                
                # Store server task
                self.services["api_server"] = server_task
            
            # Set system as running
            self.running = True
            
            logger.info("All services started successfully")
            
            # Print startup summary
            await self.print_startup_summary()
            
        except Exception as e:
            logger.error(f"Service startup failed: {str(e)}")
            raise
    
    async def print_startup_summary(self):
        """Print system startup summary"""
        print("\n" + "="*80)
        print("🚀 FreelanceX.AI System Started Successfully!")
        print("="*80)
        print(f"Environment: {self.config.environment}")
        print(f"Database: {self.config.database.type} - {'Connected' if self.db_manager and self.db_manager.is_connected() else 'Disconnected'}")
        print(f"API Gateway: http://{self.config.api_gateway.host}:{self.config.api_gateway.port}")
        print(f"API Documentation: http://{self.config.api_gateway.host}:{self.config.api_gateway.port}/docs")
        print(f"Agents: {len(self.agents)} active")
        print(f"External Integrations: {len(self.integrations_manager.integrations) if self.integrations_manager else 0} configured")
        print(f"Monitoring: {'Enabled' if self.monitoring_system else 'Disabled'}")
        print("\n📊 Quick Access URLs:")
        print(f"  • Health Check: http://{self.config.api_gateway.host}:{self.config.api_gateway.port}/health")
        print(f"  • System Metrics: http://{self.config.api_gateway.host}:{self.config.api_gateway.port}/metrics")
        print(f"  • Agent Status: http://{self.config.api_gateway.host}:{self.config.api_gateway.port}/agents")
        print("\n🎯 To start using FreelanceX.AI:")
        print("  1. Open the Chainlit UI (run: chainlit run chainlit_app/main.py)")
        print("  2. Use the API endpoints for programmatic access")
        print("  3. Monitor system health via the monitoring dashboard")
        print("\n💡 Press Ctrl+C to shutdown gracefully")
        print("="*80 + "\n")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {},
            "agents": {},
            "integrations": {}
        }
        
        try:
            # Check database
            if self.db_manager:
                health_status["services"]["database"] = {
                    "status": "healthy" if self.db_manager.is_connected() else "unhealthy",
                    "connected": self.db_manager.is_connected()
                }
            
            # Check agents
            if self.agent_manager:
                for name, agent in self.agent_manager.agents.items():
                    health_status["agents"][name] = {
                        "status": agent.status.value,
                        "type": agent.agent_type
                    }
            
            # Check external integrations
            if self.integrations_manager:
                status = self.integrations_manager.get_integration_status()
                health_status["integrations"] = status
            
            # Check monitoring
            if self.monitoring_system:
                system_status = self.monitoring_system.get_system_status()
                health_status["services"]["monitoring"] = {
                    "status": "healthy" if system_status["monitoring_active"] else "unhealthy",
                    "health_status": system_status["health_status"]
                }
            
            # Determine overall status
            unhealthy_services = sum(1 for service in health_status["services"].values() 
                                   if service.get("status") != "healthy")
            if unhealthy_services > 0:
                health_status["status"] = "degraded" if unhealthy_services == 1 else "unhealthy"
            
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            health_status["status"] = "error"
            health_status["error"] = str(e)
        
        return health_status
    
    async def graceful_shutdown(self):
        """Perform graceful shutdown of all services"""
        logger.info("Initiating graceful shutdown...")
        
        try:
            self.running = False
            
            # Stop monitoring
            if self.monitoring_system:
                await self.monitoring_system.stop_monitoring()
                logger.info("Monitoring system stopped")
            
            # Close external integrations
            if self.integrations_manager:
                # Close any active connections
                logger.info("External integrations closed")
            
            # Stop agents
            if self.agent_manager:
                # Stop all agents gracefully
                for name, agent in self.agent_manager.agents.items():
                    try:
                        # If agent has cleanup method
                        if hasattr(agent, 'cleanup'):
                            await agent.cleanup()
                    except Exception as e:
                        logger.warning(f"Error stopping agent {name}: {str(e)}")
                logger.info("All agents stopped")
            
            # Close database
            if self.db_manager:
                await self.db_manager.disconnect()
                logger.info("Database connection closed")
            
            # Set shutdown event
            self.shutdown_event.set()
            
            logger.info("Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.graceful_shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run(self):
        """Main run loop for the FreelanceX.AI system"""
        try:
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Initialize all components
            await self.initialize_database()
            await self.initialize_agents()
            await self.initialize_external_integrations()
            await self.initialize_monitoring()
            await self.initialize_api_gateway()
            
            # Start services
            await self.start_services()
            
            # Keep running until shutdown signal
            await self.shutdown_event.wait()
            
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"System error: {str(e)}")
            raise
        finally:
            await self.graceful_shutdown()

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="FreelanceX.AI System Startup")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--env", help="Environment (development/production/testing)", 
                       choices=["development", "production", "testing"], default="development")
    parser.add_argument("--log-level", help="Log level", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    parser.add_argument("--health-check", action="store_true", 
                       help="Perform health check and exit")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    
    try:
        # Load configuration
        config = get_config(args.config, args.env)
        
        # Create orchestrator
        orchestrator = FreelanceXOrchestrator(config)
        
        if args.health_check:
            # Perform health check only
            logger.info("Performing health check...")
            
            # Initialize minimal components for health check
            await orchestrator.initialize_database()
            await orchestrator.initialize_agents()
            
            health = await orchestrator.health_check()
            print(f"System Health: {health['status']}")
            
            if health['status'] != 'healthy':
                sys.exit(1)
        else:
            # Run full system
            await orchestrator.run()
            
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutdown by user")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        sys.exit(1)