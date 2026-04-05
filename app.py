
import streamlit as st
import requests
import os

st.title("📚 AI Notes Maker")

# API keys (Better to use st.secrets for Streamlit Cloud)
HF_API_KEY = os.getenv("API_KEY")
OCR_API_KEY = os.getenv("OCR_API_KEY")

HF_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HF_HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

# Initialize session state for text
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""

def extract_text_from_image(file):
    url = "https://api.ocr.space/parse/image"
    payload = {'apikey': OCR_API_KEY, 'language': 'eng'}
    # Pass the file name and the file object itself
    files = {file.name: file} 
    
    try:
        response = requests.post(url, data=payload, files=files)
        result = response.json()
        if result.get("ParsedResults"):
            return result['ParsedResults'][0]['ParsedText']
        return "❌ Could not extract text from image"
    except Exception as e:
        return f"❌ OCR Error: {str(e)}"

def generate_notes(text, note_type):
    try:
        response = requests.post(HF_URL, headers=HF_HEADERS, json={"inputs": text})
        data = response.json()
        
        # Handle model loading or API errors
        if isinstance(data, dict) and "error" in data:
            return f"❌ API Error: {data['error']}"
            
        summary = data[0]["summary_text"]

        if note_type == "Short Notes":
            points = summary.split(".")
            return "\n".join(["- " + p.strip() for p in points if p.strip()])
        return "📘 Long Notes:\n\n" + summary
    except Exception as e:
        return f"❌ Error generating notes: {str(e)}"

# UI Logic
option = st.radio("Choose Input Type:", ["Text", "Image"])

if option == "Text":
    # Update session state directly from text area
    st.session_state.extracted_text = st.text_area("Enter your notes:", value=st.session_state.extracted_text)

else:
    file = st.file_uploader("Upload image", type=["jpg", "png", "jpeg"])
    if file:
        st.image(file)
        # Only run OCR if we don't have text yet or a new file is uploaded
        if st.button("Extract Text from Image"):
            with st.spinner("Scanning image..."):
                st.session_state.extracted_text = extract_text_from_image(file)
            st.info("Text Extracted!")

# Display current working text
if st.session_state.extracted_text:
    with st.expander("View/Edit Extracted Content"):
        st.session_state.extracted_text = st.text_area("Content:", value=st.session_state.extracted_text, height=150)

note_type = st.selectbox("Select Notes Type:", ["Long Notes", "Short Notes"])

if st.button("Generate Notes"):
    if st.session_state.extracted_text:
        with st.spinner("Summarizing..."):
            result = generate_notes(st.session_state.extracted_text, note_type)
        
        if "❌" not in result:
            st.success("✅ Notes Generated!")
            st.write(result)
            st.download_button("📝 Download Notes", result, "notes.txt", "text/plain")
        else:
            st.error(result)
