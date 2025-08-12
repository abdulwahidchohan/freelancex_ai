#!/usr/bin/env python3
"""
FreelanceX.AI Enhanced API Provider Abstraction Layer
Dynamic multi-provider support with OpenAI and Google Gemini APIs and automatic fallback
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List, Type
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import json
from config.settings import get_config

logger = logging.getLogger(__name__)

class APIProvider(Enum):
    """Supported API providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"

@dataclass
class ChatMessage:
    """Standardized chat message format"""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatCompletionRequest:
    """Standardized chat completion request"""
    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChatCompletionResponse:
    """Standardized chat completion response"""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProviderConfig:
    """Configuration for API providers"""
    name: str
    api_key: str
    model: str
    enabled: bool = True
    priority: int = 1
    retry_attempts: int = 3
    timeout: float = 30.0
    custom_config: Dict[str, Any] = field(default_factory=dict)

class BaseAPIProvider(ABC):
    """Abstract base class for API providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.provider_name = config.name
        self.api_key = config.api_key
        self.model = config.model
        self.enabled = config.enabled
        self.priority = config.priority
        self.retry_attempts = config.retry_attempts
        self.timeout = config.timeout
        
        # Initialize provider-specific client
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client"""
        pass
    
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
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the provider connection"""
        try:
            test_request = ChatCompletionRequest(
                messages=[ChatMessage(role="user", content="Hello")],
                model=self.model,
                max_tokens=10
            )
            response = await self.chat_completion(test_request)
            return {
                "success": True,
                "provider": self.provider_name,
                "model": self.model,
                "response_time": getattr(response, 'response_time', None)
            }
        except Exception as e:
            return {
                "success": False,
                "provider": self.provider_name,
                "error": str(e)
            }

class OpenAIProvider(BaseAPIProvider):
    """OpenAI API provider implementation"""
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"OpenAI client initialized for {self.provider_name}")
        except ImportError:
            self.client = None
            logger.error("OpenAI client not available. Install with: pip install openai")
        except Exception as e:
            self.client = None
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self.api_key and self.client is not None and self.enabled
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Generate chat completion using OpenAI API"""
        if not self.is_available():
            raise ValueError(f"OpenAI API not available for {self.provider_name}")
        
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
                content=response.choices[0].message.content or "",
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None,
                finish_reason=response.choices[0].finish_reason,
                metadata={
                    "provider": "openai",
                    "model": response.model,
                    "usage": response.usage.model_dump() if response.usage else {}
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error for {self.provider_name}: {str(e)}")
            raise

class GeminiProvider(BaseAPIProvider):
    """Google Gemini API provider implementation"""
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai
            logger.info(f"Gemini client initialized for {self.provider_name}")
        except ImportError:
            self.client = None
            logger.error("Google Generative AI not available. Install with: pip install google-generativeai")
        except Exception as e:
            self.client = None
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Gemini API is available"""
        return self.api_key and self.client is not None and self.enabled
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Generate chat completion using Gemini API"""
        if not self.is_available():
            raise ValueError(f"Gemini API not available for {self.provider_name}")
        
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in request.messages:
                if msg.role == "system":
                    # Gemini doesn't have system messages, prepend to first user message
                    if gemini_messages and gemini_messages[-1]["role"] == "user":
                        gemini_messages[-1]["parts"] = [f"{msg.content}\n\n{gemini_messages[-1]['parts'][0]}"]
                    else:
                        gemini_messages.append({"role": "user", "parts": [msg.content]})
                else:
                    gemini_messages.append({
                        "role": msg.role,
                        "parts": [msg.content]
                    })
            
            # Create model
            model = self.client.GenerativeModel(self.model)
            
            # Generate response
            response = await asyncio.to_thread(
                model.generate_content,
                gemini_messages,
                generation_config=self.client.types.GenerationConfig(
                    temperature=request.temperature,
                    max_output_tokens=request.max_tokens
                )
            )
            
            return ChatCompletionResponse(
                content=response.text or "",
                model=self.model,
                finish_reason="stop",
                metadata={
                    "provider": "gemini",
                    "model": self.model,
                    "usage": {
                        "prompt_tokens": getattr(response, 'usage_metadata', {}).get('prompt_token_count', 0),
                        "completion_tokens": getattr(response, 'usage_metadata', {}).get('candidates_token_count', 0)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Gemini API error for {self.provider_name}: {str(e)}")
            raise

class APIManager:
    """Enhanced API manager with dynamic provider management"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.providers: Dict[APIProvider, BaseAPIProvider] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Dynamically initialize all configured providers"""
        try:
            # Load provider configurations
            self._load_provider_configs()
            
            # Initialize providers
            provider_classes = {
                APIProvider.OPENAI: OpenAIProvider,
                APIProvider.GEMINI: GeminiProvider,
            }
            
            for provider_enum, provider_class in provider_classes.items():
                config = self.provider_configs.get(provider_enum.value)
                if config and config.enabled:
                    try:
                        provider = provider_class(config)
                        if provider.is_available():
                            self.providers[provider_enum] = provider
                            logger.info(f"Initialized {provider_enum.value} provider: {config.name}")
                    except Exception as e:
                        logger.error(f"Failed to initialize {provider_enum.value} provider: {str(e)}")
            
            logger.info(f"API Manager initialized with {len(self.providers)} providers")
            
        except Exception as e:
            logger.error(f"Failed to initialize API providers: {str(e)}")
            raise
    
    def _load_provider_configs(self):
        """Load provider configurations from settings"""
        try:
            # OpenAI configuration
            if self.config.api.openai_api_key:
                self.provider_configs[APIProvider.OPENAI.value] = ProviderConfig(
                    name="OpenAI",
                    api_key=self.config.api.openai_api_key,
                    model=self.config.agents.default_model or "gpt-4o-mini",
                    enabled=True,
                    priority=1,  # Default to OpenAI as primary
                    retry_attempts=3,
                    timeout=30.0
                )
            
            # Gemini configuration
            if self.config.api.google_api_key:
                self.provider_configs[APIProvider.GEMINI.value] = ProviderConfig(
                    name="Google Gemini",
                    api_key=self.config.api.google_api_key,
                    model="gemini-pro",
                    enabled=True,
                    priority=2,  # Secondary priority
                    retry_attempts=3,
                    timeout=30.0
                )
            
            # Anthropic configuration (future support)
            if self.config.api.anthropic_api_key:
                self.provider_configs[APIProvider.ANTHROPIC.value] = ProviderConfig(
                    name="Anthropic",
                    api_key=self.config.api.anthropic_api_key,
                    model="claude-3-sonnet-20240229",
                    enabled=False,  # Not implemented yet
                    priority=3,
                    retry_attempts=3,
                    timeout=30.0
                )
                
        except Exception as e:
            logger.error(f"Failed to load provider configurations: {str(e)}")
            raise
    
    def get_available_providers(self) -> List[BaseAPIProvider]:
        """Get list of available providers"""
        return list(self.providers.values())
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Get chat completion with automatic fallback"""
        errors = []
        
        # Sort providers by priority
        sorted_providers = sorted(
            self.providers.items(),
            key=lambda x: x[1].priority
        )
        
        for provider_enum, provider in sorted_providers:
            try:
                logger.debug(f"Trying {provider.provider_name} for chat completion")
                response = await provider.chat_completion(request)
                logger.info(f"Successfully used {provider.provider_name}")
                return response
                
            except Exception as e:
                error_msg = f"{provider.provider_name}: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"Provider {provider.provider_name} failed: {str(e)}")
                continue
        
        # All providers failed
        error_summary = "; ".join(errors)
        raise Exception(f"All API providers failed: {error_summary}")

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {}
        for provider_enum, provider in self.providers.items():
            status[provider_enum.value] = {
                "name": provider.provider_name,
                "available": provider.is_available(),
                "model": provider.model,
                "priority": provider.priority,
                "enabled": provider.enabled
            }
        return status
    
    async def test_all_providers(self) -> Dict[str, Any]:
        """Test all available providers"""
        results = {}
        for provider_enum, provider in self.providers.items():
            results[provider_enum.value] = await provider.test_connection()
        return results
    
    def add_provider(self, provider_enum: APIProvider, provider: BaseAPIProvider):
        """Dynamically add a provider"""
        self.providers[provider_enum] = provider
        logger.info(f"Added provider: {provider.provider_name}")
    
    def remove_provider(self, provider_enum: APIProvider):
        """Remove a provider"""
        if provider_enum in self.providers:
            provider_name = self.providers[provider_enum].provider_name
            del self.providers[provider_enum]
            logger.info(f"Removed provider: {provider_name}")

# Global API manager instance
_api_manager: Optional[APIManager] = None

def get_api_manager(config=None) -> APIManager:
    """Get or create the global API manager instance"""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager(config)
    return _api_manager

def reset_api_manager():
    """Reset the global API manager instance"""
    global _api_manager
    _api_manager = None

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
