#!/usr/bin/env python3
"""
Test script for FreelanceX.AI system components

This script tests the basic functionality of all major components
to ensure they can be imported and initialized correctly.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all components can be imported successfully"""
    print("Testing imports...")
    
    try:
        # Test core components
        from core.agent_manager import AgentManager
        from core.user_profile_manager import UserProfileManager
        from core.daily_routines import DailyRoutinesManager
        from core.executive_agent import ExecutiveAgent
        
        # Test agents
        from agents.job_search_agent import JobSearchAgent
        from agents.web_search_agent import WebSearchAgent
        from agents.math_agent import MathAgent
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_user_profile_manager():
    """Test UserProfileManager functionality"""
    print("\nTesting UserProfileManager...")
    
    try:
        from core.user_profile_manager import UserProfileManager
        
        # Create profile manager
        profile_manager = UserProfileManager()
        
        # Test profile creation
        basic_info = {
            'name': 'Test User',
            'email': 'test@example.com',
            'location': 'Test Location'
        }
        user_id = profile_manager.create_profile(basic_info)
        print(f"✅ Created user profile with ID: {user_id}")
        
        # Test skill addition
        skill_data = {
            'name': 'Python',
            'level': 'expert',
            'years_experience': 3.0,
            'proficiency_score': 0.8,
            'is_preferred': True
        }
        skill_id = profile_manager.add_skill(skill_data)
        print(f"✅ Added skill: {skill_id}")
        
        # Test profile summary
        summary = profile_manager.get_profile_summary()
        print(f"✅ Profile summary: {summary['skills_count']} skills")
        
        return True
        
    except Exception as e:
        print(f"❌ UserProfileManager test failed: {e}")
        return False

def test_agents():
    """Test individual agent functionality"""
    print("\nTesting agents...")
    
    try:
        # Test JobSearchAgent
        from agents.job_search_agent import JobSearchAgent
        job_agent = JobSearchAgent()
        print("✅ JobSearchAgent created")
        
        # Test WebSearchAgent
        from agents.web_search_agent import WebSearchAgent
        web_agent = WebSearchAgent()
        print("✅ WebSearchAgent created")
        
        # Test MathAgent
        from agents.math_agent import MathAgent
        math_agent = MathAgent()
        print("✅ MathAgent created")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        return False

async def test_agent_manager():
    """Test AgentManager functionality"""
    print("\nTesting AgentManager...")
    
    try:
        from core.agent_manager import AgentManager
        
        # Create agent manager
        agent_manager = AgentManager()
        print("✅ AgentManager created")
        
        # Test system status
        status = agent_manager.get_system_status()
        print(f"✅ System status: {len(status['agents_online'])} agents online")
        
        return True
        
    except Exception as e:
        print(f"❌ AgentManager test failed: {e}")
        return False

async def test_daily_routines():
    """Test DailyRoutinesManager functionality"""
    print("\nTesting DailyRoutinesManager...")
    
    try:
        from core.daily_routines import DailyRoutinesManager
        from core.agent_manager import AgentManager
        from core.user_profile_manager import UserProfileManager
        
        # Create dependencies
        profile_manager = UserProfileManager()
        agent_manager = AgentManager()
        
        # Create routines manager
        routines_manager = DailyRoutinesManager(agent_manager, profile_manager)
        print("✅ DailyRoutinesManager created")
        
        # Test routine statistics
        stats = routines_manager.get_routine_statistics()
        print(f"✅ Routine statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ DailyRoutinesManager test failed: {e}")
        return False

async def test_main_application():
    """Test the main FreelanceX.AI application"""
    print("\nTesting main application...")
    
    try:
        from main import FreelanceXAI
        
        # Create application
        app = FreelanceXAI()
        print("✅ FreelanceX.AI application created")
        
        # Test initialization
        await app.initialize()
        print("✅ Application initialized")
        
        # Test system status
        status = await app.get_system_status()
        print(f"✅ System status: {status['is_running']}")
        
        # Test shutdown
        await app.shutdown()
        print("✅ Application shutdown")
        
        return True
        
    except Exception as e:
        print(f"❌ Main application test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("FREELANCEX.AI SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("UserProfileManager Test", test_user_profile_manager),
        ("Agents Test", test_agents),
        ("AgentManager Test", test_agent_manager),
        ("DailyRoutines Test", test_daily_routines),
        ("Main Application Test", test_main_application),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! FreelanceX.AI is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Run all tests
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n🚀 You can now run the demo with: python main.py --demo")
    else:
        print("\n❌ Please fix the failing tests before running the application.")
    
    sys.exit(0 if success else 1)