"""
05_model_toolcalling_execution.py - End-to-End Tool Execution Loop

This example demonstrates:
1. Complete 3-step tool calling workflow
2. Model generating tool calls
3. Executing tools with provided arguments
4. Feeding results back to model for final response

The Three-Step Loop:
  Step 1: Model decides to call tool(s) → returns tool_calls
  Step 2: Execute each tool and collect results
  Step 3: Pass results back to model for final answer

This is the foundation of:
  - Autonomous agents
  - Multi-step reasoning
  - Real-world problem solving
  - Production agent loops

Key Points:
  - Messages accumulate in the loop
  - Tool results are added to message history
  - Model can make multiple tool calls per step
  - Loop continues until model returns final response (no tool_calls)

Resources:
  - Tool Calling: https://docs.langchain.com/oss/python/langchain/frontend/tool-calling
  - Agent Pattern: https://docs.langchain.com/oss/python/langchain/agents
"""

import pprint
from langchain.chat_models import init_chat_model
from langchain.tools import tool

# Define a tool
@tool
def get_weather(location: str) -> str:
    """Get the weather at a location."""
    return f"It's sunny in {location}."

# Initialize model with tools
model = init_chat_model("ollama:qwen3.5:latest")
model_with_tools = model.bind_tools([get_weather])

# ============================================
# STEP 1: Model generates tool calls
# ============================================
print("\n=== STEP 1: Model generates tool calls ===")
messages = [{"role": "user", "content": "What's the weather in Boston and Tokyo?"}]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)  # Add model's response to history

pprint.pprint("Messages after Step 1:")
pprint.pprint(messages)

# ============================================
# STEP 2: Execute tools and collect results
# ============================================
print("\n=== STEP 2: Execute tools and collect results ===")
for tool_call in ai_msg.tool_calls:
    print(f"\nExecuting: {tool_call['name']}({tool_call['args']})")
    # Execute the tool with the arguments provided by the model
    tool_result = get_weather.invoke(tool_call)
    print(f"Result: {tool_result}")
    
    # Add tool result to message history
    messages.append(tool_result)

pprint.pprint("\nMessages after Step 2:")
pprint.pprint(messages)

# ============================================
# STEP 3: Pass results back to model
# ============================================
print("\n=== STEP 3: Pass results back to model ===")
final_response = model_with_tools.invoke(messages)

print(f"\nFinal Response:")
pprint.pprint(final_response.text)

print("\n💡 The model now has context from tool execution and can provide a final answer!")
