import uuid
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from models.chat_history import ChatHistory
from ai.mentor.mentor_chat import get_mentor_chat_reply, adapt_roadmap_from_feedback


async def get_mentor_response(
    user_id: str | uuid.UUID,
    query: str,
    current_node_id: str | None = None,
    db: AsyncSession | None = None,
) -> dict:
    """
    RAG AI tutor answer grounded in active node context and persistent database chat history.
    """
    chat_history_records = []

    if db and user_id:
        try:
            uid = uuid.UUID(str(user_id)) if isinstance(user_id, str) else user_id
            result = await db.execute(
                select(ChatHistory)
                .where(ChatHistory.user_id == uid)
                .order_by(desc(ChatHistory.timestamp))
                .limit(10)
            )
            records = result.scalars().all()
            chat_history_records = list(reversed(records))
        except Exception as e:
            print(f"[Mentor Service] DB chat history load warning: {e}")

    return await get_mentor_chat_reply(
        user_id=str(user_id),
        query=query,
        chat_history=chat_history_records,
        current_node_context=current_node_id,
    )


async def process_feedback_and_adapt(
    user_id: str | uuid.UUID,
    feedback_id: str | None = None,
    difficulty: str = "JUST_RIGHT",
    feedback_text: str = "",
    db: AsyncSession | None = None,
) -> dict:
    """
    Processes user feedback difficulty signals and triggers roadmap adaptation if needed.
    """
    return await adapt_roadmap_from_feedback(
        user_id=str(user_id),
        feedback_text=feedback_text,
        difficulty=difficulty,
    )
