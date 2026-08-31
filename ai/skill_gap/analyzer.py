import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SKILL_FILE = BASE_DIR / "data" / "skill_graph.json"

ROLE_SKILLS = {}
if SKILL_FILE.exists():
    with open(SKILL_FILE, "r", encoding="utf-8") as f:
        ROLE_SKILLS = json.load(f)


def get_required_skills(goal: str, experience_level: str = "Fresher") -> list[str]:
    """
    Looks up required skills for a given role and experience level from skill_graph.json.
    Supports title fallback matching.
    """
    if not ROLE_SKILLS:
        return ["Java", "Spring Boot", "SQL", "REST APIs", "Git", "Docker", "Testing", "System Design"]

    norm_level = "Fresher"
    lvl_lower = str(experience_level).lower()
    if "exp" in lvl_lower or "senior" in lvl_lower or "lead" in lvl_lower:
        norm_level = "Experienced"
    elif "mid" in lvl_lower or "junior" in lvl_lower:
        norm_level = "Mid"

    # 1. Exact title + level lookup
    if goal in ROLE_SKILLS:
        role_levels = ROLE_SKILLS[goal]
        if norm_level in role_levels:
            return role_levels[norm_level]
        # Fallback to any available level in this role
        for key in ["Fresher", "Experienced", "Mid", "Junior", "Senior"]:
            if key in role_levels:
                return role_levels[key]

    # 2. Case-insensitive / partial title lookup
    goal_clean = re.sub(r"\s*-\s*(Entry Level|Experienced|Fresher|Junior|Senior|Lead)$", "", goal, flags=re.IGNORECASE).strip()
    for title, role_levels in ROLE_SKILLS.items():
        if title.lower() == goal_clean.lower() or goal_clean.lower() in title.lower():
            if norm_level in role_levels:
                return role_levels[norm_level]
            for key in ["Fresher", "Experienced", "Mid", "Junior", "Senior"]:
                if key in role_levels:
                    return role_levels[key]

    # 3. Default fallback for Backend Developer if not found
    return ["Java", "Spring Boot", "SQL", "REST APIs", "Git", "Docker", "Testing", "System Design"]


def get_skill_gap(goal: str, experience_level: str = "Fresher", current_skills: list | dict | None = None) -> dict:
    """
    Performs skill gap analysis comparing required role skills against current profile skills.
    Returns identified_gaps with priority scores matching LLD §6.1 spec.
    """
    if current_skills is None:
        current_skills = []

    # Standardize current skills map: {skill_name: proficiency_float}
    skills_map = {}
    if isinstance(current_skills, list):
        for item in current_skills:
            if isinstance(item, dict):
                skills_map[item.get("name", "").strip().lower()] = float(item.get("proficiency", 0.5))
            elif isinstance(item, str):
                skills_map[item.strip().lower()] = 0.8  # Assume known string skill = 80% proficiency
    elif isinstance(current_skills, dict):
        for k, v in current_skills.items():
            skills_map[str(k).strip().lower()] = float(v)

    required = get_required_skills(goal, experience_level)

    missing_skills = []
    identified_gaps = []

    for idx, req_skill in enumerate(required):
        req_lower = req_skill.lower()
        # Find if user has this skill (exact or substring)
        found_prof = 0.0
        for user_skill, prof in skills_map.items():
            if user_skill == req_lower or user_skill in req_lower or req_lower in user_skill:
                found_prof = max(found_prof, prof)

        if found_prof < 0.8:
            gap_val = round(1.0 - found_prof, 2)
            missing_skills.append(req_skill)

            # Assign priority based on gap value and index position
            if gap_val >= 0.8 or idx < 3:
                priority = "HIGH"
            elif gap_val >= 0.4 or idx < 6:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            identified_gaps.append({
                "name": req_skill,
                "gap": gap_val,
                "priority": priority
            })

    return {
        "goal": goal,
        "experience_level": experience_level,
        "required_skills": required,
        "current_skills": current_skills,
        "missing_skills": missing_skills,
        "identified_gaps": identified_gaps,
    }