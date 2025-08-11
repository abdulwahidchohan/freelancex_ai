#!/usr/bin/env python3
"""
Test script to demonstrate FreelanceX.AI agentic capabilities
This script shows how the different agents work together
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fx_agents.triage_agent import route_request
from fx_agents.api_provider import get_api_manager
from config.settings import get_config

async def test_agentic_system():
    """Test the agentic AI system with different types of requests"""
    
    print("🤖 FreelanceX.AI Agentic System Test")
    print("=" * 50)
    
    # Load configuration
    cfg = get_config()
    
    # Initialize API manager
    api_manager = get_api_manager(cfg)
    
    # Test requests
    test_requests = [
        {
            "type": "job_search",
            "content": "Find me remote Python development jobs on Upwork with budgets over $50/hour",
            "description": "Testing JobSearchAgent"
        },
        {
            "type": "proposal_writing", 
            "content": "Write a proposal for a React.js project to build an e-commerce website",
            "description": "Testing ProposalWriterAgent"
        },
        {
            "type": "research",
            "content": "Research the latest trends in AI-powered productivity tools for freelancers",
            "description": "Testing WebResearchAgent"
        },
        {
            "type": "math",
            "content": "Calculate the ROI for a $5000 investment in marketing tools over 6 months",
            "description": "Testing MathAgent"
        },
        {
            "type": "general",
            "content": "Help me optimize my freelance workflow and increase my productivity",
            "description": "Testing TriageAgent routing"
        }
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n🔍 Test {i}: {request['description']}")
        print(f"Request: {request['content']}")
        print("-" * 40)
        
        try:
            # Route the request to the appropriate agent
            response = await route_request(
                request["content"],
                request_type=request["type"],
                api_manager=api_manager
            )
            
            print(f"✅ Response: {response[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print()

async def test_individual_agents():
    """Test individual agents directly"""
    
    print("\n🎯 Testing Individual Agents")
    print("=" * 50)
    
    # Import individual agents
    try:
        from fx_agents.job_search_agent import JobSearchAgent
        from fx_agents.proposal_writer_agent import ProposalWriterAgent
        from fx_agents.web_research_agent import WebResearchAgent
        from fx_agents.math_agent import MathAgent
        
        cfg = get_config()
        api_manager = get_api_manager(cfg)
        
        # Test JobSearchAgent
        print("\n🔍 Testing JobSearchAgent...")
        job_agent = JobSearchAgent(api_manager)
        job_result = await job_agent.search_jobs("Python developer remote")
        print(f"Jobs found: {len(job_result) if job_result else 0}")
        
        # Test MathAgent
        print("\n🧮 Testing MathAgent...")
        math_agent = MathAgent(api_manager)
        math_result = await math_agent.solve_math("What is 25% of 1200?")
        print(f"Math result: {math_result}")
        
    except Exception as e:
        print(f"❌ Error testing individual agents: {str(e)}")

def main():
    """Main test function"""
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  Warning: OPENAI_API_KEY not set or using placeholder")
        print("Please set your OpenAI API key to test the full functionality")
        print("You can set it with: $env:OPENAI_API_KEY='your_actual_key'")
        print()
    
    # Run tests
    asyncio.run(test_agentic_system())
    asyncio.run(test_individual_agents())
    
    print("\n🎉 Agentic AI System Test Complete!")
    print("\nTo use the full interactive system:")
    print("1. Set your OpenAI API key")
    print("2. Run: cd chainlit_app && chainlit run main.py")
    print("3. Open your browser to the provided URL")

if __name__ == "__main__":
    main()

