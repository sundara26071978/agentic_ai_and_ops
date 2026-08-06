from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["AICREDITS_API_KEY"]=os.getenv("AICREDITS_API_KEY")
os.environ["AICREDITS_BASE_URL"]=os.getenv("AICREDITS_BASE_URL")
os.environ["AICREDITS_MODEL"]=os.getenv("AICREDITS_MODEL")
os.environ["AICREDITS_MODEL_MAX_TOKENS"]=os.getenv("AICREDITS_MODEL_MAX_TOKENS")
os.environ["AICREDITS_MODEL_5_MINI"]=os.getenv("AICREDITS_MODEL_5_MINI")

os.environ["OPENROUTER_API_KEY"]=os.getenv("OPENROUTER_API_KEY")
os.environ["OPENROUTER_BASE_URL"]=os.getenv("OPENROUTER_BASE_URL")
os.environ["OPENROUTER_MODEL"]=os.getenv("OPENROUTER_MODEL")
os.environ["OPENROUTER_MODEL_MAX_TOKENS"]=os.getenv("OPENROUTER_MODEL_MAX_TOKENS")
os.environ["OPENROUTER_MODEL_5_MINI"]=os.getenv("OPENROUTER_MODEL_5_MINI")

# llm = ChatOpenAI(
#     model=os.getenv("AICREDITS_MODEL"),
#     base_url=os.getenv("AICREDITS_BASE_URL"),
#     api_key=os.getenv("AICREDITS_API_KEY"),
#     max_tokens=int(os.getenv("AICREDITS_MODEL_MAX_TOKENS")),
# )


llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    max_tokens=int(os.getenv("OPENROUTER_MODEL_MAX_TOKENS")),
)


response = llm.invoke("What is ESG?")
print(response.content)