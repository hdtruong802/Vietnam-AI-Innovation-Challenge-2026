from fastapi import APIRouter, Depends

from app.dependencies import get_copilot_service
from app.models.intake import (
    IntakeRequest,
    IntakeResponse,
    RecommendationRequest,
    RecommendationResponse,
)
from app.services.copilot_service import CopilotService

router = APIRouter(prefix="/v1", tags=["intake"])


@router.post("/procedures/recommend", response_model=RecommendationResponse)
async def recommend_procedure(
    request: RecommendationRequest,
    service: CopilotService = Depends(get_copilot_service),
) -> RecommendationResponse:
    return await service.recommend(request)


@router.post("/intake/turn", response_model=IntakeResponse)
async def intake_turn(
    request: IntakeRequest,
    service: CopilotService = Depends(get_copilot_service),
) -> IntakeResponse:
    return await service.intake(request)
