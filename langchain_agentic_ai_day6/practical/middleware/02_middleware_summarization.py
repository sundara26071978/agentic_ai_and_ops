from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

from langchain.tools import tool
from rich import print as rprint
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Literal

import os

from dotenv import load_dotenv

load_dotenv()


model_basic = init_chat_model("nvidia/nemotron-3-ultra-550b-a55b:free",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=1000, temperature=0.0)

model_medium = init_chat_model("openai/gpt-5.6-luna",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)

model_advanced = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)

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


agent = create_agent(
    model=model_advanced,
    tools=[get_weather],
    middleware=[
        SummarizationMiddleware(
            model= model_advanced,
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)

# response = agent.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "What is the weather in Boston?"
#         }
#     ]
# })

# rprint(response)



agent = create_agent(
    model=model_advanced,
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model=model_medium,
            trigger=("tokens", 1000),
            keep=("messages", 2),
        ),
    ],
)

def invoke_agent(agent, thread_id, message):

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ]
        },
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return result

thread_id = "summarization-test-1"

response = invoke_agent(
    agent,
    thread_id,
    "Explain RAG architecture in detail."
)

rprint(response)
response = invoke_agent(
    agent,
    thread_id,
    "Now explain vector databases in great detail."
)


rprint(response)
response = invoke_agent(
    agent,
    thread_id,
    "Now explain reranking and RRF with several examples."
)


rprint(response)
response = invoke_agent(
    agent,
    thread_id,
    "Now explain retrieval metrics with several examples."
)

rprint(response)
for message in response["messages"]:
    rprint(type(message))
    rprint(message)
    rprint("-" * 80)
rprint("Done")