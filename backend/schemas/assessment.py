from pydantic import BaseModel


class AnswerItem(BaseModel):
    question_id: str
    selected_option: str


class AssessmentSubmitRequest(BaseModel):
    assessment_id: str
    node_id: str
    answers: list[AnswerItem]


class UpdatedPathSummary(BaseModel):
    hours_saved: int = 0
    next_node_id: str | None = None


class AssessmentResult(BaseModel):
    score: float
    passed: bool
    adaptation_triggered: bool = False
    adaptation_type: str = "NONE"  # FAST_TRACK, REMEDIAL, NONE
    message: str
    skipped_node_ids: list[str] = []
    updated_path_summary: UpdatedPathSummary | None = None
