# Tools Module - LangChain Tool Calling Guide

Learn how to create, bind, and manage tools for AI agents using LangChain with **Ollama** as the local language model provider.

## 📋 Prerequisites

### Required
- **Ollama** installed and running (`ollama serve`)
- **Python 3.11+** in virtual environment
- **LangChain** and dependencies installed

### Recommended Models for Tools
```bash
ollama pull qwen3.5:latest      # Balanced, good for tool calling
ollama pull gemma4:latest       # Fast and capable
ollama pull deepseek-r1:latest  # Advanced reasoning
```

### Key Dependencies
```python
# Core packages used in these examples
langchain
langchain-core
langchain-community
langgraph
ollama
pydantic  # For schema definition
```

---

## 🎯 Module Overview

This module demonstrates **6 progressive examples** of tool creation and usage:

| File | Topic | Complexity | Key Learning |
|------|-------|-----------|--------------|
| `01_tools_with_model.py` | Basic tool definition | ⭐ Beginner | Create simple tools with `@tool` decorator |
| `02_tools_with_schema_pydantic.py` | Pydantic schema validation | ⭐⭐ Intermediate | Define structured input schemas |
| `03_tools_with_schema_json.py` | JSON schema validation | ⭐⭐ Intermediate | Use raw JSON for schema definition |
| `04_tools_stateaccess_toolruntiem.py` | State access via ToolRuntime | ⭐⭐⭐ Advanced | Access conversation state and custom fields |
| `05_tools_access_context.py` | Context-aware tools | ⭐⭐⭐ Advanced | Access immutable context data (user IDs, session info) |
| `06_tools_access_longterm_memory.py` | Long-term memory (Store) | ⭐⭐⭐ Advanced | Persistent storage across sessions |

---

## 📚 Detailed Examples

### 1️⃣ Basic Tool Definition
**File:** `01_tools_with_model.py`

**What it teaches:**
- Creating tools with `@tool` decorator
- Function docstrings as tool descriptions
- Type hints for automatic schema generation
- Binding tools to a model
- Extracting tool calls from model responses

**Key Concepts:**
```python
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.
    
    Args:
        query: Search terms to look for
        limit: Maximum number of results to return (default: 10)
    """
    return f"Found {limit} results for '{query}'"

# Bind to model
model_with_tools = model.bind_tools([search_database])

# Model can now call the tool
response = model_with_tools.invoke("Search for customers named John")
```

**Message Types Involved:**
- `HumanMessage`: User query
- `AIMessage`: Model response with tool calls
- `ToolMessage`: Tool execution result (handled internally)

---

### 2️⃣ Pydantic Schema Validation
**File:** `02_tools_with_schema_pydantic.py`

**What it teaches:**
- Complex input validation using Pydantic `BaseModel`
- `Field()` with descriptions for better model guidance
- Literal types for constrained choices
- Custom tool descriptions
- Type checking before tool execution

**Key Concepts:**
```python
from pydantic import BaseModel, Field
from typing import Literal

class WeatherInput(BaseModel):
    """Input for weather queries."""
    location: str = Field(description="City name or coordinates")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference"
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast."""
    # Implementation...
    return result
```

**Advantages:**
- ✅ Automatic input validation
- ✅ Better model understanding via field descriptions
- ✅ Type safety
- ✅ Clear API contract

---

### 3️⃣ JSON Schema Validation
**File:** `03_tools_with_schema_json.py`

**What it teaches:**
- Using raw JSON Schema instead of Pydantic
- When to prefer JSON over Pydantic
- Schema structure and requirements
- JSON schema validation

**Key Concepts:**
```python
weather_schema = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "units": {"type": "string"},
        "include_forecast": {"type": "boolean"}
    },
    "required": ["location", "units", "include_forecast"]
}

@tool(args_schema=weather_schema)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast."""
    # Implementation...
    return result
```

**Use Cases:**
- 📌 Dynamic schema generation
- 📌 Non-Python systems integration
- 📌 Complex schema transformations
- 📌 When Pydantic feels overkill

---

### 4️⃣ State Access via ToolRuntime
**File:** `04_tools_stateaccess_toolruntiem.py`

**What it teaches:**
- Accessing conversation state from tools
- Reading message history
- Accessing custom state fields
- Updating state via `Command`
- LangGraph state management
- ToolNode for state injection

