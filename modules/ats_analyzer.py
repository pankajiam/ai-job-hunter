# modules/ats_analyzer.py
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_resume(resume_text: str) -> dict:
    """
    Sends resume text to Groq AI and gets back:
    - ATS score (0-100)
    - Skills found
    - Missing keywords
    - Suggestions
    """
    prompt = f"""
You are an expert ATS (Applicant Tracking System) analyzer.

Analyze the following resume and return a JSON response with these exact keys:
- "ats_score": a number between 0 and 100
- "skills_found": a list of skills/technologies found in the resume
- "missing_keywords": a list of commonly expected keywords that are missing
- "suggestions": a list of 5 improvement suggestions
- "summary": a 2-3 sentence professional summary of the candidate

Resume Text:
{resume_text}

IMPORTANT: Return ONLY valid JSON, no extra text.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    import json
    raw = response.choices[0].message.content.strip()
    
    # Sometimes AI adds ```json ... ``` around it, so we clean that
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    
    try:
        result = json.loads(raw)
    except:
        result = {
            "ats_score": 50,
            "skills_found": ["Could not parse skills"],
            "missing_keywords": ["Could not parse missing keywords"],
            "suggestions": ["Please try again"],
            "summary": raw  # show raw response as summary if JSON fails
        }
    
    return result