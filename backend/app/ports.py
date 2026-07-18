from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from app.models.common import SessionContext
from app.models.procedure import ProcedureCandidate, ProcedurePack, ProcedureSummary
from app.models.validation import Finding


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

    async def explain_findings(
        self, session_id: str, form_data: dict[str, Any], findings: Sequence[Finding]
    ) -> dict[str, str]:
        """Trả về rule_id -> câu diễn giải thân thiện, không đổi finding/verdict.

        Caller phải truyền `form_data` chưa tokenize; adapter chịu trách
        nhiệm tokenize PII trước khi rời trusted boundary (PII Guard) và
        không được trả về evidence/finding mới ngoài rule_id đã có.
        """
        ...


class AuditSink(Protocol):
    async def emit(
        self, event: str, fields: dict[str, str | int | float | bool | None]
    ) -> None: ...
