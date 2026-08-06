"""
LangChain Agent Example: Dynamic Model Selection

This example demonstrates:
- Middleware pattern for intercepting agent requests
- Dynamic model selection based on conversation state
- Choosing between simple and advanced models based on context

Dynamic model selection enables cost optimization and performance tuning
by using appropriate models based on task complexity.
"""
from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse


# Tool definitions
def get_weather(city: str) -> str:
    """Get the current weather for a given city.
    
    Args:
        city: The city name to get weather for
    
    Returns:
        A string describing the weather conditions
    """
    # This is a placeholder function. In a real implementation, this would call a weather API.
    return f"The current weather in {city} is always sunny at 72°F."


def search(query: str) -> str:  
    """Search the web for a given query.
    
    Args:
        query: The search query
    
    Returns:
        Search results as a string
    """
    # This is a placeholder function. In a real implementation, this would call a search API.
    return f"Search results for {query}: ..."


# Initialize models with different sizes/capabilities
# simplemodel: Lightweight, faster, lower cost - for basic queries
# advancedmodel: More powerful, better reasoning - for complex queries
simplemodel = ChatOllama(model="qwen3.5:latest")
advancedmodel = ChatOllama(model="gemma4:latest")


# Middleware function decorated with @wrap_model_call
# This allows us to intercept and modify model requests before they're processed
@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Select an appropriate model based on conversation complexity.
    
    Strategy:
    - First message: Use simple model for quick response
    - Subsequent messages: Use advanced model for better reasoning
    
    Args:
        request: The model request containing state and tools
        handler: The next handler in the middleware chain
    
    Returns:
        The response after processing with the selected model
    """
    # Analyze conversation complexity
    message_count = len(request.state["messages"])
    
    # Select model based on conversation state
    if message_count < 1:
        # First message - use simple model for efficiency
        model = simplemodel
    else:
        # Subsequent messages - may need more reasoning, use advanced model
        model = advancedmodel
    
    # Modify the request to use the selected model and continue processing
    return handler(request.override(model=model))

# Create agent with middleware for dynamic model selection
agent = create_agent(
    model=simplemodel,  # Default/fallback model
    tools=[get_weather, search],  # Available tools
    system_prompt="you are a helpful assistant that provides weather information and can search the web.",
    middleware=[dynamic_model_selection]  # Apply middleware to intercept requests
)

# Invoke the agent with multiple messages
# Watch how the middleware selects different models based on message count
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

