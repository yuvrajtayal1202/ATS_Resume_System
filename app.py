from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai
import io
import pdfplumber

# ---------------- Gemini API Config ----------------
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load Gemini Vision model
vision_model = genai.GenerativeModel("gemini-1.5-flash") 


# ---------------- Helper Functions ----------------
def get_gemini_response(job_desc, resume_text, prompt):
    """
    Generate a response using Gemini Vision model.
    """
    if not resume_text.strip():
        return "⚠️ Resume text could not be extracted. Please try another PDF."

    input_text = f"""
    Job Description:
    {job_desc}

    Candidate Resume:
    {resume_text}

    Task: {prompt}
    """
    try:
        response = vision_model.generate_content([input_text])
        return response.text if response and response.text else "No response received."
    except Exception as e:
        return f"Error from Gemini API: {e}"


def input_pdf(file_bytes):
    """
    Extract text from PDF using two approaches:
    1. Try Gemini Vision OCR (page by page).
    2. If empty, fallback to pdfplumber (direct text extraction).
    """
    text = ""

    # ---- Try Gemini Vision OCR first ----
    try:
        images = pdf2image.convert_from_bytes(file_bytes)
        for image in images:
            response = vision_model.generate_content(
                ["Extract all text from this resume page:", image]
            )
            if response and response.text:
                text += response.text + "\n"
    except Exception as e:
        print("Gemini Vision failed:", e)

    # ---- Fallback to pdfplumber ----
    if not text.strip():
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            return f"Error extracting text: {e}"

    return text.strip()


# ---------------- Streamlit UI ----------------
st.title("📄 ATS Resume System with Gemini Vision")

# Job description input
input_text = st.text_area("Job Description:", key="input")

# PDF uploader
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])


# Action buttons
submit1 = st.button("📋 Tell me about my resume")
submit2 = st.button("🛠️ How can I improve my skills?")
submit3 = st.button("🔑 What keywords are missing?")
submit4 = st.button("📊 Percentage match with job description?")

resume_text = ""
file_bytes = None

if uploaded_file is not None:
    st.success("✅ PDF uploaded successfully!")
    if file_bytes is None:  # make sure we don't read it twice
        file_bytes = uploaded_file.read()
    resume_text = input_pdf(file_bytes)

if resume_text.strip():
    if submit1:
        st.subheader("Resume Summary")
        st.write(get_gemini_response(
            input_text,
            resume_text,
            "Summarize this resume and highlight strengths."
        ))

    elif submit2:
        st.subheader("Skill Improvement Suggestions")
        st.write(get_gemini_response(
            input_text,
            resume_text,
            "Suggest specific skills I should learn to better match the job description."
        ))

    elif submit3:
        st.subheader("Missing Keywords")
        st.write(get_gemini_response(
            input_text,
            resume_text,
            "List important keywords from the job description that are missing in my resume."
        ))

    elif submit4:
        st.subheader("ATS Match Percentage")
        st.write(get_gemini_response(
            input_text,
            resume_text,
            "Compare the job description and resume, and give a percentage match for ATS systems. "
            "Provide just a percentage value with short reasoning."
        ))
else:
    st.warning("⚠️ No text extracted from PDF. Try uploading another file or check if it’s scanned (image-only).")
