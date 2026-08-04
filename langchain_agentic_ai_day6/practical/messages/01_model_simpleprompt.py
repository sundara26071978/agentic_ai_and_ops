"""Simple Text Prompt Example

Demonstrates the basic usage of LangChain with a text prompt (string).
This is the simplest way to invoke a model - ideal for straightforward,
standalone requests without conversation history.

Prerequisite: Ollama must be running with deepseek-r1 model installed
"""
import pprint

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage

# Initialize the chat model using Ollama with deepseek-r1:latest
# Use init_chat_model() for model-agnostic initialization
model = init_chat_model("ollama:gemma4:latest", max_tokens=500, temperature=0.0)

# Invoke model with a simple text prompt (string)
# This is converted internally to a HumanMessage
response = model.invoke("write a haiku about the ocean both in english and tamil in 200 words")

# Access the content from the AIMessage response
pprint.pprint(response.content)  # Displays the model's response

print("✓ Text prompt invocation completed.")
#Deepseek
# '2. கடல் மீது பெய்கிறது (kaEthal meeThu peykiRathu) - 8 syllables (kaEth-al - '
#  '2, mee-Thu - 2, pey-ki-Ra-thu - 4)\n'
#  '3. மூழ்கிற கனவு (muL kizhathu kaNavu) - 5 syllables (muL - 1, kizhathu - 3, '
#  'kaNavu - 1)\n'
#  '\n'
#  'This is closer to the 5-7-5 structure in spirit, capturing the depth, '
#  'mystery, and vastness of the ocean. The English version is cleaner at 5-7-5.')

