from fastapi import APIRouter
from services.skill_gap_service import get_skill_gap

router = APIRouter(
    prefix="/skill-gap",
    tags=["Skill Gap"]
)

@router.post("/")
async def skill_gap(payload: dict):

    return get_skill_gap(
        payload["goal"],
        payload.get("current_skills", [])
    )