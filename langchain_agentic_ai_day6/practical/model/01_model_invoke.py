"""
01_model_invoke.py - Basic Model Invocation & Multi-Turn Conversations

This example demonstrates:
1. Initializing a chat model with Ollama
2. Simple single-turn model invocation
3. Multi-turn conversations with message history
4. Maintaining conversation context

Prerequisites:
  - Ollama running locally
  - Model available: ollama pull qwen3.5

Resources:
  - LangChain Models: https://docs.langchain.com/oss/python/langchain/models
  - Ollama Integration: https://docs.langchain.com/oss/python/integrations/providers/ollama
"""

import pprint
from langchain.chat_models import init_chat_model

# Initialize the model with Ollama backend
# Format: "ollama:<model_name>:<tag>"
# Available models: qwen3.5, gemma4, deepseek-r1, llama2, etc.

# model = init_chat_model("ollama:qwen3.5:latest")
# model = init_chat_model("ollama:chevalblanc/gpt-4o-mini:latest")
model = init_chat_model("openrouter:openrouter/free")

# Example 1: Simple single-turn invocation
# response = model.invoke("Why do parrots talk?")
# pprint.pprint(response)

# Example 2: Multi-turn conversation with message history
# This demonstrates how to maintain conversation context
conversation = [
    # System message: Sets the assistant's behavior
    {"role": "system", "content": "You are a helpful assistant that translates English to Tamil."},
    
    # First exchange
    {"role": "user", "content": "Translate: I love programming."},
    {"role": "assistant", "content": "நான் நிரலாக்கத்தை விரும்புகிறேன்"},
    
    # Follow-up: Model uses context from previous messages
    {"role": "user", "content": "Translate: I love building agentic AI systems."}
]

# Expected output in Tamil (comment shows translation):
# நான் பயன்பாடுகளை உருவாக்குவதை விரும்புகிறேன்.

# Send conversation history to model
# The model understands the pattern and context
response = model.invoke(conversation)
print(response)  # AIMessage with the translation
print("✓ Multi-turn conversation completed.")