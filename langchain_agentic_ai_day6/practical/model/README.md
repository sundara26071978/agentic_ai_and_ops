# LangChain Model Examples with Ollama

This folder contains comprehensive examples demonstrating LangChain's model capabilities using **Ollama** as the local AI provider. Learn everything from basic model invocation to advanced features like tool calling and structured outputs.

## 📋 Prerequisites

### Required
1. **Ollama** - Local LLM runtime
   - Download from: https://ollama.ai
   - Ensure Ollama is running: `ollama serve`

2. **Python 3.9+** with LangChain
   ```bash
   pip install langchain langchain-ollama pydantic
   ```

### Recommended Models
- **Qwen 3.5** (Balanced, ~4GB) - Best for most examples
  ```bash
  ollama pull qwen3.5
  ```
- **Gemma 4** (Lightweight, ~2.5GB) - Good for structured outputs
  ```bash
  ollama pull gemma4
  ```
- **DeepSeek-R1** (Advanced reasoning, ~15GB) - For reasoning examples
  ```bash
  ollama pull deepseek-r1:7b
  ```

### LangChain Documentation
- [Ollama Integration](https://docs.langchain.com/oss/python/integrations/providers/ollama)
- [Chat Models](https://docs.langchain.com/oss/python/langchain/models)
- [Tool Calling](https://docs.langchain.com/oss/python/langchain/frontend/tool-calling)
- [Structured Output](https://docs.langchain.com/oss/python/langchain/structured-output)

---

## 📚 Examples Overview

### 1. **01_model_invoke.py** - Basic Model Invocation
**What it teaches:** Basic model interaction and conversation history

```bash
uv run 01_model_invoke.py
```

**Key Concepts:**
- Using `init_chat_model()` for model initialization
- Sending messages and receiving responses
- Multi-turn conversations with message history
- Working with Pydantic models for data validation

**Example Use Case:** Translation tasks, basic Q&A, conversation memory

---

### 2. **02_model_stream.py** - Streaming Responses
**What it teaches:** Real-time token streaming for faster feedback

```bash
uv run 02_model_stream.py
```

**Key Concepts:**
- Streaming responses token-by-token
- Real-time display of model output
- Better UX for long responses
- Flushing output immediately

**Example Use Case:** Chatbots, live response display, long-form text generation

---

### 3. **03_model_stream_by_blocktype.py** - Advanced Streaming
**What it teaches:** Parsing different content block types during streaming

```bash
uv run 03_model_stream_by_blocktype.py
```

**Key Concepts:**
- Identifying content block types (text, reasoning, tool calls)
- Handling different response components separately
- Processing reasoning steps from advanced models
- Conditional streaming based on content type

**Example Use Case:** Displaying reasoning steps, handling tool calls, multi-modal responses

---

### 4. **04_model_toolcalling.py** - Tool Binding (Model-Side)
**What it teaches:** Binding tools to models and analyzing tool calls

```bash
uv run 04_model_toolcalling.py
```

**Key Concepts:**
- Creating tools with `@tool` decorator
- Binding tools to models with `bind_tools()`
- Extracting tool calls from model responses
- Tool call arguments and execution planning

**Example Use Case:** API integrations, function calling, agent scaffolding

---

### 5. **05_model_toolcalling_execution.py** - End-to-End Tool Execution
**What it teaches:** Complete tool calling loop with result feedback

```bash
uv run 05_model_toolcalling_execution.py
```

**Key Concepts:**
- Step 1: Model generates tool calls
- Step 2: Execute tools with provided arguments
- Step 3: Return results to model for final response
- Iterative refinement with tool results

**Example Use Case:** Autonomous agents, multi-step reasoning, real-world problem solving

---

### 6. **06_model_structured_output_pydantic.py** - Simple Structured Output
**What it teaches:** Enforcing output structure with Pydantic models

```bash
uv run 06_model_structured_output_pydantic.py
```

**Key Concepts:**
- Defining Pydantic models for output schemas
- Using `with_structured_output()` for type safety
- Field descriptions for better model guidance
- Guaranteed structured JSON responses

**Example Use Case:** Data extraction, form filling, consistent API responses

---

### 7. **07_model_structured_output_pydantic_nestedobject.py** - Complex Nested Structures
**What it teaches:** Handling complex, nested structured outputs

```bash
uv run 07_model_structured_output_pydantic_nestedobject.py
```

**Key Concepts:**
- Nested Pydantic models
- List fields with type constraints
- Optional fields with defaults
- Complex data parsing

**Example Use Case:** Movie databases, user profiles, hierarchical data extraction

---

### 8. **08_model_reasoning.py** - Extended Reasoning (DeepSeek-R1)
**What it teaches:** Extracting explicit reasoning steps from advanced models

```bash
uv run 08_model_reasoning.py
```

**Prerequisites:** Requires DeepSeek-R1 model for reasoning blocks
```bash
ollama pull deepseek-r1:7b
```

**Key Concepts:**
- Reasoning/thinking block extraction
- Content block parsing for different types
- Advanced models with explicit thought process
- Debugging with `content_blocks`

**Example Use Case:** Complex problem solving, showing work, educational applications

---

### 9. **09_model_server_side_tools.py** - Server-Side Tool Definitions
**What it teaches:** Defining tools on the server that the model can call

```bash
uv run 09_model_server_side_tools.py
```

**Key Concepts:**
- Tool dictionaries for server-side definitions
- Model recognition of server-provided tools
- Dynamic tool availability
- Server-driven tool execution

**Example Use Case:** API gateways, restricted tool access, server-managed capabilities

---

## 🔄 Learning Path

### Beginner
1. Start with `01_model_invoke.py` - Understand basic model interaction
2. Explore `02_model_stream.py` - See real-time responses
3. Try `06_model_structured_output_pydantic.py` - Get predictable outputs

### Intermediate
4. Learn `04_model_toolcalling.py` - Connect models to functions
5. Master `05_model_toolcalling_execution.py` - Build autonomous loops
6. Practice `03_model_stream_by_blocktype.py` - Advanced parsing

### Advanced
7. Study `07_model_structured_output_pydantic_nestedobject.py` - Complex data
8. Explore `08_model_reasoning.py` - Extract thinking steps
9. Implement `09_model_server_side_tools.py` - Production patterns

---

## 🚀 Quick Reference

### Model Initialization
```python
from langchain.chat_models import init_chat_model

# Local model via Ollama
model = init_chat_model("ollama:qwen3.5:latest")

# Alternative models
model = init_chat_model("ollama:gemma4:latest")
model = init_chat_model("ollama:deepseek-r1:7b")
```

### Common Patterns

#### Invoke (Wait for complete response)
```python
response = model.invoke("Your question here")
print(response.content)
```

#### Stream (Real-time tokens)
```python
for chunk in model.stream("Your question here"):
    print(chunk.text, end="", flush=True)
```

#### With Tools
```python
from langchain.tools import tool

@tool
def my_tool(arg: str) -> str:
    """Tool description."""
    return f"Result: {arg}"

model_with_tools = model.bind_tools([my_tool])
response = model_with_tools.invoke("Use my_tool with foo")
```

#### Structured Output
```python
from pydantic import BaseModel, Field

class OutputSchema(BaseModel):
    field1: str = Field(description="Description")
    field2: int = Field(description="Description")

model_structured = model.with_structured_output(OutputSchema)
result = model_structured.invoke("Extract data")
```

---

## 📊 Model Comparison

| Feature | Qwen 3.5 | Gemma 4 | DeepSeek-R1 |
|---------|----------|---------|------------|
| Size | ~4GB | ~2.5GB | ~15GB |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| Quality | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Reasoning | ✓ | ✗ | ✓ |
| Tool Calling | ✓ | ✓ | ✓ |
| Structured Output | ✓ | ✓ | ✓ |

---

## 🔧 Troubleshooting

### "Connection refused" error
```bash
# Ensure Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

### Model not found
```bash
# List available models
ollama list

# Pull a model
ollama pull qwen3.5
```

### Out of memory
- Use smaller models: `gemma4` (2.5GB) instead of `deepseek-r1` (15GB)
- Reduce context window in system prompts
- Run on GPU for better performance

### Model responses are slow
- Check GPU availability: `ollama list`
- Use quantized models
- Increase Ollama memory: See Ollama documentation

---

## 📖 Key LangChain Concepts

### init_chat_model()
Universal model initialization supporting multiple providers:
- Ollama (local)
- OpenAI
- Anthropic
- Google
- And more

### Content Blocks
Different response components:
- `"text"` - Regular output text
- `"tool_call"` - Function call
- `"reasoning"` - Thinking steps (advanced models)

### Message History
Maintain conversation context:
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "First question"},
    {"role": "assistant", "content": "First answer"},
    {"role": "user", "content": "Follow-up question"}
]
response = model.invoke(messages)
```

---

## 🎯 Next Steps

1. **Run all examples** - Get familiar with different patterns
2. **Modify prompts** - Experiment with different inputs
3. **Combine patterns** - Mix tools + streaming + structured output
4. **Build applications** - Create your own LangChain applications
5. **Explore agents** - See the parent folder for agent examples

---

## 📚 Additional Resources

- [LangChain Documentation](https://docs.langchain.com)
- [Ollama Models](https://ollama.ai/library)
- [Pydantic Models](https://docs.pydantic.dev)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)

---

**Happy learning! 🚀**
