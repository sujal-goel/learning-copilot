from fastapi import APIRouter
from services.resource_service import get_resources_for_skill

router = APIRouter(
    prefix="/resources",
    tags=["Resources"]
)

@router.get("/{skill}")
async def get_resources(skill: str):
    return get_resources_for_skill(skill)