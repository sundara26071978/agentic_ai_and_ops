# LangChain LLM Tool Emulator

## 1. Overview

`LLMToolEmulator` is LangChain middleware that **emulates tool execution using an LLM** instead of executing the actual tool implementation.

It is useful when you want to test an agent's tool-selection and orchestration behavior without calling real databases, APIs, enterprise systems, or expensive external services.

### Core idea

Normal agent execution:

```text
User
  ↓
Agent / LLM
  ↓
Tool Call
  ↓
Real Tool
  ↓
External System
  ↓
Tool Result
  ↓
Agent
  ↓
Final Response
```

With `LLMToolEmulator`:

```text
User
  ↓
Agent / LLM
  ↓
Tool Call
  ↓
LLMToolEmulator
  ↓
Emulator LLM
  ↓
Simulated Tool Result
  ↓
Agent
  ↓
Final Response
```

The agent still decides to call the tool, but the actual tool function is intercepted and an LLM generates a realistic tool response.

---

# 2. Why Use a Tool Emulator?

There are three important use cases.

| Use Case | What You Are Testing |
|---|---|
| Test agent behavior without real tools | Agent reasoning and tool orchestration |
| External tool unavailable or expensive | Agent development without backend dependencies |
| Prototype workflows before implementing tools | Agent architecture and workflow |

---

# 3. Use Case 1 — Test Agent Behavior Without Executing Real Tools

You may want to verify:

- Does the agent select the correct tool?
- Does it pass the correct arguments?
- Does it call tools in the correct order?
- Does it correctly use tool results?
- Does it recover from unexpected tool results?

You can test these behaviors without executing the real backend.

## Example

Suppose the real production tool is:

```python
from langchain.tools import tool

@tool
def get_trade_status(trade_id: str) -> str:
    """Get the current status of a securities trade."""

    print("REAL TOOL EXECUTED!")

    return f"Trade {trade_id}: MATCHED"
```

Normally the function executes.

With an emulator:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

agent = create_agent(
    model="openai:gpt-5.6",
    tools=[get_trade_status],
    middleware=[
        LLMToolEmulator(
            tools=["get_trade_status"],
            model="openai:gpt-5-mini",
        )
    ],
)
```

Invoke:

```python
result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "What is the status of trade TRD1001?"
        }
    ]
})
```

The execution becomes:

```text
Agent
  ↓
get_trade_status("TRD1001")
  ↓
LLMToolEmulator
  ↓
Emulator LLM
  ↓
Simulated response
```

The actual `get_trade_status()` implementation does not execute.

---

# 4. Practice Exercise 1 — One Emulated Tool

Create this program:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator
from langchain.tools import tool


@tool
def get_trade_status(trade_id: str) -> str:
    """Get the current status of a securities trade."""

    print("🔥 REAL TOOL EXECUTED!")

    return f"Trade {trade_id}: MATCHED"


agent = create_agent(
    model="openai:gpt-5.6",
    tools=[get_trade_status],
    middleware=[
        LLMToolEmulator(
            tools=["get_trade_status"],
            model="openai:gpt-5-mini",
        )
    ],
)


result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": "Check the status of trade TRD1001"
        }
    ]
})


print(result)
```

## Debug Exercise

Put a breakpoint inside:

```python
@tool
def get_trade_status(trade_id: str):

    print("🔥 REAL TOOL EXECUTED!")

    return f"Trade {trade_id}: MATCHED"
```

Or simply observe:

```python
print("🔥 REAL TOOL EXECUTED!")
```

### Expected observation

```text
The agent selects get_trade_status
             ↓
LLMToolEmulator intercepts the call
             ↓
Real get_trade_status() is NOT executed
             ↓
Emulator LLM generates a ToolMessage
             ↓
Agent continues
```

### What are you testing?

You are testing the **agent**, not the backend.

---

# 5. Use Case 2 — External Tool Is Unavailable or Expensive

A real enterprise tool may depend on:

- REST APIs
- Databases
- Authentication
- Network connectivity
- Vendor systems
- Expensive API calls
- Systems that are not available in development

For example:

```python
@tool
def get_security_reference(isin: str) -> str:
    """Retrieve security reference information."""

    print("🔥 REAL REFERENCE DATA SYSTEM CALLED!")

    return call_reference_data_api(isin)
```

During development, the API may not be available.

Without emulation:

```text
Agent
  ↓
get_security_reference()
  ↓
Reference Data API
  ↓
❌ API unavailable
```

With emulation:

```text
Agent
  ↓
get_security_reference()
  ↓
LLMToolEmulator
  ↓
Emulator LLM
  ↓
Simulated security data
```

This allows you to develop the agent before the external system is ready.

---

# 6. Practice Exercise 2 — Security Reference Data

Define:

