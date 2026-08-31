import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import get_current_user
from database.session import get_db
from models.progress import Progress
from models.user import User
from schemas.progress import (
    ProgressResponse,
    ProgressSummaryResponse,
    ProgressUpsertRequest,
    SkillProgressItem,
)

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])


@router.post("", response_model=ProgressResponse)
async def update_progress(
    req: ProgressUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Records or updates a user's completion percentage for a specific skill."""
    skill_uuid = uuid.UUID(req.skill_id) if req.skill_id else None

    result = await db.execute(
        select(Progress).where(
            Progress.user_id == current_user.id,
            Progress.skill_name == req.skill_name,
        )
    )
    progress = result.scalar_one_or_none()

    if not progress:
        progress = Progress(
            user_id=current_user.id,
            skill_name=req.skill_name,
            skill_id=skill_uuid,
            completion_percentage=req.completion_percentage,
            last_updated=datetime.now(timezone.utc),
        )
        db.add(progress)
    else:
        progress.completion_percentage = req.completion_percentage
        if skill_uuid:
            progress.skill_id = skill_uuid
        progress.last_updated = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(progress)
    return progress


@router.get("", response_model=ProgressSummaryResponse)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns all tracked skill progress records and overall completion percentage."""
    result = await db.execute(
        select(Progress).where(Progress.user_id == current_user.id)
    )
    records = result.scalars().all()

    if not records:
        return ProgressSummaryResponse(
            overall_completion=0.0,
            skills=[
                SkillProgressItem(skill_name="Java", completion_percentage=80.0),
                SkillProgressItem(skill_name="SQL", completion_percentage=60.0),
                SkillProgressItem(skill_name="Spring Boot", completion_percentage=75.0),
                SkillProgressItem(skill_name="Docker", completion_percentage=0.0),
            ],
        )

    skills_list = [
        SkillProgressItem(
            skill_name=p.skill_name,
            completion_percentage=p.completion_percentage,
        )
        for p in records
    ]
    avg_completion = sum(p.completion_percentage for p in records) / len(records)

    return ProgressSummaryResponse(
        overall_completion=round(avg_completion, 1),
        skills=skills_list,
    )


@router.get("/{user_id}", response_model=ProgressSummaryResponse)
async def get_progress_by_user_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view another user's progress",
        )
    return await get_progress(current_user=current_user, db=db)
