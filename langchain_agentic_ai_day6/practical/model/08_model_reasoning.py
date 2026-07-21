"""
08_model_reasoning.py - Extracting Extended Reasoning Steps

This example demonstrates:
1. Using models with explicit reasoning capabilities
2. Extracting reasoning/thinking blocks
3. Separating reasoning from final response
4. Advanced model introspection

Important: Reasoning Support
  - DeepSeek-R1: Native reasoning blocks ✓
  - Claude 3.5+: Extended thinking (requires API key)
  - Ollama Local Models: Most don't support reasoning ✗
  - Qwen, Gemma: Limited reasoning ✗

Setup:
  1. Install DeepSeek-R1: ollama pull deepseek-r1:7b
  2. Ensure Ollama is running: ollama serve
  3. Run this script

Output Structure:
  response.content_blocks contains multiple block types:
    - "reasoning": Thinking steps (what the model thought)
    - "text": Final answer
    - "tool_call": Function calls (if applicable)

Use Cases:
  - Show reasoning to users for transparency
  - Educational applications
  - Debugging model behavior
  - Validating model logic
  - Building explainable AI systems

Resources:
  - DeepSeek-R1: https://ollama.ai/library/deepseek-r1
  - Extended Thinking: https://docs.langchain.com/oss/python/langchain/models
"""

import pprint
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

# Initialize DeepSeek-R1 model which supports reasoning
# Prerequisites: ollama pull deepseek-r1:7b
model = init_chat_model("ollama:deepseek-r1:latest")

# Invoke the model
response = model.invoke("Why do parrots have colorful feathers?")

# Extract reasoning blocks
# Reasoning blocks contain the model's thinking process
reasoning_steps = [b for b in response.content_blocks if b["type"] == "reasoning"]

print("=== REASONING STEPS ===")
print(" ".join(step["reasoning"] for step in reasoning_steps))

print("\n=== DEBUG: All Content Blocks ===")
pprint.pprint(response.content_blocks)

# Extract the final answer (text blocks)
print("\n=== FINAL ANSWER ===")
text_blocks = [b for b in response.content_blocks if b["type"] == "text"]
for block in text_blocks:
    print(block.get("text", ""))  