**Key Concepts:**
```python
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

@tool
def get_user_preference(pref_name: str, runtime: ToolRuntime) -> str:
    """Get a user preference value."""
    # Access state (read-only)
    preferences = runtime.state.get("user_preferences", {})
    return preferences.get(pref_name, "Not set")

@tool
def set_user_preference(pref_name: str, pref_value: str, runtime: ToolRuntime) -> Command:
    """Set a user preference value."""
    preferences = runtime.state.get("user_preferences", {})
    preferences[pref_name] = pref_value
    
    # Update state via Command
    return Command(
        update={
            "user_preferences": preferences,
            "messages": [
                ToolMessage(
                    content=f"Preference '{pref_name}' set to '{pref_value}'.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
```

**State Access Available:**
- `runtime.state["messages"]` - Conversation history
- `runtime.state.get("custom_field")` - Custom state fields
- `runtime.state` - Full state dict

**Important:** The `runtime` parameter is automatically injected by **ToolNode** and is **hidden from the LLM**.

**Architecture:**
```
StateGraph
├── LLM Node (decides which tools to call)
├── ToolNode (executes tools with runtime injection)
└── Conditional Edges (route based on tool calls)
```

---

### 5️⃣ Context-Aware Tools
**File:** `05_tools_access_context.py`

**What it teaches:**
- Accessing immutable context data
- User identity and session information
- Context injection via `create_agent`
- Dataclass-based context schemas
- Personalized tool behavior

**Key Concepts:**
```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime

@dataclass
class UserContext:
    user_id: str

# Database lookup
USER_DATABASE = {
    "user123": {"name": "Alice", "balance": 5000},
    "user456": {"name": "Bob", "balance": 1200}
}

@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """Get the current user's account information."""
    user_id = runtime.context.user_id  # Access context
    user = USER_DATABASE.get(user_id)
    return f"Account: {user['name']}, Balance: ${user['balance']}"

# Pass context at invocation
agent = create_agent(
    model,
    tools=[get_account_info],
    context_schema=UserContext,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's my balance?"}]},
    context=UserContext(user_id="user123")
)
```

**Key Differences from State:**
| Feature | State | Context |
|---------|-------|---------|
| **Scope** | Per-conversation (mutable) | Across calls (immutable) |
| **Use** | Track conversation history | User/session info |
| **Updates** | Can be modified | Read-only |
| **Examples** | Messages, preferences | User IDs, permissions |

---

### 6️⃣ Long-Term Memory (Store)
**File:** `06_tools_access_longterm_memory.py`

**What it teaches:**
- Persistent storage across sessions
- Store API: namespace/key pattern
- Reading and writing to store
- InMemoryStore for development
- Long-term data management

**Key Concepts:**
```python
from langgraph.store.memory import InMemoryStore

@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """Look up user info from persistent storage."""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "Unknown user"

@tool
def save_user_info(user_id: str, user_info: dict, runtime: ToolRuntime) -> str:
    """Save user info to persistent storage."""
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "User saved successfully"

# Create agent with store
store = InMemoryStore()
agent = create_agent(
    model,
    tools=[get_user_info, save_user_info],
    store=store
)

# Session 1: Save data
agent.invoke({
    "messages": [{"role": "user", "content": "Save: user_id: abc123, name: Alice, age: 30"}]
})

# Session 2: Retrieve data (persisted from Session 1)
agent.invoke({
    "messages": [{"role": "user", "content": "Get user info for abc123"}]
})
```

**Store Structure:**
```python
# Namespace/Key pattern
store.put(("namespace", "sub_namespace"), key_id, value)
store.get(("namespace", "sub_namespace"), key_id)

# Examples
store.put(("users",), "user123", user_dict)
store.put(("conversations", "user123"), "conv_001", messages)
store.put(("settings", "user123", "preferences"), "theme", "dark")
```

**Store Implementations:**
- **InMemoryStore** - Development/testing (loses data on restart)
- **PostgresStore** - Production (persistent across service restarts)
- Custom implementations via `BaseStore`

**Best Practice:**
```python
# Production: Use PostgresStore
from langgraph.store.postgres import PostgresStore

store = PostgresStore(
    connection_string="postgresql://user:password@localhost/langchain"
)
```

---

## 🔧 Tool Runtime (ToolRuntime)

The `ToolRuntime` parameter provides access to execution context:

```python
@tool
def example_tool(runtime: ToolRuntime) -> str:
    """Example showing all runtime capabilities."""
    
    # Short-term memory (conversation state)
    messages = runtime.state["messages"]
    custom_data = runtime.state.get("custom_field")
    
    # Immutable context (user/session info)
    user_id = runtime.context.user_id
    
    # Long-term memory (persistent storage)
    store = runtime.store
    data = store.get(("namespace",), key_id)
    
    # Stream real-time updates
    runtime.stream_writer("Processing...")
    
    # Execution metadata
    execution_info = runtime.execution_info
    print(f"Thread: {execution_info.thread_id}")
    
    return "Done"
```

