"""
07_model_structured_output_pydantic_nestedobject.py - Complex Nested Structures

This example demonstrates:
1. Nested Pydantic models for complex data
2. List fields with typed elements
3. Optional fields with default values
4. Hierarchical data extraction

Key Concepts:
  - Nested Models: Models containing other models
  - List Typing: list[ModelType] for arrays of objects
  - Optional Fields: Using | None for optional data
  - Defaults: Field(..., default=None) for optional values

When to use:
  - Complex object extraction (movies with cast lists)
  - Hierarchical data (companies with departments)
  - Database record creation (with relationships)
  - API response generation
  - Multi-level data parsing

Example Use Cases:
  - Extract movie details with full cast lists
  - Parse user profiles with activity history
  - Generate product catalogs with nested attributes
  - Extract organizational hierarchies

Resources:
  - Structured Output: https://docs.langchain.com/oss/python/langchain/structured-output
  - Pydantic Complex Models: https://docs.pydantic.dev/latest/api/types/
"""

import pprint
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

# Initialize model (using gemma4 for lighter resource usage)
model = init_chat_model("ollama:gemma4:latest")

# Define nested models
# Actor is a sub-model used inside MovieDetails
class Actor(BaseModel):
    name: str
    role: str

# Main model with nested structure
class MovieDetails(BaseModel):
    title: str
    year: int
    # list[Actor] = array of Actor objects (nested models)
    cast: list[Actor]
    # list[str] = array of strings
    genres: list[str]
    # Optional field with default value
    # budget: float | None means it can be float or None
    budget: float | None = Field(None, description="Budget in millions USD")

# Enable structured output
model_with_structure = model.with_structured_output(MovieDetails)

# Invoke the model
response = model_with_structure.invoke("Provide details about the movie Inception")

print("Movie Details:")
print(response)
# Output: MovieDetails(title="Inception", year=2010, cast=[...], genres=[...], budget=...)

# Access nested data
print(f"\nTitle: {response.title}")
print(f"Year: {response.year}")
print(f"Genres: {', '.join(response.genres)}")

if response.cast:
    print(f"\nCast:")
    for actor in response.cast:
        print(f"  - {actor.name} as {actor.role}")

if response.budget:
    print(f"\nBudget: ${response.budget}M")
