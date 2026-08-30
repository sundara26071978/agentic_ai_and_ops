from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

from langchain.tools import tool
from rich import print as rprint
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing import Literal

import os

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


def your_read_email_tool(email_id: str) -> str:
    """Mock function to read an email by its ID."""
    return f"Email content for ID: {email_id}"

def your_send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Mock function to send an email."""
    return f"Email sent to {recipient} with subject '{subject}'"

agent = create_agent(
    model=model_advanced,
    tools=[your_read_email_tool, your_send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "your_send_email_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "your_read_email_tool": False,
            }
        ),
    ],
)

# 1. Test read_email — should NOT trigger HITL
# config = {
#     "configurable": {
#         "thread_id": "hitl-test-1"
#     }
# }

# result = agent.invoke(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": "Read email with ID EMAIL-123"
#             }
#         ]
#     },
#     config=config
# )

# rprint(result)

# 2. Test send_email — should trigger HITL
config = {
    "configurable": {
        "thread_id": "hitl-test-2"
    }
}

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": """
Send an email to trader@example.com.

Subject: Trade Confirmation

Body: Please confirm the trade details.
"""
            }
        ]
    },
    config=config
)

rprint(result)
# 3. Inspect the interrupt
rprint("-" * 50)
rprint("3. Inspect the interrupt")
rprint(result.get("__interrupt__"))

for message in result["messages"]:
    rprint(type(message).__name__)
    rprint(message)
    rprint("-" * 50)

# # 4. Approve the email
# print("-" * 80)
# rprint("4. Approve the email")
# from langgraph.types import Command
# result = agent.invoke(
#     Command(
#         resume={
#             "decisions": [
#                 {
#                     "type": "approve"
#                 }
#             ]
#         }
#     ),
#     config=config
# )

# rprint(result)

# print("-" * 80)


# 4. Reject the email
print("-" * 80)
rprint("4. Reject the email")
from langgraph.types import Command
result = agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "reject"
                }
            ]
        }
    ),
    config=config
)

rprint(result)

print("-" * 80)