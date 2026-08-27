import os

from dotenv import load_dotenv

load_dotenv()

import pprint
import pprint
from langchain.tools import tool

from langchain.chat_models import init_chat_model
from rich import print as rprint

model_free = init_chat_model("openai/gpt-oss-20b",
                        api_key=os.environ["GROQ_API_KEY"],
                        model_provider="groq",
                        # base_url="https://api.groq.com/openai/v1",
                        max_tokens=4000, temperature=0.0)

model_basic = init_chat_model("openrouter/free",
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

model_safety = init_chat_model("nvidia/nemotron-3.5-content-safety:free",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)

from langchain.agents import create_agent

@tool
def get_weather(city : str) -> str :
    """Get current weather of a city"""
    return f"The weather in {city} is always sunny"

agent = create_agent(
    model=model_free,
    tools=[get_weather],
    middleware=[]
   )

result= agent.invoke({"messages":[{"role":"user", "content" : "what is the weather in Newyork"}]})

result1= agent.invoke({"messages":[{"role":"user", "content" : "what is the weather in Texas"}]})

rprint(result)

rprint(result1)

print("done")