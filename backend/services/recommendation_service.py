import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.profile import LearnerProfile
from ai.skill_gap.analyzer import get_skill_gap
from ai.recommender.recommendation_engine import recommend_courses


async def get_recommendations(profile_id: str | uuid.UUID, db: AsyncSession | None = None) -> dict:
    """
    Executes recommendation engine by reloading profile from DB, computing dynamic skill gaps,
    and searching candidate learning resources from coursera-courses.csv.
    """
    goal = "Backend Developer"
    experience_level = "BEGINNER"
    user_skills_map = {}

    # Reload profile with DB if session provided
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
                goal = prof_obj.goal
                experience_level = prof_obj.experience_level.value if hasattr(prof_obj.experience_level, "value") else str(prof_obj.experience_level)
                for ls in getattr(prof_obj, "learner_skills", []):
                    if hasattr(ls, "skill") and ls.skill:
                        user_skills_map[ls.skill.name] = ls.proficiency_level
        except Exception as e:
            print(f"[Recommendation Service] DB profile reload warning: {e}")

    # Calculate gap skills
    gap_result = get_skill_gap(goal=goal, experience_level=experience_level, current_skills=user_skills_map)
    missing_skills = gap_result.get("missing_skills", ["Spring Boot", "REST APIs", "SQL", "Docker"])

    # Query coursera-courses.csv matching gap skills
    rec_courses_dict = recommend_courses(missing_skills=missing_skills, experience_level=experience_level)

    skill_gaps_output = []
    for gap in gap_result.get("identified_gaps", []):
        s_name = gap["name"]
        rec_resources = rec_courses_dict.get(s_name, [])
        skill_gaps_output.append({
            "skill_name": s_name,
            "gap_score": gap["gap"],
            "priority": gap["priority"],
            "recommended_resources": rec_resources,
        })

    # If no gaps found, provide default recommended resources
    if not skill_gaps_output:
        for s_name in missing_skills[:3]:
            rec_resources = rec_courses_dict.get(s_name, [])
            skill_gaps_output.append({
                "skill_name": s_name,
                "gap_score": 1.0,
                "priority": "HIGH",
                "recommended_resources": rec_resources,
            })

    return {"skill_gaps": skill_gaps_output}
