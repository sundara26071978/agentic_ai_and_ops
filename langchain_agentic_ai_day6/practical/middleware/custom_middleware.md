

Absolutely — **banking use case**, specifically your **investment-banking trade pre-matching agent**.

The same distinction becomes much clearer in this context.

## Banking use case

Let's assume your agent receives:

> "Pre-match trade TRD-1001 and tell me whether it is ready for settlement."

The agent may call:

```text
get_trade_details()
        ↓
get_counterparty_details()
        ↓
get_settlement_instructions()
        ↓
compare_trade_fields()
        ↓
pre_match_trade()
```

Now we can put **Node-style** and **Wrap-style hooks** around this flow.

---

# 1. Node-style hooks in trade pre-matching

Think:

> **"Run something when the agent reaches a particular lifecycle point."**

For example, before the model decides what to do:

```python
@before_model
def audit_request(state, runtime):
    print("Starting trade pre-match")
```

After the model responds:

```python
@after_model
def audit_response(state, runtime):
    print("Trade pre-match reasoning completed")
```

You can also have a hook around a tool call:

```python
@before_tool
def validate_trade_tool(request, runtime):
    tool_name = request.tool_call["name"]

    if tool_name == "pre_match_trade":
        print("About to pre-match trade")
```

Conceptually:

```text
                 Agent
                   │
                   ▼
          ┌─────────────────┐
          │ before_model    │  ← Node hook
          └────────┬────────┘
                   ↓
                LLM
                   ↓
          decides to call
          get_trade_details
                   ↓
          ┌─────────────────┐
          │ before_tool     │  ← Node hook
          └────────┬────────┘
                   ↓
        get_trade_details()
                   ↓
          ┌─────────────────┐
          │ after_tool      │  ← Node hook
          └─────────────────┘
```

The hook is primarily saying:

> **"Something happened at this node; let me inspect/validate/audit it."**

---

# 2. Wrap-style hook in trade pre-matching

Now suppose you want stronger control.

You want:

> "Before calling `pre_match_trade`, check that the trade is eligible. Then execute it. If the matching service times out, retry. Finally audit the result."

That's a **Wrap-style hook**.

```python
@wrap_tool_call
def trade_pre_match_wrapper(request, handler):

    print("BEFORE pre-match")

    # 1. Validate
    validate_trade(request)

    # 2. Execute actual tool
    result = handler(request)

    # 3. Audit result
    audit_trade_result(result)

    print("AFTER pre-match")

    return result
```

The important part is:

```python
result = handler(request)
```

`handler` represents the **actual downstream execution**.

So the wrapper controls what happens around it.

---

# 3. Banking example: validation

Suppose:

```text
TRD-1001

Buy 100 AAPL
Counterparty: ABC Bank
Settlement date: T+2
```

The agent wants to call:

```python
pre_match_trade("TRD-1001")
```

Your Wrap middleware can enforce:

```text
             Wrap Hook
                 │
                 ▼
        Validate trade
                 │
        ┌────────┴────────┐
        │                 │
      valid             invalid
        │                 │
        ▼                 ▼
  call handler()       BLOCK
        │
        ▼
 pre_match_trade()
```

For example:

```python
@wrap_tool_call
def trade_control(request, handler):

    trade_id = request.tool_call["args"]["trade_id"]

    trade = get_trade_from_db(trade_id)

    if trade["status"] != "EXECUTED":
        raise ValueError(
            f"{trade_id} cannot be pre-matched"
        )

    return handler(request)
```

The key difference is that the wrapper can say:

> **"Do NOT execute the actual tool."**

---

# 4. Node-style vs Wrap-style for this exact scenario

### Node-style

```python
@before_tool_call
def validate(request):

    if request.tool_call["name"] == "pre_match_trade":
        validate_trade(request)
```

The middleware performs a validation step associated with that lifecycle point.

### Wrap-style

```python
@wrap_tool_call
def validate_and_execute(request, handler):

    validate_trade(request)

    result = handler(request)

    audit(result)

    return result
```

Now the middleware owns the **execution boundary**.

That's a much more powerful abstraction.

---

# 5. Banking example: retry a settlement service

Imagine:

```text
pre_match_trade()
       ↓
Settlement Matching Service
       ↓
TIMEOUT
```

With Wrap-style:

```python
@wrap_tool_call
def resilient_pre_match(request, handler):

    max_retries = 3

    for attempt in range(max_retries):

        try:
            return handler(request)

        except TimeoutError:

            print(
                f"Pre-match attempt {attempt + 1} failed"
            )

            if attempt == max_retries - 1:
                raise
```

