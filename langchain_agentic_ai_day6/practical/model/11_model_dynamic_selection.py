

import pprint
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain.agents import create_agent
import os
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from dotenv import load_dotenv



load_dotenv("C:\\Users\\socgen\\ML\\agentic_ai_and_ops\\langchain_day5\\.env")


# Initialize model
basic_model = init_chat_model("ollama:qwen3.5:latest")

nvidia_model = init_chat_model("nvidia/nemotron-3-ultra-550b-a55b:free",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=1000, temperature=0.0)

advanced_model = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=100, temperature=0.0)


complex_messages = [
    SystemMessage("You are a poetry expert"),  # Set model behavior and role
    HumanMessage("Write a haiku about Agentic AI"),  # User request
    AIMessage("Agentic minds rise, Learning, adapting, they grow, Guiding paths unknown.")  # Model response
]
simple_message=[
    HumanMessage("Write a joke about Agentic AI")  # User request
]

joke_config={
        "run_name": "joke_generation",      # Custom name for this run
        "tags": ["humor", "demo"],          # Tags for categorization
        "metadata": {"user_id": "Sunj123"},     # Custom metadata
       
    }


haiku_config={
        "run_name": "haiku_generation",      # Custom name for this run
        "tags": ["poetry", "demo"],          # Tags for categorization
        "metadata": {"user_id": "Sunj123"},     # Custom metadata
           }


@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """Choose model based on conversation complexity."""
    message_count = len(request.state["messages"])

    if message_count > 2:
        # Use an advanced model for longer conversations
        model = advanced_model
    else:
        model = nvidia_model

    return handler(request.override(model=model))

agent = create_agent(
    model=basic_model,  # Default model
    middleware=[dynamic_model_selection]
)
# response = agent.invoke({"messages": complex_messages}, config=haiku_config)
response = agent.invoke({"messages": simple_message}, config=joke_config)

# Display the final assistant message from the agent state
print("Response Content:")
print(response["messages"][-1].content)

# print("\n=== Debug Information ===")
# pprint.pprint("Invocation configuration complete")
