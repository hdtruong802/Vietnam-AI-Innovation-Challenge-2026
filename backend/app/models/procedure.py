from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models.common import Citation, ClarifyingQuestion, FindingSeverity


class ReviewStatus(str, Enum):
    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review"
    FIXTURE = "fixture"
    UNAVAILABLE = "unavailable"
    CONFLICT = "conflict"
    STALE = "stale"


class ValidationRuleType(str, Enum):
    REQUIRED = "required"
    TYPE = "type"
    STRING_PATTERN = "string_pattern"
    DATE_FORMAT = "date_format"
    DATE_NOT_FUTURE = "date_not_future"
    CONDITIONAL_REQUIRED = "conditional_required"
    FIELD_COMPARE = "field_compare"


class ValidationRule(BaseModel):
    rule_id: str = Field(min_length=1, max_length=120)
    type: ValidationRuleType
    field_id: str = Field(min_length=1, max_length=120)
    severity: FindingSeverity = FindingSeverity.ERROR
    message: str = Field(min_length=1, max_length=500)
    fix_hint: str | None = Field(default=None, max_length=500)
    params: dict[str, Any] = Field(default_factory=dict)
    source_ref_ids: list[str] = Field(default_factory=list)


class ChecklistItem(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    label: str = Field(min_length=1, max_length=300)
    kind: Literal["required", "conditional", "optional"]
    description: str = Field(min_length=1, max_length=1_000)
    source_ref_ids: list[str] = Field(default_factory=list)
    condition: dict[str, Any] | None = None


class ProcedureStep(BaseModel):
    order: int = Field(ge=1, le=30)
    title: str = Field(min_length=1, max_length=300)
    detail: str = Field(min_length=1, max_length=1_000)


class JourneyStageDefinition(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1, max_length=500)
    question_ids: list[str] = Field(default_factory=list, max_length=20)
    requires_document_review: bool = False


class FormSection(BaseModel):
    id: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=500)
    field_ids: list[str] = Field(default_factory=list, max_length=40)


class ProcedureCard(BaseModel):
    procedure_id: str
    name: str
    authority: str | None = Field(default=None, max_length=300)
    processing_time: str | None = Field(default=None, max_length=300)
    fee: str | None = Field(default=None, max_length=300)


class ProcedurePack(BaseModel):
    procedure_id: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=300)
    jurisdiction: str | None = Field(default=None, max_length=300)
    authority: str | None = Field(default=None, max_length=300)
    version: str = Field(min_length=1, max_length=120)
    review_status: ReviewStatus
    effective_from: date | None = None
    effective_to: date | None = None
    last_verified_at: date | None = None
    checksum: str | None = Field(default=None, max_length=128)
    source_refs: list[Citation] = Field(default_factory=list)
    intake_questions: list[ClarifyingQuestion] = Field(default_factory=list)
    required_documents: list[ChecklistItem] = Field(default_factory=list)
    optional_documents: list[ChecklistItem] = Field(default_factory=list)
    steps: list[ProcedureStep] = Field(default_factory=list)
    form_schema: dict[str, Any] = Field(default_factory=dict)
    form_sections: list[FormSection] = Field(default_factory=list, max_length=20)
    journey_stages: list[JourneyStageDefinition] = Field(default_factory=list, max_length=5)
    processing_time: str | None = Field(default=None, max_length=300)
    fee: str | None = Field(default=None, max_length=300)
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)


class ProcedureSummary(BaseModel):
    procedure_id: str
    name: str
    version: str | None = None
    review_status: ReviewStatus
    fixture_mode: bool = False


class ProcedureCandidate(BaseModel):
    procedure_id: str
    name: str
    reason: str = Field(min_length=1, max_length=500)
