from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

courses_df = pd.read_csv(
    BASE_DIR / "data" / "coursera-courses.csv"
)

def get_resources_for_skill(skill: str):
    skill = skill.lower()

    matches = courses_df[
        courses_df["skills"]
        .fillna("")
        .str.lower()
        .str.contains(skill, na=False)
    ]

    resources = []

    for _, row in matches.head(10).iterrows():
        resources.append({
            "title": row["course_name"],
            "platform": row["course_provided_by"],
            "difficulty": row["course_difficulty"],
            "url": row["course_url"],
            "description": str(row["description"])[:200] + "..."
        })

    return resources