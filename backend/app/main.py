from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import Settings, get_settings
from app.dependencies import AppContainer, build_container
from app.models.common import APIError, ErrorEnvelope
from app.models.errors import AppError
from app.rate_limit import InMemoryRateLimiter
from app.routers import health, intake, procedures, validation


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[dict] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    payload = ErrorEnvelope(
        error=APIError(code=code, message=message, request_id=request_id, details=details or [])
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def create_app(settings: Settings | None = None, container: AppContainer | None = None) -> FastAPI:
    runtime_settings = settings or get_settings()
    app = FastAPI(
        title="AI Procedure Copilot API",
        description="Integration-ready backend for AI-guided public service procedures.",
        version=runtime_settings.app_version,
    )
    app.state.container = container or build_container(runtime_settings)
    rate_limiter = InMemoryRateLimiter(
        runtime_settings.rate_limit_requests, runtime_settings.rate_limit_window_seconds
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=runtime_settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = request.headers.get("X-Request-ID") or str(uuid4())
        content_length = request.headers.get("content-length")
        try:
            declared_size = int(content_length) if content_length else 0
        except ValueError:
            response = _error_response(
                request,
                400,
                "invalid_content_length",
                "Kích thước yêu cầu không hợp lệ.",
            )
        else:
            if declared_size > runtime_settings.max_body_bytes:
                response = _error_response(
                    request,
                    422,
                    "request_too_large",
                    "Yêu cầu vượt quá giới hạn kích thước cho phép.",
                )
            elif (
                runtime_settings.rate_limit_enabled
                and request.url.path.startswith("/v1/")
                and not rate_limiter.allow(request.client.host if request.client else "unknown")
            ):
                response = _error_response(
                    request,
                    429,
                    "rate_limit_exceeded",
                    "Bạn đã gửi quá nhiều yêu cầu. Vui lòng thử lại sau.",
                )
            else:
                response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(request, exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {"location": list(error["loc"]), "type": error["type"]} for error in exc.errors()
        ]
        return _error_response(
            request,
            422,
            "request_validation_failed",
            "Dữ liệu gửi lên không đúng định dạng yêu cầu.",
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "route_not_found" if exc.status_code == 404 else "http_error"
        message = (
            "Không tìm thấy endpoint yêu cầu."
            if exc.status_code == 404
            else "Yêu cầu không thể thực hiện."
        )
        return _error_response(request, exc.status_code, code, message)

    app.include_router(health.router)
    app.include_router(procedures.router)
    app.include_router(intake.router)
    app.include_router(validation.router)
    return app


app = create_app()
