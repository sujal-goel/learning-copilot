import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base


class DifficultyLevel(str, enum.Enum):
    TOO_EASY = "TOO_EASY"
    JUST_RIGHT = "JUST_RIGHT"
    TOO_HARD = "TOO_HARD"


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_path_nodes.id", ondelete="SET NULL"), nullable=True
    )
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty_level: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level_enum"), default=DifficultyLevel.JUST_RIGHT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="feedbacks")
    node: Mapped["LearningPathNode"] = relationship("LearningPathNode", back_populates="feedbacks")
