# modules/job_search.py
# We use the JSearch API via RapidAPI (free tier available)
# OR we can use a mock/demo mode for testing without API keys

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_jobs_jsearch(role: str, location: str, num_results: int = 10) -> list:
    """
    Search for jobs using the JSearch API (RapidAPI).
    If no API key, returns demo data so the app still works.
    """
    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key:
        # Return demo data if no API key is set
        return get_demo_jobs(role, location)
    
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {
        "query": f"{role} in {location}",
        "page": "1",
        "num_pages": "1"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        jobs = []
        for job in data.get("data", [])[:num_results]:
            jobs.append({
                "title": job.get("job_title", "N/A"),
                "company": job.get("employer_name", "N/A"),
                "location": job.get("job_city", "") + ", " + job.get("job_country", ""),
                "description": job.get("job_description", "")[:500],
                "url": job.get("job_apply_link", "#"),
                "source": "JSearch"
            })
        return jobs
    except Exception as e:
        print(f"Job search error: {e}")
        return get_demo_jobs(role, location)


def get_demo_jobs(role: str, location: str) -> list:
    """
    Returns fake demo job listings for testing purposes.
    Replace this with real API calls once you have an API key.
    """
    return [
        {
            "title": f"Junior {role}",
            "company": "TechCorp India",
            "location": location,
            "description": f"We are looking for a Junior {role} with strong Python skills, good communication, and eagerness to learn. Experience with ML/AI is a plus.",
            "url": "https://linkedin.com/jobs",
            "source": "Demo"
        },
        {
            "title": f"{role} Trainee",
            "company": "Infosys",
            "location": location,
            "description": f"Trainee {role} position. You will work on real projects and learn industry best practices.",
            "url": "https://linkedin.com/jobs",
            "source": "Demo"
        },
        {
            "title": f"Associate {role}",
            "company": "Wipro Technologies",
            "location": location,
            "description": f"Associate {role} role. Requirements: B.Tech/MCA, good problem-solving, Python/Java knowledge.",
            "url": "https://naukri.com",
            "source": "Demo"
        },
        {
            "title": f"{role} - Fresher",
            "company": "Startup Hub",
            "location": location,
            "description": f"Exciting fresher opportunity as {role}. We value creativity and fast learning over years of experience.",
            "url": "https://internshala.com",
            "source": "Demo"
        },
        {
            "title": f"Entry Level {role}",
            "company": "HCL Technologies",
            "location": location,
            "description": f"Entry level {role} position open for fresh graduates. Training will be provided.",
            "url": "https://naukri.com",
            "source": "Demo"
        },
    ]