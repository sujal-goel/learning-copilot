from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_PATH = BASE_DIR / "data" / "resources.csv"


def recommend_courses(missing_skills):

    df = pd.read_csv(CSV_PATH)

    recommendations = {}

    for skill in missing_skills:

        courses = df[
            df["skill"] == skill
        ].to_dict(orient="records")

        recommendations[skill] = courses

    return recommendations