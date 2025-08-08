#!/usr/bin/env python3
"""
FreelanceX.AI SQLite Memory Management System
Persistent memory storage using SQLite with OpenAI Agent SDK integration
"""

import os
import json
import logging
import asyncio
import aiosqlite
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from openai import OpenAI

# Use SDK Session protocol types for typing only, we will persist minimal metadata
try:  # pragma: no cover
    from agents.memory import Session as AgentSessionProtocol
except Exception:  # pragma: no cover
    from typing import Protocol as AgentSessionProtocol  # type: ignore

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a memory entry in the system"""
    id: str
    user_id: str
    agent_name: str
    content: str
    memory_type: str
    importance: float
    created_at: datetime
    last_accessed: datetime
    access_count: int
    metadata: Dict[str, Any]
    tags: List[str]
    context: str
    is_active: bool = True

class SQLiteMemoryManager:
    """
    SQLite-based memory management system
    Integrates with OpenAI Agent SDK sessions for enhanced memory management
    """
    
    def __init__(self, db_path: str = "memory.db"):
        self.db_path = db_path
        self.initialized = False
        
        # OpenAI Agent SDK session storage
        self.active_sessions: Dict[str, AgentSessionProtocol] = {}
        
        # Memory cache for performance
        self.memory_cache: Dict[str, MemoryEntry] = {}
        self.cache_size = 1000
        self.cache_ttl = timedelta(hours=1)
        
        logger.info(f"SQLiteMemoryManager initialized with database: {db_path}")
        
    async def initialize(self):
        """Initialize the database and create tables"""
        if self.initialized:
            return
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Create memory entries table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        content TEXT NOT NULL,
                        memory_type TEXT NOT NULL,
                        bucket TEXT NOT NULL DEFAULT 'short',
                        importance REAL DEFAULT 0.5,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        access_count INTEGER DEFAULT 0,
                        metadata TEXT,
                        tags TEXT,
                        context TEXT,
                        is_active INTEGER DEFAULT 1
                    )
                """)
            
                # Create user profiles table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id TEXT PRIMARY KEY,
                        name TEXT,
                        email TEXT,
                        preferences TEXT,
                        created_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        is_active INTEGER DEFAULT 1
                    )
                """)
            
                # Create agent sessions table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS agent_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        agent_name TEXT NOT NULL,
                        session_data TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        last_accessed TEXT NOT NULL,
                        is_active INTEGER DEFAULT 1
                    )
                """)
            
            # Create indexes for better performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_user_agent ON memory_entries(user_id, agent_name)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_type_importance ON memory_entries(memory_type, importance)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_memory_last_accessed ON memory_entries(last_accessed)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_agent_sessions_user_id ON agent_sessions(user_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_name ON agent_sessions(agent_name)")
                
                await db.commit()
                
            self.initialized = True
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def store_memory(self, 
                          user_id: str, 
                          agent_name: str, 
                          content: str, 
                          memory_type: str = "general",
                          bucket: str = "short",
                          importance: float = 0.5,
                          metadata: Dict[str, Any] = None,
                          tags: List[str] = None,
                          context: str = "") -> str:
        """
        Store a new memory entry
        
        Args:
            user_id: User identifier
            agent_name: Name of the agent that created the memory
            content: Memory content
            memory_type: Type of memory (general, task, conversation, etc.)
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            tags: Tags for categorization
            context: Context information
            
        Returns:
            str: Memory entry ID
        """
        await self.initialize()
        
        memory_id = f"mem_{user_id}_{agent_name}_{datetime.now().timestamp()}"
        now = datetime.now().isoformat()
        
        memory_entry = MemoryEntry(
            id=memory_id,
            user_id=user_id,
            agent_name=agent_name,
            content=content,
            memory_type=memory_type,
            importance=importance,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=0,
            metadata=metadata or {},
            tags=tags or [],
            context=context
        )
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO memory_entries 
                    (id, user_id, agent_name, content, memory_type, bucket, importance, 
                     created_at, last_accessed, access_count, metadata, tags, context, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id, user_id, agent_name, content, memory_type, bucket, importance,
                    now, now, 0, json.dumps(metadata or {}), json.dumps(tags or []), context, True
                ))
                await db.commit()
                
            # Add to cache
            self.memory_cache[memory_id] = memory_entry
            
            logger.info(f"Stored memory entry: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            raise
    
    async def retrieve_memory(self, 
                             user_id: str, 
                             agent_name: str = None,
                             memory_type: str = None,
                              bucket: str = None,
                             limit: int = 10,
                             min_importance: float = 0.0) -> List[MemoryEntry]:
        """
        Retrieve memory entries based on criteria
        
        Args:
            user_id: User identifier
            agent_name: Filter by agent name (optional)
            memory_type: Filter by memory type (optional)
            limit: Maximum number of entries to return
            min_importance: Minimum importance threshold
            
        Returns:
            List[MemoryEntry]: List of memory entries
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = """
                    SELECT id, user_id, agent_name, content, memory_type, importance,
                           created_at, last_accessed, access_count, metadata, tags, context, is_active
                    FROM memory_entries 
                    WHERE user_id = ? AND is_active = 1 AND importance >= ?
                """
                params = [user_id, min_importance]
                
                if agent_name:
                    query += " AND agent_name = ?"
                    params.append(agent_name)
                    
                if memory_type:
                    query += " AND memory_type = ?"
                    params.append(memory_type)
                if bucket:
                    query += " AND bucket = ?"
                    params.append(bucket)
                    
                query += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
                params.append(limit)
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    
                memory_entries = []
                for row in rows:
                    memory_entry = MemoryEntry(
                        id=row[0],
                        user_id=row[1],
                        agent_name=row[2],
                        content=row[3],
                        memory_type=row[4],
                        importance=row[5],
                        created_at=datetime.fromisoformat(row[6]),
                        last_accessed=datetime.fromisoformat(row[7]),
                        access_count=row[8],
                        metadata=json.loads(row[9]),
                        tags=json.loads(row[10]),
                        context=row[11],
                        is_active=bool(row[12])
                    )
                    memory_entries.append(memory_entry)
                    
                    # Update cache
                    self.memory_cache[memory_entry.id] = memory_entry
                
                # Update access count and last accessed
                if memory_entries:
                    await self._update_access_stats([entry.id for entry in memory_entries])
                
                return memory_entries
                
        except Exception as e:
            logger.error(f"Failed to retrieve memory: {str(e)}")
            return []
    
    async def search_memory(self, 
                           user_id: str, 
                           query: str, 
                           limit: int = 10) -> List[MemoryEntry]:
        """
        Search memory entries using text search
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[MemoryEntry]: List of matching memory entries
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Simple text search - could be enhanced with full-text search
                search_query = f"%{query}%"
                
                async with db.execute("""
                    SELECT id, user_id, agent_name, content, memory_type, importance,
                           created_at, last_accessed, access_count, metadata, tags, context, is_active
                    FROM memory_entries 
                    WHERE user_id = ? AND is_active = 1 
                    AND (content LIKE ? OR context LIKE ? OR tags LIKE ?)
                    ORDER BY importance DESC, last_accessed DESC 
                    LIMIT ?
                """, (user_id, search_query, search_query, search_query, limit)) as cursor:
                    rows = await cursor.fetchall()
                    
                    memory_entries = []
                    for row in rows:
                        memory_entry = MemoryEntry(
                            id=row[0],
                            user_id=row[1],
                            agent_name=row[2],
                            content=row[3],
                            memory_type=row[4],
                            importance=row[5],
                            created_at=datetime.fromisoformat(row[6]),
                            last_accessed=datetime.fromisoformat(row[7]),
                            access_count=row[8],
                            metadata=json.loads(row[9]),
                            tags=json.loads(row[10]),
                            context=row[11],
                            is_active=bool(row[12])
                        )
                        memory_entries.append(memory_entry)
                    
                    return memory_entries
                
        except Exception as e:
            logger.error(f"Failed to search memory: {str(e)}")
            return []
    
    async def update_memory(self, 
                           memory_id: str, 
                           content: str = None,
                           importance: float = None,
                           metadata: Dict[str, Any] = None,
                           tags: List[str] = None) -> bool:
        """
        Update an existing memory entry
        
        Args:
            memory_id: Memory entry ID
            content: New content (optional)
            importance: New importance score (optional)
            metadata: New metadata (optional)
            tags: New tags (optional)
            
        Returns:
            bool: Success status
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                update_parts = []
                params = []
                
                if content is not None:
                    update_parts.append("content = ?")
                    params.append(content)
                    
                if importance is not None:
                    update_parts.append("importance = ?")
                    params.append(importance)
                    
                if metadata is not None:
                    update_parts.append("metadata = ?")
                    params.append(json.dumps(metadata))
                    
                if tags is not None:
                    update_parts.append("tags = ?")
                    params.append(json.dumps(tags))
                
                if not update_parts:
                    return False
                
                update_parts.append("last_accessed = ?")
                params.append(datetime.now().isoformat())
                params.append(memory_id)
                
                query = f"UPDATE memory_entries SET {', '.join(update_parts)} WHERE id = ?"
                
                await db.execute(query, params)
                await db.commit()
                
                # Update cache
                if memory_id in self.memory_cache:
                    cached_entry = self.memory_cache[memory_id]
                    if content is not None:
                        cached_entry.content = content
                    if importance is not None:
                        cached_entry.importance = importance
                    if metadata is not None:
                        cached_entry.metadata = metadata
                    if tags is not None:
                        cached_entry.tags = tags
                    cached_entry.last_accessed = datetime.now()
                
                logger.info(f"Updated memory entry: {memory_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to update memory: {str(e)}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Soft delete a memory entry
        
        Args:
            memory_id: Memory entry ID
            
        Returns:
            bool: Success status
        """
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE memory_entries SET is_active = 0 WHERE id = ?", (memory_id,))
                await db.commit()
                
            # Remove from cache
            if memory_id in self.memory_cache:
                del self.memory_cache[memory_id]
            
            logger.info(f"Deleted memory entry: {memory_id}")
            return True
                
        except Exception as e:
            logger.error(f"Failed to delete memory: {str(e)}")
            return False
    
    async def store_session(self, session_id: str, user_id: str, agent_name: str, session: AgentSessionProtocol):
        """Store an OpenAI Agent SDK session"""
        await self.initialize()
        
        try:
            # Store session in memory
            self.active_sessions[session_id] = session
            
            # Store minimal session data (opaque)
            session_data = {"session_id": getattr(session, "session_id", session_id)}
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO agent_sessions 
                    (session_id, user_id, agent_name, session_data, created_at, last_accessed, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (session_id, user_id, agent_name, json.dumps(session_data), 
                     datetime.now().isoformat(), datetime.now().isoformat(), True))
                await db.commit()
                
            logger.info(f"Stored session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to store session: {str(e)}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[AgentSessionProtocol]:
        """Retrieve an OpenAI Agent SDK session"""
        await self.initialize()
        
        try:
            # Check memory first
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # Check database
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute("""
                    SELECT session_data FROM agent_sessions 
                    WHERE session_id = ? AND is_active = 1
                """, (session_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                if row:
                    _ = json.loads(row[0])
                    # Return the in-memory instance if present; otherwise, no reconstruction
                    session = self.active_sessions.get(session_id)
                    
                    # Update last accessed
                    await db.execute("""
                        UPDATE agent_sessions 
                        SET last_accessed = ?
                        WHERE session_id = ?
                    """, (datetime.now().isoformat(), session_id))
                    await db.commit()
                    
                    # Store in memory
                    self.active_sessions[session_id] = session
                
                    return session
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session: {str(e)}")
            return None
    
    async def list_sessions(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all sessions"""
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if user_id:
                    async with db.execute("""
                        SELECT session_id, agent_name, session_data, created_at, last_accessed, is_active
                        FROM agent_sessions 
                        WHERE user_id = ? AND is_active = 1
                        ORDER BY last_accessed DESC
                    """, (user_id,)) as cursor:
                        rows = await cursor.fetchall()
                else:
                    async with db.execute("""
                    SELECT session_id, agent_name, session_data, created_at, last_accessed, is_active
                    FROM agent_sessions
                        WHERE is_active = 1
                    ORDER BY last_accessed DESC
                    """) as cursor:
                        rows = await cursor.fetchall()
                        
                        sessions = []
                        for row in rows:
                            sessions.append({
                                'session_id': row[0],
                                'agent_name': row[1],
                                'created_at': row[3],
                                'last_accessed': row[4],
                                'is_active': bool(row[5])
                            })
                        
                        return sessions
                
        except Exception as e:
            logger.error(f"Failed to list sessions: {str(e)}")
            return []
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        await self.initialize()
        
        try:
            # Remove from memory
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Remove from database
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE agent_sessions SET is_active = 0 WHERE session_id = ?", (session_id,))
                await db.commit()
                
            logger.info(f"Deleted session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session: {str(e)}")
            return False
    
    async def _update_access_stats(self, memory_ids: List[str]):
        """Update access statistics for memory entries"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                now = datetime.now().isoformat()
                for memory_id in memory_ids:
                    await db.execute("""
                        UPDATE memory_entries 
                        SET access_count = access_count + 1, last_accessed = ?
                        WHERE id = ?
                    """, (now, memory_id))
                await db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update access stats: {str(e)}")
    
    async def cleanup_old_memory(self, days: int = 30):
        """Clean up old memory entries"""
        await self.initialize()
        
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE memory_entries 
                    SET is_active = 0 
                    WHERE created_at < ? AND importance < 0.3
                """, (cutoff_date,))
                await db.commit()
                
            logger.info(f"Cleaned up memory entries older than {days} days")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old memory: {str(e)}")
    
    async def get_memory_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get memory statistics"""
        await self.initialize()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if user_id:
                    async with db.execute("""
                        SELECT COUNT(*) as total,
                               COUNT(CASE WHEN is_active = 1 THEN 1 END) as active,
                               AVG(importance) as avg_importance,
                               MAX(last_accessed) as last_accessed
                        FROM memory_entries 
                        WHERE user_id = ?
                    """, (user_id,)) as cursor:
                        row = await cursor.fetchone()
                else:
                    async with db.execute("""
                        SELECT COUNT(*) as total,
                               COUNT(CASE WHEN is_active = 1 THEN 1 END) as active,
                               AVG(importance) as avg_importance,
                               MAX(last_accessed) as last_accessed
                        FROM memory_entries
                    """) as cursor:
                        row = await cursor.fetchone()
                
                return {
                    'total_entries': row[0],
                    'active_entries': row[1],
                    'average_importance': row[2] or 0.0,
                    'last_accessed': row[3]
                }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {str(e)}")
            return {}