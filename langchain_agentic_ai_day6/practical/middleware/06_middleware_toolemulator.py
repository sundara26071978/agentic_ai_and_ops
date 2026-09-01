import os

from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator
from langchain_core.tools import tool

from rich import print as rprint
from langchain.chat_models import init_chat_model


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



@tool
def get_weather(location: str) -> str:
    """Get the current weather for a location."""
    return f"Weather in {location}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return "Email sent"



agent = create_agent(
    model=model_advanced,
    tools=[get_weather, send_email],
    middleware=[LLMToolEmulator(tools=["get_weather"],model=model_advanced)],
    system_prompt="You are a software development assistant.",
    
)
print("-"*50)
print("tool emulator middleware")
print("-"*50)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": """
            what is the weather in India
            """
        }
    ]
},  
config={
        "run_name": "tool emulator middleware",      # Custom name for this run
        "tags": ["emulator", "tools","agenttracking"],          # Tags for categorization
        "metadata": {"user_id": "sunjemulator"},     # Custom metadata
      
    })

print("-"*50)
rprint(result)
print("done")