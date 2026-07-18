from __future__ import annotations

from typing import Any

from pydantic import Field

from app.models.common import (
    JourneyProgress,
    NextAction,
    RegulatoryResponse,
    SessionContext,
    StrictRequestModel,
)
from app.models.procedure import (
    ChecklistItem,
    FormSection,
    ProcedureCard,
    ProcedureStep,
)


class ChecklistRequest(StrictRequestModel):
    clarification_answers: dict[str, str] = Field(default_factory=dict, max_length=20)
    procedure_version: str | None = Field(default=None, max_length=120)
    session_context: SessionContext = Field(default_factory=SessionContext)


class ChecklistResponse(RegulatoryResponse):
    procedure_id: str
    procedure_name: str
    required_documents: list[ChecklistItem] = Field(default_factory=list)
    optional_documents: list[ChecklistItem] = Field(default_factory=list)
    steps: list[ProcedureStep] = Field(default_factory=list)
    form_schema: dict[str, Any] = Field(default_factory=dict)
    form_sections: list[FormSection] = Field(default_factory=list)
    procedure_card: ProcedureCard | None = None
    journey: JourneyProgress | None = None
    next_action: NextAction | None = None
    message_plain: str = Field(min_length=1, max_length=1_000)
