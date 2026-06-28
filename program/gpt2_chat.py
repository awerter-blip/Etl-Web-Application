import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


MODEL_NAME = "distilgpt2"
#MODEL_NAME = "Mistral-7B-Instruct"


@st.cache_resource
def load_model():

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME
    )

    model.eval()

    return model, tokenizer


model, tokenizer = load_model()


def generate_text(prompt):

    formatted_prompt = f"""
User: {prompt}
Assistant:
"""

    inputs = tokenizer(
        formatted_prompt,
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    with torch.no_grad():

        output = model.generate(
            **inputs,
            max_new_tokens=80,
            temperature=0.5,
            top_k=50,
            top_p=0.95,
            do_sample=True,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_text = tokenizer.decode(
        output[0],
        skip_special_tokens=True
    )

    # Assistant válasz kivágása
    if "Assistant:" in generated_text:

        generated_text = generated_text.split(
            "Assistant:"
        )[-1].strip()

    return generated_text