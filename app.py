import streamlit as st
import requests
from PIL import Image
import pytesseract
import os

st.title("📚 AI Notes Maker")

# Secure API key
API_KEY = os.getenv("API_KEY")

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {API_KEY}"}

def generate_notes(text, note_type):
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    summary = response.json()[0]["summary_text"]

    if note_type == "Short Notes":
        points = summary.split(".")
        return "\n".join(["- " + p.strip() for p in points if p.strip()])
    else:
        return "📘 Long Notes:\n\n" + summary

# UI
option = st.radio("Choose Input Type:", ["Text", "Image"])
text = ""

if option == "Text":
    text = st.text_area("Enter your notes:")

if option == "Image":
    file = st.file_uploader("Upload image")
    if file:
        img = Image.open(file)
        st.image(img)
        text = pytesseract.image_to_string(img)

note_type = st.selectbox("Select Notes Type:", ["Long Notes", "Short Notes"])

if st.button("Generate Notes"):
    if text:
        result = generate_notes(text, note_type)
        st.write(result)
    else:
        st.warning("Please enter something!")
