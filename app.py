import streamlit as st
import requests
import os

st.title("📚 AI Notes Maker")

# API keys (from Streamlit Secrets)
HF_API_KEY = os.getenv("API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")

# Hugging Face API
HF_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# 🔹 OCR Function
def extract_text_from_image(file):
    url = "https://api.ocr.space/parse/image"
    
    payload = {
        'apikey': OCR_API_KEY,
        'language': 'eng'
    }
    
    files = {'file': file}

    response = requests.post(url, data=payload, files=files)
    result = response.json()

    if result.get("ParsedResults"):
        return result['ParsedResults'][0]['ParsedText']
    else:
        return "❌ Could not extract text from image"

# 🔹 Notes Generator
def generate_notes(text, note_type):
    try:
        response = requests.post(HF_URL, headers=HF_HEADERS, json={"inputs": text})
        summary = response.json()[0]["summary_text"]

        if note_type == "Short Notes":
            points = summary.split(".")
            return "\n".join(["- " + p.strip() for p in points if p.strip()])
        else:
            return "📘 Long Notes:\n\n" + summary
    except:
        return "❌ Error generating notes. Try again."

# 🔹 UI
option = st.radio("Choose Input Type:", ["Text", "Image"])
text = ""

if option == "Text":
    text = st.text_area("Enter your notes:")

if option == "Image":
    file = st.file_uploader("Upload image")
    if file:
        st.image(file)
        text = extract_text_from_image(file)

note_type = st.selectbox("Select Notes Type:", ["Long Notes", "Short Notes"])

if st.button("Generate Notes"):
    if text:
        result = generate_notes(text, note_type)
        st.success("✅ Notes Generated!")
        st.write(result)

        # Download button
        st.download_button(
            label="📝 Download Notes",
            data=result,
            file_name="notes.txt",
            mime="text/plain"
        )
    else:
        st.warning("Please enter or upload content!")
