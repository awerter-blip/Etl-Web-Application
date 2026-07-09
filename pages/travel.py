import streamlit as st
import datetime
import json

from program.travel_planner import generate_text, generate_json
from program.travel_planner2 import main
from program.google_maps import create_google_maps_url
import plans


def load(user, username, lastlogin, cookies):

    st.set_page_config(
        page_title="Travel Planner",
        layout="wide",
        page_icon="✈️"
    )

    st.header("Plan your Travel")
    st.divider()

    # Session states
    if "selected_plan" not in st.session_state:
        st.session_state.selected_plan = None
    
    if "searchform" not in st.session_state:
        st.session_state.searchform = False

    if "submitted_form" not in st.session_state:
        st.session_state.submitted_form = False

    if "load_plan" not in st.session_state:
        st.session_state.load_plan = False

    if "show_save" not in st.session_state:
        st.session_state.show_save = False

    # =====================================================
    # LOAD SAVED PLAN
    # =====================================================

    plan_list = plans.load_plans(user)

    selected_plan = None

    with st.form("Load Plan Form"):

        if plan_list:

            selected_plan = st.selectbox(
                "Choose a plan",
                options=[p["plan_label"] for p in plan_list]
            )

        else:

            st.selectbox(
                "Choose a plan",
                options=[],
                index=None,
                placeholder="No saved plans"
            )
        load_col, remove_col = st.columns([0.3,0.3], gap="small")
        with load_col:
            load_plan_button = st.form_submit_button("Load Plan")
        with remove_col:
            remove_plan_button = st.form_submit_button("Remove Plan")

    if remove_plan_button and selected_plan:
        plans.remove_plan(
                user,
                selected_plan
                #st.session_state.selected_plan
            )

        st.session_state.load_plan = False

        st.session_state.pop("trip", None)
        st.session_state.pop("hotel", None)
        st.session_state.pop("travel_mode", None)
        st.session_state.pop("selected_plan", None)

        st.success("Plan Removed")

        st.rerun()
    
    if load_plan_button and selected_plan:

        trip_data = plans.load_plan(user, selected_plan)

        st.session_state.searchform = False
        st.session_state.load_plan = True

        st.session_state.selected_plan = selected_plan
        st.session_state.trip = json.loads(trip_data[0]["plan"])
        st.session_state.hotel = trip_data[0]["hotel"]
        st.session_state.travel_mode = trip_data[0]["travel_mode"]

    # =====================================================
    # DISPLAY LOADED PLAN
    # =====================================================

    if st.session_state.load_plan and "trip" in st.session_state:

        trip = st.session_state.trip
        hotel = st.session_state.hotel
        travel_mode = st.session_state.travel_mode

        for day in trip["trip"]:

            st.header(f"Day {day['day']}")

            concat = []

            for index, place in enumerate(day["places"], start=1):

                st.subheader(f"Program {index}")
                st.subheader(place["name"])
                if place["image"] != None:
                        st.image(place["image"], width=150)

                st.write(place["description"])

                st.write(
                    f"⏱ {place['estimated_visit_minutes']} minutes"
                )
                st.write(
                        f"Program Starts: {place['start']}"
                )
                st.write(
                    f"Program Ends: {place['end']}"
                )

                st.write(
                    f"Estimated distance from Hotel: {place['distance']}"
                )

                concat.append(
                    f"{place['name']}, {place['address']}"
                )

            result = create_google_maps_url(
                hotel,
                concat,
                travel_mode
            )

            st.link_button(
                "🚗 Open Navigation in Google Maps",
                result
            )

            st.divider()

        if st.button(
            "Remove Plan",
            key="remove_loaded_plan"
        ):

            plans.remove_plan(
                user,
                st.session_state.selected_plan
            )

            st.session_state.load_plan = False

            st.session_state.pop("trip", None)
            st.session_state.pop("hotel", None)
            st.session_state.pop("travel_mode", None)
            st.session_state.pop("selected_plan", None)

            st.success("Plan Removed")

            st.rerun()

    # =====================================================
    # OPEN SEARCH FORM
    # =====================================================

    if st.button("Open Searchform"):

        st.session_state.searchform = True
        st.session_state.submitted_form = False
        st.session_state.load_plan = False

        st.session_state.pop("trip", None)
        st.session_state.pop("hotel", None)
        st.session_state.pop("travel_mode", None)
        st.session_state.pop("selected_plan", None)

    # =====================================================
    # SEARCH FORM
    # =====================================================

    if st.session_state.searchform:

        with st.form("input_form"):

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                hotel = st.text_input(
                    "Hotel Address, City(Starting Point)",
                    
                )

            with col2:
                days = st.number_input(
                    "Number of Days",
                    min_value=1
                )

            with col3:
                travel_mode = st.selectbox(
                    "Transport",
                    ["walking", "driving", "transit"]
                )

            col4, col5, col6 = st.columns([1, 1, 1])

            with col4:

                preferences = st.multiselect(
                    "Preferences",
                    [
                        "history",
                        "food",
                        "nature",
                        "shopping",
                        "nightlife",
                        "beaches"
                    ]
                )

            with col5:

                start_time = st.time_input(
                    "Choose the Start Time of the Day",
                    datetime.time(0, 0)
                )

            with col6:

                end_time = st.time_input(
                    "Choose the End Time of the Day",
                    datetime.time(23, 45)
                )

            col7, col8, col9, col10 = st.columns([1, 1, 1, 1])

            with col7:

                places_per_day = st.number_input(
                    "Visited Places per day",
                    min_value=1,
                    step=1
                )

            with col8:

                max_time_per_visit = st.number_input(
                    "Maximum spent time per Places",
                    min_value=30,
                    step=15
                )

            with col9:

                max_km = st.number_input(
                    "Maximum km per day",
                    min_value=5,
                    step=1
                )
            with col10:
                language = st.selectbox("Select the Language", ["HUN", "ENG"])

            submitted = st.form_submit_button("Submit")

        # =====================================================
        # GENERATE PLAN
        # =====================================================

        if submitted:

            st.session_state.submitted_form = True

            with st.spinner("Planning AI tips..."):
                ## Groq REST APi Version
                # st.session_state.trip = generate_text(
                    # hotel,
                    # start_time,
                    # end_time,
                    # travel_mode,
                    # preferences,
                    # days,
                    # places_per_day,
                    # max_time_per_visit,
                    # max_km,
                    # language
                # )
                ## Hugging Face Version
                st.session_state.trip = main(
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
                )

                st.session_state.hotel = hotel
                st.session_state.travel_mode = travel_mode

        # =====================================================
        # DISPLAY GENERATED PLAN
        # =====================================================

        if "trip" in st.session_state:

            trip = st.session_state.trip

            for day in trip["trip"]:

                st.header(f"Day {day['day']}")

                concat = []

                for index, place in enumerate(
                    day["places"],
                    start=1
                ):

                    st.subheader(f"Program {index}")
                    st.subheader(place["name"])
                    
                    if place["image"] != None:
                        st.image(place["image"], width=150)

                    st.write(place["description"])

                    st.write(
                        f"⏱ {place['estimated_visit_minutes']} minutes"
                    )

                    st.write(
                        f"Estimated distance from Hotel: {place['distance']}"
                    )
                    
                    st.write(
                        f"Program Starts: {place['start']}"
                    )
                    st.write(
                        f"Program Ends: {place['end']}"
                    )

                    concat.append(
                        f"{place['name']}, {place['address']}"
                    )

                result = create_google_maps_url(
                    st.session_state.hotel,
                    concat,
                    st.session_state.travel_mode
                )

                st.link_button(
                    "🚗 Open Navigation in Google Maps",
                    result
                )

                st.divider()

            # =====================================================
            # SAVE PLAN
            # =====================================================

            if st.button("Save Plan"):
                st.session_state.show_save = True

            if st.session_state.show_save:

                plan_label = st.text_input("Add a name")

                if st.button("Save to Database"):

                    plan_json = json.dumps(trip)

                    plans.save_plan(
                        user,
                        plan_label,
                        plan_json,
                        st.session_state.hotel,
                        st.session_state.travel_mode
                    )

                    st.success("Plan Saved")

                    st.session_state.show_save = False
                    st.session_state.submitted_form = False
                    
                    st.rerun()