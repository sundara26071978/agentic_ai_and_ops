import re
from langchain.agents import create_agent
from langchain.agents.middleware import  PIIMiddleware
from langchain.agents.middleware._redaction import PIIMatch


from rich import print as rprint
from langchain.chat_models import init_chat_model
import os

from dotenv import load_dotenv

load_dotenv()


model_basic = init_chat_model("nvidia/nemotron-3-ultra-550b-a55b:free",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=1000, temperature=0.0)

model_medium = init_chat_model("openai/gpt-5.6-luna",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)

model_advanced = init_chat_model("openai/gpt-5.6-luna-pro",
                        api_key=os.environ["OPENROUTER_API_KEY"],
                        model_provider="openrouter",
                        base_url="https://openrouter.ai/api/v1",
                        max_tokens=10000, temperature=0.0)


agent = create_agent(
    model=model_advanced,
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
        PIIMiddleware("url", strategy="hash", apply_to_input=True),
    ],
)

# Method 1: Regex pattern string
agent1 = create_agent(
    model=model_advanced,
    tools=[],
    middleware=[
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            
        ),
    ],
)

# Method 2: Compiled regex pattern
agent2 = create_agent(
    model=model_advanced,
    tools=[],
    middleware=[
        PIIMiddleware(
            "phone_number",
            detector=re.compile(r"\+?\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{4}"),
            strategy="mask",
        ),
    ],
)

# Method 3: Custom detector function
def detect_ssn(content: str) -> list[PIIMatch]:
    """Detect SSNs with validation."""
    matches: list[PIIMatch] = []
    pattern = r"\d{3}-\d{2}-\d{4}"
    for match in re.finditer(pattern, content):
        ssn = match.group(0)
        # Validate: first 3 digits shouldn't be 000, 666, or 900-999
        first_three = int(ssn[:3])
        if first_three not in [0, 666] and not (900 <= first_three <= 999):
            matches.append({
                "type": "ssn",
                "value": ssn,
                "start": match.start(),
                "end": match.end(),
            })
    return matches

agent3 = create_agent(
    model=model_advanced,
    tools=[],
    middleware=[
        PIIMiddleware(
            "ssn",
            detector=detect_ssn,
            strategy="hash",
        ),
    ],
)


result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": """
            The customer's credit card is 4111 1111 1111 1111.
            The url of transaction system is https://gptm.bank.com.
            Please send a dummy report to john.smith@example.com.
            """
        }
    ]
},  
config={
        "run_name": "PII Built-in detector email, credit_card, url",      # Custom name for this run
        "tags": ["REDACT", "mask","hash"],          # Tags for categorization
        "metadata": {"user_id": "sunj"},     # Custom metadata
      
    })
print("Built-in detector — email, credit_card, url")
print("-"*50)
rprint(result)
print("-"*50)
# print("Method 1: Regex pattern string API key")
# print("-"*50)
# result = agent1.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": "My API key is sk-abcdefghijklmnopqrstuvwxyz123456. Please use it."
#         }
#     ]
# })

# rprint(result)
# # print("-"*50)
# print("# Method 2: Compiled regex pattern phone number")

# print("-"*50)
# result = agent2.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": """
#             Please call me at +91 9876 543210
#             regarding the trade confirmation.
#             """
#         }
#     ]
# })

# rprint(result)
# print("-"*50)
# print("Method 3: Custom detector function SSN number")
# print("-"*50)
# result = agent3.invoke({
#     "messages": [
#         {
#             "role": "user",
#             "content": """
#             Customer SSN: 123-45-6789

#             Another value is 666-12-3456.
#             Please process these customer details.
#             """
#         }
#     ]
# })

# rprint(result)
# print("-"*50)

