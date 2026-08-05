"""
03_tools_with_schema_json.py - JSON Schema Validation

This example demonstrates:
✅ Using raw JSON Schema instead of Pydantic
✅ When to prefer JSON over Pydantic
✅ Schema structure and requirements
✅ JSON schema validation
✅ Tool creation with external schema definitions

When to Use JSON vs Pydantic?
- JSON: Dynamic schemas, non-Python systems, simple validation
- Pydantic: Type safety, validation, IDE support, Python-first

Prerequisites:
- Ollama running locally (ollama serve)
- ollama pull gemma4:latest

JSON Schema Structure:
{
    "type": "object",
    "properties": {
        "param_name": {"type": "string", "description": "..."},
        "another_param": {"type": "boolean"}
    },
    "required": ["param_name"]
}

Reference: https://docs.langchain.com/oss/python/langchain/tools#advanced-schema-definition
"""

from langchain.tools import tool
import pprint
from langchain.chat_models import init_chat_model


# ============================================================================
# Define Tool Schema Using JSON Schema
# ============================================================================

weather_schema = {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "City name or coordinates (e.g., 'Paris', '48.8566°N, 2.3522°E')"
        },
        "units": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Temperature unit preference - must be either 'celsius' or 'fahrenheit'"
        },
        "include_forecast": {
            "type": "boolean",
            "description": "Include 5-day forecast in the response"
        }
    },
    "required": ["location", "units", "include_forecast"]
}


# ============================================================================
# Define Tool with JSON Schema
# ============================================================================

@tool(args_schema=weather_schema)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """Get current weather and optional forecast.
    
    Args:
        location: City name or coordinates to get weather for
        units: Temperature unit (celsius or fahrenheit)
        include_forecast: Whether to include 5-day forecast
    
    Returns:
        String describing current weather and optionally forecast
    
    Note: The schema is defined via JSON above, not Pydantic.
    This is useful when you need dynamic schema generation or
    integration with non-Python systems.
    """
    # Simulate weather lookup
    temp = 22 if units == "celsius" else 72
    unit_symbol = "°C" if units == "celsius" else "°F"
    
    result = f"Current weather in {location}: {temp}{unit_symbol}"
    
    if include_forecast:
        result += "\nNext 5 days: Sunny, Cloudy, Sunny, Rainy, Sunny"
    
    return result


# ============================================================================
# Initialize Model and Bind Tools
# ============================================================================

print("=" * 70)
print("EXAMPLE: JSON Schema Validation for Tools")
print("=" * 70)

# Initialize the model with Ollama backend
model = init_chat_model("ollama:gemma4:latest")

# Bind tools with JSON schema validation to the model
model_with_tools = model.bind_tools([get_weather])

print("\n📋 Tool Schema (JSON):")
print(f"  Type: {weather_schema['type']}")
print(f"  Properties: {list(weather_schema['properties'].keys())}")
print(f"  Required: {weather_schema['required']}")


# ============================================================================
# Invoke Model with JSON Schema-Based Tool
# ============================================================================

# Example 1: Simple weather query
print("\n" + "=" * 70)
print("Query 1: Get weather for Paris (Celsius)")
print("=" * 70)

response1 = model_with_tools.invoke("What's the weather like in Paris in celsius?")
print(f"\n📝 Model Response: {response1.content}")

if response1.tool_calls:
    print("\n🔧 Tool Calls Made:")
    for tool_call in response1.tool_calls:
        print(f"  📞 Tool: {tool_call['name']}")
        print(f"     Arguments:")
        for key, value in tool_call['args'].items():
            print(f"       - {key}: {value}")


# Example 2: Complex query with forecast
print("\n" + "=" * 70)
print("Query 2: Get weather for London with forecast (Fahrenheit)")
print("=" * 70)

response2 = model_with_tools.invoke(
    "What's the weather like in London in celsius with a 5-day forecast?"
)
print(f"\n📝 Model Response: {response2.content}")

if response2.tool_calls:
    print("\n🔧 Tool Calls Made:")
    for tool_call in response2.tool_calls:
        print(f"  📞 Tool: {tool_call['name']}")
        print(f"     Arguments:")
        for key, value in tool_call['args'].items():
            print(f"       - {key}: {value}")


# ============================================================================
# Comparison: JSON vs Pydantic
# ============================================================================

print("\n" + "=" * 70)
print("JSON vs Pydantic Comparison")
print("=" * 70)
print("""
┌─────────────────┬────────────────────────┬────────────────────────┐
│    Feature      │        JSON            │      Pydantic          │
├─────────────────┼────────────────────────┼────────────────────────┤
│ Definition      │ Raw dict/JSON string   │ Python class           │
│ Type Checking   │ Manual                 │ Automatic              │
│ IDE Support     │ Limited                │ Excellent              │
│ Validation      │ Basic                  │ Advanced               │
│ Dynamic Schema  │ ✅ Easy                │ ❌ Complex             │
│ Non-Python Use  │ ✅ Good for APIs       │ ❌ Python-only         │
│ Complexity      │ ⭐ Simple              │ ⭐⭐ More code         │
└─────────────────┴────────────────────────┴────────────────────────┘
""")




