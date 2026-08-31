import json
import uuid
from ai.shared.gemini_client import call_llm_json
from ai.profile_engine.prompts import PROFILE_EXTRACTION_PROMPT
from ai.skill_gap.analyzer import get_skill_gap


def extract_profile(messages: list | str | dict, user_id: str | None = None) -> dict:
    """
    Extracts structured learner profile using Gemini LLM and computes skill gaps via analyzer.
    Returns LLD §6.1 contract schema.
    """
    messages_text = ""
    if isinstance(messages, list):
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages_text += f"{role.upper()}: {content}\n"
            else:
                messages_text += f"USER: {str(msg)}\n"
    elif isinstance(messages, dict):
        messages_text = json.dumps(messages)
    else:
        messages_text = str(messages)

    # Attempt LLM structured extraction
    extracted_data = {}
    try:
        prompt = PROFILE_EXTRACTION_PROMPT.format(messages_text=messages_text)
        extracted_data = call_llm_json(prompt)
    except Exception as e:
        print(f"[Profile Extractor] LLM extraction fallback triggered: {e}")
        extracted_data = {
            "goal": "Backend Developer",
            "experience_level": "BEGINNER",
            "study_hours_per_week": 10,
            "timeline_months": 6,
            "skills": [
                {"name": "Java", "proficiency": 0.8},
                {"name": "SQL", "proficiency": 0.6},
            ]
        }

    # Normalize extracted fields
    goal = extracted_data.get("goal", "Backend Developer")
    exp_level = str(extracted_data.get("experience_level", "BEGINNER")).upper()
    study_hours = int(extracted_data.get("study_hours_per_week", 10))
    timeline = int(extracted_data.get("timeline_months", 6))
    user_skills = extracted_data.get("skills", [])

    # Format skills list with skill_ids
    formatted_skills = []
    skills_for_gap = {}
    for idx, s in enumerate(user_skills):
        if isinstance(s, dict):
            s_name = s.get("name", f"Skill_{idx}")
            s_prof = float(s.get("proficiency", 0.5))
        else:
            s_name = str(s)
            s_prof = 0.8

        formatted_skills.append({
            "skill_id": f"c{idx+1}_id",
            "name": s_name,
            "proficiency": s_prof
        })
        skills_for_gap[s_name] = s_prof

    # Compute dynamic skill gaps using skill_graph.json
    gap_analysis = get_skill_gap(goal=goal, experience_level=exp_level, current_skills=skills_for_gap)

    profile_id = str(uuid.uuid4())
    result = {
        "profile_id": profile_id,
        "goal": goal,
        "experience_level": exp_level,
        "study_hours_per_week": study_hours,
        "timeline_months": timeline,
        "skills": formatted_skills,
        "identified_gaps": gap_analysis.get("identified_gaps", []),
    }
    if user_id:
        result["user_id"] = str(user_id)

    return result