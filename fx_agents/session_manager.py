"""Enhanced Session Manager - OpenAI Agents SDK Integration
Provides comprehensive session management with full SDK Session integration
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from agents import Session, SQLiteSession
from memory.sqlite_memory import get_memory, create_enhanced_session

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionContext(BaseModel):
    """Enhanced session context with SDK features"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    agent_name: str = Field(..., description="Current agent name")
    created_at: datetime = Field(default_factory=datetime.now, description="Session creation time")
    last_activity: datetime = Field(default_factory=datetime.now, description="Last activity time")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    system_state: Dict[str, Any] = Field(default_factory=dict, description="System state")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")

class SessionConfig(BaseModel):
    """Session configuration"""
    max_session_duration: int = Field(default=3600, description="Maximum session duration in seconds")
    max_conversation_history: int = Field(default=100, description="Maximum conversation history items")
    enable_memory_persistence: bool = Field(default=True, description="Enable memory persistence")
    enable_performance_tracking: bool = Field(default=True, description="Enable performance tracking")
    enable_context_management: bool = Field(default=True, description="Enable context management")
    auto_cleanup: bool = Field(default=True, description="Enable automatic cleanup")

class SessionManager:
    """Enhanced session manager with full SDK integration"""
    
    def __init__(self, config: Optional[SessionConfig] = None):
        self.config = config or SessionConfig()
        self.active_sessions: Dict[str, Session] = {}
        self.session_contexts: Dict[str, SessionContext] = {}
        self.memory = get_memory()
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start automatic cleanup task"""
        if self.config.auto_cleanup:
            async def cleanup_worker():
                while True:
                    await asyncio.sleep(300)  # Clean up every 5 minutes
                    await self.cleanup_expired_sessions()
            
            self._cleanup_task = asyncio.create_task(cleanup_worker())
            logger.info("Started automatic session cleanup")
    
    async def create_session(self, session_id: str, agent: Any, user_id: Optional[str] = None,
                           initial_context: Optional[Dict[str, Any]] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Session:
        """Create enhanced session with SDK integration"""
        try:
            # Create SDK Session with memory integration
            session = await create_enhanced_session(
                session_id=session_id,
                agent=agent,
                user_id=user_id,
                trace_metadata=metadata
            )
            
            # Create session context
            context = SessionContext(
                session_id=session_id,
                user_id=user_id,
                agent_name=getattr(agent, 'name', 'Unknown'),
                user_preferences=initial_context.get('user_preferences', {}) if initial_context else {},
                system_state=initial_context.get('system_state', {}) if initial_context else {},
                metadata=metadata or {},
                performance_metrics={
                    "start_time": datetime.now().isoformat(),
                    "message_count": 0,
                    "tool_calls": 0,
                    "handoffs": 0,
                    "total_duration": 0.0
                }
            )
            
            # Store session and context
            self.active_sessions[session_id] = session
            self.session_contexts[session_id] = context
            
            # Store in memory if enabled
            if self.config.enable_memory_persistence:
                await self.memory.create_session(
                    session_id=session_id,
                    user_id=user_id,
                    agent_history=[context.agent_name],
                    user_preferences=context.user_preferences,
                    system_state=context.system_state,
                    trace_metadata=context.metadata
                )
            
            logger.info(f"Created enhanced session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {str(e)}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get active session"""
        return self.active_sessions.get(session_id)
    
    async def get_session_context(self, session_id: str) -> Optional[SessionContext]:
        """Get session context"""
        return self.session_contexts.get(session_id)
    
    async def update_session_context(self, session_id: str, updates: Dict[str, Any]):
        """Update session context"""
        try:
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                context.last_activity = datetime.now()
                
                # Update specific fields
                if "user_preferences" in updates:
                    context.user_preferences.update(updates["user_preferences"])
                
                if "system_state" in updates:
                    context.system_state.update(updates["system_state"])
                
                if "metadata" in updates:
                    context.metadata.update(updates["metadata"])
                
                if "performance_metrics" in updates:
                    context.performance_metrics.update(updates["performance_metrics"])
                
                # Update in memory if enabled
                if self.config.enable_memory_persistence:
                    await self.memory.update_session_context(
                        session_id=session_id,
                        user_preferences=context.user_preferences,
                        system_state=context.system_state
                    )
                
                logger.debug(f"Updated session context for {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to update session context: {str(e)}")
    
    async def add_conversation_entry(self, session_id: str, message_type: str, content: str,
                                   agent_name: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add conversation entry to session"""
        try:
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                
                # Create conversation entry
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "message_type": message_type,
                    "content": content,
                    "agent_name": agent_name or context.agent_name,
                    "metadata": metadata or {}
                }
                
                # Add to conversation history
                context.conversation_history.append(entry)
                
                # Limit history size
                if len(context.conversation_history) > self.config.max_conversation_history:
                    context.conversation_history = context.conversation_history[-self.config.max_conversation_history:]
                
                # Update performance metrics
                context.performance_metrics["message_count"] += 1
                context.last_activity = datetime.now()
                
                # Store in memory if enabled
                if self.config.enable_memory_persistence:
                    await self.memory.add_memory_entry(
                        session_id=session_id,
                        message_type=message_type,
                        content=content,
                        user_id=context.user_id,
                        agent_name=agent_name or context.agent_name,
                        metadata=metadata
                    )
                
                logger.debug(f"Added conversation entry to session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to add conversation entry: {str(e)}")
    
    async def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get conversation history for session"""
        try:
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                history = context.conversation_history
                
                if limit:
                    history = history[-limit:]
                
                return history
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}")
            return []
    
    async def switch_agent(self, session_id: str, new_agent: Any, handoff_reason: Optional[str] = None):
        """Switch agent within session"""
        try:
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                old_agent = context.agent_name
                
                # Update agent
                context.agent_name = getattr(new_agent, 'name', 'Unknown')
                context.last_activity = datetime.now()
                
                # Add handoff entry
                handoff_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "message_type": "handoff",
                    "content": f"Handoff from {old_agent} to {context.agent_name}",
                    "agent_name": "system",
                    "metadata": {
                        "from_agent": old_agent,
                        "to_agent": context.agent_name,
                        "reason": handoff_reason or "Automatic routing"
                    }
                }
                
                context.conversation_history.append(handoff_entry)
                context.performance_metrics["handoffs"] += 1
                
                # Update session with new agent
                if session_id in self.active_sessions:
                    new_session = await create_enhanced_session(
                        session_id=session_id,
                        agent=new_agent,
                        user_id=context.user_id,
                        trace_metadata=context.metadata
                    )
                    self.active_sessions[session_id] = new_session
                
                # Update in memory
                if self.config.enable_memory_persistence:
                    await self.memory.update_session_context(
                        session_id=session_id,
                        agent_history=[context.agent_name],
                        system_state={
                            **context.system_state,
                            "current_agent": context.agent_name,
                            "last_handoff": datetime.now().isoformat()
                        }
                    )
                
                logger.info(f"Switched agent in session {session_id}: {old_agent} -> {context.agent_name}")
                
        except Exception as e:
            logger.error(f"Failed to switch agent: {str(e)}")
    
    async def end_session(self, session_id: str, reason: Optional[str] = None):
        """End session with cleanup"""
        try:
            if session_id in self.session_contexts:
                context = self.session_contexts[session_id]
                
                # Calculate final metrics
                start_time = datetime.fromisoformat(context.performance_metrics["start_time"])
                end_time = datetime.now()
                total_duration = (end_time - start_time).total_seconds()
                
                context.performance_metrics["end_time"] = end_time.isoformat()
                context.performance_metrics["total_duration"] = total_duration
                
                # Add session end entry
                end_entry = {
                    "timestamp": end_time.isoformat(),
                    "message_type": "session_end",
                    "content": f"Session ended: {reason or 'User request'}",
                    "agent_name": "system",
                    "metadata": {
                        "reason": reason,
                        "total_duration": total_duration,
                        "message_count": context.performance_metrics["message_count"],
                        "handoffs": context.performance_metrics["handoffs"]
                    }
                }
                
                context.conversation_history.append(end_entry)
                
                # Store final session data
                if self.config.enable_memory_persistence:
                    await self.memory.update_session_context(
                        session_id=session_id,
                        conversation_summary=f"Session ended after {total_duration:.1f}s with {context.performance_metrics['message_count']} messages",
                        system_state={
                            **context.system_state,
                            "session_ended": True,
                            "end_reason": reason,
                            "final_duration": total_duration
                        }
                    )
                
                # Clean up session
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
                
                if session_id in self.session_contexts:
                    del self.session_contexts[session_id]
                
                logger.info(f"Ended session {session_id} (duration: {total_duration:.1f}s)")
                
        except Exception as e:
            logger.error(f"Failed to end session: {str(e)}")
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, context in self.session_contexts.items():
                time_since_activity = (current_time - context.last_activity).total_seconds()
                
                if time_since_activity > self.config.max_session_duration:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                await self.end_session(session_id, reason="Session expired")
            
            if expired_sessions:
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {str(e)}")
    
    async def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive session summary"""
        try:
            if session_id not in self.session_contexts:
                return None
            
            context = self.session_contexts[session_id]
            
            # Calculate additional metrics
            start_time = datetime.fromisoformat(context.performance_metrics["start_time"])
            current_time = datetime.now()
            duration = (current_time - start_time).total_seconds()
            
            # Get conversation statistics
            user_messages = len([msg for msg in context.conversation_history if msg["message_type"] == "user"])
            agent_messages = len([msg for msg in context.conversation_history if msg["message_type"] == "agent"])
            handoffs = len([msg for msg in context.conversation_history if msg["message_type"] == "handoff"])
            
            return {
                "session_id": session_id,
                "user_id": context.user_id,
                "agent_name": context.agent_name,
                "created_at": context.created_at.isoformat(),
                "last_activity": context.last_activity.isoformat(),
                "duration": duration,
                "message_count": context.performance_metrics["message_count"],
                "user_messages": user_messages,
                "agent_messages": agent_messages,
                "handoffs": handoffs,
                "tool_calls": context.performance_metrics.get("tool_calls", 0),
                "user_preferences": context.user_preferences,
                "system_state": context.system_state,
                "metadata": context.metadata,
                "conversation_summary": f"Session with {user_messages} user messages and {agent_messages} agent responses"
            }
            
        except Exception as e:
            logger.error(f"Failed to get session summary: {str(e)}")
            return None
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        try:
            sessions = []
            
            for session_id, context in self.session_contexts.items():
                session_info = {
                    "session_id": session_id,
                    "user_id": context.user_id,
                    "agent_name": context.agent_name,
                    "created_at": context.created_at.isoformat(),
                    "last_activity": context.last_activity.isoformat(),
                    "message_count": context.performance_metrics["message_count"],
                    "handoffs": context.performance_metrics.get("handoffs", 0)
                }
                sessions.append(session_info)
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to list active sessions: {str(e)}")
            return []
    
    async def get_session_analytics(self) -> Dict[str, Any]:
        """Get session analytics"""
        try:
            total_sessions = len(self.session_contexts)
            total_messages = sum(
                context.performance_metrics["message_count"] 
                for context in self.session_contexts.values()
            )
            total_handoffs = sum(
                context.performance_metrics.get("handoffs", 0)
                for context in self.session_contexts.values()
            )
            
            # Calculate average session duration
            durations = []
            for context in self.session_contexts.values():
                start_time = datetime.fromisoformat(context.performance_metrics["start_time"])
                duration = (datetime.now() - start_time).total_seconds()
                durations.append(duration)
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            return {
                "total_active_sessions": total_sessions,
                "total_messages": total_messages,
                "total_handoffs": total_handoffs,
                "average_session_duration": avg_duration,
                "average_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0,
                "average_handoffs_per_session": total_handoffs / total_sessions if total_sessions > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {str(e)}")
            return {}

# Global session manager
_session_manager = None

def get_session_manager(config: Optional[SessionConfig] = None) -> SessionManager:
    """Get global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(config)
    return _session_manager

