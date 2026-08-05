"""
06_tools_access_longterm_memory.py - Long-Term Memory with Store

This example demonstrates:
✅ Persistent storage across sessions using runtime.store
✅ Store API: namespace/key pattern for organization
✅ Reading and writing to persistent storage
✅ InMemoryStore for development (loses data on restart)
✅ Long-term data management for multi-session scenarios

Store vs State vs Context:
- Store: Long-term memory, persistent across sessions
- State: Short-term memory, per-conversation
- Context: Immutable config, per-invocation

Prerequisites:
- Ollama running locally (ollama serve)
- ollama pull gemma4:latest

Session Pattern:
┌─── Session 1 ───┐         ┌─── Session 2 ───┐
│ save_user_info  │────────▶│ get_user_info   │
│ (alice)         │ Store   │ (retrieve alice)│
└─────────────────┘ ▲       └─────────────────┘
                    └─ Persists across sessions

Store Namespace Pattern:
  store.put(("users",), "user123", user_dict)
  store.get(("users",), "user123")
  
  Namespaces organize data hierarchically:
  ("users",)                    - All users
  ("users", "preferences")      - User preferences
  ("conversations", "user123")  - User conversations

Reference: https://docs.langchain.com/oss/python/langchain/tools#long-term-memory-store
"""

import pprint
from typing import Any
from langgraph.store.memory import InMemoryStore
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model


# ============================================================================
# Define Store-Aware Tools
# ============================================================================

@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Look up user info from persistent storage.
    
    This tool reads from the store (long-term memory). If the user exists,
    returns their information. Otherwise returns "Unknown user".
    
    Args:
        user_id: The ID of the user to look up
        runtime: ToolRuntime providing access to store
    
    Returns:
        User information as a string or "Unknown user"
    """
    # Access the store from runtime
    store = runtime.store
    
    # Query the store using namespace/key pattern
    # Namespace: ("users",) - All users
    # Key: user_id - Specific user
    user_info = store.get(("users",), user_id)
    
    if user_info:
        return str(user_info.value)
    
    return f"Unknown user: {user_id}"


@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """Save user info to persistent storage.
    
    This tool writes to the store (long-term memory). Data saved here
    persists across sessions and is available to all agents using this store.
    
    Args:
        user_id: The ID of the user to save
        user_info: Dictionary containing user information
        runtime: ToolRuntime providing access to store
    
    Returns:
        Confirmation message
    """
    # Access the store from runtime
    store = runtime.store
    
    # Save to store using namespace/key pattern
    # Namespace: ("users",) - All users
    # Key: user_id - Specific user
    # Value: user_info - The data to store
    store.put(("users",), user_id, user_info)
    
    return f"Successfully saved user info for {user_id}"


# ============================================================================
# Initialize Model and Create Agent with Store
# ============================================================================

print("=" * 70)
print("EXAMPLE: Long-Term Memory with Store")
print("=" * 70)

# Initialize the model with Ollama backend
model = init_chat_model("ollama:gemma4:latest")

# Create an InMemoryStore for this example
# In production, use PostgresStore for persistence across service restarts
store = InMemoryStore()

# Create agent with store
agent = create_agent(
    model,
    tools=[get_user_info, save_user_info],
    store=store,  # Pass the store to the agent
    system_prompt="You are a helpful data assistant. Help users save and retrieve their information."
)


# ============================================================================
# Session 1: Save User Data
# ============================================================================

print("\n" + "=" * 70)
print("Session 1: Save User Data")
print("=" * 70)

print("\n💾 Saving Alice's information...")
result1 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Save the following user: user_id: abc123, name: Alice Johnson, age: 30, email: alice@example.com"
    }]
})

print(result1["messages"][-1].content if result1["messages"] else "No response")


print("\n💾 Saving Bob's information...")
result2 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Save the following user: user_id: abc456, name: Bob Smith, age: 25, email: bob@example.com"
    }]
})

print(result2["messages"][-1].content if result2["messages"] else "No response")


# ============================================================================
# Session 2: Retrieve User Data
# ============================================================================

print("\n" + "=" * 70)
print("Session 2: Retrieve User Data (from persistent store)")
print("=" * 70)

print("\n🔍 Retrieving Alice's information...")
result3 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Get user info for user with id 'abc123'"
    }]
})

print(result3["messages"][-1].content if result3["messages"] else "No response")


print("\n🔍 Retrieving Bob's information...")
result4 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Get user info for user with id 'abc456'"
    }]
})

print(result4["messages"][-1].content if result4["messages"] else "No response")


# ============================================================================
# Session 3: Retrieve Non-Existent User
# ============================================================================

print("\n" + "=" * 70)
print("Session 3: Query Non-Existent User")
print("=" * 70)

print("\n🔍 Trying to retrieve non-existent user...")
result5 = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Get user info for user with id 'xyz789'"
    }]
})

print(result5["messages"][-1].content if result5["messages"] else "No response")


# ============================================================================
# Store Contents Inspection
# ============================================================================

print("\n" + "=" * 70)
print("Store Contents (Debugging)")
print("=" * 70)

print("\n📦 All stored users:")
all_users = store.list(("users",))
for record in all_users:
    print(f"  User ID: {record.key}")
    print(f"  Data: {record.value}")
    print()


# ============================================================================
# Store Organization Example
# ============================================================================

print("=" * 70)
print("Store Organization: Namespace Patterns")
print("=" * 70)
print("""
Example namespace hierarchy:

("users",)
  └─ abc123: {"name": "Alice", "age": 30}
  └─ abc456: {"name": "Bob", "age": 25}

("users", "preferences")
  └─ abc123: {"theme": "dark", "language": "en"}
  └─ abc456: {"theme": "light", "language": "fr"}

("conversations", "abc123")
  └─ conv_001: [messages...]
  └─ conv_002: [messages...]

Store API:
  store.put(namespace, key, value)    # Save
  store.get(namespace, key)           # Retrieve
  store.delete(namespace, key)        # Delete
  store.list(namespace)               # List all in namespace
""")