"""Structured I/O contract cho LLM Gateway (xem docs/proposal.md muc 5, 6).

LLM chi duoc tra ve cac truong duoi day — khong tu them giay to, khong tu
doi finding/verdict cua rule engine. Neu model tra loi thieu field bat
buoc, gateway se fallback deterministic thay vi hien mot cau tra loi
khong co cau truc.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ClarificationOutput(BaseModel):
    """Output cho luong Guided Intake (capability 1)."""

    intent_summary: str = Field(..., description="Tom tat nhu cau nguoi dung bang ngon ngu don gian")
    needs_clarification: bool = False
    clarifying_question: Optional[str] = None
    reply_message: str = Field(..., description="Cau tra loi hien thi cho nguoi dung")


class ExplanationOutput(BaseModel):
    """Output khi LLM duoc goi de dien giai finding/checklist (khong doi verdict)."""

    friendly_message: str
    suggested_fix: Optional[str] = None


class LLMCallMetadata(BaseModel):
    provider: str
    model: str
    used_fallback: bool
    latency_ms: Optional[float] = None
