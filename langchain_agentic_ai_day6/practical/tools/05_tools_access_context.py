"""
05_tools_access_context.py - Context-Aware Tools with ToolRuntime

This example demonstrates:
✅ Accessing immutable context data from tools
✅ User identity and session information
✅ Context injection via create_agent
✅ Dataclass-based context schemas
✅ Personalized tool behavior based on context

Context vs State:
- Context: Immutable, passed at invocation time (user ID, session)
- State: Mutable, changes during conversation (messages, preferences)

Prerequisites:
- Ollama running locally (ollama serve)
- ollama pull gemma4:latest

Message Flow:
1. User invokes agent with specific context (e.g., user_id="user123")
2. HumanMessage: User asks a question
3. AIMessage: Model calls tool that needs user-specific data
4. ToolMessage: Tool uses runtime.context to fetch user data
5. AIMessage: Model provides personalized response

Reference: https://docs.langchain.com/oss/python/langchain/tools#context
"""

from dataclasses import dataclass
import pprint
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime


# ============================================================================
# Define Context Schema
# ============================================================================

@dataclass
class UserContext:
    """Context data passed at invocation time.
    
    This dataclass defines what context information is available to tools.
    Context is immutable and same for all tools in a single invocation.
    """
    user_id: str  # Which user is making the request


# ============================================================================
# Define Context-Aware Tool
# ============================================================================

# User database - in production, this would be a real database
USER_DATABASE = {
    "user123": {
        "name": "Alice Johnson",
        "account_type": "Premium",
        "balance": 5000,
        "email": "alice@example.com"
    },
    "user456": {
        "name": "Bob Smith",
        "account_type": "Standard",
        "balance": 1200,
        "email": "bob@example.com"
    }
}


@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Get the current user's account information.
    
    This tool accesses runtime.context to get the user_id, then looks up
    account details. The same tool provides different results for different
    users based on context.
    
    Args:
        runtime: ToolRuntime containing context with user_id
    
    Returns:
        User's account information
    """
    # Access user_id from immutable context
    user_id = runtime.context.user_id
    
    # Look up user in database
    if user_id in USER_DATABASE:
        user = USER_DATABASE[user_id]
        return (
            f"Account holder: {user['name']}\n"
            f"Account Type: {user['account_type']}\n"
            f"Balance: ${user['balance']}\n"
            f"Email: {user['email']}"
        )
    
    return f"User '{user_id}' not found in database"


# ============================================================================
# Initialize Agent with Context Schema
# ============================================================================

print("=" * 70)
print("EXAMPLE: Context-Aware Tools")
print("=" * 70)

# Initialize the model with Ollama backend
model = init_chat_model("ollama:gemma4:latest")

# Create agent with context schema
# This tells the agent that tools may need UserContext
agent = create_agent(
    model,
    tools=[get_account_info],
    context_schema=UserContext,  # Define context schema
    system_prompt="You are a friendly financial assistant. Help users with their account information."
)


# ============================================================================
# Invoke Agent with Different Context Values
# ============================================================================

# Session 1: Query as user123 (Alice)
print("\n" + "=" * 70)
print("Session 1: Alice's Account")
print("=" * 70)

result1 = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my current balance?"}]},
    context=UserContext(user_id="user123")  # Pass context at invocation time
)

print("\n📝 Agent Response for user123:")
print(result1["messages"][-1].content if result1["messages"] else "No response")


# Session 2: Query as user456 (Bob)
print("\n" + "=" * 70)
print("Session 2: Bob's Account")
print("=" * 70)

result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my current balance and account type?"}]},
    context=UserContext(user_id="user456")  # Different context
)

print("\n📝 Agent Response for user456:")
print(result2["messages"][-1].content if result2["messages"] else "No response")


# Session 3: Invalid user
print("\n" + "=" * 70)
print("Session 3: Invalid User")
print("=" * 70)

result3 = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my account info?"}]},
    context=UserContext(user_id="user999")  # Non-existent user
)

print("\n📝 Agent Response for user999:")
print(result3["messages"][-1].content if result3["messages"] else "No response")


# ============================================================================
# Full Debug Output
# ============================================================================

print("\n" + "=" * 70)
print("Debug: Full Result for Alice")
print("=" * 70)
pprint.pprint(result1)