Execution:

```text
              Wrapper
                 │
                 ▼
             Attempt 1
                 │
              timeout
                 ↓
             Attempt 2
                 │
              timeout
                 ↓
             Attempt 3
                 │
              success
                 ↓
             Result
```

A Node-style `after_tool` hook can't naturally do this because by the time it runs, the failed execution has already happened.

---

# 6. Banking example: audit trail

This is a good Node-style use case.

```python
@after_tool_call
def audit_tool_result(request, result):

    trade_id = request.tool_call["args"].get(
        "trade_id"
    )

    write_audit_log(
        trade_id=trade_id,
        tool=request.tool_call["name"],
        result=result
    )
```

You aren't trying to control the tool.

You're saying:

> "Whenever this node completes, record what happened."

That's exactly where Node-style hooks shine.

---

# 7. Banking example: authorization

Suppose your pre-match agent can call:

```text
get_trade_details
get_ssi
compare_trade
pre_match_trade
cancel_trade
```

But only certain users should be allowed to call:

```text
cancel_trade
```

A Wrap hook can act as a policy enforcement boundary:

```python
@wrap_tool_call
def authorization_wrapper(request, handler):

    tool_name = request.tool_call["name"]

    if tool_name == "cancel_trade":

        if not user_has_permission():
            raise PermissionError(
                "User is not authorized to cancel trades"
            )

    return handler(request)
```

Flow:

```text
                 Tool Call
                     │
                     ▼
             ┌───────────────┐
             │ Authorization │
             │    Wrapper    │
             └───────┬───────┘
                     │
              ┌──────┴──────┐
              │             │
          authorized      denied
              │             │
              ▼             ▼
        handler()          BLOCK
              │
              ▼
       cancel_trade()
```

This is particularly useful in banking because the wrapper becomes a **control boundary**.

---

# 8. Complete simplified LangChain example

Here's how I'd structure your trade pre-match agent conceptually:

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    before_model,
    after_model,
    wrap_tool_call,
)
from langchain.tools import tool


@tool
def get_trade_details(trade_id: str):
    return {
        "trade_id": trade_id,
        "status": "EXECUTED",
        "account": "ACCT-78421",
        "security": "AAPL",
        "side": "BUY",
        "quantity": 100,
        "price": 189.50,
    }


@tool
def get_settlement_instructions(trade_id: str):
    return {
        "trade_id": trade_id,
        "settlement_account": "SETTLE-001",
        "settlement_date": "T+2",
    }


@tool
def pre_match_trade(trade_id: str):
    return {
        "trade_id": trade_id,
        "match_status": "MATCHED",
    }


@before_model
def pre_match_before_model(state, runtime):

    print("=== BEFORE MODEL ===")

    # Audit / metrics / context checks
    print(
        "Starting trade pre-match workflow"
    )


@after_model
def pre_match_after_model(state, runtime):

    print("=== AFTER MODEL ===")

    # Record model completion
    print(
        "Model completed pre-match reasoning"
    )


@wrap_tool_call
def banking_tool_wrapper(request, handler):

    tool_name = request.tool_call["name"]

    print(
        f"=== TOOL START: {tool_name} ==="
    )

    # ---------------------------------
    # PRE-EXECUTION CONTROL
    # ---------------------------------

    if tool_name == "pre_match_trade":

        trade_id = request.tool_call[
            "args"
        ]["trade_id"]

        print(
            f"Validating {trade_id}"
        )

        # Example control
        trade = get_trade_details.invoke(
            {"trade_id": trade_id}
        )

        if trade["status"] != "EXECUTED":
            raise ValueError(
                "Only executed trades can be pre-matched"
            )

    # ---------------------------------
    # ACTUAL TOOL EXECUTION
    # ---------------------------------

    result = handler(request)

    # ---------------------------------
    # POST-EXECUTION
    # ---------------------------------

    print(
        f"=== TOOL END: {tool_name} ==="
    )

    print("Result:", result)

    return result


agent = create_agent(
    model="gpt-5.5",

    tools=[
        get_trade_details,
        get_settlement_instructions,
        pre_match_trade,
    ],

    middleware=[
        pre_match_before_model,
        banking_tool_wrapper,
        pre_match_after_model,
    ],
)
```

Then invoke:

```python
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Pre-match trade TRD-1001. "
                    "Check the trade details and "
                    "settlement instructions first."
                ),
            }
        ]
    }
)

print("\nFINAL RESULT")
print(result)
```

---

# 9. Expected conceptual execution

Your agent could produce a flow like:

```text
User
 │
 │ Pre-match TRD-1001
 ▼
