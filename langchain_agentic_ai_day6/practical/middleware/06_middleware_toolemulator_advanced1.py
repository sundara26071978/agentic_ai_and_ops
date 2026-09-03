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

from pydantic import BaseModel, Field
from datetime import datetime, date
from decimal import Decimal




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



class TradeDetails(BaseModel):
    """Structured representation of executed trade details."""

    trade_id: str = Field(
        description="Unique identifier of the trade."
    )

    status: str = Field(
        description="Current status of the trade, e.g. Executed."
    )

    account: str = Field(
        description="Trading account associated with the trade."
    )

    security: str = Field(
        description="Security symbol or identifier, e.g. AAPL."
    )

    side: str = Field(
        description="Trade side, e.g. Buy or Sell."
    )

    quantity: int = Field(
        description="Original order quantity."
    )

    order_type: str = Field(
        description="Type of order, e.g. Market or Limit."
    )

    limit_price: Decimal | None = Field(
        default=None,
        description="Limit price specified for the order."
    )

    executed_price: Decimal = Field(
        description="Price at which the trade was executed."
    )

    filled_quantity: int = Field(
        description="Quantity actually filled."
    )

    notional_value: Decimal = Field(
        description="Total executed notional value of the trade."
    )

    currency: str = Field(
        default="USD",
        description="Currency of the notional value."
    )

    commission: Decimal = Field(
        description="Commission charged for the trade."
    )

    venue: str = Field(
        description="Execution venue or exchange."
    )

    order_time: datetime = Field(
        description="Timestamp when the order was placed."
    )

    execution_time: datetime = Field(
        description="Timestamp when the order was executed."
    )

    settlement_date: date = Field(
        description="Expected settlement date."
    )

@tool
def get_trade_details(trade_id: str) -> TradeDetails:
    """Retrieve trade details."""
    raise NotImplementedError


@tool
def get_counterparty_details(counterparty: str) -> str:
    """Retrieve counterparty information."""
    raise NotImplementedError


@tool
def get_settlement_instruction(
    counterparty: str,
    security: str
) -> str:
    """Retrieve settlement instructions."""
    raise NotImplementedError

print("-"*50)
print("tool emulator middleware")
print("-"*50)


agent = create_agent(
    model=model_advanced,

    tools=[
        get_trade_details,
        get_counterparty_details,
        get_settlement_instruction,
    ],

    middleware=[
        LLMToolEmulator(
            model=model_advanced
        )
    ],
)

# result = agent.invoke( {
#         "messages": [
#             (
#                 "human",
#                 "Retrieve trade details for trade ID TRD-1001."
#             )
#         ]
#     },
# config={
#         "run_name": "external tool emulator middleware",      # Custom name for this run
#         "tags": ["emulator", "externaltools","agenttracking"],          # Tags for categorization
#         "metadata": {"user_id": "sunjemulator"},     # Custom metadata
      
#     }
# )

# print("-"*50)
# rprint(result)
# print("done")

# for message in result["messages"]:
#     print("=" * 80)
#     print("TYPE:", message.type)
#     print("CONTENT:", message.content)


queries = [
    "What are the details of trade TRD-1001?",
    
    "Give me the information about counterparty Goldman Sachs.",
    
    "What settlement instruction should be used for Goldman Sachs "
    "for security US0378331005?",
    
    "Check trade TRD-1001 and determine whether the counterparty "
    "and settlement instruction are consistent with the trade."
]

for query in queries:

    print("\n" + "#" * 100)
    print("QUERY:", query)

    result = agent.invoke(
        {
            "messages": [
                ("human", query)
            ]
        },
        config={
        "run_name": "external tool emulator middleware",      # Custom name for this run
        "tags": ["emulator", "externaltools","agenttracking"],          # Tags for categorization
        "metadata": {"user_id": "sunjemulator"},     # Custom metadata
      
    }
    )
    rprint(result)

    print("\nFINAL RESPONSE:")
    print(result["messages"][-1].content)