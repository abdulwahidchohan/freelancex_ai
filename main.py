#!/usr/bin/env python3
"""
FreelanceX.AI - Main Application
The world's most powerful AI Assistant for Freelancers

This application orchestrates all AI agents to provide comprehensive
freelancing support including job search, research, financial analysis,
and personalized recommendations.
"""

import asyncio
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agent_collaboration import AgentCollaborationManager, BaseAgent, Task, TaskPriority
from core.user_profile_manager import UserProfileManager, Skill, SkillLevel, WorkHistory, LearningGoal
from agents.job_search_agent import JobSearchAgent
from agents.web_search_agent import WebSearchAgent, SearchType
from agents.math_agent import MathAgent, MathProblem, MathProblemType
from core.executive_agent import ExecutiveAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('freelancex_ai.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class FreelanceXAI:
    """
    Main FreelanceX.AI application that orchestrates all agents and provides
    a unified interface for freelancers.
    """
    
    def __init__(self, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.logger = logging.getLogger(f"FreelanceXAI_{self.user_id}")
        
        # Initialize core systems
        self.user_profile_manager = UserProfileManager(self.user_id)
        self.agent_collaboration_manager = AgentCollaborationManager()
        self.executive_agent = ExecutiveAgent()
        
        # Initialize specialized agents
        self.job_search_agent = None
        self.web_search_agent = None
        self.math_agent = None
        
        # Application state
        self.is_initialized = False
        self.daily_routines = {}
        self.active_tasks = {}
        
        self.logger.info(f"FreelanceX.AI initialized for user {self.user_id}")
    
    async def initialize(self) -> bool:
        """Initialize the FreelanceX.AI system"""
        try:
            self.logger.info("Initializing FreelanceX.AI system...")
            
            # Get user profile data
            profile_data = await self.user_profile_manager.get_profile_data()
            
            # Initialize specialized agents with user profile
            self.job_search_agent = JobSearchAgent(profile_data)
            self.web_search_agent = WebSearchAgent(profile_data)
            self.math_agent = MathAgent(profile_data)
            
            # Register agents with collaboration manager
            await self._register_agents()
            
            # Set up daily routines
            await self._setup_daily_routines()
            
            # Initialize executive agent
            await self.executive_agent.handle_message("System initialized")
            
            self.is_initialized = True
            self.logger.info("FreelanceX.AI system initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize FreelanceX.AI: {str(e)}")
            return False
    
    async def _register_agents(self):
        """Register all agents with the collaboration manager"""
        # Create agent wrapper classes that inherit from BaseAgent
        class JobSearchAgentWrapper(BaseAgent):
            def __init__(self, agent_id: str, agent_name: str, job_agent: JobSearchAgent):
                super().__init__(agent_id, agent_name)
                self.job_agent = job_agent
                self.capabilities = ["job_search", "job_analysis", "competitive_analysis", "job_alerts"]
            
            async def process_task(self, task: Task) -> Dict[str, Any]:
                if task.task_type == "job_search":
                    return await self.job_agent.search_jobs()
                elif task.task_type == "competitive_analysis":
                    # Extract job data from task metadata
                    job_data = task.metadata.get("job_data")
                    if job_data:
                        return await self.job_agent.get_competitive_analysis(job_data)
                return {"error": "Unsupported task type"}
            
            async def can_handle_task(self, task: Task) -> bool:
                return task.task_type in self.capabilities
        
        class WebSearchAgentWrapper(BaseAgent):
            def __init__(self, agent_id: str, agent_name: str, web_agent: WebSearchAgent):
                super().__init__(agent_id, agent_name)
                self.web_agent = web_agent
                self.capabilities = ["research", "market_analysis", "trend_analysis", "competitive_research"]
            
            async def process_task(self, task: Task) -> Dict[str, Any]:
                if task.task_type == "research":
                    topic = task.metadata.get("topic", "")
                    search_type = SearchType(task.metadata.get("search_type", "business_strategy"))
                    return await self.web_agent.conduct_research(topic, search_type)
                return {"error": "Unsupported task type"}
            
            async def can_handle_task(self, task: Task) -> bool:
                return task.task_type in self.capabilities
        
        class MathAgentWrapper(BaseAgent):
            def __init__(self, agent_id: str, agent_name: str, math_agent: MathAgent):
                super().__init__(agent_id, agent_name)
                self.math_agent = math_agent
                self.capabilities = ["math_calculation", "financial_analysis", "statistical_analysis"]
            
            async def process_task(self, task: Task) -> Dict[str, Any]:
                if task.task_type == "math_calculation":
                    problem_data = task.metadata.get("problem_data")
                    if problem_data:
                        problem = MathProblem(**problem_data)
                        return await self.math_agent.solve_math_problem(problem)
                elif task.task_type == "financial_analysis":
                    analysis_type = task.metadata.get("analysis_type", "")
                    data = task.metadata.get("data", {})
                    return await self.math_agent.conduct_financial_analysis(analysis_type, data)
                return {"error": "Unsupported task type"}
            
            async def can_handle_task(self, task: Task) -> bool:
                return task.task_type in self.capabilities
        
        # Register agents
        self.agent_collaboration_manager.register_agent(
            JobSearchAgentWrapper("job_search_001", "Job Search Agent", self.job_search_agent)
        )
        self.agent_collaboration_manager.register_agent(
            WebSearchAgentWrapper("web_search_001", "Web Search Agent", self.web_search_agent)
        )
        self.agent_collaboration_manager.register_agent(
            MathAgentWrapper("math_001", "Math Agent", self.math_agent)
        )
        
        self.logger.info("All agents registered with collaboration manager")
    
    async def _setup_daily_routines(self):
        """Set up daily routines for freelancers"""
        self.daily_routines = {
            "morning": [
                "job_market_analysis",
                "daily_job_digest",
                "market_trends_research"
            ],
            "work_session": [
                "job_search_alerts",
                "financial_calculations",
                "skill_development_check"
            ],
            "evening": [
                "daily_summary",
                "performance_analysis",
                "next_day_planning"
            ]
        }
        
        self.logger.info("Daily routines configured")
    
    async def search_jobs(self, platforms: Optional[List[str]] = None, 
                         keywords: Optional[List[str]] = None,
                         budget_range: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
        """Search for freelance jobs"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Searching jobs for user {self.user_id}")
            
            # Submit job search task
            task_id = await self.agent_collaboration_manager.submit_task(
                task_type="job_search",
                description="Search for relevant freelance jobs",
                priority=TaskPriority.HIGH,
                metadata={
                    "platforms": platforms,
                    "keywords": keywords,
                    "budget_range": budget_range
                }
            )
            
            # Auto-assign and process
            await self.agent_collaboration_manager.auto_assign_tasks()
            
            # Get results (in a real implementation, this would be async)
            jobs = await self.job_search_agent.search_jobs(platforms, keywords, budget_range)
            
            # Log behavior
            await self.user_profile_manager.log_behavior(
                "job_search",
                {"platforms": platforms, "keywords": keywords, "results_count": len(jobs)}
            )
            
            return [job.__dict__ for job in jobs]
            
        except Exception as e:
            self.logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    async def conduct_research(self, topic: str, research_type: str = "business_strategy") -> Dict[str, Any]:
        """Conduct research on a specific topic"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Conducting research on '{topic}' for user {self.user_id}")
            
            # Map research type to SearchType enum
            search_type_map = {
                "business_strategy": SearchType.BUSINESS_STRATEGY,
                "ai_tools": SearchType.AI_TOOLS,
                "industry_trends": SearchType.INDUSTRY_TRENDS,
                "competitive_analysis": SearchType.COMPETITIVE_ANALYSIS,
                "technology_research": SearchType.TECHNOLOGY_RESEARCH,
                "market_analysis": SearchType.MARKET_ANALYSIS,
                "skill_development": SearchType.SKILL_DEVELOPMENT,
                "freelance_tips": SearchType.FREELANCE_TIPS
            }
            
            search_type = search_type_map.get(research_type, SearchType.BUSINESS_STRATEGY)
            
            # Submit research task
            task_id = await self.agent_collaboration_manager.submit_task(
                task_type="research",
                description=f"Research on {topic}",
                priority=TaskPriority.MEDIUM,
                metadata={
                    "topic": topic,
                    "search_type": search_type.value
                }
            )
            
            # Auto-assign and process
            await self.agent_collaboration_manager.auto_assign_tasks()
            
            # Get results
            report = await self.web_search_agent.conduct_research(topic, search_type)
            
            # Log behavior
            await self.user_profile_manager.log_behavior(
                "research_conducted",
                {"topic": topic, "research_type": research_type}
            )
            
            return {
                "topic": report.topic,
                "summary": report.summary,
                "key_findings": report.key_findings,
                "recommendations": report.recommendations,
                "market_insights": report.market_insights,
                "trend_analysis": report.trend_analysis
            }
            
        except Exception as e:
            self.logger.error(f"Error conducting research: {str(e)}")
            return {"error": str(e)}
    
    async def solve_math_problem(self, problem_type: str, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve mathematical problems"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Solving math problem for user {self.user_id}")
            
            # Map problem type to MathProblemType enum
            problem_type_map = {
                "arithmetic": MathProblemType.ARITHMETIC,
                "algebra": MathProblemType.ALGEBRA,
                "calculus": MathProblemType.CALCULUS,
                "statistics": MathProblemType.STATISTICS,
                "financial": MathProblemType.FINANCIAL,
                "geometry": MathProblemType.GEOMETRY,
                "probability": MathProblemType.PROBABILITY,
                "optimization": MathProblemType.OPTIMIZATION
            }
            
            math_problem_type = problem_type_map.get(problem_type, MathProblemType.ARITHMETIC)
            
            # Create problem object
            problem = MathProblem(
                problem_id=str(uuid.uuid4()),
                problem_type=math_problem_type,
                description=problem_data.get("description", ""),
                input_data=problem_data.get("input_data", {}),
                complexity=problem_data.get("complexity", "medium"),
                context=problem_data.get("context", "")
            )
            
            # Submit math task
            task_id = await self.agent_collaboration_manager.submit_task(
                task_type="math_calculation",
                description=f"Solve {problem_type} problem",
                priority=TaskPriority.MEDIUM,
                metadata={"problem_data": problem.__dict__}
            )
            
            # Auto-assign and process
            await self.agent_collaboration_manager.auto_assign_tasks()
            
            # Get results
            solution = await self.math_agent.solve_math_problem(problem)
            
            # Log behavior
            await self.user_profile_manager.log_behavior(
                "math_problem_solved",
                {"problem_type": problem_type, "complexity": problem.complexity}
            )
            
            return {
                "solution": solution.solution,
                "steps": solution.steps,
                "answer": solution.answer,
                "confidence": solution.confidence,
                "verification": solution.verification
            }
            
        except Exception as e:
            self.logger.error(f"Error solving math problem: {str(e)}")
            return {"error": str(e)}
    
    async def conduct_financial_analysis(self, analysis_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct financial analysis"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Conducting financial analysis for user {self.user_id}")
            
            # Submit financial analysis task
            task_id = await self.agent_collaboration_manager.submit_task(
                task_type="financial_analysis",
                description=f"Financial analysis: {analysis_type}",
                priority=TaskPriority.MEDIUM,
                metadata={
                    "analysis_type": analysis_type,
                    "data": data
                }
            )
            
            # Auto-assign and process
            await self.agent_collaboration_manager.auto_assign_tasks()
            
            # Get results
            analysis = await self.math_agent.conduct_financial_analysis(analysis_type, data)
            
            # Log behavior
            await self.user_profile_manager.log_behavior(
                "financial_analysis",
                {"analysis_type": analysis_type}
            )
            
            return {
                "analysis_type": analysis.analysis_type,
                "results": analysis.results,
                "recommendations": analysis.recommendations,
                "risk_assessment": analysis.risk_assessment
            }
            
        except Exception as e:
            self.logger.error(f"Error conducting financial analysis: {str(e)}")
            return {"error": str(e)}
    
    async def get_daily_digest(self) -> Dict[str, Any]:
        """Get daily digest of jobs, trends, and recommendations"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Generating daily digest for user {self.user_id}")
            
            # Get job digest
            job_digest = await self.job_search_agent.get_daily_job_digest()
            
            # Get trending topics
            trending_topics = await self.web_search_agent.get_trending_topics()
            
            # Get personalized recommendations
            recommendations = await self.user_profile_manager.get_personalized_recommendations()
            
            # Get profile summary
            profile_summary = await self.user_profile_manager.get_profile_summary()
            
            digest = {
                "date": datetime.now().date().isoformat(),
                "job_market": job_digest,
                "trending_topics": trending_topics,
                "recommendations": recommendations,
                "profile_summary": profile_summary,
                "system_status": await self.agent_collaboration_manager.get_system_status()
            }
            
            # Log behavior
            await self.user_profile_manager.log_behavior("daily_digest_viewed", {})
            
            return digest
            
        except Exception as e:
            self.logger.error(f"Error generating daily digest: {str(e)}")
            return {"error": str(e)}
    
    async def update_user_profile(self, section: str, data: Dict[str, Any]) -> bool:
        """Update user profile information"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Updating user profile section '{section}' for user {self.user_id}")
            
            if section == "personal_info":
                return await self.user_profile_manager.update_personal_info(data)
            elif section == "work_preferences":
                return await self.user_profile_manager.update_work_preferences(data)
            elif section == "skills":
                # Handle skill updates
                for skill_name, skill_data in data.items():
                    skill = Skill(
                        name=skill_name,
                        level=SkillLevel(skill_data.get("level", "intermediate")),
                        years_experience=skill_data.get("years_experience", 0),
                        last_used=datetime.now(),
                        confidence_score=skill_data.get("confidence_score", 0.5),
                        certifications=skill_data.get("certifications", []),
                        projects_count=skill_data.get("projects_count", 0)
                    )
                    await self.user_profile_manager.add_skill(skill)
                return True
            else:
                self.logger.warning(f"Unknown profile section: {section}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    async def add_work_history(self, work_data: Dict[str, Any]) -> bool:
        """Add work history entry"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Adding work history for user {self.user_id}")
            
            work_history = WorkHistory(
                project_id=work_data.get("project_id", str(uuid.uuid4())),
                title=work_data["title"],
                description=work_data["description"],
                client=work_data["client"],
                platform=work_data["platform"],
                start_date=datetime.fromisoformat(work_data["start_date"]),
                end_date=datetime.fromisoformat(work_data["end_date"]) if work_data.get("end_date") else None,
                budget=work_data["budget"],
                skills_used=work_data.get("skills_used", []),
                rating=work_data.get("rating"),
                feedback=work_data.get("feedback"),
                status=work_data.get("status", "completed")
            )
            
            return await self.user_profile_manager.add_work_history(work_history)
            
        except Exception as e:
            self.logger.error(f"Error adding work history: {str(e)}")
            return False
    
    async def add_learning_goal(self, goal_data: Dict[str, Any]) -> bool:
        """Add learning goal"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            self.logger.info(f"Adding learning goal for user {self.user_id}")
            
            goal = LearningGoal(
                goal_id=goal_data.get("goal_id", str(uuid.uuid4())),
                skill_name=goal_data["skill_name"],
                target_level=SkillLevel(goal_data["target_level"]),
                target_date=datetime.fromisoformat(goal_data["target_date"]),
                current_progress=goal_data.get("current_progress", 0.0),
                learning_resources=goal_data.get("learning_resources", []),
                status=goal_data.get("status", "active")
            )
            
            return await self.user_profile_manager.add_learning_goal(goal)
            
        except Exception as e:
            self.logger.error(f"Error adding learning goal: {str(e)}")
            return False
    
    async def get_skill_gap_analysis(self) -> Dict[str, Any]:
        """Get skill gap analysis"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            return await self.user_profile_manager.get_skill_gap_analysis()
        except Exception as e:
            self.logger.error(f"Error getting skill gap analysis: {str(e)}")
            return {"error": str(e)}
    
    async def submit_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Submit user feedback"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            return await self.user_profile_manager.add_feedback(feedback_data)
        except Exception as e:
            self.logger.error(f"Error submitting feedback: {str(e)}")
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            return await self.agent_collaboration_manager.get_system_status()
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {"error": str(e)}
    
    async def export_user_data(self, format: str = "json") -> str:
        """Export user data"""
        if not self.is_initialized:
            await self.initialize()
        
        try:
            return await self.user_profile_manager.export_profile(format)
        except Exception as e:
            self.logger.error(f"Error exporting user data: {str(e)}")
            return json.dumps({"error": str(e)})

async def main():
    """Main function to demonstrate FreelanceX.AI capabilities"""
    print("🚀 Initializing FreelanceX.AI - The World's Most Powerful AI Assistant for Freelancers")
    print("=" * 80)
    
    # Initialize FreelanceX.AI
    freelancex = FreelanceXAI("demo_user_001")
    
    if await freelancex.initialize():
        print("✅ FreelanceX.AI initialized successfully!")
        
        # Demo: Search for jobs
        print("\n🔍 Searching for AI/ML jobs...")
        jobs = await freelancex.search_jobs(
            keywords=["Python", "Machine Learning", "AI"],
            budget_range={"min": 5000, "max": 20000}
        )
        print(f"Found {len(jobs)} relevant jobs")
        
        # Demo: Conduct research
        print("\n📚 Conducting research on AI tools for freelancers...")
        research = await freelancex.conduct_research("AI tools for freelancers", "ai_tools")
        print(f"Research completed: {research.get('summary', 'No summary available')[:100]}...")
        
        # Demo: Financial analysis
        print("\n💰 Conducting financial analysis...")
        financial_data = {
            "income": [5000, 6000, 4500, 7000, 5500],
            "expenses": {"software": 200, "marketing": 300, "office": 150}
        }
        analysis = await freelancex.conduct_financial_analysis("income_analysis", financial_data)
        print(f"Financial analysis completed: {len(analysis.get('recommendations', []))} recommendations")
        
        # Demo: Get daily digest
        print("\n📊 Generating daily digest...")
        digest = await freelancex.get_daily_digest()
        print(f"Daily digest generated with {len(digest.get('recommendations', {}))} recommendation categories")
        
        # Demo: Get system status
        print("\n⚙️ Getting system status...")
        status = await freelancex.get_system_status()
        print(f"System status: {status.get('system_health', 'unknown')}")
        
        print("\n🎉 FreelanceX.AI demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• Intelligent job search across multiple platforms")
        print("• Comprehensive research and market analysis")
        print("• Financial analysis and planning")
        print("• Personalized recommendations")
        print("• Agent collaboration and task management")
        print("• User profile management and personalization")
        
    else:
        print("❌ Failed to initialize FreelanceX.AI")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())