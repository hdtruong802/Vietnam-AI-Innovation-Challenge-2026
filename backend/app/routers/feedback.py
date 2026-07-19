from fastapi import APIRouter, Depends, status

from app.dependencies import AppContainer, get_container
from app.models.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_feedback(
    request: FeedbackRequest,
    container: AppContainer = Depends(get_container),
) -> FeedbackResponse:
    # Session identifiers and free-text notes are deliberately excluded from audit.
    await container.audit_sink.emit(
        "feedback_received",
        {
            "context": request.context,
            "procedure_id": request.procedure_id,
            "procedure_version": request.procedure_version,
            "trust_state": request.trust_state.value if request.trust_state else None,
            "verdict": request.verdict.value if request.verdict else None,
            "vote": request.vote,
            "reason": request.reason,
            "has_note": bool(request.note),
        },
    )
    return FeedbackResponse()
