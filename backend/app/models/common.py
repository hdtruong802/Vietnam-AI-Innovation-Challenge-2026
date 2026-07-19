from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictRequestModel(BaseModel):
    """Reject undeclared external input rather than silently accepting it."""

    model_config = ConfigDict(extra="forbid")


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


class IntakeTurnType(str, Enum):
    FREE_TEXT = "free_text"
    PROCEDURE_SELECT = "procedure_select"
    CLARIFICATION_ANSWER = "clarification_answer"
    REVIEW_ACKNOWLEDGEMENT = "review_acknowledgement"


class JourneyStepStatus(str, Enum):
    COMPLETE = "complete"
    CURRENT = "current"
    UPCOMING = "upcoming"
    BLOCKED = "blocked"


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
    demo_mode: bool = False


class RegulatoryResponse(TrustMetadata):
    """Metadata required on every response that could be read as guidance."""


class SessionContext(StrictRequestModel):
    """Client-owned flow state; never a server-side transcript or draft."""

    procedure_id: str | None = Field(default=None, max_length=120)
    procedure_version: str | None = Field(default=None, max_length=120)
    clarification_answers: dict[str, str] = Field(default_factory=dict, max_length=20)
    pending_question_ids: list[str] = Field(default_factory=list, max_length=20)
    acknowledged_review_gates: list[ReviewGate] = Field(default_factory=list, max_length=3)
    reviewed_document_ids: list[str] = Field(default_factory=list, max_length=30)


class ClarifyingQuestion(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    prompt: str = Field(min_length=1, max_length=500)
    options: list[str] = Field(default_factory=list, max_length=8)
    why: str | None = Field(default=None, max_length=500)
    required: bool = True


class ClarificationAnswer(StrictRequestModel):
    question_id: str = Field(min_length=1, max_length=120)
    value: str = Field(min_length=1, max_length=300)


class JourneyStep(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=500)
    status: JourneyStepStatus


class JourneyProgress(BaseModel):
    completed_steps: int = Field(ge=0, le=5)
    total_steps: int = Field(default=5, ge=5, le=5)
    steps: list[JourneyStep] = Field(default_factory=list, min_length=5, max_length=5)


class ConfirmedFact(BaseModel):
    key: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=300)
    value: str = Field(min_length=1, max_length=300)


class NextAction(BaseModel):
    code: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=300)
    review_gate: ReviewGate | None = None


class APIError(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[dict[str, Any]] = Field(default_factory=list)


class ErrorEnvelope(BaseModel):
    error: APIError
