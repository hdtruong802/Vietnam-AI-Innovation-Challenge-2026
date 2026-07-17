from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"


class TrustState(str, Enum):
    VERIFIED_GUIDANCE = "verified_guidance"
    NEED_MORE_INFORMATION = "need_more_information"
    OFFICIAL_REVIEW_REQUIRED = "official_review_required"


class ReviewGate(str, Enum):
    U1_PROCEDURE_CONFIRMATION = "U1"
    U2_CHECKLIST_REVIEW = "U2"
    U3_PRECHECK_REVIEW = "U3"


class FindingSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class PrecheckVerdict(str, Enum):
    PASS_PRELIMINARY = "pass_preliminary"
    NEEDS_FIX = "needs_fix"


class Citation(BaseModel):
    ref_id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=240)
    url_or_ref: str | None = Field(default=None, max_length=1_000)
    effective_from: date | None = None
    effective_to: date | None = None


class TrustMetadata(BaseModel):
    trust_state: TrustState
    procedure_version: str | None = Field(default=None, max_length=120)
    source_refs: list[Citation] = Field(default_factory=list)
    last_verified_at: date | None = None
    review_gate: ReviewGate | None = None
    fixture_mode: bool = False


class RegulatoryResponse(TrustMetadata):
    """Metadata required on every response that could be read as guidance."""


class SessionContext(BaseModel):
    procedure_id: str | None = Field(default=None, max_length=120)
    procedure_version: str | None = Field(default=None, max_length=120)
    clarification_answers: dict[str, Any] = Field(default_factory=dict)
    pending_question_ids: list[str] = Field(default_factory=list, max_length=20)
    review_state: str | None = Field(default=None, max_length=80)


class ClarifyingQuestion(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=500)
    options: list[str] = Field(default_factory=list, max_length=8)
    why: str | None = Field(default=None, max_length=500)
    required: bool = True


class APIError(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class ErrorEnvelope(BaseModel):
    error: APIError
