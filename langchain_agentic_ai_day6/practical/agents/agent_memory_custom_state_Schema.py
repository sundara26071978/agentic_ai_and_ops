"""
LangChain Agent Example: Custom State Schema

This example demonstrates:
- Extending AgentState with custom attributes
- Tracking user preferences and metadata beyond messages
- Persisting custom data across agent invocations

Custom state allows you to maintain application-specific data
throughout the agent's execution lifecycle.
"""
import pprint

from langchain.agents import AgentState
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


# Define a custom state schema by extending AgentState
class CustomState(AgentState):
    """Extended agent state with user preferences.
    
    Attributes:
        user_preferences (dict): Dictionary containing user-specific settings
                               like explanation style and verbosity level
    """
    user_preferences: dict


# Initialize the model
model = ChatOllama(model="qwen3.5:latest ")

# Create agent with custom state schema
# The agent can now track additional state beyond messages
agent = create_agent(
    model,
    state_schema=CustomState  # Use custom state instead of default AgentState
)

# Invoke the agent with both messages and custom state
# The agent can access and utilize the user_preferences throughout its execution
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "I prefer technical explanations"}],
        # Custom state attribute
        "user_preferences": {
            "style": "technical",  # Explanation style: technical, simple, etc.
            "verbosity": "detailed",  # Detail level: brief, detailed, comprehensive
        },
    }
)

# Pretty print the result
pprint.pprint(result)