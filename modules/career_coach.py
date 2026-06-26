# modules/career_coach.py
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_career_roadmap(target_role: str, current_skills: str) -> dict:
    """
    Generates a personalized career roadmap for a fresher.
    """
    prompt = f"""
You are an expert AI career coach helping freshers and students.

A student wants to become a: {target_role}
Their current skills are: {current_skills}

Generate a detailed career roadmap as JSON with:
- "skill_gaps": list of skills they need to learn
- "learning_roadmap": list of steps with "step", "duration", "resources" keys
- "recommended_projects": list of 4-5 project ideas to build portfolio
- "interview_prep": list of 10 important interview topics/questions for this role
- "timeline": estimated timeline to be job-ready (e.g., "3-6 months")
- "motivational_message": a short encouraging message

IMPORTANT: Return ONLY valid JSON, no extra text.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
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
            "skill_gaps": ["Unable to parse - please try again"],
            "learning_roadmap": [],
            "recommended_projects": [],
            "interview_prep": [],
            "timeline": "3-6 months",
            "motivational_message": raw
        }

    return result