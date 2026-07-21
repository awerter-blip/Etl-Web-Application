import json
import os
import requests
import re
from functools import lru_cache
from openai import OpenAI
from geopy.geocoders import Nominatim


# -----------------------------
# CONFIG
# -----------------------------



client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


geolocator = Nominatim(
    user_agent="travel-planner-app"
)


def create_tips(hotel,hotel_address,
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

    Start Location: {hotel_address}
    Destination: {hotel_address}
    Preferences: {preferences}
    Days: {days}
    Places per day: {places_per_day}
    Maximum time spent per Places:{max_time_per_visit}
    Maximum distance from Start Location: {max_km}
    Start: {start_time}
    End: {end_time}
    Language: {language}
    """

    # list = generate_ai_response(prompt)
    list = generate_ai_response(prompt)
    #print(list)

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







def generate_ai_response_description(place, language, address):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": f"""
                You are an expert travel guide and tourism writer.

                Write a travel description in {language}.

                Rules:
                - Return ONLY the final description text.
                - Do NOT include your reasoning.
                - Do NOT output <think> tags.
                - Do NOT use Markdown.
                - Do NOT use headings.
                - Do NOT use bullet points.
                - Do NOT include labels like "Description:".

                Content requirements:
                - Length: 120-180 words.
                - Start with an engaging introduction of the place.
                - Explain its historical or cultural importance.
                - Describe the atmosphere and main attractions.
                - Include useful visitor information.
                - Mention the best visiting time if relevant.
                - Mention local food, traditions, or interesting facts when appropriate.
                - Include the official website URL at the end if available.
                - Finish with an inviting sentence encouraging a visit.
                """
                            },
                            {
                                "role": "user",
                                "content": f"""
                Place:
                {place}

                Address:
                {address}
                """
            }
        ]
    )

    content = response.choices[0].message.content

    # Qwen gondolkodás eltávolítása
    content = re.sub(
        r"<think>.*?</think>",
        "",
        content,
        flags=re.DOTALL
    )

    # felesleges whitespace
    content = content.strip()
    #print(content)

    return content
    
def generate_ai_response(prompt):


        response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
        {
            "role": "system",
            "content": """
            You are a travel planner.

            Return ONLY valid JSON.

            Do not show your reasoning.
            Do not output <think> tags.
            Do not explain anything.
            Do not use markdown.
            Do not use ```.

            The response must start with {
            and end with }.
            """
            },
            {
                "role": "user",
                "content": prompt
            }
            ]
            )


        content = response.choices[0].message.content


        # Qwen thinking blokk törlése
        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL
        )


        # Markdown törlés
        content = content.replace("```json", "")
        content = content.replace("```", "")

        content = content.strip()


        data = json.loads(content)

        return data
        



def get_wiki_image(title):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}"
    headers = {
    "User-Agent": "TravelTipsBot/1.0 (https://example.com; werter.attila@gmail.com)"
    }
    #print(url)
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        return None

    data = r.json()

    if "originalimage" in data:
        return data["originalimage"]["source"]

    if "thumbnail" in data:
        return data["thumbnail"]["source"]

    



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
    

    hotel_address = get_address(hotel)
    result = create_tips(hotel,hotel_address,start_time,end_time,travel_mode, preferences,days, places_per_day, max_time_per_visit, max_km, language)

    #trip = json.loads(result)
    trip = result
    #print(trip)
    hotel_address = get_address(hotel)
    #print(hotel_address)

    for day in trip["trip"]:

            for place in day["places"]:

                place["address"] = get_address(
                    place["name"]
                )
                
                place["image"] = get_wiki_image(place["name"])
                

                place["description"] = generate_ai_response_description(
                    place["name"],language, place["address"]
                )
                
                
                place["distance"] = get_distance(hotel_address, place["address"])

    #print(trip)
    return trip