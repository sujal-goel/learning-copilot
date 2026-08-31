import uuid
from ai.profile_engine.extractor import extract_profile as ai_extract_profile


async def extract_profile(messages: list[dict], user_id: uuid.UUID | None = None) -> dict:
    """
    Calls AI engine to extract structured profile from conversational onboarding messages.
    Invokes Gemini LLM for profile entity extraction + dynamic skill gap analyzer.
    """
    return ai_extract_profile(messages=messages, user_id=str(user_id) if user_id else None)
