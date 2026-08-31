from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SKILL_FILE = BASE_DIR / "data" / "skill_graph.json"

with open(SKILL_FILE, "r") as f:
    ROLE_SKILLS = json.load(f)


def get_skill_gap(goal, current_skills):

    GOAL_ALIASES = {
    "Become an AI Engineer": "AI Engineer",
    "AI Engineer": "AI Engineer",
    "Artificial Intelligence Engineer": "AI Engineer"
    }

    goal = GOAL_ALIASES.get(goal, goal)

    required_skills = ROLE_SKILLS.get(goal, [])

    missing_skills = [
        skill
        for skill in required_skills
        if skill not in current_skills
    ]

    return {
        "goal": goal,
        "required_skills": required_skills,
        "current_skills": current_skills,
        "missing_skills": missing_skills
    }