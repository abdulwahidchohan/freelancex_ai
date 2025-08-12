"""FreelanceX.AI Context Manager Agent
Session continuity & personalization
"""

from agents import Agent, function_tool as _function_tool
from functools import partial
tool = partial(_function_tool, strict_mode=False)
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextSnapshot(BaseModel):
    user_id: str = Field(..., description="User identifier")
    preferences: Dict[str, Any] = Field(..., description="User preferences and settings")
    recent_topics: List[str] = Field(..., description="Recent conversation topics")
    session_data: Dict[str, Any] = Field(..., description="Session-specific data")
    last_updated: str = Field(..., description="Last update timestamp")
    context_score: float = Field(..., description="Context relevance score (0-1)")


class UserProfile(BaseModel):
    user_id: str = Field(..., description="User identifier")
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    behavior_patterns: Dict[str, Any] = Field(..., description="User behavior patterns")
    expertise_level: str = Field(..., description="User expertise level")
    communication_style: str = Field(..., description="Preferred communication style")
    interests: List[str] = Field(..., description="User interests and focus areas")


class SessionContext(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    conversation_history: List[Dict[str, Any]] = Field(..., description="Conversation history")
    current_topic: str = Field(..., description="Current conversation topic")
    context_entities: List[str] = Field(..., description="Key entities in current context")
    sentiment: str = Field(..., description="Conversation sentiment")
    urgency_level: str = Field(..., description="Urgency level of the conversation")


class PersonalizationData(BaseModel):
    user_id: str = Field(..., description="User identifier")
    personalized_responses: List[str] = Field(..., description="Personalized response suggestions")
    recommended_actions: List[str] = Field(..., description="Recommended actions for the user")
    content_preferences: Dict[str, Any] = Field(..., description="Content preferences")
    interaction_history: Dict[str, Any] = Field(..., description="Interaction history")


@tool
def build_context(user_id: str, last_messages: List[str], session_data: Optional[Dict[str, Any]] = None) -> ContextSnapshot:
    """
    Build comprehensive context from user messages and session data.
    
    Args:
        user_id: User identifier
        last_messages: Recent conversation messages
        session_data: Optional session-specific data
        
    Returns:
        ContextSnapshot with detailed context information
    """
    try:
        logger.info(f"Building context for user: {user_id}")
        
        # Extract topics from recent messages
        topics = []
        for message in last_messages[-10:]:  # Last 10 messages
            if message and len(message.strip()) > 0:
                # Extract key topics from message
                words = message.lower().split()
                # Filter out common words and extract meaningful topics
                meaningful_words = [word for word in words if len(word) > 3 and word not in ['the', 'and', 'for', 'with', 'this', 'that']]
                topics.extend(meaningful_words[:3])  # Top 3 words per message
        
        # Remove duplicates and get most common topics
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        recent_topics = sorted(topic_counts.keys(), key=lambda x: topic_counts[x], reverse=True)[:5]
        
        # Build dynamic preferences based on conversation content
        preferences = {
            "tone": "professional",
            "detail_level": "standard",
            "response_format": "conversational"
        }
        
        # Analyze message content for tone preferences
        if any(word in ' '.join(last_messages).lower() for word in ['casual', 'informal', 'friendly']):
            preferences["tone"] = "casual"
        elif any(word in ' '.join(last_messages).lower() for word in ['formal', 'technical', 'detailed']):
            preferences["tone"] = "formal"
        
        # Analyze for detail level preferences
        if any(len(msg) > 200 for msg in last_messages):
            preferences["detail_level"] = "detailed"
        elif any(len(msg) < 50 for msg in last_messages):
            preferences["detail_level"] = "concise"
        
        # Build session data
        session_info = session_data or {}
        session_info.update({
            "message_count": len(last_messages),
            "session_duration": "ongoing",
            "last_activity": datetime.now().isoformat()
        })
        
        # Calculate context relevance score
        context_score = min(1.0, len(recent_topics) / 5.0 + len(last_messages) / 20.0)
        
        return ContextSnapshot(
            user_id=user_id,
            preferences=preferences,
            recent_topics=recent_topics,
            session_data=session_info,
            last_updated=datetime.now().isoformat(),
            context_score=context_score
        )
        
    except Exception as e:
        logger.error(f"Error building context: {e}")
        return ContextSnapshot(
            user_id=user_id,
            preferences={"tone": "professional", "detail_level": "standard"},
            recent_topics=[],
            session_data={"error": str(e)},
            last_updated=datetime.now().isoformat(),
            context_score=0.0
        )


@tool
def create_user_profile(user_id: str, interaction_data: Dict[str, Any]) -> UserProfile:
    """
    Create or update user profile based on interaction data.
    
    Args:
        user_id: User identifier
        interaction_data: User interaction data and preferences
        
    Returns:
        UserProfile with comprehensive user information
    """
    try:
        logger.info(f"Creating user profile for: {user_id}")
        
        # Extract preferences from interaction data
        preferences = interaction_data.get("preferences", {})
        
        # Analyze behavior patterns
        behavior_patterns = {
            "response_time": interaction_data.get("avg_response_time", "standard"),
            "session_frequency": interaction_data.get("session_frequency", "moderate"),
            "preferred_topics": interaction_data.get("topics", []),
            "interaction_style": interaction_data.get("style", "direct")
        }
        
        # Determine expertise level based on interaction complexity
        complexity_score = interaction_data.get("complexity_score", 0.5)
        if complexity_score > 0.8:
            expertise_level = "expert"
        elif complexity_score > 0.5:
            expertise_level = "intermediate"
        else:
            expertise_level = "beginner"
        
        # Determine communication style
        communication_style = "professional"
        if interaction_data.get("casual_interactions", 0) > interaction_data.get("formal_interactions", 0):
            communication_style = "casual"
        elif interaction_data.get("technical_interactions", 0) > interaction_data.get("general_interactions", 0):
            communication_style = "technical"
        
        # Extract interests from interaction history
        interests = interaction_data.get("interests", [])
        if not interests and "topics" in interaction_data:
            interests = interaction_data["topics"][:5]  # Top 5 topics
        
        return UserProfile(
            user_id=user_id,
            preferences=preferences,
            behavior_patterns=behavior_patterns,
            expertise_level=expertise_level,
            communication_style=communication_style,
            interests=interests
        )
        
    except Exception as e:
        logger.error(f"Error creating user profile: {e}")
        return UserProfile(
            user_id=user_id,
            preferences={},
            behavior_patterns={},
            expertise_level="beginner",
            communication_style="professional",
            interests=[]
        )


@tool
def manage_session_context(session_id: str, user_id: str, conversation_history: List[Dict[str, Any]]) -> SessionContext:
    """
    Manage and analyze session context for ongoing conversations.
    
    Args:
        session_id: Session identifier
        user_id: User identifier
        conversation_history: List of conversation messages
        
    Returns:
        SessionContext with session analysis
    """
    try:
        logger.info(f"Managing session context: {session_id}")
        
        # Extract current topic from recent messages
        recent_messages = conversation_history[-5:] if len(conversation_history) > 5 else conversation_history
        message_texts = [msg.get("content", "") for msg in recent_messages if msg.get("content")]
        
        # Analyze for current topic
        if message_texts:
            # Simple topic extraction (first few words of last message)
            last_message = message_texts[-1]
            current_topic = " ".join(last_message.split()[:3]).lower()
        else:
            current_topic = "general"
        
        # Extract context entities (key terms, names, concepts)
        context_entities = []
        for message in message_texts:
            words = message.lower().split()
            # Extract capitalized words and technical terms
            entities = [word for word in words if word[0].isupper() or len(word) > 8]
            context_entities.extend(entities[:3])  # Top 3 entities per message
        
        context_entities = list(set(context_entities))[:10]  # Unique entities, max 10
        
        # Analyze sentiment
        positive_words = ["good", "great", "excellent", "happy", "satisfied", "thanks"]
        negative_words = ["bad", "poor", "unhappy", "frustrated", "problem", "issue"]
        
        all_text = " ".join(message_texts).lower()
        positive_count = sum(1 for word in positive_words if word in all_text)
        negative_count = sum(1 for word in negative_words if word in all_text)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Determine urgency level
        urgency_indicators = ["urgent", "asap", "emergency", "critical", "immediate"]
        urgency_count = sum(1 for indicator in urgency_indicators if indicator in all_text)
        
        if urgency_count > 2:
            urgency_level = "high"
        elif urgency_count > 0:
            urgency_level = "medium"
        else:
            urgency_level = "low"
        
        return SessionContext(
            session_id=session_id,
            user_id=user_id,
            conversation_history=conversation_history,
            current_topic=current_topic,
            context_entities=context_entities,
            sentiment=sentiment,
            urgency_level=urgency_level
        )
        
    except Exception as e:
        logger.error(f"Error managing session context: {e}")
        return SessionContext(
            session_id=session_id,
            user_id=user_id,
            conversation_history=conversation_history,
            current_topic="general",
            context_entities=[],
            sentiment="neutral",
            urgency_level="low"
        )


@tool
def generate_personalization(user_id: str, context_snapshot: ContextSnapshot, user_profile: UserProfile) -> PersonalizationData:
    """
    Generate personalized content and recommendations based on user context and profile.
    
    Args:
        user_id: User identifier
        context_snapshot: Current context snapshot
        user_profile: User profile information
        
    Returns:
        PersonalizationData with personalized content
    """
    try:
        logger.info(f"Generating personalization for user: {user_id}")
        
        # Generate personalized response suggestions
        personalized_responses = []
        tone = context_snapshot.preferences.get("tone", "professional")
        expertise = user_profile.expertise_level
        
        if tone == "casual":
            personalized_responses.extend([
                "Hey there! Here's what I found for you...",
                "Got it! Let me help you with that...",
                "Sure thing! Here's the scoop..."
            ])
        elif tone == "formal":
            personalized_responses.extend([
                "Based on your request, I've prepared the following analysis...",
                "Per your requirements, here are the detailed findings...",
                "In accordance with your specifications, I present the following..."
            ])
        else:  # professional
            personalized_responses.extend([
                "I've analyzed your request and here are the results...",
                "Based on the information provided, here's what I found...",
                "Here's my assessment of your situation..."
            ])
        
        # Generate recommended actions based on context and profile
        recommended_actions = []
        if context_snapshot.recent_topics:
            for topic in context_snapshot.recent_topics[:3]:
                recommended_actions.append(f"Explore more about {topic}")
        
        if user_profile.expertise_level == "beginner":
            recommended_actions.extend([
                "Check out our getting started guide",
                "Review basic concepts and terminology"
            ])
        elif user_profile.expertise_level == "expert":
            recommended_actions.extend([
                "Access advanced features and APIs",
                "Explore integration options"
            ])
        
        # Build content preferences
        content_preferences = {
            "detail_level": context_snapshot.preferences.get("detail_level", "standard"),
            "format": context_snapshot.preferences.get("response_format", "conversational"),
            "topics": user_profile.interests,
            "style": user_profile.communication_style
        }
        
        # Build interaction history
        interaction_history = {
            "total_sessions": context_snapshot.session_data.get("session_count", 1),
            "preferred_topics": context_snapshot.recent_topics,
            "last_interaction": context_snapshot.last_updated,
            "context_score": context_snapshot.context_score
        }
        
        return PersonalizationData(
            user_id=user_id,
            personalized_responses=personalized_responses,
            recommended_actions=recommended_actions,
            content_preferences=content_preferences,
            interaction_history=interaction_history
        )
        
    except Exception as e:
        logger.error(f"Error generating personalization: {e}")
        return PersonalizationData(
            user_id=user_id,
            personalized_responses=["I'm here to help you."],
            recommended_actions=["Explore the platform"],
            content_preferences={},
            interaction_history={}
        )


context_manager_agent = Agent(
    name="Context Manager Agent",
    instructions="""You maintain session context and preferences for personalization in FreelanceX.AI.

Your responsibilities include:
- Building comprehensive context from user interactions
- Creating and updating user profiles
- Managing session context and conversation flow
- Generating personalized content and recommendations
- Maintaining continuity across user sessions

Always prioritize user experience and context relevance.""",
    tools=[build_context, create_user_profile, manage_session_context, generate_personalization],
)


