from fastapi import APIRouter, HTTPException
from app.models.intake import IntakeRequest, IntakeResponse
from app.services.intake_service import IntakeService

router = APIRouter(prefix="/v1")


@router.post("/intake/turn", response_model=IntakeResponse)
def intake_turn(request: IntakeRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")

    return IntakeService.handle_turn(request)
