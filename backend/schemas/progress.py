import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProgressUpsertRequest(BaseModel):
    skill_name: str
    skill_id: str | None = None
    completion_percentage: float = Field(ge=0.0, le=100.0)


class SkillProgressItem(BaseModel):
    skill_name: str
    completion_percentage: float


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    skill_name: str
    completion_percentage: float
    last_updated: datetime


class ProgressSummaryResponse(BaseModel):
    overall_completion: float
    skills: list[SkillProgressItem]
