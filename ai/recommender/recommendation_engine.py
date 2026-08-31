import csv
import re
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "data" / "coursera-courses.csv"

_COURSE_CACHE = []


def load_courses():
    global _COURSE_CACHE
    if _COURSE_CACHE:
        return _COURSE_CACHE

    if not CSV_PATH.exists():
        print(f"Coursera CSV not found at {CSV_PATH}")
        return []

    courses = []
    with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            c_name = row.get("course_name", "").strip()
            if not c_name:
                continue

            c_url = row.get("course_url", "").strip()
            if not c_url.startswith("http"):
                c_url = f"https://www.coursera.org/learn/{re.sub(r'[^a-z0-9]+', '-', c_name.lower())}"

            try:
                rating = float(row.get("course_rating", 4.5))
            except ValueError:
                rating = 4.5

            try:
                enrolled = float(row.get("enrolled_student_count", 1000.0))
            except ValueError:
                enrolled = 1000.0

            time_str = row.get("estimated_time_to_complete", "")
            est_hours = 15
            hours_match = re.search(r"(\d+)\s*(hour|month|week)", time_str, re.IGNORECASE)
            if hours_match:
                num = int(hours_match.group(1))
                unit = hours_match.group(2).lower()
                if "month" in unit:
                    est_hours = num * 20
                elif "week" in unit:
                    est_hours = num * 5
                else:
                    est_hours = num

            courses.append({
                "id": f"c_{idx}",
                "course_name": c_name,
                "course_url": c_url,
                "provider": row.get("course_provided_by", "Coursera"),
                "rating": rating,
                "enrolled": enrolled,
                "difficulty": row.get("course_difficulty", "Beginner").strip(),
                "skills": row.get("skills", "").lower(),
                "description": row.get("description", "").lower(),
                "estimated_hours": est_hours,
            })

    _COURSE_CACHE = courses
    return _COURSE_CACHE


def recommend_courses(missing_skills: list[str], experience_level: str = "Beginner") -> dict:
    """
    Searches coursera-courses.csv dynamically for candidate learning resources matching gap skills.
    Returns dictionary mapping skill_name -> list of ranked resource dicts.
    """
    courses = load_courses()
    recommendations = {}

    target_diff = "Beginner"
    lvl_lower = str(experience_level).lower()
    if "exp" in lvl_lower or "senior" in lvl_lower:
        target_diff = "Advanced"
    elif "mid" in lvl_lower or "inter" in lvl_lower:
        target_diff = "Intermediate"

    for skill in missing_skills:
        skill_clean = skill.strip().lower()
        matched = []

        for c in courses:
            score = 0.0
            # Keyword match scoring
            if skill_clean in c["skills"]:
                score += 3.0
            if skill_clean in c["course_name"].lower():
                score += 2.0
            if skill_clean in c["description"]:
                score += 1.0

            if score > 0:
                # Bonus for rating and difficulty alignment
                score += (c["rating"] / 5.0)
                if c["difficulty"].lower() == target_diff.lower():
                    score += 0.5

                matched.append((c, score))

        # Sort by match score descending
        matched.sort(key=lambda x: x[1], reverse=True)

        top_courses = []
        for c, score in matched[:3]:
            top_courses.append({
                "resource_id": f"r_{uuid.uuid4().hex[:8]}",
                "title": c["course_name"],
                "url": c["course_url"],
                "provider": c["provider"],
                "type": "COURSE",
                "difficulty": c["difficulty"].upper(),
                "estimated_hours": c["estimated_hours"],
                "relevance_score": round(min(0.98, score / 4.5), 2),
            })

        # Fallback if no course matched in Coursera dataset
        if not top_courses:
            top_courses.append({
                "resource_id": f"r_{uuid.uuid4().hex[:8]}",
                "title": f"Mastering {skill} - Hands-on Guide",
                "url": f"https://www.coursera.org/search?query={re.sub(r'[^a-z0-9]+', '%20', skill_clean)}",
                "provider": "Coursera",
                "type": "COURSE",
                "difficulty": target_diff.upper(),
                "estimated_hours": 12,
                "relevance_score": 0.85,
            })

        recommendations[skill] = top_courses

    return recommendations