import pprint
from typing import Any
from typing_extensions import Annotated, TypedDict
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain_core.messages import HumanMessage, ToolMessage, BaseMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langgraph.graph.message import add_messages


# ============================================================================
# Custom State with user preferences
# ============================================================================
class AgentState(TypedDict):
    """Custom agent state with messages and user preferences."""
    messages: Annotated[list[BaseMessage], add_messages]
    user_preferences: dict[str, Any]

# ============================================================================
# Define tools that access runtime state
# ============================================================================

@tool
def get_last_user_message(runtime: ToolRuntime) -> str:
    """Get the most recent message from the user."""
    messages = runtime.state["messages"]

    # Find the last human message
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message.content

    return "No user messages found"


@tool
def get_user_preference(pref_name: str, runtime: ToolRuntime) -> str:
    """Get a user preference value."""
    preferences = runtime.state.get("user_preferences", {})
    return preferences.get(pref_name, "Not set")


@tool
def set_user_preference(pref_name: str, pref_value: str, runtime: ToolRuntime) -> Command:
    """Set a user preference value."""
    # Get current preferences or create new dict
    preferences = runtime.state.get("user_preferences", {})
    preferences[pref_name] = pref_value
    
    return Command(
        update={
            "user_preferences": preferences,
            "messages": [
                ToolMessage(
                    content=f"User preference '{pref_name}' set to '{pref_value}'.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# ============================================================================
# Create LangGraph Agent with state management
# ============================================================================

def process_tool_calls(state: AgentState):
    """LLM node that processes messages and calls tools."""
    model = init_chat_model("ollama:gemma4:latest")
    model_with_tools = model.bind_tools([
        get_last_user_message, 
        get_user_preference, 
        set_user_preference
    ])
    
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}


# Create the StateGraph
builder = StateGraph(AgentState)

# Add the LLM node
builder.add_node("llm", process_tool_calls)

# Add the ToolNode - this is where runtime state gets injected!
tool_node = ToolNode([
    get_last_user_message, 
    get_user_preference, 
    set_user_preference
])
builder.add_node("tools", tool_node)

# Add edges
builder.add_edge(START, "llm")

# Conditional routing: if the model called tools, go to tools node, else END
def should_continue(state: AgentState):
    """Route to tools if there are tool calls, otherwise end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools"
    return END


builder.add_conditional_edges("llm", should_continue)
builder.add_edge("tools", "llm")

graph = builder.compile()

# ============================================================================
# Invoke the agent with custom state
# ============================================================================

if __name__ == "__main__":
    # Create initial state with custom fields
    initial_state: AgentState = {
        "messages": [
            HumanMessage(content="What's my favorite color preference?")
        ],
        "user_preferences": {
            "favorite_color": "blue",
            "theme": "dark",
            "language": "english"
        }
    }

    print("=" * 70)
    print("INVOKING AGENT WITH STATE ACCESS")
    print("=" * 70)
    print(f"\nInitial State: {initial_state}\n")

    try:
        # Run the graph with recursion limit to prevent infinite loops
        result = graph.invoke(initial_state, {"recursion_limit": 10})

        print("\n" + "=" * 70)
        print("FINAL STATE")
        print("=" * 70)
        pprint.pprint(result)

        print("\n" + "=" * 70)
        print("CONVERSATION TRACE")
        print("=" * 70)
        for i, msg in enumerate(result["messages"]):
            print(f"\n[{i}] {msg.__class__.__name__}:")
            if hasattr(msg, 'content') and msg.content:
                print(f"    Content: {msg.content}")
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"    Tool Calls: {msg.tool_calls}")
            if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                print(f"    Tool Call ID: {msg.tool_call_id}")

        print("\n" + "=" * 70)
        print("FINAL USER PREFERENCES")
        print("=" * 70)
        pprint.pprint(result.get("user_preferences", {}))

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()



