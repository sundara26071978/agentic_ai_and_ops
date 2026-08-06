"""
LangChain Agent Example: Streaming Agent Responses

This example demonstrates:
- Creating an agent and streaming its responses
- Listening to intermediate steps in real-time
- Handling different message types (user, assistant, tool calls)

Streaming allows you to display agent responses as they are generated,
providing real-time feedback to users.
"""
import pprint
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from langchain.messages import AIMessage, HumanMessage

# Select and initialize the model
# ChatOllama provides integration with Ollama models running locally
model_name = "qwen3.5:latest"
model_name = "gemma4:latest"
model = ChatOllama(model=model_name)

# Create a basic agent without explicit tools
# The agent can be used for reasoning-only tasks or with built-in capabilities
agent = create_agent(
    model,
)

# Stream agent responses using agent.stream()
# stream_mode="values" returns the full agent state at each step
# This is useful for displaying real-time progress to users
for chunk in agent.stream(
    {
        "messages": [{
            "role": "user",
            "content": "Search for AI news today and summarize the findings"
        }]
    },
    stream_mode="values"
):
    # Each chunk contains the complete agent state at that iteration
    latest_message = chunk["messages"][-1]
    
    # Handle different types of messages
    if latest_message.content:
        # Display human or assistant messages with their content
        if isinstance(latest_message, HumanMessage):
            print(f"User: {latest_message.content}")
        elif isinstance(latest_message, AIMessage):
            print(f"Agent: {latest_message.content}")
    elif latest_message.tool_calls:
        # Display tool calls (if any tools were being used)
        tool_names = [tc['name'] for tc in latest_message.tool_calls]
        print(f"Calling tools: {tool_names}")
