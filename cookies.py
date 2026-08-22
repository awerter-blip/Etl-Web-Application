import streamlit as st
import os
from streamlit_cookies_manager_ext import EncryptedCookieManager


def get_cookies():

    cookies = EncryptedCookieManager(
        prefix="my_app/",
        password=st.secrets["COOKIES_PASSWORD"]
    )

    if not cookies.ready():
        st.stop()

    return cookies