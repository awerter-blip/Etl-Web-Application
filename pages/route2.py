import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import polyline

# --- API KEY ---
API_KEY = "YOUR_GOOGLE_API_KEY"

st.title("🗺️ Route Planner")

# --- input ---
col1, col2 = st.columns(2)

with col1:
    origin = st.text_input("Honnan?", "Budapest")

with col2:
    destination = st.text_input("Hová?", "Vienna")

# --- gomb ---
if st.button("Útvonal tervezés"):

    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={API_KEY}"

    data = requests.get(url).json()

    if data["status"] != "OK":
        st.error("Hiba az útvonal lekérésnél")
    else:
        route = data["routes"][0]
        leg = route["legs"][0]

        distance = leg["distance"]["text"]
        duration = leg["duration"]["text"]

        st.success(f"Távolság: {distance} | Idő: {duration}")

        # --- polyline dekódolás ---
        points = polyline.decode(route["overview_polyline"]["points"])

        # --- térkép ---
        m = folium.Map(location=points[0], zoom_start=7)

        # marker-ek
        folium.Marker(points[0], tooltip="Start").add_to(m)
        folium.Marker(points[-1], tooltip="Cél").add_to(m)

        # route vonal
        folium.PolyLine(points, color="blue", weight=5).add_to(m)

        st_folium(m, width=700, height=500)

        # --- Google Maps gomb ---
        maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"

        st.markdown(f"[🚗 Navigáció megnyitása Google Maps-ben]({maps_url})")