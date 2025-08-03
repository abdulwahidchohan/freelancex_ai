"""
FreelanceX.AI Memory Management System
SQLite-based storage for user interactions, context, and learning data
"""

import asyncio
import sqlite3
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import aiosqlite
import hashlib

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    SQLite-based memory manager for FreelanceX.AI
    Stores user interactions, context, and learning data
    """
    
    def __init__(self, db_path: str = "data/freelancex_memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        
    async def initialize(self):
        """Initialize the memory system and create tables"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            logger.info("✅ Memory system initialized")
        except Exception as e:
            logger.error(f"❌ Memory initialization failed: {str(e)}")
            raise
    
    async def _create_tables(self):
        """Create necessary database tables"""
        async with self.connection.cursor() as cursor:
            # User interactions table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    input_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT,
                    importance_score REAL DEFAULT 0.5,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User profiles table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    name TEXT,
                    skills TEXT,
                    preferences TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Task history table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    agent_used TEXT,
                    success BOOLEAN,
                    response_time REAL,
                    timestamp TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Learning data table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    success_rate REAL,
                    usage_count INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_history_user_id ON task_history(user_id)")
            await cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_data_user_id ON learning_data(user_id)")
            
        await self.connection.commit()
        logger.info("📊 Database tables created successfully")
    
    async def log_interaction(self, user_id: str, input_type: str, content: str, 
                            timestamp: str = None, metadata: Dict[str, Any] = None,
                            importance_score: float = 0.5):
        """Log a user interaction"""
        try:
            if timestamp is None:
                timestamp = datetime.now().isoformat()
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO interactions (user_id, input_type, content, timestamp, metadata, importance_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (user_id, input_type, content, timestamp, metadata_json, importance_score))
            
            await self.connection.commit()
            logger.debug(f"📝 Logged interaction for user {user_id}: {input_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log interaction: {str(e)}")
    
    async def get_recent_interactions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent interactions for a user"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT input_type, content, timestamp, metadata, importance_score
                    FROM interactions
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (user_id, limit))
                
                rows = await cursor.fetchall()
                
                interactions = []
                for row in rows:
                    interactions.append({
                        'input_type': row[0],
                        'content': row[1],
                        'timestamp': row[2],
                        'metadata': json.loads(row[3]) if row[3] else None,
                        'importance_score': row[4]
                    })
                
                return interactions
                
        except Exception as e:
            logger.error(f"❌ Failed to get recent interactions: {str(e)}")
            return []
    
    async def search_interactions(self, user_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search interactions by content"""
        try:
            search_pattern = f"%{query}%"
            
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT input_type, content, timestamp, metadata, importance_score
                    FROM interactions
                    WHERE user_id = ? AND content LIKE ?
                    ORDER BY importance_score DESC, timestamp DESC
                    LIMIT ?
                """, (user_id, search_pattern, limit))
                
                rows = await cursor.fetchall()
                
                interactions = []
                for row in rows:
                    interactions.append({
                        'input_type': row[0],
                        'content': row[1],
                        'timestamp': row[2],
                        'metadata': json.loads(row[3]) if row[3] else None,
                        'importance_score': row[4]
                    })
                
                return interactions
                
        except Exception as e:
            logger.error(f"❌ Failed to search interactions: {str(e)}")
            return []
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    SELECT name, skills, preferences, created_at, updated_at
                    FROM user_profiles
                    WHERE user_id = ?
                """, (user_id,))
                
                row = await cursor.fetchone()
                
                if row:
                    return {
                        'user_id': user_id,
                        'name': row[0],
                        'skills': json.loads(row[1]) if row[1] else [],
                        'preferences': json.loads(row[2]) if row[2] else {},
                        'created_at': row[3],
                        'updated_at': row[4]
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to get user profile: {str(e)}")
            return None
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Update user profile"""
        try:
            name = profile_data.get('name')
            skills = json.dumps(profile_data.get('skills', []))
            preferences = json.dumps(profile_data.get('preferences', {}))
            updated_at = datetime.now().isoformat()
            
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT OR REPLACE INTO user_profiles (user_id, name, skills, preferences, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, name, skills, preferences, updated_at))
            
            await self.connection.commit()
            logger.info(f"👤 Updated profile for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update user profile: {str(e)}")
    
    async def log_task_execution(self, user_id: str, task_type: str, agent_used: str,
                               success: bool, response_time: float, metadata: Dict[str, Any] = None):
        """Log task execution for analytics"""
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            timestamp = datetime.now().isoformat()
            
            async with self.connection.cursor() as cursor:
                await cursor.execute("""
                    INSERT INTO task_history (user_id, task_type, agent_used, success, response_time, timestamp, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, task_type, agent_used, success, response_time, timestamp, metadata_json))
            
            await self.connection.commit()
            logger.debug(f"📊 Logged task execution: {task_type} by {agent_used}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log task execution: {str(e)}")
    
    async def get_task_statistics(self, user_id: str = None, days: int = 30) -> Dict[str, Any]:
        """Get task execution statistics"""
        try:
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            async with self.connection.cursor() as cursor:
                if user_id:
                    await cursor.execute("""
                        SELECT task_type, agent_used, success, response_time
                        FROM task_history
                        WHERE user_id = ? AND timestamp >= ?
                    """, (user_id, since_date))
                else:
                    await cursor.execute("""
                        SELECT task_type, agent_used, success, response_time
                        FROM task_history
                        WHERE timestamp >= ?
                    """, (since_date,))
                
                rows = await cursor.fetchall()
                
                stats = {
                    'total_tasks': len(rows),
                    'successful_tasks': sum(1 for row in rows if row[2]),
                    'task_types': {},
                    'agent_performance': {},
                    'avg_response_time': 0
                }
                
                response_times = []
                for row in rows:
                    task_type, agent_used, success, response_time = row
                    
                    # Task type stats
                    if task_type not in stats['task_types']:
                        stats['task_types'][task_type] = {'total': 0, 'successful': 0}
                    stats['task_types'][task_type]['total'] += 1
                    if success:
                        stats['task_types'][task_type]['successful'] += 1
                    
                    # Agent performance stats
                    if agent_used not in stats['agent_performance']:
                        stats['agent_performance'][agent_used] = {'total': 0, 'successful': 0, 'total_time': 0}
                    stats['agent_performance'][agent_used]['total'] += 1
                    if success:
                        stats['agent_performance'][agent_used]['successful'] += 1
                    stats['agent_performance'][agent_used]['total_time'] += response_time
                    
                    response_times.append(response_time)
                
                # Calculate averages
                if response_times:
                    stats['avg_response_time'] = sum(response_times) / len(response_times)
                
                # Calculate success rates
                for task_type in stats['task_types']:
                    total = stats['task_types'][task_type]['total']
                    successful = stats['task_types'][task_type]['successful']
                    stats['task_types'][task_type]['success_rate'] = successful / total if total > 0 else 0
                
                for agent in stats['agent_performance']:
                    total = stats['agent_performance'][agent]['total']
                    successful = stats['agent_performance'][agent]['successful']
                    total_time = stats['agent_performance'][agent]['total_time']
                    stats['agent_performance'][agent]['success_rate'] = successful / total if total > 0 else 0
                    stats['agent_performance'][agent]['avg_response_time'] = total_time / total if total > 0 else 0
                
                return stats
                
        except Exception as e:
            logger.error(f"❌ Failed to get task statistics: {str(e)}")
            return {}
    
    async def store_learning_pattern(self, user_id: str, pattern_type: str, pattern_data: Dict[str, Any],
                                   success_rate: float = 0.5):
        """Store learning pattern for future reference"""
        try:
            pattern_hash = hashlib.md5(json.dumps(pattern_data, sort_keys=True).encode()).hexdigest()
            pattern_json = json.dumps(pattern_data)
            updated_at = datetime.now().isoformat()
            
            async with self.connection.cursor() as cursor:
                # Check if pattern already exists
                await cursor.execute("""
                    SELECT id, usage_count, success_rate
                    FROM learning_data
                    WHERE user_id = ? AND pattern_type = ? AND pattern_data = ?
                """, (user_id, pattern_type, pattern_json))
                
                existing = await cursor.fetchone()
                
                if existing:
                    # Update existing pattern
                    pattern_id, usage_count, old_success_rate = existing
                    new_usage_count = usage_count + 1
                    new_success_rate = (old_success_rate * usage_count + success_rate) / new_usage_count
                    
                    await cursor.execute("""
                        UPDATE learning_data
                        SET usage_count = ?, success_rate = ?, updated_at = ?
                        WHERE id = ?
                    """, (new_usage_count, new_success_rate, updated_at, pattern_id))
                else:
                    # Insert new pattern
                    await cursor.execute("""
                        INSERT INTO learning_data (user_id, pattern_type, pattern_data, success_rate, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user_id, pattern_type, pattern_json, success_rate, updated_at))
            
            await self.connection.commit()
            logger.debug(f"🧠 Stored learning pattern: {pattern_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to store learning pattern: {str(e)}")
    
    async def get_learning_patterns(self, user_id: str, pattern_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get learning patterns for a user"""
        try:
            async with self.connection.cursor() as cursor:
                if pattern_type:
                    await cursor.execute("""
                        SELECT pattern_type, pattern_data, success_rate, usage_count, updated_at
                        FROM learning_data
                        WHERE user_id = ? AND pattern_type = ?
                        ORDER BY success_rate DESC, usage_count DESC
                        LIMIT ?
                    """, (user_id, pattern_type, limit))
                else:
                    await cursor.execute("""
                        SELECT pattern_type, pattern_data, success_rate, usage_count, updated_at
                        FROM learning_data
                        WHERE user_id = ?
                        ORDER BY success_rate DESC, usage_count DESC
                        LIMIT ?
                    """, (user_id, limit))
                
                rows = await cursor.fetchall()
                
                patterns = []
                for row in rows:
                    patterns.append({
                        'pattern_type': row[0],
                        'pattern_data': json.loads(row[1]),
                        'success_rate': row[2],
                        'usage_count': row[3],
                        'updated_at': row[4]
                    })
                
                return patterns
                
        except Exception as e:
            logger.error(f"❌ Failed to get learning patterns: {str(e)}")
            return []
    
    async def cleanup_old_data(self, days: int = 365):
        """Clean up old data to prevent database bloat"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            async with self.connection.cursor() as cursor:
                # Clean up old interactions
                await cursor.execute("""
                    DELETE FROM interactions
                    WHERE timestamp < ? AND importance_score < 0.7
                """, (cutoff_date,))
                
                # Clean up old task history
                await cursor.execute("""
                    DELETE FROM task_history
                    WHERE timestamp < ?
                """, (cutoff_date,))
                
                # Clean up unused learning patterns
                await cursor.execute("""
                    DELETE FROM learning_data
                    WHERE usage_count < 3 AND updated_at < ?
                """, (cutoff_date,))
            
            await self.connection.commit()
            logger.info(f"🧹 Cleaned up data older than {days} days")
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {str(e)}")
    
    async def close(self):
        """Close the database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("🔒 Memory system connection closed") 