import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import get_current_user
from database.session import get_db
from models.feedback import Feedback
from models.user import User
from schemas.feedback import FeedbackRequest, FeedbackResponse
from services.mentor_service import process_feedback_and_adapt

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    req: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Submits user difficulty and text feedback for a roadmap milestone/node,
    triggering AI mentor adaptation if necessary.
    """
    node_uuid = uuid.UUID(req.node_id) if req.node_id else None

    feedback = Feedback(
        user_id=current_user.id,
        node_id=node_uuid,
        feedback_text=req.feedback_text,
        difficulty_level=req.difficulty_level,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # Process mentor feedback adaptation
    adaptation = await process_feedback_and_adapt(
        user_id=str(current_user.id),
        feedback_id=str(feedback.id),
        difficulty=req.difficulty_level.value,
    )
    mutation_triggered = adaptation.get("roadmap_mutation", {}).get("triggered", False)

    return FeedbackResponse(
        id=feedback.id,
        user_id=feedback.user_id,
        node_id=str(feedback.node_id) if feedback.node_id else None,
        feedback_text=feedback.feedback_text,
        difficulty_level=feedback.difficulty_level,
        roadmap_update_triggered=mutation_triggered,
        created_at=feedback.created_at,
    )
