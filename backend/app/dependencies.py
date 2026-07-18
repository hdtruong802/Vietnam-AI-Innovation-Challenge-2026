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
            audit_sink=self.audit_sink,
            rule_engine=RuleEngine(),
            trust_policy=TrustPolicy(),
        )

    @property
    def capabilities(self) -> dict[str, str]:
        return {
            "procedure_data": self.settings.procedure_data_mode,
            "rag": self.settings.rag_mode,
            "llm": self.settings.llm_mode,
        }


def build_container(settings: Settings) -> AppContainer:
    if settings.procedure_data_mode == "fixture":
        if settings.app_env == "production":
            raise RuntimeError("Dev fixture mode is not allowed in production.")
        procedure_repository: ProcedureRepository = FixtureProcedureRepository()
        recommendation_provider: RecommendationProvider = FixtureRecommendationProvider()
    else:
        procedure_repository = DisabledProcedureRepository()
        recommendation_provider = DisabledRecommendationProvider()

    return AppContainer(
        settings=settings,
        procedure_repository=procedure_repository,
        recommendation_provider=recommendation_provider,
        retrieval_provider=DisabledRetrievalProvider(),
        llm_provider=DisabledLLMProvider(),
        audit_sink=InMemoryAuditSink(),
    )


def get_container(request: Request) -> AppContainer:
    return request.app.state.container


def get_copilot_service(request: Request) -> CopilotService:
    return get_container(request).copilot_service()
