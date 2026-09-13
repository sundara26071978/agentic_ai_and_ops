"""

Write short-term memory from tools
To modify the agent’s short-term memory (state) during execution, you can return state updates directly from the tools.
This is useful for persisting intermediate results or making information accessible to subsequent tools or prompts.

"""


from langchain.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime
from langchain.messages import HumanMessage



import os

import pprint
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from rich import print as rprint
from dotenv import load_dotenv

load_dotenv()

model_advanced = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)



@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]
    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    return None

agent = create_agent(
    model=model_advanced,
    tools=[],
    middleware=[validate_response],
    checkpointer=InMemorySaver(),
)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "agent-thread-1"}}

    response = agent.invoke(
        {"messages": [HumanMessage(content="Hello, my password is 1234")]},
        config=config,
    )

    rprint(response)

    response = agent.invoke(
    {"messages": [HumanMessage(content="What did I just say?")]},
    config=config,
)

    print(response)