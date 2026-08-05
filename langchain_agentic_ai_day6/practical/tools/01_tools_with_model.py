"""
01_tools_with_model.py - Basic Tool Definition and Binding

This example demonstrates:
✅ Creating tools with the @tool decorator
✅ Using function docstrings as tool descriptions
✅ Type hints for automatic schema generation
✅ Binding tools to a language model
✅ Invoking the model to call tools
✅ Extracting tool calls from model responses

Prerequisites:
- Ollama running locally (ollama serve)
- ollama pull qwen3.5:latest (or gemma4:latest)

Message Flow:
1. HumanMessage: User asks a question
2. AIMessage: Model recognizes need to call a tool
3. ToolMessage: Tool result is returned (handled internally)
4. AIMessage: Model provides final response

Reference: https://docs.langchain.com/oss/python/langchain/tools
"""

from langchain.tools import tool
import pprint
from langchain.chat_models import init_chat_model

import pprint
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

import os

from dotenv import load_dotenv

load_dotenv("C:\\Users\\socgen\\ML\\agentic_ai_and_ops\\langchain_day5\\.env")

# ============================================================================
# Define Tools Using @tool Decorator
# ============================================================================

@tool
def search_database(query: str, limit: int = 10) -> str:
    """Search the customer database for records matching the query.

    The docstring above becomes the tool's description that helps the model
    understand when and how to use this tool.

    Args:
        query: Search terms to look for in the database
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        String with search results
    """
    return f"Found {limit} results for '{query}'"

@tool("web_search")  # Custom name - override the function name
def search(query: str) -> str:
    """Search the web for information.
    
    Note: The tool name is "web_search" (custom), not the function name "search".
    The function name is only used as a fallback if no custom name is provided.
    
    Args:
        query: Terms to search for on the web
    
    Returns:
        String with search results
    """
    return f"Results for: {query}"


# ============================================================================
# Initialize Model and Bind Tools
# ============================================================================

# Initialize the model with Ollama backend
# Make sure ollama serve is running before executing this
model = init_chat_model("ollama:qwen3.5:latest")

model_gr_lamma = init_chat_model("llama-3.3-70b-versatile",
                        api_key=os.environ["GROQ_API_KEY"],
                        model_provider="groq",
                        # base_url="https://api.groq.com/openai/v1",
                        max_tokens=1000, temperature=0.0)

# Bind tools to the model - the model now "knows" about these tools
# The model will only call tools when it determines the user request requires it
model_with_tools = model_gr_lamma.bind_tools([search_database, search])


# ============================================================================
# Invoke Model and Process Tool Calls
# ============================================================================

# Ask the model something that requires tool calling
# The model will recognize it needs to call search_database
print("=" * 70)
print("EXAMPLE: Asking model to search for customers")
print("=" * 70)

response = model_with_tools.invoke("Search for customers named John Doe")

# Display the model's response
print("\n📝 Model Response Content:")
pprint.pprint(response.content)

# Extract and display tool calls made by the model
print("\n🔧 Tool Calls Made by Model:")
if response.tool_calls:
    for tool_call in response.tool_calls:
        print(f"  📞 Tool Name: {tool_call['name']}")
        print(f"     Arguments: {tool_call['args']}")
else:
    print("  (No tool calls were made)")

# Display the custom tool name
print(f"\n✨ Custom Tool Name: {search.name}")  # Output: web_search


