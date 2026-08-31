# Mock AI Response Contract as defined in LLD.md §6.2
MOCK_ROADMAP_RESPONSE = {
    "path_id": "d1eebc99-9c0b-4ef8-bb6d-6bb9bd380a44",
    "title": "Backend Developer Roadmap (6 months)",
    "total_estimated_hours": 120,
    "milestones": [
        {
            "milestone_id": "m1",
            "title": "Month 1: Framework Foundations",
            "nodes": [
                {
                    "node_id": "n1",
                    "type": "COURSE",
                    "title": "Spring Boot Fundamentals",
                    "resource_url": "https://example.com/course/spring-boot",
                    "estimated_hours": 15,
                    "status": "IN_PROGRESS",
                    "dependencies": [],
                },
                {
                    "node_id": "n2",
                    "type": "ASSESSMENT",
                    "title": "Spring Boot Basics Quiz",
                    "estimated_hours": 1,
                    "status": "LOCKED",
                    "dependencies": ["n1"],
                },
            ],
        },
        {
            "milestone_id": "m2",
            "title": "Month 2: REST APIs & Database Integration",
            "nodes": [
                {
                    "node_id": "n3",
                    "type": "COURSE",
                    "title": "Building REST APIs with Spring",
                    "resource_url": "https://example.com/course/rest-apis",
                    "estimated_hours": 20,
                    "status": "LOCKED",
                    "dependencies": ["n2"],
                }
            ],
        },
    ],
}


async def generate_roadmap(profile_id: str, goal: str | None = None) -> dict:
    """
    Generates a personalized topological roadmap DAG.
    TODO: Replace with AI DAG generation + topological sort call.
    """
    return dict(MOCK_ROADMAP_RESPONSE)
