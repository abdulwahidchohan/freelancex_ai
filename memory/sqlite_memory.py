#!/usr/bin/env python3
"""Enhanced Memory Management - OpenAI Agents SDK Integration
Provides enhanced memory management with full SDK Session integration
"""

import logging
import sqlite3
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from agents import Session, SQLiteSession
import aiosqlite

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import set_trace_metadata, use a dummy function if not available
try:
    from agents import set_trace_metadata
except ImportError:
    def set_trace_metadata(metadata: Dict[str, Any]) -> None:
        """Dummy function for trace metadata when not available"""
        logger.info(f"Trace metadata (not available): {metadata}")
        pass

class MemoryEntry(BaseModel):
    """Enhanced memory entry with SDK integration"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    message_type: str = Field(..., description="Type of message")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    agent_name: Optional[str] = Field(default=None, description="Agent name")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="Tool calls")
    handoffs: Optional[List[Dict[str, Any]]] = Field(default=None, description="Handoffs")

class SessionContext(BaseModel):
    """Enhanced session context with SDK features"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity")
    agent_history: List[str] = Field(default_factory=list, description="Agent interaction history")
    conversation_summary: Optional[str] = Field(default=None, description="Conversation summary")
    user_preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    system_state: Optional[Dict[str, Any]] = Field(default=None, description="System state")
    trace_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Trace metadata")

