import urllib.error
import urllib.request
import pprint
from langchain.tools import tool

from langchain.chat_models import init_chat_model

import langchain_groq
import os

from dotenv import load_dotenv

load_dotenv()

# model = init_chat_model("nvidia/nemotron-3-ultra-550b-a55b:free",
#                         api_key=os.environ["OPENROUTER_API_KEY"],
#                         model_provider="openrouter",
#                         base_url="https://openrouter.ai/api/v1",
#                         max_tokens=1000, temperature=0.0)


model = init_chat_model("openrouter/free",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=1000, temperature=0.0)


response = model.invoke("which model are you?")

pprint.pprint("Model response:")
pprint.pprint(response)