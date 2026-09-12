"""

Write short-term memory from tools
To modify the agent’s short-term memory (state) during execution, you can return state updates directly from the tools.
This is useful for persisting intermediate results or making information accessible to subsequent tools or prompts.

"""


from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from langchain.tools import tool, ToolRuntime
from langchain.messages import ToolMessage
from langgraph.types import Command
from pydantic import BaseModel

import os

import pprint
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from rich import print as rprint
from dotenv import load_dotenv

load_dotenv()

model_advanced = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)




class CustomContext(TypedDict):
    user_name: str


def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"The weather in {city} is always sunny!"


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context["user_name"]
    system_prompt = f"You are a helpful assistant. Address the user as {user_name}."
    return system_prompt


agent = create_agent(
    model=model_advanced,
    tools=[get_weather],
    middleware=[dynamic_system_prompt],
    context_schema=CustomContext,
)

if __name__ == "__main__":
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What is the weather in SF?"}]},
        context=CustomContext(user_name="Sunj"),
    )
    for msg in result["messages"]:
        msg.pretty_print()