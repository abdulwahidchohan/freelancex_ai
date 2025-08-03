#!/usr/bin/env python3
"""
FreelanceX.AI System Test
Comprehensive test script to verify all system components
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import FreelanceXAI
from core.user_profile_manager import Skill, SkillLevel, WorkHistory, LearningGoal
from agents.math_agent import MathProblem, MathProblemType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_user_profile_manager():
    """Test user profile management functionality"""
    print("\n🧪 Testing User Profile Manager...")
    
    from core.user_profile_manager import UserProfileManager
    
    # Initialize profile manager
    profile_manager = UserProfileManager("test_user_001")
    
    # Test personal info update
    personal_info = {
        "name": "Test User",
        "email": "test@example.com",
        "location": "Test City, TC",
        "bio": "Experienced freelancer"
    }
    
    success = await profile_manager.update_personal_info(personal_info)
    print(f"✅ Personal info update: {'PASS' if success else 'FAIL'}")
    
    # Test skill addition
    skill = Skill(
        name="Python",
        level=SkillLevel.ADVANCED,
        years_experience=3.5,
        last_used=datetime.now(),
        confidence_score=0.85,
        certifications=["Python Developer"],
        projects_count=15
    )
    
    success = await profile_manager.add_skill(skill)
    print(f"✅ Skill addition: {'PASS' if success else 'FAIL'}")
    
    # Test work history
    work_history = WorkHistory(
        project_id="proj_001",
        title="AI Chatbot Development",
        description="Built a conversational AI chatbot",
        client="TechCorp",
        platform="Upwork",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now() - timedelta(days=5),
        budget=5000,
        skills_used=["Python", "Machine Learning", "NLP"],
        rating=4.8,
        feedback="Excellent work, highly recommended!",
        status="completed"
    )
    
    success = await profile_manager.add_work_history(work_history)
    print(f"✅ Work history addition: {'PASS' if success else 'FAIL'}")
    
    # Test learning goal
    learning_goal = LearningGoal(
        goal_id="goal_001",
        skill_name="React",
        target_level=SkillLevel.INTERMEDIATE,
        target_date=datetime.now() + timedelta(days=90),
        current_progress=0.3,
        learning_resources=["Udemy Course", "React Docs"],
        status="active"
    )
    
    success = await profile_manager.add_learning_goal(learning_goal)
    print(f"✅ Learning goal addition: {'PASS' if success else 'FAIL'}")
    
    # Test profile summary
    summary = await profile_manager.get_profile_summary()
    print(f"✅ Profile summary: {'PASS' if summary else 'FAIL'}")
    
    # Test recommendations
    recommendations = await profile_manager.get_personalized_recommendations()
    print(f"✅ Recommendations: {'PASS' if recommendations else 'FAIL'}")
    
    return True

async def test_job_search_agent():
    """Test job search agent functionality"""
    print("\n🔍 Testing Job Search Agent...")
    
    from agents.job_search_agent import JobSearchAgent
    
    # Initialize with test profile
    test_profile = {
        "skills": ["Python", "Machine Learning"],
        "min_hourly_rate": 50,
        "max_hourly_rate": 100,
        "preferred_job_types": ["fixed_price", "hourly"],
        "experience_level": "intermediate",
        "location_preference": "remote"
    }
    
    job_agent = JobSearchAgent(test_profile)
    
    # Test job search
    jobs = await job_agent.search_jobs(
        keywords=["Python", "AI"],
        budget_range={"min": 5000, "max": 15000}
    )
    
    print(f"✅ Job search: {'PASS' if jobs else 'FAIL'} (Found {len(jobs)} jobs)")
    
    # Test daily digest
    digest = await job_agent.get_daily_job_digest()
    print(f"✅ Daily digest: {'PASS' if digest else 'FAIL'}")
    
    return True

async def test_web_search_agent():
    """Test web search agent functionality"""
    print("\n📚 Testing Web Search Agent...")
    
    from agents.web_search_agent import WebSearchAgent, SearchType
    
    # Initialize with test profile
    test_profile = {
        "skills": ["Python", "Machine Learning"],
        "experience_level": "intermediate"
    }
    
    web_agent = WebSearchAgent(test_profile)
    
    # Test research
    research = await web_agent.conduct_research(
        topic="AI tools for freelancers",
        search_type=SearchType.AI_TOOLS
    )
    
    print(f"✅ Research: {'PASS' if research else 'FAIL'}")
    
    # Test trending topics
    topics = await web_agent.get_trending_topics()
    print(f"✅ Trending topics: {'PASS' if topics else 'FAIL'}")
    
    return True

async def test_math_agent():
    """Test math agent functionality"""
    print("\n🧮 Testing Math Agent...")
    
    from agents.math_agent import MathAgent
    
    # Initialize with test profile
    test_profile = {
        "skills": ["Python", "Mathematics"],
        "experience_level": "intermediate"
    }
    
    math_agent = MathAgent(test_profile)
    
    # Test arithmetic problem
    arithmetic_problem = MathProblem(
        problem_id="math_001",
        problem_type=MathProblemType.ARITHMETIC,
        description="Calculate monthly income",
        input_data={"expression": "5000 + 3000 + 2000"},
        complexity="easy",
        context="Income calculation"
    )
    
    solution = await math_agent.solve_math_problem(arithmetic_problem)
    print(f"✅ Arithmetic problem: {'PASS' if solution.confidence > 0 else 'FAIL'}")
    
    # Test financial analysis
    financial_data = {
        "income": [5000, 6000, 4500, 7000, 5500],
        "expenses": {"software": 200, "marketing": 300, "office": 150}
    }
    
    analysis = await math_agent.conduct_financial_analysis("income_analysis", financial_data)
    print(f"✅ Financial analysis: {'PASS' if analysis else 'FAIL'}")
    
    return True

async def test_agent_collaboration():
    """Test agent collaboration system"""
    print("\n🤝 Testing Agent Collaboration...")
    
    from core.agent_collaboration import AgentCollaborationManager, TaskPriority
    
    # Initialize collaboration manager
    collaboration_manager = AgentCollaborationManager()
    
    # Test task submission
    task_id = await collaboration_manager.submit_task(
        task_type="job_search",
        description="Search for Python development jobs",
        priority=TaskPriority.HIGH,
        metadata={"keywords": ["Python"], "budget_range": {"min": 5000, "max": 15000}}
    )
    
    print(f"✅ Task submission: {'PASS' if task_id else 'FAIL'}")
    
    # Test system status
    status = await collaboration_manager.get_system_status()
    print(f"✅ System status: {'PASS' if status else 'FAIL'}")
    
    return True

async def test_main_application():
    """Test main FreelanceX.AI application"""
    print("\n🚀 Testing Main FreelanceX.AI Application...")
    
    # Initialize FreelanceX.AI
    freelancex = FreelanceXAI("test_user_002")
    
    # Test initialization
    success = await freelancex.initialize()
    print(f"✅ Application initialization: {'PASS' if success else 'FAIL'}")
    
    if success:
        # Test job search
        jobs = await freelancex.search_jobs(
            keywords=["Python", "Machine Learning"],
            budget_range={"min": 5000, "max": 20000}
        )
        print(f"✅ Main job search: {'PASS' if jobs else 'FAIL'} (Found {len(jobs)} jobs)")
        
        # Test research
        research = await freelancex.conduct_research(
            topic="AI tools for freelancers",
            research_type="ai_tools"
        )
        print(f"✅ Main research: {'PASS' if research else 'FAIL'}")
        
        # Test financial analysis
        financial_data = {
            "income": [5000, 6000, 4500, 7000, 5500],
            "expenses": {"software": 200, "marketing": 300, "office": 150}
        }
        analysis = await freelancex.conduct_financial_analysis("income_analysis", financial_data)
        print(f"✅ Main financial analysis: {'PASS' if analysis else 'FAIL'}")
        
        # Test daily digest
        digest = await freelancex.get_daily_digest()
        print(f"✅ Main daily digest: {'PASS' if digest else 'FAIL'}")
        
        # Test system status
        status = await freelancex.get_system_status()
        print(f"✅ Main system status: {'PASS' if status else 'FAIL'}")
    
    return success

async def run_all_tests():
    """Run all system tests"""
    print("🧪 Starting FreelanceX.AI System Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run individual component tests
    test_results.append(await test_user_profile_manager())
    test_results.append(await test_job_search_agent())
    test_results.append(await test_web_search_agent())
    test_results.append(await test_math_agent())
    test_results.append(await test_agent_collaboration())
    test_results.append(await test_main_application())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! FreelanceX.AI is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the implementation.")
        return False

async def main():
    """Main test function"""
    try:
        success = await run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())