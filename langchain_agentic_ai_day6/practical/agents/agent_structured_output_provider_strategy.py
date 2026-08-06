"""
LangChain Agent Example: Structured Output - Provider Strategy

This example demonstrates:
- Extracting structured data using provider-native capabilities
- ProviderStrategy for structured output (provider-native approach)
- Model-specific structured output methods
- Advantages over tool-based approach for some providers

ProviderStrategy uses the underlying model provider's structured
output capabilities (like JSON mode), which may be more efficient
than the tool-based approach.
"""
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
import pprint


# Define the output schema using Pydantic
class ContactInfo(BaseModel):
    """Structured contact information.
    
    Attributes:
        name: The person's full name
        email: The person's email address
        phone: The person's phone number
    """
    name: str
    email: str
    phone: str


# Initialize the model
model = ChatOllama(model="qwen3.5:latest")

# Create agent with structured output using ProviderStrategy
# ProviderStrategy uses the model provider's native structured output capabilities
agent = create_agent(
    model=model,
    response_format=ProviderStrategy(ContactInfo)  # Use provider-native structured output
)

# Invoke the agent with an extraction task
# The agent will extract contact information and return it as a ContactInfo object
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Extract contact info from: John Doe, john@example.com, (555) 123-4567"
    }]
})

# Pretty print the structured response
# result["structured_response"] contains the ContactInfo object
pprint.pprint(result["structured_response"])

# Output: ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')