# modules/email_generator.py
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_cold_email(candidate_name: str, candidate_summary: str, 
                         job_title: str, company_name: str, 
                         recruiter_name: str = "Hiring Manager") -> dict:
    """
    Generates a cold email, LinkedIn message, and follow-up email.
    """
    prompt = f"""
You are an expert career coach helping a fresher write job outreach messages.

Generate professional outreach messages for:
- Candidate: {candidate_name}
- Candidate Summary: {candidate_summary}
- Target Job: {job_title} at {company_name}
- Recruiter/Contact: {recruiter_name}

Return a JSON with these exact keys:
- "cold_email_subject": subject line for the cold email
- "cold_email_body": full cold email (professional, 150-200 words)
- "linkedin_message": LinkedIn connection request message (under 300 characters)
- "followup_email_subject": follow-up email subject
- "followup_email_body": follow-up email to send after 1 week (100-150 words)

IMPORTANT: Return ONLY valid JSON, no extra text.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except:
        result = {
            "cold_email_subject": "Application for " + job_title,
            "cold_email_body": raw,
            "linkedin_message": "Hi, I'm interested in opportunities at " + company_name,
            "followup_email_subject": "Following up on my application",
            "followup_email_body": "I wanted to follow up on my previous email."
        }

    return result