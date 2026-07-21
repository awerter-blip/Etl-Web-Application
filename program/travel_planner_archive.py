import json
import os
import requests
import torch

from openai import OpenAI
from pydantic import BaseModel
from typing import List

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM



client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)



def generate_text(
    hotel,
    start_time,
    end_time,
    travel_mode,
    preferences,
    days,
    places_per_day,
    max_time_per_visit,
    max_km,
    language
):

    prompt = f"""
    Create a {days}-day travel itinerary.

    Hotel:
    {hotel}

    Transport:
    {travel_mode}

    Preferences:
    {preferences}

    Places per day:
    {places_per_day}
    
    Start Time:
    {start_time}
    
    End Time:
    {end_time}
    
    Maximum km per day:
    {max_km}
    
    Max Time per Visit:
    {max_time_per_visit}

    IMPORTANT:
    
    For each place:
    - Places should come after each other by distance
    - write a detailed description
    - minimum 80 words
    - explain why it is worth visiting
    - include historical or cultural context
    - mention tips for tourists
    - Show The Start Time and End time of the Program
    - Write is in {language}
    

    Return ONLY valid JSON.

    REQUIRED JSON FORMAT:

    {{
      "trip": [
        {{
          "day": 1,
          "places": [
            {{
              "name": "string",
              "description": "minimum 80 words with website link",
              "estimated_visit_minutes": int,
              "address": "string"
              "distance": "Distance from Hotel in km."
              "start": "Start Time of the program."
              "end": "Start Time of the program."
            }}
          ]
        }}
      ]
    }}

    trip MUST be a JSON array.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
                You are a travel planner API.

                Return ONLY valid JSON.
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content
    #print(content)

    # cleanup
    # content = (
        # content
        # .replace("```json", "")
        # .replace("```", "")
        # .strip()
    # )

    content= json.loads(content)
    

    #parsed = json.loads(content)

    #return TripPlan.model_validate(parsed)
    return content
    
 ## Transformers library   #####

MODEL_NAME = "google/flan-t5-large"
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return tokenizer, model
 
def generate_places(city, preferences, days, places_per_day):

    tokenizer, model = load_model()
    
    
    
    prompt = f"""
    Return ONLY valid JSON.

    {{
        "trip":[
            {{
                "day":1,
                "places":[
                    {{
                        "name":""
                    }}
                ]
            }}
        ]
    }}

    Destination: {city}
    Preferences: {preferences}
    Days: {days}
    Places per day: {places_per_day}
    """

    # messages = [
        # {"role": "user", "content": prompt}
    # ]

    # text = tokenizer.apply_chat_template(
        # messages,
        # tokenize=False,
        # add_generation_prompt=True
    # )

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7
    )

    result = tokenizer.decode(
        outputs[0][inputs.input_ids.shape[1]:],
        skip_special_tokens=True
    )
    
  
    result = json.loads(result)
    
    return result
    

def get_address(place_name, city):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": f"{place_name}, {city}",
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": "TravelPlanner"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers
    )

    data = response.json()

    if not data:
        return ""

    return data[0]["display_name"]
    
def generate_description(place_name, language):

    tokenizer, model = load_model()
    
    
    prompt = f"""
    Write a travel guide description.

    Place: {place_name}

    Requirements:
    - Minimum 100 words
    - Historical background
    - Why visit
    - Tourist tips

    Language:
    {language}
    """

    # messages = [
        # {"role": "user", "content": prompt}
    # ]

    # text = tokenizer.apply_chat_template(
        # messages,
        # tokenize=False,
        # add_generation_prompt=True
    # )

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=300,
        temperature=0.7
    )

    return tokenizer.decode(
        outputs[0][inputs.input_ids.shape[1]:],
        skip_special_tokens=True
    )
    
def generate_json(hotel,
    start_time,
    end_time,
    travel_mode,
    preferences,
    days,
    places_per_day,
    max_time_per_visit,
    max_km,
    language):
    
    
    
    trip = generate_places(
    city=hotel,
    preferences=preferences,
    days=days,
    places_per_day=places_per_day
    )

    
    
    
    for day in trip["trip"]:

        for place in day["places"]:

            place["address"] = get_address(
                place["name"],hotel
            )

            place["description"] = generate_description(
                place["name"],language
            )
            
            place["estimated_visit_minutes"] = 90
            
            place["distance"] = max_km
            place["start"] = start_time
            place["end"] = end_time
    
    
    
    # trip_json = json.dumps(
    # trip,
    # ensure_ascii=False,
    # indent=2
    #)

    #print(trip_json)
    return trip
    