class EnhancedSQLiteMemory:
    """Enhanced SQLite memory with full OpenAI Agents SDK integration"""
    
    def __init__(self, db_path: str = "freelancex.db"):
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database with enhanced schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enhanced memory entries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent_name TEXT,
                    tool_calls TEXT,
                    handoffs TEXT
                )
            ''')
            
            # Enhanced session contexts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS session_contexts (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    agent_history TEXT,
                    conversation_summary TEXT,
                    user_preferences TEXT,
                    system_state TEXT,
                    trace_metadata TEXT
                )
            ''')
            
            # Enhanced user profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT,
                    behavior_patterns TEXT,
                    expertise_areas TEXT,
                    communication_style TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Enhanced agent performance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_name TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    execution_time REAL,
                    success_rate REAL,
                    tool_calls_count INTEGER,
                    handoffs_count INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_session_timestamp ON memory_entries(session_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_user_activity ON session_contexts(user_id, last_activity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_profiles_id ON user_profiles(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_performance_name_session ON agent_performance(agent_name, session_id, timestamp)')
            
            conn.commit()
            conn.close()
            logger.info("Enhanced database schema initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def add_memory_entry(self, session_id: str, message_type: str, content: str, 
                              user_id: Optional[str] = None, agent_name: Optional[str] = None,
                              tool_calls: Optional[List[Dict[str, Any]]] = None,
                              handoffs: Optional[List[Dict[str, Any]]] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add memory entry with SDK integration"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute('''
                    INSERT INTO memory_entries 
                    (session_id, user_id, message_type, content, metadata, agent_name, tool_calls, handoffs)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id, message_type, content,
                    json.dumps(metadata) if metadata else None,
                    agent_name,
                    json.dumps(tool_calls) if tool_calls else None,
                    json.dumps(handoffs) if handoffs else None
                ))
                await conn.commit()
                logger.debug(f"Added memory entry for session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to add memory entry: {str(e)}")
            raise
    
    async def get_session_memory(self, session_id: str, limit: int = 50) -> List[MemoryEntry]:
        """Get session memory entries"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT session_id, user_id, message_type, content, metadata, 
                           timestamp, agent_name, tool_calls, handoffs
                    FROM memory_entries 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (session_id, limit))
                
                rows = await cursor.fetchall()
                memory_entries = []
                
                for row in rows:
                    entry = MemoryEntry(
                        session_id=row[0],
                        user_id=row[1],
                        message_type=row[2],
                        content=row[3],
                        metadata=json.loads(row[4]) if row[4] else None,
                        timestamp=datetime.fromisoformat(row[5]),
                        agent_name=row[6],
                        tool_calls=json.loads(row[7]) if row[7] else None,
                        handoffs=json.loads(row[8]) if row[8] else None
                    )
                    memory_entries.append(entry)
                
                return memory_entries
                
        except Exception as e:
            logger.error(f"Failed to get session memory: {str(e)}")
            return []
    
    async def create_session(self, session_id: str, user_id: Optional[str] = None,
                           agent_history: Optional[List[str]] = None,
                           user_preferences: Optional[Dict[str, Any]] = None,
                           system_state: Optional[Dict[str, Any]] = None,
                           trace_metadata: Optional[Dict[str, Any]] = None) -> SessionContext:
        """Create session context with SDK integration"""
        try:
            context = SessionContext(
                session_id=session_id,
                user_id=user_id,
                agent_history=agent_history or [],
                user_preferences=user_preferences,
                system_state=system_state,
                trace_metadata=trace_metadata
            )
            
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute('''
                    INSERT OR REPLACE INTO session_contexts 
                    (session_id, user_id, agent_history, user_preferences, system_state, trace_metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    session_id, user_id,
                    json.dumps(agent_history) if agent_history else None,
                    json.dumps(user_preferences) if user_preferences else None,
                    json.dumps(system_state) if system_state else None,
                    json.dumps(trace_metadata) if trace_metadata else None
                ))
                await conn.commit()
                logger.info(f"Created session context for {session_id}")
                return context
                
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise
    
    async def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """Get session context"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT session_id, user_id, created_at, last_activity, agent_history,
                           conversation_summary, user_preferences, system_state, trace_metadata
                    FROM session_contexts 
                    WHERE session_id = ?
                ''', (session_id,))
                
                row = await cursor.fetchone()
                if row:
                    return SessionContext(
                        session_id=row[0],
                        user_id=row[1],
                        created_at=datetime.fromisoformat(row[2]),
                        last_activity=datetime.fromisoformat(row[3]),
                        agent_history=json.loads(row[4]) if row[4] else [],
                        conversation_summary=row[5],
                        user_preferences=json.loads(row[6]) if row[6] else None,
                        system_state=json.loads(row[7]) if row[7] else None,
                        trace_metadata=json.loads(row[8]) if row[8] else None
                    )
                return None
                
        except Exception as e:
            logger.error(f"Failed to get session context: {str(e)}")
            return None
    
    async def update_session_context(self, session_id: str, agent_history: Optional[List[str]] = None,
                                   conversation_summary: Optional[str] = None,
                                   user_preferences: Optional[Dict[str, Any]] = None,
                                   system_state: Optional[Dict[str, Any]] = None) -> None:
        """Update session context"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                update_fields = []
                params = []
                
                if agent_history is not None:
                    update_fields.append("agent_history = ?")
                    params.append(json.dumps(agent_history))
                
                if conversation_summary is not None:
                    update_fields.append("conversation_summary = ?")
                    params.append(conversation_summary)
                
                if user_preferences is not None:
                    update_fields.append("user_preferences = ?")
                    params.append(json.dumps(user_preferences))
                
                if system_state is not None:
                    update_fields.append("system_state = ?")
                    params.append(json.dumps(system_state))
                
                if update_fields:
                    update_fields.append("last_activity = ?")
                    params.append(datetime.now().isoformat())
                    params.append(session_id)
                    
                    query = f"UPDATE session_contexts SET {', '.join(update_fields)} WHERE session_id = ?"
                    await conn.execute(query, params)
                    await conn.commit()
                    logger.debug(f"Updated session context for {session_id}")
                    
        except Exception as e:
            logger.error(f"Failed to update session context: {str(e)}")
            raise
    
    async def create_sdk_session(self, session_id: str, agent: Any, 
                               user_id: Optional[str] = None,
                               trace_metadata: Optional[Dict[str, Any]] = None) -> Session:
        """Create SDK Session with memory integration"""
        try:
            # Create SQLiteSession for automatic conversation history
            # Note: SQLiteSession doesn't accept agent parameter in constructor
            session = SQLiteSession(
                session_id=session_id,
                db_path=self.db_path
            )
            
            # Store session context
            await self.create_session(
                session_id=session_id,
                user_id=user_id,
                trace_metadata=trace_metadata
            )
            
            logger.info(f"Created SDK session for {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create SDK session: {str(e)}")
            raise
    
    async def record_agent_performance(self, agent_name: str, session_id: str,
                                     execution_time: float, success_rate: float,
                                     tool_calls_count: int = 0, handoffs_count: int = 0) -> None:
        """Record agent performance metrics"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute('''
                    INSERT INTO agent_performance 
                    (agent_name, session_id, execution_time, success_rate, tool_calls_count, handoffs_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (agent_name, session_id, execution_time, success_rate, tool_calls_count, handoffs_count))
                await conn.commit()
                logger.debug(f"Recorded performance for {agent_name}")
                
        except Exception as e:
            logger.error(f"Failed to record agent performance: {str(e)}")
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute('''
                    SELECT preferences, behavior_patterns, expertise_areas, communication_style
                    FROM user_profiles 
                    WHERE user_id = ?
                ''', (user_id,))
                
                row = await cursor.fetchone()
                if row:
                    return {
                        "preferences": json.loads(row[0]) if row[0] else {},
                        "behavior_patterns": json.loads(row[1]) if row[1] else {},
                        "expertise_areas": json.loads(row[2]) if row[2] else [],
                        "communication_style": row[3]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            return None
    
    async def update_user_profile(self, user_id: str, preferences: Optional[Dict[str, Any]] = None,
                                behavior_patterns: Optional[Dict[str, Any]] = None,
                                expertise_areas: Optional[List[str]] = None,
                                communication_style: Optional[str] = None) -> None:
        """Update user profile"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute('''
                    INSERT OR REPLACE INTO user_profiles 
                    (user_id, preferences, behavior_patterns, expertise_areas, communication_style, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    json.dumps(preferences) if preferences else None,
                    json.dumps(behavior_patterns) if behavior_patterns else None,
                    json.dumps(expertise_areas) if expertise_areas else None,
                    communication_style,
                    datetime.now().isoformat()
                ))
                await conn.commit()
                logger.debug(f"Updated user profile for {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to update user profile: {str(e)}")
    
    async def cleanup_old_sessions(self, days: int = 30) -> None:
        """Clean up old sessions and memory entries"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as conn:
                # Clean up old memory entries
                await conn.execute('''
                    DELETE FROM memory_entries 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Clean up old session contexts
                await conn.execute('''
                    DELETE FROM session_contexts 
                    WHERE last_activity < ?
                ''', (cutoff_date.isoformat(),))
                
                # Clean up old performance data
                await conn.execute('''
                    DELETE FROM agent_performance 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                await conn.commit()
                logger.info(f"Cleaned up sessions older than {days} days")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {str(e)}")

# Global memory instance
_memory_instance = None

def get_memory() -> EnhancedSQLiteMemory:
    """Get global memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = EnhancedSQLiteMemory()
    return _memory_instance

async def create_enhanced_session(session_id: str, agent: Any, user_id: Optional[str] = None,
                                trace_metadata: Optional[Dict[str, Any]] = None) -> Session:
    """Create enhanced SDK session with memory integration"""
    memory = get_memory()
    return await memory.create_sdk_session(session_id, agent, user_id, trace_metadata)