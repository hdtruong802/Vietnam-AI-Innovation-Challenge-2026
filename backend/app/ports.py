from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.models.common import SessionContext
from app.models.procedure import ProcedureCandidate, ProcedurePack, ProcedureSummary


@dataclass(frozen=True)
class RetrievalQuery:
    query: str
    procedure_id: str | None = None
    jurisdiction: str | None = None


@dataclass(frozen=True)
class RetrievalEvidence:
    available: bool
    references: tuple[str, ...] = ()
    reason: str | None = None


class ProcedureRepository(Protocol):
    async def list_procedures(self) -> list[ProcedureSummary]: ...

    async def get_procedure(self, procedure_id: str) -> ProcedurePack | None: ...


class RecommendationProvider(Protocol):
    async def recommend(
        self, need_text: str, session_context: SessionContext
    ) -> list[ProcedureCandidate]: ...


class RetrievalProvider(Protocol):
    async def retrieve(self, query: RetrievalQuery) -> RetrievalEvidence: ...


class LLMProvider(Protocol):
    async def is_available(self) -> bool: ...


class AuditSink(Protocol):
    async def emit(
        self, event: str, fields: dict[str, str | int | float | bool | None]
    ) -> None: ...
