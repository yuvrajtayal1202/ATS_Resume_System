import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import pdfplumber
from dotenv import load_dotenv

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use flash (better quota)
model = genai.GenerativeModel("gemini-1.5-flash")

# Extract resume text
def extract_text_from_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf_file:
            for page in pdf_file.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except:
        reader = pdf.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text.strip()

# Generate ATS response
def ats_match_prompt(job_desc, resume_text):
    return f"""
You are an ATS (Applicant Tracking System). Compare the candidate's resume against the job description.

Job Description:
{job_desc}

Candidate Resume:
{resume_text}

Tasks:
1. Provide a **percentage match** between the resume and the job description.
2. List key strengths.
3. Highlight missing skills/keywords.
4. Recommend improvements.

Important:
- Start with ATS Match: XX%
- Then structured explanation.
"""

def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text if response else "No response."

# Streamlit UI



st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    # layout="wide",
    initial_sidebar_state="expanded",
    # menu_items={
    #     'Get Help': 'https://www.example.com/help',
    #     'About': '# This is a sample Streamlit app.'
    # }
)


st.title("📄 ATS Resume Analyzer")

job_desc = st.text_area("Paste Job Description:", height=200)
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if st.button("🔍 Analyze Resume"):
    if uploaded_file and job_desc.strip():
        with st.spinner("Analyzing..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            if not resume_text:
                st.error("⚠️ Could not extract text. Please upload a text-based resume.")
            else:
                prompt = ats_match_prompt(job_desc, resume_text)
                result = generate_response(prompt)
                st.subheader("📊 ATS Analysis")
                st.write(result)
                with st.expander("🔍 Preview Extracted Resume Text"):
                    st.text_area("Resume Text", resume_text[:4000], height=300)
    else:
        st.warning("Please upload a resume and provide a job description.")
