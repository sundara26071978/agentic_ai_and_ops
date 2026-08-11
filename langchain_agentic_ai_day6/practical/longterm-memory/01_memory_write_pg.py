"""
01_memory_write_pg.py - Long-Term Memory with PostgreSQL Store

This example demonstrates persistent storage across sessions using LangGraph Store.
It uses PostgresStore for production-grade persistence.

Prerequisites:
- PostgreSQL database running
- Database connection string configured
- Or use InMemoryStore for development (no PostgreSQL needed)

To use PostgreSQL:
1. Install: pip install psycopg[binary]
2. Set DB_URI to your PostgreSQL connection string
3. Run: python 01_memory_write_pg.py

For development without PostgreSQL, use InMemoryStore instead.
"""

from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import ToolRuntime, tool
from langchain_core.runnables import Runnable
from langgraph.store.memory import InMemoryStore  # Use InMemoryStore for development
from typing_extensions import TypedDict


@dataclass
class Context:
    user_id: str


class UserInfo(TypedDict):
    name: str


@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """Save user info.
    
    This tool saves user information to the persistent store.
    The data persists across sessions.
    """
    assert runtime.store is not None
    runtime.store.put(("users",), runtime.context.user_id, dict(user_info))
    return f"Successfully saved user info for {runtime.context.user_id}."


# Initialize the model with Ollama backend
model = init_chat_model("ollama:gemma4:latest")

# Use InMemoryStore for development (no PostgreSQL needed)
# For production, replace with PostgreSQL configuration:
# DB_URI = "postgresql://postgres:admin@localhost:5432/ExampleStateDB?sslmode=disable"
# with PostgresStore.from_conn_string(DB_URI) as store:
#     store.setup()
#     ...

store = InMemoryStore()

agent: Runnable = create_agent(
    model,
    tools=[save_user_info],
    store=store,
    context_schema=Context,
    system_prompt="You are a helpful assistant. Help users save their information."
)

print("=" * 70)
print("Session 1: Saving User Information")
print("=" * 70)

# Save first user
result1 = agent.invoke(
    {"messages": [{"role": "user", "content": "My name is John Smith"}]},
    context=Context(user_id="user_123"),
)
print(f"\n✅ Session 1 Result:\n{result1['messages'][-1].content if result1['messages'] else 'No response'}")

# Save second user
result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "My name is Sunj"}]},
    context=Context(user_id="user_456"),
)
print(f"\n✅ Session 2 Result:\n{result2['messages'][-1].content if result2['messages'] else 'No response'}")

print("\n" + "=" * 70)
print("Store Contents (Persistent Data)")
print("=" * 70)

# Display what's stored
all_users = store.list(("users",))
for record in all_users:
    print(f"\nUser ID: {record.key}")
    print(f"Data: {record.value}")

print("\n✨ Data persists across invocations in the store!")