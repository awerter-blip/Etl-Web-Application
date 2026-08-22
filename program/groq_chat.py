import streamlit as st
from openai import OpenAI

# -----------------------------------
# Groq client
# -----------------------------------
client = OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

def generate_text(prompt, messages):
    # user message
    messages.append({
        "role": "user",
        "content": prompt
    })
    completion = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=messages,

        temperature=0.7,

        max_tokens=300
        )

    response = completion.choices[0].message.content

    return response