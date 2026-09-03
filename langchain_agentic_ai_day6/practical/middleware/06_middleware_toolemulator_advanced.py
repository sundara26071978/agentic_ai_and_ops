# LLM tool emulator
# Emulate tool execution using an LLM for testing purposes, replacing actual tool calls with AI-generated responses. 
# LLM tool emulators are useful for the following:
# Testing agent behavior without executing real tools.
# Developing agents when external tools are unavailable or expensive.
# Prototyping agent workflows before implementing actual tools.



import os

from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator
from langchain_core.tools import tool

from rich import print as rprint
from langchain.chat_models import init_chat_model

import requests
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
def get_trade_status(trade_id: str) -> str:
    """Get the current status of a securities trade."""
    
    print("🔥 REAL TOOL EXECUTED!")
    
    # Expensive database/API call
    return "MATCHED"

@tool
def get_security_reference(isin: str) -> str:
    """Retrieve security reference information including currency,
    settlement cycle and asset class."""

    print("🔥 REAL REFERENCE DATA SYSTEM CALLED!")

    return """
    ISIN: US0378331005
    Currency: USD
    Asset Class: Equity
    Settlement Cycle: T+1
    """

@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float | str:
    """Convert an amount from one currency to another using the latest exchange rate.

    Args:
        amount: The monetary amount to convert.
        from_currency: The three-letter ISO 4217 currency code of the source
            currency, such as "USD", "EUR", or "INR".
        to_currency: The three-letter ISO 4217 currency code of the target
            currency, such as "USD", "EUR", or "INR".

    Returns:
        The converted amount rounded to two decimal places if the exchange
        rate is available. Returns an error message if the currency service
        cannot be reached or no exchange rate is available.

    Examples:
        convert_currency(100, "USD", "EUR") -> 85.42
        convert_currency(5000, "INR", "USD") -> 59.12
    """
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": from_currency, "symbols": to_currency},
            timeout=10,
        )
        response.raise_for_status()
        rate = response.json()["rates"][to_currency]
        return round(amount * rate, 2)
    except requests.exceptions.RequestException as exc:
        return f"Couldn't reach the currency service: {exc}"
    except KeyError:
        return f"No rate available for {from_currency} -> {to_currency}"

agent = create_agent(
    model=model_advanced,
    tools=[get_trade_status,convert_currency,get_security_reference],
    middleware=[LLMToolEmulator(tools=["get_trade_status","convert_currency","get_security_reference"],model=model_advanced)],
    system_prompt="You are a software development assistant.",
    
)
print("-"*50)
print("tool emulator middleware")
print("-"*50)

# result = agent.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "What is the status of trade TRD12345?"
#         }
#     ]
# },  
# config={
#         "run_name": "tool emulator middleware",      # Custom name for this run
#         "tags": ["emulator", "tools","agenttracking"],          # Tags for categorization
#         "metadata": {"user_id": "sunjemulator"},     # Custom metadata
      
#     })


# result = agent.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "Convert JPY 1000000 to MMM"
#         }
#     ]
# },  
# config={
#         "run_name": "external tool emulator middleware",      # Custom name for this run
#         "tags": ["emulator", "externaltools","agenttracking"],          # Tags for categorization
#         "metadata": {"user_id": "sunjemulator"},     # Custom metadata
      
#     })

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Retrieve the security information for "
                "ISIN US0378331005 and tell me the settlement cycle."
            )
        }
    ]
},
config={
        "run_name": "external tool emulator middleware",      # Custom name for this run
        "tags": ["emulator", "externaltools","agenttracking"],          # Tags for categorization
        "metadata": {"user_id": "sunjemulator"},     # Custom metadata
      
    }
)

print("-"*50)
rprint(result)
print("done")