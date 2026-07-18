from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from app.adapters.dev_fixture import (
    DisabledLLMProvider,
    DisabledProcedureRepository,
    DisabledRecommendationProvider,
    DisabledRetrievalProvider,
    FixtureProcedureRepository,
    FixtureRecommendationProvider,
    InMemoryAuditSink,
)
from app.adapters.rag_llm import (
    GatewayLLMProvider,
    RagProcedureRepository,
    RagRecommendationProvider,
    RagRetrievalProvider,
)
from app.config import Settings
from app.ports import (
    AuditSink,
    LLMProvider,
    ProcedureRepository,
    RecommendationProvider,
    RetrievalProvider,
)
from app.services.copilot_service import CopilotService
from app.services.rule_engine import RuleEngine
from app.services.trust_policy import TrustPolicy


@dataclass
class AppContainer:
    settings: Settings
    procedure_repository: ProcedureRepository
    recommendation_provider: RecommendationProvider
    retrieval_provider: RetrievalProvider
    llm_provider: LLMProvider
    audit_sink: AuditSink

    def copilot_service(self) -> CopilotService:
        return CopilotService(
            procedure_repository=self.procedure_repository,
            recommendation_provider=self.recommendation_provider,
            retrieval_provider=self.retrieval_provider,
            llm_provider=self.llm_provider,
            audit_sink=self.audit_sink,
            rule_engine=RuleEngine(),
            trust_policy=TrustPolicy(),
        )

    @property
    def capabilities(self) -> dict[str, str]:
        source_available = self.settings.rag_source_path.is_dir() and any(
            self.settings.rag_source_path.glob("*.txt")
        )
        procedure_guidance = {
            "fixture": "fixture",
            "rag": "needs_review" if source_available else "unavailable",
            "external": "unavailable",
            "disabled": "unavailable",
        }[self.settings.procedure_data_mode]
        rag_ready = self.settings.rag_mode == "rag" and source_available
        llm_ready = self.settings.llm_mode == "gateway" and bool(
            self.settings.effective_ai_api_key
        )
        return {
            "procedure_data": self.settings.procedure_data_mode,
            "procedure_guidance": procedure_guidance,
            "rag": self.settings.rag_mode,
            "rag_ready": "true" if rag_ready else "false",
            "llm": self.settings.llm_mode,
            "llm_ready": "true" if llm_ready else "false",
            "legacy_rag": "enabled" if self.settings.legacy_rag_enabled else "disabled",
        }

    @property
    def is_ready(self) -> bool:
        capabilities = self.capabilities
        return (
            capabilities["procedure_guidance"] == "ready"
            and capabilities["rag_ready"] == "true"
            and capabilities["llm_ready"] == "true"
        )


def build_container(settings: Settings) -> AppContainer:
    if settings.procedure_data_mode == "fixture":
        if settings.app_env == "production":
            raise RuntimeError("Dev fixture mode is not allowed in production.")
        procedure_repository: ProcedureRepository = FixtureProcedureRepository()
        recommendation_provider: RecommendationProvider = (
            FixtureRecommendationProvider()
        )
    elif settings.procedure_data_mode == "rag":
        procedure_repository = RagProcedureRepository()
        recommendation_provider = RagRecommendationProvider()
    else:
        procedure_repository = DisabledProcedureRepository()
        recommendation_provider = DisabledRecommendationProvider()

    retrieval_provider: RetrievalProvider = (
        RagRetrievalProvider()
        if settings.rag_mode == "rag"
        else DisabledRetrievalProvider()
    )
    llm_provider: LLMProvider = (
        GatewayLLMProvider()
        if settings.llm_mode == "gateway"
        else DisabledLLMProvider()
    )

    return AppContainer(
        settings=settings,
        procedure_repository=procedure_repository,
        recommendation_provider=recommendation_provider,
        retrieval_provider=retrieval_provider,
        llm_provider=llm_provider,
        audit_sink=InMemoryAuditSink(),
    )


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_copilot_service(request: Request) -> CopilotService:
    return get_container(request).copilot_service()