**Reserved Parameter Names:**
- ⚠️ `config` - Reserved for RunnableConfig
- ⚠️ `runtime` - Reserved for ToolRuntime
- ✅ Use these names only for their intended purposes

---

## 📝 Message Types

LangChain uses typed messages for conversational AI:

### Core Message Types
```python
from langchain_core.messages import (
    HumanMessage,      # User input
    AIMessage,         # LLM response
    SystemMessage,     # System instructions
    ToolMessage,       # Tool execution result
)

# Example conversation
messages = [
    SystemMessage("You are a helpful assistant."),
    HumanMessage("What's the weather?"),
    AIMessage(
        content="",
        tool_calls=[{"name": "get_weather", "args": {"city": "Paris"}}]
    ),
    ToolMessage(
        content="Sunny, 22°C",
        tool_call_id="<call_id>",
        name="get_weather"
    ),
    AIMessage("The weather in Paris is sunny and 22 degrees."),
]
```

### Message Flow in Tool Calling
1. **HumanMessage** → User asks question
2. **AIMessage with tool_calls** → Model decides to use tool
3. **ToolMessage** → Tool result returned
4. **AIMessage** → Model provides final response

---

## 🚀 Running Examples

### Basic Example (01)
```bash
cd tools
python 01_tools_with_model.py
```

### State Access Example (04)
```bash
python 04_tools_stateaccess_toolruntiem.py
```

### Long-Term Memory Example (06)
```bash
python 06_tools_access_longterm_memory.py
```

---

## 💡 Common Patterns

### Pattern 1: Tool with Validation
```python
from pydantic import BaseModel, Field, validator

class QueryInput(BaseModel):
    query: str = Field(min_length=1, max_length=100)
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v

@tool(args_schema=QueryInput)
def search(query: str) -> str:
    return f"Results for: {query}"
```

### Pattern 2: Tool with Error Handling
```python
@tool
def fetch_data(url: str) -> str:
    """Safely fetch data from URL."""
    try:
        # Implementation
        return data
    except Exception as e:
        return f"Error: {str(e)}"
```

### Pattern 3: State-Modifying Tool
```python
@tool
def update_preference(key: str, value: str, runtime: ToolRuntime) -> Command:
    """Update user preference in state."""
    prefs = runtime.state.get("preferences", {})
    prefs[key] = value
    
    return Command(
        update={
            "preferences": prefs,
            "messages": [
                ToolMessage(
                    content=f"Preference '{key}' updated.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
```

---

## ❓ FAQ

**Q: When should I use Pydantic vs JSON schema?**
A: Use Pydantic for Python-first projects (validation, IDE support). Use JSON for flexibility or non-Python integration.

**Q: How do I update state from a tool?**
A: Use `Command` return type with `update` dict. Must be executed via `ToolNode`.

**Q: Can tools access each other's results?**
A: No directly, but through state if you use `Command` to store results.

**Q: What's the difference between state and context?**
A: **State** is mutable, per-conversation (messages, preferences). **Context** is immutable, per-invocation (user ID, session ID).

**Q: How do I persist data across sessions?**
A: Use `runtime.store` with `PostgresStore` in production.

---

## 🔗 Related Documentation

- [LangChain Tools Documentation](https://docs.langchain.com/oss/python/langchain/tools)
- [LangGraph State Management](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Message Types](https://docs.langchain.com/oss/python/langchain/messages)
- [Tool Calling Guide](https://docs.langchain.com/oss/python/langchain/models#tool-calling)

---

## 📊 Learning Path

```
Start Here
    ↓
01: Basic @tool decorator
    ↓
02: Pydantic schemas
    ↓
03: JSON schemas
    ↓
(Choose based on needs)
    ├→ 04: State management
    ├→ 05: User context
    └→ 06: Long-term memory
```

---

## 🤝 Contributing

To add new examples or improve documentation:

1. Follow existing code style and docstring format
2. Add comprehensive inline comments
3. Update this README with new patterns
4. Test with `ollama:qwen3.5:latest` and `ollama:gemma4:latest`

---

**Last Updated:** May 2026  
**LangChain Version:** Latest  
**Ollama Models Tested:** qwen3.5, gemma4, deepseek-r1
