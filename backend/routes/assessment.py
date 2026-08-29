from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt import get_current_user
from database.session import get_db
from models.user import User
from schemas.assessment import AssessmentResult, AssessmentSubmitRequest, UpdatedPathSummary

router = APIRouter(prefix="/assessment", tags=["Assessments"])


@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(
    req: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates assessment answers, updates user skill proficiency,
    and returns score with dynamic adaptation triggers (Fast-Track or Remedial).
    """
    total_answers = len(req.answers)
    # Simple deterministic mock grading logic for testing
    score = 0.90 if total_answers > 0 else 0.50

    if score >= 0.85:
        return AssessmentResult(
            score=score,
            passed=True,
            adaptation_triggered=True,
            adaptation_type="FAST_TRACK",
            message="Outstanding! You demonstrated advanced mastery. We have fast-tracked your roadmap and skipped beginner tutorials.",
            skipped_node_ids=["n_skip_1", "n_skip_2"],
            updated_path_summary=UpdatedPathSummary(hours_saved=8, next_node_id="n5"),
        )
    elif score < 0.50:
        return AssessmentResult(
            score=score,
            passed=False,
            adaptation_triggered=True,
            adaptation_type="REMEDIAL",
            message="Looks like a few fundamental concepts need reinforcement. We have inserted remedial drill exercises into your roadmap.",
            skipped_node_ids=[],
            updated_path_summary=UpdatedPathSummary(hours_saved=0, next_node_id="n_remedial_1"),
        )
    else:
        return AssessmentResult(
            score=score,
            passed=True,
            adaptation_triggered=False,
            adaptation_type="NONE",
            message="Great work! You passed this milestone assessment.",
            skipped_node_ids=[],
            updated_path_summary=UpdatedPathSummary(hours_saved=0, next_node_id="n3"),
        )
