import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base


class ExperienceLevel(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    goal: Mapped[str] = mapped_column(String(500), nullable=False)
    experience_level: Mapped[ExperienceLevel] = mapped_column(
        Enum(ExperienceLevel, name="experience_level_enum"), default=ExperienceLevel.BEGINNER
    )
    study_hours_per_week: Mapped[int] = mapped_column(Integer, default=10)
    timeline_months: Mapped[int] = mapped_column(Integer, default=6)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")
    learner_skills: Mapped[list["LearnerSkill"]] = relationship("LearnerSkill", back_populates="profile", cascade="all, delete-orphan")
    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="profile", uselist=False)


class LearnerSkill(Base):
    __tablename__ = "learner_skills"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learner_profiles.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    proficiency_level: Mapped[float] = mapped_column(Float, default=0.0)

    profile: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="learner_skills")
    skill: Mapped["Skill"] = relationship("Skill", back_populates="learner_skills")
