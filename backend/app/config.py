from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent
DEFAULT_RAG_SOURCE_DIR = str(REPO_ROOT / "data" / "Data_DVC")


class Settings(BaseSettings):
    """Runtime configuration that never contains a secret by default."""

    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "0.2.0"
    api_port: int = Field(default=8000, ge=1, le=65_535)
    cors_allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    max_intake_chars: int = Field(default=500, ge=1, le=2_000)
    max_body_bytes: int = Field(default=65_536, ge=1_024, le=1_048_576)
    procedure_data_mode: Literal["fixture", "disabled", "external", "rag"] = "fixture"
    rag_mode: Literal["disabled", "external", "rag"] = "disabled"
    llm_mode: Literal["disabled", "external", "gateway"] = "disabled"
    rate_limit_enabled: bool = False
    rate_limit_requests: int = Field(default=60, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)

    # --- AI / LLM Gateway (provider-neutral, xem docs/proposal.md muc 5 va D-006) ---
    # De trong ai_api_key khi demo offline: LLMGateway se fallback deterministic,
    # khong goi model va khong bia noi dung quy pham.
    ai_provider: str = ""
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_base_url: str | None = None
    ai_timeout_seconds: float = Field(default=8.0, gt=0)

    # --- RAG / Knowledge (in-process, xem D-006) ---
    rag_source_dir: str = DEFAULT_RAG_SOURCE_DIR
    rag_source_freeze_date: str = "2026-07-17"
    rag_top_k: int = Field(default=5, ge=1, le=50)
    rag_min_confidence: float = Field(default=0.12, ge=0, le=1)

    # --- Guardrail / PII Guard (session-scoped, in-memory, xem D-006) ---
    pii_token_ttl_seconds: int = Field(default=1_800, ge=1)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def rag_source_path(self) -> Path:
        return Path(self.rag_source_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
