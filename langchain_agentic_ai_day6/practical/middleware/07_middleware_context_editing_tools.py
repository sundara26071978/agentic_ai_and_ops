"""# Context Editing Middleware — LangChain Agent

This example demonstrates how `ContextEditingMiddleware` 
manages a long-running agent conversation by clearing older tool outputs 
while preserving the most recent tool results.
"""
import os

from langchain.agents import create_agent
from rich import print as rprint
from langchain.chat_models import init_chat_model
from langchain.agents.middleware import (
    ContextEditingMiddleware,
    ClearToolUsesEdit,
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




# ============================================================
# 1. Tools that generate large tool outputs
# ============================================================

@tool
def get_trade_details(trade_id: str) -> str:
    """
    Retrieve detailed information about a trade.

    Returns a large simulated trade record so that repeated
    tool calls can increase the agent context size.
    """

    trade = f"""
    TRADE DETAILS
    -------------
    Trade ID       : {trade_id}
    Instrument     : US Equity
    Security       : Apple Inc. (AAPL)
    Side           : BUY
    Quantity       : 100000
    Price          : 225.50
    Currency       : USD
    Trade Date     : 2026-09-01
    Settlement     : T+2
    Counterparty   : GLOBAL_FUND_001
    Trader         : TRADER_123
    Account        : FUND_ACCOUNT_456
    Market         : NASDAQ

    Additional trade attributes:
    Execution venue: NYSE
    Order type     : LIMIT
    Settlement type: DVP
    Broker         : GLOBAL_BROKER
    Custodian      : GLOBAL_CUSTODIAN
    """

    # Simulate a large response
    return trade * 500


@tool
def get_counterparty_details(counterparty_id: str) -> str:
    """
    Retrieve detailed counterparty information.
    """

    counterparty = f"""
    COUNTERPARTY DETAILS
    --------------------
    Counterparty ID : {counterparty_id}
    Name            : GLOBAL INVESTMENT FUND
    Type            : Hedge Fund
    Country         : United States
    LEI             : 549300XXXXXXXXXXXXXX
    Status          : ACTIVE
    Prime Broker    : GLOBAL PRIME BROKER
    Custodian       : GLOBAL CUSTODIAN
    Settlement     : DVP
    """

    return counterparty * 500


@tool
def get_settlement_instructions(trade_id: str) -> str:
    """
    Retrieve settlement instructions for a trade.
    """

    instructions = f"""
    SETTLEMENT INSTRUCTIONS
    -----------------------
    Trade ID        : {trade_id}
    Settlement Date : 2026-09-03
    Currency        : USD
    Custodian       : GLOBAL CUSTODIAN
    Custodian BIC   : CUSTUS33XXX
    Account         : 123456789
    SSI Status      : VERIFIED
    Settlement Type : DVP
    Delivery Agent  : GLOBAL_AGENT
    Receiving Agent : GLOBAL_RECEIVER
    """

    return instructions * 500


@tool
def check_trade_match(trade_id: str) -> str:
    """
    Check whether a trade matches between the two counterparties.
    """

    result = f"""
    TRADE MATCH RESULT
    ------------------
    Trade ID          : {trade_id}
    Trade Status      : MATCHED
    Quantity Match    : TRUE
    Price Match       : TRUE
    Currency Match    : TRUE
    Settlement Match  : TRUE
    Counterparty Match: TRUE
    SSI Match         : TRUE
    Overall Result    : PREMATCHED
    """

    return result * 500


@tool
def get_market_reference_data(symbol: str) -> str:
    """
    Retrieve market reference data for a security.
    """

    market_data = f"""
    MARKET REFERENCE DATA
    ---------------------
    Symbol          : {symbol}
    Exchange        : NASDAQ
    Currency        : USD
    Asset Class     : EQUITY
    Country         : USA
    Sector          : Technology
    Trading Status  : ACTIVE
    Reference Price : 225.50
    """

    return market_data * 500


# ============================================================
# 2. Context Editing Middleware
# ============================================================

context_editing = ContextEditingMiddleware(
    edits=[
        ClearToolUsesEdit(
            trigger=3000,
            keep=3,
        ),
    ],
)


# ============================================================
# 3. Create Agent
# ============================================================

agent = create_agent(
    model=model_advanced,

    tools=[
        get_trade_details,
        get_counterparty_details,
        get_settlement_instructions,
        check_trade_match,
        get_market_reference_data,
    ],

    middleware=[
        context_editing,
    ],
)


# ============================================================
# 4. Invoke the Agent
# ============================================================

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
                Perform pre-matching analysis for trade TRD-10001.

                1. Retrieve the trade details.
                2. Retrieve the counterparty details.
                3. Retrieve settlement instructions.
                4. Retrieve market reference data.
                5. Check whether the trade can be pre-matched.

                Provide the final pre-match decision.
                """
            }
        ]
    },
config={
        "run_name": "Context Editing Middleware",      # Custom name for this run
        "tags": ["contextediting", "tools","agenttracking"],          # Tags for categorization
        "metadata": {"user_id": "sunjcontextediting"},     # Custom metadata
      
    }
)

# ============================================================
# 5. Display final response
# ============================================================

rprint(response["messages"][-1].content)
print("-"*50)
print("Context Editing Middleware")
print("-"*50)

print("-"*50)
rprint(response)
print("done")