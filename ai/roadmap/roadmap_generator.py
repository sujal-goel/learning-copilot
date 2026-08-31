import json
import uuid
from ai.shared.gemini_client import call_llm_json
from ai.roadmap.prompts import ROADMAP_GENERATION_PROMPT
from ai.recommender.recommendation_engine import recommend_courses


def generate_roadmap(profile: dict, missing_skills: list | None = None) -> dict:
    """
    Generates a personalized topological roadmap DAG using candidate Coursera resources and Gemini LLM.
    Returns response shape matching LLD §6.2 contract.
    """
    goal = profile.get("goal", "Backend Developer")
    exp_level = profile.get("experience_level", "BEGINNER")
    study_hours = profile.get("study_hours_per_week", 10)
    timeline = profile.get("timeline_months", 6)
    skills = profile.get("skills", [])
    gaps = profile.get("identified_gaps", [])

    if not missing_skills:
        missing_skills = [g["name"] for g in gaps] if gaps else ["Spring Boot", "REST APIs", "SQL", "Docker"]

    # 1. Fetch candidate Coursera course recommendations
    rec_dict = recommend_courses(missing_skills=missing_skills, experience_level=exp_level)
    rec_text = ""
    for skill_name, course_list in rec_dict.items():
        rec_text += f"- Skill: {skill_name}\n"
        for c in course_list:
            rec_text += f"  * Title: {c['title']} | URL: {c['url']} | Hours: {c['estimated_hours']} | Diff: {c['difficulty']}\n"

    # 2. Format prompt
    prompt = ROADMAP_GENERATION_PROMPT.format(
        goal=goal,
        experience_level=exp_level,
        current_skills=json.dumps(skills),
        identified_gaps=json.dumps(gaps),
        timeline_months=timeline,
        study_hours_per_week=study_hours,
        recommended_courses_text=rec_text,
    )

    path_id = str(uuid.uuid4())

    try:
        roadmap_json = call_llm_json(prompt)
        roadmap_json["path_id"] = path_id
        if "milestones" not in roadmap_json or not isinstance(roadmap_json["milestones"], list):
            raise ValueError("Invalid roadmap JSON structure returned by LLM")
        return roadmap_json
    except Exception as e:
        print(f"[Roadmap Generator] LLM generation fallback triggered: {e}")
        # Deterministic fallback roadmap matching Coursera resources
        milestones = []
        node_counter = 1
        prev_node_id = None

        for month in range(1, timeline + 1):
            m_id = f"m{month}"
            m_nodes = []

            # Pick a skill for this month
            skill_idx = (month - 1) % len(missing_skills)
            skill_name = missing_skills[skill_idx]
            courses = rec_dict.get(skill_name, [])
            target_course = courses[0] if courses else {
                "title": f"Mastering {skill_name}",
                "url": "https://www.coursera.org",
                "estimated_hours": 15
            }

            n_id = f"n{node_counter}"
            node_counter += 1

            course_node = {
                "node_id": n_id,
                "type": "COURSE",
                "title": target_course["title"],
                "resource_url": target_course["url"],
                "estimated_hours": target_course["estimated_hours"],
                "status": "IN_PROGRESS" if prev_node_id is None else "LOCKED",
                "dependencies": [prev_node_id] if prev_node_id else []
            }
            m_nodes.append(course_node)

            q_id = f"n{node_counter}"
            node_counter += 1
            quiz_node = {
                "node_id": q_id,
                "type": "ASSESSMENT",
                "title": f"{skill_name} Mastery Quiz",
                "estimated_hours": 1,
                "status": "LOCKED",
                "dependencies": [n_id]
            }
            m_nodes.append(quiz_node)
            prev_node_id = q_id

            milestones.append({
                "milestone_id": m_id,
                "title": f"Month {month}: {skill_name} Foundations",
                "nodes": m_nodes
            })

        return {
            "path_id": path_id,
            "title": f"{goal} Internship Roadmap ({timeline} months)",
            "total_estimated_hours": timeline * 20,
            "milestones": milestones
        }