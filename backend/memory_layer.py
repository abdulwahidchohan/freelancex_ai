#!/usr/bin/env python3
"""
FreelanceX.AI - Memory Layer
Handles user data storage, preferences, and long-term memory for the multi-agent system.
"""

import asyncio
import logging
import json
import sqlite3
import redis
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import pickle
from pathlib import Path
import aiofiles
from pydantic import BaseModel, ValidationError

class MemoryType(Enum):
    """Types of memory storage"""
    USER_PROFILE = "user_profile"
    INTERACTION_HISTORY = "interaction_history"
    JOB_HISTORY = "job_history"
    PREFERENCES = "preferences"
    LEARNING_DATA = "learning_data"
    SYSTEM_STATE = "system_state"

@dataclass
class UserProfile:
    """Comprehensive user profile"""
    user_id: str
    name: str
    email: str
    skills: List[str]
    experience_years: int
    preferred_hourly_rate: float
    location: str
    timezone: str
    work_schedule: Dict[str, Any]
    goals: List[str]
    preferences: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    profile_completeness: float = 0.0

@dataclass
class InteractionRecord:
    """Record of user-agent interactions"""
    interaction_id: str
    user_id: str
    agent_name: str
    request_type: str
    request_content: Dict[str, Any]
    response_content: Dict[str, Any]
    timestamp: datetime
    duration_ms: int
    success: bool
    feedback_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)

@dataclass
class JobRecord:
    """Record of job-related activities"""
    job_id: str
    user_id: str
    platform: str
    title: str
    description: str
    budget: Optional[float]
    status: str  # applied, interviewed, hired, completed, etc.
    applied_at: datetime
    last_updated: datetime
    notes: str = ""
    tags: List[str] = field(default_factory=list)

@dataclass
class LearningData:
    """Data for system learning and improvement"""
    data_id: str
    user_id: str
    data_type: str
    content: Dict[str, Any]
    timestamp: datetime
    importance_score: float
    usage_count: int = 0

