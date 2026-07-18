"""Hybrid retrieval: keyword TF-IDF cosine + dense Vietnamese embeddings.

Retrieval mode (RAG_RETRIEVAL_MODE env / config):
  "keyword"  — BM25-style TF-IDF cosine (default fallback, no deps).
  "semantic" — chi dense embedding (yeu cau sentence-transformers hoac API key).
  "hybrid"   — ket hop: score = (1 - alpha) * keyword + alpha * dense.
               Tu dong giam ve keyword khi dense embedding khong kha dung.

Dense embedding duoc cung cap boi app.services.rag.embedding:
  - Provider "local": sentence-transformers + HuggingFace model (offline,
    khong mat API cost, uu tien viet-bi-encoder cho retrieval tieng Viet).
  - Provider "openai": OpenAI-compatible embedding API (fallback).
  - Provider "auto": thu local truoc, roi openai.
  Neu ca hai deu that bai, retrieval tu dong ve keyword-only.

Chi truy hoi tren cac chunk duoc allowlist trong source_store.PROCEDURE_ALLOWLIST
— khong co PII, chat memory hay case memory nao trong index nay.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache
from typing import Dict, List, Optional

from app.config import get_settings
from app.services.rag.chunking import build_chunks
from app.services.rag.embedding import (
    EmbeddingMap,
    Vector,
    build_embedding_index,
    clear_embedding_cache,
    cosine_similarity_dense,
    embed_query,
)
from app.services.rag.schemas import (
    EvidenceChunk,
    ProcedureCandidate,
    RetrievalEvidence,
    RetrievalQuery,
)
from app.services.rag.source_store import (
    PROCEDURE_DISPLAY_NAME,
    load_candidate_records,
    strip_diacritics,
)

_TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")
_STOPWORDS = {
    "toi",
    "ban",
    "la",
    "va",
    "cua",
    "cho",
    "the",
    "nay",
    "o",
    "co",
    "khong",
    "muon",
    "can",
    "de",
    "voi",
    "tai",
    "mot",
    "nhung",
    "duoc",
    "phai",
    "khi",
    "tu",
    "ve",
    "hay",
    "nhu",
    "da",
    "se",
    "cac",
    "trong",
    "theo",
    "nguoi",
}


def _tokenize(text: str) -> List[str]:
    normalized = strip_diacritics(text).lower()
    tokens = _TOKEN_RE.findall(normalized)
    return [t for t in tokens if len(t) > 1 and t not in _STOPWORDS]


def _term_vector(tokens: List[str]) -> Counter:
    return Counter(tokens)


def _cosine_similarity(vec_a: Counter, vec_b: Counter) -> float:
    if not vec_a or not vec_b:
        return 0.0
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[t] * vec_b[t] for t in common)
    if dot == 0:
        return 0.0
    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class _ScoredChunk:
    __slots__ = ("chunk", "vector")

    def __init__(self, chunk: EvidenceChunk):
        self.chunk = chunk
        self.vector = _term_vector(
            _tokenize(f"{chunk.procedure_name} {chunk.section} {chunk.text}")
        )


@lru_cache(maxsize=1)
def _build_keyword_index() -> Dict[str, List[_ScoredChunk]]:
    """Build keyword TF-IDF index (luon co, khong can API/model)."""
    records_by_procedure = load_candidate_records()
    index: Dict[str, List[_ScoredChunk]] = {}
    for procedure_id, records in records_by_procedure.items():
        chunks = build_chunks(procedure_id, records)
        index[procedure_id] = [_ScoredChunk(c) for c in chunks]
    return index


def _build_dense_index() -> Optional[EmbeddingMap]:
    """Build dense embedding index tu cung corpus voi keyword index.

    Tra ve None neu embedding khong kha dung (rag_retrieval_mode=keyword
    hoac sentence-transformers chua cai hoac API key trong).
    """
    keyword_index = _build_keyword_index()
    all_chunks: List[EvidenceChunk] = []
    for scored_list in keyword_index.values():
        for sc in scored_list:
            all_chunks.append(sc.chunk)

    if not all_chunks:
        return None

    chunk_ids = tuple(c.chunk_id for c in all_chunks)
    chunk_texts = tuple(f"{c.procedure_name} {c.section} {c.text}" for c in all_chunks)
    return build_embedding_index(chunk_ids, chunk_texts)


def _hybrid_score(
    keyword_score: float,
    chunk_id: str,
    query_vec: Optional[Vector],
    dense_index: Optional[EmbeddingMap],
    alpha: float,
) -> float:
    """Ket hop keyword va dense score.

    final = (1 - alpha) * keyword + alpha * dense

    Neu dense_index la None hoac chunk khong co trong index,
    tu dong dung keyword-only (alpha = 0).
    """
    if alpha == 0.0 or dense_index is None or query_vec is None:
        return keyword_score
    chunk_vec = dense_index.get(chunk_id)
    if chunk_vec is None:
        return keyword_score
    dense_score = cosine_similarity_dense(query_vec, chunk_vec)
    return (1.0 - alpha) * keyword_score + alpha * dense_score


class RetrievalService:
    """Facade cho tang RAG duoc Orchestrator/service khac goi.

    Static methods de cac router/service dung truc tiep khong can khoi tao
    instance rieng (index duoc cache o module-level, chi build mot lan).
    """

    @staticmethod
    def clear_cache() -> None:
        """Chi dung trong test: xoa cache khi doi RAG_SOURCE_DIR hoac settings."""
        _build_keyword_index.cache_clear()
        load_candidate_records.cache_clear()
        clear_embedding_cache()

    @staticmethod
    def known_procedure_ids() -> List[str]:
        return list(PROCEDURE_DISPLAY_NAME.keys())

    @staticmethod
    def recommend_procedure(query_text: str, top_k: int = 3) -> List[ProcedureCandidate]:
        settings = get_settings()
        alpha = settings.rag_semantic_weight

        keyword_index = _build_keyword_index()
        dense_index = _build_dense_index() if alpha > 0 else None
        query_vec = embed_query(query_text) if (alpha > 0 and dense_index is not None) else None
        keyword_query_vec = _term_vector(_tokenize(query_text))

        best_per_procedure: Dict[str, float] = {}
        for procedure_id, scored_chunks in keyword_index.items():
            best = 0.0
            for sc in scored_chunks:
                kw = _cosine_similarity(keyword_query_vec, sc.vector)
                score = _hybrid_score(kw, sc.chunk.chunk_id, query_vec, dense_index, alpha)
                if score > best:
                    best = score
            best_per_procedure[procedure_id] = best

        ranked = sorted(best_per_procedure.items(), key=lambda kv: kv[1], reverse=True)
        return [
            ProcedureCandidate(
                procedure_id=pid,
                procedure_name=PROCEDURE_DISPLAY_NAME.get(pid, pid),
                score=round(score, 4),
            )
            for pid, score in ranked[:top_k]
        ]

    @staticmethod
    def retrieve(query: RetrievalQuery) -> RetrievalEvidence:
        settings = get_settings()
        alpha = settings.rag_semantic_weight

        keyword_index = _build_keyword_index()
        dense_index = _build_dense_index() if alpha > 0 else None
        query_vec = (
            embed_query(query.text)
            if (alpha > 0 and dense_index is not None and query.text)
            else None
        )
        keyword_query_vec = _term_vector(_tokenize(query.text)) if query.text else Counter()

        if query.procedure_id and query.procedure_id not in keyword_index:
            return RetrievalEvidence(
                procedure_id=query.procedure_id,
                chunks=[],
                citations=[],
                confidence=0.0,
                is_grounded=False,
                conflict=False,
            )

        candidate_procedures = (
            [query.procedure_id] if query.procedure_id else list(keyword_index.keys())
        )

        scored: List[tuple] = []
        for procedure_id in candidate_procedures:
            for sc in keyword_index.get(procedure_id, []):
                if keyword_query_vec or query_vec:
                    kw = (
                        _cosine_similarity(keyword_query_vec, sc.vector)
                        if keyword_query_vec
                        else 0.0
                    )
                    score = _hybrid_score(kw, sc.chunk.chunk_id, query_vec, dense_index, alpha)
                else:
                    score = 1.0
                scored.append((score, sc.chunk))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        top_k = query.top_k or settings.rag_top_k
        top = scored[:top_k]

        resolved_procedure_id = query.procedure_id
        if resolved_procedure_id is None and top:
            resolved_procedure_id = top[0][1].procedure_id

        chunks: List[EvidenceChunk] = []
        seen_citations: Dict[str, Dict[str, str]] = {}
        for score, chunk in top:
            enriched = chunk.model_copy(update={"score": round(score, 4)})
            chunks.append(enriched)
            seen_citations[chunk.source_ref] = {
                "title": chunk.source_title,
                "url": chunk.source_url or "",
                "ref_code": chunk.source_ref,
            }

        confidence = top[0][0] if top else 0.0
        is_grounded = bool(chunks) and confidence >= settings.rag_min_confidence

        return RetrievalEvidence(
            procedure_id=resolved_procedure_id,
            procedure_name=(
                PROCEDURE_DISPLAY_NAME.get(resolved_procedure_id) if resolved_procedure_id else None
            ),
            chunks=chunks,
            citations=list(seen_citations.values()),
            confidence=round(confidence, 4),
            is_grounded=is_grounded,
            conflict=False,
            last_verified_at=chunks[0].last_verified_at if chunks else None,
        )

    @staticmethod
    def get_citations_for_procedure(procedure_id: str) -> List[Dict[str, str]]:
        evidence = RetrievalService.retrieve(
            RetrievalQuery(text="", procedure_id=procedure_id, top_k=50)
        )
        return evidence.citations