┌──────────────────────┐
│ before_model         │
│ Audit request        │
└──────────┬───────────┘
           ▼
        LLM
           │
           │ get_trade_details
           ▼
┌────────────────────────────┐
│ WRAP TOOL                  │
│                            │
│ before                     │
│   ↓                        │
│ get_trade_details          │
│   ↓                        │
│ after                      │
└─────────────┬──────────────┘
              ▼
             LLM
              │
              │ get_settlement_instructions
              ▼
┌────────────────────────────┐
│ WRAP TOOL                  │
│                            │
│ before                     │
│   ↓                        │
│ get_settlement_instructions│
│   ↓                        │
│ after                      │
└─────────────┬──────────────┘
              ▼
             LLM
              │
              │ pre_match_trade
              ▼
┌────────────────────────────┐
│ WRAP TOOL                  │
│                            │
│ Validate trade             │
│       ↓                    │
│ handler()                  │
│       ↓                    │
│ pre_match_trade()          │
│       ↓                    │
│ Audit result               │
└─────────────┬──────────────┘
              ▼
             LLM
              ▼
┌──────────────────────┐
│ after_model          │
│ Audit final response │
└──────────┬───────────┘
           ▼
         User
```

## 10. The banking mental model

For your **trade pre-matching agent**, I'd remember it this way:

| Requirement                                   | Best fit       |
| --------------------------------------------- | -------------- |
| Log every model invocation                    | **Node-style** |
| Count model calls                             | **Node-style** |
| Audit final model response                    | **Node-style** |
| Inspect tool result                           | **Node-style** |
| Validate tool request                         | **Either**     |
| Block a tool call                             | **Wrap-style** |
| Retry a tool                                  | **Wrap-style** |
| Fallback to another tool/model                | **Wrap-style** |
| Add authorization around execution            | **Wrap-style** |
| Transaction / rollback                        | **Wrap-style** |
| Cache tool execution                          | **Wrap-style** |
| Measure exact execution latency               | **Wrap-style** |
| Modify behavior before/after actual execution | **Wrap-style** |

### The simplest distinction

For your banking agent:

**Node-style**

> "A trade pre-match step just happened. Let me inspect/audit/react to it."

**Wrap-style**

> "I'm going to sit around the trade pre-match operation and control what happens before, during, and after it."

And this distinction becomes especially important when you combine it with the other middleware we've been discussing — **PII, Human-in-the-Loop, Context Editing, Summarization, Model Fallback, and Provider Tool Search**. In a production trade-processing agent, many of those controls naturally map to either **node-style observation** or **wrap-style execution control**.

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    before_model,
    after_model,
    wrap_tool_call,
)
from langchain.tools import tool


@tool
def get_trade_details(trade_id: str):
    """
    Retrieve the executed trade details for a given trade ID.

    This tool is used by the trade pre-matching agent to obtain the
    canonical trade information before attempting to pre-match the trade.

    Args:
        trade_id: Unique identifier of the trade, for example "TRD-1001".

    Returns:
        A dictionary containing the trade ID, execution status, account,
        security, side, quantity, and execution price.

    Example:
        get_trade_details("TRD-1001")
    """
    return {
        "trade_id": trade_id,
        "status": "EXECUTED",
        "account": "ACCT-78421",
        "security": "AAPL",
        "side": "BUY",
        "quantity": 100,
        "price": 189.50,
    }


@tool
def get_settlement_instructions(trade_id: str):
    """
    Retrieve settlement instructions associated with a trade.

    The tool provides the settlement account and expected settlement date.
    The trade pre-matching agent uses this information to compare the
    trade's settlement requirements against the counterparty instructions.

    Args:
        trade_id: Unique identifier of the trade, for example "TRD-1001".

    Returns:
        A dictionary containing the trade ID, settlement account, and
        settlement date.

    Example:
        get_settlement_instructions("TRD-1001")
    """
    return {
        "trade_id": trade_id,
        "settlement_account": "SETTLE-001",
        "settlement_date": "T+2",
    }


@tool
def pre_match_trade(trade_id: str):
    """
    Pre-match an executed trade against the available settlement data.

    This tool represents the downstream trade-matching service. It should
    only be invoked after the trade has been validated and the required
    trade and settlement information has been retrieved.

    Args:
        trade_id: Unique identifier of the trade to pre-match.

    Returns:
        A dictionary containing the trade ID and the resulting match status.

    Example:
        pre_match_trade("TRD-1001")
    """
    return {
        "trade_id": trade_id,
        "match_status": "MATCHED",
    }


@before_model
def pre_match_before_model(state, runtime):
    """
    Execute logic before the agent invokes the language model.

    This node-style hook can be used for activities such as request
    auditing, metrics collection, policy checks, and preparing contextual
    information required by the model.

    Args:
        state: Current agent state containing the conversation messages
            and other state information.
        runtime: LangChain runtime context for the current execution.

    Returns:
        None. The hook performs side effects such as logging or auditing.
    """
    print("=== BEFORE MODEL ===")
    print("Starting trade pre-match workflow")


@after_model
def pre_match_after_model(state, runtime):
    """
    Execute logic after the language model has completed an invocation.

    This node-style hook can be used for response auditing, metrics,
    observability, and recording model execution information.

    Args:
        state: Current agent state containing the conversation messages
            and model response.
        runtime: LangChain runtime context for the current execution.

    Returns:
        None. The hook performs post-model processing.
    """
    print("=== AFTER MODEL ===")
    print("Model completed pre-match reasoning")


@wrap_tool_call
def banking_tool_wrapper(request, handler):
    """
    Wrap every tool execution with banking-specific controls.

    This wrap-style middleware executes logic before and after the actual
    tool invocation. It can therefore be used to implement authorization,
    validation, retry, auditing, caching, transaction handling, and other
    execution controls.

    For the pre_match_trade tool, this wrapper verifies that the trade
    exists and has an EXECUTED status before allowing the actual tool
    invocation to proceed.

    Args:
        request: Tool-call request containing the selected tool name and
            its arguments.
        handler: Callable that executes the actual downstream tool call.

    Returns:
        The result returned by the downstream tool.

    Raises:
        ValueError: If a trade that is not in EXECUTED status is submitted
            for pre-matching.

    Example:
        The agent requests:

            pre_match_trade(trade_id="TRD-1001")

        The wrapper validates the trade before calling:

            handler(request)
    """

    tool_name = request.tool_call["name"]

    print(f"=== TOOL START: {tool_name} ===")

    # ---------------------------------
    # PRE-EXECUTION CONTROL
    # ---------------------------------

    if tool_name == "pre_match_trade":

        trade_id = request.tool_call["args"]["trade_id"]

        print(f"Validating {trade_id}")

        # In a production system this would normally
        # call a repository/service rather than the
        # LangChain tool directly.
        trade = get_trade_details.invoke(
            {"trade_id": trade_id}
        )

        if trade["status"] != "EXECUTED":
            raise ValueError(
                f"Trade {trade_id} cannot be pre-matched "
                f"because its status is {trade['status']}"
            )

    # ---------------------------------
    # ACTUAL TOOL EXECUTION
    # ---------------------------------

    result = handler(request)

    # ---------------------------------
    # POST-EXECUTION CONTROL
    # ---------------------------------

    print(f"=== TOOL END: {tool_name} ===")
    print("Result:", result)

    return result


agent = create_agent(
    model="gpt-5.5",
    tools=[
        get_trade_details,
        get_settlement_instructions,
        pre_match_trade,
    ],
    middleware=[
        pre_match_before_model,
        banking_tool_wrapper,
        pre_match_after_model,
    ],
)
```