class DatabaseManager:
    """Manages SQLite database operations"""
    
    def __init__(self, db_path: str = "data/freelancex.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("FreelanceX.Memory.Database")
        self._ensure_data_directory()
        self._initialize_database()
    
    def _ensure_data_directory(self):
        """Ensure data directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _initialize_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # User profiles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        skills TEXT NOT NULL,
                        experience_years INTEGER NOT NULL,
                        preferred_hourly_rate REAL NOT NULL,
                        location TEXT NOT NULL,
                        timezone TEXT NOT NULL,
                        work_schedule TEXT NOT NULL,
                        goals TEXT NOT NULL,
                        preferences TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        profile_completeness REAL DEFAULT 0.0
                    )
                """)
                
                # Interaction history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS interaction_history (
                        interaction_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        request_type TEXT NOT NULL,
                        request_content TEXT NOT NULL,
                        response_content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        duration_ms INTEGER NOT NULL,
                        success BOOLEAN NOT NULL,
                        feedback_score REAL,
                        tags TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """)
                
                # Job history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS job_history (
                        job_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        budget REAL,
                        status TEXT NOT NULL,
                        applied_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        notes TEXT DEFAULT '',
                        tags TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """)
                
                # Learning data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS learning_data (
                        data_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        data_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        importance_score REAL NOT NULL,
                        usage_count INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interaction_history(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interaction_history(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON job_history(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status ON job_history(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_user_id ON learning_data(user_id)")
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise
    
    async def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, name, email, skills, experience_years, preferred_hourly_rate,
                     location, timezone, work_schedule, goals, preferences, created_at,
                     last_updated, profile_completeness)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.name,
                    profile.email,
                    json.dumps(profile.skills),
                    profile.experience_years,
                    profile.preferred_hourly_rate,
                    profile.location,
                    profile.timezone,
                    json.dumps(profile.work_schedule),
                    json.dumps(profile.goals),
                    json.dumps(profile.preferences),
                    profile.created_at.isoformat(),
                    profile.last_updated.isoformat(),
                    profile.profile_completeness
                ))
                
                conn.commit()
                self.logger.info(f"User profile saved for {profile.user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving user profile: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return UserProfile(
                        user_id=row[0],
                        name=row[1],
                        email=row[2],
                        skills=json.loads(row[3]),
                        experience_years=row[4],
                        preferred_hourly_rate=row[5],
                        location=row[6],
                        timezone=row[7],
                        work_schedule=json.loads(row[8]),
                        goals=json.loads(row[9]),
                        preferences=json.loads(row[10]),
                        created_at=datetime.fromisoformat(row[11]),
                        last_updated=datetime.fromisoformat(row[12]),
                        profile_completeness=row[13]
                    )
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving user profile: {str(e)}")
            return None
    
    async def save_interaction(self, interaction: InteractionRecord) -> bool:
        """Save interaction record to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO interaction_history 
                    (interaction_id, user_id, agent_name, request_type, request_content,
                     response_content, timestamp, duration_ms, success, feedback_score, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.interaction_id,
                    interaction.user_id,
                    interaction.agent_name,
                    interaction.request_type,
                    json.dumps(interaction.request_content),
                    json.dumps(interaction.response_content),
                    interaction.timestamp.isoformat(),
                    interaction.duration_ms,
                    interaction.success,
                    interaction.feedback_score,
                    json.dumps(interaction.tags)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error saving interaction: {str(e)}")
            return False
    
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[InteractionRecord]:
        """Retrieve user interaction history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM interaction_history 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                interactions = []
                for row in cursor.fetchall():
                    interactions.append(InteractionRecord(
                        interaction_id=row[0],
                        user_id=row[1],
                        agent_name=row[2],
                        request_type=row[3],
                        request_content=json.loads(row[4]),
                        response_content=json.loads(row[5]),
                        timestamp=datetime.fromisoformat(row[6]),
                        duration_ms=row[7],
                        success=bool(row[8]),
                        feedback_score=row[9],
                        tags=json.loads(row[10])
                    ))
                
                return interactions
                
        except Exception as e:
            self.logger.error(f"Error retrieving interactions: {str(e)}")
            return []

class RedisMemoryManager:
    """Manages Redis-based caching and temporary memory"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
        self.logger = logging.getLogger("FreelanceX.Memory.Redis")
    
    async def cache_user_data(self, user_id: str, data_type: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Cache user data in Redis"""
        try:
            key = f"user:{user_id}:{data_type}"
            await self.redis_client.setex(key, ttl, json.dumps(data))
            return True
        except Exception as e:
            self.logger.error(f"Error caching user data: {str(e)}")
            return False
    
    async def get_cached_user_data(self, user_id: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached user data from Redis"""
        try:
            key = f"user:{user_id}:{data_type}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            self.logger.error(f"Error retrieving cached data: {str(e)}")
            return None
    
    async def cache_agent_response(self, agent_name: str, request_hash: str, response: Dict[str, Any], ttl: int = 1800) -> bool:
        """Cache agent responses for similar requests"""
        try:
            key = f"agent:{agent_name}:response:{request_hash}"
            await self.redis_client.setex(key, ttl, json.dumps(response))
            return True
        except Exception as e:
            self.logger.error(f"Error caching agent response: {str(e)}")
            return False
    
    async def get_cached_agent_response(self, agent_name: str, request_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached agent response"""
        try:
            key = f"agent:{agent_name}:response:{request_hash}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            self.logger.error(f"Error retrieving cached agent response: {str(e)}")
            return None

class MemoryLayer:
    """Main memory layer orchestrator"""
    
    def __init__(self, db_path: str = "data/freelancex.db", redis_url: str = "redis://localhost:6379"):
        self.db_manager = DatabaseManager(db_path)
        self.redis_manager = RedisMemoryManager(redis_url)
        self.logger = logging.getLogger("FreelanceX.Memory")
    
    async def store_user_profile(self, profile: UserProfile) -> bool:
        """Store user profile in both database and cache"""
        try:
            # Save to database
            db_success = await self.db_manager.save_user_profile(profile)
            
            # Cache for quick access
            cache_success = await self.redis_manager.cache_user_data(
                profile.user_id, 
                "profile", 
                asdict(profile), 
                ttl=7200  # 2 hours
            )
            
            return db_success and cache_success
            
        except Exception as e:
            self.logger.error(f"Error storing user profile: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from cache or database"""
        try:
            # Try cache first
            cached_data = await self.redis_manager.get_cached_user_data(user_id, "profile")
            if cached_data:
                return UserProfile(**cached_data)
            
            # Fall back to database
            profile = await self.db_manager.get_user_profile(user_id)
            if profile:
                # Cache for future use
                await self.redis_manager.cache_user_data(
                    user_id, 
                    "profile", 
                    asdict(profile), 
                    ttl=7200
                )
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error retrieving user profile: {str(e)}")
            return None
    
    async def store_interaction(self, interaction: InteractionRecord) -> bool:
        """Store interaction record"""
        try:
            # Save to database
            success = await self.db_manager.save_interaction(interaction)
            
            # Update user activity cache
            if success:
                await self.redis_manager.cache_user_data(
                    interaction.user_id,
                    "last_activity",
                    {"timestamp": interaction.timestamp.isoformat(), "agent": interaction.agent_name},
                    ttl=3600
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error storing interaction: {str(e)}")
            return False
    
    async def get_user_interactions(self, user_id: str, limit: int = 100) -> List[InteractionRecord]:
        """Retrieve user interaction history"""
        try:
            return await self.db_manager.get_user_interactions(user_id, limit)
        except Exception as e:
            self.logger.error(f"Error retrieving user interactions: {str(e)}")
            return []
    
    async def store_job_record(self, job_record: JobRecord) -> bool:
        """Store job record in database"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO job_history 
                    (job_id, user_id, platform, title, description, budget, status,
                     applied_at, last_updated, notes, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_record.job_id,
                    job_record.user_id,
                    job_record.platform,
                    job_record.title,
                    job_record.description,
                    job_record.budget,
                    job_record.status,
                    job_record.applied_at.isoformat(),
                    job_record.last_updated.isoformat(),
                    job_record.notes,
                    json.dumps(job_record.tags)
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing job record: {str(e)}")
            return False
    
    async def get_user_job_history(self, user_id: str, status: Optional[str] = None) -> List[JobRecord]:
        """Retrieve user job history"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute("""
                        SELECT * FROM job_history 
                        WHERE user_id = ? AND status = ?
                        ORDER BY last_updated DESC
                    """, (user_id, status))
                else:
                    cursor.execute("""
                        SELECT * FROM job_history 
                        WHERE user_id = ?
                        ORDER BY last_updated DESC
                    """, (user_id,))
                
                job_records = []
                for row in cursor.fetchall():
                    job_records.append(JobRecord(
                        job_id=row[0],
                        user_id=row[1],
                        platform=row[2],
                        title=row[3],
                        description=row[4],
                        budget=row[5],
                        status=row[6],
                        applied_at=datetime.fromisoformat(row[7]),
                        last_updated=datetime.fromisoformat(row[8]),
                        notes=row[9],
                        tags=json.loads(row[10])
                    ))
                
                return job_records
                
        except Exception as e:
            self.logger.error(f"Error retrieving job history: {str(e)}")
            return []
    
    async def store_learning_data(self, learning_data: LearningData) -> bool:
        """Store learning data for system improvement"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO learning_data 
                    (data_id, user_id, data_type, content, timestamp, importance_score, usage_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    learning_data.data_id,
                    learning_data.user_id,
                    learning_data.data_type,
                    json.dumps(learning_data.content),
                    learning_data.timestamp.isoformat(),
                    learning_data.importance_score,
                    learning_data.usage_count
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing learning data: {str(e)}")
            return False
    
    async def get_learning_data(self, user_id: str, data_type: Optional[str] = None) -> List[LearningData]:
        """Retrieve learning data"""
        try:
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                if data_type:
                    cursor.execute("""
                        SELECT * FROM learning_data 
                        WHERE user_id = ? AND data_type = ?
                        ORDER BY importance_score DESC, timestamp DESC
                    """, (user_id, data_type))
                else:
                    cursor.execute("""
                        SELECT * FROM learning_data 
                        WHERE user_id = ?
                        ORDER BY importance_score DESC, timestamp DESC
                    """, (user_id,))
                
                learning_data_list = []
                for row in cursor.fetchall():
                    learning_data_list.append(LearningData(
                        data_id=row[0],
                        user_id=row[1],
                        data_type=row[2],
                        content=json.loads(row[3]),
                        timestamp=datetime.fromisoformat(row[4]),
                        importance_score=row[5],
                        usage_count=row[6]
                    ))
                
                return learning_data_list
                
        except Exception as e:
            self.logger.error(f"Error retrieving learning data: {str(e)}")
            return []
    
    async def generate_request_hash(self, request_content: Dict[str, Any]) -> str:
        """Generate hash for request content for caching"""
        content_str = json.dumps(request_content, sort_keys=True)
        return hashlib.md5(content_str.encode()).hexdigest()
    
    async def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data to prevent database bloat"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            with sqlite3.connect(self.db_manager.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean up old interactions
                cursor.execute("""
                    DELETE FROM interaction_history 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                # Clean up old learning data with low importance
                cursor.execute("""
                    DELETE FROM learning_data 
                    WHERE timestamp < ? AND importance_score < 0.5
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                self.logger.info(f"Cleaned up data older than {days_to_keep} days")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    async def test_memory_layer():
        """Test the memory layer functionality"""
        memory = MemoryLayer()
        
        # Test user profile
        profile = UserProfile(
            user_id="test_user_123",
            name="John Doe",
            email="john@example.com",
            skills=["Python", "AI", "Web Development"],
            experience_years=5,
            preferred_hourly_rate=75.0,
            location="San Francisco, CA",
            timezone="America/Los_Angeles",
            work_schedule={"monday": "9-17", "tuesday": "9-17"},
            goals=["Increase income", "Learn new technologies"],
            preferences={"remote_work": True, "project_length": "long_term"},
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        # Store profile
        success = await memory.store_user_profile(profile)
        print(f"Profile stored: {success}")
        
        # Retrieve profile
        retrieved_profile = await memory.get_user_profile("test_user_123")
        print(f"Profile retrieved: {retrieved_profile is not None}")
        
        if retrieved_profile:
            print(f"User name: {retrieved_profile.name}")
            print(f"Skills: {retrieved_profile.skills}")
    
    asyncio.run(test_memory_layer())