import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
from cookies import get_cookies
from openai import OpenAI
import os
import uuid
from auth import login, register, last_login, username, get_user_by_token, logout
#from messages import save_message, load_messages, remove_messages
#from pages import chatgpt, gpt , route, travel
from pages import chatgpt, gpt, route, travel


# Page Config
st.set_page_config(page_title="Etl Basic App", layout="wide", page_icon="user.jpg")
#st.title("🤖 Mini Chat GPT")

st.title("Etl App")

# Open AI kliens


api = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api)

# Initialize sqlite db
#init_db()

cookies = get_cookies()

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



# Authentikáció

if "user" not in st.session_state:
    st.session_state.user = None

# 🔐 LOGIN UI

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        # ------------------------
        # LOGIN SCREEN
        # ------------------------
        if not st.session_state["user"]:
            st.title("Login")

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                result = login(username, password)

                if result:
                    st.session_state["user"] = {
                        "id": result["user_id"],
                        "username": username
                    }
                    st.session_state["token"] = result["token"]

                    cookies["auth_token"] = result["token"]
                    cookies.save()

                    st.rerun()
                else:
                    st.error("Invalid credentials")

        # ------------------------
        # LOGGED IN VIEW
        # ------------------------
        else:
            st.title(f"Welcome {st.session_state['user']['username']} 👋")

            if st.button("Logout"):
                logout(st.session_state["token"])

                cookies["auth_token"] = ""
                cookies.save()

                st.session_state.clear()
                st.rerun()

    with tab2:
        new_user = st.text_input("New username")
        name = st.text_input("Name")
        new_pass = st.text_input("New password", type="password")       

        if st.button("Register"):
            if register(new_user, new_pass, name):
                st.success("Registration was successful")
            else:
                st.error("User already exist.")

    st.stop()


user = st.session_state.user["id"]
username = username(user)
lastlogin = last_login(user)





# --- INIT ---
if "page" not in st.session_state:
    st.session_state.page = "home"



# --- NAVBAR ---

def navbar():
    
    width = streamlit_js_eval(js_expressions='window.innerWidth', key='WIDTH')
    
    if width is None:
        width = 1200  # fallback érték

    #print(type(width))
    is_mobile = width < 768
    
    if "menu_open" not in st.session_state:
        st.session_state.menu_open = False

    # --- MOBIL NÉZET ---
    if is_mobile:
        col1, col2 = st.columns([1, 8])

        with col1:
            if st.button("☰"):
                #st.session_state.menu_open = not st.session_state.menu_open
                st.session_state.menu_open = True

        with col2:
            st.markdown("### ETL App")
            
        if st.session_state.menu_open:
            st.button("🏠 Home", use_container_width=True, on_click=lambda: set_page("home"))
            st.button("💬 Chat", use_container_width=True, on_click=lambda: set_page("chat"))
            st.button("🤖 GPT", use_container_width=True, on_click=lambda: set_page("gpt"))
            st.button("🗺️ Route", use_container_width=True, on_click=lambda: set_page("route"))
            st.button("✈️ Travel", use_container_width=True, on_click=lambda: set_page("travel"))
            st.button("🚪 Logout", use_container_width=True, on_click=do_logout)

    # --- DESKTOP NÉZET ---
    else:
        col1, col2, col3, col4, col5, col6  = st.columns([1,1,1,1,1, 1])

        with col1:
            st.button("🏠 Home", use_container_width=True, on_click=lambda: set_page("home"))
            

        with col2:
            st.button("💬 Chat", use_container_width=True, on_click=lambda: set_page("chat"))
            
        with col3:
            st.button("🤖 GPT", use_container_width=True, on_click=lambda: set_page("gpt"))
            
        with col4:
            st.button("🗺️ Route", use_container_width=True, on_click=lambda: set_page("route"))
            

        with col5:
            st.button("✈️ Travel", use_container_width=True, on_click=lambda: set_page("travel"))
            

        with col6:
            st.button("🚪 Logout", use_container_width=True, on_click=do_logout)
            


# --- helper funkciók ---
def set_page(page):
    st.session_state.page = page
    st.session_state.menu_open = False
    st.rerun()

def do_logout():
    logout(st.session_state["token"])
    st.session_state.clear()
    st.rerun()
# --- PAGE CONTENT ---
def home():
    st.title("🏠 Main Page")
    #st.write("Ez a kezdőképernyő")

def chat():
    st.title("💬 Chat oldal")
    st.write("Itt jön a ChatGPT rész")




# --- RENDER ---
navbar()

if st.session_state.page == "home":
    home()

elif st.session_state.page == "chat":
    chatgpt.render(client, user, username, lastlogin ,cookies)
    
elif st.session_state.page == "gpt":
    gpt.render(client, user, username, lastlogin ,cookies)

elif st.session_state.page == "route":
    route.render(client, user, username, lastlogin ,cookies)
    
elif st.session_state.page == "travel":
    travel.load(client, user, username, lastlogin ,cookies)







