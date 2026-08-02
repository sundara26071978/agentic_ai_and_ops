

import pprint
from langchain.chat_models import init_chat_model
import pprint
from langchain_core.callbacks import UsageMetadataCallbackHandler
import os

from dotenv import load_dotenv

load_dotenv("C:\\Users\\socgen\\ML\\agentic_ai_and_ops\\langchain_day5\\.env")


# Initialize model
# model = init_chat_model("ollama:qwen3.5:latest")
model_or_paid_gpt56_luna_pro = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=100, temperature=0.0)


my_callback_handler= UsageMetadataCallbackHandler()
# Ask the model something that might require web search
response = model_or_paid_gpt56_luna_pro.invoke(
    "Tell me a joke",
    config={
        "run_name": "joke_generation",      # Custom name for this run
        "tags": ["humor", "demo"],          # Tags for categorization
        "metadata": {"user_id": "Sunj123"},     # Custom metadata
        "callbacks": [my_callback_handler], # Callback handlers
    }
)

# Display response content blocks
print("Response Content Blocks:")
print(response.content_blocks)

# print("\n=== Debug Information ===")
# pprint.pprint("Invocation configuration complete")
