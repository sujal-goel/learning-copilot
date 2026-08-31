from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

courses_df = pd.read_csv(
    BASE_DIR / "data" / "coursera-courses.csv"
)

def get_courses_for_skill(skill: str):
    results = courses_df[
        courses_df["skills"]
        .fillna("")
        .str.contains(skill, case=False)
    ]

    courses = []

    for _, row in results.head(10).iterrows():
        courses.append({
            "title": row["course_name"],
            "platform": row["course_provided_by"],
            "difficulty": row["course_difficulty"],
            "description": (
            str(row["description"])[:180] + "..."
            if len(str(row["description"])) > 180
            else str(row["description"])
            ),
            "url": row["course_url"]
        })

    return courses