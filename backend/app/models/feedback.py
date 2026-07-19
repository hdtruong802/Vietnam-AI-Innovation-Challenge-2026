from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.common import PrecheckVerdict, StrictRequestModel, TrustState


class FeedbackRequest(StrictRequestModel):
    context: Literal["checklist", "precheck"]
    session_id: str = Field(min_length=1, max_length=120)
    procedure_id: str | None = Field(default=None, max_length=120)
    procedure_version: str | None = Field(default=None, max_length=120)
    trust_state: TrustState | None = None
    verdict: PrecheckVerdict | None = None
    vote: Literal["up", "down"]
    reason: (
        Literal[
            "sai_thu_tuc",
            "thieu_thua_giay_to",
            "kho_hieu",
            "loi_precheck_sai",
            "khac",
        ]
        | None
    ) = None
    note: str | None = Field(default=None, max_length=200)
    created_at: datetime


class FeedbackResponse(StrictRequestModel):
    status: Literal["accepted"] = "accepted"