## Invocation script

```python
def invoke_trade_pre_match_agent(trade_id: str):
    """
    Invoke the trade pre-matching agent for a specific trade.

    Args:
        trade_id: Unique identifier of the trade to pre-match.

    Returns:
        The final agent state containing the conversation and
        trade pre-matching result.
    """
    return agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Pre-match trade {trade_id}. "
                        "First check the trade details and "
                        "settlement instructions."
                    ),
                }
            ]
        }
    )


if __name__ == "__main__":

    result = invoke_trade_pre_match_agent(
        "TRD-1001"
    )

    print("\nFINAL RESULT")
    print(result)
```

### Important production distinction

Notice that the **tools themselves have business-level docstrings**:

```text
get_trade_details
    ↓
"What does this tool do?"

get_settlement_instructions
    ↓
"What does this tool do?"

pre_match_trade
    ↓
"What does this tool do?"
```

Whereas the **middleware docstrings describe execution control**:

```text
before_model
    ↓
"What should happen before the LLM node?"

after_model
    ↓
"What should happen after the LLM node?"

wrap_tool_call
    ↓
"How should tool execution be controlled?"
```

This distinction is particularly useful when you have dozens of banking tools: the **tool docstring helps the LLM select the right tool**, while the **middleware controls whether and how that selected tool is actually allowed to execute**.
