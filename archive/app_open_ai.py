import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch



st.title("🤖 Local GPT2 Chat Demo")

# Modell betöltése
@st.cache_resource
def load_model():
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

# Prompt input
prompt = st.text_area("Írd be a promptot:")

if st.button("Generálás"):
    if prompt:
        inputs = tokenizer(prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=100)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        st.write("**AI válasz:**")
        st.write(response)
    else:
        st.warning("Adj meg promptot!")
        






