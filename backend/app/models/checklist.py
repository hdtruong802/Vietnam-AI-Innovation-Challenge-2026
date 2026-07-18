from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.models.common import RegulatoryResponse
from app.models.procedure import ChecklistItem, ProcedureStep


class ChecklistRequest(BaseModel):
    clarification_answers: dict[str, Any] = Field(default_factory=dict)
    procedure_version: str | None = Field(default=None, max_length=120)


class ChecklistResponse(RegulatoryResponse):
    procedure_id: str
    procedure_name: str
    required_documents: list[ChecklistItem] = Field(default_factory=list)
    optional_documents: list[ChecklistItem] = Field(default_factory=list)
    steps: list[ProcedureStep] = Field(default_factory=list)
    form_schema: dict[str, Any] = Field(default_factory=dict)
    message_plain: str = Field(min_length=1, max_length=1_000)
