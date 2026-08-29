import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    profile: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="user", uselist=False)
    progress_records: Mapped[list["Progress"]] = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")
    chat_logs: Mapped[list["ChatHistory"]] = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
