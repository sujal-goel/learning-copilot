from routes.assessment import router as assessment_router
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from routes.feedback import router as feedback_router
from routes.profile import router as profile_router
from routes.progress import router as progress_router
from routes.roadmap import router as roadmap_router

__all__ = [
    "auth_router",
    "profile_router",
    "roadmap_router",
    "progress_router",
    "feedback_router",
    "chat_router",
    "assessment_router",
]
