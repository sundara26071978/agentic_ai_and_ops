"""
Access the store inside nodes
Once you compile a graph with a store, LangGraph automatically injects the store 
into your node functions. 
The recommended way to access the store is through the Runtime object.
"""

from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict, NotRequired
from langchain_core.utils.uuid import uuid7
from dataclasses import dataclass
from langgraph.runtime import Runtime
from langgraph.graph import StateGraph, MessagesState, START
import uuid
import pprint

from langchain.chat_models import init_chat_model
from rich import print as rprint
import os
from dotenv import load_dotenv


load_dotenv()

model_advanced = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)


@dataclass
class Context:
    user_id: str

async def call_model(state: MessagesState, runtime: Runtime[Context]):
    user_id = runtime.context.user_id  
    namespace = (user_id, "memories")

    # Search for relevant memories
    memories = await runtime.store.asearch(
        namespace, query=state["messages"][-1].content, limit=3
    )
    info = "\n".join([d.value["data"] for d in memories])

    # ... Use memories in model call

    # Store a new memory
    await runtime.store.aput(
        namespace, str(uuid.uuid4()), {"data": "User prefers dark mode"}
    )

builder = StateGraph(MessagesState, context_schema=Context)
builder.add_node(call_model)
builder.add_edge(START, "call_model")
graph = builder.compile(store=store)

# Pass context at invocation time
graph.invoke(
    {"messages": [{"role": "user", "content": "hi"}]},
    {"configurable": {"thread_id": "1"}},
    context=Context(user_id="1"),
)