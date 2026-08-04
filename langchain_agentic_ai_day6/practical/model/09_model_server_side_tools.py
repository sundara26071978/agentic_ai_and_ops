"""
09_model_server_side_tools.py - Server-Side Tool Definitions

This example demonstrates:
1. Defining tools as dictionaries (server-side)
2. Binding server-defined tools to models
3. Differences from @tool decorator approach
4. Dynamic tool availability

Two Ways to Define Tools:
  1. @tool decorator (examples 04, 05)
     - For client-side tool definitions
     - Full function implementation required
     - Type hints included
  
  2. Dictionary format (this example)
     - For server-side tool definitions
     - Tool description in dictionary
     - Useful for dynamic/remote tools
     - Great for APIs that manage tools

Server-Side Tool Approach Benefits:
  - Tools defined on backend/server
  - Client doesn't implement logic
  - Dynamic tool loading
  - Restricted tool access control
  - Version control on server

Use Cases:
  - Microservices architecture
  - API gateways with tool management
  - Restricted tool access for users
  - Dynamic tool availability
  - SaaS platforms with tool marketplace

Resources:
  - Tool Calling: https://docs.langchain.com/oss/python/langchain/frontend/tool-calling
"""

import pprint
from langchain.chat_models import init_chat_model
import urllib.error
import urllib.request
import pprint
from langchain.tools import tool

import os

from dotenv import load_dotenv

load_dotenv("C:\\Users\\socgen\\ML\\agentic_ai_and_ops\\langchain_day5\\.env")


# Initialize model
# model = init_chat_model("ollama:qwen3.5:latest")
model_or_paid_gpt56_luna = init_chat_model("openai/gpt-5.6-luna",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=500, temperature=0.0)


# Define a tool as a dictionary (server-side)
# Format: {"type": "<tool_name>", "description": "<description>", ...}
tool = {"type": "web_search"}

# Bind server-defined tools to the model
model_with_tools = model_or_paid_gpt56_luna.bind_tools([tool])

# Ask the model something that might require web search
response = model_with_tools.invoke("What was a positive news story from today?")

# Display response content blocks
print("Response Content Blocks:")
print(response.content_blocks)

print("\n=== Debug Information ===")
pprint.pprint("Server-side tool configuration complete")

# Note: In a real application:
# 1. Model identifies it needs to call web_search
# 2. Returns tool_calls with search query
# 3. Server executes the actual web search
# 4. Results returned to model for final response