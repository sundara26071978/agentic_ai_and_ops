# LLM Tool Selector vs Provider Tool Search

## 1. Basic Difference

**LLM Tool Selector:** an LLM-based selector chooses which tools are relevant before the main agent/model runs.

**Provider Tool Search:** the model provider performs server-side discovery of deferred tools, so the full tool catalog does not need to be loaded into the model context upfront.

### LLM Tool Selector

```text
Your application
      |
      | tool catalog
      v
LLM Tool Selector
      |
      | selects relevant tools
      v
Main Agent / LLM
```

### Provider Tool Search

```text
Your application
      |
      | searchable/deferred tools
      v
Model Provider
      |
      | server-side tool search
      v
Relevant tool definitions
      |
      v
Main Model
```

---

# 2. Common Securities Trading Tools

```python
from langchain.tools import tool

@tool
def lookup_trade(trade_id: str) -> str:
    """Look up trade details using a trade ID."""
    return f"""
Trade {trade_id}:
Security: AAPL
Side: BUY
Quantity: 100
Counterparty: ABC Fund
Settlement Date: 2026-09-04
"""

@tool
def get_settlement_status(trade_id: str) -> str:
    """Get the settlement status of a trade."""
    return f"Trade {trade_id} settlement status: FAILED"

@tool
def get_settlement_fail_reason(trade_id: str) -> str:
    """Get the reason why a trade failed settlement."""
    return """
Trade settlement failed because:
SSI mismatch - incorrect custodian account.
"""

@tool
def get_security_price(symbol: str) -> str:
    """Get the current market price of a security."""
    return f"{symbol} current price: $189.50"

@tool
def get_fx_rate(pair: str) -> str:
    """Get the current foreign exchange rate."""
    return f"{pair} FX rate: 1.10"

@tool
def calculate_exposure(account: str) -> str:
    """Calculate trading exposure for an account."""
    return f"{account} exposure: $2.4M"

@tool
def get_var(account: str) -> str:
    """Get Value at Risk for an account."""
    return f"{account} VaR: $125K"
```

---

# 3. LLM Tool Selector

The selector uses an LLM to determine which tools should be exposed to the main agent.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import llm_tool_selector_middleware

agent = create_agent(
    model="openai:gpt-5.4",

    tools=[
        lookup_trade,
        get_settlement_status,
        get_settlement_fail_reason,
        get_security_price,
        get_fx_rate,
        calculate_exposure,
        get_var,
    ],

    middleware=[
        llm_tool_selector_middleware(
            model="openai:gpt-5.4-mini",
            max_tools=3,
        )
    ],
)
```

Conceptually:

```text
User
 |
 | "Why did TRD-1001 fail settlement?"
 v
Selector LLM
 |
 | selects
 +-- lookup_trade
 +-- get_settlement_status
 +-- get_settlement_fail_reason
 |
 v
Main Agent
 |
 +-- lookup_trade("TRD-1001")
 +-- get_settlement_status("TRD-1001")
 +-- get_settlement_fail_reason("TRD-1001")
 |
 v
Final answer
```

## Invoke Script

```python
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Why did trade TRD-1001 fail settlement?",
            }
        ]
    }
)

for message in result["messages"]:
    message.pretty_print()
```

The selector reduces the tool set before the main agent reasons about and calls tools.

---

# 4. Provider Tool Search

Provider tool search is different. Tools are marked as deferred/searchable and the provider discovers relevant tools when needed.

## Anthropic Example

```python
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from anthropic.types.beta import BetaToolSearchToolBM2520251119Param
```

Mark tools for deferred loading:

```python
@tool(extras={"defer_loading": True})
def lookup_trade(trade_id: str) -> str:
    """Look up trade details using a trade ID."""
    return f"""
Trade {trade_id}:
Security: AAPL
Side: BUY
Quantity: 100
Counterparty: ABC Fund
Settlement Date: 2026-09-04
"""

@tool(extras={"defer_loading": True})
def get_settlement_status(trade_id: str) -> str:
    """Get the settlement status of a trade."""
    return f"Trade {trade_id} settlement status: FAILED"

@tool(extras={"defer_loading": True})
def get_settlement_fail_reason(trade_id: str) -> str:
    """Get the reason why a trade failed settlement."""
    return "SSI mismatch - incorrect custodian account."

@tool(extras={"defer_loading": True})
def get_security_price(symbol: str) -> str:
    """Get the current market price of a security."""
    return f"{symbol} current price: $189.50"

@tool(extras={"defer_loading": True})
def get_fx_rate(pair: str) -> str:
    """Get the current foreign exchange rate."""
    return f"{pair} FX rate: 1.10"
```

Create the provider-side search tool:

```python
tool_search = BetaToolSearchToolBM2520251119Param(
    name="tool_search_tool_bm25",
    type="tool_search_tool_bm25_20251119",
)
```

Create the model:

```python
model = ChatAnthropic(
    model="claude-sonnet-4-6"
)
```

Create the agent:

```python
agent = create_agent(
    model=model,
    tools=[
        tool_search,
        lookup_trade,
        get_settlement_status,
        get_settlement_fail_reason,
        get_security_price,
        get_fx_rate,
    ],
)
```

## Invoke Script

```python
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Why did trade TRD-1001 fail settlement?",
            }
        ]
    }
)

