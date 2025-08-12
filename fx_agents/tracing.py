"""Enhanced Tracing System - OpenAI Agents SDK Integration
Provides comprehensive tracing for debugging, monitoring, and performance analysis
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from agents import set_trace_metadata, trace

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TraceMetadata(BaseModel):
    """Enhanced trace metadata"""
    trace_id: str = Field(..., description="Unique trace identifier")
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    agent_name: str = Field(..., description="Agent name")
    timestamp: datetime = Field(default_factory=datetime.now, description="Trace timestamp")
    message_type: str = Field(..., description="Message type")
    message_length: int = Field(..., description="Message length")
    execution_context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    error_info: Optional[Dict[str, Any]] = Field(default=None, description="Error information")

class TraceEvent(BaseModel):
    """Trace event for detailed tracking"""
    event_id: str = Field(..., description="Event identifier")
    trace_id: str = Field(..., description="Trace identifier")
    event_type: str = Field(..., description="Event type")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    agent_name: str = Field(..., description="Agent name")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    duration: Optional[float] = Field(default=None, description="Event duration")
    parent_event_id: Optional[str] = Field(default=None, description="Parent event ID")

class TraceSession(BaseModel):
    """Trace session for grouping related traces"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    start_time: datetime = Field(default_factory=datetime.now, description="Session start time")
    end_time: Optional[datetime] = Field(default=None, description="Session end time")
    total_traces: int = Field(default=0, description="Total traces in session")
    total_events: int = Field(default=0, description="Total events in session")
    performance_summary: Dict[str, Any] = Field(default_factory=dict, description="Performance summary")

