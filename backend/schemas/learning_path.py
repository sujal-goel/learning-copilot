from pydantic import BaseModel, ConfigDict
from models.learning_path import NodeStatus, NodeType


class RoadmapNodeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    node_id: str
    type: NodeType
    title: str
    resource_url: str | None = None
    estimated_hours: int = 5
    status: NodeStatus = NodeStatus.LOCKED
    dependencies: list[str] = []


class MilestoneSchema(BaseModel):
    milestone_id: str
    title: str
    nodes: list[RoadmapNodeSchema]


class RoadmapResponse(BaseModel):
    path_id: str
    title: str
    total_estimated_hours: int
    milestones: list[MilestoneSchema]
