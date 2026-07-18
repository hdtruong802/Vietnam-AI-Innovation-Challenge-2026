from fastapi import APIRouter, Depends

from app.dependencies import AppContainer, get_container
from app.models.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    container: AppContainer = Depends(get_container),
) -> HealthResponse:
    capabilities = container.capabilities
    status = "ok" if container.is_ready else "degraded"
    return HealthResponse(
        status=status,
        version=container.settings.app_version,
        environment=container.settings.app_env,
        capabilities=capabilities,
    )
