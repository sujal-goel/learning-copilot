import asyncio
import uuid
from sqlalchemy import select
from database.session import AsyncSessionLocal, Base, engine
from models import Course, Skill, SkillPrerequisite


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database tables created successfully.")


async def seed_data():
    await init_db()
    async with AsyncSessionLocal() as session:
        # Check if skills already exist
        result = await session.execute(select(Skill).limit(1))
        if result.scalar_one_or_none():
            print("[INFO] Skills already seeded.")
            return

        # Seed Foundation Skills
        skills_data = [
            {"id": uuid.uuid4(), "name": "Python", "description": "Core Python programming fundamentals and data structures", "domain": "Backend"},
            {"id": uuid.uuid4(), "name": "Java", "description": "Core Java, OOP principles, and JVM fundamentals", "domain": "Backend"},
            {"id": uuid.uuid4(), "name": "SQL", "description": "Relational database querying, joins, indexing, and normalization", "domain": "Database"},
            {"id": uuid.uuid4(), "name": "FastAPI", "description": "Modern high-performance web framework for Python APIs", "domain": "Backend"},
            {"id": uuid.uuid4(), "name": "Spring Boot", "description": "Production-grade Java enterprise framework and dependency injection", "domain": "Backend"},
            {"id": uuid.uuid4(), "name": "Docker", "description": "Containerization, Dockerfiles, compose, and multi-stage builds", "domain": "DevOps"},
            {"id": uuid.uuid4(), "name": "PostgreSQL", "description": "Advanced PostgreSQL features, ACID transactions, and pgvector", "domain": "Database"},
        ]

        skills_map = {}
        for item in skills_data:
            skill = Skill(id=item["id"], name=item["name"], description=item["description"], domain=item["domain"])
            session.add(skill)
            skills_map[item["name"]] = skill

        await session.flush()

        # Seed Prerequisites (e.g. Python -> FastAPI, Java -> Spring Boot, SQL -> PostgreSQL)
        prereqs = [
            (skills_map["Python"].id, skills_map["FastAPI"].id, 1.0),
            (skills_map["Java"].id, skills_map["Spring Boot"].id, 1.0),
            (skills_map["SQL"].id, skills_map["PostgreSQL"].id, 0.8),
        ]
        for prereq_id, target_id, weight in prereqs:
            session.add(SkillPrerequisite(skill_id=target_id, prerequisite_skill_id=prereq_id, importance=weight))

        # Seed Courses
        courses_data = [
            {
                "title": "Python for Beginners to Pro",
                "description": "Learn modern Python syntax, OOP, error handling, and standard library.",
                "url": "https://example.com/python-pro",
                "difficulty": "BEGINNER",
                "estimated_hours": 12,
                "target_skill_id": skills_map["Python"].id
            },
            {
                "title": "FastAPI Masterclass: Modern Async REST APIs",
                "description": "Build high-speed asynchronous REST APIs with Pydantic validation, dependency injection, and JWT security.",
                "url": "https://example.com/fastapi-masterclass",
                "difficulty": "INTERMEDIATE",
                "estimated_hours": 16,
                "target_skill_id": skills_map["FastAPI"].id
            },
            {
                "title": "Spring Boot Fundamentals",
                "description": "Master Spring Boot autoconfiguration, JPA repositories, and REST controllers.",
                "url": "https://example.com/course/spring-boot",
                "difficulty": "INTERMEDIATE",
                "estimated_hours": 15,
                "target_skill_id": skills_map["Spring Boot"].id
            },
            {
                "title": "PostgreSQL & Database Design",
                "description": "Schema design, normalization, complex joins, indexing, and transactions in Postgres.",
                "url": "https://example.com/postgres-course",
                "difficulty": "BEGINNER",
                "estimated_hours": 10,
                "target_skill_id": skills_map["PostgreSQL"].id
            },
            {
                "title": "Docker Essentials for Developers",
                "description": "Containerize apps, manage multi-container networks with docker-compose.",
                "url": "https://example.com/docker-essentials",
                "difficulty": "BEGINNER",
                "estimated_hours": 8,
                "target_skill_id": skills_map["Docker"].id
            }
        ]

        for c in courses_data:
            session.add(Course(**c))

        await session.commit()
        print("[OK] Database successfully seeded with starter skills, prerequisites, and courses.")


if __name__ == "__main__":
    asyncio.run(seed_data())
