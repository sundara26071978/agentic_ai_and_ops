"""
Custom middleware
Hooks

Middleware provides two styles of hooks to intercept agent execution:

Node-style hooks
Run sequentially at specific execution points. Use for logging, validation, and state updates.
Choose the hooks your middleware needs. You can choose between node-style hooks and wrap-style hooks.
Node-style hooks run at specific execution points:

Hook	When it runs
before_agent	Before agent starts (once per invocation)
before_model	Before each model call
after_model	After each model response
after_agent	After agent completes (once per invocation)

Wrap-style hooks run around each call, giving you control over execution:
Hook	When it runs
wrap_model_call	Around each model call
wrap_tool_call	Around each tool call

"""
import os

from langchain.agents import create_agent
from rich import print as rprint
from langchain.chat_models import init_chat_model

from langchain.agents.middleware import (
    before_model,
    after_model,
    wrap_tool_call,
    AgentState,
    ModelRequest,
    ModelResponse,

)

from typing import Callable
from langgraph.runtime import Runtime
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
def pre_match_before_model(state : AgentState, runtime: Runtime):
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

    # Audit / metrics / context checks
    print(
        "Starting trade pre-match workflow"
    )


@after_model
def pre_match_after_model(state : AgentState, runtime: Runtime):
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

    # Record model completion
    print(
        "Model completed pre-match reasoning"
    )


@wrap_tool_call
def banking_tool_wrapper(request : ModelRequest, handler: Callable[[ModelRequest],ModelResponse]):
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



# ---------------------------------------------------------
# 2. Create agent
# ---------------------------------------------------------


agent = create_agent(
    model=model_advanced,

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


# ---------------------------------------------------------
# 3. Invoke agent
# ---------------------------------------------------------


def invoke_agent(): 

    print("\n" + "=" * 70)
    print("USER REQUEST")
    print("=" * 70)

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
    },config={
            "run_name": "Custom Middleware",      # Custom name for this run
            "tags": ["custommiddleware", "before_model","after_model","wrap_tool_call"],          # Tags for categorization
            "metadata": {"user_id": "sunjcustommiddleware"},     # Custom metadata
        
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
    result= invoke_agent()
    rprint(result)

