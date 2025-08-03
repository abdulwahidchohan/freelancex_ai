#!/usr/bin/env python3
"""
FreelanceX.AI - Main Application
Empowering freelancers with cutting-edge AI tools for enhanced productivity, 
decision-making, and market adaptability.

Mission: Enhance productivity, decision-making, and market adaptability
Vision: Become the global leader in AI-driven solutions for freelancers
Values: Innovation, autonomy, collaboration, growth, and impact
"""

import asyncio
import logging
import schedule
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import FreelanceX.AI core components
from core.agent_manager import AgentManager
from core.base_agent import BaseAgent, AgentStatus
from core.executive_agent import ExecutiveAgent
from memory.sqlite_memory import MemoryManager
from openai_agents import Agent, Session
from openai import OpenAI

# Import specialized agents
from agents.proposal_writer_agent import ProposalWriterAgent
from agents.job_search_agent import JobSearchAgent
from agents.web_search_agent import WebSearchAgent  
from agents.math_agent import MathAgent

# Additional imports for comprehensive system
import os
from pathlib import Path
import sqlite3
from threading import Thread

@dataclass
class UserProfile:
    """Comprehensive user profile for FreelanceX.AI"""
    user_id: str
    name: str
    skills: List[str]
    experience_years: int
    preferred_hourly_rate: float
    location: str
    time_zone: str
    work_schedule: Dict[str, Any]
    goals: List[str]
    preferences: Dict[str, Any]
    created_at: str
    last_updated: str

@dataclass
class DailyRoutine:
    """Daily routine configuration"""
    morning_briefing_time: str
    work_session_alerts: List[str]
    end_of_day_summary_time: str
    enabled: bool
    custom_settings: Dict[str, Any]

