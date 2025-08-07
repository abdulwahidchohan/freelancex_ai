"""Test script to verify OpenAI Agents SDK import"""

try:
    # Try importing with underscores
    import openai_agents
    print("Successfully imported openai_agents with underscores")
    print(f"Module location: {openai_agents.__file__}")
except ImportError as e1:
    print(f"Error importing openai_agents with underscores: {e1}")

# Try importing specific components
try:
    from openai_agents import Agent, Runner, Session
    print("Successfully imported specific components from openai_agents")
except ImportError as e3:
    print(f"Error importing specific components: {e3}")