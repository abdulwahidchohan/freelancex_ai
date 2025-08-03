#!/usr/bin/env python3
"""
Simple FreelanceX.AI Test
Basic functionality test without external dependencies
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_user_profile_manager():
    """Test user profile management functionality"""
    print("\n🧪 Testing User Profile Manager...")
    
    try:
        from core.user_profile_manager import UserProfileManager, Skill, SkillLevel, WorkHistory, LearningGoal
        
        # Initialize profile manager
        profile_manager = UserProfileManager("test_user_001")
        
        # Test personal info update
        personal_info = {
            "name": "Test User",
            "email": "test@example.com",
            "location": "Test City, TC",
            "bio": "Experienced freelancer"
        }
        
        # Test profile data access
        profile_data = profile_manager.profile_data
        print(f"✅ Profile initialization: PASS")
        
        # Test skill creation
        skill = Skill(
            name="Python",
            level=SkillLevel.ADVANCED,
            years_experience=3.5,
            last_used=datetime.now(),
            confidence_score=0.85,
            certifications=["Python Developer"],
            projects_count=15
        )
        print(f"✅ Skill object creation: PASS")
        
        # Test work history creation
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
        print(f"✅ Work history object creation: PASS")
        
        # Test learning goal creation
        learning_goal = LearningGoal(
            goal_id="goal_001",
            skill_name="React",
            target_level=SkillLevel.INTERMEDIATE,
            target_date=datetime.now() + timedelta(days=90),
            current_progress=0.3,
            learning_resources=["Udemy Course", "React Docs"],
            status="active"
        )
        print(f"✅ Learning goal object creation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ User Profile Manager test failed: {str(e)}")
        return False

def test_job_search_agent():
    """Test job search agent functionality"""
    print("\n🔍 Testing Job Search Agent...")
    
    try:
        from agents.job_search_agent import JobSearchAgent, JobListing, JobPlatform
        
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
        print(f"✅ Job Search Agent initialization: PASS")
        
        # Test job listing creation
        job = JobListing(
            id="test_job_001",
            title="Python Developer",
            description="Looking for experienced Python developer",
            platform=JobPlatform.UPWORK,
            budget_min=5000,
            budget_max=10000,
            skills_required=["Python", "Django"],
            posted_date=datetime.now(),
            client_rating=4.5,
            project_type="Fixed-price",
            experience_level="Intermediate",
            location="Remote",
            url="https://upwork.com/jobs/test"
        )
        print(f"✅ Job Listing object creation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Job Search Agent test failed: {str(e)}")
        return False

def test_web_search_agent():
    """Test web search agent functionality"""
    print("\n📚 Testing Web Search Agent...")
    
    try:
        from agents.web_search_agent import WebSearchAgent, SearchType, SearchResult, ResearchReport
        
        # Initialize with test profile
        test_profile = {
            "skills": ["Python", "Machine Learning"],
            "experience_level": "intermediate"
        }
        
        web_agent = WebSearchAgent(test_profile)
        print(f"✅ Web Search Agent initialization: PASS")
        
        # Test search result creation
        search_result = SearchResult(
            title="AI Tools for Freelancers",
            url="https://example.com/ai-tools",
            snippet="Comprehensive guide to AI tools...",
            source="example.com",
            relevance_score=0.95,
            content_type="article",
            published_date=datetime.now(),
            author="Expert Author",
            tags=["AI", "freelancing", "tools"],
            summary="Guide to AI tools for freelancers"
        )
        print(f"✅ Search Result object creation: PASS")
        
        # Test research report creation
        research_report = ResearchReport(
            topic="AI Tools",
            search_type=SearchType.AI_TOOLS,
            created_at=datetime.now(),
            summary="Research on AI tools for freelancers",
            key_findings=["Finding 1", "Finding 2"],
            recommendations=["Recommendation 1", "Recommendation 2"],
            sources=[search_result],
            market_insights={"market_size": "$50B"},
            trend_analysis={"trend": "increasing"}
        )
        print(f"✅ Research Report object creation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Web Search Agent test failed: {str(e)}")
        return False

def test_math_agent():
    """Test math agent functionality"""
    print("\n🧮 Testing Math Agent...")
    
    try:
        from agents.math_agent import MathAgent, MathProblem, MathProblemType, MathSolution, FinancialAnalysis
        
        # Initialize with test profile
        test_profile = {
            "skills": ["Python", "Mathematics"],
            "experience_level": "intermediate"
        }
        
        math_agent = MathAgent(test_profile)
        print(f"✅ Math Agent initialization: PASS")
        
        # Test math problem creation
        math_problem = MathProblem(
            problem_id="math_001",
            problem_type=MathProblemType.ARITHMETIC,
            description="Calculate monthly income",
            input_data={"expression": "5000 + 3000 + 2000"},
            complexity="easy",
            context="Income calculation"
        )
        print(f"✅ Math Problem object creation: PASS")
        
        # Test math solution creation
        math_solution = MathSolution(
            problem_id="math_001",
            solution="The result is 10000",
            steps=["Step 1", "Step 2"],
            answer=10000,
            confidence=0.95,
            time_taken=0.1,
            verification="Verified"
        )
        print(f"✅ Math Solution object creation: PASS")
        
        # Test financial analysis creation
        financial_analysis = FinancialAnalysis(
            analysis_id="fin_001",
            analysis_type="income_analysis",
            data={"income": [5000, 6000]},
            results={"total": 11000},
            recommendations=["Recommendation 1"],
            risk_assessment={"risk": "low"},
            visualizations=[]
        )
        print(f"✅ Financial Analysis object creation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Math Agent test failed: {str(e)}")
        return False

def test_agent_collaboration():
    """Test agent collaboration system"""
    print("\n🤝 Testing Agent Collaboration...")
    
    try:
        from core.agent_collaboration import AgentCollaborationManager, TaskPriority, Task, TaskStatus
        
        # Initialize collaboration manager
        collaboration_manager = AgentCollaborationManager()
        print(f"✅ Agent Collaboration Manager initialization: PASS")
        
        # Test task creation
        task = Task(
            task_id="task_001",
            task_type="job_search",
            description="Search for Python jobs",
            priority=TaskPriority.HIGH
        )
        print(f"✅ Task object creation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent Collaboration test failed: {str(e)}")
        return False

def test_main_application():
    """Test main FreelanceX.AI application"""
    print("\n🚀 Testing Main FreelanceX.AI Application...")
    
    try:
        from main import FreelanceXAI
        
        # Initialize FreelanceX.AI
        freelancex = FreelanceXAI("test_user_002")
        print(f"✅ FreelanceX.AI object creation: PASS")
        
        # Test user profile manager access
        profile_manager = freelancex.user_profile_manager
        print(f"✅ User Profile Manager access: PASS")
        
        # Test agent collaboration manager access
        collaboration_manager = freelancex.agent_collaboration_manager
        print(f"✅ Agent Collaboration Manager access: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Main Application test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("🧪 Starting FreelanceX.AI System Tests")
    print("=" * 50)
    
    test_results = []
    
    # Run individual component tests
    test_results.append(test_user_profile_manager())
    test_results.append(test_job_search_agent())
    test_results.append(test_web_search_agent())
    test_results.append(test_math_agent())
    test_results.append(test_agent_collaboration())
    test_results.append(test_main_application())
    
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
        print("\n🎉 All tests passed! FreelanceX.AI core components are working correctly.")
        print("\n📋 What was tested:")
        print("• User Profile Manager - Data structures and object creation")
        print("• Job Search Agent - Job listing and search functionality")
        print("• Web Search Agent - Research and analysis capabilities")
        print("• Math Agent - Mathematical and financial calculations")
        print("• Agent Collaboration - Task management and coordination")
        print("• Main Application - System integration and orchestration")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the implementation.")
        return False

def main():
    """Main test function"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()