```python
from langchain.tools import tool


@tool
def get_security_reference(isin: str) -> str:
    """Retrieve security reference information including
    currency, settlement cycle and asset class."""

    print("🔥 REAL REFERENCE DATA SYSTEM CALLED!")

    return """
    ISIN: US0378331005
    Currency: USD
    Asset Class: Equity
    Settlement Cycle: T+1
    """
```

Configure:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator


agent = create_agent(
    model="openai:gpt-5.6",
    tools=[get_security_reference],
    middleware=[
        LLMToolEmulator(
            tools=["get_security_reference"],
            model="openai:gpt-5-mini",
        )
    ],
)
```

Invoke:

```python
result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Retrieve security information for "
                "ISIN US0378331005 and tell me the "
                "settlement cycle."
            )
        }
    ]
})

print(result)
```

The real reference-data implementation is not called.

The emulator generates a plausible response.

---

# 7. Important Warning About Emulated Data

An emulator response is **not authoritative data**.

It should not be used as the source of truth for:

```text
❌ Actual trade execution
❌ Settlement
❌ Regulatory decisions
❌ Compliance decisions
❌ Production financial calculations
❌ Real customer/account decisions
```

It is a development and testing mechanism.

---

# 8. Use Case 3 — Prototype Agent Workflows Before Implementing Tools

This is particularly useful for Agentic AI projects.

Suppose you want to build a **Trade Prematching Agent**, but the backend tools have not been implemented yet.

You can define placeholder tools:

```python
from langchain.tools import tool


@tool
def get_trade_details(trade_id: str) -> str:
    """Retrieve trade details."""
    raise NotImplementedError


@tool
def get_counterparty_details(counterparty: str) -> str:
    """Retrieve counterparty information."""
    raise NotImplementedError


@tool
def get_settlement_instruction(
    counterparty: str,
    security: str,
) -> str:
    """Retrieve settlement instructions."""
    raise NotImplementedError
```

Normally these tools would fail immediately.

Instead, emulate them:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator


agent = create_agent(
    model="openai:gpt-5.6",
    tools=[
        get_trade_details,
        get_counterparty_details,
        get_settlement_instruction,
    ],
    middleware=[
        LLMToolEmulator(
            model="openai:gpt-5-mini"
        )
    ],
)
```

This lets you prototype the entire workflow before implementing the actual integrations.

---

# 9. Prototype Trade Prematching

User:

```text
Analyze trade TRD1001 and determine whether
it can be pre-matched.
```

The agent could execute a conceptual workflow:

```text
                    Trade Prematching Agent
                              │
                              ▼
                    get_trade_details
                              │
                              ▼
                         Emulator
                              │
                              ▼
                       Trade details
                              │
                              ▼
                  get_counterparty_details
                              │
                              ▼
                         Emulator
                              │
                              ▼
                    Counterparty details
                              │
                              ▼
                get_settlement_instruction
                              │
                              ▼
                         Emulator
                              │
                              ▼
                    Settlement information
                              │
                              ▼
                       Agent reasoning
                              │
                              ▼
                    Prematching decision
```

You can now test:

- Tool selection
- Tool sequencing
- Tool arguments
- Agent reasoning
- Dependency between tool calls
- Missing information handling
- Final response generation

without implementing the backend systems.

---

# 10. Selective Tool Emulation

You do not have to emulate every tool.

Suppose you have three tools:

```text
Tool A → Enterprise database
Tool B → REST API
Tool C → Local calculation
```

You may want:

```text
Tool A → EMULATED
Tool B → EMULATED
Tool C → REAL
```

Configure:

```python
LLMToolEmulator(
    tools=[
        "database_tool",
        "reference_data_tool",
    ],
    model="openai:gpt-5-mini",
)
```

Conceptually:

```text
database_tool
      ↓
   EMULATED


reference_data_tool
      ↓
   EMULATED


calculate_match_score
      ↓
     REAL
```

This is useful during incremental integration.

---

# 11. Hybrid Testing

A particularly useful pattern is to combine real and emulated tools.

Example:

```python
from langchain.tools import tool


@tool
def get_trade_status(trade_id: str) -> str:
    """Get trade status."""
    return "MATCHED"


@tool
def calculate_match_score(
    trade_status: str,
    settlement_status: str,
) -> str:
    """Calculate the trade matching score."""

    return "95%"
```

Configure only the external dependency for emulation:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator


agent = create_agent(
    model="openai:gpt-5.6",
    tools=[
        get_trade_status,
        calculate_match_score,
    ],
    middleware=[
        LLMToolEmulator(
            tools=["get_trade_status"],
            model="openai:gpt-5-mini",
        )
    ],
)
```

Result:

```text
get_trade_status
      ↓
   EMULATOR
      ↓
