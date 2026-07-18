import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from pydantic import BaseModel, ValidationError

load_dotenv()

SAMPLE_WEATHER={"tokyo":{"temp":30,"condition":"warm"}}

def get_weather(city:str)->str:
    data=SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather available for {city}"
    return f"{city.title()}, {data.get('temp')}c"

get_weather_schema = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use this whenever "
                        "the user asks about weather, temperature, or conditions "
                        "in a specific place.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name, e.g. 'Tokyo'."}
            },
            "required": ["city"],
        },
    },
}

def get_client_and_model()-> tuple[OpenAI,str] :
    if (os.environ["GROQ_API_KEY"]):
        return (OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1"),
                "llama-3.3-70b-versatile",)



def ask_ai_to_choose(question :str) :
    client, model=get_client_and_model()
    response=client.chat.completions.create(
        model=model, 
        messages=[{"role":"user","content":question}],
        max_tokens=200,
        tools=[get_weather_schema]

        )
    return response.choices[0].message


if __name__=="__main__":
    question="What is the eather in Tokyo"
    message=ask_ai_to_choose(question)

    if message.tool_calls:
        call=message.tool_calls[0]
        args=json.loads(call.function.arguments)
        result=get_weather(**args)
        print(result)

    print("Done")