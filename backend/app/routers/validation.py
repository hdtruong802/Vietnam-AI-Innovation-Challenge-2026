from fastapi import APIRouter, Depends

from app.dependencies import get_copilot_service
from app.models.validation import ValidationRequest, ValidationResponse
from app.services.copilot_service import CopilotService

router = APIRouter(prefix="/v1/applications", tags=["validation"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_application(
    request: ValidationRequest,
    service: CopilotService = Depends(get_copilot_service),
) -> ValidationResponse:
    return await service.validate(request)
