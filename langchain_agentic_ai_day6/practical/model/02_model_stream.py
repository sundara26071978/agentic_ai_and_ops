"""
02_model_stream.py - Streaming Model Responses

This example demonstrates:
1. Streaming responses token-by-token
2. Real-time display of model output
3. Flushing output immediately for live feedback
4. Better UX for long-form responses

Key Difference from invoke():
  - invoke(): Wait for complete response (blocking)
  - stream(): Get tokens as they're generated (streaming)

Use stream() when:
  - User expects immediate feedback
  - Response is long (articles, code, etc.)
  - Building real-time chatbot UIs
  - Network latency is a concern

Resources:
  - LangChain Streaming: https://docs.langchain.com/oss/python/langchain/models#streaming
"""

import pprint
from langchain.chat_models import init_chat_model

# Initialize model with Ollama backend
model = init_chat_model("ollama:gemma4:latest", max_tokens=200, temperature=0.0)

# Stream responses token-by-token
# Each chunk is a partial response that arrives in real-time
for chunk in model.stream("write a short poem about agentic AI systems in less than 50 words"):
    # chunk.text contains the token text
    # end="|" shows token boundaries
    # flush=True sends output immediately instead of buffering
    print(chunk.text, end="|", flush=True)
