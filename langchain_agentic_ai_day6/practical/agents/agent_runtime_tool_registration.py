"""
LangChain Agent Example: Runtime Tool Registration

This example demonstrates:
- Dynamically registering tools at runtime
- Custom middleware for tool management
- Loading tools from external sources (databases, MCP servers, etc.)
- Adding capabilities without agent recreation

Runtime tool registration enables flexible agent architectures where
capabilities can be extended dynamically based on context or requirements.
"""
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ToolCallRequest
from langchain_ollama import ChatOllama

# A tool that will be added dynamically at runtime
@tool
def calculate_tip(bill_amount: float, tip_percentage: float = 20.0) -> str:
    """Calculate the tip amount for a bill.
    
    This tool is not registered at agent creation time,
    but added dynamically by middleware.
    
    Args:
        bill_amount: The bill total in dollars
        tip_percentage: The tip percentage (default 20%)
    
    Returns:
        A string with tip and total amounts
    """
    tip = bill_amount * (tip_percentage / 100)
    return f"Tip: ${tip:.2f}, Total: ${bill_amount + tip:.2f}"


def get_weather(city: str) -> str:
    """Get the current weather for a given city.
    
    This is a static tool registered at agent creation.
    
    Args:
        city: The city name
    
    Returns:
        Weather information
    """
    # This is a placeholder function. In a real implementation, this would call a weather API.
    return f"The current weather in {city} is always sunny"


class DynamicToolMiddleware(AgentMiddleware):
    """Middleware that registers and handles dynamic tools.
    
    This middleware demonstrates:
    - Adding tools during model request processing (wrap_model_call)
    - Routing tool calls to dynamically registered tools (wrap_tool_call)
    
    Tools can be loaded from:
    - MCP (Model Context Protocol) servers
    - Databases or APIs
    - Configuration files or runtime state
    """

    def wrap_model_call(self, request: ModelRequest, handler):
        """Add dynamic tools to the agent request.
        
        This method intercepts the model call and injects additional tools
        that weren't registered at agent creation time.
        
        Args:
            request: The model request with current tools
            handler: The next handler in the middleware chain
        
        Returns:
            The response after injecting dynamic tools
        """
        # Add dynamic tool to the request
        # In production, this could fetch tools from external sources
        updated = request.override(tools=[*request.tools, calculate_tip])
        return handler(updated)

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        """Handle execution of dynamically registered tools.
        
        This method routes tool calls to the appropriate implementation,
        including dynamically registered tools.
        
        Args:
            request: The tool call request
            handler: The next handler in the middleware chain
        
        Returns:
            The tool execution result
        """
        # Route tool calls to the appropriate handler
        if request.tool_call["name"] == "calculate_tip":
            return handler(request.override(tool=calculate_tip))
        return handler(request)
    

# Initialize the model
model = ChatOllama(model="qwen3.5:latest")

# Create agent with dynamic tool middleware
agent = create_agent(
    model=model,
    tools=[get_weather],  # Only static tools registered here
    middleware=[DynamicToolMiddleware()],  # Middleware adds dynamic tools
)

# The agent can now use both get_weather AND calculate_tip
# Even though calculate_tip wasn't in the initial tools list
result = agent.invoke({
    "messages": [{"role": "user", "content": "Calculate a 20% tip on $85"}]
})
print(result)
