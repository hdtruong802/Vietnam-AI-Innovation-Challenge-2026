from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.common import (
    FindingSeverity,
    JourneyProgress,
    NextAction,
    PrecheckVerdict,
    RegulatoryResponse,
    SessionContext,
    StrictRequestModel,
)


class ValidationRequest(StrictRequestModel):
    procedure_id: str = Field(min_length=1, max_length=120)
    procedure_version: str | None = Field(default=None, max_length=120)
    form_data: dict[str, Any] = Field(default_factory=dict)
    session_context: SessionContext = Field(default_factory=SessionContext)


class Finding(BaseModel):
    field_id: str | None = Field(default=None, max_length=120)
    severity: FindingSeverity
    rule_id: str = Field(min_length=1, max_length=120)
    message: str = Field(min_length=1, max_length=500)
    fix_hint: str | None = Field(default=None, max_length=500)
    source_ref_ids: list[str] = Field(default_factory=list)


class ValidationResponse(RegulatoryResponse):
    procedure_id: str
    verdict: PrecheckVerdict | None = None
    findings: list[Finding] = Field(default_factory=list)
    summary_message: str = Field(min_length=1, max_length=1_000)
    journey: JourneyProgress | None = None
    next_action: NextAction | None = None
    proposed_session_context: SessionContext = Field(default_factory=SessionContext)
    explanations: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "rule_id -> câu diễn giải thân thiện từ LLM Gateway (best-effort, "
            "chỉ diễn giải finding đã có, không thay đổi verdict/finding gốc)."
        ),
    )
