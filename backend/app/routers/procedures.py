from fastapi import APIRouter, Depends, Path

from app.dependencies import get_copilot_service
from app.models.checklist import ChecklistRequest, ChecklistResponse
from app.models.procedure import ProcedureSummary
from app.services.copilot_service import CopilotService

router = APIRouter(prefix="/v1/procedures", tags=["procedures"])


@router.get("", response_model=list[ProcedureSummary])
async def get_procedures(
    service: CopilotService = Depends(get_copilot_service),
) -> list[ProcedureSummary]:
    return await service.list_procedures()


@router.post("/{procedure_id}/checklist", response_model=ChecklistResponse)
async def get_checklist(
    request: ChecklistRequest,
    procedure_id: str = Path(..., min_length=1, max_length=120),
    service: CopilotService = Depends(get_copilot_service),
) -> ChecklistResponse:
    return await service.checklist(procedure_id, request)
