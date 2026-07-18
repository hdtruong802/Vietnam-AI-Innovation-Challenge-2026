import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from app.config import get_settings
from app.models.rag import EvidenceHit, EvidenceSearchResponse
from app.rag.chunking import EvidenceChunk
from app.rag.retrieval import (
    ApprovedSourceRegistry,
    KeywordRetriever,
    RetrievalQuery,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CLEAN_CHUNKS_PATH = REPOSITORY_ROOT / "artifacts" / "chatbot" / "clean-rag-chunks.jsonl"
RUNTIME_TO_RAG_PROCEDURE_IDS = {
    "dang-ky-khai-sinh": "birth_registration",
    "dang-ky-thuong-tru": "residence_registration",
    "dang-ky-ho-kinh-doanh": "household_business_registration",
}


def _tuple_fields(record: dict) -> dict:
    tuple_fields = {
        "section_ids",
        "procedure_ids",
        "section_path",
        "source_refs",
        "legal_basis_refs",
    }
    return {
        key: tuple(value) if key in tuple_fields and isinstance(value, list) else value
        for key, value in record.items()
    }


def load_clean_chunks(
    path: Path = DEFAULT_CLEAN_CHUNKS_PATH,
) -> tuple[EvidenceChunk, ...]:
    if not path.is_file():
        return ()
    chunks: List[EvidenceChunk] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            chunks.append(EvidenceChunk(**_tuple_fields(json.loads(line))))
    return tuple(chunks)


@lru_cache(maxsize=1)
def _cached_chunks() -> tuple[EvidenceChunk, ...]:
    return load_clean_chunks()


class RAGService:
    @staticmethod
    def search_evidence(
        query: str,
        procedure_id: Optional[str] = None,
        top_k: int = 5,
    ) -> EvidenceSearchResponse:
        if not get_settings().legacy_rag_enabled:
            return EvidenceSearchResponse(
                status="blocked",
                reason="legacy_rag_disabled",
                hits=[],
                store_path=str(DEFAULT_CLEAN_CHUNKS_PATH),
                loaded_chunks=0,
            )

        chunks = _cached_chunks()
        if not query.strip():
            return EvidenceSearchResponse(
                status="blocked",
                reason="query_required",
                hits=[],
                store_path=str(DEFAULT_CLEAN_CHUNKS_PATH),
                loaded_chunks=len(chunks),
            )
        rag_procedure_id = (
            RUNTIME_TO_RAG_PROCEDURE_IDS.get(procedure_id, procedure_id) if procedure_id else None
        )
        retriever = KeywordRetriever(ApprovedSourceRegistry(chunks))
        result = retriever.search(
            RetrievalQuery(text=query, procedure_id=rag_procedure_id, top_k=top_k)
        )
        hits = [
            EvidenceHit(
                chunk_id=hit.chunk_id,
                source_id=hit.source_id,
                procedure_ids=list(hit.procedure_ids),
                chunk_type=hit.chunk_type,
                text=hit.text,
                context_prefix=hit.context_prefix,
                score=hit.score,
                source_refs=list(hit.source_refs),
                legal_basis_refs=list(hit.legal_basis_refs),
            )
            for hit in result.hits
        ]
        return EvidenceSearchResponse(
            status=result.status,
            reason=result.reason,
            hits=hits,
            store_path=str(DEFAULT_CLEAN_CHUNKS_PATH),
            loaded_chunks=len(chunks),
        )

    @staticmethod
    def clear_cache() -> None:
        _cached_chunks.cache_clear()
