from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_ROOT.parent
ENV_FILES = (REPOSITORY_ROOT / ".env", BACKEND_ROOT / ".env")
DEFAULT_RAG_SOURCE_DIR = str(REPOSITORY_ROOT / "data" / "Data_DVC")


class Settings(BaseSettings):
    """Runtime configuration that never contains a secret by default."""

    app_env: Literal["development", "test", "production"] = "development"
    app_version: str = "0.2.0"
    api_port: int = Field(default=8000, ge=1, le=65_535)
    cors_allowed_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000," "http://localhost:3001,http://127.0.0.1:3001"
    )
    max_intake_chars: int = Field(default=500, ge=1, le=2_000)
    max_body_bytes: int = Field(default=65_536, ge=1_024, le=1_048_576)
    procedure_data_mode: Literal["fixture", "disabled", "external", "rag"] = "fixture"
    rag_mode: Literal["disabled", "external", "rag"] = "disabled"
    llm_mode: Literal["disabled", "external", "gateway"] = "disabled"
    legacy_rag_enabled: bool = False
    rate_limit_enabled: bool = False
    rate_limit_requests: int = Field(default=60, ge=1, le=10_000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3_600)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = ""
    openai_timeout_seconds: float = Field(default=20, ge=1, le=120)

    # --- AI / LLM Gateway (provider-neutral, xem docs/proposal.md muc 5 va D-006) ---
    # De trong ai_api_key khi demo offline: LLMGateway se fallback deterministic,
    # khong goi model va khong bia noi dung quy pham.
    ai_provider: str = ""
    ai_model: str = Field(
        default="gpt-4o-mini", validation_alias=AliasChoices("AI_MODEL", "OPENAI_MODEL")
    )
    ai_api_key: str = Field(
        default="", validation_alias=AliasChoices("AI_API_KEY", "OPENAI_API_KEY")
    )
    ai_base_url: str | None = Field(
        default=None, validation_alias=AliasChoices("AI_BASE_URL", "OPENAI_BASE_URL")
    )
    ai_timeout_seconds: float = Field(
        default=8.0,
        gt=0,
        validation_alias=AliasChoices("AI_TIMEOUT_SECONDS", "OPENAI_TIMEOUT_SECONDS"),
    )
    rag_source_dir: str = DEFAULT_RAG_SOURCE_DIR
    rag_source_freeze_date: str = "2026-07-17"
    rag_top_k: int = Field(default=5, ge=1, le=50)
    rag_min_confidence: float = Field(default=0.12, ge=0, le=1)

    # --- Semantic search (xem docs/proposal.md D-005) ---
    # "keyword"  — BM25-style TF-IDF cosine (luon co, khong can API key/model).
    # "semantic" — chi dung dense embedding.
    # "hybrid"   — ket hop: final = (1-alpha)*keyword + alpha*dense.
    #              Tu dong fallback alpha=0 neu embedding khong kha dung.
    rag_retrieval_mode: Literal["keyword", "semantic", "hybrid"] = "hybrid"
    rag_semantic_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    # Model HuggingFace (dung voi sentence-transformers, KHONG can API key).
    # Default: vietnamese-bi-encoder — duoc train cho information retrieval tieng Viet.
    # Override: RAG_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
    rag_embedding_model: str = "bkai-foundation-models/vietnamese-bi-encoder"
    rag_embedding_batch_size: int = Field(default=64, ge=1, le=512)
    # Provider: "local" (sentence-transformers), "openai" (API), "auto" (local dau, roi openai).
    rag_embedding_provider: Literal["local", "openai", "auto"] = "auto"
    pii_token_ttl_seconds: int = Field(default=1_800, ge=1)

    model_config = SettingsConfigDict(env_file=ENV_FILES, extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def rag_source_path(self) -> Path:
        return Path(self.rag_source_dir)

    @property
    def effective_ai_api_key(self) -> str:
        return self.ai_api_key or self.openai_api_key

    @property
    def effective_ai_model(self) -> str:
        return self.ai_model if self.ai_api_key else self.openai_model

    @property
    def effective_ai_base_url(self) -> str | None:
        return self.ai_base_url or self.openai_base_url or None

    @property
    def effective_ai_timeout_seconds(self) -> float:
        return self.ai_timeout_seconds if self.ai_api_key else self.openai_timeout_seconds


@lru_cache
def get_settings() -> Settings:
    return Settings()


_SETTINGS = get_settings()

# Backwards-compatible constants for existing modules.
APP_ENV = _SETTINGS.app_env
ALLOWED_ORIGINS = _SETTINGS.allowed_origins
OPENAI_API_KEY = _SETTINGS.openai_api_key
OPENAI_MODEL = _SETTINGS.openai_model
OPENAI_BASE_URL = _SETTINGS.openai_base_url
OPENAI_TIMEOUT_SECONDS = _SETTINGS.openai_timeout_seconds
