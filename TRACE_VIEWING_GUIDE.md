# FreelanceX.AI Trace Viewing Guide

This guide explains how to use the OpenAI Dashboard to view traces of your agent runs, which is a powerful feature of the OpenAI Agent SDK.

## What are Traces?

Traces provide a detailed view of your agent's execution, including:
- Messages sent to and from the model
- Tool calls and their results
- Handoffs between agents
- Timing information

This information is invaluable for debugging, monitoring, and improving your agents.

## Viewing Traces

1. **Access the OpenAI Dashboard**
   - Go to [https://platform.openai.com/traces](https://platform.openai.com/traces)
   - Log in with your OpenAI account (the same one associated with your API key)

2. **Navigate to the Traces Section**
   - In the left sidebar, click on "Traces"

3. **Filter and Search**
   - You can filter traces by time period, agent name, or search for specific content
   - Click on any trace to view its details

4. **Analyze Trace Details**
   - View the complete conversation history
   - See which tools were called and their inputs/outputs
   - Examine handoffs between agents
   - Check timing information to identify bottlenecks

## Enabling Tracing

Tracing is enabled by default in the OpenAI Agent SDK. However, you can control tracing behavior:

```python
# Disable tracing for a specific run
result = await Runner.run(agent, message, trace=False)

# Enable tracing with a custom run ID
import uuid
run_id = str(uuid.uuid4())
result = await Runner.run(agent, message, trace_id=run_id)
```

## Best Practices

1. **Use Descriptive Agent Names**
   - Give your agents clear, descriptive names to make them easier to identify in traces

2. **Add Metadata to Traces**
   - You can add custom metadata to traces for better organization:
   ```python
   from agents import set_trace_metadata
   set_trace_metadata({"user_id": "123", "session_type": "freelance_consultation"})
   ```

3. **Regular Review**
   - Regularly review traces to identify patterns, errors, or areas for improvement
   - Look for repeated tool calls or inefficient handoffs

4. **Privacy Considerations**
   - Remember that trace data is stored on OpenAI's servers
   - Avoid including sensitive personal information in your agent interactions

## Troubleshooting

If you don't see traces in the dashboard:

1. Verify your API key is correctly set
2. Ensure tracing is enabled (it is by default)
3. Check that you're logged into the correct OpenAI account
4. Allow some time for traces to appear (there can be a short delay)

## Further Resources

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [OpenAI Platform Dashboard](https://platform.openai.com/)