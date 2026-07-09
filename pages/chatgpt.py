
import streamlit as st
from cookies import get_cookies
from openai import OpenAI
import os
import uuid
from db import init_db
from auth import login, register, last_login, username, get_user_by_token, logout
from messages import save_message, load_messages, remove_messages


def render(client, user, username, lastlogin ,cookies):
    
    # Page Title
    # Page Config
    st.set_page_config(page_title="Mini ChatGpt", layout="wide", page_icon="chatgpt.png")
   

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



    # Chat GPT Header
    st.image("chatgpt.png", width=50)
    st.title("Mini Chat Gpt")
    
    # User neve és kijelentkezés
    # CSS
    #st.markdown("""
    #<style>
    #.custom-container {
     #   background-color: #f0f2f6;
      #  border: 2px solid #4CAF50;
       # border-radius: 10px;
       # padding: 20px;
    #}
    #</style>
    #""", unsafe_allow_html=True)


    col1, col2 = st.columns(2)

    
    with col1:
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        st.markdown(f"***Hello {username["name"]}.***")
        st.markdown(f"How are you? Please tell me how can i help you?")
        st.markdown('</div>', unsafe_allow_html=True)
                
    with col2:
        st.markdown(f"Last login: {lastlogin}")


    #st.markdown('</div>', unsafe_allow_html=True)

    # Avatarok
    user_avatar = "user.jpg"
    robot_avatar = "chatgpt.png"



    # Header Section
    header = st.container()

    # Sidebar

    with st.sidebar:
        
        model =st.selectbox("Choose a model", ["gpt-5.4-nano"], 0)
        temp = st.slider("Temperature", 0.0, 1.0, 0.7)
        
        if st.sidebar.button("Save settings"):
            model = model
            temp = temp
            st.markdown("**:green[Settings saved]**")
            
    # Üzenetek betöltése  
    chat_type = 1    
    if "messages_1" not in st.session_state:
        st.session_state.messages_1 = load_messages(user, chat_type)    
            
            
    for msg_1 in st.session_state.messages_1:
        avatar = user_avatar if msg_1["role"] == "user" else robot_avatar

        with st.chat_message(msg_1["role"], avatar=avatar):
            st.markdown(msg_1["content"])

    # Delete messages gomb
    if st.button("🧹 Delete Previous Conversations"):
        with st.spinner("Wait for the deletion...", show_time=True):
            remove_messages(user, chat_type)
            st.session_state.messages_1 = []
            
        
    # Üzenetek ismételt betöltése   
    if "messages_1" not in st.session_state:
        st.session_state.messages_1 = load_messages(user, chat_type)    
            
            
    for msg_1 in st.session_state.messages_1:
        avatar = user_avatar if msg_1["role"] == "user" else robot_avatar

        with st.chat_message(msg_1["role"], avatar=avatar):
            st.markdown(msg_1["content"])
                

    # Add be a prompt-ot
    if prompt := st.chat_input("Please write your prompt here:"):
        # User üzenet mentése
        st.session_state.messages_1.append({"role": "user", "content": prompt})
        save_message(user, "user",chat_type ,prompt)
            
        # Megjelenítés
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(prompt)
                
        with st.spinner("Wait for the answer...", show_time=True):
            
                
            # AI válasz generálása
            with st.chat_message("assistant", avatar=robot_avatar):
                response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages_1,
                temperature=temp,
                )
                reply = response.choices[0].message.content
                #reply = "Dummy"

            st.markdown(reply)
                
            # AI válasz mentése
        st.session_state.messages_1.append({"role": "assistant", "content": reply})
        save_message(user, "assistant",chat_type ,reply)