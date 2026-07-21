"""
04_model_toolcalling.py - Tool Binding & Function Calling (Model-Side)

This example demonstrates:
1. Creating tools with @tool decorator
2. Binding tools to models with bind_tools()
3. Extracting tool calls from model responses
4. Analyzing tool call arguments

Key Concepts:
  - Tool: A function the model can call (not executed by default)
  - bind_tools(): Makes model aware of available tools
  - tool_calls: Array of tool calls the model decided to make
  - This is Step 1 of a 3-step tool calling workflow

Three-Step Tool Calling Pattern:
  1. Model decides to call a tool → returns tool_calls
  2. Execute the tool with provided arguments
  3. Return results to model for final response

Use bind_tools() for:
  - Agents that need external functions
  - Planning tasks before execution
  - Multi-step workflows
  - Autonomous systems

Resources:
  - Tool Calling: https://docs.langchain.com/oss/python/langchain/frontend/tool-calling
  - Tools Guide: https://docs.langchain.com/oss/python/langchain/tools
"""

import pprint
from langchain.chat_models import init_chat_model
from langchain.tools import tool

# Define a tool using the @tool decorator
# The docstring becomes the tool description for the model
@tool
def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"It's sunny in {location}."

@tool
def get_time(location: str) -> str:
    """Get the current time at a location."""
    return f"The current time in {location} is 12:00 PM."

# Initialize the model
model = init_chat_model("ollama:gemma4:latest")

# Bind tools to the model
# The model now knows about get_weather and can call it
model_with_tools = model.bind_tools([get_weather, get_time]) 

# Ask the model something that requires tool calling
# The model will recognize it needs to call get_weather
response = model_with_tools.invoke("What's the weather like in Boston and New York and get the time in London")

print("Full Response:")
pprint.pprint(response)

# Extract and display tool calls
print("\nTool Calls Made:")
for tool_call in response.tool_calls:
    # tool_call is a dict with 'name' and 'args' keys
    print(f"📞 Tool: {tool_call['name']}")
    print(f"   Args: {tool_call['args']}")
    print(f"   ID: {tool_call['id']}")
