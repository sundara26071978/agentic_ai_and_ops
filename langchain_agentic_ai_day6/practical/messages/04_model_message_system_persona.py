"""System Message with Detailed Persona Example

Demonstrates how to use SystemMessage objects to define detailed model behavior
and persona. The system message primes the model with specific instructions,
role definition, and behavioral guidelines.

Best Practices:
- Use clear, specific instructions in system messages
- Define the model's role and expertise
- Provide guidelines for response format and tone
- Multi-line messages can contain detailed instructions

Prerequisite: Ollama must be running with deepseek-coder model installed
"""
import pprint

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

# Initialize the chat model using Ollama with deepseek-coder
# This model is optimized for code generation and technical explanations
model = init_chat_model("ollama:deepseek-coder:6.7b")

# Simple system message (basic example)
simple_system_msg = SystemMessage("You are a helpful coding assistant.")

# Detailed system message (recommended approach)
# This comprehensive persona gives the model clear direction on behavior
detailed_system_msg = SystemMessage("""
You are a senior Python developer with expertise in web frameworks.
Always provide code examples and explain your reasoning.
Be concise but thorough in your explanations.
""")

# Use the detailed system message in the message list
messages = [
    detailed_system_msg,  # System instruction to prime behavior
    HumanMessage("How do I create a REST API?")  # User query
]

# Invoke model with system message and user query
response = model.invoke(messages)

# Extract and print the text content from the AIMessage response
pprint.pprint(response.content)

print("✓ System persona-based invocation completed.")