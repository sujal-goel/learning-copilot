import re


def extract_profile(user_input):

    profile = {
        "goal": "AI Engineer",
        "current_skills": [],
        "experience_level": "Beginner",
        "study_hours_per_day": 2,
        "timeline_months": 6,
        "interests": []
    }

    text = user_input.lower()

    if "data scientist" in text:
        profile["goal"] = "Data Scientist"

    if "product manager" in text:
        profile["goal"] = "Product Manager"

    if "intermediate" in text:
        profile["experience_level"] = "Intermediate"

    if "advanced" in text:
        profile["experience_level"] = "Advanced"

    hours_match = re.search(r"(\d+)\s*hour", text)
    if hours_match:
        profile["study_hours_per_day"] = int(
            hours_match.group(1)
        )

    months_match = re.search(r"(\d+)\s*month", text)
    if months_match:
        profile["timeline_months"] = int(
            months_match.group(1)
        )

    return profile