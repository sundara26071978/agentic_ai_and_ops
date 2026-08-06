"""
LangChain Agent Example: Tool Error Handling

This example demonstrates:
- Handling tool execution errors gracefully
- Providing meaningful error messages back to the agent
- Using middleware for error interception
- Custom error recovery strategies

Error handling ensures agents can recover from failures and
provide helpful feedback to users.
"""
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain_ollama import ChatOllama

from agents.agent_dynamicmodels import get_weather


# Middleware for handling tool execution errors
@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages.
    
    When a tool fails:
    1. Catch the exception
    2. Create a meaningful error message
    3. Return the message to the agent for retry/recovery
    
    Args:
        request: The tool call request
        handler: The actual tool execution handler
    
    Returns:
        ToolMessage with either the tool result or error message
    """
    try:
        # Attempt to execute the tool
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        # This allows the agent to understand and potentially recover from the error
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


# Initialize the model
model = ChatOllama(model="gemma4:latest")

# Create agent with error handling middleware
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="you are a helpful assistant",
    middleware=[handle_tool_errors]  # Apply error handling middleware
)

# Invoke the agent
# If the get_weather tool fails, the error handler will catch it and provide feedback
result = agent.invoke({
    "messages": [{"role": "user", "content": "What is the weather in Delhi?"}]
})

print(result)