class TracingManager:
    """Enhanced tracing manager with SDK integration"""
    
    def __init__(self):
        self.active_traces: Dict[str, TraceMetadata] = {}
        self.trace_events: Dict[str, List[TraceEvent]] = {}
        self.trace_sessions: Dict[str, TraceSession] = {}
        self.performance_data: Dict[str, List[Dict[str, Any]]] = {}
    
    def start_trace(self, session_id: str, agent_name: str, user_id: Optional[str] = None,
                   message_type: str = "user", message_length: int = 0,
                   execution_context: Optional[Dict[str, Any]] = None) -> str:
        """Start a new trace with enhanced metadata"""
        try:
            trace_id = str(uuid.uuid4())
            
            metadata = TraceMetadata(
                trace_id=trace_id,
                session_id=session_id,
                user_id=user_id,
                agent_name=agent_name,
                message_type=message_type,
                message_length=message_length,
                execution_context=execution_context or {},
                performance_metrics={
                    "start_time": time.time(),
                    "message_count": 0,
                    "tool_calls": 0,
                    "handoffs": 0
                }
            )
            
            self.active_traces[trace_id] = metadata
            self.trace_events[trace_id] = []
            
            # Set trace metadata for SDK integration
            set_trace_metadata({
                "trace_id": trace_id,
                "session_id": session_id,
                "agent_name": agent_name,
                "user_id": user_id,
                "timestamp": metadata.timestamp.isoformat(),
                "message_type": message_type,
                "message_length": message_length
            })
            
            # Create or update trace session
            if session_id not in self.trace_sessions:
                self.trace_sessions[session_id] = TraceSession(
                    session_id=session_id,
                    user_id=user_id
                )
            
            self.trace_sessions[session_id].total_traces += 1
            
            logger.info(f"Started trace {trace_id} for agent {agent_name}")
            return trace_id
            
        except Exception as e:
            logger.error(f"Failed to start trace: {str(e)}")
            return str(uuid.uuid4())  # Fallback trace ID
    
    def add_trace_event(self, trace_id: str, event_type: str, agent_name: str,
                       event_data: Optional[Dict[str, Any]] = None,
                       duration: Optional[float] = None,
                       parent_event_id: Optional[str] = None) -> str:
        """Add event to trace with enhanced tracking"""
        try:
            event_id = str(uuid.uuid4())
            
            event = TraceEvent(
                event_id=event_id,
                trace_id=trace_id,
                event_type=event_type,
                agent_name=agent_name,
                event_data=event_data or {},
                duration=duration,
                parent_event_id=parent_event_id
            )
            
            if trace_id in self.trace_events:
                self.trace_events[trace_id].append(event)
                
                # Update session event count
                if trace_id in self.active_traces:
                    session_id = self.active_traces[trace_id].session_id
                    if session_id in self.trace_sessions:
                        self.trace_sessions[session_id].total_events += 1
            
            logger.debug(f"Added trace event {event_id} ({event_type}) to trace {trace_id}")
            return event_id
            
        except Exception as e:
            logger.error(f"Failed to add trace event: {str(e)}")
            return str(uuid.uuid4())
    
    def update_trace_metadata(self, trace_id: str, updates: Dict[str, Any]):
        """Update trace metadata"""
        try:
            if trace_id in self.active_traces:
                metadata = self.active_traces[trace_id]
                
                # Update performance metrics
                if "performance_metrics" in updates:
                    metadata.performance_metrics.update(updates["performance_metrics"])
                
                # Update execution context
                if "execution_context" in updates:
                    metadata.execution_context.update(updates["execution_context"])
                
                # Update error info
                if "error_info" in updates:
                    metadata.error_info = updates["error_info"]
                
                # Update SDK trace metadata
                set_trace_metadata({
                    "trace_id": trace_id,
                    "session_id": metadata.session_id,
                    "agent_name": metadata.agent_name,
                    "user_id": metadata.user_id,
                    "performance_metrics": metadata.performance_metrics,
                    "execution_context": metadata.execution_context,
                    "error_info": metadata.error_info
                })
                
                logger.debug(f"Updated trace metadata for {trace_id}")
                
        except Exception as e:
            logger.error(f"Failed to update trace metadata: {str(e)}")
    
    def end_trace(self, trace_id: str, success: bool = True, error_info: Optional[Dict[str, Any]] = None):
        """End trace with final metrics"""
        try:
            if trace_id in self.active_traces:
                metadata = self.active_traces[trace_id]
                
                # Calculate final performance metrics
                end_time = time.time()
                start_time = metadata.performance_metrics.get("start_time", end_time)
                duration = end_time - start_time
                
                metadata.performance_metrics.update({
                    "end_time": end_time,
                    "duration": duration,
                    "success": success
                })
                
                if error_info:
                    metadata.error_info = error_info
                
                # Update session performance summary
                session_id = metadata.session_id
                if session_id in self.trace_sessions:
                    session = self.trace_sessions[session_id]
                    
                    if "total_duration" not in session.performance_summary:
                        session.performance_summary["total_duration"] = 0
                    session.performance_summary["total_duration"] += duration
                    
                    if "successful_traces" not in session.performance_summary:
                        session.performance_summary["successful_traces"] = 0
                    if success:
                        session.performance_summary["successful_traces"] += 1
                    
                    if "average_duration" not in session.performance_summary:
                        session.performance_summary["average_duration"] = 0
                    session.performance_summary["average_duration"] = (
                        session.performance_summary["total_duration"] / session.total_traces
                    )
                
                # Store performance data
                if session_id not in self.performance_data:
                    self.performance_data[session_id] = []
                
                self.performance_data[session_id].append({
                    "trace_id": trace_id,
                    "agent_name": metadata.agent_name,
                    "duration": duration,
                    "success": success,
                    "timestamp": metadata.timestamp.isoformat(),
                    "message_length": metadata.message_length,
                    "tool_calls": metadata.performance_metrics.get("tool_calls", 0),
                    "handoffs": metadata.performance_metrics.get("handoffs", 0)
                })
                
                logger.info(f"Ended trace {trace_id} (duration: {duration:.2f}s, success: {success})")
                
        except Exception as e:
            logger.error(f"Failed to end trace: {str(e)}")
    
    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive trace summary"""
        try:
            if trace_id not in self.active_traces:
                return None
            
            metadata = self.active_traces[trace_id]
            events = self.trace_events.get(trace_id, [])
            
            return {
                "trace_id": trace_id,
                "session_id": metadata.session_id,
                "user_id": metadata.user_id,
                "agent_name": metadata.agent_name,
                "timestamp": metadata.timestamp.isoformat(),
                "message_type": metadata.message_type,
                "message_length": metadata.message_length,
                "performance_metrics": metadata.performance_metrics,
                "execution_context": metadata.execution_context,
                "error_info": metadata.error_info,
                "event_count": len(events),
                "events": [event.dict() for event in events]
            }
            
        except Exception as e:
            logger.error(f"Failed to get trace summary: {str(e)}")
            return None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session performance summary"""
        try:
            if session_id not in self.trace_sessions:
                return None
            
            session = self.trace_sessions[session_id]
            performance_data = self.performance_data.get(session_id, [])
            
            # Calculate additional metrics
            total_duration = sum(item["duration"] for item in performance_data)
            successful_traces = sum(1 for item in performance_data if item["success"])
            success_rate = (successful_traces / len(performance_data)) if performance_data else 0
            
            avg_message_length = sum(item["message_length"] for item in performance_data) / len(performance_data) if performance_data else 0
            total_tool_calls = sum(item["tool_calls"] for item in performance_data)
            total_handoffs = sum(item["handoffs"] for item in performance_data)
            
            return {
                "session_id": session_id,
                "user_id": session.user_id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "total_traces": session.total_traces,
                "total_events": session.total_events,
                "total_duration": total_duration,
                "average_duration": total_duration / len(performance_data) if performance_data else 0,
                "success_rate": success_rate,
                "average_message_length": avg_message_length,
                "total_tool_calls": total_tool_calls,
                "total_handoffs": total_handoffs,
                "performance_data": performance_data
            }
            
        except Exception as e:
            logger.error(f"Failed to get session summary: {str(e)}")
            return None
    
    def cleanup_old_traces(self, max_age_hours: int = 24):
        """Clean up old traces and events"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            # Clean up old active traces
            old_trace_ids = [
                trace_id for trace_id, metadata in self.active_traces.items()
                if metadata.timestamp < cutoff_time
            ]
            
            for trace_id in old_trace_ids:
                del self.active_traces[trace_id]
                if trace_id in self.trace_events:
                    del self.trace_events[trace_id]
            
            # Clean up old performance data
            for session_id in list(self.performance_data.keys()):
                self.performance_data[session_id] = [
                    item for item in self.performance_data[session_id]
                    if datetime.fromisoformat(item["timestamp"]) > cutoff_time
                ]
                
                if not self.performance_data[session_id]:
                    del self.performance_data[session_id]
            
            logger.info(f"Cleaned up {len(old_trace_ids)} old traces")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old traces: {str(e)}")

# Global tracing manager
_tracing_manager = TracingManager()

def get_tracing_manager() -> TracingManager:
    """Get global tracing manager"""
    return _tracing_manager

@trace
def trace_agent_execution(agent_name: str, session_id: str, user_id: Optional[str] = None,
                         message_type: str = "user", message_length: int = 0,
                         execution_context: Optional[Dict[str, Any]] = None):
    """Decorator for tracing agent execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracing_manager = get_tracing_manager()
            
            # Start trace
            trace_id = tracing_manager.start_trace(
                session_id=session_id,
                agent_name=agent_name,
                user_id=user_id,
                message_type=message_type,
                message_length=message_length,
                execution_context=execution_context
            )
            
            try:
                # Add execution start event
                tracing_manager.add_trace_event(
                    trace_id=trace_id,
                    event_type="execution_start",
                    agent_name=agent_name,
                    event_data={"function": func.__name__}
                )
                
                # Execute function
                start_time = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Add execution end event
                tracing_manager.add_trace_event(
                    trace_id=trace_id,
                    event_type="execution_end",
                    agent_name=agent_name,
                    event_data={"function": func.__name__, "result_type": type(result).__name__},
                    duration=duration
                )
                
                # End trace successfully
                tracing_manager.end_trace(trace_id, success=True)
                
                return result
                
            except Exception as e:
                # Add error event
                tracing_manager.add_trace_event(
                    trace_id=trace_id,
                    event_type="execution_error",
                    agent_name=agent_name,
                    event_data={"function": func.__name__, "error": str(e)}
                )
                
                # End trace with error
                tracing_manager.end_trace(trace_id, success=False, error_info={"error": str(e)})
                raise
        
        return wrapper
    return decorator

