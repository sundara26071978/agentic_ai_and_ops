"""
LangChain Agent Example: Structured Output - Tool Strategy

This example demonstrates:
- Extracting structured data from unstructured input
- Using Pydantic models to define output schema
- ToolStrategy for structured output (tool-based approach)
- Validating and parsing agent responses

Structured output ensures that agent responses conform to a
predefined schema, enabling reliable downstream processing.
"""
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
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
model = ChatOllama(model="qwen3.5:latest ")

# Create agent with structured output using ToolStrategy
# ToolStrategy uses a tool to ensure structured output
agent = create_agent(
    model=model,
    response_format=ToolStrategy(ContactInfo)  # Enforce structured output schema
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