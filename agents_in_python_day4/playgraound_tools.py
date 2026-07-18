import json
import pprint
from pydantic import BaseModel, ValidationError
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

def ask_groq(question : str)-> str :
    client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
    response= client.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        max_tokens=200, 
        messages=[{"role":"user", "content":question}])
    return response.choices[0].message.content


def ask_ai(question:str)->str:
    return ask_groq(question)

class WeatherQuestion(BaseModel):
    city:str
    wants_fahrenheit:bool=False

def extract_weather_question(question: str)-> WeatherQuestion | str:
    instruction= (
        "Read the user's message and reply with ONLY a JSON object -- no other "
        'text -- in this exact shape: {"city": "<city name>", '
        '"wants_fahrenheit": <true or false>}. '
        f"User's message: {question!r}"
    )

    raw_response=ask_ai(instruction)
    try:
        cleaned=raw_response.strip().removeprefix("```json").removesuffix("```").strip()
        data=json.loads(cleaned)
        weather=WeatherQuestion(**data)
        return weather
    except(json.JSONDecodeError, ValidationError) as e:
        return f"Rejected: {e}"

SAMPLE_WEATHER={"tokyo": {"celsius":30,"condition":"warm"}}

def get_weather(city:str)->str :
    data=SAMPLE_WEATHER.get(city.lower())
    if data is None:
        return f"No weather data for {city!r}."
    return f"{city.title()}: {data['celsius']}C, {data['condition']}"


def answer_weather_question(question : str) -> str :
    extracted = extract_weather_question(question)
    if not isinstance(extracted, WeatherQuestion):
        return f"could not extract weather for city : {extracted}"
    return get_weather(extracted.city)

if __name__=="__main__":
    weather_question = answer_weather_question("what is the weather in tokyo")
    print(weather_question)