Simulated trade data


calculate_match_score
      ↓
    REAL
      ↓
Actual calculation
```

This is a powerful transition strategy from prototype to production.

---

# 12. Traditional Mocking vs LLM Tool Emulation

These concepts are related but different.

## Traditional Mock

A traditional mock returns a predefined response:

```python
def mock_trade_status(trade_id):
    return "MATCHED"
```

The result is deterministic.

```text
Tool
 ↓
Hard-coded response
 ↓
"MATCHED"
```

## LLM Tool Emulator

The response is generated dynamically by an LLM.

Conceptually:

```text
Tool name
   +
Tool description
   +
Tool arguments
   +
Emulator LLM
   ↓
Generated ToolMessage
```

This makes the emulator flexible for prototyping.

However, it is also less deterministic than a traditional mock.

### Recommendation

Use:

```text
LLM Emulator
    ↓
Exploratory development
Workflow prototyping
Agent behavior testing
```

Use deterministic mocks/fixtures for:

```text
Automated regression tests
Exact expected outputs
Repeatable CI/CD tests
Business-rule validation
```

---

# 13. What Exactly Is Being Emulated?

A tool call typically contains:

```text
Tool name
Arguments
```

For example:

```json
{
    "name": "get_trade_status",
    "arguments": {
        "trade_id": "TRD1001"
    }
}
```

Conceptually, the emulator uses information about the tool and the tool call to generate a plausible result:

```text
Tool Definition
       +
Tool Call Arguments
       +
Emulator Instructions
       ↓
   Emulator LLM
       ↓
   ToolMessage
```

The agent then receives that result as if the tool had executed.

---

# 14. Debugging the Agent

One of the best ways to learn tool emulation is to inspect:

```python
result["messages"]
```

You may see a sequence conceptually similar to:

```text
HumanMessage
      ↓
AIMessage
      ↓
ToolMessage
      ↓
AIMessage
      ↓
ToolMessage
      ↓
AIMessage
```

The sequence means:

```text
HumanMessage
    ↓
User asks a question

AIMessage
    ↓
Agent decides to call a tool

ToolMessage
    ↓
Tool result — generated by emulator

AIMessage
    ↓
Agent reasons using tool result

ToolMessage
    ↓
Another tool result

AIMessage
    ↓
Final answer
```

This is an excellent debugging technique for understanding LangChain agents.

---

# 15. Practice Lab — Exercise 1

Create:

```python
@tool
def get_trade_status(trade_id: str) -> str:
    """Get the status of a securities trade."""

    print("REAL TOOL CALLED")

    return "MATCHED"
```

Emulate it.

Question:

> Does `REAL TOOL CALLED` appear?

Expected:

```text
NO
```

---

# 16. Practice Lab — Exercise 2

Create two tools:

```python
@tool
def get_trade_status(trade_id: str) -> str:
    """Get the status of a securities trade."""

    return "MATCHED"


@tool
def get_counterparty(trade_id: str) -> str:
    """Get the counterparty for a trade."""

    return "Goldman Sachs"
```

Ask:

```text
What is the status of TRD1001 and who is
the counterparty?
```

Debug:

> Which tool does the agent call first?

---

# 17. Practice Lab — Exercise 3

Add:

```python
@tool
def get_settlement_instruction(
    counterparty: str,
    security: str,
) -> str:
    """Get settlement instructions."""

    return "USD settlement account"
```

Ask:

```text
Determine whether TRD1001 can be pre-matched.
```

Inspect:

```python
result["messages"]
```

Determine:

1. Which tool was called first?
2. Which arguments were generated?
3. Which tool was called next?
4. Did the agent use the first result?
5. What was the final decision?

---

# 18. Practice Lab — Exercise 4

Create a hybrid environment.

Emulate:

```text
get_trade_status
```

but execute:

```text
calculate_match_score
```

Expected:

```text
get_trade_status
      ↓
EMULATED

calculate_match_score
      ↓
REAL
```

This helps you understand selective emulation.

---

# 19. Practice Lab — Exercise 5

Deliberately test bad tool data.

For example, create a simulated scenario where:

```text
Trade Currency      = USD
Settlement Currency = EUR
```

Then determine whether the agent identifies the mismatch.

This tests whether your agent can reason over tool results rather than simply assuming every tool result is correct.

For production-grade automated tests, use deterministic mocks or fixtures when reproducibility is required.

---

# 20. Development → Integration → Production

A useful architecture is:

```text
                 ┌─────────────────────┐
                 │    Agent Logic      │
                 └──────────┬──────────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼

           DEV        INTEGRATION        PROD
             │              │              │
             ▼              ▼              ▼
       LLM Emulator     Mixed Tools    Real Tools
             │              │              │
             ▼              ▼              ▼
       Fast/cheap       Partial        Actual systems
       development      integration    execution
