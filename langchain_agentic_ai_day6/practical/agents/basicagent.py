"""
LangChain Agent Example: Basic Agent with Single Tool

This example demonstrates:
- Creating a simple agent with a single tool
- Using Ollama as the LLM model
- OpenTelemetry tracing for observability

An agent is an autonomous system that uses an LLM to reason about tasks,
decide which tools to use, and iteratively work towards solutions.
"""
from langchain.agents import create_agent
from phoenix.otel import register

# Initialize OpenTelemetry tracing for observability
# This helps monitor agent performance and debug issues
tracer_provider = register(
  project_name="default",
)

tracer = tracer_provider.get_tracer(__name__)

# Define a tool that the agent can use
# Tools are functions that extend the agent's capabilities
@tracer.chain
def get_weather(city: str) -> str:
    """Get the current weather for a given city.
    
    Args:
        city: The city name to get weather for
    
    Returns:
        A string describing the weather conditions
    """
    # This is a placeholder function. In a real implementation, this would call a weather API.
    return f"The current weather in {city} is sunny with a temperature of 25°C."



# Create an agent using create_agent
# Arguments:
#   model: Model identifier string ("ollama:gemma4:latest" - auto-infers Ollama provider)
#   tools: List of tools available to the agent
#   system_prompt: Instructions for how the agent should behave
agent = create_agent(
    model="ollama:gemma4:latest",
    tools=[get_weather],
    system_prompt="you are a helpful assistant that provides weather information."
)

# Invoke the agent with a user query
# The agent will:
# 1. Reason about the task
# 2. Decide to call the get_weather tool
# 3. Execute the tool and observe the result
# 4. Provide a final response to the user
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "What is the weather in New York?"
    }]
})

# Print the agent's response
print(result)



