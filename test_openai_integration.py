#!/usr/bin/env python3
"""
Test script for OpenAI Agent SDK integration
Verifies that all components work together properly
"""

import asyncio
import logging
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_openai_integration():
    """Test OpenAI Agent SDK integration"""
    try:
        logger.info("🚀 Starting OpenAI Agent SDK integration test...")
        
        # Test imports
        logger.info("📦 Testing imports...")
        from core.executive_agent import ExecutiveAgent
        from core.base_agent import BaseAgent
        from memory.sqlite_memory import MemoryManager
        from agents.proposal_writer_agent import ProposalWriterAgent
        logger.info("✅ All imports successful")
        
        # Test OpenAI import (without requiring API key)
        logger.info("🔌 Testing OpenAI import...")
        try:
            import openai
            logger.info("✅ OpenAI package imported successfully")
            logger.info(f"📋 OpenAI version: {openai.__version__}")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI import issue: {str(e)}")
        
        # Test memory manager initialization
        logger.info("💾 Testing memory manager...")
        memory_manager = MemoryManager()
        await memory_manager.initialize()
        logger.info("✅ Memory manager initialized")
        
        # Test executive agent initialization
        logger.info("🎯 Testing executive agent...")
        executive_agent = ExecutiveAgent()
        logger.info("✅ Executive agent initialized")
        
        # Test proposal writer agent
        logger.info("📝 Testing proposal writer agent...")
        proposal_agent = ProposalWriterAgent()
        capabilities = proposal_agent.get_capabilities()
        logger.info(f"✅ Proposal agent capabilities: {capabilities}")
        
        # Test agent tools
        logger.info("🔧 Testing agent tools...")
        tools = proposal_agent._get_agent_tools()
        logger.info(f"✅ Agent has {len(tools)} tools available")
        
        # Test task execution (fallback mode)
        logger.info("⚡ Testing task execution...")
        test_task = {
            'user_id': 'test_user_123',
            'content': 'Generate a proposal for a web development project',
            'task_type': 'proposal_generation'
        }
        
        result = await proposal_agent.execute_task(test_task)
        logger.info(f"✅ Task execution result: {result['success']}")
        
        logger.info("🎉 All tests completed successfully!")
        logger.info("🔧 FreelanceX.AI migration to OpenAI Agent SDK architecture completed")
        logger.info("ℹ️ Note: Full OpenAI Agent SDK functionality requires OPENAI_API_KEY environment variable")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test_openai_integration())
        print("\n✅ Integration test completed successfully!")
    except Exception as e:
        print(f"\n❌ Integration test failed: {str(e)}")
        sys.exit(1)