def create_trace_visualization(trace_id: str) -> Dict[str, Any]:
    """Create trace visualization data"""
    try:
        tracing_manager = get_tracing_manager()
        trace_summary = tracing_manager.get_trace_summary(trace_id)
        
        if not trace_summary:
            return {"error": "Trace not found"}
        
        # Create visualization data
        events = trace_summary.get("events", [])
        timeline = []
        
        for event in events:
            timeline.append({
                "event_id": event["event_id"],
                "event_type": event["event_type"],
                "timestamp": event["timestamp"],
                "duration": event.get("duration", 0),
                "agent_name": event["agent_name"],
                "data": event["event_data"]
            })
        
        return {
            "trace_id": trace_id,
            "session_id": trace_summary["session_id"],
            "agent_name": trace_summary["agent_name"],
            "start_time": trace_summary["timestamp"],
            "duration": trace_summary["performance_metrics"].get("duration", 0),
            "success": trace_summary["performance_metrics"].get("success", True),
            "timeline": timeline,
            "performance_metrics": trace_summary["performance_metrics"],
            "error_info": trace_summary.get("error_info")
        }
        
    except Exception as e:
        logger.error(f"Failed to create trace visualization: {str(e)}")
        return {"error": str(e)}

# Initialize tracing system
def initialize_tracing():
    """Initialize the tracing system"""
    try:
        # Set up periodic cleanup
        import threading
        import time
        
        def cleanup_worker():
            while True:
                time.sleep(3600)  # Clean up every hour
                get_tracing_manager().cleanup_old_traces()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        
        logger.info("Tracing system initialized")
        
    except Exception as e:
        logger.error(f"Failed to initialize tracing: {str(e)}")

# Initialize tracing on module import
initialize_tracing()
