import streamlit as st
import fitz  # pymupdf
import pytesseract
from PIL import Image
import io
import re
from pymongo import MongoClient

# MongoDB setup
MONGO_URI = "mongodb+srv://<db_username>:<db_password>@brainiac.hxcvwj1.mongodb.net/?retryWrites=true&w=majority&appName=brainiac"
client = MongoClient(MONGO_URI)
db = client.real_estate
collection = db.properties

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("🏠 Auto Property Info Organizer")

uploaded_file = st.file_uploader("Upload PDF, Image, or Paste Text", type=["pdf", "png", "jpg", "jpeg"])

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def classify_fields(text):
    price = re.search(r"(Price|ราคา)\D*(\d[\d,\.]*)", text, re.IGNORECASE)
    area = re.search(r"(Area|Size|ขนาด)\D*(\d+)\s*(sqm|ตรม)", text, re.IGNORECASE)
    location = re.search(r"(Location|ที่ตั้ง)\D*(.*)", text, re.IGNORECASE)
    
    return {
        "price": price.group(2) if price else None,
        "area": area.group(0) if area else None,
        "location": location.group(2).strip() if location else None,
        "raw_text": text
    }

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type.startswith("image"):
        text = extract_text_from_image(uploaded_file)
    else:
        text = uploaded_file.read().decode()

    st.subheader("🧾 Extracted Text")
    st.text_area("Preview", text, height=200)

    if st.button("📥 Save to MongoDB"):
        data = classify_fields(text)
        collection.insert_one(data)
        st.success("Saved to database!")

st.subheader("📚 Stored Properties")
for doc in collection.find().sort("_id", -1):
    st.markdown(f"""
    **Price**: {doc.get('price')}
    **Area**: {doc.get('area')}
    **Location**: {doc.get('location')}
    ---
    """)
