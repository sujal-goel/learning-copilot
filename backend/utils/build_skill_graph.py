import csv
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_PATH = BASE_DIR / "data" / "job_descriptions_2025.csv"
OUTPUT_JSON = BASE_DIR / "data" / "skill_graph.json"
OUTPUT_FLAT_JSON = BASE_DIR / "data" / "skill_graph_flat.json"

LEVEL_MAP = {
    "fresher": "Fresher",
    "entry-level": "Fresher",
    "entry level": "Fresher",
    "junior": "Junior",
    "mid-level": "Mid",
    "mid-senior": "Mid",
    "mid-senior level": "Mid",
    "mid level": "Mid",
    "experienced": "Experienced",
    "senior": "Senior",
    "senior-level": "Senior",
    "senior level": "Senior",
    "lead": "Lead",
}


def normalize_level(level_str: str) -> str:
    if not level_str:
        return "Fresher"
    cleaned = str(level_str).strip().lower()
    return LEVEL_MAP.get(cleaned, str(level_str).strip())


def build_skill_graph():
    if not CSV_PATH.exists():
        print(f"CSV file not found at {CSV_PATH}")
        return

    graph = {}
    flat_graph = {}

    with open(CSV_PATH, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_title = row.get("Title", "").strip()
            if not raw_title:
                continue

            title_base = re.sub(
                r"\s*-\s*(Entry Level|Experienced|Fresher|Junior|Senior|Lead)$",
                "",
                raw_title,
                flags=re.IGNORECASE,
            ).strip()

            level = normalize_level(row.get("ExperienceLevel", "Fresher"))

            skills_set = set()
            for col in ["Skills", "Keywords"]:
                val = row.get(col, "")
                if val:
                    items = [k.strip() for k in re.split(r"[;,]", str(val)) if k.strip()]
                    skills_set.update(items)

            skills_list = sorted(list(skills_set))

            for key_title in set([raw_title, title_base]):
                if key_title not in graph:
                    graph[key_title] = {}
                if level not in graph[key_title]:
                    graph[key_title][level] = set()
                graph[key_title][level].update(skills_list)

                flat_key = f"{key_title}:{level}"
                if flat_key not in flat_graph:
                    flat_graph[flat_key] = set()
                flat_graph[flat_key].update(skills_list)

    nested_output = {
        t: {l: sorted(list(s)) for l, s in levels.items()}
        for t, levels in graph.items()
    }
    flat_output = {k: sorted(list(v)) for k, v in flat_graph.items()}

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(nested_output, f, indent=2)

    with open(OUTPUT_FLAT_JSON, "w", encoding="utf-8") as f:
        json.dump(flat_output, f, indent=2)

    print(f"Skill graph successfully generated! {len(nested_output)} titles saved to {OUTPUT_JSON}")


if __name__ == "__main__":
    build_skill_graph()
