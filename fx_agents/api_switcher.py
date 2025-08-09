#!/usr/bin/env python3
"""
FreelanceX.AI API Switcher Utility
Provides utilities for switching between API providers and checking their status
"""

import logging
from typing import Dict, Any, List
from .api_provider import APIProvider, get_api_manager, reset_api_manager
from config.settings import get_config

logger = logging.getLogger(__name__)

class APISwitcher:
    """Utility class for managing API provider switching"""
    
    def __init__(self):
        self.config = get_config()
        self.api_manager = get_api_manager(self.config)
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available API providers with their status"""
        providers = []
        
        # Check OpenAI
        openai_status = {
            "name": "OpenAI",
            "provider": APIProvider.OPENAI,
            "available": False,
            "configured": bool(self.config.external_integrations.openai_api_key),
            "is_primary": self.config.external_integrations.primary_api_provider == "openai",
            "is_fallback": self.config.external_integrations.fallback_api_provider == "openai"
        }
        
        if openai_status["configured"]:
            openai_provider = self.api_manager.providers.get(APIProvider.OPENAI)
            openai_status["available"] = openai_provider.is_available() if openai_provider else False
        
        providers.append(openai_status)
        
        # Check Gemini
        gemini_status = {
            "name": "Google Gemini",
            "provider": APIProvider.GEMINI,
            "available": False,
            "configured": bool(self.config.external_integrations.google_gemini_api_key),
            "is_primary": self.config.external_integrations.primary_api_provider == "gemini",
            "is_fallback": self.config.external_integrations.fallback_api_provider == "gemini"
        }
        
        if gemini_status["configured"]:
            gemini_provider = self.api_manager.providers.get(APIProvider.GEMINI)
            gemini_status["available"] = gemini_provider.is_available() if gemini_provider else False
        
        providers.append(gemini_status)
        
        return providers
    
    def switch_primary_provider(self, provider_name: str) -> Dict[str, Any]:
        """Switch the primary API provider"""
        try:
            if provider_name.lower() not in ["openai", "gemini"]:
                return {
                    "success": False,
                    "error": f"Invalid provider: {provider_name}. Must be 'openai' or 'gemini'"
                }
            
            # Update configuration
            self.config.external_integrations.primary_api_provider = provider_name.lower()
            
            # Reset API manager to pick up new configuration
            reset_api_manager()
            self.api_manager = get_api_manager(self.config)
            
            logger.info(f"Switched primary provider to: {provider_name}")
            
            return {
                "success": True,
                "message": f"Successfully switched primary provider to {provider_name}",
                "new_primary": provider_name.lower(),
                "available_providers": self.get_available_providers()
            }
            
        except Exception as e:
            logger.error(f"Error switching provider: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to switch provider: {str(e)}"
            }
    
    def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """Test a specific API provider"""
        try:
            provider_enum = APIProvider(provider_name.lower())
            provider = self.api_manager.providers.get(provider_enum)
            
            if not provider:
                return {
                    "success": False,
                    "error": f"Provider {provider_name} not configured"
                }
            
            if not provider.is_available():
                return {
                    "success": False,
                    "error": f"Provider {provider_name} not available"
                }
            
            # Test with a simple request
            from .api_provider import ChatMessage, ChatCompletionRequest
            
            test_request = ChatCompletionRequest(
                messages=[
                    ChatMessage(role="user", content="Hello, this is a test message.")
                ],
                model=provider.get_model_name(),
                temperature=0.1,
                max_tokens=50
            )
            
            import asyncio
            response = asyncio.run(provider.chat_completion(test_request))
            
            return {
                "success": True,
                "message": f"Provider {provider_name} is working correctly",
                "response": response.content,
                "model": response.model
            }
            
        except Exception as e:
            logger.error(f"Error testing provider {provider_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Provider test failed: {str(e)}"
            }
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get a summary of all API providers' status"""
        providers = self.get_available_providers()
        
        available_count = sum(1 for p in providers if p["available"])
        configured_count = sum(1 for p in providers if p["configured"])
        
        primary_provider = next((p for p in providers if p["is_primary"]), None)
        fallback_provider = next((p for p in providers if p["is_fallback"]), None)
        
        return {
            "total_providers": len(providers),
            "configured_providers": configured_count,
            "available_providers": available_count,
            "primary_provider": primary_provider["name"] if primary_provider else None,
            "fallback_provider": fallback_provider["name"] if fallback_provider else None,
            "fallback_enabled": self.config.external_integrations.enable_api_fallback,
            "providers": providers
        }

# Global switcher instance
_switcher = None

def get_api_switcher() -> APISwitcher:
    """Get or create the global API switcher instance"""
    global _switcher
    if _switcher is None:
        _switcher = APISwitcher()
    return _switcher

# Convenience functions
def list_providers() -> List[Dict[str, Any]]:
    """List all available API providers"""
    return get_api_switcher().get_available_providers()

def switch_provider(provider_name: str) -> Dict[str, Any]:
    """Switch to a different primary API provider"""
    return get_api_switcher().switch_primary_provider(provider_name)

def test_provider(provider_name: str) -> Dict[str, Any]:
    """Test a specific API provider"""
    return get_api_switcher().test_provider(provider_name)

def get_status() -> Dict[str, Any]:
    """Get status summary of all providers"""
    return get_api_switcher().get_status_summary()
