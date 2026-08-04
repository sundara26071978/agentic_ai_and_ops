"""
06_model_structured_output_pydantic.py - Simple Structured Output

This example demonstrates:
1. Defining output schemas with Pydantic models
2. Enforcing structured responses from the model
3. Using Field descriptions for guidance
4. Type-safe data extraction

Key Concepts:
  - Pydantic Model: Defines the expected output structure
  - with_structured_output(): Forces model to return this structure
  - Field: Defines field properties and descriptions
  - Type Safety: Guarantees output matches the schema

Benefits:
  - No manual JSON parsing
  - Type hints for IDE support
  - Validation built-in
  - Error handling for invalid outputs
  - Chain outputs directly to downstream tasks

When to use:
  - Data extraction from text
  - Form filling
  - Consistent API responses
  - Database record generation
  - Type-safe pipelines

Resources:
  - Structured Output: https://docs.langchain.com/oss/python/langchain/structured-output
  - Pydantic: https://docs.pydantic.dev
"""

import pprint
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

# Initialize model
model = init_chat_model("ollama:qwen3.5:latest")

# Define the output structure using Pydantic
class Movie(BaseModel):
    """A movie with details."""
    # Each field has a type and optional description
    # The description helps the model understand what to extract
    title: str = Field(description="The title of the movie")
    year: int = Field(description="The year the movie was released")
    director: str = Field(description="The director of the movie")
    rating: float = Field(description="The movie's rating out of 10")

# Enable structured output
# The model will now return a Movie instance instead of text
model_with_structure = model.with_structured_output(Movie)

# Invoke the model
response = model_with_structure.invoke("Provide details about the movie Inception")

print(response)
# Output: Movie(title="Inception", year=2010, director="Christopher Nolan", rating=8.8)

# Now you can access fields directly
print(f"\nMovie: {response.title}")
print(f"Year: {response.year}")
print(f"Director: {response.director}")
print(f"Rating: {response.rating}/10")