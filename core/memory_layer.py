#!/usr/bin/env python3
"""
FreelanceX.AI Memory Layer
User data storage, preferences, and legacy memory management
"""

import asyncio
import logging
import json
import sqlite3
import hashlib
import pickle
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import aiosqlite
from enum import Enum

class MemoryType(Enum):
    """Types of memory stored in the system"""
    USER_PROFILE = "user_profile"
    INTERACTION_HISTORY = "interaction_history"
    PREFERENCES = "preferences"
    LEARNING_DATA = "learning_data"
    JOB_HISTORY = "job_history"
    RESEARCH_DATA = "research_data"
    CALCULATION_HISTORY = "calculation_history"

@dataclass
class UserProfile:
    """Comprehensive user profile data"""
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
    is_active: bool = True

@dataclass
class InteractionRecord:
    """Record of user interactions with the system"""
    interaction_id: str
    user_id: str
    agent_name: str
    interaction_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    timestamp: datetime
    duration: float
    success: bool
    feedback_score: Optional[float] = None

@dataclass
class LearningData:
    """Data for system learning and improvement"""
    data_id: str
    user_id: str
    data_type: str
    content: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0

class MemoryLayer:
    """
    Centralized memory management for FreelanceX.AI
    Handles user data, preferences, and legacy memory
    """
    
    def __init__(self, db_path: str = "data/freelancex_memory.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("FreelanceX.MemoryLayer")
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        asyncio.create_task(self._initialize_database())
        
        # Memory cache for frequently accessed data
        self.memory_cache: Dict[str, Any] = {}
        self.cache_ttl: Dict[str, datetime] = {}
        self.cache_duration = timedelta(minutes=30)
        
        # Encryption key for sensitive data
        self.encryption_key = self._generate_encryption_key()
        
        self.logger.info("FreelanceX.AI Memory Layer initialized")
    
    def _generate_encryption_key(self) -> str:
        """Generate encryption key for sensitive data"""
        # In production, this should be stored securely
        return hashlib.sha256("freelancex-memory-key".encode()).hexdigest()
    
    async def _initialize_database(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # User profiles table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    skills TEXT,
                    experience_years INTEGER,
                    preferred_hourly_rate REAL,
                    location TEXT,
                    timezone TEXT,
                    work_schedule TEXT,
                    goals TEXT,
                    preferences TEXT,
                    created_at TEXT,
                    last_updated TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Interaction history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS interaction_history (
                    interaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    interaction_type TEXT NOT NULL,
                    input_data TEXT,
                    output_data TEXT,
                    timestamp TEXT NOT NULL,
                    duration REAL,
                    success BOOLEAN,
                    feedback_score REAL,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            # Learning data table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS learning_data (
                    data_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    content TEXT,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            # Job history table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS job_history (
                    job_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    platform TEXT,
                    budget REAL,
                    status TEXT,
                    applied_at TEXT,
                    result TEXT,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            # Research data table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS research_data (
                    research_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    sources TEXT,
                    findings TEXT,
                    created_at TEXT NOT NULL,
                    last_updated TEXT,
                    relevance_score REAL,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """)
            
            await db.commit()
            self.logger.info("Database tables initialized successfully")
    
    async def store_user_profile(self, profile: UserProfile) -> bool:
        """Store or update user profile"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, name, email, skills, experience_years, preferred_hourly_rate,
                     location, timezone, work_schedule, goals, preferences, created_at, last_updated, is_active)
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
                    profile.is_active
                ))
                await db.commit()
                
                # Update cache
                cache_key = f"profile:{profile.user_id}"
                self.memory_cache[cache_key] = profile
                self.cache_ttl[cache_key] = datetime.now() + self.cache_duration
                
                self.logger.info(f"User profile stored for {profile.user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store user profile: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile from memory"""
        # Check cache first
        cache_key = f"profile:{user_id}"
        if cache_key in self.memory_cache and datetime.now() < self.cache_ttl[cache_key]:
            return self.memory_cache[cache_key]
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    "SELECT * FROM user_profiles WHERE user_id = ?", (user_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    
                    if row:
                        profile = UserProfile(
                            user_id=row[0],
                            name=row[1],
                            email=row[2],
                            skills=json.loads(row[3]) if row[3] else [],
                            experience_years=row[4],
                            preferred_hourly_rate=row[5],
                            location=row[6],
                            timezone=row[7],
                            work_schedule=json.loads(row[8]) if row[8] else {},
                            goals=json.loads(row[9]) if row[9] else [],
                            preferences=json.loads(row[10]) if row[10] else {},
                            created_at=datetime.fromisoformat(row[11]),
                            last_updated=datetime.fromisoformat(row[12]),
                            is_active=bool(row[13])
                        )
                        
                        # Update cache
                        self.memory_cache[cache_key] = profile
                        self.cache_ttl[cache_key] = datetime.now() + self.cache_duration
                        
                        return profile
                    
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve user profile: {str(e)}")
            return None
    
    async def store_interaction(self, interaction: InteractionRecord) -> bool:
        """Store interaction record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO interaction_history 
                    (interaction_id, user_id, agent_name, interaction_type, input_data,
                     output_data, timestamp, duration, success, feedback_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.interaction_id,
                    interaction.user_id,
                    interaction.agent_name,
                    interaction.interaction_type,
                    json.dumps(interaction.input_data),
                    json.dumps(interaction.output_data),
                    interaction.timestamp.isoformat(),
                    interaction.duration,
                    interaction.success,
                    interaction.feedback_score
                ))
                await db.commit()
                
                self.logger.info(f"Interaction stored: {interaction.interaction_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store interaction: {str(e)}")
            return False
    
    async def get_interaction_history(self, user_id: str, limit: int = 100) -> List[InteractionRecord]:
        """Retrieve interaction history for a user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT * FROM interaction_history 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (user_id, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
                    interactions = []
                    for row in rows:
                        interaction = InteractionRecord(
                            interaction_id=row[0],
                            user_id=row[1],
                            agent_name=row[2],
                            interaction_type=row[3],
                            input_data=json.loads(row[4]) if row[4] else {},
                            output_data=json.loads(row[5]) if row[5] else {},
                            timestamp=datetime.fromisoformat(row[6]),
                            duration=row[7],
                            success=bool(row[8]),
                            feedback_score=row[9]
                        )
                        interactions.append(interaction)
                    
                    return interactions
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve interaction history: {str(e)}")
            return []
    
    async def store_learning_data(self, learning_data: LearningData) -> bool:
        """Store learning data for system improvement"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO learning_data 
                    (data_id, user_id, data_type, content, created_at, last_accessed, access_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    learning_data.data_id,
                    learning_data.user_id,
                    learning_data.data_type,
                    json.dumps(learning_data.content),
                    learning_data.created_at.isoformat(),
                    learning_data.last_accessed.isoformat(),
                    learning_data.access_count
                ))
                await db.commit()
                
                self.logger.info(f"Learning data stored: {learning_data.data_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store learning data: {str(e)}")
            return False
    
    async def get_learning_data(self, user_id: str, data_type: str = None) -> List[LearningData]:
        """Retrieve learning data for a user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if data_type:
                    query = "SELECT * FROM learning_data WHERE user_id = ? AND data_type = ?"
                    params = (user_id, data_type)
                else:
                    query = "SELECT * FROM learning_data WHERE user_id = ?"
                    params = (user_id,)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    learning_data_list = []
                    for row in rows:
                        learning_data = LearningData(
                            data_id=row[0],
                            user_id=row[1],
                            data_type=row[2],
                            content=json.loads(row[3]) if row[3] else {},
                            created_at=datetime.fromisoformat(row[4]),
                            last_accessed=datetime.fromisoformat(row[5]),
                            access_count=row[6]
                        )
                        learning_data_list.append(learning_data)
                    
                    return learning_data_list
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve learning data: {str(e)}")
            return []
    
    async def store_job_history(self, job_data: Dict[str, Any]) -> bool:
        """Store job application history"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO job_history 
                    (job_id, user_id, job_title, platform, budget, status, applied_at, result, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    job_data.get('job_id'),
                    job_data.get('user_id'),
                    job_data.get('job_title'),
                    job_data.get('platform'),
                    job_data.get('budget'),
                    job_data.get('status'),
                    job_data.get('applied_at'),
                    job_data.get('result'),
                    job_data.get('notes')
                ))
                await db.commit()
                
                self.logger.info(f"Job history stored: {job_data.get('job_id')}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store job history: {str(e)}")
            return False
    
    async def get_job_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieve job history for a user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT * FROM job_history 
                    WHERE user_id = ? 
                    ORDER BY applied_at DESC
                """, (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    job_history = []
                    for row in rows:
                        job_data = {
                            'job_id': row[0],
                            'user_id': row[1],
                            'job_title': row[2],
                            'platform': row[3],
                            'budget': row[4],
                            'status': row[5],
                            'applied_at': row[6],
                            'result': row[7],
                            'notes': row[8]
                        }
                        job_history.append(job_data)
                    
                    return job_history
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve job history: {str(e)}")
            return []
    
    async def store_research_data(self, research_data: Dict[str, Any]) -> bool:
        """Store research findings"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO research_data 
                    (research_id, user_id, topic, sources, findings, created_at, last_updated, relevance_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    research_data.get('research_id'),
                    research_data.get('user_id'),
                    research_data.get('topic'),
                    json.dumps(research_data.get('sources', [])),
                    json.dumps(research_data.get('findings', {})),
                    research_data.get('created_at'),
                    research_data.get('last_updated'),
                    research_data.get('relevance_score', 0.0)
                ))
                await db.commit()
                
                self.logger.info(f"Research data stored: {research_data.get('research_id')}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to store research data: {str(e)}")
            return False
    
    async def get_research_data(self, user_id: str, topic: str = None) -> List[Dict[str, Any]]:
        """Retrieve research data for a user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if topic:
                    query = "SELECT * FROM research_data WHERE user_id = ? AND topic LIKE ?"
                    params = (user_id, f"%{topic}%")
                else:
                    query = "SELECT * FROM research_data WHERE user_id = ? ORDER BY created_at DESC"
                    params = (user_id,)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                    research_data_list = []
                    for row in rows:
                        research_data = {
                            'research_id': row[0],
                            'user_id': row[1],
                            'topic': row[2],
                            'sources': json.loads(row[3]) if row[3] else [],
                            'findings': json.loads(row[4]) if row[4] else {},
                            'created_at': row[5],
                            'last_updated': row[6],
                            'relevance_score': row[7]
                        }
                        research_data_list.append(research_data)
                    
                    return research_data_list
                    
        except Exception as e:
            self.logger.error(f"Failed to retrieve research data: {str(e)}")
            return []
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences from profile"""
        profile = await self.get_user_profile(user_id)
        if profile:
            return profile.preferences
        return {}
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        profile = await self.get_user_profile(user_id)
        if profile:
            profile.preferences.update(preferences)
            profile.last_updated = datetime.now()
            return await self.store_user_profile(profile)
        return False
    
    async def get_system_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # Count records in each table
                tables = ['user_profiles', 'interaction_history', 'learning_data', 'job_history', 'research_data']
                for table in tables:
                    async with db.execute(f"SELECT COUNT(*) FROM {table}") as cursor:
                        count = await cursor.fetchone()
                        stats[f"{table}_count"] = count[0] if count else 0
                
                # Cache statistics
                stats['cache_size'] = len(self.memory_cache)
                stats['cache_entries'] = list(self.memory_cache.keys())
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {str(e)}")
            return {}
    
    async def clear_user_data(self, user_id: str) -> bool:
        """Clear all data for a user (GDPR compliance)"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                tables = ['user_profiles', 'interaction_history', 'learning_data', 'job_history', 'research_data']
                
                for table in tables:
                    await db.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
                
                await db.commit()
                
                # Clear from cache
                cache_key = f"profile:{user_id}"
                if cache_key in self.memory_cache:
                    del self.memory_cache[cache_key]
                    del self.cache_ttl[cache_key]
                
                self.logger.info(f"All data cleared for user: {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to clear user data: {str(e)}")
            return False
    
    async def cleanup_old_data(self, days_old: int = 90) -> int:
        """Clean up old data to maintain performance"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_count = 0
            
            async with aiosqlite.connect(self.db_path) as db:
                # Clean up old interactions
                async with db.execute("""
                    DELETE FROM interaction_history 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),)) as cursor:
                    deleted_count += cursor.rowcount
                
                # Clean up old learning data
                async with db.execute("""
                    DELETE FROM learning_data 
                    WHERE last_accessed < ?
                """, (cutoff_date.isoformat(),)) as cursor:
                    deleted_count += cursor.rowcount
                
                await db.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old records")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {str(e)}")
            return 0