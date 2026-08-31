from pathlib import Path
import pandas as pd
from collections import Counter
import re

BASE_DIR = Path(__file__).resolve().parents[2]

df = pd.read_csv(
    BASE_DIR / "data" / "job_descriptions_2025.csv"
)

SKILLS = [
    "Python",
    "SQL",
    "Machine Learning",
    "Deep Learning",
    "Data Analysis",
    "Data Visualization",
    "Statistics",
    "TensorFlow",
    "PyTorch",
    "NLP",
    "LLM",
    "Generative AI",
    "MLOps",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "Power BI",
    "Tableau",
]

def get_skill_gap(goal: str, current_skills: list):

    goal = goal.lower()

    matches = df[
        df.astype(str)
          .apply(
              lambda row: row.str.contains(goal, case=False, na=False).any(),
              axis=1
          )
    ]

    text = " ".join(matches.astype(str).fillna("").agg(" ".join, axis=1))

    counter = Counter()

    for skill in SKILLS:
        count = len(
            re.findall(
                re.escape(skill),
                text,
                flags=re.IGNORECASE
            )
        )

        if count:
            counter[skill] += count

    required_skills = [
        skill
        for skill, _ in counter.most_common(8)
    ]

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