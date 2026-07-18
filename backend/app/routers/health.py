from fastapi import APIRouter, Depends

from app.dependencies import AppContainer, get_container
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    container: AppContainer = Depends(get_container),
) -> HealthResponse:
    capabilities = container.capabilities
    status = "degraded" if capabilities["procedure_data"] == "disabled" else "ok"
    return HealthResponse(
        status=status,
        version=container.settings.app_version,
        environment=container.settings.app_env,
        capabilities=capabilities,
    )