```

## DEV

Use:

```python
LLMToolEmulator(...)
```

Goal:

> Does my agent workflow work?

## INTEGRATION

Emulate tools that are not ready, while using real tools that are available.

Goal:

> Does the agent integrate correctly with the systems already implemented?

## PROD

Remove the emulator.

```text
Agent
  ↓
Real Tools
  ↓
Real Systems
```

Goal:

> Execute actual business operations.

---

# 21. Trade Prematching Example

For an investment-banking back-office prematching agent, a development architecture could look like:

```text
                    User / Event
                         │
                         ▼
                 Trade Prematching
                      Agent
                         │
          ┌──────────────┼───────────────┐
          │              │               │
          ▼              ▼               ▼
    Trade Details   Counterparty       SSI Lookup
        Tool            Tool              Tool
          │              │               │
          └──────────────┼───────────────┘
                         │
                         ▼
                 LLMToolEmulator
                         │
                         ▼
                  Emulator LLM
                         │
                         ▼
                 Simulated Results
                         │
                         ▼
                  Agent Reasoning
                         │
                         ▼
                Prematching Decision
```

This allows you to build and debug the orchestration before connecting:

- Trade database
- Counterparty service
- Security master
- SSI/reference-data service
- Settlement platform
- Other enterprise systems

---

# 22. Recommended Testing Strategy

For a real Agentic AI project, use multiple layers of testing.

```text
                 Agent Testing
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Unit Tests      Emulator Tests   Integration
        │              │              │
        ▼              ▼              ▼
 Deterministic     Dynamic agent    Real tools
 tool tests        behavior tests   + systems
```

### Layer 1 — Unit Tests

Test individual functions.

```text
Input
  ↓
Tool
  ↓
Expected result
```

### Layer 2 — LLM Tool Emulator

Test:

```text
User
  ↓
Agent
  ↓
Tool selection
  ↓
Tool orchestration
  ↓
Final response
```

without external dependencies.

### Layer 3 — Integration Tests

Connect selected real tools.

```text
Agent
  ↓
Real Tool
  ↓
Test Database/API
```

### Layer 4 — Production

All required tools connect to actual enterprise systems.

---

# 23. Important Limitations

LLM tool emulation is powerful, but it has limitations.

## 1. Responses are not deterministic

The emulator is itself an LLM.

The same request can potentially produce different responses.

## 2. Responses may be unrealistic

The emulator does not have access to your actual enterprise database unless you explicitly provide that information.

## 3. It does not test backend correctness

You are testing the agent's interaction with a simulated tool, not the real implementation.

## 4. It can hide integration problems

An agent may work perfectly with the emulator but fail against the actual API because of:

- Authentication
- HTTP errors
- Timeouts
- Schema differences
- Invalid parameters
- Network issues
- Rate limits
- Real data inconsistencies

Therefore, emulator testing should not replace integration testing.

---

# 24. Mental Model

The simplest mental model is:

```text
              NORMAL
              ======

Agent
  ↓
Tool
  ↓
Database/API
  ↓
Result
```

versus:

```text
              EMULATED
              ========

Agent
  ↓
Tool Call
  ↓
LLMToolEmulator
  ↓
LLM
  ↓
Simulated Tool Result
  ↓
Agent
```

The agent's workflow remains essentially the same.

The difference is **where the tool result comes from**.

---

# 25. Key Takeaways

Remember these five points:

### 1. The agent still calls the tool

The agent's tool-selection behavior is preserved.

### 2. The actual tool implementation does not execute

The middleware intercepts the tool call.

### 3. An LLM generates the simulated result

The emulator produces a realistic-looking `ToolMessage`.

### 4. You can emulate all or selected tools

Selective emulation is especially useful during integration.

### 5. It is for development/testing, not business truth

An emulator response is generated data, not authoritative enterprise data.

---

# 26. Final Architecture

The overall concept can be summarized as:

```text
                         USER
                          │
                          ▼
                   ┌─────────────┐
                   │    AGENT    │
                   │     LLM     │
                   └──────┬──────┘
                          │
                     Tool Call
                          │
                          ▼
              ┌───────────────────────┐
              │ LLMToolEmulator       │
              └───────────┬───────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Emulator LLM│
                   └──────┬──────┘
                          │
                   Simulated Result
                          │
                          ▼
                   ┌─────────────┐
                   │    AGENT    │
                   └──────┬──────┘
                          │
                          ▼
                    Final Answer
```

The key idea is:

> **LLMToolEmulator lets you test the agent's behavior as if tools existed, without actually executing those tools.**

For an Agentic AI trade-prematching system, this lets you prototype and debug the orchestration layer first, then progressively replace simulated tools with real enterprise integrations.