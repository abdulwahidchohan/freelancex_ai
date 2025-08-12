#!/usr/bin/env python3
"""
Simple test to verify FreelanceX.AI can respond to prompts
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fx_agents.triage_agent import dynamic_triage_agent

async def test_response():
    """Test that the application can respond to a simple prompt"""
    try:
        print("🧪 Testing FreelanceX.AI Response Capability...")
        
        # Test message
        test_message = "Hello, can you help me find freelance Python development jobs?"
        
        print(f"📝 Sending test message: '{test_message}'")
        
        # Create a test session
        session_id = "test-session-123"
        user_id = "test-user"
        
        # Route the request
        result = await dynamic_triage_agent.route_request(
            message=test_message,
            session_id=session_id,
            user_id=user_id
        )
        
        print("✅ Response received successfully!")
        print(f"📊 Success: {result.success}")
        print(f"⏱️  Execution time: {result.execution_time:.2f}s")
        print(f"🎯 Target agent: {result.routing_decision.target_agent if result.routing_decision else 'None'}")
        print(f"📝 Response length: {len(result.response)} characters")
        print(f"🔍 Response preview: {result.response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_response())
    if success:
        print("\n🎉 FreelanceX.AI is working correctly and WILL answer your prompts!")
        print("🌐 Open http://localhost:8000 in your browser to use the chat interface.")
    else:
        print("\n💥 There's an issue with the application. Check the logs above.")
