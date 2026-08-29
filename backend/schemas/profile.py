import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.profile import ExperienceLevel


class ChatMessageItem(BaseModel):
    role: str
    content: str


class OnboardRequest(BaseModel):
    messages: list[ChatMessageItem]


class SkillItem(BaseModel):
    skill_id: str | None = None
    name: str
    proficiency: float = 0.0


class SkillGapItem(BaseModel):
    name: str
    gap: float
    priority: str


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    profile_id: uuid.UUID
    user_id: uuid.UUID
    goal: str
    experience_level: ExperienceLevel
    study_hours_per_week: int
    timeline_months: int
    skills: list[SkillItem] = []
    created_at: datetime
    updated_at: datetime


class OnboardResponse(BaseModel):
    profile_id: uuid.UUID
    goal: str
    experience_level: ExperienceLevel
    study_hours_per_week: int
    timeline_months: int
    skills: list[SkillItem]
    identified_gaps: list[SkillGapItem]


class ProfileUpdateRequest(BaseModel):
    goal: str | None = None
    experience_level: ExperienceLevel | None = None
    study_hours_per_week: int | None = None
    timeline_months: int | None = None
