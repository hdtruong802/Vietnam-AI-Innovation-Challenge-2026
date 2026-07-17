from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration that never contains a secret by default."""

    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "0.2.0"
    api_port: int = Field(default=8000, ge=1, le=65_535)
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_intake_chars: int = Field(default=500, ge=1, le=2_000)
    max_body_bytes: int = Field(default=65_536, ge=1_024, le=1_048_576)
    procedure_data_mode: Literal["fixture", "disabled", "external"] = "fixture"
    rag_mode: Literal["disabled", "external"] = "disabled"
    llm_mode: Literal["disabled", "external"] = "disabled"
    rate_limit_enabled: bool = False
    rate_limit_requests: int = Field(default=60, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
