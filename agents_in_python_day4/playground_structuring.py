import pprint
from pydantic import BaseModel,ValidationError
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
load_dotenv()

def pretty_print(response)->None:
    pretty_json=json.dumps(response, indent=4)
    pprint.pprint(pretty_json)

def call_groq(question:str)->str:
    client= OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    response=client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role":"user", "content":question}],
        max_tokens=200,
        )
    # pretty_print(response)
    return response.choices[0].message.content

def ask_ai(question : str)->str:
    if(os.environ["GROQ_API_KEY"]):
        return call_groq(question)


class WeatherQuestion(BaseModel) :
    city :str
    wants_farenheit :bool=False

def extract_weather_question(user_message:str)->WeatherQuestion|str:
    
    instruction = (
        "Read the user's message and reply with ONLY a JSON object -- no other "
        'text -- in this exact shape: {"city": "<city name>", '
        '"wants_fahrenheit": <true or false>}. '
        f"User's message: {user_message!r}"
    )
    raw_reply=ask_ai(instruction)
    try:
        cleaned=raw_reply.strip().removeprefix("```json").removesuffix("```").strip()
        data= json.loads(cleaned)
        weather_question= WeatherQuestion(**data)
        return weather_question
    except(ValidationError,json.JSONDecodeError)as e:
        return f"Rejected : {e}"
    
if __name__=="__main__":
    questions: list[str]=["what is the weather in Tokyo"]

    for question in questions:
        result=extract_weather_question(question)
        print(f"question: {question} and answer: {result}")



