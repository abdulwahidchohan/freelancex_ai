#!/usr/bin/env python3
"""
FreelanceX.AI API Provider Abstraction Layer
Supports OpenAI and Google Gemini APIs with automatic fallback
"""

import os
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """Supported API providers"""
    OPENAI = "openai"
    GEMINI = "gemini"

@dataclass
class ChatMessage:
    """Standardized chat message format"""
    role: str  # "system", "user", "assistant"
    content: str

@dataclass
class ChatCompletionRequest:
    """Standardized chat completion request"""
    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

@dataclass
class ChatCompletionResponse:
    """Standardized chat completion response"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

class BaseAPIProvider(ABC):
    """Abstract base class for API providers"""
    
    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Generate chat completion"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the API is available and configured"""
        pass
    
    def get_model_name(self) -> str:
        """Get the model name for this provider"""
        return self.model

class OpenAIProvider(BaseAPIProvider):
    """OpenAI API provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__(api_key, model)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            self.client = None
            logger.error("OpenAI client not available. Install with: pip install openai")
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.api_key and self.client is not None
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Generate chat completion using OpenAI API"""
        if not self.is_available():
            raise ValueError("OpenAI API not available")
        
        try:
            # Convert to OpenAI format
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            response = self.client.chat.completions.create(
                model=request.model or self.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
            
            return ChatCompletionResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage=response.usage.dict() if response.usage else None,
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

class GeminiProvider(BaseAPIProvider):
    """Google Gemini API provider implementation"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        super().__init__(api_key, model)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            self.client = None
            logger.error("Google Generative AI client not available. Install with: pip install google-generativeai")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.api_key and self.client is not None
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Generate chat completion using Gemini API"""
        if not self.is_available():
            raise ValueError("Gemini API not available")
        
        try:
            # Convert to Gemini format
            # Gemini doesn't have a direct chat completion API like OpenAI
            # We'll use the generate_content method with conversation history
            
            # Extract the last user message and build context from previous messages
            user_messages = [msg.content for msg in request.messages if msg.role == "user"]
            system_messages = [msg.content for msg in request.messages if msg.role == "system"]
            
            # Combine system messages into a single prompt
            system_prompt = "\n".join(system_messages) if system_messages else ""
            
            # Get the last user message
            user_message = user_messages[-1] if user_messages else ""
            
            # Build the full prompt
            full_prompt = f"{system_prompt}\n\nUser: {user_message}" if system_prompt else user_message
            
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    "temperature": request.temperature,
                    "max_output_tokens": request.max_tokens or 2048,
                }
            )
            
            return ChatCompletionResponse(
                content=response.text,
                model=self.model,
                usage=None,  # Gemini doesn't provide usage info in the same format
                finish_reason="stop"
            )
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

class APIManager:
    """Manages multiple API providers with fallback functionality"""
    
    def __init__(self, config):
        """Initialize API manager with configuration"""
        self.config = config
        self.providers: Dict[APIProvider, BaseAPIProvider] = {}
        self.primary_provider = APIProvider(config.external_integrations.primary_api_provider)
        self.fallback_provider = APIProvider(config.external_integrations.fallback_api_provider)
        self.enable_fallback = config.external_integrations.enable_api_fallback
        # Init cache
        from .cache import Cache
        self.cache = Cache(getattr(config.external_integrations, "redis_url", ""))
        
        # Initialize providers
        self._initialize_providers()
        self._last_cache_hit: bool = False
    
    def _initialize_providers(self):
        """Initialize available API providers"""
        # Initialize OpenAI provider
        if self.config.external_integrations.openai_api_key:
            self.providers[APIProvider.OPENAI] = OpenAIProvider(
                api_key=self.config.external_integrations.openai_api_key,
                model=self.config.agents.default_model
            )
        
        # Initialize Gemini provider
        if self.config.external_integrations.google_gemini_api_key:
            self.providers[APIProvider.GEMINI] = GeminiProvider(
                api_key=self.config.external_integrations.google_gemini_api_key,
                model="gemini-1.5-flash"  # Use a good default for Gemini
            )
        
        logger.info(f"Initialized providers: {list(self.providers.keys())}")
    
    def get_available_providers(self) -> List[BaseAPIProvider]:
        """Get list of available and configured providers"""
        return [provider for provider in self.providers.values() if provider.is_available()]
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Generate chat completion with fallback support"""
        # Cache key from model + last messages
        try:
            last = request.messages[-1].content if request.messages else ""
            sys = "\n".join([m.content for m in request.messages if m.role == "system"]) if request.messages else ""
            key = self.cache.make_key("cc", (request.model or ""), last[:256], sys[:256])
            cached = self.cache.get(key)
            if cached:
                self._last_cache_hit = True
                data = json.loads(cached)
                return ChatCompletionResponse(**data)
        except Exception:
            key = None
        self._last_cache_hit = False
        # Try primary provider first
        primary = self.providers.get(self.primary_provider)
        if primary and primary.is_available():
            try:
                logger.info(f"Using primary provider: {self.primary_provider.value}")
                resp = await primary.chat_completion(request)
                if key:
                    try:
                        self.cache.set(key, json.dumps(resp.__dict__), ttl_seconds=600)
                    except Exception:
                        pass
                return resp
            except Exception as e:
                logger.warning(f"Primary provider failed: {str(e)}")
                if not self.enable_fallback:
                    raise
        
        # Try fallback provider
        fallback = self.providers.get(self.fallback_provider)
        if fallback and fallback.is_available():
            try:
                logger.info(f"Using fallback provider: {self.fallback_provider.value}")
                resp = await fallback.chat_completion(request)
                if key:
                    try:
                        self.cache.set(key, json.dumps(resp.__dict__), ttl_seconds=600)
                    except Exception:
                        pass
                return resp
            except Exception as e:
                logger.error(f"Fallback provider also failed: {str(e)}")
        
        # If both fail, try any available provider
        for provider_name, provider in self.providers.items():
            if provider.is_available() and provider_name not in [self.primary_provider, self.fallback_provider]:
                try:
                    logger.info(f"Using alternative provider: {provider_name.value}")
                    resp = await provider.chat_completion(request)
                    if key:
                        try:
                            self.cache.set(key, json.dumps(resp.__dict__), ttl_seconds=600)
                        except Exception:
                            pass
                    return resp
                except Exception as e:
                    logger.warning(f"Alternative provider failed: {str(e)}")
                    continue
        
        raise RuntimeError("No API providers available")

    def was_last_cache_hit(self) -> bool:
        return self._last_cache_hit

# Global API manager instance
_api_manager = None

def get_api_manager(config=None) -> APIManager:
    """Get or create the global API manager instance"""
    global _api_manager
    if _api_manager is None:
        if config is None:
            from config.settings import get_config
            config = get_config()
        _api_manager = APIManager(config)
    return _api_manager

def reset_api_manager():
    """Reset the global API manager (useful for testing)"""
    global _api_manager
    _api_manager = None
