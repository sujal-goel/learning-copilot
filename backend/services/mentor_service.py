# Mock AI Response Contract as defined in LLD.md §6.4

MOCK_MENTOR_CHAT_RESPONSE = {
    "reply": "JPA is an ORM that maps Java objects to relational tables. SQL knowledge ensures you understand what JPA generates under the hood, helping you write efficient queries and debug N+1 problems.",
    "citations": [
        {"source": "Database Fundamentals", "course_id": "c1"}
    ],
    "roadmap_mutation": {"triggered": False},
}

MOCK_MENTOR_ADAPTATION_RESPONSE = {
    "reply": (
        "Based on your feedback that Spring Boot felt too theoretical, "
        "I've added two hands-on project nodes after the quiz. "
        "You'll build a small REST API from scratch before moving on. "
        "I also noticed your last assessment score was 62% — you're on track, "
        "but a quick review of Dependency Injection concepts might help."
    ),
    "citations": [
        {"source": "Spring Boot Docs", "url": "https://docs.spring.io/spring-boot/docs/current/reference/html/"}
    ],
    "roadmap_mutation": {
        "triggered": True,
        "mutation_type": "REMEDIAL_SPLICE",
        "spliced_nodes": [
            {"node_id": "n_r1", "title": "Build a TODO REST API (Project)", "type": "PROJECT"},
            {"node_id": "n_r2", "title": "Dependency Injection Deep Dive", "type": "COURSE"},
        ],
    },
}


async def get_mentor_response(user_id: str, query: str, current_node_id: str | None = None) -> dict:
    """
    RAG AI tutor answer grounded in course metadata and prerequisite rules.
    TODO: Replace with actual RAG streaming / retrieval pipeline.
    """
    return dict(MOCK_MENTOR_CHAT_RESPONSE)


async def process_feedback_and_adapt(user_id: str, feedback_id: str | None = None, difficulty: str = "JUST_RIGHT") -> dict:
    """
    Processes user feedback difficulty signals and triggers roadmap adaptation if needed.
    TODO: Replace with dynamic DAG mutation logic.
    """
    if difficulty in ["TOO_HARD", "TOO_EASY"]:
        return dict(MOCK_MENTOR_ADAPTATION_RESPONSE)
    return {
        "reply": "Thank you for the feedback! Your roadmap is progressing smoothly.",
        "citations": [],
        "roadmap_mutation": {"triggered": False},
    }
