from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.common import ClarifyingQuestion, RegulatoryResponse, SessionContext
from app.models.procedure import ProcedureCandidate


class RecommendationRequest(BaseModel):
    need_text: str = Field(min_length=1, max_length=500)
    session_context: SessionContext = Field(default_factory=SessionContext)


class RecommendationResponse(RegulatoryResponse):
    candidates: list[ProcedureCandidate] = Field(default_factory=list, max_length=3)
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    message_plain: str = Field(min_length=1, max_length=1_000)


class IntakeRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128)
    message: str = Field(min_length=1, max_length=500)
    session_context: SessionContext = Field(default_factory=SessionContext)


class IntakeResponse(RegulatoryResponse):
    session_id: str
    detected_procedure_id: str | None = None
    procedure: ProcedureCandidate | None = None
    message_plain: str = Field(min_length=1, max_length=1_000)
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    proposed_session_context: SessionContext = Field(default_factory=SessionContext)
