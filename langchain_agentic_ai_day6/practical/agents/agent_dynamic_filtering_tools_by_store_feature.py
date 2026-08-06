from dataclasses import dataclass
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.agents.middleware import wrap_model_call, ModelRequest,ModelResponse
from typing import Callable
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

def public_get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    # This is a placeholder function. In a real implementation, this would call a weather API.
    return f"The current weather in {city} is always sunnyat 72°F."

def public_search(query: str) -> str:  
    """Search the web for a given query."""
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Private Search results for {query}: ..."

def private_search(query: str) -> str:  
    """Search the web for a given query."""
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Private Search results for {query}: ..."

def advanced_search(query: str) -> str:  
    """Search the web for a given query."""
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Advanced Search results for {query}: ..."

model = ChatOllama(model="qwen3.5:latest")

@wrap_model_call
def store_based_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Filter tools based on Store preferences."""
    user_id = request.runtime.context.user_id

    # Read from Store: get user's enabled features
    store = request.runtime.store
    feature_flags = store.get(("features",), user_id)

    if feature_flags:
        enabled_features = feature_flags.value.get("enabled_tools", [])
        # Only include tools that are enabled for this user
        tools = [t for t in request.tools if t.name in enabled_features]
        request = request.override(tools=tools)

    return handler(request)



# InMemoryStore saves data to an in-memory dictionary. Use a DB-backed store in production.
store = InMemoryStore()

# Write sample data to the store using the put method
store.put(
    (
        "features",
    ),  # Namespace to group related data together (users namespace for user data)
    "user_123",  # Key within the namespace (user ID as key)
    {
        "user_id" : "user_123",
        "name": "Sundara",
        "enabled_tools": ["public_get_weather", "private_search"],
    },  # Data to store for the given user
)



agent= create_agent(
    model=model, 
    tools=[public_get_weather, public_search, private_search, advanced_search],
    system_prompt="you are a helpful assistant that provides weather information and can search the web.",
    middleware=[store_based_tools],
    store=store,  # Pass the store to the agent's runtime
    context_schema=Context  
    # runtime_context=Context(user_id="user_123")  # Set the user ID in the runtime context
)

context=Context(user_id="user_123")
# result = agent.invoke({"messages": [{"role": "user", "content": "What is the weather in Chennai?"}]})

result = agent.invoke({"messages": [{"role": "user", "content": "can you search for the latest news on AI on agent security and a related project glasswing by anthropic"},
                                    {"role": "user", "content": "What is the weather in Chennai?"}]},
                    context=context                
                    )

print(result)