for message in result["messages"]:
    message.pretty_print()
```

Conceptually:

```text
User
 |
 | "Why did TRD-1001 fail settlement?"
 v
Claude
 |
 | I need a settlement-related tool
 v
Anthropic Provider Tool Search
 |
 | searches deferred tool catalog
 v
Relevant tools
 |
 +-- get_settlement_status
 +-- get_settlement_fail_reason
 |
 v
Claude
 |
 v
Tool calls
 |
 v
Final answer
```

---

# 5. OpenAI Provider Tool Search

A similar pattern can be used with OpenAI's Responses API integration.

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

@tool(extras={"defer_loading": True})
def lookup_trade(trade_id: str) -> str:
    """Look up a securities trade by trade ID."""
    return f"Trade {trade_id}: AAPL BUY 100 shares"

@tool(extras={"defer_loading": True})
def get_settlement_status(trade_id: str) -> str:
    """Get settlement status for a securities trade."""
    return f"Trade {trade_id}: FAILED"

@tool(extras={"defer_loading": True})
def get_settlement_fail_reason(trade_id: str) -> str:
    """Get the reason a securities trade failed settlement."""
    return "SSI mismatch"

model = ChatOpenAI(
    model="gpt-5.4",
    use_responses_api=True,
)

agent = create_agent(
    model=model,
    tools=[
        lookup_trade,
        get_settlement_status,
        get_settlement_fail_reason,
        {
            "type": "tool_search"
        },
    ],
)
```

## Invoke Script

```python
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Why did TRD-1001 fail settlement?",
            }
        ]
    }
)

for message in result["messages"]:
    message.pretty_print()
```

---

# 6. Side-by-Side Execution

Suppose there are 500 tools.

## LLM Tool Selector

```text
                 USER
                  |
                  v
        +------------------+
        | Selector LLM     |
        | gpt-5.4-mini     |
        +------------------+
                  |
                  | select relevant tools
                  v
       +-----------------------+
       | 3 selected tools      |
       +-----------------------+
                  |
                  v
        +------------------+
        | Main LLM         |
        | gpt-5.4          |
        +------------------+
                  |
                  v
              Tool Call
```

## Provider Tool Search

```text
                 USER
                  |
                  v
        +------------------+
        | Main LLM         |
        | Claude/OpenAI    |
        +------------------+
                  |
                  | tool search
                  v
        +------------------+
        | Provider Search  |
        +------------------+
                  |
                  | discover relevant tools
                  v
       +-----------------------+
       | 1-5 relevant tools    |
       +-----------------------+
                  |
                  v
        +------------------+
        | Main LLM         |
        +------------------+
                  |
                  v
              Tool Call
```

---

# 7. Key Difference

| Aspect | LLM Tool Selector | Provider Tool Search |
|---|---|---|
| Selection performed by | LLM-based selector | Model provider |
| Location | Application/agent layer | Provider infrastructure |
| Main purpose | Select/reduce tools | Lazy discovery/loading |
| Provider dependency | No | Yes |
| Application control | High | Lower |
| Large tool catalogs | Useful | Especially useful |
| Main model initially gets all schemas? | Depends on implementation | Deferred tools are designed not to be loaded initially |

---

# 8. Recommended Architecture for a Bank

For a large securities-trading platform, the two approaches can be combined:

```text
                         USER
                           |
                           v
                 +---------------------+
                 | DOMAIN ROUTER       |
                 |                     |
                 | Trade?              |
                 | Settlement?         |
                 | KYC?                |
                 | Risk?               |
                 +---------------------+
                           |
                           v
                  Settlement Tool Set
                           |
                           v
               +-----------------------+
               | Provider Tool Search  |
               +-----------------------+
                           |
                           v
                    Relevant Tools
                           |
                           v
                      Main Agent
                           |
                           v
                       Tool Calls
```

For example:

```text
10,000 enterprise tools
          |
          v
     Domain Router
          |
          | Settlement
          v
       500 tools
          |
          v
Provider Tool Search
          |
          v
       2-5 tools
          |
          v
        Main LLM
```

This provides:

**Application-level control + provider-level lazy tool discovery.**

---

# 9. Final Mental Model

```text
NORMAL TOOL CALLING
-------------------

500 tools
   ↓
LLM sees 500
   ↓
LLM chooses 1


LLM TOOL SELECTOR
-----------------

500 tools
   ↓
Selector LLM
   ↓
select 5
   ↓
Main LLM sees 5


PROVIDER TOOL SEARCH
--------------------

500 tools
   ↓
Provider tool search
   ↓
find 1-5
   ↓
Main LLM sees loaded tools
```

## One-Line Summary

> **LLM Tool Selector = application-side LLM routing.**

> **Provider Tool Search = provider-side lazy tool discovery.**

For a large enterprise/banking agent platform, a strong architecture can use **domain routing first, followed by provider tool search within the selected domain**.
