"""
Provider tool search
Defer selected tools behind model providers’ server-side tool search, so the model discovers them on demand instead of receiving every tool schema up front. Provider tool search is useful for:
Reducing context bloat when using many tools.
Improving tool selection accuracy by surfacing only relevant tools.

# The provide tool search might not work if we are inferencing a model from a llm gateways like open router/aicredits
"""
import os

from langchain.agents import create_agent
from rich import print as rprint
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import (
    ContextEditingMiddleware,
    ClearToolUsesEdit,
    ProviderToolSearchMiddleware,
)

from langchain_core.tools import tool

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


# ---------------------------------------------------------
# 1. Define tools
# ---------------------------------------------------------

@tool
def get_trade(trade_id: str) -> str:
    """Retrieve trade details using a trade ID."""
    print(f"[TOOL] get_trade called with trade_id={trade_id}")

    return (
        f"Trade {trade_id}: "
        "BUY 1000 IBM, counterparty=CP001, "
        "settlement_date=2026-09-03"
    )


@tool
def lookup_counterparty(counterparty_id: str) -> str:
    """Retrieve counterparty information."""
    print(
        f"[TOOL] lookup_counterparty called "
        f"with counterparty_id={counterparty_id}"
    )

    return (
        f"Counterparty {counterparty_id}: "
        "Goldman Sachs, status=ACTIVE"
    )


@tool
def lookup_order(order_id: str) -> str:
    """Retrieve order information using an order ID."""
    print(
        f"[TOOL] lookup_order called with order_id={order_id}"
    )

    return (
        f"Order {order_id}: "
        "BUY 1000 IBM, status=EXECUTED"
    )


# ---------------------------------------------------------
# 2. Create agent
# ---------------------------------------------------------

agent = create_agent(
    model=model_advanced,

    tools=[
        get_trade,
        lookup_counterparty,
        lookup_order,
    ],

    middleware=[
        ProviderToolSearchMiddleware(
            searchable_tools=[
                "lookup_counterparty",
                "lookup_order",
            ]
        )
    ],
)


# ---------------------------------------------------------
# 3. Invoke agent
# ---------------------------------------------------------


def invoke_agent(user_request: str):

    print("\n" + "=" * 70)
    print("USER REQUEST")
    print("=" * 70)

    print(user_request)

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_request,
                }
            ]
        },
        config={
        "run_name": "Provider Toolsearch Middleware",      # Custom name for this run
        "tags": ["providertoolsearch", "toolsdeferloading","agenttracking"],          # Tags for categorization
        "metadata": {"user_id": "sunjProviderToolsearch"},     # Custom metadata
    
    }
    )

    print("\n" + "=" * 70)
    print("FINAL RESPONSE")
    print("=" * 70)

    rprint(result["messages"][-1].content)

    return result


# ---------------------------------------------------------
# 4. Test
# ---------------------------------------------------------

if __name__ == "__main__":

    result= invoke_agent(
        "Get trade TRD123 and tell me the counterparty details."
    )
    rprint(result)

