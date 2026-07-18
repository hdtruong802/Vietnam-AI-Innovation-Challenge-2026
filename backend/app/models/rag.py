from pydantic import BaseModel, Field
from typing import List, Optional


class EvidenceSearchRequest(BaseModel):
    query: str = Field(..., description="Vietnamese user query")
    procedure_id: Optional[str] = Field(None, description="Procedure ID filter")
    top_k: int = Field(5, ge=1, le=10, description="Maximum evidence chunks")


class EvidenceHit(BaseModel):
    chunk_id: str
    source_id: str
    procedure_ids: List[str]
    chunk_type: str
    text: str
    context_prefix: str
    score: float
    source_refs: List[str]
    legal_basis_refs: List[str]


class EvidenceSearchResponse(BaseModel):
    status: str
    reason: Optional[str] = None
    hits: List[EvidenceHit] = Field(default_factory=list)
    store_path: str
    loaded_chunks: int


class GroundedAnswerRequest(EvidenceSearchRequest):
    pass


class GroundedAnswerResponse(BaseModel):
    status: str
    reason: Optional[str] = None
    answer: Optional[str] = None
    model: str
    provider: str = "openai"
    citations: List[str] = Field(default_factory=list)
    evidence: List[EvidenceHit] = Field(default_factory=list)
    store_path: str
    loaded_chunks: int
