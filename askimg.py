import os
import json
from PIL import Image
import streamlit as st
import google.generativeai as genai

working_directory= os.path.dirname(os.path.abspath(__file__))

config_file_path=f"{working_directory}/config.json"
config_data=json.load(open(config_file_path))
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

def get_gemini_response(input,image,prompt):
    response=model.generate_content([input,image[0],prompt])
    return response.text 

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type":uploaded_file.type,
                "data":bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file Uploaded")

st.set_page_config(page_title="ASK to Image")

st.header("Ask about image")

uploaded_file = st.file_uploader("Choose an image ...",type=["jpg","jpeg","png"])
image=""
if uploaded_file is not None:
    image=Image.open(uploaded_file)
    st.image(image,caption="Uploaded Image",use_column_width=True)
input = st.text_input("Input Prompt: ", key=input)
submit = st.button("Tell me about the image")

input_prompt = """
 As an expert in image analysis, your task is to thoroughly examine the uploaded image and provide detailed insights based on the following:

Object Identification: Identify all visible objects, their attributes (e.g., color, size, shape, texture, and position), and relationships between them.
Text Recognition: Extract and interpret any text within the image, noting its content, context, font, and placement.
Contextual Understanding: Provide a comprehensive description of the scene, including relevant context, objects, and any other notable details.
You will then respond to the user’s query, using the information extracted from the image to provide an accurate and detailed answer. The user may ask any question related to the image, and you should tailor your response to the query while referencing relevant image details
Answer with precision and clarity based on the image content.
"""

if submit:
    image_data = input_image_details(uploaded_file)
    respose= get_gemini_response(input_prompt,image_data,input)
    st.subheader("The Response is")
    st.write(respose)


