# Context Editing Middleware — LangChain Agent

This example demonstrates how `ContextEditingMiddleware` manages a long-running agent conversation by clearing older tool outputs while preserving the most recent tool results.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ContextEditingMiddleware,
    ClearToolUsesEdit,
)

from langchain_core.tools import tool


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
            trigger=100000,
            keep=3,
        ),
    ],
)


# ============================================================
# 3. Create Agent
# ============================================================

agent = create_agent(
    model="gpt-5.5",

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
    }
)


# ============================================================
# 5. Display final response
# ============================================================

print(response["messages"][-1].content)
```

## What triggers the context editing?

The important configuration is:

```python
ClearToolUsesEdit(
    trigger=100000,
    keep=3,
)
```

Think of it as:

```text
                Agent Context
                     │
                     ▼
        ┌──────────────────────────┐
        │ Tool outputs accumulate  │
        └────────────┬─────────────┘
                     │
                     │ token count
                     ▼
              > 100,000 tokens?
                     │
                ┌────┴────┐
                │         │
               NO        YES
                │         │
                ▼         ▼
             Keep      Clear older
             context   tool outputs
                           │
                           ▼
                    Keep latest 3
                    tool results
```

So `trigger=100000` means:

> Start applying the edit when the relevant tool-output context reaches approximately 100K tokens.

And:

```python
keep=3
```

means:

> Preserve the three most recent tool results and remove older tool outputs from the model's context.

---

# A better way to demonstrate it explicitly

For learning/debugging, I would actually recommend creating a **single tool that intentionally generates large results**.

```python
@tool
def retrieve_trade_history(trade_id: str, number_of_records: int = 1000) -> str:
    """
    Retrieve historical trade records.

    Used to demonstrate context growth.
    """

    records = []

    for i in range(number_of_records):
        records.append(
            f"""
            Trade History Record {i}

            Trade ID       : {trade_id}-{i}
            Instrument     : AAPL
            Side           : BUY
            Quantity       : {1000 + i}
            Price          : 225.50
            Currency       : USD
            Counterparty   : FUND_{i}
            Settlement     : DVP
            Settlement Date: 2026-09-03
            Status         : MATCHED
            Execution Venue: NASDAQ
            Broker         : GLOBAL_BROKER
            Custodian      : GLOBAL_CUSTODIAN
            """
        )

    return "\n".join(records)
```

Then create:

```python
agent = create_agent(
    model="gpt-5.5",

    tools=[
        get_trade_details,
        get_counterparty_details,
        get_settlement_instructions,
        check_trade_match,
        get_market_reference_data,
        retrieve_trade_history,
    ],

    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=100000,
                    keep=3,
                ),
            ],
        ),
    ],
)
```

And invoke it:

```python
response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
                Analyze trade TRD-10001.

                Retrieve the trade history multiple times,
                then retrieve the counterparty information,
                settlement instructions, and trade details.

                Finally determine whether the trade can be pre-matched.
                """
            }
        ]
    }
)
```

## The important conceptual distinction

Context editing **does not delete the actual data from your database**.

It only changes what is carried forward in the **LLM conversation context**.

```text
                  Database
                     │
                     │
                     ▼
             ┌───────────────┐
             │ Trade History │
             └───────┬───────┘
                     │
                     ▼
                  Tool
                     │
                     ▼
              Tool Result
                     │
                     ▼
             Agent Context
                     │
              100K threshold
                     │
                     ▼
          ContextEditingMiddleware
                     │
          ┌──────────┴──────────┐
          │                     │
      Old results           Recent 3
        removed             retained
          │                     │
          ▼                     ▼
       Not sent             Sent to LLM
       to LLM
```

This is particularly useful for your **IB trade pre-matching agent** because a long-running investigation might look like:

```text
User
 │
 ▼
Trade details
 │
 ▼
Counterparty lookup
 │
 ▼
SSI lookup
 │
 ▼
Historical trades
 │
 ▼
Settlement exceptions
 │
 ▼
Market reference
 │
 ▼
Compliance checks
 │
 ▼
Previous failed matches
 │
 ▼
More historical data
 │
 ▼
...
 │
 ▼
Context becomes huge
 │
 ▼
ContextEditingMiddleware
 │
 ├── Old tool result #1  ❌ cleared
 ├── Old tool result #2  ❌ cleared
 ├── Old tool result #3  ❌ cleared
 ├── ...
 ├── Recent result #1   ✅ kept
 ├── Recent result #2   ✅ kept
 └── Recent result #3   ✅ kept
```

### One subtle but important point

`keep=3` does **not** mean "keep the last three messages."

It is specifically about **tool-use outputs** being edited. The purpose is to prevent large historical tool results from consuming the model's context while retaining the most recent tool information that is likely to be relevant.

For your pre-matching architecture, I would therefore view `ContextEditingMiddleware` as a **context lifecycle / context-budget control layer**, sitting alongside your other harness layers:

```text
                    PRE-MATCHING AGENT
                           │
             ┌─────────────┴─────────────┐
             │                           │
        Guardrails                    Policies
             │                           │
             └─────────────┬─────────────┘
                           │
                    Agent / Model
                           │
                    Tool execution
                           │
                           ▼
                 Tool results accumulate
                           │
                           ▼
              ContextEditingMiddleware
                           │
                 ┌─────────┴─────────┐
                 │                   │
             Recent data          Old data
                 │                   │
              KEEP 3             CLEAR
                 │                   │
                 └─────────┬─────────┘
                           ▼
                     Next LLM call
```

This is different from **summarization middleware**: context editing can simply remove old tool outputs, whereas summarization attempts to preserve their information in a compressed form.