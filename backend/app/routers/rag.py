from fastapi import APIRouter, Query

from app.models.rag import (
    EvidenceSearchRequest,
    EvidenceSearchResponse,
    GroundedAnswerRequest,
    GroundedAnswerResponse,
)
from app.services.llm_service import GroundedRAGAnswerService
from app.services.rag_service import RAGService

router = APIRouter(prefix="/v1")


@router.post("/rag/search", response_model=EvidenceSearchResponse)
def search_evidence(request: EvidenceSearchRequest):
    return RAGService.search_evidence(
        query=request.query,
        procedure_id=request.procedure_id,
        top_k=request.top_k,
    )


@router.get("/rag/search", response_model=EvidenceSearchResponse)
def search_evidence_get(
    query: str = Query(..., description="Vietnamese user query"),
    procedure_id: str | None = Query(None, description="Procedure ID filter"),
    top_k: int = Query(5, ge=1, le=10, description="Maximum evidence chunks"),
):
    return RAGService.search_evidence(
        query=query,
        procedure_id=procedure_id,
        top_k=top_k,
    )


@router.post("/rag/answer", response_model=GroundedAnswerResponse)
def answer_with_grounded_llm(request: GroundedAnswerRequest):
    return GroundedRAGAnswerService.answer(
        query=request.query,
        procedure_id=request.procedure_id,
        top_k=request.top_k,
    )


@router.get("/rag/answer", response_model=GroundedAnswerResponse)
def answer_with_grounded_llm_get(
    query: str = Query("", description="Vietnamese user query"),
    procedure_id: str | None = Query(None, description="Procedure ID filter"),
    top_k: int = Query(5, ge=1, le=10, description="Maximum evidence chunks"),
):
    return GroundedRAGAnswerService.answer(
        query=query,
        procedure_id=procedure_id,
        top_k=top_k,
    )
