from ai.skill_gap.analyzer import get_skill_gap
from ai.recommender.recommendation_engine import recommend_courses
from ai.roadmap.roadmap_generator import generate_roadmap


def run_learning_pipeline(
    goal,
    level,
    hours,
    timeline,
    interests,
    current_skills
):

    # Convert timeline string -> integer months
    try:
        timeline_months = int(
            timeline.replace("months", "").strip()
        )
    except:
        timeline_months = 6

    # Convert hours string -> integer
    study_hours = 1

    if "2" in hours:
        study_hours = 2
    elif "3" in hours:
        study_hours = 3

    # Build profile directly from frontend data
    profile = {
        "goal": goal,
        "current_skills": current_skills,
        "experience_level": level,
        "study_hours_per_day": study_hours,
        "timeline_months": timeline_months,
        "interests": [interests] if interests else []
    }

    # Skill Gap Analysis
    gap = get_skill_gap(
        profile["goal"],
        profile["current_skills"]
    )

    # Course Recommendations
    recommendations = recommend_courses(
        gap["missing_skills"]
    )

    # Gemini Roadmap Generation
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