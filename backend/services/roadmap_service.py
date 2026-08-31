import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.profile import LearnerProfile
from ai.roadmap.roadmap_generator import generate_roadmap as ai_generate_roadmap
from ai.skill_gap.analyzer import get_skill_gap


async def generate_roadmap(profile_id: str | uuid.UUID, goal: str | None = None, db: AsyncSession | None = None) -> dict:
    """
    Generates a personalized topological roadmap DAG using Gemini LLM and Coursera course catalog.
    Reloads profile from database if db session is provided.
    """
    profile_dict = {
        "goal": goal or "Backend Developer",
        "experience_level": "BEGINNER",
        "study_hours_per_week": 10,
        "timeline_months": 6,
        "skills": [],
        "identified_gaps": []
    }

    if db and profile_id:
        try:
            pid = uuid.UUID(str(profile_id)) if isinstance(profile_id, str) else profile_id
            result = await db.execute(
                select(LearnerProfile)
                .options(selectinload(LearnerProfile.learner_skills))
                .where((LearnerProfile.id == pid) | (LearnerProfile.user_id == pid))
            )
            prof_obj = result.scalars().first()
            if prof_obj:
                profile_dict["goal"] = prof_obj.goal
                profile_dict["experience_level"] = prof_obj.experience_level.value if hasattr(prof_obj.experience_level, "value") else str(prof_obj.experience_level)
                profile_dict["study_hours_per_week"] = prof_obj.study_hours_per_week
                profile_dict["timeline_months"] = prof_obj.timeline_months

                skills_map = {}
                skills_list = []
                for ls in getattr(prof_obj, "learner_skills", []):
                    if hasattr(ls, "skill") and ls.skill:
                        skills_map[ls.skill.name] = ls.proficiency_level
                        skills_list.append({"name": ls.skill.name, "proficiency": ls.proficiency_level})

                profile_dict["skills"] = skills_list
                gap_analysis = get_skill_gap(goal=profile_dict["goal"], experience_level=profile_dict["experience_level"], current_skills=skills_map)
                profile_dict["identified_gaps"] = gap_analysis.get("identified_gaps", [])
        except Exception as e:
            print(f"[Roadmap Service] DB profile reload warning: {e}")

    return ai_generate_roadmap(profile=profile_dict)
