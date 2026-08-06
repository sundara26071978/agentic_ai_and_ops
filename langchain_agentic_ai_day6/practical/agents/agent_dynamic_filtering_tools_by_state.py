"""
LangChain Agent Example: Dynamic Tool Filtering Based on State

This example demonstrates:
- Pre-registering all tools at agent creation
- Filtering available tools based on conversation state
- Using middleware to control tool access dynamically
- Progressive tool unlocking based on conversation milestones

Tool filtering enables progressive disclosure of capabilities and
enforces security policies during conversations.
"""
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable


# Tool definitions
def public_get_weather(city: str) -> str:
    """Get the current weather for a given city.
    
    A public tool available to all users.
    """
    # This is a placeholder function. In a real implementation, this would call a weather API.
    return f"The current weather in {city} is always sunny at 72°F."


def public_search(query: str) -> str:  
    """Search the web for a given query.
    
    A public search tool available to all users.
    """
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Public Search results for {query}: ..."


def private_search(query: str) -> str:  
    """Search the web for a given query.
    
    A private search tool requiring higher permissions.
    """
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Private Search results for {query}: ..."


def advanced_search(query: str) -> str:  
    """Search the web for a given query.
    
    An advanced search tool requiring authentication and conversation history.
    """
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Advanced Search results for {query}: ..."


# Initialize models
simplemodel = ChatOllama(model="qwen3.5:latest")
advancedmodel = ChatOllama(model="gemma4:latest")

# Middleware for dynamic model selection
@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Select model based on conversation length.
    
    Args:
        request: The model request with current state
        handler: The next handler in the middleware chain
    
    Returns:
        The response after processing with the selected model
    """
    message_count = len(request.state["messages"])
    if message_count < 1:
        model = simplemodel
    else:
        model = advancedmodel
    return handler(request.override(model=model))


# Middleware for filtering tools based on conversation state
@wrap_model_call
def state_based_tools(request: ModelRequest, handler: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    """Filter tools based on conversation State and authentication.
    
    Security Policy:
    - Unauthenticated users: Only public tools
    - Authenticated, early conversation: Public + private tools, exclude advanced
    - Authenticated, later in conversation: All tools available
    
    Args:
        request: The model request containing state and tools
        handler: The next handler in the middleware chain
    
    Returns:
        The response after processing with filtered tools
    """
    # Read from State: check if user has authenticated
    state = request.state
    is_authenticated = state.get("authenticated", False)
    message_count = len(state["messages"])

    # Apply tool filtering rules
    if not is_authenticated:
        # Unauthenticated users only get public tools
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)
    elif message_count < 3:
        # Limit advanced tools early in conversation
        # This prevents accidental misuse before the user proves intent
        tools = [t for t in request.tools if t.name != "advanced_search"]
        request = request.override(tools=tools)
    # If authenticated and past message threshold, all tools are available

    return handler(request)


# Create agent with multiple middleware
# Middleware are applied in order to the agent request
agent = create_agent(
    model=simplemodel, 
    tools=[public_get_weather, public_search, private_search, advanced_search],
    system_prompt="you are a helpful assistant that provides weather information and can search the web.",
    middleware=[state_based_tools, dynamic_model_selection]  # Apply middleware in order
)

# Invoke the agent with multiple user messages
# The state_based_tools middleware will filter available tools based on authentication status
result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "can you search for the latest news on AI on agent security and a related project glasswing by anthropic"
        },
        {
            "role": "user",
            "content": "What is the weather in Chennai?"
        }
    ]
})

print(result)

