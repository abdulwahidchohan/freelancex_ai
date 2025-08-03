#!/usr/bin/env python3
"""
FreelanceX.AI Enhanced Chainlit UI
Advanced user interface with dashboard features, multimodal support, and real-time notifications
Features: Voice/image input, personalized dashboards, notifications, real-time updates
"""

import chainlit as cl
import sys
import os
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import speech_recognition as sr
import io
import base64
from PIL import Image
import requests

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from core.executive_agent import ExecutiveAgent
from core.agent_manager import AgentManager
from backend.database import DatabaseManager
from chainlit_app.dashboard_widgets import DashboardManager
from agents.job_search_agent import JobSearchAgent
from agents.web_search_agent import WebSearchAgent
from agents.math_agent import MathAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
executive_agent = ExecutiveAgent()
agent_manager = AgentManager()
db_manager = DatabaseManager()
dashboard_manager = DashboardManager()

# Initialize specialized agents
job_search_agent = JobSearchAgent()
web_search_agent = WebSearchAgent()
math_agent = MathAgent()

# Register agents with the manager
agent_manager.register_agent(job_search_agent)
agent_manager.register_agent(web_search_agent)
agent_manager.register_agent(math_agent)

# Global user context
user_context = {}

@cl.on_chat_start
async def start_chat():
    """Enhanced chat initialization with user authentication and dashboard setup"""
    try:
        # Initialize database connection
        await db_manager.connect()
        
        # Send enhanced welcome message with interactive elements
        welcome_message = """
# 🚀 Welcome to FreelanceX.AI - Your AI-Powered Freelancing Assistant!

I'm your comprehensive AI assistant designed to enhance your freelancing journey with cutting-edge technology.

## 🎯 What I Can Help You With:

### 💼 **Job Search & Matching**
- Real-time job discovery across multiple platforms
- AI-powered skill matching and recommendations
- Market rate analysis and negotiation insights

### 🔍 **Research & Intelligence**
- Industry trends and market analysis
- Competitor research and positioning
- Technology and tools recommendations

### 📊 **Financial & Mathematical Analysis**
- Budget planning and tax calculations
- Pricing strategies and profit optimization
- Project ROI and time tracking

### 🎤 **Multimodal Interaction**
- Voice commands and dictation
- Image analysis and processing
- Document parsing and extraction

## 🛠 **Quick Actions:**
"""
        
        await cl.Message(content=welcome_message).send()
        
        # Create action buttons for quick access
        actions = [
            cl.Action(name="find_jobs", value="find_jobs", label="🔍 Find Jobs", description="Search for relevant freelance opportunities"),
            cl.Action(name="market_research", value="market_research", label="📈 Market Research", description="Get industry insights and trends"),
            cl.Action(name="calculate_rates", value="calculate_rates", label="💰 Calculate Rates", description="Analyze pricing and financial planning"),
            cl.Action(name="voice_input", value="voice_input", label="🎤 Voice Input", description="Use voice commands"),
            cl.Action(name="show_dashboard", value="show_dashboard", label="📊 Dashboard", description="View your personalized dashboard")
        ]
        
        await cl.Message(
            content="Choose a quick action or simply type your request:",
            actions=actions
        ).send()
        
        # Set up user settings
        await cl.ChatSettings([
            cl.input_widget.Switch(
                id="notifications_enabled",
                label="Enable Real-time Notifications",
                initial=True
            ),
            cl.input_widget.Switch(
                id="voice_enabled",
                label="Enable Voice Input",
                initial=False
            ),
            cl.input_widget.Select(
                id="dashboard_layout",
                label="Dashboard Layout",
                values=["compact", "detailed", "advanced"],
                initial_index=1
            ),
            cl.input_widget.Slider(
                id="job_alert_frequency",
                label="Job Alert Frequency (hours)",
                min=1,
                max=24,
                initial=6,
                step=1
            )
        ]).send()
        
        # Initialize user context
        user_context["session_start"] = datetime.now().isoformat()
        user_context["preferences"] = {
            "notifications_enabled": True,
            "voice_enabled": False,
            "dashboard_layout": "detailed",
            "job_alert_frequency": 6
        }
        
        # Show initial dashboard if user preferences allow
        if user_context["preferences"].get("dashboard_layout") != "compact":
            await show_dashboard()
        
    except Exception as e:
        logger.error(f"Error in chat initialization: {str(e)}")
        await cl.Message(
            content="⚠️ Welcome! There was a minor issue during initialization, but I'm ready to help you. What would you like to do today?"
        ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Enhanced message handling with multimodal support and intelligent routing"""
    try:
        # Show typing indicator
        async with cl.Step("Processing your request...") as step:
            
            # Handle different types of input
            response = ""
            
            # Check for voice input
            if hasattr(message, 'audio') and message.audio:
                response = await handle_voice_input(message.audio)
            
            # Check for image input
            elif message.elements:
                for element in message.elements:
                    if element.type == "image":
                        response = await handle_image_input(element, message.content)
                        break
            
            # Handle text input with intelligent agent routing
            else:
                response = await route_text_message(message.content)
            
            # Send response with appropriate formatting
            if response:
                # Add relevant actions based on response type
                actions = []
                
                if "job" in response.lower() or "opportunity" in response.lower():
                    actions.append(
                        cl.Action(name="apply_job", value="apply_job", label="📝 Help Apply", description="Get help with application")
                    )
                
                if "rate" in response.lower() or "price" in response.lower():
                    actions.append(
                        cl.Action(name="negotiate_rate", value="negotiate_rate", label="💬 Negotiation Tips", description="Get negotiation strategies")
                    )
                
                await cl.Message(content=response, actions=actions).send()
                
                # Update user interaction memory
                await store_interaction_memory(message.content, response)
                
            else:
                step.error("No response generated")
                await cl.Message(
                    content="I apologize, but I couldn't process your request properly. Could you please try rephrasing it?"
                ).send()
                
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await cl.Message(
            content="I encountered an error processing your request. Please try again or contact support if the issue persists."
        ).send()

@cl.action_callback("find_jobs")
async def find_jobs_action(action):
    """Handle job search action"""
    try:
        # Get user profile for personalized search
        search_params = {
            "skills": user_context.get("skills", []),
            "experience_level": user_context.get("experience_level", "intermediate"),
            "preferred_rate": user_context.get("preferred_hourly_rate", 50),
            "location": user_context.get("location", "remote")
        }
        
        # Execute job search through agent
        jobs = await job_search_agent.search_jobs(search_params)
        
        if jobs:
            job_summary = f"Found {len(jobs)} relevant opportunities:\n\n"
            for i, job in enumerate(jobs[:5], 1):
                job_summary += f"**{i}. {job.get('title', 'Untitled')}**\n"
                job_summary += f"💰 ${job.get('budget', 'Not specified')}\n"
                job_summary += f"🏢 {job.get('company', 'Not specified')}\n"
                job_summary += f"📍 {job.get('location', 'Not specified')}\n\n"
            
            await cl.Message(content=job_summary).send()
        else:
            await cl.Message(
                content="No jobs found matching your criteria. Let me help you refine your search parameters."
            ).send()
            
    except Exception as e:
        logger.error(f"Error in job search action: {str(e)}")
        await cl.Message(content="Failed to search for jobs. Please try again.").send()

@cl.action_callback("market_research")
async def market_research_action(action):
    """Handle market research action"""
    try:
        # Get current market trends
        research_query = f"freelance market trends {user_context.get('primary_skill', 'technology')} 2024"
        research_results = await web_search_agent.search_web(research_query)
        
        if research_results:
            research_summary = "📈 **Current Market Insights:**\n\n"
            research_summary += research_results.get("summary", "Market analysis completed.")
            
            # Add trend visualization if available
            if research_results.get("trends"):
                research_summary += "\n\n📊 **Key Trends:**\n"
                for trend in research_results["trends"][:3]:
                    research_summary += f"• {trend}\n"
            
            await cl.Message(content=research_summary).send()
        else:
            await cl.Message(
                content="Unable to retrieve current market data. Please try again later."
            ).send()
            
    except Exception as e:
        logger.error(f"Error in market research: {str(e)}")
        await cl.Message(content="Failed to conduct market research. Please try again.").send()

@cl.action_callback("calculate_rates")
async def calculate_rates_action(action):
    """Handle rate calculation action"""
    try:
        # Get user's financial context
        user_data = {
            "experience_years": user_context.get("experience_years", 3),
            "skills": user_context.get("skills", []),
            "location": user_context.get("location", "US"),
            "target_income": user_context.get("target_annual_income", 75000)
        }
        
        # Calculate recommended rates
        rate_analysis = await math_agent.calculate_optimal_rates(user_data)
        
        if rate_analysis:
            rate_message = "💰 **Rate Analysis Results:**\n\n"
            rate_message += f"**Recommended Hourly Rate:** ${rate_analysis.get('hourly_rate', 50)}\n"
            rate_message += f"**Project Rate Range:** ${rate_analysis.get('project_min', 500)} - ${rate_analysis.get('project_max', 5000)}\n"
            rate_message += f"**Market Position:** {rate_analysis.get('market_position', 'Competitive')}\n\n"
            
            if rate_analysis.get("recommendations"):
                rate_message += "📋 **Recommendations:**\n"
                for rec in rate_analysis["recommendations"]:
                    rate_message += f"• {rec}\n"
            
            await cl.Message(content=rate_message).send()
        else:
            await cl.Message(
                content="Unable to calculate rates. Please provide more information about your experience and skills."
            ).send()
            
    except Exception as e:
        logger.error(f"Error in rate calculation: {str(e)}")
        await cl.Message(content="Failed to calculate rates. Please try again.").send()

@cl.action_callback("show_dashboard")
async def show_dashboard_action(action):
    """Handle dashboard display action"""
    await show_dashboard()

async def show_dashboard():
    """Display personalized dashboard with widgets"""
    try:
        dashboard_content = "📊 **Your FreelanceX.AI Dashboard**\n\n"
        
        # Get dashboard widgets based on user preferences
        widgets = await dashboard_manager.get_user_widgets(user_context)
        
        for widget in widgets:
            dashboard_content += f"### {widget['title']}\n"
            dashboard_content += f"{widget['content']}\n\n"
        
        # Add quick stats
        stats = await get_user_stats()
        if stats:
            dashboard_content += "### 📈 Quick Stats\n"
            dashboard_content += f"• **Active Job Searches:** {stats.get('active_searches', 0)}\n"
            dashboard_content += f"• **Applications This Month:** {stats.get('applications', 0)}\n"
            dashboard_content += f"• **Average Response Rate:** {stats.get('response_rate', 0)}%\n\n"
        
        await cl.Message(content=dashboard_content).send()
        
    except Exception as e:
        logger.error(f"Error displaying dashboard: {str(e)}")
        await cl.Message(content="Unable to display dashboard at this time.").send()

async def handle_voice_input(audio_data) -> str:
    """Process voice input and convert to text"""
    try:
        # Initialize speech recognition
        r = sr.Recognizer()
        
        # Convert audio data to text
        with sr.AudioFile(io.BytesIO(audio_data)) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
        
        # Process the transcribed text
        response = await route_text_message(f"Voice input: {text}")
        return f"🎤 I heard: \"{text}\"\n\n{response}"
        
    except sr.UnknownValueError:
        return "I couldn't understand the audio. Please try speaking more clearly."
    except sr.RequestError as e:
        logger.error(f"Speech recognition error: {str(e)}")
        return "Voice recognition service is currently unavailable."
    except Exception as e:
        logger.error(f"Voice input error: {str(e)}")
        return "Error processing voice input."

async def handle_image_input(image_element, text_context: str) -> str:
    """Process image input with context"""
    try:
        # Basic image processing
        image_info = f"📷 Image received: {image_element.name}\n"
        image_info += f"Size: {getattr(image_element, 'size', 'Unknown')}\n\n"
        
        # If there's text context, provide relevant assistance
        if text_context:
            response = await route_text_message(f"Analyze this image in context of: {text_context}")
            return image_info + response
        else:
            return image_info + "I can see your image. Please let me know how you'd like me to help analyze or use it."
            
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        return "Error processing the image. Please try uploading again."

async def route_text_message(content: str) -> str:
    """Intelligently route text messages to appropriate agents"""
    try:
        content_lower = content.lower()
        
        # Job search routing
        if any(keyword in content_lower for keyword in ["job", "work", "opportunity", "gig", "project", "hire"]):
            return await job_search_agent.process_message(content)
        
        # Research routing
        elif any(keyword in content_lower for keyword in ["research", "trend", "market", "industry", "competition"]):
            return await web_search_agent.process_message(content)
        
        # Math/calculation routing
        elif any(keyword in content_lower for keyword in ["calculate", "rate", "price", "budget", "tax", "income"]):
            return await math_agent.process_message(content)
        
        # Default to executive agent
        else:
            return await executive_agent.handle_message(content)
            
    except Exception as e:
        logger.error(f"Message routing error: {str(e)}")
        return "I encountered an error processing your message. Please try again."

async def store_interaction_memory(user_input: str, assistant_response: str):
    """Store interaction in long-term memory"""
    try:
        from backend.database import MemoryEntry
        import secrets
        
        memory_entry = MemoryEntry(
            memory_id=secrets.token_urlsafe(16),
            user_id=user_context.get("user_id", "anonymous"),
            agent_name="chainlit_ui",
            interaction_type="chat",
            content={
                "user_input": user_input,
                "assistant_response": assistant_response,
                "timestamp": datetime.now().isoformat()
            },
            metadata={
                "session_id": user_context.get("session_id"),
                "ui_version": "enhanced"
            },
            importance_score=0.5,
            created_at=datetime.now().isoformat()
        )
        
        await db_manager.store_memory(memory_entry)
        
    except Exception as e:
        logger.error(f"Memory storage error: {str(e)}")

async def get_user_stats() -> Dict[str, Any]:
    """Get user statistics for dashboard"""
    try:
        # This would fetch real user statistics from the database
        # Placeholder implementation
        return {
            "active_searches": 3,
            "applications": 12,
            "response_rate": 25,
            "total_earnings": 15000,
            "avg_project_value": 1250
        }
    except Exception as e:
        logger.error(f"Stats retrieval error: {str(e)}")
        return {}

@cl.on_settings_update
async def settings_update(settings):
    """Handle user settings updates"""
    try:
        user_context["preferences"].update(settings)
        
        # Apply settings changes
        if settings.get("notifications_enabled"):
            await cl.Message(content="✅ Notifications enabled").send()
        
        if settings.get("voice_enabled"):
            await cl.Message(content="🎤 Voice input activated").send()
        
        # Update dashboard layout if changed
        if settings.get("dashboard_layout"):
            await cl.Message(content=f"📊 Dashboard layout updated to {settings['dashboard_layout']}").send()
            
    except Exception as e:
        logger.error(f"Settings update error: {str(e)}")

# Background task for notifications
@cl.on_chat_start
async def setup_background_tasks():
    """Setup background tasks for notifications and updates"""
    try:
        # This would set up real-time notifications
        # Placeholder for background task initialization
        pass
    except Exception as e:
        logger.error(f"Background task setup error: {str(e)}")

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    print("FreelanceX.AI Enhanced Chainlit UI initialized")
    print("Ready to serve advanced freelancing assistance!")
