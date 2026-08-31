from ai.profile_engine.extractor import extract_profile
from ai.skill_gap.analyzer import get_skill_gap
from ai.recommender.recommendation_engine import recommend_courses
from ai.roadmap.roadmap_generator import generate_roadmap


def run_learning_pipeline(
    user_input,
    current_skills=None
):

    profile = extract_profile(user_input)

    if current_skills is not None:
        profile["current_skills"] = current_skills

    gap = get_skill_gap(
        profile["goal"],
        profile["current_skills"]
    )

    recommendations = recommend_courses(
        gap["missing_skills"]
    )

    roadmap = generate_roadmap(
        profile,
        gap["missing_skills"]
    )

    return {
        "profile": profile,
        "skill_gap": gap,
        "recommendations": recommendations,
        "roadmap": roadmap
    }