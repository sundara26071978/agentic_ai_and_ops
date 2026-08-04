"""
03_model_stream_by_blocktype.py - Advanced Streaming with Content Block Parsing

This example demonstrates:
1. Parsing different content block types during streaming
2. Handling reasoning/thinking blocks (advanced models only)
3. Detecting tool calls in streamed responses
4. Processing text tokens with context

Content Block Types:
  - "text": Regular response tokens
  - "reasoning": Thinking steps (DeepSeek-R1, Claude with extended thinking)
  - "tool_call_chunk": Function/tool call being made
  - "tool_result": Result from a tool execution

When to use:
  - Displaying reasoning steps to users
  - Handling tool calls in real-time
  - Building advanced debugging interfaces
  - Multi-modal response handling

Note: Reasoning blocks only available with DeepSeek-R1 or Claude models

Resources:
  - LangChain Streaming: https://docs.langchain.com/oss/python/langchain/models#streaming
"""

import pprint
from langchain.chat_models import init_chat_model

# Initialize model
model = init_chat_model("ollama:qwen3.5:latest")

# Stream and parse by content block type
for chunk in model.stream("What color is the sky?"):
    # Each chunk can contain multiple content blocks
    for block in chunk.content_blocks:
        # Handle reasoning/thinking blocks (advanced models)
        if block["type"] == "reasoning" and (reasoning := block.get("reasoning")):
            print(f"🤔 Reasoning: {reasoning}")
        
        # Handle tool call chunks
        elif block["type"] == "tool_call_chunk":
            print(f"🔧 Tool call chunk: {block}")
        
        # Handle regular text tokens
        elif block["type"] == "text":
            print(block["text"], end="", flush=True)
        
        # Handle other types (extend as needed)
        else:
            pass
        
