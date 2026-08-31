from ai.skill_gap.analyzer import get_skill_gap as analyze_skill_gap


def get_skill_gap(goal: str, current_skills: list, experience_level: str = "Fresher"):
    return analyze_skill_gap(goal=goal, experience_level=experience_level, current_skills=current_skills)