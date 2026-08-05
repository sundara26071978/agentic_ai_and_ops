"""
02_tools_with_schema_pydantic.py - Pydantic Schema Validation

This example demonstrates:
✅ Complex input validation using Pydantic BaseModel
✅ Field descriptions for better model guidance
✅ Literal types for constrained choices
✅ Custom tool descriptions
✅ Automatic type checking before tool execution
✅ Schema-based input validation

Why Pydantic?
- Provides automatic validation of tool arguments
- Field descriptions help the model understand parameter meaning
- Type hints enable IDE support and error catching
- More readable than raw JSON schemas

Prerequisites:
- Ollama running locally (ollama serve)
- ollama pull gemma4:latest

Message Flow:
1. HumanMessage: User asks for weather
2. AIMessage: Model decides to call get_weather with validated args
3. ToolMessage: Tool result (Pydantic validated the arguments)
4. AIMessage: Model provides final response

Reference: https://docs.langchain.com/oss/python/langchain/tools#advanced-schema-definition
"""

from langchain.tools import tool
import pprint
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Literal


# ============================================================================
# Define Tool Schema Using Pydantic
# ============================================================================

class WeatherInput(BaseModel):
    """Input schema for weather queries.
    
    This Pydantic model defines the structure and validation rules for the
    get_weather tool. The model will use these descriptions to decide what
    values to pass.
    """
    location: str = Field(
        description="City name or coordinates (e.g., 'Paris', '48.8566°N, 2.3522°E')"
    )
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="Temperature unit preference - must be either 'celsius' or 'fahrenheit'"
    )
    include_forecast: bool = Field(
        default=False,
        description="Include 5-day forecast in the response"
    )


# ============================================================================
# Define Tool with Schema Validation
# ============================================================================

@tool(
    args_schema=WeatherInput,
    description="Get current weather and optional forecast for a location."
)
def get_weather(
    location: str,
    units: str = "celsius",
    include_forecast: bool = False
) -> str:
    """Get current weather and optional forecast.
    
    Args:
        location: City name or coordinates to get weather for
        units: Temperature unit (celsius or fahrenheit)
        include_forecast: Whether to include 5-day forecast
    
    Returns:
        String describing current weather and optionally forecast
    """
    # Simulate weather lookup
    temp = 22 if units == "celsius" else 72
    unit_symbol = "°C" if units == "celsius" else "°F"
    
    result = f"Current weather in {location}: {temp}{unit_symbol}"
    
    if include_forecast:
        result += "\nNext 5 days: Sunny, Cloudy, Sunny, Rainy, Sunny"
    
    return result


# ============================================================================
# Initialize Model and Bind Tools with Schema
# ============================================================================

print("=" * 70)
print("EXAMPLE: Pydantic Schema Validation for Tools")
print("=" * 70)

# Initialize the model with Ollama backend
model = init_chat_model("ollama:gemma4:latest")

# Bind tools with Pydantic validation to the model
# The model will receive the schema information and validate before calling
model_with_tools = model.bind_tools([get_weather])

print("\n📋 Tool Schema (what the model sees):")
print(f"  Description: {get_weather.description}")
print(f"  Args Schema: {get_weather.args_schema}")


# ============================================================================
# Invoke Model with Schema-Based Tool
# ============================================================================

# Example 1: Simple weather query
print("\n" + "=" * 70)
print("Query 1: Get weather for Paris (Celsius)")
print("=" * 70)

response1 = model_with_tools.invoke("What's the weather like in Paris?")
print(f"\n📝 Model Response: {response1.content}")

if response1.tool_calls:
    print("\n🔧 Tool Calls Made:")
    for tool_call in response1.tool_calls:
        print(f"  📞 Tool: {tool_call['name']}")
        print(f"     Args: {tool_call['args']}")


# Example 2: Complex query with forecast
print("\n" + "=" * 70)
print("Query 2: Get weather for London with forecast (Fahrenheit)")
print("=" * 70)

response2 = model_with_tools.invoke(
    "What's the weather like in London in fahrenheit with a 5-day forecast?"
)
print(f"\n📝 Model Response: {response2.content}")

if response2.tool_calls:
    print("\n🔧 Tool Calls Made:")
    for tool_call in response2.tool_calls:
        print(f"  📞 Tool: {tool_call['name']}")
        print(f"     Args: {tool_call['args']}")


# ============================================================================
# Display Tool Metadata
# ============================================================================

print("\n" + "=" * 70)
print("Tool Metadata")
print("=" * 70)
print(f"Tool Name: {get_weather.name}")
print(f"Tool Description: {get_weather.description}")
print(f"Tool Args Schema: {get_weather.args_schema}")




