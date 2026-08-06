"""
LangChain Agent Example: Dynamic Tool Filtering Based on Runtime Context

This example demonstrates:
- Filtering tools based on user role/permissions from runtime context
- Role-based access control (RBAC) patterns
- Using InMemoryStore for feature flags and preferences
- Context schema for typed runtime parameters

Context-based filtering enables role-based security policies where
different users get different tool capabilities.
"""
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable
from langgraph.store.memory import InMemoryStore


# Define the runtime context schema
# This provides type hints and structure for user context data
@dataclass
class Context:
    """Runtime context for the agent.
    
    Attributes:
        user_role: The user's role (admin, editor, viewer)
    """
    user_role: str


# Initialize the model
model = ChatOllama(model="qwen3.5:latest")


# Middleware for context-based tool filtering
@wrap_model_call
def context_based_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Filter tools based on Runtime Context permissions.
    
    RBAC Policy:
    - admin: Access to all tools
    - editor: Can access read and write tools, but not delete
    - viewer: Read-only access
    
    Args:
        request: The model request with runtime context
        handler: The next handler in the middleware chain
    
    Returns:
        The response after processing with role-appropriate tools
    """
    # Read from Runtime Context: get user role
    # Safely handle cases where context is not provided
    if request.runtime is None or request.runtime.context is None:
        # If no context provided, default to viewer (most restrictive)
        user_role = "viewer"
    else:
        user_role = request.runtime.context.user_role

    # Apply role-based tool filtering
    if user_role == "admin":
        # Admins get all tools
        pass  # All tools remain available
    elif user_role == "editor":
        # Editors can't delete
        tools = [t for t in request.tools if t.name != "delete_data"]
        request = request.override(tools=tools)
    else:  # viewer or default
        # Viewers get read-only tools
        tools = [t for t in request.tools if t.name.startswith("read_")]
        request = request.override(tools=tools)

    return handler(request)



# Initialize InMemoryStore for feature flags and user preferences
# Note: For production, use a persistent store like a database
store = InMemoryStore()

# Write sample data to the store
# This data represents user preferences and feature flags
store.put(
    ("features",),  # Namespace to group related data
    "user_123",     # Key within the namespace (user ID)
    {
        "user_id": "user_123",
        "name": "Sundara",
        "enabled_tools": ["public_get_weather", "private_search"],  # User-specific tool access
    },
)


# Tool definitions with role-based naming
def read_data(key: str) -> str:
    """Read data for a given key.
    
    Available to viewers, editors, and admins.
    """
    return f"Reading data for {key}..."


def write_data(key: str, value: str) -> str:
    """Write data for a given key.
    
    Available to editors and admins.
    """
    return f"Writing data for {key}: {value}..."


def delete_data(key: str) -> str:
    """Delete data for a given key.
    
    Available to admins only.
    """
    return f"Deleting data for {key}..."


# Create agent with context-based tool filtering
agent = create_agent(
    model=model, 
    tools=[read_data, write_data, delete_data],
    system_prompt="you are a helpful assistant that provides weather information and can search the web.",
    middleware=[context_based_tools],  # Apply role-based filtering
    context_schema=Context  # Use Context for type validation
)

# Set the user role for this execution
# Try different roles: "viewer", "editor", "admin"
context = Context(user_role="viewer")  # Viewer - read-only access
# context = Context(user_role="editor")  # Editor - read and write
# context = Context(user_role="admin")   # Admin - full access

# Invoke the agent with different user requests
result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "read data for key1"},
            {"role": "user", "content": "Write data for key1 with value 'hello'"},
            # {"role": "user", "content": "Delete data for key1"}  # Uncomment to test delete
        ]
    },
    context=context  # Pass the user context to the agent
)

print(result)

