import uuid

# Mock AI Response Contract as defined in LLD.md §6.1
MOCK_PROFILE_RESPONSE = {
    "profile_id": "b1eebc99-9c0b-4ef8-bb6d-6bb9bd380a22",
    "goal": "Backend Developer",
    "experience_level": "BEGINNER",  # BEGINNER | INTERMEDIATE | ADVANCED
    "study_hours_per_week": 10,
    "timeline_months": 6,
    "skills": [
        {"skill_id": "c1", "name": "Java", "proficiency": 0.8},
        {"skill_id": "c2", "name": "SQL", "proficiency": 0.6},
        {"skill_id": "c3", "name": "Python", "proficiency": 0.3},
    ],
    "identified_gaps": [
        {"name": "Spring Boot", "gap": 1.0, "priority": "HIGH"},
        {"name": "REST APIs", "gap": 1.0, "priority": "HIGH"},
        {"name": "Docker", "gap": 1.0, "priority": "MEDIUM"},
        {"name": "System Design", "gap": 0.9, "priority": "LOW"},
    ],
}


async def extract_profile(messages: list[dict], user_id: uuid.UUID | None = None) -> dict:
    """
    Calls LLM to extract structured profile from conversational onboarding messages.
    During mock phase, returns contract-compliant mock response.
    TODO: Replace with actual OpenAI/Gemini structured output function call.
    """
    response = dict(MOCK_PROFILE_RESPONSE)
    if user_id:
        response["user_id"] = str(user_id)
    return response
