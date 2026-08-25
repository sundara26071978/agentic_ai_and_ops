# Model Context Protocol (MCP) with LangChain

A hands-on playground demonstrating how **Model Context Protocol (MCP)** servers can expose tools to a **LangChain agent**, using the `langchain-mcp-adapters` library.

## Overview

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open protocol that standardizes how applications provide **tools and context to LLM applications**.

This notebook demonstrates how a LangChain agent can consume tools exposed by MCP servers through `MultiServerMCPClient`.

The example connects to two MCP servers:

- **Math MCP Server** — connected through `stdio`
- **Weather MCP Server** — connected through HTTP

The tools from both servers are dynamically loaded and supplied to a LangChain agent.

## Architecture

```text
                         ┌──────────────────────┐
                         │    LangChain Agent   │
                         │                      │
                         │      LLM + Tools     │
                         └──────────┬───────────┘
                                    │
                         get_tools()
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
        ┌─────────▼─────────┐              ┌──────────▼─────────┐
        │  Math MCP Server  │              │ Weather MCP Server │
        │                   │              │                    │
        │ Transport: stdio │              │ Transport: HTTP    │
        └───────────────────┘              └────────────────────┘
```

## What This Notebook Demonstrates

### 1. MCP fundamentals

The notebook introduces MCP and its role in standardizing how LLM applications access external tools and context.

### 2. LangChain MCP integration

The integration is implemented using:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
```

`MultiServerMCPClient` allows the application to connect to multiple MCP servers and retrieve their tools.

### 3. Multiple MCP transports

The example demonstrates two different ways of communicating with MCP servers.

#### STDIO

The Math server is configured as a local Python process:

```python
"math": {
    "transport": "stdio",
    "command": "python",
    "args": ["/path/to/math_server.py"],
}
```

This allows the MCP client to communicate with a locally launched server process.

#### HTTP

The Weather server is configured as an HTTP-based MCP server:

```python
"weather": {
    "transport": "http",
    "url": "http://localhost:8000/mcp",
}
```

This demonstrates how the same LangChain agent can consume tools from a remotely accessible MCP endpoint.

## Key Code

The MCP client is configured with multiple servers:

```python
client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/path/to/math_server.py"],
        },
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        },
    }
)
```

The available tools are then retrieved dynamically:

```python
tools = await client.get_tools()
```

Those tools are passed directly to the LangChain agent:

```python
agent = create_agent(
    "claude-sonnet-4-6",
    tools
)
```

The agent can subsequently decide which MCP tool to use based on the user's request.

## Example Use Cases

### Math

```text
User
  │
  │ "What's (3 + 5) x 12?"
  ▼
LangChain Agent
  │
  ▼
Math MCP Tool
  │
  ▼
Result
```

### Weather

```text
User
  │
  │ "What is the weather in NYC?"
  ▼
LangChain Agent
  │
  ▼
Weather MCP Tool
  │
  ▼
Result
```

The notebook invokes both examples using asynchronous agent calls.

## Prerequisites

- Python 3.13+
- LangChain
- `langchain-mcp-adapters`
- `python-dotenv`
- An MCP Math server
- An MCP Weather server
- Appropriate model/API credentials

The notebook currently uses environment variables including:

```text
GROQ_API_KEY
OPENROUTER_API_KEY
```

## Installation

Install the required Python packages:

```bash
pip install langchain langchain-mcp-adapters python-dotenv rich
```

Install or configure the MCP servers used by the notebook separately.

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=<your-groq-api-key>
OPENROUTER_API_KEY=<your-openrouter-api-key>
```

The notebook loads these variables using:

```python
from dotenv import load_dotenv

load_dotenv()
```

## Running the Notebook

Start Jupyter:

```bash
jupyter notebook
```

Open:

```text
playground.ipynb
```

Before executing the MCP example, make sure:

1. The Math MCP server is available at the configured Python path.
2. The Weather MCP server is running.
3. The Weather MCP endpoint is available at:

```text
http://localhost:8000/mcp
```

4. Required API keys are configured.

## Important Concepts

### MCP Server

An MCP server exposes capabilities such as tools or resources through the MCP protocol.

### MCP Client

The client connects the LLM application to one or more MCP servers.

In this example:

```python
MultiServerMCPClient(...)
```

acts as the MCP client.

### MCP Tool

Tools exposed by MCP servers are retrieved dynamically:

```python
tools = await client.get_tools()
```

The resulting tools can then be supplied to a LangChain agent.

### LangChain Agent

The agent combines the LLM with the tools retrieved from the MCP servers and determines when a tool should be invoked.

## Project Structure

```text
.
├── playground.ipynb
└── README.md
```

The main implementation and experiments are currently contained in `playground.ipynb`.

## Learning Flow

The notebook follows this conceptual flow:

```text
MCP
 │
 ├── Understand MCP
 │
 ├── Connect to MCP servers
 │
 ├── Configure different transports
 │     ├── STDIO
 │     └── HTTP
 │
 ├── Retrieve MCP tools
 │
 └── Provide tools to a LangChain agent
          │
          ├── Math request
          └── Weather request
```

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [LangChain](https://www.langchain.com/)
- [LangChain MCP Adapters](https://github.com/langchain-ai/langchain-mcp-adapters)

## Status

This repository is a **learning/playground implementation** exploring MCP integration with LangChain agents. The notebook can be extended with additional MCP servers, tools, transports, middleware, and agent workflows.