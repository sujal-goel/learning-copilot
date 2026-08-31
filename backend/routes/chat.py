import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import get_current_user
from database.session import get_db
from models.chat_history import ChatHistory, ChatRole
from models.user import User
from schemas.chat import ChatHistoryResponse, ChatMessageSchema, ChatRequest
from services.mentor_service import get_mentor_response

router = APIRouter(tags=["AI Tutor / Chat"])


@router.post("/chat")
async def chat_with_mentor(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Sends message to AI Tutor/Mentor.
    Saves user message and AI response to chat_history table.
    """
    session_uuid = uuid.UUID(req.session_id) if req.session_id else uuid.uuid4()
    node_uuid = uuid.UUID(req.current_node_id) if req.current_node_id else None

    # 1. Save User Message
    user_msg = ChatHistory(
        user_id=current_user.id,
        session_id=session_uuid,
        role=ChatRole.USER,
        message=req.query,
        node_context_id=node_uuid,
    )
    db.add(user_msg)
    await db.flush()

    # 2. Get AI Response
    ai_data = await get_mentor_response(
        user_id=str(current_user.id),
        query=req.query,
        current_node_id=req.current_node_id,
        db=db,
    )

    # 3. Save Assistant Message
    assistant_msg = ChatHistory(
        user_id=current_user.id,
        session_id=session_uuid,
        role=ChatRole.ASSISTANT,
        message=ai_data.get("reply", ""),
        node_context_id=node_uuid,
    )
    db.add(assistant_msg)
    await db.commit()

    return {
        "reply": ai_data.get("reply"),
        "session_id": str(session_uuid),
        "citations": ai_data.get("citations", []),
        "roadmap_mutation": ai_data.get("roadmap_mutation", {"triggered": False}),
    }


@router.get("/chat/history", response_model=ChatHistoryResponse)
@router.get("/chat-history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns past chat history messages for the authenticated user."""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == current_user.id)
        .order_by(desc(ChatHistory.timestamp))
        .limit(limit)
    )
    records = result.scalars().all()
    # Reverse to return chronological order
    records = list(reversed(records))

    return ChatHistoryResponse(
        messages=[ChatMessageSchema.model_validate(r) for r in records],
        has_more=len(records) >= limit,
    )


@router.get("/chat-history/{user_id}", response_model=ChatHistoryResponse)
@router.get("/chat/history/{user_id}", response_model=ChatHistoryResponse)
async def get_chat_history_by_user_id(
    user_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view another user's chat history",
        )
    return await get_chat_history(limit=limit, current_user=current_user, db=db)
