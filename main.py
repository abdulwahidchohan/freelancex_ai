#!/usr/bin/env python3
"""
FreelanceX.AI - World-Class AI Assistant Platform for Freelancers
Main entry point with executive agent coordination and multimodal support

Author: Abdul Wahid Chohan
Mission: Build legendary tech that empowers freelancers worldwide
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from core.agent_manager import AgentManager
from core.dispatcher import TaskDispatcher
from core.config import Config
from agents.executive_agent import ExecutiveAgent
from memory.sqlite_memory import MemoryManager
from tools.control_panel import ControlPanel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('freelancex_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FreelanceXAI:
    """
    Main FreelanceX.AI system orchestrator
    Coordinates agents, tools, and memory for seamless freelancer assistance
    """
    
    def __init__(self):
        self.config = Config()
        self.agent_manager = AgentManager()
        self.dispatcher = TaskDispatcher()
        self.memory_manager = MemoryManager()
        self.control_panel = ControlPanel()
        self.executive_agent = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("🚀 Initializing FreelanceX.AI...")
            
            # Load configuration
            await self.config.load()
            
            # Initialize memory system
            await self.memory_manager.initialize()
            
            # Initialize executive agent
            self.executive_agent = ExecutiveAgent(
                agent_manager=self.agent_manager,
                memory_manager=self.memory_manager,
                config=self.config
            )
            
            # Register all agents
            await self._register_agents()
            
            # Initialize control panel
            await self.control_panel.initialize()
            
            logger.info("✅ FreelanceX.AI initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {str(e)}")
            return False
    
    async def _register_agents(self):
        """Register all specialized agents"""
        from agents.job_search_agent import JobSearchAgent
        from agents.proposal_writer_agent import ProposalWriterAgent
        from agents.planning_agent import PlanningAgent
        from agents.invoice_agent import InvoiceAgent
        from agents.client_agent import ClientAgent
        
        agents = [
            JobSearchAgent(),
            ProposalWriterAgent(),
            PlanningAgent(),
            InvoiceAgent(),
            ClientAgent()
        ]
        
        for agent in agents:
            await self.agent_manager.register_agent(agent)
            logger.info(f"📋 Registered agent: {agent.name}")
    
    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process multimodal input (text, voice, image) and route to appropriate agents
        
        Args:
            input_data: Dict containing input type and content
                - type: 'text', 'voice', 'image'
                - content: The actual input data
                - user_id: User identifier
                - context: Additional context
        """
        try:
            # Log input for memory
            await self.memory_manager.log_interaction(
                user_id=input_data.get('user_id', 'default'),
                input_type=input_data['type'],
                content=input_data['content'],
                timestamp=datetime.now().isoformat()
            )
            
            # Route to executive agent for task determination
            task_analysis = await self.executive_agent.analyze_task(input_data)
            
            # Dispatch to appropriate specialized agent
            result = await self.dispatcher.dispatch_task(task_analysis)
            
            # Store result in memory
            await self.memory_manager.log_interaction(
                user_id=input_data.get('user_id', 'default'),
                input_type='response',
                content=result,
                timestamp=datetime.now().isoformat()
            )
            
            return {
                'success': True,
                'result': result,
                'task_type': task_analysis.get('task_type'),
                'agent_used': task_analysis.get('agent_name')
            }
            
        except Exception as e:
            logger.error(f"Error processing input: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'result': None
            }
    
    async def start(self):
        """Start the FreelanceX.AI system"""
        if not await self.initialize():
            logger.error("Failed to initialize system")
            return False
        
        self.is_running = True
        logger.info("🎯 FreelanceX.AI is now running and ready to assist!")
        
        # Start background tasks
        asyncio.create_task(self._background_tasks())
        
        return True
    
    async def _background_tasks(self):
        """Run background tasks like monitoring and maintenance"""
        while self.is_running:
            try:
                # Health check
                await self.control_panel.health_check()
                
                # Memory cleanup
                await self.memory_manager.cleanup_old_data()
                
                # Wait before next cycle
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                logger.error(f"Background task error: {str(e)}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the FreelanceX.AI system"""
        self.is_running = False
        logger.info("🛑 FreelanceX.AI shutting down...")
        
        # Cleanup
        await self.memory_manager.close()
        await self.control_panel.shutdown()

# Global instance
freelancex_ai = FreelanceXAI()

async def main():
    """Main entry point"""
    try:
        # Start the system
        success = await freelancex_ai.start()
        
        if success:
            # Keep the system running
            while freelancex_ai.is_running:
                await asyncio.sleep(1)
        else:
            logger.error("Failed to start FreelanceX.AI")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        await freelancex_ai.stop()

if __name__ == "__main__":
    # Run the main event loop
    asyncio.run(main()) 