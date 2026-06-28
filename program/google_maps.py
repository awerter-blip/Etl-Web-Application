from urllib.parse import quote


def create_google_maps_url(
    hotel,
    places,
    travel_mode="walking"
):
    # """
    # places:
    # [
        # {
            # "name": "...",
            # "address": "..."
        # }
    # ]
    # """

    if not places:
        return None

    origin = quote(hotel)
    
    destination = origin

    # destination = quote(
        # places[-1]["address"]
    # )

    # köztes waypointok
    #print(places)
    waypoint_string = "|".join(
        quote(place) for place in places
    )
    

    url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&waypoints={waypoint_string}"
        f"&travelmode={travel_mode}"
    )
    
    return url