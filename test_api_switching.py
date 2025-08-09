#!/usr/bin/env python3
"""
FreelanceX.AI API Switching Test Utility
Test and demonstrate the multi-API provider functionality
"""

import os
import asyncio
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_api_switching():
    """Test the API switching functionality"""
    print("🚀 FreelanceX.AI API Switching Test")
    print("=" * 50)
    
    try:
        # Import our modules
        from fx_agents.api_switcher import get_status, list_providers, test_provider, switch_provider
        from fx_agents.api_provider import get_api_manager
        from config.settings import get_config
        
        # Get current status
        print("\n📊 Current API Provider Status:")
        status = get_status()
        print(f"Total Providers: {status['total_providers']}")
        print(f"Configured Providers: {status['configured_providers']}")
        print(f"Available Providers: {status['available_providers']}")
        print(f"Primary Provider: {status['primary_provider']}")
        print(f"Fallback Provider: {status['fallback_provider']}")
        print(f"Fallback Enabled: {status['fallback_enabled']}")
        
        # List all providers
        print("\n🔍 Detailed Provider Information:")
        providers = list_providers()
        for provider in providers:
            print(f"\n{provider['name']}:")
            print(f"  Configured: {'✅' if provider['configured'] else '❌'}")
            print(f"  Available: {'✅' if provider['available'] else '❌'}")
            print(f"  Primary: {'✅' if provider['is_primary'] else '❌'}")
            print(f"  Fallback: {'✅' if provider['is_fallback'] else '❌'}")
        
        # Test each configured provider
        print("\n🧪 Testing Configured Providers:")
        for provider in providers:
            if provider['configured']:
                print(f"\nTesting {provider['name']}...")
                result = test_provider(provider['name'].lower().replace(' ', ''))
                if result['success']:
                    print(f"  ✅ {provider['name']} is working!")
                    print(f"  Response: {result['response'][:100]}...")
                    print(f"  Model: {result['model']}")
                else:
                    print(f"  ❌ {provider['name']} failed: {result['error']}")
        
        # Test switching providers
        print("\n🔄 Testing Provider Switching:")
        available_providers = [p['name'].lower().replace(' ', '') for p in providers if p['configured']]
        
        if len(available_providers) > 1:
            for provider in available_providers:
                print(f"\nSwitching to {provider}...")
                result = switch_provider(provider)
                if result['success']:
                    print(f"  ✅ Successfully switched to {provider}")
                else:
                    print(f"  ❌ Failed to switch to {provider}: {result['error']}")
        else:
            print("  ⚠️  Need at least 2 configured providers to test switching")
        
        # Test API manager directly
        print("\n🔧 Testing API Manager:")
        config = get_config()
        api_manager = get_api_manager(config)
        
        print(f"Primary Provider: {api_manager.primary_provider.value}")
        print(f"Fallback Provider: {api_manager.fallback_provider.value}")
        print(f"Fallback Enabled: {api_manager.enable_fallback}")
        
        available = api_manager.get_available_providers()
        print(f"Available Providers: {[p.value for p in available]}")
        
        print("\n✅ API Switching Test Complete!")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure all dependencies are installed and the project structure is correct.")
    except Exception as e:
        print(f"❌ Test Error: {e}")
        logger.error(f"Test failed: {str(e)}")

def test_simple_conversation():
    """Test a simple conversation with the system"""
    print("\n💬 Testing Simple Conversation")
    print("=" * 40)
    
    try:
        from fx_agents.triage_agent import route_request
        
        # Test messages
        test_messages = [
            "Hello, how can you help me?",
            "Find Python developer jobs",
            "Calculate my project budget for $50/hour",
            "Write a proposal for web development",
            "Research market rates for React developers"
        ]
        
        for message in test_messages:
            print(f"\n🤖 User: {message}")
            try:
                result = asyncio.run(route_request(message))
                if result['success']:
                    print(f"✅ Response: {result['response'][:200]}...")
                    print(f"   Agent: {result['agent_used']}")
                    print(f"   Provider: {result['provider']}")
                    if result.get('handoffs'):
                        print(f"   Handoffs: {result['handoffs']}")
                else:
                    print(f"❌ Error: {result['error']}")
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
        
        print("\n✅ Conversation Test Complete!")
        
    except Exception as e:
        print(f"❌ Conversation Test Error: {e}")

def show_configuration_help():
    """Show help for configuring API keys"""
    print("\n🔧 Configuration Help")
    print("=" * 30)
    print("To use the API switching functionality, you need to set up API keys:")
    print()
    print("1. Create a .env file in your project root:")
    print("   touch .env")
    print()
    print("2. Add your API keys to the .env file:")
    print("   # OpenAI API Key")
    print("   OPENAI_API_KEY=your_openai_api_key_here")
    print("   # Google Gemini API Key")
    print("   GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here")
    print()
    print("3. Optional: Configure provider preferences:")
    print("   FREELANCEX_PRIMARY_API_PROVIDER=openai")
    print("   FREELANCEX_FALLBACK_API_PROVIDER=gemini")
    print("   FREELANCEX_ENABLE_API_FALLBACK=true")
    print()
    print("4. Get API keys from:")
    print("   - OpenAI: https://platform.openai.com/api-keys")
    print("   - Google Gemini: https://makersuite.google.com/app/apikey")
    print()

def main():
    """Main test function"""
    print("🎯 FreelanceX.AI API Switching Test Suite")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating one with template...")
        show_configuration_help()
        return
    
    # Run tests
    test_api_switching()
    test_simple_conversation()
    
    print("\n🎉 All tests completed!")
    print("\nTo run your FreelanceX.AI application:")
    print("   python -m chainlit run chainlit_app/main.py --host 127.0.0.1 --port 8000")

if __name__ == "__main__":
    main()
