"""
LangChain Agent Example: Dynamic System Prompt Based on User Context

This example demonstrates:
- Customizing system prompts dynamically at runtime
- Tailoring agent behavior based on user role or context
- Using @dynamic_prompt decorator for middleware
- Context-aware response generation

Dynamic prompts enable personalized agent behavior, optimized for
specific user types (e.g., beginner vs expert).
"""
import pprint
from typing import TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_ollama import ChatOllama


# Define the context schema
class Context(TypedDict):
    """Runtime context for prompt customization.
    
    Attributes:
        user_role: The user's role affecting prompt generation
    """
    user_role: str


# Define a dynamic prompt function
@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """Generate system prompt based on user role.
    
    Different users get different system prompts:
    - Experts: Detailed technical responses
    - Beginners: Simple explanations without jargon
    
    Args:
        request: The model request containing user context
    
    Returns:
        The customized system prompt for the user
    """
    # Extract user role from runtime context
    user_role = request.runtime.context.get("user_role", "user")
    
    # Base prompt for all users
    base_prompt = "You are a helpful assistant."

    # Customize based on user role
    if user_role == "expert":
        return f"{base_prompt} Provide detailed technical responses."
    elif user_role == "beginner":
        return f"{base_prompt} Explain concepts simply and avoid jargon."

    return base_prompt


# Initialize the model
model = ChatOllama(model="qwen3.5:latest ")

# Create agent with dynamic prompt middleware
agent = create_agent(
    model=model,
    middleware=[user_role_prompt],  # Apply dynamic prompt middleware
    context_schema=Context  # Provide type schema for context
)

# Example 1: Invoke with expert context
# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "Explain machine learning"}]},
#     context={"user_role": "expert"}
# )


# Example 2: Invoke with beginner context
# The system prompt will be customized for beginners
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Explain machine learning"}]},
    context={"user_role": "beginner"}
)

# Pretty print the last message (the agent's response)
pprint.pprint(result["messages"][-1].content_blocks)