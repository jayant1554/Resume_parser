import streamlit as st
import re
from PyPDF2 import PdfReader
import pandas as pd

# Helper functions
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_skills(text, job_field):
    skills_dict = {
        "software": ["Python", "Java", "C++", "Machine Learning", "Data Analysis", "NLP", "Deep Learning", "SQL", "AWS", "Docker", "Kubernetes"],
        "finance": ["Accounting", "Financial Modeling", "Excel", "VBA", "SQL", "Python", "Tableau"],
        "marketing": ["SEO", "Social Media", "Content Creation", "Google Analytics", "Advertising", "Branding", "Email Marketing"],
        "general": ["Communication", "Problem-Solving", "Teamwork", "Leadership", "Adaptability", "Time Management"]
    }
    skills = [skill for skill in skills_dict.get(job_field, skills_dict["general"]) if skill.lower() in text.lower()]
    return list(set(skills))

def extract_info(text):
    # Extract name
    name_pattern = r"^([A-Z][a-z]+)\s([A-Z][a-z]+)"
    name_match = re.search(name_pattern, text)
    if name_match:
        name = f"{name_match.group(1)} {name_match.group(2)}"
    else:
        name = None

    # Extract email
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else None

    # Extract phone number
    phone_pattern = r"\b\d{10}\b|\(\d{3}\)\s?\d{3}-\d{4}|\d{3}-\d{3}-\d{4}"
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else None

    # Extract work experience
    experience_pattern = r"Experience\s*(.+?)(?=Projects|Technical Skills)"
    experience_match = re.search(experience_pattern, text, re.DOTALL)
    if experience_match:
        work_experience = experience_match.group(1).strip()
    else:
        work_experience = None

    # Extract education
    education_pattern = r"Education\s*(.+?)(?=Experience|Projects)"
    education_match = re.search(education_pattern, text, re.DOTALL)
    if education_match:
        education = education_match.group(1).strip()
    else:
        education = None

    return name, email, phone, work_experience, education

# Streamlit App
def main():
    st.title("Automated Resume Parser")
    st.write("Upload a resume in PDF format and select a job field to parse details.")

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    job_field = st.selectbox("Select Job Field", ["software", "finance", "marketing", "general"])

    if uploaded_file:
        st.write("Processing your resume...")
        text = extract_text_from_pdf(uploaded_file)
        name, email, phone, work_experience, education = extract_info(text)
        skills = extract_skills(text, job_field)

        # Store the extracted information in an Excel sheet
        data = {
            "Name": [name],
            "Email": [email],
            "Phone": [phone],
            "Work Experience": [work_experience],
            "Education": [education],
            "Skills": [', '.join(skills)]
        }
        df = pd.DataFrame(data)
        df.to_excel("resume_data.xlsx", index=False)

        st.subheader("Parsed Details")
        st.write(f"**Name:** {name}")
        st.write(f"**Email:** {email}")
        st.write(f"**Phone Number:** {phone}")
        st.write(f"**Work Experience:** {work_experience if work_experience else 'No work experience found.'}")
        st.write(f"**Education:** {education if education else 'No education details found.'}")
        st.write(f"**Skills:** {', '.join(skills) if skills else 'No relevant skills found.'}")

        st.write("Resume data has been saved to 'resume_data.xlsx'.")

if __name__ == "__main__":
    main()