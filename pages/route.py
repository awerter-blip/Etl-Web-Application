import streamlit as st
from urllib.parse import quote

def render(client, user, username, lastlogin ,cookies):
    st.set_page_config(page_title="Route Planner", layout="wide", page_icon="🗺️")
    st.title("Route planner")
    # ------------------------
    # AUTO LOGIN (refresh után)
    # ------------------------
    if "user" not in st.session_state:
        token = cookies.get("auth_token")

        if token:
            user = get_user_by_token(token)
            if user:
                st.session_state["user"] = user
                st.session_state["token"] = token
            else:
                st.session_state["user"] = None
        else:
            st.session_state["user"] = None
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"User: {username}")
    
                
    with col2:
        st.markdown(f"Last login: {lastlogin}")

    
    start = st.text_input("From:")
    destination = st.text_input("Where:")

    
    start_encoded = quote(start)
    destination_encoded = quote(destination)
    

    if st.button("Submit"):
        url = f"https://www.google.com/maps/dir/?api=1&origin={start_encoded}&destination={destination_encoded}"
        st.markdown(f"[🚗 Indítás Google Maps-ben]({url})")