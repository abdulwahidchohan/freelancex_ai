"""Enhanced FreelanceX.AI Chainlit Application - OpenAI Agents SDK Integration
Provides enhanced chat interface with full SDK integration
"""

import chainlit as cl
import asyncio
import logging
import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fx_agents.triage_agent import dynamic_triage_agent, route_request
from fx_agents.custom_agent import AgentResponse
from fx_agents.access_control import get_access_control_manager, ResourceType, PermissionLevel, AccessRequest
from memory.sqlite_memory import get_memory, create_enhanced_session
from config.settings import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global memory instance
memory = get_memory()

@cl.on_chat_start
async def on_chat_start():
    """Enhanced chat start with SDK integration"""
    try:
        # Set up enhanced session
        session_id = cl.user_session.get("id")
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"
        user_id = cl.user_session.get("id")
        
        # Set trace metadata for SDK integration
        trace_metadata = {
            "user_id": user_id,
            "session_id": session_id,
            "session_type": "freelance_consultation",
            "platform": "chainlit",
            "start_time": datetime.now().isoformat()
        }
        
        # Create enhanced session (simplified to avoid SDK session issues)
        try:
            session = await create_enhanced_session(
                session_id=session_id,
                agent=dynamic_triage_agent,
                user_id=user_id,
                trace_metadata=trace_metadata
            )
        except Exception as session_error:
            logger.warning(f"Session creation failed, continuing without SDK session: {str(session_error)}")
            session = None
        
        # Store session info
        cl.user_session.set("session_id", session_id)
        cl.user_session.set("user_id", user_id)
        cl.user_session.set("trace_metadata", trace_metadata)
        
        # Welcome message with enhanced features
        welcome_message = """
        🚀 **Welcome to FreelanceX.AI - Enhanced Edition!**
        
        I'm your AI assistant with **full OpenAI Agents SDK integration** and enhanced capabilities:
        
        ✨ **Enhanced Features:**
        - 🧠 **Dynamic Memory Integration** - I remember our conversations
        - 🔄 **Intelligent Handoffs** - Seamless agent coordination
        - 🛡️ **Guardrails & Safety** - Secure and reliable responses
        - 📊 **Performance Monitoring** - Optimized response times
        - 🔍 **Advanced Tracing** - Detailed debugging and insights
        
        🎯 **What I can help you with:**
        - 📝 **Proposal Writing** - Professional proposals and bids
        - 🔍 **Job Search** - Find freelance opportunities
        - 📈 **Marketing Strategy** - Campaign planning and analysis
        - 🧮 **Financial Planning** - Budgeting and pricing strategies
        - 🔬 **Market Research** - Industry analysis and trends
        - 🛡️ **Security & Compliance** - Data protection and risk assessment
        - 🎨 **UX/UI Design** - User experience optimization
        - 🚀 **Business Growth** - Expansion strategies and planning
        
        **How to get started:**
        Simply describe what you need help with, and I'll route your request to the most appropriate specialized agent!
        
        💡 **Pro Tips:**
        - Be specific about your needs for better routing
        - Ask follow-up questions for detailed analysis
        - Request different perspectives from various agents
        """
        
        await cl.Message(
            content=welcome_message,
            author="FreelanceX.AI Assistant"
        ).send()
        
        logger.info(f"Enhanced chat session started: {session_id}")
        
    except Exception as e:
        logger.error(f"Failed to start enhanced chat session: {str(e)}")
        await cl.Message(
            content="⚠️ Session initialization failed. Please refresh and try again.",
            author="System"
        ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Enhanced message handling with SDK integration"""
    try:
        # Get session information
        session_id = cl.user_session.get("session_id")
        user_id = cl.user_session.get("user_id")
        trace_metadata = cl.user_session.get("trace_metadata", {})
        
        # Ensure we have a valid session_id
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"
            cl.user_session.set("session_id", session_id)
            logger.warning(f"Session ID was None, created new one: {session_id}")
        
        # Update trace metadata
        trace_metadata.update({
            "message_count": trace_metadata.get("message_count", 0) + 1,
            "last_message_time": datetime.now().isoformat(),
            "message_length": len(message.content)
        })
        
        # Add user message to memory (only if session_id is valid)
        if session_id:
            try:
                await memory.add_memory_entry(
                    session_id=session_id,
                    message_type="user",
                    content=message.content,
                    user_id=user_id,
                    metadata={
                        "message_id": message.id,
                        "timestamp": datetime.now().isoformat(),
                        "trace_metadata": trace_metadata
                    }
                )
            except Exception as memory_error:
                logger.error(f"Memory entry failed: {str(memory_error)}")
                # Continue without memory entry rather than failing the entire request
        
        # Show processing indicator
        await cl.Message(
            content="🤔 Analyzing your request and routing to the best agent...",
            author="System"
        ).send()
        
        # Route request with enhanced features
        triage_result = await route_request(
            message=message.content,
            session_id=session_id,
            user_id=user_id,
            trace_metadata=trace_metadata
        )
        
        # Prepare response with enhanced metadata
        response_content = triage_result.response
        
        # Add routing information to response
        if triage_result.routing_decision:
            routing_info = f"""
            🎯 **Routing Information:**
            - **Target Agent:** {triage_result.routing_decision.target_agent}
            - **Confidence:** {triage_result.routing_decision.confidence:.2f}
            - **Handoff Type:** {triage_result.routing_decision.handoff_type}
            - **Processing Time:** {triage_result.execution_time:.2f}s
            
            💭 **Reasoning:** {triage_result.routing_decision.reasoning}
            """
            response_content += f"\n\n{routing_info}"
        
        # Add performance metrics
        performance_info = f"""
        📊 **Performance Metrics:**
        - **Execution Time:** {triage_result.execution_time:.2f}s
        - **Handoffs:** {len(triage_result.handoffs)}
        - **Success:** {'✅' if triage_result.success else '❌'}
        """
        
        if triage_result.trace_id:
            performance_info += f"- **Trace ID:** {triage_result.trace_id}"
        
        response_content += f"\n\n{performance_info}"
        
        # Send enhanced response with better error handling
        try:
            await cl.Message(
                content=response_content,
                author="FreelanceX.AI Assistant",
                metadata={
                    "routing_decision": triage_result.routing_decision.dict() if triage_result.routing_decision else None,
                    "handoffs": triage_result.handoffs,
                    "execution_time": triage_result.execution_time,
                    "trace_id": triage_result.trace_id,
                    "success": triage_result.success,
                    "target_agent": triage_result.routing_decision.target_agent if triage_result.routing_decision else None
                }
            ).send()
            logger.info(f"Response sent successfully: {len(response_content)} characters")
        except Exception as send_error:
            logger.error(f"Failed to send response: {str(send_error)}")
            # Try sending a simple response as fallback
            await cl.Message(
                content=f"Response: {response_content[:500]}...",
                author="FreelanceX.AI Assistant"
            ).send()
        
        # Add agent response to memory (only if session_id is valid)
        if session_id:
            try:
                await memory.add_memory_entry(
                    session_id=session_id,
                    message_type="agent",
                    content=response_content,
                    user_id=user_id,
                    agent_name=triage_result.routing_decision.target_agent if triage_result.routing_decision else "triage_agent",
                    handoffs=triage_result.handoffs,
                    metadata={
                        "execution_time": triage_result.execution_time,
                        "trace_id": triage_result.trace_id,
                        "success": triage_result.success,
                        "routing_decision": triage_result.routing_decision.dict() if triage_result.routing_decision else None
                    }
                )
                
                # Update session context
                await memory.update_session_context(
                    session_id=session_id,
                    agent_history=triage_result.handoffs,
                    system_state={
                        "last_response_time": datetime.now().isoformat(),
                        "total_messages": trace_metadata.get("message_count", 0),
                        "last_target_agent": triage_result.routing_decision.target_agent if triage_result.routing_decision else None
                    }
                )
            except Exception as memory_error:
                logger.error(f"Memory operations failed: {str(memory_error)}")
                # Continue without memory operations rather than failing the entire request
        
        # Update trace metadata
        cl.user_session.set("trace_metadata", trace_metadata)
        
        logger.info(f"Enhanced message processed successfully: {session_id}")
        
    except Exception as e:
        logger.error(f"Enhanced message processing failed: {str(e)}")
        
        # Record error in memory
        session_id = cl.user_session.get("session_id")
        user_id = cl.user_session.get("user_id")
        
        if session_id:
            try:
                await memory.add_memory_entry(
                    session_id=session_id,
                    message_type="error",
                    content=f"Message processing failed: {str(e)}",
                    user_id=user_id,
                    agent_name="system",
                    metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
                )
            except Exception as memory_error:
                logger.error(f"Failed to record error in memory: {str(memory_error)}")
        
        # Send error response
        await cl.Message(
            content=f"❌ **Error:** {str(e)}\n\nPlease try again or contact support if the issue persists.",
            author="System"
        ).send()

@cl.on_chat_end
async def on_chat_end():
    """Enhanced chat end with cleanup and analytics"""
    try:
        session_id = cl.user_session.get("session_id")
        user_id = cl.user_session.get("user_id")
        trace_metadata = cl.user_session.get("trace_metadata", {})
        
        if session_id:
            # Get session analytics
            session_context = await memory.get_session_context(session_id)
            session_memory = await memory.get_session_memory(session_id)
            
            # Calculate session metrics
            total_messages = len(session_memory)
            user_messages = len([m for m in session_memory if m.message_type == "user"])
            agent_messages = len([m for m in session_memory if m.message_type == "agent"])
            errors = len([m for m in session_memory if m.message_type == "error"])
            
            # Update session context with final metrics
            await memory.update_session_context(
                session_id=session_id,
                conversation_summary=f"Session ended with {total_messages} total messages, {user_messages} user messages, {agent_messages} agent responses, and {errors} errors.",
                system_state={
                    "session_end_time": datetime.now().isoformat(),
                    "total_messages": total_messages,
                    "user_messages": user_messages,
                    "agent_messages": agent_messages,
                    "errors": errors,
                    "session_duration": trace_metadata.get("session_duration", 0)
                }
            )
            
            logger.info(f"Enhanced chat session ended: {session_id} - {total_messages} messages processed")
        
    except Exception as e:
        logger.error(f"Failed to end enhanced chat session: {str(e)}")

# Enhanced configuration
def get_enhanced_config() -> Dict[str, Any]:
    """Get enhanced configuration with SDK features"""
    config = get_config()
    
    enhanced_config = {
        **config.dict(),
        "sdk_features": {
            "tracing_enabled": True,
            "memory_integration": True,
            "handoffs_enabled": True,
            "guardrails_enabled": True,
            "performance_monitoring": True
        },
        "chainlit_config": {
            "session_management": "enhanced",
            "memory_persistence": True,
            "tracing_integration": True,
            "agent_coordination": "dynamic"
        }
    }
    
    return enhanced_config

# Enhanced utilities
async def get_session_analytics(session_id: str) -> Dict[str, Any]:
    """Get enhanced session analytics"""
    try:
        session_context = await memory.get_session_context(session_id)
        session_memory = await memory.get_session_memory(session_id)
        
        if not session_context:
            return {"error": "Session not found"}
        
        # Calculate analytics
        total_messages = len(session_memory)
        user_messages = len([m for m in session_memory if m.message_type == "user"])
        agent_messages = len([m for m in session_memory if m.message_type == "agent"])
        errors = len([m for m in session_memory if m.message_type == "error"])
        
        # Calculate average response time
        response_times = []
        for i, entry in enumerate(session_memory):
            if entry.message_type == "agent" and i > 0:
                prev_entry = session_memory[i-1]
                if prev_entry.message_type == "user":
                    time_diff = (entry.timestamp - prev_entry.timestamp).total_seconds()
                    response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "session_id": session_id,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "agent_messages": agent_messages,
            "errors": errors,
            "average_response_time": avg_response_time,
            "session_duration": (session_context.last_activity - session_context.created_at).total_seconds(),
            "agent_history": session_context.agent_history,
            "success_rate": (agent_messages / user_messages) if user_messages > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get session analytics: {str(e)}")
        return {"error": str(e)}

async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get enhanced user profile"""
    try:
        profile = await memory.get_user_profile(user_id)
        if profile:
            return profile
        else:
            return {
                "user_id": user_id,
                "preferences": {},
                "behavior_patterns": {},
                "expertise_areas": [],
                "communication_style": "professional",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Failed to get user profile: {str(e)}")
        return {"error": str(e)}