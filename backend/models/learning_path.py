import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.session import Base


class PathStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class NodeType(str, enum.Enum):
    COURSE = "COURSE"
    PROJECT = "PROJECT"
    ASSESSMENT = "ASSESSMENT"


class NodeStatus(str, enum.Enum):
    LOCKED = "LOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learner_profiles.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), default="Personalized Learning Roadmap")
    status: Mapped[PathStatus] = mapped_column(
        Enum(PathStatus, name="path_status_enum"), default=PathStatus.ACTIVE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    profile: Mapped["LearnerProfile"] = relationship("LearnerProfile", back_populates="learning_path")
    nodes: Mapped[list["LearningPathNode"]] = relationship("LearningPathNode", back_populates="learning_path", cascade="all, delete-orphan", order_by="LearningPathNode.order_index")


class LearningPathNode(Base):
    __tablename__ = "learning_path_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_paths.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    resource_type: Mapped[NodeType] = mapped_column(
        Enum(NodeType, name="node_type_enum"), default=NodeType.COURSE
    )
    milestone: Mapped[str] = mapped_column(String(255), default="Milestone 1")
    status: Mapped[NodeStatus] = mapped_column(
        Enum(NodeStatus, name="node_status_enum"), default=NodeStatus.LOCKED
    )
    estimated_hours: Mapped[int] = mapped_column(Integer, default=5)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    learning_path: Mapped["LearningPath"] = relationship("LearningPath", back_populates="nodes")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="node")
