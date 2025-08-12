#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test fx_agents imports
        from fx_agents import dynamic_triage_agent, route_request
        print("✅ fx_agents imports successful")
        
        # Test memory imports
        from memory import get_memory, create_enhanced_session
        print("✅ memory imports successful")
        
        # Test config imports
        from config.settings import get_config
        print("✅ config imports successful")
        
        # Test triage agent initialization
        print("Testing triage agent...")
        triage = dynamic_triage_agent
        print("✅ Triage agent loaded successfully")
        
        # Test memory initialization
        print("Testing memory system...")
        memory = get_memory()
        print("✅ Memory system initialized successfully")
        
        print("\n🎉 All imports and initializations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
