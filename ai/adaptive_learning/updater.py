import uuid


def trigger_fast_track(roadmap_dag: dict, skill_name: str) -> dict:
    """
    Fast-tracks the learner by updating downstream introductory nodes for a mastered skill to SKIPPED.
    """
    skipped_count = 0
    milestones = roadmap_dag.get("milestones", [])

    for m in milestones:
        for node in m.get("nodes", []):
            title = node.get("title", "").lower()
            if skill_name.lower() in title and node.get("status") == "LOCKED":
                node["status"] = "SKIPPED"
                skipped_count += 1

    return {
        "mutation_type": "FAST_TRACK",
        "skill_name": skill_name,
        "skipped_nodes_count": skipped_count,
        "updated_roadmap": roadmap_dag
    }


def trigger_remediation(roadmap_dag: dict, weak_skill: str, remedial_resource: dict | None = None) -> dict:
    """
    Splices remedial practice nodes into the roadmap DAG when learner scores < 50% or submits TOO_HARD feedback.
    """
    milestones = roadmap_dag.get("milestones", [])
    spliced_node = None

    if remedial_resource:
        title = f"Remedial Practice: {remedial_resource.get('title', weak_skill)}"
        url = remedial_resource.get("url", "https://www.coursera.org")
    else:
        title = f"Remedial Hands-on Project: {weak_skill}"
        url = "https://www.coursera.org"

    new_node = {
        "node_id": f"n_remedial_{uuid.uuid4().hex[:6]}",
        "type": "PROJECT",
        "title": title,
        "resource_url": url,
        "estimated_hours": 5,
        "status": "IN_PROGRESS",
        "dependencies": []
    }

    # Splice into first milestone
    if milestones:
        milestones[0].get("nodes", []).insert(1, new_node)
        spliced_node = new_node

    return {
        "mutation_type": "REMEDIAL_SPLICE",
        "weak_skill": weak_skill,
        "spliced_node": spliced_node,
        "updated_roadmap": roadmap_dag
    }
