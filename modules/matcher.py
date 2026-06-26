# modules/matcher.py
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def match_resume_to_job(resume_text: str, job_description: str) -> dict:
    """
    Compares resume with a job description.
    Returns match percentage, missing skills, and recommendations.
    """
    prompt = f"""
You are a professional recruiter and resume matcher.

Compare the following resume with the job description and return a JSON with:
- "match_score": a number between 0 and 100 (percentage match)
- "matching_skills": list of skills in resume that match the job
- "missing_skills": list of skills required by job but missing in resume
- "recommendation": a short paragraph on how to improve the resume for this job

Resume:
{resume_text[:2000]}

Job Description:
{job_description[:1000]}

IMPORTANT: Return ONLY valid JSON, no extra text.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
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
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": raw
        }

    return result