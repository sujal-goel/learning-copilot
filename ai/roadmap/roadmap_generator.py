import json

from ai.shared.gemini_client import client
from ai.roadmap.prompts import ROADMAP_PROMPT


def generate_roadmap(profile, missing_skills):

    timeline = profile.get("timeline_months", 0)

    if timeline <= 0:
        timeline = 6

    prompt = ROADMAP_PROMPT.format(
        goal=profile["goal"],
        skills=profile["current_skills"],
        missing_skills=missing_skills,
        timeline_months=timeline
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    print("\n========== GEMINI RESPONSE ==========")
    print(response.text)
    print("=====================================\n")

    text = response.text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    try:
        return json.loads(text)
    except Exception as e:
        print("JSON Parse Error:", e)
        return {}