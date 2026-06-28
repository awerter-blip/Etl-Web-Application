import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

st.set_page_config(page_title="Local Chat + File Demo", page_icon="📄🤖", layout="wide")

st.title("📄🤖 Local Chat + File Summarization")

# -----------------------------
# Modell betöltése
# -----------------------------
@st.cache_resource
def load_model():
    model_name = "gpt2"  # CPU-barát demo modell
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

# -----------------------------
# Session state init
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Reset chat
# -----------------------------
if st.button("🔄 Reset chat"):
    st.session_state.messages = []

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader("Tölts fel egy szöveges fájlt (.txt)", type=["txt"])
if uploaded_file:
    file_content = uploaded_file.read().decode("utf-8")
    st.text_area("Fájl tartalma", file_content, height=150)

    # Ha van tartalom, összefoglaljuk
    if st.button("📄 Összefoglalás"):
        summary_prompt = f"Összefoglalás:\n{file_content}\nÖsszegzés:"
        inputs = tokenizer(summary_prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=inputs['input_ids'].shape[1]+100)
        summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
        summary_text = summary.split(file_content)[-1].strip()
        st.session_state.messages.append({"role": "ai", "content": f"Fájl összefoglaló:\n{summary_text}"})

# -----------------------------
# Chat input
# -----------------------------
prompt = st.text_input("Írj be valamit a chatbe:", key="input")

if st.button("Küldés"):
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Modell input a teljes beszélgetésből
        full_prompt = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages]
        )

        inputs = tokenizer(full_prompt, return_tensors="pt")
        outputs = model.generate(**inputs, max_length=inputs['input_ids'].shape[1]+50)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        ai_response = response.split(prompt)[-1].strip()
        st.session_state.messages.append({"role": "ai", "content": ai_response})
    else:
        st.warning("Adj meg valamit!")

# -----------------------------
# Chat megjelenítése scrollable boxban
# -----------------------------
chat_html = ""
for msg in st.session_state.messages:
    if msg["role"] == "user":
        chat_html += f"<div style='background-color:#DCF8C6; padding:8px; border-radius:10px; margin:5px 0'><b>Te:</b> {msg['content']}</div>"
    else:
        chat_html += f"<div style='background-color:#F1F0F0; padding:8px; border-radius:10px; margin:5px 0'><b>AI:</b> {msg['content']}</div>"

st.markdown(f"<div style='max-height:400px; overflow-y:auto'>{chat_html}</div>", unsafe_allow_html=True)