import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from auth.jwt import get_current_user
from database.session import get_db
from models.profile import ExperienceLevel, LearnerProfile, LearnerSkill
from models.skill import Skill
from models.user import User
from schemas.profile import (
    OnboardRequest,
    OnboardResponse,
    ProfileResponse,
    ProfileUpdateRequest,
    SkillGapItem,
    SkillItem,
)
from services.profile_service import extract_profile

router = APIRouter(prefix="/profile", tags=["Learner Profile"])


@router.post("/onboard", response_model=OnboardResponse, status_code=status.HTTP_201_CREATED)
async def onboard_user(
    req: OnboardRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Consumes conversation history from conversational onboarding flow,
    extracts structured entities via profile_service, and persists the learner profile.
    """
    messages_payload = [m.model_dump() for m in req.messages]
    ai_extracted = await extract_profile(messages_payload, user_id=current_user.id)

    # Check if profile already exists, update or create
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    exp_level_str = ai_extracted.get("experience_level", "BEGINNER")
    try:
        exp_level = ExperienceLevel(exp_level_str)
    except ValueError:
        exp_level = ExperienceLevel.BEGINNER

    if not profile:
        profile = LearnerProfile(
            user_id=current_user.id,
            goal=ai_extracted.get("goal", "Full Stack Developer"),
            experience_level=exp_level,
            study_hours_per_week=ai_extracted.get("study_hours_per_week", 10),
            timeline_months=ai_extracted.get("timeline_months", 6),
        )
        db.add(profile)
        await db.flush()
    else:
        profile.goal = ai_extracted.get("goal", profile.goal)
        profile.experience_level = exp_level
        profile.study_hours_per_week = ai_extracted.get("study_hours_per_week", profile.study_hours_per_week)
        profile.timeline_months = ai_extracted.get("timeline_months", profile.timeline_months)

    # Save skills
    for s in ai_extracted.get("skills", []):
        # find or create skill
        skill_res = await db.execute(select(Skill).where(Skill.name == s["name"]))
        db_skill = skill_res.scalar_one_or_none()
        if not db_skill:
            db_skill = Skill(name=s["name"], domain="General")
            db.add(db_skill)
            await db.flush()

        # check learner skill
        ls_res = await db.execute(
            select(LearnerSkill).where(
                LearnerSkill.profile_id == profile.id,
                LearnerSkill.skill_id == db_skill.id,
            )
        )
        ls = ls_res.scalar_one_or_none()
        if not ls:
            db.add(LearnerSkill(profile_id=profile.id, skill_id=db_skill.id, proficiency_level=s.get("proficiency", 0.0)))
        else:
            ls.proficiency_level = s.get("proficiency", ls.proficiency_level)

    await db.commit()
    await db.refresh(profile)

    return OnboardResponse(
        profile_id=profile.id,
        goal=profile.goal,
        experience_level=profile.experience_level,
        study_hours_per_week=profile.study_hours_per_week,
        timeline_months=profile.timeline_months,
        skills=[SkillItem(**item) for item in ai_extracted.get("skills", [])],
        identified_gaps=[SkillGapItem(**item) for item in ai_extracted.get("identified_gaps", [])],
    )


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Returns the authenticated user's full learner profile."""
    result = await db.execute(
        select(LearnerProfile)
        .options(selectinload(LearnerProfile.learner_skills).selectinload(LearnerSkill.skill))
        .where(LearnerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found. Please complete onboarding first.",
        )

    skills_list = [
        SkillItem(
            skill_id=str(ls.skill_id),
            name=ls.skill.name if ls.skill else "Unknown",
            proficiency=ls.proficiency_level,
        )
        for ls in profile.learner_skills
    ]

    return ProfileResponse(
        profile_id=profile.id,
        user_id=profile.user_id,
        goal=profile.goal,
        experience_level=profile.experience_level,
        study_hours_per_week=profile.study_hours_per_week,
        timeline_months=profile.timeline_months,
        skills=skills_list,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_profile_by_user_id(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch profile by user_id with IDOR protection."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: cannot access another user's profile",
        )
    return await get_my_profile(current_user=current_user, db=db)


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates mutable profile fields."""
    result = await db.execute(
        select(LearnerProfile)
        .options(selectinload(LearnerProfile.learner_skills).selectinload(LearnerSkill.skill))
        .where(LearnerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found",
        )

    if req.goal is not None:
        profile.goal = req.goal
    if req.experience_level is not None:
        profile.experience_level = req.experience_level
    if req.study_hours_per_week is not None:
        profile.study_hours_per_week = req.study_hours_per_week
    if req.timeline_months is not None:
        profile.timeline_months = req.timeline_months

    await db.commit()
    await db.refresh(profile)

    return await get_my_profile(current_user=current_user, db=db)


@router.put("/{user_id}", response_model=ProfileResponse)
async def update_profile_by_user_id(
    user_id: uuid.UUID,
    req: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )
    return await update_my_profile(req=req, current_user=current_user, db=db)
