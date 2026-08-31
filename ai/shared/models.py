from pydantic import BaseModel

class UserProfile(BaseModel):
    goal: str
    current_skills: list[str]
    experience_level: str
    study_hours_per_day: int
    timeline_months: int
    interests: list[str]