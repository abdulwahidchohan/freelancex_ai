# FreelanceX.AI Examples

This directory contains example scripts demonstrating how to use FreelanceX.AI with the OpenAI Agent SDK.

## Available Examples

### agent_sdk_example.py

A simple command-line example showing how to:
- Create a session
- Run the triage agent
- Access trace information
- Handle errors

#### Usage

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-api-key-here  # Linux/Mac
$env:OPENAI_API_KEY="your-api-key-here"  # Windows PowerShell

# Run the example
python agent_sdk_example.py "I need help finding freelance jobs for Python developers"
```

## Creating Your Own Examples

Feel free to create additional examples in this directory. Some ideas:

- Direct usage of specialized agents (bypassing the triage agent)
- Custom tool implementations
- Integration with external APIs
- Batch processing of requests