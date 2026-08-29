import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import get_current_user
from database.session import get_db
from models.profile import LearnerProfile
from models.user import User
from schemas.learning_path import RoadmapResponse
from services.roadmap_service import generate_roadmap

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])


@router.post("/generate", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=RoadmapResponse, status_code=status.HTTP_201_CREATED)
async def create_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers the recommendation engine & topological sort to build/retrieve the learner's roadmap.
    """
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    profile_id = str(profile.id) if profile else str(uuid.uuid4())
    goal = profile.goal if profile else "Developer"

    roadmap_data = await generate_roadmap(profile_id=profile_id, goal=goal)
    return roadmap_data


@router.get("/current", response_model=RoadmapResponse)
async def get_current_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns active learning roadmap DAG nodes, milestones, and completion status."""
    return await create_roadmap(current_user=current_user, db=db)


@router.get("/{user_id}", response_model=RoadmapResponse)
async def get_roadmap_by_user_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """IDOR-protected roadmap retrieval by user_id."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot view another user's roadmap",
        )
    return await get_current_roadmap(current_user=current_user, db=db)
