import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

def get_cookies():
    cookies = EncryptedCookieManager(
        prefix="my_app",
        password="super_secret_key"
    )

    if not cookies.ready():
        st.stop()

    return cookies