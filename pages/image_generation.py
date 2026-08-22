import streamlit as st
import datetime
import json
import os
import io
import datetime
import requests
from PIL import Image
from openai import OpenAI, BadRequestError
import base64

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://api.openai.com/v1"
)


def create_file(uploaded_file):
    # Feltöltött kép bytes
    file_bytes = uploaded_file.getvalue()

    # OpenAI Files API
    file = client.files.create(
        file=(
            uploaded_file.name,
            file_bytes,
            uploaded_file.type
        ),
        purpose="vision"
    )

    return file.id


def encode_image(uploaded_file):
    image_bytes = uploaded_file.getvalue()
    return base64.b64encode(image_bytes).decode("utf-8")

def edit_image(prompt, image_file, width, height):

    try:

        result = client.images.edit(
            model="gpt-image-1-mini",
            image=image_file,
            prompt=prompt,
            size="auto"
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(
            image_base64
        )

        return image_bytes

    except BadRequestError as e:

        if "moderation_blocked" in str(e):

            st.error(
                "A kép vagy a megadott kérés "
                "fennakadt az OpenAI biztonsági ellenőrzésén."
            )
            error_body = e.body if isinstance(e.body, dict) else {}
            moderation_details = error_body.get("moderation_details") or {}
            categories = moderation_details.get("categories") or []
            stage = moderation_details.get("moderation_stage")

            hint = "This request could not be completed because it did not meet safety requirements."

            if "harassment" in categories:
                hint = "Try removing abusive or targeting language and focus on neutral visual details instead."
            elif stage == "input":
                hint = "Try revising the prompt or input images and submit the request again."
            elif stage == "output":
                hint = "The generated result was blocked by a safety check. Try changing the prompt and generating again."
            st.error(
                f"request_id: {e.request_id}\n"
                f"code: {e.code}\n"
                f"moderation_details: {moderation_details}\n"
                f"hint: {hint}"
            )

        else:

            st.error(
                f"OpenAI hiba: {e}"
            )

        return None    
        
def new_image(prompt):
    try:
        result = client.images.generate(model="gpt-image-1-mini", prompt=prompt, size="auto")
        
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        
        return image_bytes
    
    except BadRequestError as e:

        if "moderation_blocked" in str(e):

            st.error(
                "A kép vagy a megadott kérés "
                "fennakadt az OpenAI biztonsági ellenőrzésén."
            )
            error_body = e.body if isinstance(e.body, dict) else {}
            moderation_details = error_body.get("moderation_details") or {}
            categories = moderation_details.get("categories") or []
            stage = moderation_details.get("moderation_stage")

            hint = "This request could not be completed because it did not meet safety requirements."

            if "harassment" in categories:
                hint = "Try removing abusive or targeting language and focus on neutral visual details instead."
            elif stage == "input":
                hint = "Try revising the prompt or input images and submit the request again."
            elif stage == "output":
                hint = "The generated result was blocked by a safety check. Try changing the prompt and generating again."
            st.error(
                f"request_id: {e.request_id}\n"
                f"code: {e.code}\n"
                f"moderation_details: {moderation_details}\n"
                f"hint: {hint}"
            )

        else:

            st.error(
                f"OpenAI hiba: {e}"
            )

        return None  
    
def multi_images(prompt, main_image, sub_image):

    if main_image is None:
        st.warning("Válassz ki egy fő képet!")
        return None

    if not sub_image:
        st.warning("Válassz ki legalább egy további képet!")
        return None

    content = [
        {
            "type": "input_text",
            "text": prompt
        }
    ]

    # Fő kép
    main_file_id = create_file(main_image)

    content.append({
        "type": "input_image",
        "file_id": main_file_id
    })

    # További képek
    for image in sub_image:

        file_id = create_file(image)

        content.append({
            "type": "input_image",
            "file_id": file_id
        })

    response = client.responses.create(
        model="gpt-5.4-mini",
        input=[
            {
                "role": "user",
                "content": content
            }
        ],
        tools=[
            {
                "type": "image_generation"
            }
        ]
    )

    # DEBUG
    # st.write("TELJES RESPONSE:")
    # st.write(response)

    for output in response.output:

        if output.type == "image_generation_call":

            if output.status != "completed":
                st.warning("A képgenerálás nem sikerült.")

                # Ha van magyarázó szöveges válasz
                for item in response.output:

                    if item.type == "message":

                        for content_item in item.content:

                            if content_item.type == "output_text":
                                st.info(content_item.text)

                return None

            if output.result is None:
                st.warning("Az OpenAI nem adott vissza képet.")
                return None

            return base64.b64decode(output.result)

    st.warning("Nem érkezett kép az OpenAI-tól.")
    return None



def image_generation(user, username, lastlogin, cookies):
    
    st.set_page_config(
        page_title="Generate Image",
        layout="wide",
        page_icon="✈️"
    )

    st.divider()
    
    st.title("AI Image Editor")
    
    # Create Session States
    
    if "new_image" not in st.session_state:
        st.session_state.new_image = None
    
    if "edit_image" not in st.session_state:
        st.session_state.edit_image = None
    
    if "multiple_image" not in st.session_state:
        st.session_state.multiple_image = None
    
    # Define Tabs
    tab1, tab2, tab3 = st.tabs(["New Image", "Edit Image", "Create Image from Multiple Image"])
    
    # New Image
    with tab1:

        st.subheader("New Image")
        with st.form("Edit Image"):

            prompt = st.text_input(
                "Milyen képet szeretnél?"
            )

            generate_button = st.form_submit_button(
                "Generate Image"
            )
            if generate_button:
                with st.spinner("Generate image..."):
                    result = new_image(prompt)
                    
                    if result is not None:
                        st.session_state.new_image = result
            # Generált kép
            if st.session_state.new_image is not None:
                st.image(st.session_state.new_image, caption="Generated Image")
                    
                st.download_button(
                    label="⬇️ Kép letöltése",
                    data=st.session_state.new_image,
                    file_name="generated_image.jpg",
                    mime="image/jpg"
                )
                
            # Reset Button
            reset_button = st.form_submit_button("Clear Image")
            if reset_button:
                st.session_state.new_image = None
                st.rerun()
                        
                
                
        
    
    # Edit Image
    with tab2:

        with st.form("Modify Image"):

            uploaded_file = st.file_uploader(
                "Kép kiválasztása",
                type=["jpg", "jpeg", "png"]
            )

            prompt = st.text_input(
                "Mit szeretnél módosítani?"
            )

            generate_button = st.form_submit_button(
                "Generate Image"
            )

            if generate_button:

                if uploaded_file is None:
                    st.warning("Válassz ki egy képet!")

                elif not prompt:
                    st.warning("Add meg, hogy mit szeretnél módosítani!")

                else:

                    with st.spinner("Generate Image...."):

                        # Kép beolvasása
                        image = Image.open(uploaded_file)

                        # Méret lekérése
                        width, height = image.size

                        st.write(
                            f"Eredeti méret: {width} × {height}px"
                        )

                        # Átméretezés
                        image.thumbnail((1024, 1024))

                        width, height = image.size

                        st.write(
                            f"Küldött méret: {width} × {height}px"
                        )

                        # Bytes létrehozása
                        buffer = io.BytesIO()

                        image.save(
                            buffer,
                            format="PNG"
                        )

                        buffer.seek(0)

                        # OpenAI-nak küldhető fájlszerű objektum
                        image_file = (
                            "image.png",
                            buffer,
                            "image/png"
                        )

                        result = edit_image(
                            prompt,
                            image_file,
                            width,
                            height
                        )

                        if result is not None:

                            st.session_state.edit_image = result
        # Download button
        if st.session_state.edit_image is not None:
            st.image(
                st.session_state.edit_image,
                caption="Generated image"
                )
                        
            st.download_button(
                    label="⬇️ Kép letöltése",
                    data=st.session_state.edit_image,
                    file_name="generated_image.jpg",
                    mime="image/jpg"
                )
            # Reset button
        if st.session_state.edit_image is not None:
            reset_button = st.button("Clear Image")
            if reset_button:
                st.session_state.edit_image = None
                st.rerun()
    
    # Multiple Image
    with tab3:
        st.subheader("Create Image from Multiple Image")
        
        with st.form("Create New Image based on multiple Images"):
            
            # Main Image
            main_image = st.file_uploader(
                "Fő Kép kiválasztása",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False
            )
            
            
            
            sub_image = st.file_uploader(
                "1. Elem kép kiválasztása",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True
            )
            
            
            

            prompt = st.text_input(
                "Milyen képet szeretnél?"
            )

            generate_button = st.form_submit_button("Generate Image")
            
            if generate_button:
                with st.spinner("Generate Image..."):
                    result = multi_images(prompt, main_image, sub_image)
                    
                    if result is not None:
                        st.session_state.multiple_image = result
    
        if st.session_state.multiple_image is not None:
            st.image(st.session_state.multiple_image, caption="Generated image")
            
            st.download_button(
                    label="⬇️ Kép letöltése",
                    data=st.session_state.multiple_image,
                    file_name="generated_image.jpg",
                    mime="image/jpg"
                )
        # Reset button
        if st.session_state.multiple_image is not None:
            reset_button = st.button("Clear Image")
            if reset_button:
                st.session_state.multiple_image = None
                st.rerun()
                
                
            
                
        
    