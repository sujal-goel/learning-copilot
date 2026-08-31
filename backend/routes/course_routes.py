from fastapi import APIRouter
from services.course_service import get_courses_for_skill

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.get("/{skill}")
async def get_courses(skill: str):
    return get_courses_for_skill(skill)