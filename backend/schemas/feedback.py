import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.feedback import DifficultyLevel


class FeedbackRequest(BaseModel):
    node_id: str | None = None
    feedback_text: str
    difficulty_level: DifficultyLevel = DifficultyLevel.JUST_RIGHT


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    node_id: str | None = None
    feedback_text: str
    difficulty_level: DifficultyLevel
    roadmap_update_triggered: bool = False
    created_at: datetime