async def create_enhanced_session_with_context(session_id: str, agent: Any, user_id: Optional[str] = None,
                                             initial_context: Optional[Dict[str, Any]] = None,
                                             metadata: Optional[Dict[str, Any]] = None) -> Session:
    """Create enhanced session with full context management"""
    session_manager = get_session_manager()
    return await session_manager.create_session(session_id, agent, user_id, initial_context, metadata)

async def get_session_with_context(session_id: str) -> Optional[Session]:
    """Get session with context"""
    session_manager = get_session_manager()
    return await session_manager.get_session(session_id)

async def update_session_context_data(session_id: str, updates: Dict[str, Any]):
    """Update session context data"""
    session_manager = get_session_manager()
    await session_manager.update_session_context(session_id, updates)

async def switch_session_agent(session_id: str, new_agent: Any, handoff_reason: Optional[str] = None):
    """Switch agent within session"""
    session_manager = get_session_manager()
    await session_manager.switch_agent(session_id, new_agent, handoff_reason)

async def end_session_with_cleanup(session_id: str, reason: Optional[str] = None):
    """End session with cleanup"""
    session_manager = get_session_manager()
    await session_manager.end_session(session_id, reason)

# Initialize session manager
def initialize_session_manager(config: Optional[SessionConfig] = None):
    """Initialize the session manager"""
    try:
        get_session_manager(config)
        logger.info("Session manager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize session manager: {str(e)}")

# Initialize on module import
initialize_session_manager()
