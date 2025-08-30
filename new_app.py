import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate response using Gemini
def generate_response(prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")  # or gemini-1.5-flash
    response = model.generate_content(prompt)
    return response.text

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = pdf.PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text

# ATS Prompt Template
def ats_match_prompt(job_desc, resume_text):
    return f"""
You are an ATS (Applicant Tracking System). Compare the candidate's resume against the job description and give a detailed analysis.

Job Description:
{job_desc}

Candidate Resume:
{resume_text}

Tasks:
1. Provide a **percentage match** between the resume and the job description (0–100%).
2. List the **key strengths** of the resume that align with the job description.
3. Highlight the **missing skills/keywords** that ATS would look for but are not found in the resume.
4. Give **actionable recommendations** for improving the resume to increase the ATS score.

Important:
- Start with the percentage match on the first line (example: "ATS Match: 76%").
- Then give the detailed explanation.
- Keep the response clear and structured.
"""

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="ATS Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 ATS Resume Analyzer with Gemini")

# Job description input
job_desc = st.text_area("Paste the Job Description here:", height=200)

# Resume upload
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

# Analyze button
if st.button("🔍 Analyze Resume"):
    if uploaded_file and job_desc.strip():
        with st.spinner("Extracting resume and analyzing..."):
            # Extract resume text
            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text.strip():
                st.error("⚠️ No text could be extracted from the PDF. Please upload a text-based resume.")
            else:
                # Build prompt
                prompt = ats_match_prompt(job_desc, resume_text)

                # Get Gemini response
                result = generate_response(prompt)

                # Display result
                st.subheader("📊 ATS Analysis Result")
                st.write(result)

                # Optional: show extracted resume preview
                with st.expander("🔍 Preview Extracted Resume Text"):
                    st.text_area("Resume Text", resume_text[:2000], height=300)
    else:
        st.warning("⚠️ Please provide both a job description and a resume.")
