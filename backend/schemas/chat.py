import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models.chat_history import ChatRole


class ChatRequest(BaseModel):
    query: str
    current_node_id: str | None = None
    session_id: str | None = None


class ChatMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    role: ChatRole
    message: str
    node_context_id: uuid.UUID | None = None
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessageSchema]
    has_more: bool = False
