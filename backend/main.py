import uvicorn

from app.config import get_settings
from app.main import app

__all__ = ["app"]

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=settings.app_env == "development",
    )
