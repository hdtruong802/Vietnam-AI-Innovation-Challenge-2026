"""Logical contracts cho tang RAG / Knowledge (xem docs/proposal.md muc 5).

Cac model nay la internal contract giua Orchestrator va RAG service,
khong phai public REST schema (public schema van giu nguyen trong
app/models/*.py theo Context Pack local-20260718-rag-llm-guardrail).
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceChunk(BaseModel):
    """Mot doan trich co the trich dan, gan voi mot section cua procedure pack."""

    chunk_id: str
    procedure_id: str
    procedure_name: str
    section: str = Field(
        ...,
        description="Ten section nguon: steps | documents | legal_basis | eligibility | ...",
    )
    text: str
    source_title: str
    source_ref: str = Field(..., description="Ma quyet dinh / van ban phap ly lam citation")
    source_url: Optional[str] = None
    last_verified_at: str
    score: float = Field(0.0, description="Diem lexical relevance, chua chuan hoa xac suat")


class RetrievalQuery(BaseModel):
    """RetrievalQuery da giam thieu du lieu: khong PII, chi text + filter."""

    text: str
    procedure_id: Optional[str] = None
    top_k: int = 5


class RetrievalEvidence(BaseModel):
    """Ket qua fused/reranked evidence tra ve Orchestrator (xem VERIFY trong diagram_v3)."""

    procedure_id: Optional[str] = None
    procedure_name: Optional[str] = None
    chunks: List[EvidenceChunk] = Field(default_factory=list)
    citations: List[Dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    is_grounded: bool = False
    conflict: bool = False
    jurisdiction: Optional[str] = None
    authority: Optional[str] = None
    last_verified_at: Optional[str] = None


class ProcedureCandidate(BaseModel):
    """Ket qua xep hang khi chua biet procedure_id (dung cho intent/recommend)."""

    procedure_id: str
    procedure_name: str
    score: float
