from fastapi import APIRouter
from pydantic import BaseModel
from ai.pipeline.learning_pipeline import run_learning_pipeline

router = APIRouter(prefix="/ai", tags=["AI Roadmap"])


class AIRequest(BaseModel):
    user_input: str
    current_skills: list[str] = []


@router.post("/generate")
async def generate_ai_roadmap(req: AIRequest):
    return run_learning_pipeline(
        req.user_input,
        req.current_skills
    )


class ChatRequest(BaseModel):
    message: str

    
@router.post("/chat")
async def chat_with_ai(req: ChatRequest):

    try:
        from ai.shared.gemini_client import client

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=req.message
        )

        return {
            "response": response.text
        }

    except Exception as e:
        return {
            "error": str(e)
        }
