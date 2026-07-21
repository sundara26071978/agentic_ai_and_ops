"""Dictionary Format Messages Example

Demonstrates using OpenAI chat completions format (dictionary format)
for messages instead of LangChain message objects.
LangChain automatically converts these dictionaries to message objects internally.

Dictionary Format Specification:
- role: One of "system", "user", or "assistant"
- content: The message text content

Note: While this format works, using message objects is recommended for better
type safety and IDE support.

Prerequisite: Ollama must be running with qwen model installed
"""
import pprint

from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage, SystemMessage

# Initialize the chat model using Ollama
model = init_chat_model("ollama:qwen3.5:latest")

# Alternative using message objects (commented out):
# sys_msg = SystemMessage(content="You are a helpful assistant that translates English to Tamil.")
# human_msg = HumanMessage(content="Translate: I love my mom and dad.")
# messages = [sys_msg, human_msg]

# Create messages using OpenAI chat completions format (dictionaries)
# LangChain automatically converts these to internal message objects
messages = [
    {"role": "system", "content": "You are a poetry expert"},  # System instruction
    {"role": "user", "content": "Write a haiku about AI"},  # User query
    {"role": "assistant", "content": "Cherry Blossoms bloom..."}  # Prior AI response
]

# Invoke model with dictionary-format messages
response = model.invoke(messages)

# Print the resulting AIMessage object
pprint.pprint(response)

print("✓ Dictionary-format messages invocation completed.")