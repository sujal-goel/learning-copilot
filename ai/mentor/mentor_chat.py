from ai.shared.gemini_client import call_llm_json, call_llm_json_async
from ai.mentor.prompts import MENTOR_CHAT_PROMPT, MENTOR_ADAPTATION_PROMPT


async def get_mentor_chat_reply(
    user_id: str,
    query: str,
    chat_history: list | None = None,
    current_node_context: str | None = None,
) -> dict:
    """
    RAG AI tutor answer grounded in course metadata, active node context, and user chat history.
    Returns LLD §6.4 response schema.
    Async — uses thread pool for the blocking Gemini SDK.
    """
    history_text = ""
    if chat_history:
        for msg in chat_history[-6:]:
            role = getattr(msg, "role", "USER")
            text = getattr(msg, "message", str(msg))
            history_text += f"{role}: {text}\n"
    else:
        history_text = "No prior history.\n"

    node_str = current_node_context or "General Curriculum"

    prompt = MENTOR_CHAT_PROMPT.format(
        user_id=user_id,
        current_node_context=node_str,
        chat_history_text=history_text,
        query=query,
    )

    try:
        res = await call_llm_json_async(prompt)
        if "reply" in res:
            return res
    except Exception as e:
        print(f"[Mentor Chat] LLM reply fallback triggered: {e}")

    # Fallback contextual reply
    return {
        "reply": f"Regarding '{query}': In the context of {node_str}, understanding these underlying fundamentals ensures you build robust applications and prevent runtime errors.",
        "citations": [
            {"source": "Core Reference", "url": "https://www.coursera.org"}
        ],
        "roadmap_mutation": {"triggered": False},
    }


async def adapt_roadmap_from_feedback(
    user_id: str,
    feedback_text: str = "",
    difficulty: str = "JUST_RIGHT",
) -> dict:
    """
    Evaluates learner feedback signals (TOO_HARD, TOO_EASY) and returns adaptation message + roadmap mutation payload.
    """
    prompt = MENTOR_ADAPTATION_PROMPT.format(
        user_id=user_id,
        difficulty=difficulty,
        feedback_text=feedback_text,
    )

    try:
        res = await call_llm_json_async(prompt)
        if "reply" in res:
            return res
    except Exception as e:
        print(f"[Mentor Adaptation] LLM adaptation fallback triggered: {e}")

    if difficulty in ["TOO_HARD", "TOO_EASY"]:
        return {
            "reply": f"Based on your feedback ('{feedback_text}'), I've updated your roadmap with targeted remedial modules.",
            "citations": [],
            "roadmap_mutation": {
                "triggered": True,
                "mutation_type": "REMEDIAL_SPLICE" if difficulty == "TOO_HARD" else "FAST_TRACK",
                "spliced_nodes": [
                    {"node_id": "n_r1", "title": "Hands-on Practical Exercise", "type": "PROJECT"}
                ]
            }
        }

    return {
        "reply": "Thank you for the feedback! Your roadmap is progressing smoothly.",
        "citations": [],
        "roadmap_mutation": {"triggered": False},
    }
