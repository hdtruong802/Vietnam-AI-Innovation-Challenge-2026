"""Approved-only keyword retrieval baseline for evidence chunks."""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Iterable

from .chunking import EvidenceChunk

RETRIEVER_VERSION = "vaic-keyword-retriever-v1"
FAIL_CLOSED_REASON = "official_review_required"

_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class RetrievalQuery:
    text: str
    procedure_id: str | None = None
    jurisdiction: str | None = None
    effective_on: str | None = None
    top_k: int = 5

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("query text is required")
        if self.top_k < 1:
            raise ValueError("top_k must be positive")


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    chunk_id: str
    source_id: str
    section_ids: tuple[str, ...]
    procedure_ids: tuple[str, ...]
    chunk_type: str
    text: str
    context_prefix: str
    score: float
    source_refs: tuple[str, ...]
    legal_basis_refs: tuple[str, ...]
    retriever_version: str = RETRIEVER_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    query: RetrievalQuery
    status: str
    hits: tuple[RetrievalHit, ...]
    reason: str | None = None
    retriever_version: str = RETRIEVER_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_marks = "".join(
        character for character in decomposed if unicodedata.category(character) != "Mn"
    )
    return without_marks.replace("đ", "d")


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(_TOKEN_PATTERN.findall(_fold(text)))


def _date_in_effect(chunk: EvidenceChunk, effective_on: str | None) -> bool:
    if effective_on is None:
        return True
    if chunk.effective_from is not None and chunk.effective_from > effective_on:
        return False
    if chunk.effective_to is not None and chunk.effective_to < effective_on:
        return False
    return True


class ApprovedSourceRegistry:
    """In-memory release gate for chunks that are eligible for retrieval."""

    def __init__(self, chunks: Iterable[EvidenceChunk]) -> None:
        self._chunks = tuple(chunks)
        self._approved = tuple(chunk for chunk in self._chunks if chunk.review_status == "approved")

    @property
    def selected_count(self) -> int:
        return len(self._chunks)

    @property
    def approved_count(self) -> int:
        return len(self._approved)

    @property
    def quarantined_count(self) -> int:
        return sum(chunk.review_status == "needs_review" for chunk in self._chunks)

    @property
    def rejected_count(self) -> int:
        return sum(chunk.review_status == "rejected" for chunk in self._chunks)

    def filter(
        self,
        procedure_id: str | None = None,
        jurisdiction: str | None = None,
        effective_on: str | None = None,
    ) -> tuple[EvidenceChunk, ...]:
        chunks = self._approved
        if procedure_id is not None:
            chunks = tuple(chunk for chunk in chunks if procedure_id in chunk.procedure_ids)
        if jurisdiction is not None:
            chunks = tuple(chunk for chunk in chunks if chunk.jurisdiction == jurisdiction)
        if effective_on is not None:
            chunks = tuple(chunk for chunk in chunks if _date_in_effect(chunk, effective_on))
        return chunks


class KeywordRetriever:
    """Small deterministic keyword scorer for approved chunks."""

    def __init__(self, registry: ApprovedSourceRegistry) -> None:
        self._registry = registry

    def search(self, query: RetrievalQuery) -> RetrievalResult:
        candidates = self._registry.filter(
            procedure_id=query.procedure_id,
            jurisdiction=query.jurisdiction,
            effective_on=query.effective_on,
        )
        if not candidates:
            return RetrievalResult(
                query=query,
                status="blocked",
                hits=(),
                reason=FAIL_CLOSED_REASON,
            )

        query_terms = tokenize(query.text)
        if not query_terms:
            return RetrievalResult(
                query=query,
                status="blocked",
                hits=(),
                reason=FAIL_CLOSED_REASON,
            )
        query_counts = Counter(query_terms)
        document_frequency: dict[str, int] = defaultdict(int)
        candidate_terms: dict[str, Counter[str]] = {}
        for chunk in candidates:
            terms = Counter(tokenize(f"{chunk.context_prefix}\n{chunk.text}"))
            candidate_terms[chunk.chunk_id] = terms
            for term in set(terms):
                document_frequency[term] += 1

        hits: list[RetrievalHit] = []
        total = len(candidates)
        for chunk in candidates:
            terms = candidate_terms[chunk.chunk_id]
            score = 0.0
            for term, query_weight in query_counts.items():
                if term not in terms:
                    continue
                inverse_document_frequency = (
                    math.log((1 + total) / (1 + document_frequency[term])) + 1.0
                )
                score += query_weight * terms[term] * inverse_document_frequency
            if score <= 0:
                continue
            hits.append(
                RetrievalHit(
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    section_ids=chunk.section_ids,
                    procedure_ids=chunk.procedure_ids,
                    chunk_type=chunk.chunk_type,
                    text=chunk.text,
                    context_prefix=chunk.context_prefix,
                    score=round(score, 6),
                    source_refs=chunk.source_refs,
                    legal_basis_refs=chunk.legal_basis_refs,
                )
            )

        hits.sort(key=lambda hit: (-hit.score, hit.source_id, hit.chunk_id))
        selected = tuple(hits[: query.top_k])
        if not selected:
            return RetrievalResult(
                query=query,
                status="blocked",
                hits=(),
                reason=FAIL_CLOSED_REASON,
            )
        return RetrievalResult(query=query, status="ok", hits=selected)
