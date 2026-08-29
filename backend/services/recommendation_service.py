# Mock AI Response Contract as defined in LLD.md §6.3
MOCK_RECOMMENDATIONS_RESPONSE = {
    "skill_gaps": [
        {
            "skill_name": "Spring Boot",
            "gap_score": 1.0,
            "priority": "HIGH",
            "recommended_resources": [
                {
                    "resource_id": "r1",
                    "title": "Spring Boot in Action",
                    "url": "https://example.com/spring-boot-in-action",
                    "type": "COURSE",
                    "difficulty": "BEGINNER",
                    "estimated_hours": 15,
                    "relevance_score": 0.91,
                }
            ],
        },
        {
            "skill_name": "Docker",
            "gap_score": 1.0,
            "priority": "MEDIUM",
            "recommended_resources": [
                {
                    "resource_id": "r2",
                    "title": "Docker for Java Developers",
                    "url": "https://example.com/docker-java",
                    "type": "COURSE",
                    "difficulty": "INTERMEDIATE",
                    "estimated_hours": 8,
                    "relevance_score": 0.84,
                }
            ],
        },
    ]
}


async def get_recommendations(profile_id: str) -> dict:
    """
    Executes 3-layer recommendation engine (Prerequisite filtering -> pgvector search -> Gap scoring).
    TODO: Replace with actual recommendation algorithm.
    """
    return dict(MOCK_RECOMMENDATIONS_RESPONSE)
