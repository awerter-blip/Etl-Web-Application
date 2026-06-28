import json
import os
import requests
import torch
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForMultimodalLM, AutoModelForCausalLM
from huggingface_hub import InferenceClient
from geopy.geocoders import Nominatim
from geopy.distance import geodesic


geolocator = Nominatim(user_agent="travel_app")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL_NAME = "qwen/qwen3-32b"


def create_tips(hotel,
                    start_time,
                    end_time,
                    travel_mode,
                    preferences,
                    days,
                    places_per_day,
                    max_time_per_visit,
                    max_km,
                    language):
    prompt = f"""
    You are a travel Agent.
    Collect tips for Place visit.
    Return ONLY valid JSON.

    {{
        "trip":[
            {{
                "day":1,
                "places":[
                    {{
                        "name":"",
                        "start":"",
                        "end":"",
                        "estimated_visit_minutes": int
                    }}
                ]
            }}
        ]
    }}

    Destination: {hotel}
    Preferences: {preferences}
    Days: {days}
    Places per day: {places_per_day}
    Maximum time spent per Places:{max_time_per_visit}
    Start: {start_time}
    End: {end_time}
    Language: {language}
    """

    # list = generate_ai_response(prompt)
    list = generate_ai_response(prompt)

    return list

def generate_description(place_name, language):

    
    
    prompt = f"""
    You are a travel Agency.
    Write a travel guide description.

    Place: {place_name}

    Requirements:
    - Minimum 100 words
    - Historical background
    - Why visit
    - Tourist tips
    - Valid Website Link

    Language:
    {language}
    """
    list = generate_ai_response_description(prompt)

    return list

def get_address(place_name):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": place_name,
        "format": "jsonv2",
        "limit": 1
    }

    headers = {
        "User-Agent": "MyTravelApp/1.0"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()

    results = response.json()

    if results:
        return results[0]["display_name"]
    else:
        return None

     
def get_distance(hotel_address, place_address):
    loc1 = geolocator.geocode(hotel_address)
    loc2 = geolocator.geocode(place_address)

    if not loc1 or not loc2:
        return None

    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{loc1.longitude},{loc1.latitude};"
        f"{loc2.longitude},{loc2.latitude}"
        f"?overview=false"
    )

    response = requests.get(url)
    data = response.json()
    #print(data)

    distance_m = data["routes"][0]["distance"]

    return round(distance_m / 1000, 2)







def generate_ai_response_description(prompt):
    
    
    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": """
                You are a travel planner API.

                Remove <think> at the beginning of the response.
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

 
    return content
    
    
def generate_ai_response(prompt):
    
    
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
    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    #content= json.loads(content)
    

    #parsed = json.loads(content)

    #return TripPlan.model_validate(parsed)
    return content






def main(hotel,
start_time,
end_time,
travel_mode,
preferences,
days,
places_per_day,
max_time_per_visit,
max_km,
language):
    


    result = create_tips(hotel,start_time,end_time,travel_mode, preferences,days, places_per_day, max_time_per_visit, max_km, language)

    trip = json.loads(result)
    #print(trip)
    hotel_address = get_address(hotel)
    #print(hotel_address)

    for day in trip["trip"]:

            for place in day["places"]:

                place["address"] = get_address(
                    place["name"]
                )

                place["description"] = generate_description(
                    place["name"],language
                )
                
                
                place["distance"] = get_distance(hotel_address, place["address"])

    #print(trip)
    return trip