class FreelanceXAI:
    """
    Main FreelanceX.AI Application Class
    Orchestrates all AI agents and provides unified interface for freelancers
    """
    
    def __init__(self, config_path: str = "config/freelancex_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize logging
        self._setup_logging()
        self.logger = logging.getLogger("FreelanceX.Main")
        
        # Initialize core components
        self.agent_manager = AgentManager()
        self.memory_manager = MemoryManager()
        self.executive_agent = ExecutiveAgent()
        self.openai_client = OpenAI()
        self.user_profile: Optional[UserProfile] = None
        self.daily_routine: Optional[DailyRoutine] = None
        
        # Initialize database
        self.db_path = "data/freelancex.db"
        self._setup_database()
        
        # System state
        self.is_running = False
        self.startup_time = datetime.now()
        self.session_data = {
            'tasks_completed': 0,
            'insights_generated': 0,
            'jobs_found': 0,
            'calculations_performed': 0,
            'recommendations_provided': 0
        }
        
        # Initialize agents
        self._initialize_agents()
        
        # Setup daily routines
        self._setup_daily_routines()
        
        self.logger.info("FreelanceX.AI initialized successfully")

    def _load_config(self) -> Dict[str, Any]:
        """Load application configuration"""
        default_config = {
            "app_name": "FreelanceX.AI",
            "version": "1.0.0",
            "log_level": "INFO",
            "agents": {
                "job_search": {"enabled": True, "update_frequency": 300},
                "web_search": {"enabled": True, "cache_ttl": 3600},
                "math": {"enabled": True, "precision": 6}
            },
            "daily_routines": {
                "morning_briefing": "09:00",
                "work_session_alerts": ["10:00", "14:00", "16:00"],
                "end_of_day_summary": "18:00",
                "enabled": True
            },
            "user_interface": {
                "theme": "professional",
                "notifications": True,
                "auto_save": True
            },
            "privacy": {
                "data_encryption": True,
                "user_consent_required": True,
                "data_retention_days": 365
            }
        }
        
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                config = {**default_config, **user_config}
            else:
                config = default_config
                self._save_config(config)
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return default_config

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def _setup_logging(self):
        """Setup comprehensive logging for FreelanceX.AI"""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"logs/freelancex_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler()
            ]
        )

    def _setup_database(self):
        """Setup SQLite database for persistent storage"""
        os.makedirs("data", exist_ok=True)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create user profiles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        skills TEXT,
                        experience_years INTEGER,
                        preferred_hourly_rate REAL,
                        location TEXT,
                        time_zone TEXT,
                        work_schedule TEXT,
                        goals TEXT,
                        preferences TEXT,
                        created_at TEXT,
                        last_updated TEXT
                    )
                """)
                
                # Create daily routines table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS daily_routines (
                        user_id TEXT PRIMARY KEY,
                        morning_briefing_time TEXT,
                        work_session_alerts TEXT,
                        end_of_day_summary_time TEXT,
                        enabled BOOLEAN,
                        custom_settings TEXT,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """)
                
                # Create session logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS session_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        session_date TEXT,
                        tasks_completed INTEGER,
                        insights_generated INTEGER,
                        jobs_found INTEGER,
                        calculations_performed INTEGER,
                        recommendations_provided INTEGER,
                        session_duration_minutes INTEGER,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """)
                
                # Create agent performance table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_name TEXT,
                        date TEXT,
                        tasks_executed INTEGER,
                        success_rate REAL,
                        avg_response_time REAL,
                        user_satisfaction REAL
                    )
                """)
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Database setup error: {e}")

    def _initialize_agents(self):
        """Initialize and register all FreelanceX.AI agents"""
        try:
            # Initialize core agents
            if self.config["agents"]["job_search"]["enabled"]:
                job_agent = JobSearchAgent()
                self.agent_manager.register_agent(job_agent)
                self.logger.info("JobSearchAgent initialized and registered")
            
            if self.config["agents"]["web_search"]["enabled"]:
                web_agent = WebSearchAgent()
                self.agent_manager.register_agent(web_agent)
                self.logger.info("WebSearchAgent initialized and registered")
            
            if self.config["agents"]["math"]["enabled"]:
                math_agent = MathAgent()
                self.agent_manager.register_agent(math_agent)
                self.logger.info("MathAgent initialized and registered")
            
            self.logger.info(f"All agents initialized. Active agents: {len(self.agent_manager.agents)}")
            
        except Exception as e:
            self.logger.error(f"Agent initialization error: {e}")

    def _setup_daily_routines(self):
        """Setup scheduled daily routines for users"""
        if not self.config["daily_routines"]["enabled"]:
            return
        
        try:
            # Morning briefing
            morning_time = self.config["daily_routines"]["morning_briefing"]
            schedule.every().day.at(morning_time).do(self._morning_briefing)
            
            # Work session alerts
            for alert_time in self.config["daily_routines"]["work_session_alerts"]:
                schedule.every().day.at(alert_time).do(self._work_session_alert)
            
            # End of day summary
            summary_time = self.config["daily_routines"]["end_of_day_summary"]
            schedule.every().day.at(summary_time).do(self._end_of_day_summary)
            
            # Start scheduler in background thread
            def run_scheduler():
                while self.is_running:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
            
            scheduler_thread = Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            self.logger.info("Daily routines scheduled successfully")
            
        except Exception as e:
            self.logger.error(f"Daily routine setup error: {e}")

    async def start(self):
        """Start the FreelanceX.AI system"""
        self.is_running = True
        self.logger.info("🚀 FreelanceX.AI starting up...")
        
        try:
            # Load user profile if exists
            await self._load_user_profile()
            
            # Perform system health check
            await self._system_health_check()
            
            # Start agent execution loops
            await self._start_agents()
            
            # Run initial morning briefing if it's morning
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 12:
                await self._morning_briefing()
            
            self.logger.info("✅ FreelanceX.AI is now running and ready to assist!")
            
            # Main application loop
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Startup error: {e}")
            await self.shutdown()

    async def _load_user_profile(self):
        """Load user profile from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM user_profiles LIMIT 1")
                row = cursor.fetchone()
                
                if row:
                    self.user_profile = UserProfile(
                        user_id=row[0],
                        name=row[1],
                        skills=json.loads(row[2]) if row[2] else [],
                        experience_years=row[3] or 0,
                        preferred_hourly_rate=row[4] or 0.0,
                        location=row[5] or "",
                        time_zone=row[6] or "UTC",
                        work_schedule=json.loads(row[7]) if row[7] else {},
                        goals=json.loads(row[8]) if row[8] else [],
                        preferences=json.loads(row[9]) if row[9] else {},
                        created_at=row[10] or "",
                        last_updated=row[11] or ""
                    )
                    self.logger.info(f"User profile loaded: {self.user_profile.name}")
                else:
                    self.logger.info("No user profile found - new user setup required")
                    
        except Exception as e:
            self.logger.error(f"Error loading user profile: {e}")

    async def _system_health_check(self):
        """Perform comprehensive system health check"""
        self.logger.info("🔍 Performing system health check...")
        
        health_report = {
            "system_status": "healthy",
            "agent_status": {},
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check agent health
            for agent_name, agent in self.agent_manager.agents.items():
                diagnosis = await agent.self_diagnose()
                health_report["agent_status"][agent_name] = diagnosis
                
                if diagnosis.get("needs_repair", False):
                    health_report["issues"].extend(diagnosis.get("issues", []))
                    health_report["recommendations"].extend(diagnosis.get("recommendations", []))
            
            # Check database connectivity
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("SELECT 1")
                health_report["database_status"] = "connected"
            except Exception:
                health_report["database_status"] = "error"
                health_report["issues"].append("Database connectivity issue")
            
            # Check disk space
            disk_usage = self._check_disk_space()
            if disk_usage > 90:
                health_report["issues"].append(f"Low disk space: {disk_usage}% used")
            
            # Overall system status
            if health_report["issues"]:
                health_report["system_status"] = "degraded" if len(health_report["issues"]) < 3 else "critical"
            
            self.logger.info(f"✅ Health check complete. Status: {health_report['system_status']}")
            
            if health_report["issues"]:
                self.logger.warning(f"Issues found: {', '.join(health_report['issues'])}")
            
            return health_report
            
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return {"system_status": "error", "error": str(e)}

    def _check_disk_space(self) -> float:
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            return (used / total) * 100
        except:
            return 0

    async def _start_agents(self):
        """Start all registered agents"""
        try:
            agent_tasks = []
            for agent_name, agent in self.agent_manager.agents.items():
                task = asyncio.create_task(agent.run())
                agent_tasks.append(task)
                self.logger.info(f"Started {agent_name}")
            
            self.logger.info(f"All {len(agent_tasks)} agents started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting agents: {e}")

    async def _main_loop(self):
        """Main application event loop"""
        self.logger.info("🔄 Entering main application loop...")
        
        try:
            while self.is_running:
                # Update session metrics
                await self._update_session_metrics()
                
                # Process any pending tasks
                await self._process_pending_tasks()
                
                # Periodic agent coordination
                await self._coordinate_agents()
                
                # Sleep to prevent busy waiting
                await asyncio.sleep(30)  # 30-second cycles
                
        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received")
        except Exception as e:
            self.logger.error(f"Main loop error: {e}")
        finally:
            await self.shutdown()

    async def _update_session_metrics(self):
        """Update session performance metrics"""
        try:
            system_status = self.agent_manager.get_system_status()
            
            # Update session data from agent metrics
            for agent_name, agent_info in system_status["agent_statuses"].items():
                metrics = agent_info.get("performance_metrics", {})
                
                if agent_name == "JobSearchAgent":
                    self.session_data["jobs_found"] = metrics.get("successful_matches", 0)
                elif agent_name == "MathAgent":
                    self.session_data["calculations_performed"] = metrics.get("calculations_performed", 0)
                elif agent_name == "WebSearchAgent":
                    self.session_data["insights_generated"] = metrics.get("insights_generated", 0)
            
        except Exception as e:
            self.logger.error(f"Error updating session metrics: {e}")

    async def _process_pending_tasks(self):
        """Process any pending system tasks"""
        try:
            # Check for high-priority agent tasks
            if self.agent_manager.task_queue.qsize() > 0:
                pending_task = await self.agent_manager.task_queue.get()
                result = await self.agent_manager.distribute_task(pending_task)
                self.logger.info(f"Processed pending task: {pending_task.get('type', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error processing pending tasks: {e}")

    async def _coordinate_agents(self):
        """Coordinate activities between agents"""
        try:
            # Check for potential cross-agent collaborations
            if len(self.agent_manager.agents) > 1:
                # Example: If job search finds AI/ML jobs, trigger research on AI tools
                job_agent = self.agent_manager.agents.get("JobSearchAgent")
                web_agent = self.agent_manager.agents.get("WebSearchAgent")
                
                if job_agent and web_agent:
                    # Get recent job search results from memory
                    recent_searches = job_agent.retrieve_memory("recent_job_categories")
                    if recent_searches and "AI" in str(recent_searches):
                        # Trigger AI tools research
                        research_task = {
                            "type": "ai_tool_research",
                            "category": "development",
                            "use_case": "freelancer_productivity"
                        }
                        await web_agent.execute_task(research_task)
                        self.logger.info("Triggered AI tools research based on job search results")
            
        except Exception as e:
            self.logger.error(f"Error in agent coordination: {e}")

    async def _morning_briefing(self):
        """Generate and deliver morning briefing"""
        self.logger.info("🌅 Generating morning briefing...")
        
        try:
            briefing = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M"),
                "weather": "☀️ Sunny",  # Could integrate weather API
                "agenda": [],
                "market_updates": [],
                "job_opportunities": [],
                "ai_insights": [],
                "productivity_tips": []
            }
            
            # Get job opportunities from JobSearchAgent
            job_agent = self.agent_manager.agents.get("JobSearchAgent")
            if job_agent:
                job_task = {
                    "type": "search_jobs",
                    "filters": {"keywords": self.user_profile.skills if self.user_profile else []}
                }
                job_result = await job_agent.execute_task(job_task)
                if job_result.get("status") == "success":
                    briefing["job_opportunities"] = job_result.get("jobs", [])[:5]  # Top 5
            
            # Get market insights from WebSearchAgent
            web_agent = self.agent_manager.agents.get("WebSearchAgent")
            if web_agent:
                research_task = {
                    "type": "daily_digest"
                }
                research_result = await web_agent.execute_task(research_task)
                if research_result.get("status") == "success":
                    digest = research_result.get("daily_digest", {})
                    briefing["market_updates"] = digest.get("industry_news", [])[:3]
                    briefing["ai_insights"] = digest.get("ai_tool_updates", [])[:3]
                    briefing["productivity_tips"] = digest.get("productivity_tips", [])[:3]
            
            # Generate agenda based on user goals
            if self.user_profile and self.user_profile.goals:
                briefing["agenda"] = [
                    f"Focus on: {goal}" for goal in self.user_profile.goals[:3]
                ]
            
            # Store briefing
            self._store_briefing(briefing)
            
            # Display briefing
            await self._display_briefing(briefing)
            
            self.logger.info("✅ Morning briefing delivered")
            
        except Exception as e:
            self.logger.error(f"Error generating morning briefing: {e}")

    async def _work_session_alert(self):
        """Send work session productivity alert"""
        self.logger.info("⏰ Work session alert triggered")
        
        try:
            current_time = datetime.now()
            session_duration = (current_time - self.startup_time).total_seconds() / 3600
            
            alert = {
                "time": current_time.strftime("%H:%M"),
                "session_duration_hours": round(session_duration, 1),
                "tasks_completed": self.session_data["tasks_completed"],
                "productivity_score": self._calculate_productivity_score(),
                "suggestions": self._generate_productivity_suggestions(),
                "break_recommendation": session_duration > 2  # Suggest break after 2 hours
            }
            
            await self._display_work_alert(alert)
            
        except Exception as e:
            self.logger.error(f"Error in work session alert: {e}")

    async def _end_of_day_summary(self):
        """Generate comprehensive end-of-day summary"""
        self.logger.info("🌆 Generating end-of-day summary...")
        
        try:
            current_date = datetime.now().date()
            session_duration = (datetime.now() - self.startup_time).total_seconds() / 3600
            
            summary = {
                "date": current_date.isoformat(),
                "session_duration_hours": round(session_duration, 1),
                "productivity_metrics": self.session_data.copy(),
                "agent_performance": {},
                "achievements": [],
                "insights": [],
                "tomorrow_recommendations": [],
                "financial_summary": {}
            }
            
            # Get agent performance data
            system_status = self.agent_manager.get_system_status()
            summary["agent_performance"] = {
                name: info.get("performance_metrics", {})
                for name, info in system_status["agent_statuses"].items()
            }
            
            # Calculate achievements
            summary["achievements"] = self._calculate_daily_achievements()
            
            # Get financial insights from MathAgent
            math_agent = self.agent_manager.agents.get("MathAgent")
            if math_agent and self.user_profile:
                financial_task = {
                    "type": "financial_analysis",
                    "financial_data": {
                        "income": [self.user_profile.preferred_hourly_rate * 8],  # Daily estimate
                        "expenses": [],
                        "projects": []
                    },
                    "analysis_goals": ["daily_performance"]
                }
                financial_result = await math_agent.execute_task(financial_task)
                if financial_result.get("status") == "success":
                    summary["financial_summary"] = financial_result.get("financial_analysis", {})
            
            # Generate tomorrow's recommendations
            summary["tomorrow_recommendations"] = await self._generate_tomorrow_recommendations()
            
            # Store summary in database
            await self._store_daily_summary(summary)
            
            # Display summary
            await self._display_end_of_day_summary(summary)
            
            self.logger.info("✅ End-of-day summary completed")
            
        except Exception as e:
            self.logger.error(f"Error generating end-of-day summary: {e}")

    def _calculate_productivity_score(self) -> float:
        """Calculate current productivity score (0-100)"""
        try:
            score = 0
            total_possible = 100
            
            # Tasks completed (40 points)
            task_score = min(40, self.session_data["tasks_completed"] * 10)
            score += task_score
            
            # Jobs found (20 points)
            job_score = min(20, self.session_data["jobs_found"] * 5)
            score += job_score
            
            # Insights generated (20 points)
            insight_score = min(20, self.session_data["insights_generated"] * 5)
            score += insight_score
            
            # Calculations performed (10 points)
            calc_score = min(10, self.session_data["calculations_performed"] * 2)
            score += calc_score
            
            # Recommendations received (10 points)
            rec_score = min(10, self.session_data["recommendations_provided"] * 2)
            score += rec_score
            
            return min(100, score)
            
        except Exception:
            return 50  # Default moderate score

    def _generate_productivity_suggestions(self) -> List[str]:
        """Generate productivity improvement suggestions"""
        suggestions = []
        score = self._calculate_productivity_score()
        
        if score < 30:
            suggestions.extend([
                "Consider taking a short break to refresh",
                "Try breaking large tasks into smaller steps",
                "Use the Pomodoro technique for focused work"
            ])
        elif score < 60:
            suggestions.extend([
                "You're making good progress - keep it up!",
                "Consider reviewing your goals for today",
                "Take a few minutes to organize your workspace"
            ])
        else:
            suggestions.extend([
                "Excellent productivity today!",
                "Consider documenting your successful strategies",
                "You're on track for a great day"
            ])
        
        return suggestions

    def _calculate_daily_achievements(self) -> List[str]:
        """Calculate and return daily achievements"""
        achievements = []
        
        if self.session_data["jobs_found"] > 5:
            achievements.append(f"🎯 Found {self.session_data['jobs_found']} job opportunities")
        
        if self.session_data["insights_generated"] > 3:
            achievements.append(f"💡 Generated {self.session_data['insights_generated']} insights")
        
        if self.session_data["calculations_performed"] > 5:
            achievements.append(f"🧮 Performed {self.session_data['calculations_performed']} calculations")
        
        productivity_score = self._calculate_productivity_score()
        if productivity_score > 80:
            achievements.append("🏆 Achieved high productivity score")
        
        return achievements

    async def _generate_tomorrow_recommendations(self) -> List[str]:
        """Generate recommendations for tomorrow"""
        recommendations = []
        
        # Based on today's performance
        if self.session_data["jobs_found"] < 3:
            recommendations.append("Focus on expanding job search criteria tomorrow")
        
        if self.session_data["insights_generated"] < 2:
            recommendations.append("Allocate time for market research and trend analysis")
        
        # Based on market trends (from WebSearchAgent)
        web_agent = self.agent_manager.agents.get("WebSearchAgent")
        if web_agent:
            trend_task = {
                "type": "trend_analysis",
                "keywords": ["freelance", "remote work", "AI"],
                "timeframe": "1d"
            }
            try:
                trend_result = await web_agent.execute_task(trend_task)
                if trend_result.get("status") == "success":
                    trends = trend_result.get("trend_analysis", {}).get("emerging_trends", [])
                    if trends:
                        recommendations.append(f"Consider exploring: {', '.join(trends[:2])}")
            except Exception:
                pass
        
        # Default recommendations
        recommendations.extend([
            "Review and update your skill portfolio",
            "Set specific goals for tomorrow's session",
            "Plan time for professional development"
        ])
        
        return recommendations

    def _store_briefing(self, briefing: Dict[str, Any]):
        """Store morning briefing data"""
        try:
            briefing_file = f"data/briefings/briefing_{briefing['date']}.json"
            os.makedirs(os.path.dirname(briefing_file), exist_ok=True)
            
            with open(briefing_file, 'w') as f:
                json.dump(briefing, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error storing briefing: {e}")

    async def _store_daily_summary(self, summary: Dict[str, Any]):
        """Store daily summary in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO session_logs 
                    (user_id, session_date, tasks_completed, insights_generated, 
                     jobs_found, calculations_performed, recommendations_provided, 
                     session_duration_minutes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.user_profile.user_id if self.user_profile else "default",
                    summary["date"],
                    summary["productivity_metrics"]["tasks_completed"],
                    summary["productivity_metrics"]["insights_generated"],
                    summary["productivity_metrics"]["jobs_found"],
                    summary["productivity_metrics"]["calculations_performed"],
                    summary["productivity_metrics"]["recommendations_provided"],
                    int(summary["session_duration_hours"] * 60)
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing daily summary: {e}")

    async def _display_briefing(self, briefing: Dict[str, Any]):
        """Display morning briefing to user"""
        print("\n" + "="*60)
        print(f"🌅 FreelanceX.AI Morning Briefing - {briefing['date']}")
        print("="*60)
        
        if briefing["job_opportunities"]:
            print(f"\n🎯 Job Opportunities ({len(briefing['job_opportunities'])} found):")
            for i, job in enumerate(briefing["job_opportunities"][:3], 1):
                print(f"  {i}. {job.get('title', 'Unknown')} - ${job.get('budget', 0):,.0f}")
        
        if briefing["market_updates"]:
            print(f"\n📊 Market Updates:")
            for update in briefing["market_updates"][:3]:
                print(f"  • {update}")
        
        if briefing["productivity_tips"]:
            print(f"\n💡 Today's Productivity Tips:")
            for tip in briefing["productivity_tips"][:2]:
                print(f"  • {tip}")
        
        if briefing["agenda"]:
            print(f"\n📋 Today's Focus:")
            for item in briefing["agenda"]:
                print(f"  • {item}")
        
        print("\nHave a productive day! 🚀")
        print("="*60 + "\n")

    async def _display_work_alert(self, alert: Dict[str, Any]):
        """Display work session alert"""
        print(f"\n⏰ Work Session Alert - {alert['time']}")
        print(f"Session Duration: {alert['session_duration_hours']} hours")
        print(f"Productivity Score: {alert['productivity_score']:.0f}/100")
        
        if alert["break_recommendation"]:
            print("💡 Consider taking a 5-10 minute break!")
        
        if alert["suggestions"]:
            print("\nSuggestions:")
            for suggestion in alert["suggestions"][:2]:
                print(f"  • {suggestion}")
        print()

    async def _display_end_of_day_summary(self, summary: Dict[str, Any]):
        """Display comprehensive end-of-day summary"""
        print("\n" + "="*60)
        print(f"🌆 FreelanceX.AI Daily Summary - {summary['date']}")
        print("="*60)
        
        print(f"\n⏱️  Session Duration: {summary['session_duration_hours']} hours")
        
        print(f"\n📊 Productivity Metrics:")
        metrics = summary['productivity_metrics']
        print(f"  • Tasks Completed: {metrics['tasks_completed']}")
        print(f"  • Jobs Found: {metrics['jobs_found']}")
        print(f"  • Insights Generated: {metrics['insights_generated']}")
        print(f"  • Calculations Performed: {metrics['calculations_performed']}")
        
        if summary["achievements"]:
            print(f"\n🏆 Today's Achievements:")
            for achievement in summary["achievements"]:
                print(f"  • {achievement}")
        
        if summary["tomorrow_recommendations"]:
            print(f"\n🚀 Tomorrow's Recommendations:")
            for rec in summary["tomorrow_recommendations"][:3]:
                print(f"  • {rec}")
        
        print(f"\nGreat work today! Rest well and see you tomorrow. 🌙")
        print("="*60 + "\n")

    async def shutdown(self):
        """Gracefully shutdown FreelanceX.AI"""
        self.logger.info("🔄 Initiating FreelanceX.AI shutdown...")
        
        try:
            self.is_running = False
            
            # Save final session data
            if self.user_profile:
                summary = {
                    "date": datetime.now().date().isoformat(),
                    "session_duration_hours": (datetime.now() - self.startup_time).total_seconds() / 3600,
                    "productivity_metrics": self.session_data.copy(),
                    "agent_performance": {},
                    "achievements": self._calculate_daily_achievements(),
                    "insights": [],
                    "tomorrow_recommendations": [],
                    "financial_summary": {}
                }
                await self._store_daily_summary(summary)
            
            # Shutdown agent manager
            await self.agent_manager.shutdown()
            
            # Close database connections
            # Database will auto-close with context managers
            
            self.logger.info("✅ FreelanceX.AI shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def process_user_command(self, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user commands through the unified interface"""
        try:
            if not parameters:
                parameters = {}
            
            # Route command to appropriate agent
            if command.startswith("search_jobs"):
                agent = self.agent_manager.agents.get("JobSearchAgent")
                task = {"type": "search_jobs", **parameters}
                
            elif command.startswith("research"):
                agent = self.agent_manager.agents.get("WebSearchAgent")
                task = {"type": "research_topic", **parameters}
                
            elif command.startswith("calculate") or command.startswith("analyze"):
                agent = self.agent_manager.agents.get("MathAgent")
                task = {"type": "financial_analysis", **parameters}
                
            else:
                return {
                    "status": "error",
                    "message": f"Unknown command: {command}",
                    "available_commands": [
                        "search_jobs", "research", "calculate", "analyze"
                    ]
                }
            
            if agent:
                result = await agent.execute_task(task)
                self.session_data["tasks_completed"] += 1
                return result
            else:
                return {
                    "status": "error",
                    "message": "Required agent not available"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing user command: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

def main():
    """Main entry point for FreelanceX.AI"""
    print("🚀 Starting FreelanceX.AI...")
    print("Empowering freelancers with cutting-edge AI tools")
    print("Mission: Enhance productivity, decision-making, and market adaptability")
    print()
    
    # Create and run FreelanceX.AI
    freelancex = FreelanceXAI()
    
    try:
        asyncio.run(freelancex.start())
    except KeyboardInterrupt:
        print("\n👋 FreelanceX.AI shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()