import streamlit as st
import re
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import os
from datetime import datetime

nltk.download("punkt")
nltk.download("stopwords")

# Helper functions
def extract_text_from_pdf(pdf_file):
    """Extract text from the uploaded PDF file."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_skills(text, job_field):
    """Extract skills based on the selected job field."""
    skills_dict = {
        "software": ["Python", "Java", "C++", "Machine Learning", "Data Analysis", "NLP", "Deep Learning", "SQL", "AWS", "Docker", "Kubernetes"],
        "finance": ["Accounting", "Financial Modeling", "Excel", "VBA", "SQL", "Python", "Tableau"],
        "marketing": ["SEO", "Social Media", "Content Creation", "Google Analytics", "Advertising", "Branding", "Email Marketing"],
        "general": ["Communication", "Problem-Solving", "Teamwork", "Leadership", "Adaptability", "Time Management"]
    }
    skills = [skill for skill in skills_dict.get(job_field, skills_dict["general"]) if skill.lower() in text.lower()]
    return list(set(skills))

def extract_info(text):
    """Extract name, email, phone, work experience, and education from text."""
    name_pattern = r"^([A-Z][a-z]+)\s([A-Z][a-z]+)"
    name_match = re.search(name_pattern, text)
    name = f"{name_match.group(1)} {name_match.group(2)}" if name_match else None
    
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    email = re.findall(email_pattern, text)[0] if re.findall(email_pattern, text) else None
    
    phone_pattern = r"\b\d{10}\b|\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4}"
    phone = re.findall(phone_pattern, text)[0] if re.findall(phone_pattern, text) else None
    
    experience_pattern = r"Experience\s*(.+?)(?=Projects|Technical Skills|Education)"
    experience = re.search(experience_pattern, text, re.DOTALL).group(1).strip() if re.search(experience_pattern, text, re.DOTALL) else None
    
    education_pattern = r"Education\s*(.+?)(?=Experience|Projects)"
    education = re.search(education_pattern, text, re.DOTALL).group(1).strip() if re.search(education_pattern, text, re.DOTALL) else None
    
    return name, email, phone, experience, education

def save_to_excel(data, file_path="parsed_resumes.xlsx"):
    """Save parsed data to an Excel file."""
    if os.path.exists(file_path):
        existing_data = pd.read_excel(file_path)
        updated_data = pd.concat([existing_data, pd.DataFrame([data])], ignore_index=True)
    else:
        updated_data = pd.DataFrame([data])
    updated_data.to_excel(file_path, index=False)

# Streamlit App
def main():
    st.title("Automated Resume Parser")
    st.write("Upload a resume in PDF format and select a job field to parse details.")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    job_field = st.selectbox("Select Job Field", ["software", "finance", "marketing", "general"])
    
    if uploaded_file:
        st.write("Processing your resume...")
        
        # Extract data
        text = extract_text_from_pdf(uploaded_file)
        name, email, phone, work_experience, education = extract_info(text)
        skills = extract_skills(text, job_field)
        
        # Display parsed details
        st.subheader("Parsed Details")
        st.write(f"**Name:** {name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Phone Number:** {phone}")
        st.write(f"**Work Experience:** {work_experience if work_experience else 'No work experience found.'}")
        st.write(f"**Education:** {education if education else 'No education details found.'}")
        st.write(f"**Skills:** {', '.join(skills) if skills else 'No relevant skills found.'}")
        
        # Prepare data for saving
        parsed_data = {
            "Name": name,
            "Email": email,
            "Phone Number": phone,
            "Work Experience": work_experience,
            "Education": education,
            "Skills": ", ".join(skills)
        }
        
        # Save data to Excel
        save_to_excel(parsed_data)
        st.success("Parsed data has been successfully saved to `parsed_resumes.xlsx`.")

if __name__ == "__main__":
    main()
