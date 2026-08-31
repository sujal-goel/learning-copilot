import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.seed import init_db
from routes import (
    assessment_router,
    auth_router,
    chat_router,
    feedback_router,
    profile_router,
    progress_router,
    roadmap_router,
)
from routes.ai_roadmap import router as ai_router
from routes.course_routes import router as course_router
from routes.resource_routes import router as resource_router
from routes.skill_gap_routes import router as skill_gap_router
from utils.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI Learning Path Copilot backend...")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database auto-migration skipped or failed (check connection): {e}")
    yield
    logger.info("Shutting down backend...")


app = FastAPI(
    title="AI Learning Path Copilot API",
    description="Adaptive, Prerequisite-Aware AI Learning Roadmap Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
api_v1_prefix = os.getenv("API_V1_STR", "/api/v1")

app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(profile_router, prefix=api_v1_prefix)
app.include_router(roadmap_router, prefix=api_v1_prefix)
app.include_router(progress_router, prefix=api_v1_prefix)
app.include_router(feedback_router, prefix=api_v1_prefix)
app.include_router(chat_router, prefix=api_v1_prefix)
app.include_router(assessment_router, prefix=api_v1_prefix)

# Also expose direct aliases if desired (e.g., /profile, /roadmap, /chat)
app.include_router(profile_router)
app.include_router(roadmap_router)
app.include_router(progress_router)
app.include_router(feedback_router)
app.include_router(chat_router)

app.include_router(ai_router)
app.include_router(course_router)
app.include_router(resource_router)
app.include_router(skill_gap_router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "AI Learning Path Copilot API"}


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "Welcome to AI Learning Path Copilot API",
        "docs": "/docs",
        "health": "/healthz",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
