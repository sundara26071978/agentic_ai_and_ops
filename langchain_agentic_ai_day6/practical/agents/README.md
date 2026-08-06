# LangChain Agents Examples

LangChain provides a production-ready agent architecture and model integrations to help you build intelligent systems that reason about tasks, decide which tools to use, and iteratively work towards solutions.

## Overview

Agents combine language models with tools to create autonomous systems. An LLM agent runs tools in a loop to achieve a goal, continuing until a stop condition is met (when the model emits a final output or an iteration limit is reached).

### Agent Architecture Flow

```
Input → Model (Decision) → Tools (Action) → Observation → Model → ... → Output
```

The agent:
1. Takes input from the user
2. Uses the model to reason and decide which tool(s) to use
3. Executes the selected tool(s)
4. Observes the results
5. Repeats until completion

## Core Concepts

### 1. Models (Reasoning Engine)
The model is the reasoning engine of your agent. It can be configured as:

#### Static Model
A fixed model configured once at agent creation:
```python
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

model = ChatOllama(model="qwen3.5:latest")
agent = create_agent(model=model, tools=tools)
```

#### Dynamic Model
Models selected at runtime based on context or state, enabling sophisticated routing:
```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler):
    # Choose model based on conversation complexity
    if len(request.state["messages"]) > 10:
        model = advanced_model
    else:
        model = basic_model
    return handler(request.override(model=model))

agent = create_agent(model=model, tools=tools, middleware=[dynamic_model_selection])
```

### 2. Tools (Actions)
Tools give agents the ability to take actions and interact with external systems:

#### Static Tools
Tools defined at agent creation time (most common):
```python
from langchain.tools import tool
from langchain.agents import create_agent

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

agent = create_agent(model=model, tools=[search, get_weather])
```

#### Dynamic Tool Filtering
Pre-register all tools and dynamically filter which ones are exposed based on state, permissions, or context:

**State-based filtering:**
```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def state_based_tools(request: ModelRequest, handler):
    """Filter tools based on conversation state."""
    is_authenticated = request.state.get("authenticated", False)
    
    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)
    
    return handler(request)
```

**Store-based filtering (User preferences/Feature flags):**
```python
@wrap_model_call
def store_based_tools(request: ModelRequest, handler):
    """Filter tools based on user preferences in Store."""
    user_id = request.runtime.context.user_id
    store = request.runtime.store
    feature_flags = store.get(("features",), user_id)
    
    if feature_flags:
        enabled_features = feature_flags.value.get("enabled_tools", [])
        tools = [t for t in request.tools if t.name in enabled_features]
        request = request.override(tools=tools)
    
    return handler(request)
```

**Runtime context-based filtering (Permissions):**
```python
@wrap_model_call
def context_based_tools(request: ModelRequest, handler):
    """Filter tools based on user role."""
    user_role = request.runtime.context.user_role if request.runtime else "viewer"
    
    if user_role == "admin":
        pass  # All tools available
    elif user_role == "editor":
        tools = [t for t in request.tools if t.name != "delete_data"]
        request = request.override(tools=tools)
    else:  # viewer
        tools = [t for t in request.tools if t.name.startswith("read_")]
        request = request.override(tools=tools)
    
    return handler(request)
```

### 3. Middleware
Middleware enables customization of agent behavior by intercepting and modifying requests:

- **Dynamic model selection** based on context
- **Tool filtering** based on permissions, state, or features
- **System prompt customization** based on user context
- **Tool error handling and retry logic**
- **Custom request/response processing**

## Examples in This Repository

### Basic Examples
- **basicagent.py** - Simple agent with a single tool using Ollama
- **agent_streaming.py** - Streaming agent responses in real-time

### Model Patterns
- **agent_model_ollama.py** - Using Ollama models
- **agent_dynamicmodels.py** - Dynamic model selection at runtime

### Tool Management
- **agent_dynamic_filtering_tools_by_state.py** - Filter tools based on conversation state
- **agent_dynamic_filtering_tools_by_store_feature.py** - Filter tools based on Store feature flags
- **agent_dynamic_filtering_tools_by_runtime_context.py** - Filter tools based on user permissions

### Advanced Patterns
- **agent_streaming.py** - Real-time streaming of agent responses
- **agent_structured_output_tool_strategy.py** - Tools returning structured output
- **agent_structured_output_provider_strategy.py** - Provider-based structured output
- **agent_tool_error_handling.py** - Error handling and retry logic
- **agent_runtime_tool_registration.py** - Runtime tool registration
- **agent_memory_custom_state_Schema.py** - Custom state management

### System Prompt Customization
- **agent_dynamic_system_prompt_by_user_context.py** - Customize system prompt based on user context

## Key Features

### Multiple Tool Calls
Agents can trigger multiple tool calls in sequence based on a single prompt, enabling complex workflows.

### Parallel Tool Calls
When appropriate, agents can execute multiple tools in parallel for efficiency.

### Tool Retry Logic
Built-in error handling and retry mechanisms for failed tool calls.

### State Persistence
Maintain state across tool calls and agent iterations.

### Feature Flags & Permissions
Control tool availability through Store-based feature flags and user roles.

## Getting Started

1. Install dependencies:
```bash
uv add langchain langchain-ollama langgraph
```

2. Run a basic example:
```bash
uv run basicagent.py
```

3. Explore different patterns:
```bash
uv run agent_streaming.py
uv run agent_dynamicmodels.py
uv run agent_dynamic_filtering_tools_by_state.py
```

## Documentation References

- [LangChain Agents Documentation](https://docs.langchain.com/oss/python/langchain/agents)
- [LangGraph (Graph-based Agent Runtime)](https://docs.langchain.com/oss/python/langgraph)
- [Tools Documentation](https://docs.langchain.com/oss/python/langchain/tools)
- [Models Documentation](https://docs.langchain.com/oss/python/langchain/models)
